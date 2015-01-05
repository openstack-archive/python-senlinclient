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

from oslo.utils import encodeutils
from oslo.utils import importutils

from keystoneclient.auth.identity import v3 as v3_auth
from keystoneclient import discover
from keystoneclient.openstack.common.apiclient import exceptions as ks_exc
from keystoneclient import session as kssession

import senlinclient
from senlinclient import client as senlin_client
from senlinclient.common.i18n import _
from senlinclient.common import utils
from senlinclient import exc

logger = logging.getLogger(__name__)
osprofiler_profiler = importutils.try_import("osprofiler.profiler")


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


class SenlinShell(object):

    def _append_global_identity_args(self, parser):
        # FIXME(gyee): these are global identity (Keystone) arguments which
        # should be consistent and shared by all service clients. Therefore,
        # they should be provided by python-keystoneclient. We will need to
        # refactor this code once this functionality is avaible in
        # python-keystoneclient.
        parser.add_argument(
            '-k', '--insecure', default=False, action='store_true',
            help=_('Explicitly allow senlinclient to perform "insecure SSL" '
                   '(HTTPS) requests. The server\'s certificate will not be '
                   'verified against any certificate authorities. This '
                   'option should be used with caution.'))

        parser.add_argument(
            '--os-cert',
            help=_('Path of certificate file to use in SSL connection. This '
                   'file can optionally be prepended with the private key.'))

        parser.add_argument(
            '--os-key',
            help=_('Path of client key to use in SSL connection. This option '
                   'is not necessary if your key is prepended to your cert '
                   'file.'))

        parser.add_argument(
            '--os-cacert', metavar='<ca-certificate-file>', dest='os_cacert',
            default=utils.env('OS_CACERT'),
            help=_('Path of CA TLS certificate(s) used to verify the remote '
                   'server\'s certificate. Without this option senlin looks '
                   'for the default system CA certificates.'))

        parser.add_argument(
            '--os-username', default=utils.env('OS_USERNAME'),
            help=_('Defaults to env[OS_USERNAME].'))

        parser.add_argument(
            '--os-user-id', default=utils.env('OS_USER_ID'),
            help=_('Defaults to env[OS_USER_ID].'))

        parser.add_argument(
            '--os-user-domain-id', default=utils.env('OS_USER_DOMAIN_ID'),
            help=_('Defaults to env[OS_USER_DOMAIN_ID].'))

        parser.add_argument(
            '--os-user-domain-name', default=utils.env('OS_USER_DOMAIN_NAME'),
            help=_('Defaults to env[OS_USER_DOMAIN_NAME].'))

        parser.add_argument(
            '--os-project-id', default=utils.env('OS_PROJECT_ID'),
            help=_('Another way to specify tenant ID. '
                   'This option is mutual exclusive with "--os-tenant-id". '
                   'Defaults to env[OS_PROJECT_ID].'))

        parser.add_argument(
            '--os-project-name', default=utils.env('OS_PROJECT_NAME'),
            help=_('Another way to specify tenant name. '
                   'This option is mutual exclusive with "--os-tenant-name". '
                   'Defaults to env[OS_PROJECT_NAME].'))

        parser.add_argument(
            '--os-project-domain-id',
            default=utils.env('OS_PROJECT_DOMAIN_ID'),
            help=_('Defaults to env[OS_PROJECT_DOMAIN_ID].'))

        parser.add_argument(
            '--os-project-domain-name',
            default=utils.env('OS_PROJECT_DOMAIN_NAME'),
            help=_('Defaults to env[OS_PROJECT_DOMAIN_NAME].'))

        parser.add_argument(
            '--os-password', default=utils.env('OS_PASSWORD'),
            help=_('Defaults to env[OS_PASSWORD]'))

        parser.add_argument(
            '--os-tenant-id', default=utils.env('OS_TENANT_ID'),
            help=_('Defaults to env[OS_TENANT_ID]'))

        parser.add_argument(
            '--os-tenant-name', default=utils.env('OS_TENANT_NAME'),
            help=_('Defaults to env[OS_TENANT_NAME]'))

        parser.add_argument(
            '--os-auth-url', default=utils.env('OS_AUTH_URL'),
            help=_('Defaults to env[OS_AUTH_URL]'))

        parser.add_argument(
            '--os-region-name', default=utils.env('OS_REGION_NAME'),
            help=_('Defaults to env[OS_REGION_NAME].'))

        parser.add_argument(
            '--os-auth-token', default=utils.env('OS_AUTH_TOKEN'),
            help=_('Defaults to env[OS_AUTH_TOKEN].'))

        parser.add_argument(
            '--os-service-type', default=utils.env('OS_SERVICE_TYPE'),
            help=_('Defaults to env[OS_SERVICE_TYPE].'))

        parser.add_argument(
            '--os-endpoint-type', default=utils.env('OS_ENDPOINT_TYPE'),
            help=_('Defaults to env[OS_ENDPOINT_TYPE].'))

    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='senlin',
            description=__doc__.strip(),
            epilog=_('Type "senlin help <COMMAND>" for help on a specific '
                     'command.'),
            add_help=False,
            formatter_class=HelpFormatter,
        )

        # GLOBAL ARGUMENTS
        parser.add_argument(
            '-h', '--help', action='store_true',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--version', action='version', version=senlinclient.__version__,
            help=_("Shows the client version and exits."))

        parser.add_argument(
            '-d', '--debug', action='store_true',
            default=bool(utils.env('SENLINCLIENT_DEBUG')),
            help=_('Defaults to env[SENLINCLIENT_DEBUG].'))

        parser.add_argument(
            '-v', '--verbose', action="store_true", default=False,
            help=_("Print more verbose output."))

        parser.add_argument(
            '--api-timeout',
            help=_('Number of seconds to wait for an API response, '
                   'defaults to system socket timeout'))

        # os-no-client-auth tells senlinclient to use token, instead of
        # env[OS_AUTH_URL]
        parser.add_argument(
            '--os-no-client-auth', action='store_true',
            default=utils.env('OS_NO_CLIENT_AUTH'),
            help=_('Do not contact keystone for a token. '
                   'Defaults to env[OS_NO_CLIENT_AUTH].'))

        parser.add_argument(
            '--senlin-url', default=utils.env('SENLIN_URL'),
            help=_('Do not contact keystone for a token. '
                   'Defaults to env[SENLIN_URL].'))

        parser.add_argument(
            '--senlin-api-version',
            default=utils.env('SENLIN_API_VERSION', default='1'),
            help=_('Defaults to env[SENLIN_API_VERSION] or 1.'))

        parser.add_argument(
            '--include-password', action='store_true',
            default=bool(utils.env('SENLIN_INCLUDE_PASSWORD')),
            help=_('Send $OS_USERNAME and $OS_PASSWORD to senlin.'))

        # FIXME(gyee): this method should come from python-keystoneclient.
        # Will refactor this code once it is available.
        # https://bugs.launchpad.net/python-keystoneclient/+bug/1332337
        self._append_global_identity_args(parser)

        if osprofiler_profiler:
            parser.add_argument(
                '--profile', metavar='HMAC_KEY',
                help=_('HMAC key to use for encrypting context data for '
                       'performance profiling of operation. This key should '
                       'be the value of HMAC key configured in osprofiler '
                       'middleware in senlin, it is specified in the paste '
                       'configuration (/etc/senlin/api-paste.ini). Without '
                       'the key, profiling will not be triggered even if '
                       'osprofiler is enabled on server side.'))
        return parser

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
        if not args.os_username and not args.os_auth_token:
            msg = _('You must provide a username via either --os-username (or '
                    'env[OS_USERNAME]) or a token via --os-auth-token (or '
                    'env[OS_AUTH_TOKEN])')
            raise exc.CommandError(msg)

        if not args.os_password and not args.os_auth_token:
            msg = _('You must provide a password via either --os-password (or '
                    'env[OS_PASSWORD]) or a token via --os-auth-token (or '
                    'env[OS_AUTH_TOKEN]')
            raise exc.CommandError(msg)

        if args.os_no_client_auth:
            if not args.senlin_url:
                msg = _('If you specify --os-no-client-auth you must also '
                        'specify a Senlin API URL via --senlin-url (or '
                        'env[SENLIN_URL]')
                raise exc.CommandError(msg)
        else:
            # Tenant/project name or ID is needed to make keystoneclient
            # retrieve a service catalog, it's not required if
            # os_no_client_auth is specified, neither is the auth URL
            if not (args.os_tenant_id or args.os_tenant_name or
                    args.os_project_id or args.os_project_name):
                msg = _('You must provide tenant ID via either --os-tenant-id'
                        ' (or env[OS_TENANT_ID]) or a tenant name via '
                        '--os-tenant-name (or env[OS_TENANT_NAME]) or a '
                        ' project ID via either --os-project-id (or '
                        'env[OS_PROJECT_ID]) or a project name via '
                        '--os-project-name (or env[OS_PROJECT_NAME])')
                raise exc.CommandError(msg)

            if not args.os_auth_url:
                msg = _('You must provide an auth url via --os-auth-url (or '
                        ' env[OS_AUTH_URL])')
                raise exc.CommandError(msg)

    def _get_keystone_session(self, **kwargs):
        # create a Keystone session
        cacert = kwargs.get('cacert', None)
        cert = kwargs.get('cert', None)
        key = kwargs.get('key', None)
        insecure = kwargs.get('insecure', False)
        timeout = kwargs.get('timeout', None)

        if insecure:
            verify = False
        else:
            verify = cacert or True

        if cert and key:
            cert = (cert, key)

        return kssession.Session(verify=verify, cert=cert, timeout=timeout)

    def _get_keystone_auth(self, session, auth_url, **kwargs):
        # discover the supported keystone versions using the given url
        try:
            ks_discover = discover.Discover(session=session, auth_url=auth_url)
            v3_url = ks_discover.url_for('3.0')
        except ks_exc.ClientException:
            msg = _('Unable to locate Keystone V3 URL for authentication. '
                    'Please check your keystone configuration.')
            raise exc.CommandError(msg)

        auth_token = kwargs.pop('auth_token', None)
        if auth_token:
            return v3_auth.Token(v3_url, auth_token)
        else:
            return v3_auth.Password(v3_url, **kwargs)

    def setup_senlin_client(self, api_ver, args):
        '''Create senlin client using given args.'''
        endpoint = args.senlin_url
        if args.os_no_client_auth:
            # Do not use session since no_client_auth means using senlin to
            # to authenticate
            kwargs = {
                'username': args.os_username,
                'password': args.os_password,
                'auth_url': args.os_auth_url,
                'token': args.os_auth_token,
                'include_pass': args.include_password,
                'insecure': args.insecure,
                'timeout': args.api_timeout
            }

            return senlin_client.Client(api_ver, endpoint, **kwargs)

        # Get a keystone session first
        kwargs = {
            'cacert': args.os_cacert,
            'cert': args.os_cert,
            'key': args.os_key,
            'insecure': args.insecure,
            'timeout': args.api_timeout
        }

        ksession = self._get_keystone_session(**kwargs)

        # Get keystone auth
        project_id = args.os_project_id or args.os_tenant_id
        project_name = args.os_project_name or args.os_tenant_name
        kwargs = {
            'username': args.os_username,
            'user_id': args.os_user_id,
            'user_domain_id': args.os_user_domain_id,
            'user_domain_name': args.os_user_domain_name,
            'password': args.os_password,
            'auth_token': args.os_auth_token,
            'project_id': project_id,
            'project_name': project_name,
            'project_domain_id': args.os_project_domain_id,
            'project_domain_name': args.os_project_domain_name,
        }
        keystone_auth = self._get_keystone_auth(ksession, args.os_auth_url,
                                                **kwargs)

        service_type = args.os_service_type or 'clustering'
        if not endpoint:
            svc_type = service_type
            region_name = args.os_region_name
            endpoint = keystone_auth.get_endpoint(ksession,
                                                  service_type=svc_type,
                                                  region_name=region_name)

        endpoint_type = args.os_endpoint_type or 'publicURL'
        kwargs = {
            'auth_url': args.os_auth_url,
            'session': ksession,
            'auth': keystone_auth,
            'service_type': service_type,
            'endpoint_type': endpoint_type,
            'region_name': args.os_region_name,
            'username': args.os_username,
            'password': args.os_password,
            'include_pass': args.include_password
        }

        return senlin_client.Client(api_ver, endpoint, **kwargs)

    def main(self, argv):
        # Parse args once to find version
        base_parser = self.get_base_parser()
        (options, args) = base_parser.parse_known_args(argv)
        self._setup_logging(options.debug)
        self._setup_verbose(options.verbose)

        # build available subcommands based on version
        api_ver = options.senlin_api_version
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
        client = self._setup_senlin_client(api_ver, args)

        profile = osprofiler_profiler and options.profile
        if profile:
            osprofiler_profiler.init(options.profile)

        args.func(client, args)

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
