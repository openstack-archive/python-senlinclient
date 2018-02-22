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
from senlinclient.v1 import policy_type as osc_policy_type


class TestPolicyType(fakes.TestClusteringv1):
    def setUp(self):
        super(TestPolicyType, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestPolicyTypeList(TestPolicyType):
    expected_columns = ['name', 'version', 'support_status']
    pt1 = mock.Mock(
        schema={'foo': 'bar'},
        support_status={
            "1.0": [{"status": "SUPPORTED", "since": "2016.10"}]
        }
    )
    pt1.name = 'BBB'
    pt2 = mock.Mock(
        schema={'foo': 'bar'},
        support_status={
            "1.0": [{"status": "DEPRECATED", "since": "2016.01"}]
        }
    )
    pt2.name = 'AAA'
    list_response = [pt1, pt2]
    expected_rows = [
        ('AAA', '1.0', 'DEPRECATED since 2016.01'),
        ('BBB', '1.0', 'SUPPORTED since 2016.10')
    ]

    def setUp(self):
        super(TestPolicyTypeList, self).setUp()
        self.cmd = osc_policy_type.PolicyTypeList(self.app, None)
        self.mock_client.policy_types = mock.Mock(
            return_value=self.list_response)

    def test_policy_type_list(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        expected_columns = self.expected_columns
        expected_rows = self.expected_rows
        columns, rows = self.cmd.take_action(parsed_args)
        if len(columns) == 2:
            expected_columns = ['name', 'version']
            expected_rows = [
                ('CCC', '1.0')
            ]

        self.mock_client.policy_types.assert_called_with()
        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_rows, rows)


class TestPolicyTypeShow(TestPolicyType):

    def setUp(self):
        super(TestPolicyTypeShow, self).setUp()
        self.cmd = osc_policy_type.PolicyTypeShow(self.app, None)
        fake_pt = mock.Mock(schema={'foo': 'bar'})
        fake_pt.name = 'senlin.policy.deletion-1.0'
        self.mock_client.get_policy_type = mock.Mock(return_value=fake_pt)

    def test_policy_type_show(self):
        arglist = ['os.heat.stack-1.0']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_policy_type.assert_called_once_with(
            'os.heat.stack-1.0')

    def test_policy_type_show_not_found(self):
        arglist = ['senlin.policy.deletion-1.0']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_policy_type.side_effect = (
            sdk_exc.ResourceNotFound())
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Policy Type not found: senlin.policy.deletion-1.0',
                         str(error))
