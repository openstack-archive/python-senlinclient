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
import subprocess

import mock
from openstack import exceptions as sdk_exc
from osc_lib import exceptions as exc
import six

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import cluster as osc_cluster


class TestCluster(fakes.TestClusteringv1):
    def setUp(self):
        super(TestCluster, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestClusterList(TestCluster):

    columns = ['id', 'name', 'status', 'created_at', 'updated_at']
    defaults = {
        'global_project': False,
        'marker': None,
        'limit': None,
        'sort': None,
    }

    def setUp(self):
        super(TestClusterList, self).setUp()
        self.cmd = osc_cluster.ListCluster(self.app, None)
        fake_cluster = mock.Mock(
            created_at="2015-02-10T14:26:14",
            data={},
            desired_capacity=4,
            domain_id=None,
            id="7d85f602-a948-4a30-afd4-e84f47471c15",
            init_time="2015-02-10T14:26:11",
            max_size=-1,
            metadata={},
            min_size=0,
            node_ids=[
                "b07c57c8-7ab2-47bf-bdf8-e894c0c601b9",
                "ecc23d3e-bb68-48f8-8260-c9cf6bcb6e61",
                "da1e9c87-e584-4626-a120-022da5062dac"
            ],
            policies=[],
            profile_id="edc63d0a-2ca4-48fa-9854-27926da76a4a",
            profile_name="mystack",
            project_id="6e18cc2bdbeb48a5b3cad2dc499f6804",
            status="ACTIVE",
            status_reason="Cluster scale-in succeeded",
            timeout=3600,
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_cluster.name = "cluster1"
        fake_cluster.to_dict = mock.Mock(return_value={})

        self.mock_client.clusters = mock.Mock(return_value=[fake_cluster])

    def test_cluster_list_defaults(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.clusters.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_cluster_list_full_id(self):
        arglist = ['--full-id']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.clusters.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_cluster_list_limit(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['limit'] = '3'
        arglist = ['--limit', '3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.clusters.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_cluster_list_sort(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:asc'
        arglist = ['--sort', 'name:asc']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.clusters.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_cluster_list_sort_invalid_key(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'bad_key'
        arglist = ['--sort', 'bad_key']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.clusters.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_cluster_list_sort_invalid_direction(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:bad_direction'
        arglist = ['--sort', 'name:bad_direction']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.clusters.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_cluster_list_filter(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['name'] = 'my_cluster'
        arglist = ['--filter', 'name=my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.clusters.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_cluster_list_marker(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['marker'] = 'a9448bf6'
        arglist = ['--marker', 'a9448bf6']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.clusters.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)


class TestClusterShow(TestCluster):

    def setUp(self):
        super(TestClusterShow, self).setUp()
        self.cmd = osc_cluster.ShowCluster(self.app, None)
        fake_cluster = mock.Mock(
            config={},
            created_at="2015-02-11T15:13:20",
            data={},
            desired_capacity=0,
            domain_id=None,
            id="7d85f602-a948-4a30-afd4-e84f47471c15",
            init_time="2015-02-10T14:26:11",
            max_size=-1,
            metadata={},
            min_size=0,
            node_ids=[],
            policies=[],
            profile_id="edc63d0a-2ca4-48fa-9854-27926da76a4a",
            profile_name="mystack",
            project_id="6e18cc2bdbeb48a5b3cad2dc499f6804",
            status="ACTIVE",
            status_reason="Cluster scale-in succeeded",
            timeout=3600,
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_cluster.name = "my_cluster"
        fake_cluster.to_dict = mock.Mock(return_value={})
        self.mock_client.get_cluster = mock.Mock(return_value=fake_cluster)

    def test_cluster_show(self):
        arglist = ['my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_cluster.assert_called_with('my_cluster')

    def test_cluster_show_not_found(self):
        arglist = ['my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_cluster.side_effect = sdk_exc.ResourceNotFound()
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Cluster not found: my_cluster', str(error))


class TestClusterCreate(TestCluster):

    defaults = {
        "config": {},
        "desired_capacity": 0,
        "max_size": -1,
        "metadata": {},
        "min_size": 0,
        "name": "test_cluster",
        "profile_id": "mystack",
        "timeout": None
    }

    def setUp(self):
        super(TestClusterCreate, self).setUp()
        self.cmd = osc_cluster.CreateCluster(self.app, None)
        fake_cluster = mock.Mock(
            config={},
            created_at="2015-02-11T15:13:20",
            data={},
            desired_capacity=0,
            domain_id=None,
            id="7d85f602-a948-4a30-afd4-e84f47471c15",
            init_time="2015-02-10T14:26:11",
            max_size=-1,
            metadata={},
            min_size=0,
            node_ids=[],
            policies=[],
            profile_id="edc63d0a-2ca4-48fa-9854-27926da76a4a",
            profile_name="mystack",
            project_id="6e18cc2bdbeb48a5b3cad2dc499f6804",
            status="ACTIVE",
            status_reason="Cluster scale-in succeeded",
            timeout=3600,
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_cluster.name = "my_cluster"
        fake_cluster.to_dict = mock.Mock(return_value={})
        self.mock_client.create_cluster = mock.Mock(return_value=fake_cluster)
        self.mock_client.get_cluster = mock.Mock(return_value=fake_cluster)

    def test_cluster_create_defaults(self):
        arglist = ['test_cluster', '--profile', 'mystack']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_cluster.assert_called_with(**self.defaults)

    def test_cluster_create_with_metadata(self):
        arglist = ['test_cluster', '--profile', 'mystack',
                   '--metadata', 'key1=value1;key2=value2']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['metadata'] = {'key1': 'value1', 'key2': 'value2'}
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_cluster.assert_called_with(**kwargs)

    def test_cluster_create_with_config(self):
        arglist = ['test_cluster', '--profile', 'mystack',
                   '--config', 'key1=value1;key2=value2']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['config'] = {'key1': 'value1', 'key2': 'value2'}
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_cluster.assert_called_with(**kwargs)

    def test_cluster_create_with_size(self):
        arglist = ['test_cluster', '--profile', 'mystack',
                   '--min-size', '1', '--max-size', '10',
                   '--desired-capacity', '2']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['min_size'] = '1'
        kwargs['max_size'] = '10'
        kwargs['desired_capacity'] = '2'
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_cluster.assert_called_with(**kwargs)


class TestClusterUpdate(TestCluster):

    defaults = {
        "metadata": {
            "nk1": "nv1",
            "nk2": "nv2",
        },
        "name": 'new_cluster',
        "profile_id": 'new_profile',
        "profile_only": False,
        "timeout": "30"
    }

    def setUp(self):
        super(TestClusterUpdate, self).setUp()
        self.cmd = osc_cluster.UpdateCluster(self.app, None)
        self.fake_cluster = mock.Mock(
            created_at="2015-02-11T15:13:20",
            data={},
            desired_capacity=0,
            domain_id=None,
            id="7d85f602-a948-4a30-afd4-e84f47471c15",
            init_time="2015-02-10T14:26:11",
            max_size=-1,
            metadata={},
            min_size=0,
            node_ids=[],
            policies=[],
            profile_id="edc63d0a-2ca4-48fa-9854-27926da76a4a",
            profile_name="mystack",
            project_id="6e18cc2bdbeb48a5b3cad2dc499f6804",
            status="ACTIVE",
            status_reason="Cluster scale-in succeeded",
            timeout=3600,
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        self.fake_cluster.name = "my_cluster"
        self.fake_cluster.to_dict = mock.Mock(return_value={})
        self.mock_client.update_cluster = mock.Mock(
            return_value=self.fake_cluster)
        self.mock_client.get_cluster = mock.Mock(
            return_value=self.fake_cluster)
        self.mock_client.find_cluster = mock.Mock(
            return_value=self.fake_cluster)

    def test_cluster_update_defaults(self):
        arglist = ['--name', 'new_cluster', '--metadata', 'nk1=nv1;nk2=nv2',
                   '--profile', 'new_profile', '--timeout', '30', '45edadcb']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.update_cluster.assert_called_with(
            self.fake_cluster, **self.defaults)

    def test_cluster_update_not_found(self):
        arglist = ['--name', 'new_cluster', '--metadata', 'nk1=nv1;nk2=nv2',
                   '--profile', 'new_profile', 'c6b8b252']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.find_cluster.return_value = None
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Cluster not found: c6b8b252', str(error))


class TestClusterDelete(TestCluster):
    def setUp(self):
        super(TestClusterDelete, self).setUp()
        self.cmd = osc_cluster.DeleteCluster(self.app, None)
        mock_cluster = mock.Mock(location='abc/fake_action_id')
        self.mock_client.delete_cluster = mock.Mock(return_value=mock_cluster)

    def test_cluster_delete(self):
        arglist = ['cluster1', 'cluster2', 'cluster3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_cluster.assert_has_calls(
            [mock.call('cluster1', False, False),
             mock.call('cluster2', False, False),
             mock.call('cluster3', False, False)]
        )

    def test_cluster_delete_force(self):
        arglist = ['cluster1', 'cluster2', 'cluster3', '--force']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_cluster.assert_has_calls(
            [mock.call('cluster1', False, False),
             mock.call('cluster2', False, False),
             mock.call('cluster3', False, False)]
        )

    def test_cluster_delete_force_delete(self):
        arglist = ['cluster1', 'cluster2', 'cluster3', '--force-delete']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_cluster.assert_has_calls(
            [mock.call('cluster1', False, True),
             mock.call('cluster2', False, True),
             mock.call('cluster3', False, True)]
        )

    def test_cluster_delete_not_found(self):
        arglist = ['my_cluster']
        self.mock_client.delete_cluster.side_effect = sdk_exc.ResourceNotFound
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        self.mock_client.delete_cluster.assert_has_calls(
            [mock.call('my_cluster', False, False)]
        )

    def test_cluster_delete_one_found_one_not_found(self):
        arglist = ['cluster1', 'cluster2']
        self.mock_client.delete_cluster.side_effect = (
            [None, sdk_exc.ResourceNotFound]
        )
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        self.mock_client.delete_cluster.assert_has_calls(
            [mock.call('cluster1', False, False),
             mock.call('cluster2', False, False)]
        )

    @mock.patch('sys.stdin', spec=six.StringIO)
    def test_cluster_delete_prompt_yes(self, mock_stdin):
        arglist = ['my_cluster']
        mock_stdin.isatty.return_value = True
        mock_stdin.readline.return_value = 'y'
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        mock_stdin.readline.assert_called_with()
        self.mock_client.delete_cluster.assert_called_with(
            'my_cluster', False, False)

    @mock.patch('sys.stdin', spec=six.StringIO)
    def test_cluster_delete_prompt_no(self, mock_stdin):
        arglist = ['my_cluster']
        mock_stdin.isatty.return_value = True
        mock_stdin.readline.return_value = 'n'
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        mock_stdin.readline.assert_called_with()
        self.mock_client.delete_cluster.assert_not_called()


class TestClusterResize(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}
    defaults = {
        "min_step": None,
        "adjustment_type": "EXACT_CAPACITY",
        "number": 2,
        "min_size": 1,
        "strict": True,
        "max_size": 20}

    def setUp(self):
        super(TestClusterResize, self).setUp()
        self.cmd = osc_cluster.ResizeCluster(self.app, None)
        self.mock_client.resize_cluster = mock.Mock(
            return_value=self.response)

    def test_cluster_resize_no_params(self):
        arglist = ['my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual(("At least one parameter of 'capacity', "
                          "'adjustment', 'percentage', 'min_size' and "
                          "'max_size' should be specified."), str(error))

    def test_cluster_resize_multi_params(self):
        arglist = ['--capacity', '2', '--percentage', '50.0', '--adjustment',
                   '1', '--min-size', '1', '--max-size', '20', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual("Only one of 'capacity', 'adjustment' "
                         "and 'percentage' can be specified.", str(error))

    def test_cluster_resize_capacity(self):
        arglist = ['--capacity', '2', '--min-size', '1', '--max-size', '20',
                   'my_cluster', '--strict']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.resize_cluster.assert_called_with('my_cluster',
                                                           **self.defaults)

    def test_cluster_resize_invalid_capacity(self):
        arglist = ['--capacity', '-1', '--min-size', '1', '--max-size', '20',
                   'my_cluster', '--strict']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Cluster capacity must be larger than or equal to'
                         ' zero.', str(error))

    def test_cluster_resize_adjustment(self):
        arglist = ['--adjustment', '1', '--min-size', '1', '--max-size', '20',
                   'my_cluster', '--strict']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['adjustment_type'] = 'CHANGE_IN_CAPACITY'
        kwargs['number'] = 1
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.resize_cluster.assert_called_with('my_cluster',
                                                           **kwargs)

    def test_cluster_resize_invalid_adjustment(self):
        arglist = ['--adjustment', '0', '--min-size', '1', '--max-size', '20',
                   'my_cluster', '--strict']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Adjustment cannot be zero.', str(error))

    def test_cluster_resize_percentage(self):
        arglist = ['--percentage', '50.0', '--min-size', '1', '--max-size',
                   '20', 'my_cluster', '--strict']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        kwargs = copy.deepcopy(self.defaults)
        kwargs['adjustment_type'] = 'CHANGE_IN_PERCENTAGE'
        kwargs['number'] = 50.0
        self.cmd.take_action(parsed_args)
        self.mock_client.resize_cluster.assert_called_with('my_cluster',
                                                           **kwargs)

    def test_cluster_resize_invalid_percentage(self):
        arglist = ['--percentage', '0', '--min-size', '1', '--max-size', '20',
                   'my_cluster', '--strict']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Percentage cannot be zero.', str(error))

    def test_cluster_resize_invalid_min_step_capacity(self):
        arglist = ['--capacity', '2', '--min-size', '1', '--max-size', '20',
                   'my_cluster', '--strict', '--min-step', '1']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Min step is only used with percentage.', str(error))

    def test_cluster_resize_invalid_min_size_capacity(self):
        arglist = ['--capacity', '2', '--min-size', '-1', '--max-size', '20',
                   'my_cluster', '--strict']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Min size cannot be less than zero.', str(error))

    def test_cluster_resize_invalid_max_size_capacity(self):
        arglist = ['--capacity', '2', '--min-size', '5', '--max-size', '3',
                   'my_cluster', '--strict']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Min size cannot be larger than max size.',
                         str(error))

    def test_cluster_resize_min_size_larger_than_capacity(self):
        arglist = ['--capacity', '3', '--min-size', '5', '--max-size', '10',
                   'my_cluster', '--strict']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Min size cannot be larger than the specified '
                         'capacity', str(error))

    def test_cluster_resize_invalid_max_size_less_capacity(self):
        arglist = ['--capacity', '15', '--min-size', '5', '--max-size', '10',
                   'my_cluster', '--strict']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Max size cannot be less than the specified '
                         'capacity.', str(error))


class TestClusterScaleIn(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterScaleIn, self).setUp()
        self.cmd = osc_cluster.ScaleInCluster(self.app, None)
        self.mock_client.scale_in_cluster = mock.Mock(
            return_value=self.response)

    def test_cluster_scale_in(self):
        arglist = ['--count', '2', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.scale_in_cluster.assert_called_with('my_cluster',
                                                             '2')


class TestClusterScaleOut(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterScaleOut, self).setUp()
        self.cmd = osc_cluster.ScaleOutCluster(self.app, None)
        self.mock_client.scale_out_cluster = mock.Mock(
            return_value=self.response)

    def test_cluster_scale_out(self):
        arglist = ['--count', '2', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.scale_out_cluster.assert_called_with('my_cluster',
                                                              '2')


class TestClusterPolicyAttach(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterPolicyAttach, self).setUp()
        self.cmd = osc_cluster.ClusterPolicyAttach(self.app, None)
        self.mock_client.attach_policy_to_cluster = mock.Mock(
            return_value=self.response)

    def test_cluster_policy_attach(self):
        arglist = ['--policy', 'my_policy', '--enabled', 'True', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.attach_policy_to_cluster.assert_called_with(
            'my_cluster',
            'my_policy',
            enabled=True)


class TestClusterPolicyDetach(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterPolicyDetach, self).setUp()
        self.cmd = osc_cluster.ClusterPolicyDetach(self.app, None)
        self.mock_client.detach_policy_from_cluster = mock.Mock(
            return_value=self.response)

    def test_cluster_policy_detach(self):
        arglist = ['--policy', 'my_policy', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.detach_policy_from_cluster.assert_called_with(
            'my_cluster',
            'my_policy')


class TestClusterNodeList(TestCluster):
    columns = ['id', 'name', 'index', 'status', 'physical_id', 'created_at']
    args = {
        'cluster_id': 'my_cluster',
        'marker': 'a9448bf6',
        'limit': '3',
        'sort': None,
    }

    def setUp(self):
        super(TestClusterNodeList, self).setUp()
        self.cmd = osc_cluster.ClusterNodeList(self.app, None)
        fake_node = mock.Mock(
            cluster_id="",
            created_at="2015-02-11T15:13:20",
            data={},
            details={},
            domain_id=None,
            id="7d85f602-a948-4a30-afd4-e84f47471c15",
            index=-1,
            init_at="2015-02-10T14:26:11",
            metadata={},
            phyiscal_id="cc028275-d078-4729-bf3e-154b7359814b",
            profile_id="edc63d0a-2ca4-48fa-9854-27926da76a4a",
            profile_name="mystack",
            project_id="6e18cc2bdbeb48a5b3cad2dc499f6804",
            status="ACTIVE",
            status_reason="Creation succeeded",
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_node.name = "node001"
        fake_node.to_dict = mock.Mock(return_value={})
        self.mock_client.nodes = mock.Mock(return_value=[fake_node])

    def test_cluster_node_list(self):
        arglist = ['--limit', '3', '--marker', 'a9448bf6', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.nodes.assert_called_with(**self.args)
        self.assertEqual(self.columns, columns)

    def test_cluster_node_list_full_id(self):
        arglist = ['--limit', '3', '--marker', 'a9448bf6', 'my_cluster',
                   '--full-id']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.nodes.assert_called_with(**self.args)
        self.assertEqual(self.columns, columns)

    def test_cluster_node_list_filter(self):
        kwargs = copy.deepcopy(self.args)
        kwargs['name'] = 'my_node'
        arglist = ['--limit', '3', '--marker', 'a9448bf6', 'my_cluster',
                   '--filter', 'name=my_node']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.nodes.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_cluster_node_list_sort(self):
        kwargs = copy.deepcopy(self.args)
        kwargs['name'] = 'my_node'
        kwargs['sort'] = 'name:asc'
        arglist = ['--limit', '3', '--marker', 'a9448bf6', 'my_cluster',
                   '--filter', 'name=my_node', '--sort', 'name:asc']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.nodes.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)


class TestClusterNodeAdd(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterNodeAdd, self).setUp()
        self.cmd = osc_cluster.ClusterNodeAdd(self.app, None)
        self.mock_client.add_nodes_to_cluster = mock.Mock(
            return_value=self.response)

    def test_cluster_node_add(self):
        arglist = ['--nodes', 'node1', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.add_nodes_to_cluster.assert_called_with(
            'my_cluster',
            ['node1'])

    def test_cluster_node_add_multi(self):
        arglist = ['--nodes', 'node1,node2', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.add_nodes_to_cluster.assert_called_with(
            'my_cluster',
            ['node1', 'node2'])


class TestClusterNodeDel(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterNodeDel, self).setUp()
        self.cmd = osc_cluster.ClusterNodeDel(self.app, None)
        self.mock_client.remove_nodes_from_cluster = mock.Mock(
            return_value=self.response)

    def test_cluster_node_delete(self):
        arglist = ['-d', 'True', '--nodes', 'node1', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.remove_nodes_from_cluster.assert_called_with(
            'my_cluster',
            ['node1'],
            destroy_after_deletion=True)

    def test_cluster_node_delete_without_destroy(self):
        arglist = ['-d', 'False', '--nodes', 'node1', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.remove_nodes_from_cluster.assert_called_with(
            'my_cluster',
            ['node1'],
            destroy_after_deletion=False)

    def test_cluster_node_delete_multi(self):
        arglist = ['--nodes', 'node1,node2', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.remove_nodes_from_cluster.assert_called_with(
            'my_cluster',
            ['node1', 'node2'],
            destroy_after_deletion=False)


class TestClusterCheck(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterCheck, self).setUp()
        self.cmd = osc_cluster.CheckCluster(self.app, None)
        self.mock_client.check_cluster = mock.Mock(
            return_value=self.response)

    def test_cluster_check(self):
        arglist = ['cluster1', 'cluster2', 'cluster3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.check_cluster.assert_has_calls(
            [mock.call('cluster1'), mock.call('cluster2'),
             mock.call('cluster3')]
        )

    def test_cluster_check_not_found(self):
        arglist = ['cluster1']
        self.mock_client.check_cluster.side_effect = sdk_exc.ResourceNotFound
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Cluster not found: cluster1', str(error))


class TestClusterRecover(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterRecover, self).setUp()
        self.cmd = osc_cluster.RecoverCluster(self.app, None)
        self.mock_client.recover_cluster = mock.Mock(
            return_value=self.response)

    def test_cluster_recover(self):
        arglist = ['cluster1', 'cluster2', 'cluster3', '--check', 'false']
        kwargs = {'check': False}
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.recover_cluster.assert_has_calls(
            [mock.call('cluster1', **kwargs), mock.call('cluster2', **kwargs),
             mock.call('cluster3', **kwargs)]
        )

    def test_cluster_recover_not_found(self):
        arglist = ['cluster1']
        self.mock_client.recover_cluster.side_effect = sdk_exc.ResourceNotFound
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Cluster not found: cluster1', str(error))


class TestClusterOp(TestCluster):

    response = {"action": "a3c6d04c-3fca-4e4a-b0b3-c0522ef711f1"}

    def setUp(self):
        super(TestClusterOp, self).setUp()
        self.cmd = osc_cluster.ClusterOp(self.app, None)
        self.mock_client.perform_operation_on_cluster = mock.Mock(
            return_value=self.response)

    def test_cluster_op(self):
        arglist = ['--operation', 'dance', '--params', 'style=tango',
                   'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.perform_operation_on_cluster.assert_called_once_with(
            'my_cluster',
            'dance',
            style='tango')

    def test_cluster_op_not_found(self):
        arglist = ['--operation', 'dance', 'cluster1']
        ex = sdk_exc.ResourceNotFound
        self.mock_client.perform_operation_on_cluster.side_effect = ex
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Cluster not found: cluster1', str(error))


class TestClusterCollect(TestCluster):
    response = [
        {
            "node_id": "8bb476c3-0f4c-44ee-9f64-c7b0260814de",
            "attr_value": "value 1",
        },
        {
            "node_id": "7d85f602-a948-4a30-afd4-e84f47471c15",
            "attr_value": "value 2",
        }
    ]

    def setUp(self):
        super(TestClusterCollect, self).setUp()
        self.cmd = osc_cluster.ClusterCollect(self.app, None)
        self.mock_client.collect_cluster_attrs = mock.Mock(
            return_value=self.response)

    def test_cluster_collect(self):
        arglist = ['--path', 'path.to.attr', 'cluster1']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.collect_cluster_attrs.assert_called_once_with(
            'cluster1', 'path.to.attr')
        self.assertEqual(['node_id', 'attr_value'], columns)

    def test_cluster_collect_with_full_id(self):
        arglist = ['--path', 'path.to.attr', '--full-id', 'cluster1']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.collect_cluster_attrs.assert_called_once_with(
            'cluster1', 'path.to.attr')
        self.assertEqual(['node_id', 'attr_value'], columns)


class TestClusterRun(TestCluster):
    attrs = [
        mock.Mock(node_id="NODE_ID1",
                  attr_value={"addresses": 'ADDRESS CONTENT 1'}),
        mock.Mock(node_id="NODE_ID2",
                  attr_value={"addresses": 'ADDRESS CONTENT 2'})
    ]

    def setUp(self):
        super(TestClusterRun, self).setUp()
        self.cmd = osc_cluster.ClusterRun(self.app, None)
        self.mock_client.collect_cluster_attrs = mock.Mock(
            return_value=self.attrs)

    @mock.patch('subprocess.Popen')
    def test__run_script(self, mock_proc):
        x_proc = mock.Mock(returncode=0)
        x_stdout = 'OUTPUT'
        x_stderr = 'ERROR'
        x_proc.communicate.return_value = (x_stdout, x_stderr)
        mock_proc.return_value = x_proc

        addr = {
            'private': [
                {
                    'OS-EXT-IPS:type': 'floating',
                    'version': 4,
                    'addr': '1.2.3.4',
                }
            ]
        }
        output = {}

        self.cmd._run_script('NODE_ID', addr, 'private', 'floating', 22,
                             'john', False, 'identity_path', 'echo foo',
                             '-f bar',
                             output=output)
        mock_proc.assert_called_once_with(
            ['ssh', '-4', '-p22', '-i identity_path', '-f bar', 'john@1.2.3.4',
             'echo foo'],
            stdout=subprocess.PIPE)
        self.assertEqual(
            {'status': 'SUCCEEDED (0)', 'output': 'OUTPUT', 'error': 'ERROR'},
            output)

    def test__run_script_network_not_found(self):
        addr = {'foo': 'bar'}
        output = {}

        self.cmd._run_script('NODE_ID', addr, 'private', 'floating', 22,
                             'john', False, 'identity_path', 'echo foo',
                             '-f bar',
                             output=output)
        self.assertEqual(
            {'status': 'FAILED',
             'error': "Node 'NODE_ID' is not attached to network 'private'."
             },
            output)

    def test__run_script_more_than_one_network(self):
        addr = {'foo': 'bar', 'koo': 'tar'}
        output = {}

        self.cmd._run_script('NODE_ID', addr, '', 'floating', 22, 'john',
                             False, 'identity_path', 'echo foo', '-f bar',
                             output=output)
        self.assertEqual(
            {'status': 'FAILED',
             'error': "Node 'NODE_ID' is attached to more than one "
                       "network. Please pick the network to use."},
            output)

    def test__run_script_no_network(self):
        addr = {}
        output = {}

        self.cmd._run_script('NODE_ID', addr, '', 'floating', 22, 'john',
                             False, 'identity_path', 'echo foo', '-f bar',
                             output=output)

        self.assertEqual(
            {'status': 'FAILED',
             'error': "Node 'NODE_ID' is not attached to any network."},
            output)

    def test__run_script_no_matching_address(self):
        addr = {
            'private': [
                {
                    'OS-EXT-IPS:type': 'fixed',
                    'version': 4,
                    'addr': '1.2.3.4',
                }
            ]
        }
        output = {}

        self.cmd._run_script('NODE_ID', addr, 'private', 'floating', 22,
                             'john', False, 'identity_path', 'echo foo',
                             '-f bar',
                             output=output)
        self.assertEqual(
            {'status': 'FAILED',
             'error': "No address that matches network 'private' and "
                      "type 'floating' of IPv4 has been found for node "
                      "'NODE_ID'."},
            output)

    def test__run_script_more_than_one_address(self):
        addr = {
            'private': [
                {
                    'OS-EXT-IPS:type': 'fixed',
                    'version': 4,
                    'addr': '1.2.3.4',
                },
                {
                    'OS-EXT-IPS:type': 'fixed',
                    'version': 4,
                    'addr': '5.6.7.8',
                },
            ]
        }

        output = {}

        self.cmd._run_script('NODE_ID', addr, 'private', 'fixed', 22, 'john',
                             False, 'identity_path', 'echo foo', '-f bar',
                             output=output)
        self.assertEqual(
            {'status': 'FAILED',
             'error': "More than one IPv4 fixed address found."},
            output)

    @mock.patch('threading.Thread')
    @mock.patch.object(osc_cluster.ClusterRun, '_run_script')
    def test_cluster_run(self, mock_script, mock_thread):
        arglist = [
            '--port', '22',
            '--address-type', 'fixed',
            '--network', 'private',
            '--user', 'root',
            '--identity-file', 'path-to-identity',
            '--ssh-options', '-f boo',
            '--script', 'script-file',
            'cluster1'
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])

        th1 = mock.Mock()
        th2 = mock.Mock()
        mock_thread.side_effect = [th1, th2]
        fake_script = 'blah blah'
        with mock.patch('senlinclient.v1.cluster.open',
                        mock.mock_open(read_data=fake_script)) as mock_open:
            self.cmd.take_action(parsed_args)

        self.mock_client.collect_cluster_attrs.assert_called_once_with(
            'cluster1', 'details')
        mock_open.assert_called_once_with('script-file', 'r')
        mock_thread.assert_has_calls([
            mock.call(target=mock_script,
                      args=('NODE_ID1', 'ADDRESS CONTENT 1', 'private',
                            'fixed', 22, 'root', False, 'path-to-identity',
                            'blah blah', '-f boo'),
                      kwargs={'output': {}}),
            mock.call(target=mock_script,
                      args=('NODE_ID2', 'ADDRESS CONTENT 2', 'private',
                            'fixed', 22, 'root', False, 'path-to-identity',
                            'blah blah', '-f boo'),
                      kwargs={'output': {}})
        ])
        th1.start.assert_called_once_with()
        th2.start.assert_called_once_with()
        th1.join.assert_called_once_with()
        th2.join.assert_called_once_with()
