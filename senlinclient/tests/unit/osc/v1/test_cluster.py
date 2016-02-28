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

from openstack.cluster.v1 import cluster as sdk_cluster
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc

from senlinclient.osc.v1 import cluster as osc_cluster
from senlinclient.tests.unit.osc.v1 import fakes


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
            return_value=sdk_cluster.Cluster(None, {}))

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
            return_value=sdk_cluster.Cluster(None, self.get_response))

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
