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
import six

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import node as osc_node


class TestNode(fakes.TestClusteringv1):
    def setUp(self):
        super(TestNode, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestNodeList(TestNode):

    columns = ['id', 'name', 'index', 'status', 'cluster_id',
               'physical_id', 'profile_name', 'created_at', 'updated_at']

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
        fake_node = mock.Mock(
            cluster_id=None,
            created_at="2015-02-27T04:39:21",
            data={},
            details={},
            domain=None,
            id="573aa1ba-bf45-49fd-907d-6b5d6e6adfd3",
            index=-1,
            init_at="2015-02-27T04:39:18",
            metadata={},
            physical_id="cc028275-d078-4729-bf3e-154b7359814b",
            profile_id="edc63d0a-2ca4-48fa-9854-27926da76a4a",
            profile_name="mystack",
            project_id="6e18cc2bdbeb48a5b3cad2dc499f6804",
            role=None,
            status="ACTIVE",
            status_reason="Creation succeeded",
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_node.name = "node00a"
        fake_node.to_dict = mock.Mock(return_value={})
        self.mock_client.nodes = mock.Mock(return_value=[fake_node])

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
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'bad_key'
        arglist = ['--sort', 'bad_key']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.nodes.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_node_list_sort_invalid_direction(self):
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
    response = {"node": {
    }}

    def setUp(self):
        super(TestNodeShow, self).setUp()
        self.cmd = osc_node.ShowNode(self.app, None)
        fake_node = mock.Mock(
            cluster_id=None,
            created_at="2015-02-10T12:03:16",
            data={},
            details={"OS-DCF:diskConfig": "MANUAL"},
            domain_id=None,
            id="d5779bb0-f0a0-49c9-88cc-6f078adb5a0b",
            index=-1,
            init_at="2015-02-10T12:03:13",
            metadata={},
            physical_id="f41537fa-22ab-4bea-94c0-c874e19d0c80",
            profile_id="edc63d0a-2ca4-48fa-9854-27926da76a4a",
            profile_name="mystack",
            project_id="6e18cc2bdbeb48a5b3cad2dc499f6804",
            role=None,
            status="ACTIVE",
            status_reason="Creation succeeded",
            updated_at="2015-03-04T04:58:27",
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_node.name = "my_node"
        fake_node.to_dict = mock.Mock(
            return_value={'details': {'key': 'value'}}
        )
        self.mock_client.get_node = mock.Mock(return_value=fake_node)

    def test_node_show(self):
        arglist = ['my_node']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_node.assert_called_with('my_node', details=False)

    def test_node_show_with_details(self):
        arglist = ['my_node', '--details']
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        self.mock_client.get_node.assert_called_with(
            'my_node', details=True)

    def test_node_show_not_found(self):
        arglist = ['my_node']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_node.side_effect = sdk_exc.ResourceNotFound()
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Node not found: my_node', str(error))


class TestNodeCreate(TestNode):

    defaults = {
        "cluster_id": None,
        "metadata": {},
        "name": "my_node",
        "profile_id": "mystack",
        "role": None
    }

    def setUp(self):
        super(TestNodeCreate, self).setUp()
        self.cmd = osc_node.CreateNode(self.app, None)
        fake_node = mock.Mock(
            action="2366d440-c73e-4961-9254-6d1c3af7c167",
            cluster_id="",
            created_at=None,
            data={},
            domain=None,
            id="0df0931b-e251-4f2e-8719-4ebfda3627ba",
            index=-1,
            init_time="2015-03-05T08:53:15",
            metadata={},
            physical_id=None,
            profile_id="edc63d0a-2ca4-48fa-9854-27926da76a4a",
            profile_name="mystack",
            project_id="6e18cc2bdbeb48a5b3cad2dc499f6804",
            role="master",
            status="INIT",
            status_reason="Initializing",
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_node.name = "my_node"
        fake_node.to_dict = mock.Mock(return_value={})

        self.mock_client.create_node = mock.Mock(return_value=fake_node)
        self.mock_client.get_node = mock.Mock(return_value=fake_node)

    def test_node_create_defaults(self):
        arglist = ['my_node', '--profile', 'mystack']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_node.assert_called_with(**self.defaults)

    def test_node_create_with_metadata(self):
        arglist = ['my_node', '--profile', 'mystack',
                   '--metadata', 'key1=value1;key2=value2']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['metadata'] = {'key1': 'value1', 'key2': 'value2'}
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_node.assert_called_with(**kwargs)

    def test_node_create_with_cluster(self):
        arglist = ['my_node', '--profile', 'mystack',
                   '--cluster', 'mycluster']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['cluster_id'] = 'mycluster'
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_node.assert_called_with(**kwargs)

    def test_node_create_with_role(self):
        arglist = ['my_node', '--profile', 'mystack',
                   '--role', 'master']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['role'] = 'master'
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_node.assert_called_with(**kwargs)


class TestNodeUpdate(TestNode):

    defaults = {
        "name": "new_node",
        "metadata": {
            "nk1": "nv1",
            "nk2": "nv2",
        },
        "profile_id": "new_profile",
        "role": "new_role"
    }

    def setUp(self):
        super(TestNodeUpdate, self).setUp()
        self.cmd = osc_node.UpdateNode(self.app, None)
        fake_node = mock.Mock(
            action="2366d440-c73e-4961-9254-6d1c3af7c167",
            cluster_id="",
            created_at=None,
            data={},
            domain=None,
            id="0df0931b-e251-4f2e-8719-4ebfda3627ba",
            index=-1,
            init_time="2015-03-05T08:53:15",
            metadata={},
            physical_id=None,
            profile_id="edc63d0a-2ca4-48fa-9854-27926da76a4a",
            profile_name="mystack",
            project_id="6e18cc2bdbeb48a5b3cad2dc499f6804",
            role="master",
            status="INIT",
            status_reason="Initializing",
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_node.name = "my_node"
        fake_node.to_dict = mock.Mock(return_value={})
        self.mock_client.update_node = mock.Mock(return_value=fake_node)
        self.mock_client.get_node = mock.Mock(return_value=fake_node)
        self.mock_client.find_node = mock.Mock(return_value=fake_node)

    def test_node_update_defaults(self):
        arglist = ['--name', 'new_node', '--metadata', 'nk1=nv1;nk2=nv2',
                   '--profile', 'new_profile', '--role', 'new_role',
                   '0df0931b']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.update_node.assert_called_with(
            '0df0931b-e251-4f2e-8719-4ebfda3627ba', **self.defaults)

    def test_node_update_not_found(self):
        arglist = ['--name', 'new_node', '--metadata', 'nk1=nv1;nk2=nv2',
                   '--profile', 'new_profile', '--role', 'new_role',
                   'c6b8b252']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.find_node.return_value = None
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Node not found: c6b8b252', str(error))


class TestNodeDelete(TestNode):
    def setUp(self):
        super(TestNodeDelete, self).setUp()
        self.cmd = osc_node.DeleteNode(self.app, None)
        mock_node = mock.Mock(location='loc/fake_action_id')
        self.mock_client.delete_node = mock.Mock(return_value=mock_node)

    def test_node_delete(self):
        arglist = ['node1', 'node2', 'node3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_node.assert_has_calls(
            [mock.call('node1', False, False),
             mock.call('node2', False, False),
             mock.call('node3', False, False)]
        )

    def test_node_delete_force(self):
        arglist = ['node1', 'node2', 'node3', '--force']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_node.assert_has_calls(
            [mock.call('node1', False, False),
             mock.call('node2', False, False),
             mock.call('node3', False, False)]
        )

    def test_node_delete_force_delete(self):
        arglist = ['node1', 'node2', 'node3', '--force-delete']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_node.assert_has_calls(
            [mock.call('node1', False, True),
             mock.call('node2', False, True),
             mock.call('node3', False, True)]
        )

    def test_node_delete_not_found(self):
        arglist = ['my_node']
        self.mock_client.delete_node.side_effect = sdk_exc.ResourceNotFound
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        self.mock_client.delete_node.assert_has_calls(
            [mock.call('my_node', False, False)]
        )

    def test_node_delete_one_found_one_not_found(self):
        arglist = ['node1', 'node2']
        self.mock_client.delete_node.side_effect = (
            [None, sdk_exc.ResourceNotFound]
        )
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        self.mock_client.delete_node.assert_has_calls(
            [mock.call('node1', False, False),
             mock.call('node2', False, False)]
        )

    @mock.patch('sys.stdin', spec=six.StringIO)
    def test_node_delete_prompt_yes(self, mock_stdin):
        arglist = ['my_node']
        mock_stdin.isatty.return_value = True
        mock_stdin.readline.return_value = 'y'
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        mock_stdin.readline.assert_called_with()
        self.mock_client.delete_node.assert_called_with(
            'my_node', False, False)

    @mock.patch('sys.stdin', spec=six.StringIO)
    def test_node_delete_prompt_no(self, mock_stdin):
        arglist = ['my_node']
        mock_stdin.isatty.return_value = True
        mock_stdin.readline.return_value = 'n'
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        mock_stdin.readline.assert_called_with()
        self.mock_client.delete_node.assert_not_called()


class TestNodeCheck(TestNode):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestNodeCheck, self).setUp()
        self.cmd = osc_node.CheckNode(self.app, None)
        self.mock_client.check_node = mock.Mock(
            return_value=self.response)

    def test_node_check(self):
        arglist = ['node1', 'node2', 'node3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.check_node.assert_has_calls(
            [mock.call('node1'), mock.call('node2'),
             mock.call('node3')]
        )

    def test_node_check_not_found(self):
        arglist = ['node1']
        self.mock_client.check_node.side_effect = sdk_exc.ResourceNotFound
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Node not found: node1', str(error))


class TestNodeRecover(TestNode):

    action_id = "8bb476c3-0f4c-44ee-9f64-c7b0260814de"

    def setUp(self):
        super(TestNodeRecover, self).setUp()
        self.cmd = osc_node.RecoverNode(self.app, None)
        fake_res = {'action': self.action_id}
        self.mock_client.recover_node = mock.Mock(return_value=fake_res)

    def test_node_recover(self):
        arglist = ['node1', 'node2', 'node3', '--check', 'false']
        kwargs = {'check': False}
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.recover_node.assert_has_calls(
            [mock.call('node1', **kwargs), mock.call('node2', **kwargs),
             mock.call('node3', **kwargs)]
        )

    def test_node_recover_not_found(self):
        arglist = ['node1']
        self.mock_client.recover_node.side_effect = sdk_exc.ResourceNotFound
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Node not found: node1', str(error))


class TestNodeAdopt(TestNode):
    defaults = {
        "identity": "fake-resource-id",
        "metadata": {},
        "name": "my_node",
        "overrides": {},
        "role": None,
        "snapshot": False,
        "type": "os.nova.server-1.0"
    }

    def setUp(self):
        super(TestNodeAdopt, self).setUp()
        self.cmd = osc_node.AdoptNode(self.app, None)
        fake_node = mock.Mock(
            action="2366d440-c73e-4961-9254-6d1c3af7c167",
            cluster_id="",
            created_at=None,
            data={},
            domain=None,
            id="0df0931b-e251-4f2e-8719-4ebfda3627ba",
            index=-1,
            init_time="2015-03-05T08:53:15",
            metadata={},
            physical_id=None,
            profile_id="edc63d0a-2ca4-48fa-9854-27926da76a4a",
            profile_name="mystack",
            project_id="6e18cc2bdbeb48a5b3cad2dc499f6804",
            role="master",
            status="INIT",
            status_reason="Initializing",
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_node.name = "my_node"
        fake_node.to_dict = mock.Mock(return_value={})

        self.mock_client.adopt_node = mock.Mock(return_value=fake_node)
        self.mock_client.get_node = mock.Mock(return_value=fake_node)

    def test_node_adopt_defaults(self):
        arglist = ['--identity', 'fake-resource-id',
                   '--type', 'os.nova.server-1.0',
                   '--name', 'my_node']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.adopt_node.assert_called_with(False, **self.defaults)

    def test_node_adopt_with_metadata(self):
        arglist = ['--identity', 'fake-resource-id',
                   '--type', 'os.nova.server-1.0',
                   '--metadata', 'key1=value1;key2=value2',
                   '--name', 'my_node']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['metadata'] = {'key1': 'value1', 'key2': 'value2'}
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.adopt_node.assert_called_with(False, **kwargs)

    def test_node_adopt_with_override(self):
        arglist = ['--identity', 'fake-resource-id',
                   '--type', 'os.nova.server-1.0',
                   '--overrides',
                   '{"networks": [{"network": "fake-net-name"}]}',
                   '--name', 'my_node']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['overrides'] = {'networks': [{'network': 'fake-net-name'}]}
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.adopt_node.assert_called_with(False, **kwargs)

    def test_node_adopt_with_role(self):
        arglist = ['--identity', 'fake-resource-id',
                   '--type', 'os.nova.server-1.0',
                   '--role', 'master',
                   '--name', 'my_node']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['role'] = 'master'
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.adopt_node.assert_called_with(False, **kwargs)

    def test_node_adopt_with_snapshot(self):
        arglist = ['--identity', 'fake-resource-id',
                   '--type', 'os.nova.server-1.0',
                   '--snapshot',
                   '--name', 'my_node']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        kwargs = copy.deepcopy(self.defaults)
        kwargs['snapshot'] = True
        self.cmd.take_action(parsed_args)
        self.mock_client.adopt_node.assert_called_with(False, **kwargs)


class TestNodeAdoptPreview(TestNode):
    defaults = {
        "identity": "fake-resource-id",
        "overrides": {},
        "snapshot": False,
        "type": "os.nova.server-1.0"
    }

    def setUp(self):
        super(TestNodeAdoptPreview, self).setUp()
        self.cmd = osc_node.AdoptNode(self.app, None)
        self.fake_node_preview = {
            "node_profile": {
                "node_preview": {
                    "properties": {

                    },
                    "type": "os.nova.server",
                    "version": "1.0"}
            }
        }

        self.mock_client.adopt_node = mock.Mock(
            return_value=self.fake_node_preview)
        self.mock_client.get_node = mock.Mock(
            return_value=self.fake_node_preview)

    def test_node_adopt_preview_default(self):
        arglist = ['--identity', 'fake-resource-id',
                   '--type', 'os.nova.server-1.0',
                   '--preview']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.adopt_node.assert_called_with(True, **self.defaults)

    def test_node_adopt_preview_with_overrides(self):
        arglist = ['--identity', 'fake-resource-id',
                   '--type', 'os.nova.server-1.0',
                   '--overrides',
                   '{"networks": [{"network": "fake-net-name"}]}',
                   '--preview']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        kwargs = copy.deepcopy(self.defaults)
        kwargs['overrides'] = {'networks': [{'network': 'fake-net-name'}]}
        self.cmd.take_action(parsed_args)
        self.mock_client.adopt_node.assert_called_with(True, **kwargs)

    def test_node_adopt_preview_with_snapshot(self):
        arglist = ['--identity', 'fake-resource-id',
                   '--type', 'os.nova.server-1.0',
                   '--snapshot', '--preview']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        kwargs = copy.deepcopy(self.defaults)
        kwargs['snapshot'] = True
        self.cmd.take_action(parsed_args)
        self.mock_client.adopt_node.assert_called_with(True, **kwargs)


class TestNodeOp(TestNode):

    response = {"action": "1db0f5c5-9183-4c47-9ef1-a5a97402a2c1"}

    def setUp(self):
        super(TestNodeOp, self).setUp()
        self.cmd = osc_node.NodeOp(self.app, None)
        self.mock_client.perform_operation_on_node = mock.Mock(
            return_value=self.response)

    def test_node_op(self):
        arglist = ['--operation', 'dance', '--params', 'style=tango',
                   'my_node']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.perform_operation_on_node.assert_called_once_with(
            'my_node',
            'dance',
            style='tango')

    def test_node_op_not_found(self):
        arglist = ['--operation', 'dance', 'node1']
        ex = sdk_exc.ResourceNotFound
        self.mock_client.perform_operation_on_node.side_effect = ex
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Node not found: node1', str(error))
