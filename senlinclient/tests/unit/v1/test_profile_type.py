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

import mock
from openstack import exceptions as sdk_exc
from osc_lib import exceptions as exc

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import profile_type as osc_profile_type


class TestProfileType(fakes.TestClusteringv1):
    def setUp(self):
        super(TestProfileType, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestProfileTypeList(TestProfileType):

    def setUp(self):
        super(TestProfileTypeList, self).setUp()
        self.cmd = osc_profile_type.ProfileTypeList(self.app, None)
        pt1 = mock.Mock(
            schema={'foo': 'bar'},
            support_status={
                "1.0": [{"status": "SUPPORTED", "since": "2016.10"}]
            }
        )
        pt1.name = "BBB"
        pt2 = mock.Mock(
            schema={'foo': 'bar'},
            support_status={
                "1.0": [{"status": "DEPRECATED", "since": "2016.01"}]
            }
        )
        pt2.name = "AAA"
        self.mock_client.profile_types = mock.Mock(return_value=[pt1, pt2])

    def test_profile_type_list(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        expected_rows = [
            ('AAA', '1.0', 'DEPRECATED since 2016.01'),
            ('BBB', '1.0', 'SUPPORTED since 2016.10')
        ]
        expected_columns = ['name', 'version', 'support_status']

        columns, rows = self.cmd.take_action(parsed_args)
        if len(columns) == 2:
            expected_columns = ['name', 'version']
            expected_rows = [
                ('CCC', '1.0')
            ]

        self.mock_client.profile_types.assert_called_with()
        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_rows, rows)


class TestProfileTypeShow(TestProfileType):

    def setUp(self):
        super(TestProfileTypeShow, self).setUp()
        self.cmd = osc_profile_type.ProfileTypeShow(self.app, None)
        fake_profile_type = mock.Mock(
            schema={'foo': 'bar'},
            support_status={
                "1.0": [{"status": "DEPRECATED", "since": "2016.01"}]
            }
        )
        fake_profile_type.name = "os.heat.stack-1.0"
        fake_profile_type.to_dict = mock.Mock(return_value={})
        self.mock_client.get_profile_type = mock.Mock(
            return_value=fake_profile_type)

    def test_profile_type_show(self):
        arglist = ['os.heat.stack-1.0']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_profile_type.assert_called_once_with(
            'os.heat.stack-1.0')

    def test_profile_type_show_not_found(self):
        arglist = ['os.heat.stack-1.1']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_profile_type.side_effect = (
            sdk_exc.ResourceNotFound())
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Profile Type not found: os.heat.stack-1.1',
                         str(error))


class TestProfileTypeOperations(TestProfileType):
    def setUp(self):
        super(TestProfileTypeOperations, self).setUp()
        self.cmd = osc_profile_type.ProfileTypeOperations(self.app, None)
        fake_profile_type_ops = mock.Mock(
            {
                'options': {
                    'abandon': {
                        'required': False,
                        'type': 'Map',
                        'description': 'Abandon a heat stack node.',
                        'updatable': False
                    }
                }
            }
        )
        self.mock_client.list_profile_type_operations = mock.Mock(
            return_value=fake_profile_type_ops)

    def test_profile_type_operations(self):
        arglist = ['os.heat.stack-1.0']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.list_profile_type_operations.assert_called_once_with(
            'os.heat.stack-1.0')

    def test_profile_type_operations_not_found(self):
        arglist = ['os.heat.stack-1.1']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.list_profile_type_operations.side_effect = (
            sdk_exc.ResourceNotFound())
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Profile Type not found: os.heat.stack-1.1',
                         str(error))
