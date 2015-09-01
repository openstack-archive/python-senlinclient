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
import testtools

from senlinclient.common import exc
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
