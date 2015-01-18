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
import six
import sys

from oslo_utils import encodeutils
from oslo_utils import importutils

import senlinclient
from senlinclient import cliargs
from senlinclient import client
from senlinclient.common import exc
from senlinclient.common.i18n import _
from senlinclient.common import sdk
from senlinclient.common import utils

osprofiler_profiler = importutils.try_import("osprofiler.profiler")

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

            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)

            subparser.set_defaults(func=callback)

    def do_bash_completion(self, args):
        '''Prints all of the commands and options to stdout.

        The senlin.bash_completion script doesn't have to hard code them.
        '''
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in list(sc._optionals._option_string_actions):
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
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

        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

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
        # project name or ID is needed to make keystoneclient
        # retrieve a service catalog, it's not required if
        # os_no_client_auth is specified, neither is the auth URL
        if not (args.project_id or args.project_name):
            msg = _('You must provide  a project ID via either '
                    '--os-project-id (or env[OS_PROJECT_ID]) or a project '
                    'name via --os-project-name (or env[OS_PROJECT_NAME])')
            raise exc.CommandError(msg)

        if not args.auth_url:
            msg = _('You must provide an auth url via --os-auth-url (or '
                    ' env[OS_AUTH_URL])')
            raise exc.CommandError(msg)

    def _setup_senlin_client(self, api_ver, args):
        '''Create senlin client using given args.'''
        kwargs = {
            'auth_plugin': args.auth_plugin,
            'auth_url': args.auth_url,
            'project_name': args.project_name,
            'domain_name': args.domain_name,
            'project_domain_name': args.project_domain_name,
            'user_domain_name': args.user_domain_name,
            'user_name': args.username,
            'password': args.password,
            'verify': args.verify,
            'token': args.token,
        }
        conn = sdk.connection.Connection(preference=args.user_preferences,
                                         **kwargs)

        return client.Client('1', conn.session)

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
