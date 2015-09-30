# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Command-line interface to the Senlin clustering API.
"""

from __future__ import print_function

import argparse
import logging
import sys

from oslo_utils import encodeutils
from oslo_utils import importutils
import six

import senlinclient
from senlinclient import cliargs
from senlinclient import client as senlin_client
from senlinclient.common import exc
from senlinclient.common.i18n import _
from senlinclient.common import utils

osprofiler_profiler = importutils.try_import("osprofiler.profiler")
USER_AGENT = 'python-senlinclient'
LOG = logging.getLogger(__name__)


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


class SenlinShell(object):
    def _setup_logging(self, debug):
        log_lvl = logging.DEBUG if debug else logging.WARNING
        logging.basicConfig(format="%(levelname)s (%(module)s) %(message)s",
                            level=log_lvl)
        logging.getLogger('iso8601').setLevel(logging.WARNING)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    def _setup_verbose(self, verbose):
        if verbose:
            exc.verbose = 1

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)

            # get callback documentation string
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(command,
                                              help=help,
                                              description=desc,
                                              add_help=False,
                                              formatter_class=HelpFormatter)

            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS)

            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

            self.subcommands[command] = subparser

    def do_bash_completion(self, args):
        '''Prints all of the commands and options to stdout.

        The senlin.bash_completion script doesn't have to hard code them.
        '''
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            if sc_str == 'bash_completion' or sc_str == 'bash-completion':
                continue

            commands.add(sc_str)
            for option in list(sc._optionals._option_string_actions):
                options.add(option)

        print(' '.join(commands | options))

    def add_profiler_args(self, parser):
        if osprofiler_profiler:
            parser.add_argument(
                '--profile', metavar='HMAC_KEY',
                help=_('HMAC key to use for encrypting context data for '
                       'performance profiling of operation. This key should '
                       'be the value of HMAC key configured in osprofiler '
                       'middleware in senlin, it is specified in the paste '
                       'deploy configuration (/etc/senlin/api-paste.ini). '
                       'Without the key, profiling will not be triggered '
                       'even if osprofiler is enabled on server side.'))

    def _add_bash_completion_subparser(self, subparsers):
        subparser = subparsers.add_parser('bash_completion',
                                          add_help=False,
                                          formatter_class=HelpFormatter)

        subparser.set_defaults(func=self.do_bash_completion)
        self.subcommands['bash_completion'] = subparser

    def get_subcommand_parser(self, base_parser, version):
        parser = base_parser

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')
        submodule = utils.import_versioned_module(version, 'shell')
        self._find_actions(subparsers, submodule)
        self._find_actions(subparsers, self)
        self._add_bash_completion_subparser(subparsers)

        return parser

    @utils.arg('command', metavar='<subcommand>', nargs='?',
               help=_('Display help for <subcommand>.'))
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()

    def _check_identity_arguments(self, args):
        # TODO(Qiming): validate the token authentication path and the trust
        # authentication path

        if not args.auth_url:
            msg = _('You must provide an auth url via --os-auth-url (or '
                    ' env[OS_AUTH_URL])')
            raise exc.CommandError(msg)

        # username or user_id or token must be specified
        if not (args.username or args.user_id or args.token):
            msg = _('You must provide a user name, a user_id or a '
                    'token for authentication')
            raise exc.CommandError(msg)

        # if both username and user_id are specified, user_id takes precedence
        if (args.username and args.user_id):
            msg = _('Both user name and user ID are specified, Senin will use '
                    'user ID for authentication')
            print(_('WARNING: %s') % msg)

        if 'v3' in args.auth_url:
            if (args.username and not args.user_id):
                if not (args.user_domain_id or args.user_domain_name):
                    msg = _('Either user domain ID (--user-domain-id / '
                            'env[OS_USER_DOMAIN_ID]) or user domain name '
                            '(--user-domain-name / env[OS_USER_DOMAIN_NAME]) '
                            'must be specified, because user name may not be '
                            'unique.')
                    raise exc.CommandError(msg)

        # password is needed if username or user_id is present
        if (args.username or args.user_id) and not (args.password):
            msg = _('You must provide a password for user %s') % (
                args.username or args.user_id)
            raise exc.CommandError(msg)

        # project name or ID is needed, or else sdk may find the wrong project
        if (not (args.project_id or args.project_name or args.tenant_id
                 or args.tenant_name)):
            if not (args.user_id):
                msg = _('Either project/tenant ID or project/tenant name '
                        'must be specified, or else Senlin cannot know '
                        'which project to use.')
                raise exc.CommandError(msg)
            else:
                msg = _('Neither project ID nor project name is specified. '
                        'Senlin will use user\'s default project which may '
                        'result in authentication error.')
                print(_('WARNING: %s') % msg)

        # both project name and ID are specified, ID takes precedence
        if ((args.project_id or args.tenant_id) and
                (args.project_name or args.tenant_name)):
            msg = _('Both project/tenant name and project/tenant ID are '
                    'specified, Senin will use project ID for authentication')
            print(_('WARNING: %s') % msg)

        # project name may not be unique
        if 'v3' in args.auth_url:
            if (not (args.project_id or args.tenant_id) and
                    (args.project_name or args.tenant_name) and
                    not (args.project_domain_id or args.project_domain_name)):
                msg = _('Either project domain ID (--project-domain-id / '
                        'env[OS_PROJECT_DOMAIN_ID]) orr project domain name '
                        '(--project-domain-name / env[OS_PROJECT_DOMAIN_NAME '
                        'must be specified, because project/tenant name may '
                        'not be unique.')
                raise exc.CommandError(msg)

    def _setup_senlin_client(self, api_ver, args):
        '''Create senlin client using given args.'''
        kwargs = {
            'auth_plugin': args.auth_plugin,
            'auth_url': args.auth_url,
            'project_name': args.project_name or args.tenant_name,
            'project_id': args.project_id or args.tenant_id,
            'domain_name': args.domain_name,
            'domain_id': args.domain_id,
            'project_domain_name': args.project_domain_name,
            'project_domain_id': args.project_domain_id,
            'user_domain_name': args.user_domain_name,
            'user_domain_id': args.user_domain_id,
            'username': args.username,
            'user_id': args.user_id,
            'password': args.password,
            'verify': args.verify,
            'token': args.token,
            'trust_id': args.trust_id,
        }

        return senlin_client.Client('1', args.user_preferences, USER_AGENT,
                                    **kwargs)

    def main(self, argv):
        # Parse args once to find version
        parser = argparse.ArgumentParser(
            prog='senlin',
            description=__doc__.strip(),
            epilog=_('Type "senlin help <COMMAND>" for help on a specific '
                     'command.'),
            add_help=False,
            formatter_class=HelpFormatter,
        )

        cliargs.add_global_args(parser, version=senlinclient.__version__)
        cliargs.add_global_identity_args(parser)
        self.add_profiler_args(parser)
        base_parser = parser

        (options, args) = base_parser.parse_known_args(argv)

        self._setup_logging(options.debug)
        self._setup_verbose(options.verbose)

        # build available subcommands based on version
        api_ver = options.senlin_api_version
        LOG.info(api_ver)
        subcommand_parser = self.get_subcommand_parser(base_parser, api_ver)
        self.parser = subcommand_parser

        # Handle top-level --help/-h before attempting to parse
        # a command off the command line
        if not args and options.help or not argv:
            self.do_help(options)
            return 0

        # Parse args again and call whatever callback was selected
        args = subcommand_parser.parse_args(argv)

        # Short-circuit and deal with help command right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        # Check if identity information are sufficient
        self._check_identity_arguments(args)

        # Setup Senlin client connection
        sc = self._setup_senlin_client(api_ver, args)

        profile = osprofiler_profiler and options.profile
        if profile:
            osprofiler_profiler.init(options.profile)

        args.func(sc, args)

        if profile:
            trace_id = osprofiler_profiler.get().get_base_id()
            print(_("Trace ID: %s") % trace_id)
            print(_("To display trace use next command:\n"
                  "osprofiler trace show --html %s ") % trace_id)


def main(args=None):
    try:
        if args is None:
            args = sys.argv[1:]

        SenlinShell().main(args)
    except KeyboardInterrupt:
        print(_("... terminating senlin client"), file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        if '--debug' in args or '-d' in args:
            raise
        else:
            print(encodeutils.safe_encode(six.text_type(e)), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
