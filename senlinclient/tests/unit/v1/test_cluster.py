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
import six

from openstack.cluster.v1 import cluster as sdk_cluster
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import cluster as osc_cluster


class TestCluster(fakes.TestClusteringv1):
    def setUp(self):
        super(TestCluster, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestClusterList(TestCluster):

    columns = ['id', 'name', 'status', 'created_at', 'updated_at']
    response = {"clusters": [
        {
            "created_at": "2015-02-10T14:26:14",
            "data": {},
            "desired_capacity": 4,
            "domain": 'null',
            "id": "7d85f602-a948-4a30-afd4-e84f47471c15",
            "init_time": "2015-02-10T14:26:11",
            "max_size": -1,
            "metadata": {},
            "min_size": 0,
            "name": "cluster1",
            "nodes": [
                "b07c57c8-7ab2-47bf-bdf8-e894c0c601b9",
                "ecc23d3e-bb68-48f8-8260-c9cf6bcb6e61",
                "da1e9c87-e584-4626-a120-022da5062dac"
            ],
            "policies": [],
            "profile_id": "edc63d0a-2ca4-48fa-9854-27926da76a4a",
            "profile_name": "mystack",
            "project": "6e18cc2bdbeb48a5b3cad2dc499f6804",
            "status": "ACTIVE",
            "status_reason": "Cluster scale-in succeeded",
            "timeout": 3600,
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
        super(TestClusterList, self).setUp()
        self.cmd = osc_cluster.ListCluster(self.app, None)
        self.mock_client.clusters = mock.Mock(
            return_value=self.response)

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
        self.mock_client.clusters = mock.Mock(
            return_value=self.response)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'bad_key'
        arglist = ['--sort', 'bad_key']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.clusters.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_cluster_list_sort_invalid_direction(self):
        self.mock_client.clusters = mock.Mock(
            return_value=self.response)
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
    get_response = {"cluster": {
        "created_at": "2015-02-11T15:13:20",
        "data": {},
        "desired_capacity": 0,
        "domain": 'null',
        "id": "45edadcb-c73b-4920-87e1-518b2f29f54b",
        "init_time": "2015-02-10T14:26:10",
        "max_size": -1,
        "metadata": {},
        "min_size": 0,
        "name": "my_cluster",
        "nodes": [],
        "policies": [],
        "profile_id": "edc63d0a-2ca4-48fa-9854-27926da76a4a",
        "profile_name": "mystack",
        "project": "6e18cc2bdbeb48a5b3cad2dc499f6804",
        "status": "ACTIVE",
        "status_reason": "Creation succeeded",
        "timeout": 3600,
        "updated_at": 'null',
        "user": "5e5bf8027826429c96af157f68dc9072"
    }}

    def setUp(self):
        super(TestClusterShow, self).setUp()
        self.cmd = osc_cluster.ShowCluster(self.app, None)
        self.mock_client.get_cluster = mock.Mock(
            return_value=sdk_cluster.Cluster(
                attrs=self.get_response['cluster']))

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
    response = {"cluster": {
        "action": "bbf4558b-9fa3-482a-93c2-a4aa5cc85317",
        "created_at": 'null',
        "data": {},
        "desired_capacity": 4,
        "domain": 'null',
        "id": "45edadcb-c73b-4920-87e1-518b2f29f54b",
        "init_at": "2015-02-10T14:16:10",
        "max_size": -1,
        "metadata": {},
        "min_size": 0,
        "name": "test_cluster",
        "nodes": [],
        "policies": [],
        "profile_id": "edc63d0a-2ca4-48fa-9854-27926da76a4a",
        "profile_name": "mystack",
        "project": "6e18cc2bdbeb48a5b3cad2dc499f6804",
        "status": "INIT",
        "status_reason": "Initializing",
        "timeout": 3600,
        "updated_at": 'null',
        "user": "5e5bf8027826429c96af157f68dc9072"
    }}

    defaults = {
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
        self.mock_client.create_cluster = mock.Mock(
            return_value=sdk_cluster.Cluster(attrs=self.response['cluster']))
        self.mock_client.get_cluster = mock.Mock(
            return_value=sdk_cluster.Cluster(attrs=self.response['cluster']))

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
    response = {"cluster": {
        "created_at": "2015-02-11T15:13:20",
        "data": {},
        "desired_capacity": 0,
        "domain": 'null',
        "id": "45edadcb-c73b-4920-87e1-518b2f29f54b",
        "init_time": "2015-02-10T14:26:10",
        "max_size": -1,
        "metadata": {},
        "min_size": 0,
        "name": "test_cluster",
        "nodes": [],
        "policies": [],
        "profile_id": "edc63d0a-2ca4-48fa-9854-27926da76a4a",
        "profile_name": "mystack",
        "project": "6e18cc2bdbeb48a5b3cad2dc499f6804",
        "status": "INIT",
        "status_reason": "Initializing",
        "timeout": 3600,
        "updated_at": 'null',
        "user": "5e5bf8027826429c96af157f68dc9072"
    }}

    defaults = {
        "metadata": {
            "nk1": "nv1",
            "nk2": "nv2",
        },
        "name": 'new_cluster',
        "profile_id": 'new_profile',
        "timeout": "30"
    }

    def setUp(self):
        super(TestClusterUpdate, self).setUp()
        self.cmd = osc_cluster.UpdateCluster(self.app, None)
        self.mock_client.update_cluster = mock.Mock(
            return_value=sdk_cluster.Cluster(attrs=self.response['cluster']))
        self.mock_client.get_cluster = mock.Mock(
            return_value=sdk_cluster.Cluster(attrs=self.response['cluster']))
        self.mock_client.find_cluster = mock.Mock(
            return_value=sdk_cluster.Cluster(attrs=self.response['cluster']))

    def test_cluster_update_defaults(self):
        arglist = ['--name', 'new_cluster', '--metadata', 'nk1=nv1;nk2=nv2',
                   '--profile', 'new_profile', '--timeout', '30', '45edadcb']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.update_cluster.assert_called_with(
            '45edadcb-c73b-4920-87e1-518b2f29f54b', **self.defaults)

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
        self.mock_client.delete_cluster = mock.Mock()

    def test_cluster_delete(self):
        arglist = ['cluster1', 'cluster2', 'cluster3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_cluster.assert_has_calls(
            [mock.call('cluster1', False), mock.call('cluster2', False),
             mock.call('cluster3', False)]
        )

    def test_cluster_delete_force(self):
        arglist = ['cluster1', 'cluster2', 'cluster3', '--force']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_cluster.assert_has_calls(
            [mock.call('cluster1', False), mock.call('cluster2', False),
             mock.call('cluster3', False)]
        )

    def test_cluster_delete_not_found(self):
        arglist = ['my_cluster']
        self.mock_client.delete_cluster.side_effect = sdk_exc.ResourceNotFound
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Failed to delete 1 of the 1 specified cluster(s).',
                      str(error))

    def test_cluster_delete_one_found_one_not_found(self):
        arglist = ['cluster1', 'cluster2']
        self.mock_client.delete_cluster.side_effect = (
            [None, sdk_exc.ResourceNotFound]
        )
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action, parsed_args)
        self.mock_client.delete_cluster.assert_has_calls(
            [mock.call('cluster1', False), mock.call('cluster2', False)]
        )
        self.assertEqual('Failed to delete 1 of the 2 specified cluster(s).',
                         str(error))

    @mock.patch('sys.stdin', spec=six.StringIO)
    def test_cluster_delete_prompt_yes(self, mock_stdin):
        arglist = ['my_cluster']
        mock_stdin.isatty.return_value = True
        mock_stdin.readline.return_value = 'y'
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        mock_stdin.readline.assert_called_with()
        self.mock_client.delete_cluster.assert_called_with('my_cluster',
                                                           False)

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
        self.mock_client.cluster_resize = mock.Mock(
            return_value=self.response)

    def test_cluster_resize_multi_params(self):
        arglist = ['--capacity', '2', '--percentage', '50.0', '--adjustment',
                   '1', '--min-size', '1', '--max-size', '20', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual("Only one of 'capacity', 'adjustment' "
                         "and 'percentage' can be specified.", str(error))

    def test_cluster_resize_none_params(self):
        arglist = ['--min-size', '1', '--max-size', '20', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertEqual("At least one of 'capacity', 'adjustment' and "
                         "'percentage' should be specified.", str(error))

    def test_cluster_resize_capacity(self):
        arglist = ['--capacity', '2', '--min-size', '1', '--max-size', '20',
                   'my_cluster', '--strict']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.cluster_resize.assert_called_with('my_cluster',
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
        self.mock_client.cluster_resize.assert_called_with('my_cluster',
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
        self.mock_client.cluster_resize.assert_called_with('my_cluster',
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
        self.mock_client.cluster_scale_in = mock.Mock(
            return_value=self.response)

    def test_cluster_scale_in(self):
        arglist = ['--count', '2', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.cluster_scale_in.assert_called_with('my_cluster',
                                                             '2')


class TestClusterScaleOut(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterScaleOut, self).setUp()
        self.cmd = osc_cluster.ScaleOutCluster(self.app, None)
        self.mock_client.cluster_scale_out = mock.Mock(
            return_value=self.response)

    def test_cluster_scale_in(self):
        arglist = ['--count', '2', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.cluster_scale_out.assert_called_with('my_cluster',
                                                              '2')


class TestClusterPolicyAttach(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterPolicyAttach, self).setUp()
        self.cmd = osc_cluster.ClusterPolicyAttach(self.app, None)
        self.mock_client.cluster_attach_policy = mock.Mock(
            return_value=self.response)

    def test_cluster_policy_attach(self):
        arglist = ['--policy', 'my_policy', '--enabled', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.cluster_attach_policy.assert_called_with(
            'my_cluster',
            'my_policy',
            enabled=True)


class TestClusterPolicyDetach(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterPolicyDetach, self).setUp()
        self.cmd = osc_cluster.ClusterPolicyDetach(self.app, None)
        self.mock_client.cluster_detach_policy = mock.Mock(
            return_value=self.response)

    def test_cluster_policy_detach(self):
        arglist = ['--policy', 'my_policy', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.cluster_detach_policy.assert_called_with(
            'my_cluster',
            'my_policy')


class TestClusterNodeList(TestCluster):
    columns = ['id', 'name', 'index', 'status', 'physical_id', 'created_at']

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

    args = {
        'cluster_id': 'my_cluster',
        'marker': 'a9448bf6',
        'limit': '3',
        'sort': None,
    }

    def setUp(self):
        super(TestClusterNodeList, self).setUp()
        self.cmd = osc_cluster.ClusterNodeList(self.app, None)
        self.mock_client.nodes = mock.Mock(
            return_value=self.response)

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
        self.mock_client.cluster_add_nodes = mock.Mock(
            return_value=self.response)

    def test_cluster_node_add(self):
        arglist = ['--nodes', 'node1', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.cluster_add_nodes.assert_called_with(
            'my_cluster',
            ['node1'])

    def test_cluster_node_add_multi(self):
        arglist = ['--nodes', 'node1,node2', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.cluster_add_nodes.assert_called_with(
            'my_cluster',
            ['node1', 'node2'])


class TestClusterNodeDel(TestCluster):
    response = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}

    def setUp(self):
        super(TestClusterNodeDel, self).setUp()
        self.cmd = osc_cluster.ClusterNodeDel(self.app, None)
        self.mock_client.cluster_del_nodes = mock.Mock(
            return_value=self.response)

    def test_cluster_node_delete(self):
        arglist = ['--nodes', 'node1', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.cluster_del_nodes.assert_called_with(
            'my_cluster',
            ['node1'])

    def test_cluster_node_delete_multi(self):
        arglist = ['--nodes', 'node1,node2', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.cluster_del_nodes.assert_called_with(
            'my_cluster',
            ['node1', 'node2'])


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

    def test_cluster_recoverk(self):
        arglist = ['cluster1', 'cluster2', 'cluster3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.recover_cluster.assert_has_calls(
            [mock.call('cluster1'), mock.call('cluster2'),
             mock.call('cluster3')]
        )

    def test_cluster_recover_not_found(self):
        arglist = ['cluster1']
        self.mock_client.recover_cluster.side_effect = sdk_exc.ResourceNotFound
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Cluster not found: cluster1', str(error))
