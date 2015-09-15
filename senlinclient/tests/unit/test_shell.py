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

import argparse
import logging
import sys

import mock
import six
from six.moves import builtins
import testtools

from senlinclient import client as senlin_client
from senlinclient.common import exc
from senlinclient.common.i18n import _
from senlinclient.common import sdk
from senlinclient.common import utils
from senlinclient import shell
from senlinclient.tests.unit import fakes


class HelpFormatterTest(testtools.TestCase):

    def test_start_section(self):
        fmtr = shell.HelpFormatter('senlin')
        res = fmtr.start_section(('heading', 'text1', 30))
        self.assertIsNone(res)
        h = fmtr._current_section.heading
        self.assertEqual("HEADING('text1', 30)", h)


class TestArgs(testtools.TestCase):

    def __init__(self):
        self.auth_url = 'http://fakeurl/v3'
        self.auth_plugin = 'test_plugin'
        self.username = 'test_user_name'
        self.user_id = 'test_user_id'
        self.token = 'test_token'
        self.project_id = 'test_project_id'
        self.project_name = 'test_project_name'
        self.tenant_id = 'test_tenant_id'
        self.tenant_name = 'test_tenant_name'
        self.password = 'test_password'
        self.user_domain_id = 'test_user_domain_id'
        self.user_domain_name = 'test_user_domain_name'
        self.project_domain_id = 'test_project_domain_id'
        self.project_domain_name = 'test_project_domain_name'
        self.domain_name = 'test_domain_name'
        self.domain_id = 'test_domain_id'
        self.verify = 'test_verify'
        self.user_preferences = 'test_preferences'
        self.trust_id = 'test_trust'


class ShellTest(testtools.TestCase):

    def setUp(self):
        super(ShellTest, self).setUp()

    def SHELL(self, func, *args, **kwargs):
        orig_out = sys.stdout
        sys.stdout = six.StringIO()
        func(*args, **kwargs)
        output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = orig_out

        return output

    @mock.patch.object(logging, 'basicConfig')
    @mock.patch.object(logging, 'getLogger')
    def test_setup_logging_debug(self, x_get, x_config):
        sh = shell.SenlinShell()
        sh._setup_logging(True)

        x_config.assert_called_once_with(
            format="%(levelname)s (%(module)s) %(message)s",
            level=logging.DEBUG)
        mock_calls = [
            mock.call('iso8601'),
            mock.call().setLevel(logging.WARNING),
            mock.call('urllib3.connectionpool'),
            mock.call().setLevel(logging.WARNING),
        ]
        x_get.assert_has_calls(mock_calls)

    @mock.patch.object(logging, 'basicConfig')
    @mock.patch.object(logging, 'getLogger')
    def test_setup_logging_no_debug(self, x_get, x_config):
        sh = shell.SenlinShell()
        sh._setup_logging(False)

        x_config.assert_called_once_with(
            format="%(levelname)s (%(module)s) %(message)s",
            level=logging.WARNING)
        mock_calls = [
            mock.call('iso8601'),
            mock.call().setLevel(logging.WARNING),
            mock.call('urllib3.connectionpool'),
            mock.call().setLevel(logging.WARNING),
        ]
        x_get.assert_has_calls(mock_calls)

    def test_setup_verbose(self):
        sh = shell.SenlinShell()
        sh._setup_verbose(True)
        self.assertEqual(1, exc.verbose)

        sh._setup_verbose(False)
        self.assertEqual(1, exc.verbose)

    def test_find_actions(self):
        sh = shell.SenlinShell()
        sh.subcommands = {}
        subparsers = mock.Mock()
        x_subparser1 = mock.Mock()
        x_subparser2 = mock.Mock()
        x_add_parser = mock.MagicMock(side_effect=[x_subparser1, x_subparser2])
        subparsers.add_parser = x_add_parser

        # subparsers.add_parser = mock.Mock(return_value=x_subparser)
        sh._find_actions(subparsers, fakes)

        self.assertEqual({'command-bar': x_subparser1,
                          'command-foo': x_subparser2},
                         sh.subcommands)
        add_calls = [
            mock.call('command-bar', help='This is the command doc.',
                      description='This is the command doc.',
                      add_help=False,
                      formatter_class=shell.HelpFormatter),
            mock.call('command-foo', help='Pydoc for command foo.',
                      description='Pydoc for command foo.',
                      add_help=False,
                      formatter_class=shell.HelpFormatter),
        ]
        x_add_parser.assert_has_calls(add_calls)

        calls_1 = [
            mock.call('-h', '--help', action='help',
                      help=argparse.SUPPRESS),
            mock.call('-F', '--flag', metavar='<FLAG>',
                      help='Flag desc.'),
            mock.call('arg1', metavar='<ARG1>',
                      help='Arg1 desc')
        ]
        x_subparser1.add_argument.assert_has_calls(calls_1)
        x_subparser1.set_defaults.assert_called_once_with(
            func=fakes.do_command_bar)

        calls_2 = [
            mock.call('-h', '--help', action='help',
                      help=argparse.SUPPRESS),
        ]
        x_subparser2.add_argument.assert_has_calls(calls_2)
        x_subparser2.set_defaults.assert_called_once_with(
            func=fakes.do_command_foo)

    def test_do_bash_completion(self):
        sh = shell.SenlinShell()
        sc1 = mock.Mock()
        sc2 = mock.Mock()
        sc1._optionals._option_string_actions = ('A1', 'A2', 'C')
        sc2._optionals._option_string_actions = ('B1', 'B2', 'C')
        sh.subcommands = {
            'command-foo': sc1,
            'command-bar': sc2,
            'bash-completion': None,
            'bash_completion': None,
        }

        output = self.SHELL(sh.do_bash_completion, None)

        output = output.split('\n')[0]
        output_list = output.split(' ')
        for option in ('A1', 'A2', 'C', 'B1', 'B2',
                       'command-foo', 'command-bar'):
            self.assertIn(option, output_list)

    def test_do_add_profiler_args(self):
        sh = shell.SenlinShell()
        parser = mock.Mock()

        sh.add_profiler_args(parser)

        self.assertEqual(0, parser.add_argument.call_count)

    def test_add_bash_completion_subparser(self):
        sh = shell.SenlinShell()
        sh.subcommands = {}
        x_subparser = mock.Mock()
        x_subparsers = mock.Mock()
        x_subparsers.add_parser.return_value = x_subparser

        sh._add_bash_completion_subparser(x_subparsers)

        x_subparsers.add_parser.assert_called_once_with(
            'bash_completion', add_help=False,
            formatter_class=shell.HelpFormatter)
        self.assertEqual({'bash_completion': x_subparser}, sh.subcommands)
        x_subparser.set_defaults.assert_called_once_with(
            func=sh.do_bash_completion)

    @mock.patch.object(utils, 'import_versioned_module')
    @mock.patch.object(shell.SenlinShell, '_find_actions')
    @mock.patch.object(shell.SenlinShell, '_add_bash_completion_subparser')
    def test_get_subcommand_parser(self, x_add, x_find, x_import):
        x_base = mock.Mock()
        x_module = mock.Mock()
        x_import.return_value = x_module
        sh = shell.SenlinShell()

        res = sh.get_subcommand_parser(x_base, 'v100')

        self.assertEqual(x_base, res)
        x_base.add_subparsers.assert_called_once_with(
            metavar='<subcommand>')
        x_subparsers = x_base.add_subparsers.return_value
        x_import.assert_called_once_with('v100', 'shell')
        find_calls = [
            mock.call(x_subparsers, x_module),
            mock.call(x_subparsers, sh)
        ]

        x_find.assert_has_calls(find_calls)
        x_add.assert_called_once_with(x_subparsers)

    @mock.patch.object(argparse.ArgumentParser, 'print_help')
    def test_do_help(self, mock_print):
        sh = shell.SenlinShell()
        args = mock.Mock()
        args.command = mock.Mock()
        sh.subcommands = {args.command: argparse.ArgumentParser}
        sh.do_help(args)
        self.assertTrue(mock_print.called)

        sh.subcommands = {}
        ex = self.assertRaises(exc.CommandError,
                               sh.do_help, args)
        msg = _("'%s' is not a valid subcommand") % args.command
        self.assertEqual(msg, six.text_type(ex))

    @mock.patch.object(builtins, 'print')
    def test_check_identity_arguments(self, mock_print):
        sh = shell.SenlinShell()
        # auth_url is not specified.
        args = TestArgs()
        args.auth_url = None
        ex = self.assertRaises(exc.CommandError,
                               sh._check_identity_arguments, args)
        msg = _('You must provide an auth url via --os-auth-url (or '
                ' env[OS_AUTH_URL])')
        self.assertEqual(msg, six.text_type(ex))
        # username, user_id and token are not specified.
        args = TestArgs()
        args.username = None
        args.user_id = None
        args.token = None
        msg = _('You must provide a user name, a user_id or a '
                'token for authentication')
        ex = self.assertRaises(exc.CommandError,
                               sh._check_identity_arguments, args)
        self.assertEqual(msg, six.text_type(ex))
        # Both username and user_id are specified.
        args = TestArgs()
        args.project_id = None
        args.tenant_id = None
        sh._check_identity_arguments(args)
        msg = _('WARNING: Both user name and user ID are specified, Senin '
                'will use user ID for authentication')
        mock_print.assert_called_with(msg)

        # 'v3' in auth_url but neither user_domain_id nor user_domain_name
        # is specified.
        args = TestArgs()
        args.user_id = None
        args.user_domain_id = None
        args.user_domain_name = None
        msg = _('Either user domain ID (--user-domain-id / '
                'env[OS_USER_DOMAIN_ID]) or user domain name '
                '(--user-domain-name / env[OS_USER_DOMAIN_NAME]) '
                'must be specified, because user name may not be '
                'unique.')
        ex = self.assertRaises(exc.CommandError,
                               sh._check_identity_arguments, args)
        self.assertEqual(msg, six.text_type(ex))
        # user_id, project_id, project_name, tenant_id and tenant_name are all
        # not specified.
        args = TestArgs()
        args.project_id = None
        args.project_name = None
        args.tenant_id = None
        args.tenant_name = None
        args.user_id = None
        msg = _('Either project/tenant ID or project/tenant name '
                'must be specified, or else Senlin cannot know '
                'which project to use.')
        ex = self.assertRaises(exc.CommandError,
                               sh._check_identity_arguments, args)
        self.assertEqual(msg, six.text_type(ex))
        args.user_id = 'test_user_id'
        sh._check_identity_arguments(args)
        msg = _('Neither project ID nor project name is specified. '
                'Senlin will use user\'s default project which may '
                'result in authentication error.')
        mock_print.assert_called_with(_('WARNING: %s') % msg)

        # Both project_name and project_id are specified
        args = TestArgs()
        args.user_id = None
        sh._check_identity_arguments(args)
        msg = _('Both project/tenant name and project/tenant ID are '
                'specified, Senin will use project ID for authentication')
        mock_print.assert_called_with(_('WARNING: %s') % msg)
        # Project name may not be unique
        args = TestArgs()
        args.user_id = None
        args.project_id = None
        args.tenant_id = None
        args.project_domain_id = None
        args.project_domain_name = None
        msg = _('Either project domain ID (--project-domain-id / '
                'env[OS_PROJECT_DOMAIN_ID]) orr project domain name '
                '(--project-domain-name / env[OS_PROJECT_DOMAIN_NAME '
                'must be specified, because project/tenant name may '
                'not be unique.')
        ex = self.assertRaises(exc.CommandError,
                               sh._check_identity_arguments, args)
        self.assertEqual(msg, six.text_type(ex))

    @mock.patch.object(sdk, 'create_connection')
    def test_setup_senlinclient(self, mock_conn):
        USER_AGENT = 'python-senlinclient'
        args = TestArgs()
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
        sh = shell.SenlinShell()
        conn = mock.Mock()
        mock_conn.return_value = conn
        conn.session = mock.Mock()
        sh._setup_senlin_client('1', args)
        mock_conn.assert_called_once_with(args.user_preferences, USER_AGENT,
                                          **kwargs)
        client = mock.Mock()
        senlin_client.Client = mock.MagicMock(return_value=client)
        self.assertEqual(client, sh._setup_senlin_client('1', args))
