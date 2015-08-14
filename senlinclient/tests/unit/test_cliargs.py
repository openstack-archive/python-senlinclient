# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock
import testtools

from senlinclient import cliargs


class TestCliArgs(testtools.TestCase):

    def test_add_global_identity_args(self):
        parser = mock.Mock()

        cliargs.add_global_identity_args(parser)
        expected = [
            '--os-auth-plugin',
            '--os-auth-url',
            '--os-project-id',
            '--os-project-name',
            '--os-tenant-id',
            '--os-tenant-name',
            '--os-domain-id',
            '--os-domain-name',
            '--os-project-domain-id',
            '--os-project-domain-name',
            '--os-user-domain-id',
            '--os-user-domain-name',
            '--os-username',
            '--os-user-id',
            '--os-password',
            '--os-trust-id',
            '--os-token',
            '--os-access-info',
            '--os-api-name',
            '--os-api-region',
            '--os-api-version',
            '--os-api-interface'
        ]

        options = [arg[0][0] for arg in parser.add_argument.call_args_list]
        self.assertEqual(expected, options)

        parser.add_mutually_exclusive_group.assert_called_once_with()
        group = parser.add_mutually_exclusive_group.return_value

        verify_opts = [arg[0][0] for arg in group.add_argument.call_args_list]
        verify_args = [
            '--os-cacert',
            '--verify',
            '--insecure'
        ]
        self.assertEqual(verify_args, verify_opts)

    def test_add_global_args(self):
        parser = mock.Mock()

        cliargs.add_global_args(parser, '1')
        expected = [
            '-h',
            '--version',
            '-d',
            '-v',
            '--api-timeout',
            '--senlin-api-version'
        ]

        options = [arg[0][0] for arg in parser.add_argument.call_args_list]
        self.assertEqual(expected, options)
