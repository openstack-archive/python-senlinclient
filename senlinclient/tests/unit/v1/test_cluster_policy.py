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

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import cluster_policy as osc_cluster_policy


class TestClusterPolicy(fakes.TestClusteringv1):
    def setUp(self):
        super(TestClusterPolicy, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestClusterPolicyList(TestClusterPolicy):

    def setUp(self):
        super(TestClusterPolicyList, self).setUp()
        self.cmd = osc_cluster_policy.ClusterPolicyList(self.app, None)
        fake_cluster = mock.Mock(id='C1')
        self.mock_client.get_cluster = mock.Mock(return_value=fake_cluster)
        fake_binding = mock.Mock(
            cluster_id="7d85f602-a948-4a30-afd4-e84f47471c15",
            cluster_name="my_cluster",
            is_enabled=True,
            id="06be3a1f-b238-4a96-a737-ceec5714087e",
            policy_id="714fe676-a08f-4196-b7af-61d52eeded15",
            policy_name="my_policy",
            policy_type="senlin.policy.deletion-1.0"
        )
        fake_binding.to_dict = mock.Mock(return_value={})
        self.mock_client.cluster_policies = mock.Mock(
            return_value=[fake_binding])

    def test_cluster_policy_list(self):
        arglist = ['--sort', 'name:asc', '--filter', 'name=my_policy',
                   'my_cluster', '--full-id']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        expected_columns = ['policy_id', 'policy_name', 'policy_type',
                            'is_enabled']

        columns, data = self.cmd.take_action(parsed_args)

        self.mock_client.get_cluster.assert_called_with('my_cluster')
        self.mock_client.cluster_policies.assert_called_with(
            'C1', name="my_policy", sort="name:asc")
        self.assertEqual(expected_columns, columns)


class TestClusterPolicyShow(TestClusterPolicy):

    def setUp(self):
        super(TestClusterPolicyShow, self).setUp()
        self.cmd = osc_cluster_policy.ClusterPolicyShow(self.app, None)
        fake_binding = mock.Mock(
            cluster_id="7d85f602-a948-4a30-afd4-e84f47471c15",
            cluster_name="my_cluster",
            is_enabled=True,
            id="06be3a1f-b238-4a96-a737-ceec5714087e",
            policy_id="714fe676-a08f-4196-b7af-61d52eeded15",
            policy_name="my_policy",
            policy_type="senlin.policy.deletion-1.0"
        )
        fake_binding.to_dict = mock.Mock(return_value={})
        self.mock_client.get_cluster_policy = mock.Mock(
            return_value=fake_binding)

    def test_cluster_policy_show(self):
        arglist = ['--policy', 'my_policy', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_cluster_policy.assert_called_with('my_policy',
                                                               'my_cluster')


class TestClusterPolicyUpdate(TestClusterPolicy):

    def setUp(self):
        super(TestClusterPolicyUpdate, self).setUp()
        self.cmd = osc_cluster_policy.ClusterPolicyUpdate(self.app, None)
        fake_resp = {"action": "8bb476c3-0f4c-44ee-9f64-c7b0260814de"}
        self.mock_client.update_cluster_policy = mock.Mock(
            return_value=fake_resp)

    def test_cluster_policy_update(self):
        arglist = ['--policy', 'my_policy', '--enabled', 'true', 'my_cluster']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.update_cluster_policy.assert_called_with(
            'my_cluster', 'my_policy', enabled=True)
