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

from openstack.cluster.v1 import profile_type as sdk_profile_type
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import profile_type as osc_profile_type


class TestProfileType(fakes.TestClusteringv1):
    def setUp(self):
        super(TestProfileType, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestProfileTypeList(TestProfileType):
    expected_columns = ['name']
    list_response = [
        sdk_profile_type.ProfileType({'name': 'BBB',
                                      'schema': {
                                          'foo': 'bar'}}
                                     ),
        sdk_profile_type.ProfileType({'name': 'AAA',
                                      'schema': {
                                          'foo': 'bar'}}
                                     ),
        sdk_profile_type.ProfileType({'name': 'CCC',
                                      'schema': {
                                          'foo': 'bar'}}
                                     ),
    ]
    expected_rows = [
        ['AAA'],
        ['BBB'],
        ['CCC']
    ]

    def setUp(self):
        super(TestProfileTypeList, self).setUp()
        self.cmd = osc_profile_type.ProfileTypeList(self.app, None)
        self.mock_client.profile_types = mock.Mock(
            return_value=self.list_response)

    def test_profile_type_list(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, rows = self.cmd.take_action(parsed_args)

        self.mock_client.profile_types.assert_called_with()
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_rows, rows)


class TestProfileTypeShow(TestProfileType):

    response = ({'name': 'os.heat.stack-1.0',
                 'schema': {
                     'foo': 'bar'}})

    def setUp(self):
        super(TestProfileTypeShow, self).setUp()
        self.cmd = osc_profile_type.ProfileTypeShow(self.app, None)
        self.mock_client.get_profile_type = mock.Mock(
            return_value=sdk_profile_type.ProfileType(self.response)
        )

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
