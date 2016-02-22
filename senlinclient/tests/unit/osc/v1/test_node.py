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

from openstack.cluster.v1 import node as sdk_node
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc

from senlinclient.osc.v1 import node as osc_node
from senlinclient.tests.unit.osc.v1 import fakes


class TestNode(fakes.TestClusteringv1):
    def setUp(self):
        super(TestNode, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestNodeList(TestNode):

    columns = ['id', 'name', 'index', 'status', 'cluster_id',
               'physical_id', 'profile_name', 'created_at', 'updated_at']

    response = {"nodes": [
        {
            "cluster_id": None,
            "created_at": "2015-02-27T04:39:21",
            "data": {},
            "details": {},
            "domain": None,
            "id": "573aa1ba-bf45-49fd-907d-6b5d6e6adfd3",
            "index": -1,
            "init_at": "2015-02-27T04:39:18",
            "metadata": {},
            "name": "node00a",
            "physical_id": "cc028275-d078-4729-bf3e-154b7359814b",
            "profile_id": "edc63d0a-2ca4-48fa-9854-27926da76a4a",
            "profile_name": "mystack",
            "project": "6e18cc2bdbeb48a5b3cad2dc499f6804",
            "role": None,
            "status": "ACTIVE",
            "status_reason": "Creation succeeded",
            "updated_at": None,
            "user": "5e5bf8027826429c96af157f68dc9072"
        }
    ]}

    defaults = {
        'cluster_id': None,
        'global_project': False,
        'marker': None,
        'limit': None,
        'sort': None,
    }

    def setUp(self):
        super(TestNodeList, self).setUp()
        self.cmd = osc_node.ListNode(self.app, None)
        self.mock_client.nodes = mock.Mock(
            return_value=sdk_node.Node(None, {}))

    def test_node_list_defaults(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.nodes.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_node_list_full_id(self):
        arglist = ['--full-id']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.nodes.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_node_list_limit(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['limit'] = '3'
        arglist = ['--limit', '3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.nodes.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_node_list_sort(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:asc'
        arglist = ['--sort', 'name:asc']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.nodes.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_node_list_sort_invalid_key(self):
        self.mock_client.nodes = mock.Mock(
            return_value=self.response)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'bad_key'
        arglist = ['--sort', 'bad_key']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.nodes.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_node_list_sort_invalid_direction(self):
        self.mock_client.nodes = mock.Mock(
            return_value=self.response)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:bad_direction'
        arglist = ['--sort', 'name:bad_direction']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.nodes.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_node_list_filter(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['name'] = 'my_node'
        arglist = ['--filter', 'name=my_node']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.nodes.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_node_list_marker(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['marker'] = 'a9448bf6'
        arglist = ['--marker', 'a9448bf6']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.nodes.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)


class TestNodeShow(TestNode):
    get_response = {"node": {
        "cluster_id": None,
        "created_at": "2015-02-10T12:03:16",
        "data": {},
        "details": {
            "OS-DCF:diskConfig": "MANUAL"},
        "domain": None,
        "id": "d5779bb0-f0a0-49c9-88cc-6f078adb5a0b",
        "index": -1,
        "init_at": "2015-02-10T12:03:13",
        "metadata": {},
        "name": "my_node",
        "physical_id": "f41537fa-22ab-4bea-94c0-c874e19d0c80",
        "profile_id": "edc63d0a-2ca4-48fa-9854-27926da76a4a",
        "profile_name": "mystack",
        "project": "6e18cc2bdbeb48a5b3cad2dc499f6804",
        "role": None,
        "status": "ACTIVE",
        "status_reason": "Creation succeeded",
        "updated_at": "2015-03-04T04:58:27",
        "user": "5e5bf8027826429c96af157f68dc9072"
    }}

    def setUp(self):
        super(TestNodeShow, self).setUp()
        self.cmd = osc_node.ShowNode(self.app, None)
        self.mock_client.get_node = mock.Mock(
            return_value=sdk_node.Node(None, self.get_response))

    def test_node_show(self):
        arglist = ['my_node']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_node.assert_called_with('my_node', args=None)

    def test_node_show_with_details(self):
        arglist = ['my_node', '--details']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_node.assert_called_with(
            'my_node', args={'show_details': True})

    def test_node_show_not_found(self):
        arglist = ['my_node']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_node.side_effect = sdk_exc.ResourceNotFound()
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Node not found: my_node', str(error))
