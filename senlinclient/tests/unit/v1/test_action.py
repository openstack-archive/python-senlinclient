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
from openstack import exceptions as sdk_exc
from osc_lib import exceptions as exc

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import action as osc_action


class TestAction(fakes.TestClusteringv1):

    def setUp(self):
        super(TestAction, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestActionList(TestAction):

    columns = ['id', 'name', 'action', 'status', 'target_id', 'depends_on',
               'depended_by', 'created_at']
    defaults = {
        'global_project': False,
        'marker': None,
        'limit': None,
        'sort': None,
    }

    def setUp(self):
        super(TestActionList, self).setUp()
        self.cmd = osc_action.ListAction(self.app, None)
        fake_action = mock.Mock(
            action="NODE_CREATE",
            cause="RPC Request",
            created_at="2015-12-04T04:54:41",
            depended_by=[],
            depends_on=[],
            end_time=1425550000.0,
            id="2366d440-c73e-4961-9254-6d1c3af7c167",
            inputs={},
            interval=-1,
            name="node_create_0df0931b",
            outputs={},
            owner=None,
            start_time=1425550000.0,
            status="SUCCEEDED",
            status_reason="Action completed successfully.",
            target_id="0df0931b-e251-4f2e-8719-4ebfda3627ba",
            timeout=3600,
            updated_at=None
        )
        fake_action.to_dict = mock.Mock(return_value={})
        self.mock_client.actions = mock.Mock(return_value=[fake_action])

    def test_action_list_defaults(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.actions.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_action_list_full_id(self):
        arglist = ['--full-id']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.actions.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_action_list_limit(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['limit'] = '3'
        arglist = ['--limit', '3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.actions.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_action_list_sort(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:asc'
        arglist = ['--sort', 'name:asc']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.actions.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_action_list_sort_invalid_key(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'bad_key'
        arglist = ['--sort', 'bad_key']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.actions.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_action_list_sort_invalid_direction(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:bad_direction'
        arglist = ['--sort', 'name:bad_direction']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.actions.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_action_list_filter(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['name'] = 'my_action'
        arglist = ['--filter', 'name=my_action']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.actions.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_action_list_marker(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['marker'] = 'a9448bf6'
        arglist = ['--marker', 'a9448bf6']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.actions.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)


class TestActionShow(TestAction):

    def setUp(self):
        super(TestActionShow, self).setUp()
        self.cmd = osc_action.ShowAction(self.app, None)
        fake_action = mock.Mock(
            action="NODE_CREATE",
            cause="RPC Request",
            created_at="2015-12-04T04:54:41",
            depended_by=[],
            depends_on=[],
            end_time=1425550000.0,
            id="2366d440-c73e-4961-9254-6d1c3af7c167",
            inputs={},
            interval=-1,
            name="node_create_0df0931b",
            outputs={},
            owner=None,
            start_time=1425550000.0,
            status="SUCCEEDED",
            status_reason="Action completed successfully.",
            target_id="0df0931b-e251-4f2e-8719-4ebfda3627ba",
            timeout=3600,
            updated_at=None
        )
        fake_action.to_dict = mock.Mock(return_value={})
        self.mock_client.get_action = mock.Mock(return_value=fake_action)

    def test_action_show(self):
        arglist = ['my_action']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_action.assert_called_with('my_action')

    def test_action_show_not_found(self):
        arglist = ['my_action']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_action.side_effect = sdk_exc.ResourceNotFound()
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Action not found: my_action', str(error))
