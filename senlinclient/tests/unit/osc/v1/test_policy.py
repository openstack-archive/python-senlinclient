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

import copy
import mock

from openstack.cluster.v1 import policy as sdk_policy
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc

from senlinclient.osc.v1 import policy as osc_policy
from senlinclient.tests.unit.osc.v1 import fakes


class TestPolicy(fakes.TestClusteringv1):
    def setUp(self):
        super(TestPolicy, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestPolicyList(TestPolicy):
    columns = ['id', 'name', 'type', 'created_at']
    response = {"policies": [
        {
            "created_at": "2015-02-15T08:33:13.000000",
            "data": {},
            "domain": 'null',
            "id": "7192d8df-73be-4e98-ab99-1cf6d5066729",
            "name": "test_policy_1",
            "project": "42d9e9663331431f97b75e25136307ff",
            "spec": {
                "description": "A test policy",
                "properties": {
                    "criteria": "OLDEST_FIRST",
                    "destroy_after_deletion": True,
                    "grace_period": 60,
                    "reduce_desired_capacity": False
                },
                "type": "senlin.policy.deletion",
                "version": "1.0"
            },
            "type": "senlin.policy.deletion-1.0",
            "updated_at": 'null',
            "user": "5e5bf8027826429c96af157f68dc9072"
        }
    ]}
    defaults = {
        'global_project': False,
        'marker': None,
        'limit': None,
        'sort': None,
    }

    def setUp(self):
        super(TestPolicyList, self).setUp()
        self.cmd = osc_policy.ListPolicy(self.app, None)
        self.mock_client.policies = mock.Mock(
            return_value=sdk_policy.Policy(None, {}))

    def test_policy_list_defaults(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_policy_list_full_id(self):
        arglist = ['--full-id']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_policy_list_limit(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['limit'] = '3'
        arglist = ['--limit', '3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_policy_list_sort(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:asc'
        arglist = ['--sort', 'name:asc']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_policy_list_sort_invalid_key(self):
        self.mock_client.policies = mock.Mock(
            return_value=self.response)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'bad_key'
        arglist = ['--sort', 'bad_key']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.policies.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_policy_list_sort_invalid_direction(self):
        self.mock_client.policies = mock.Mock(
            return_value=self.response)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:bad_direction'
        arglist = ['--sort', 'name:bad_direction']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.policies.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_policy_list_marker(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['marker'] = 'a9448bf6'
        arglist = ['--marker', 'a9448bf6']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_policy_list_filter(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['name'] = 'my_policy'
        arglist = ['--filter', 'name=my_policy']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)


class TestPolicyShow(TestPolicy):
    get_response = {"policy": {
        "created_at": "2015-03-02T07:40:31",
        "data": {},
        "domain": 'null',
        "id": "02f62195-2198-4797-b0a9-877632208527",
        "name": "sp001",
        "project": "42d9e9663331431f97b75e25136307ff",
        "spec": {
            "properties": {
                "adjustment": {
                    "best_effort": True,
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        },
        "type": "senlin.policy.scaling-1.0",
        "updated_at": 'null',
        "user": "5e5bf8027826429c96af157f68dc9072"
    }}

    def setUp(self):
        super(TestPolicyShow, self).setUp()
        self.cmd = osc_policy.ShowPolicy(self.app, None)
        self.mock_client.get_policy = mock.Mock(
            return_value=sdk_policy.Policy(None, self.get_response))

    def test_policy_show(self):
        arglist = ['sp001']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_policy.assert_called_with('sp001')

    def test_policy_show_not_found(self):
        arglist = ['sp001']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_policy.side_effect = sdk_exc.ResourceNotFound()
        self.assertRaises(exc.CommandError, self.cmd.take_action, parsed_args)
