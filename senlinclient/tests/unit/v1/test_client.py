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
import testtools

from senlinclient import plugin
from senlinclient.v1 import client


@mock.patch.object(plugin, 'create_connection')
class ClientTest(testtools.TestCase):

    def setUp(self):
        super(ClientTest, self).setUp()
        self.conn = mock.Mock()
        self.service = mock.Mock()
        self.conn.cluster = self.service

    def test_init_default(self, mock_conn):
        mock_conn.return_value = self.conn

        sc = client.Client()

        self.assertEqual(self.conn, sc.conn)
        self.assertEqual(self.service, sc.service)
        mock_conn.assert_called_once_with(prof=None, user_agent=None)

    def test_init_with_params(self, mock_conn):
        mock_conn.return_value = self.conn

        sc = client.Client(prof='FOO', user_agent='BAR', zoo='LARR')

        self.assertEqual(self.conn, sc.conn)
        self.assertEqual(self.service, sc.service)
        mock_conn.assert_called_once_with(prof='FOO', user_agent='BAR',
                                          zoo='LARR')

    def test_profile_types(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.profile_types(foo='bar')
        self.assertEqual(self.service.profile_types.return_value, res)
        self.service.profile_types.assert_called_once_with(foo='bar')

    def test_get_profile_type(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_profile_type('FOOBAR')
        self.assertEqual(self.service.get_profile_type.return_value, res)
        self.service.get_profile_type.assert_called_once_with('FOOBAR')

    def test_profiles(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.profiles(foo='bar')
        self.assertEqual(self.service.profiles.return_value, res)
        self.service.profiles.assert_called_once_with(foo='bar')

    def test_get_profile(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_profile('FOOBAR')
        self.assertEqual(self.service.get_profile.return_value, res)
        self.service.get_profile.assert_called_once_with('FOOBAR')

    def test_update_profile(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.update_profile('FAKE_ID', foo='bar')
        self.assertEqual(self.service.update_profile.return_value, res)
        self.service.update_profile.assert_called_once_with('FAKE_ID',
                                                            foo='bar')

    def test_delete_profile(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.delete_profile('FAKE_ID')
        self.assertEqual(self.service.delete_profile.return_value, res)
        self.service.delete_profile.assert_called_once_with(
            'FAKE_ID', True)

    def test_delete_profile_ignore_missing(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.delete_profile('FAKE_ID', False)
        self.assertEqual(self.service.delete_profile.return_value, res)
        self.service.delete_profile.assert_called_once_with(
            'FAKE_ID', False)

    def test_policy_types(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.policy_types(foo='bar')
        self.assertEqual(self.service.policy_types.return_value, res)
        self.service.policy_types.assert_called_once_with(foo='bar')

    def test_get_policy_type(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_policy_type('FOOBAR')
        self.assertEqual(self.service.get_policy_type.return_value, res)
        self.service.get_policy_type.assert_called_once_with('FOOBAR')

    def test_policies(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.policies(foo='bar')
        self.assertEqual(self.service.policies.return_value, res)
        self.service.policies.assert_called_once_with(foo='bar')

    def test_get_policy(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_policy('FOOBAR')
        self.assertEqual(self.service.get_policy.return_value, res)
        self.service.get_policy.assert_called_once_with('FOOBAR')

    def test_update_policy(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.update_policy('FAKE_ID', foo='bar')
        self.assertEqual(self.service.update_policy.return_value, res)
        self.service.update_policy.assert_called_once_with(
            'FAKE_ID', foo='bar')

    def test_delete_policy(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.delete_policy('FAKE_ID')
        self.assertEqual(self.service.delete_policy.return_value, res)
        self.service.delete_policy.assert_called_once_with(
            'FAKE_ID', True)

    def test_delete_policy_ignore_missing(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.delete_policy('FAKE_ID', False)
        self.assertEqual(self.service.delete_policy.return_value, res)
        self.service.delete_policy.assert_called_once_with(
            'FAKE_ID', False)

    def test_clusters(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.clusters(foo='bar')
        self.assertEqual(self.service.clusters.return_value, res)
        self.service.clusters.assert_called_once_with(foo='bar')

    def test_get_cluster(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_cluster('FOOBAR')
        self.assertEqual(self.service.get_cluster.return_value, res)
        self.service.get_cluster.assert_called_once_with('FOOBAR')

    def test_create_cluster(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.create_cluster(name='FOO', bar='zoo')
        self.assertEqual(self.service.create_cluster.return_value, res)
        self.service.create_cluster.assert_called_once_with(
            name='FOO', bar='zoo')

    def test_update_cluster(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.update_cluster('FAKE_ID', foo='bar')
        self.assertEqual(self.service.update_cluster.return_value, res)
        self.service.update_cluster.assert_called_once_with(
            'FAKE_ID', foo='bar')

    def test_delete_cluster(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.delete_cluster('FAKE_ID', True)
        self.assertEqual(self.service.delete_cluster.return_value, res)
        self.service.delete_cluster.assert_called_once_with(
            'FAKE_ID', True, False)

    def test_delete_cluster_ignore_missing(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.delete_cluster('FAKE_ID', True, False)
        self.assertEqual(self.service.delete_cluster.return_value, res)
        self.service.delete_cluster.assert_called_once_with(
            'FAKE_ID', True, False)

    def test_cluster_add_nodes(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.cluster_add_nodes('FAKE_ID', ['NODE1', 'NODE2'])
        self.assertEqual(self.service.add_nodes_to_cluster.return_value, res)
        self.service.add_nodes_to_cluster.assert_called_once_with(
            'FAKE_ID', ['NODE1', 'NODE2'])

    def test_cluster_del_nodes(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.cluster_del_nodes('FAKE_ID', ['NODE1', 'NODE2'])
        self.assertEqual(self.service.remove_nodes_from_cluster.return_value,
                         res)
        self.service.remove_nodes_from_cluster.assert_called_once_with(
            'FAKE_ID', ['NODE1', 'NODE2'])

    def test_cluster_resize(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.cluster_resize('FAKE_ID', foo='bar', zoo=1)
        self.assertEqual(self.service.resize_cluster.return_value, res)
        self.service.resize_cluster.assert_called_once_with(
            'FAKE_ID', foo='bar', zoo=1)

    def test_cluster_scale_in(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.cluster_scale_in('FAKE_ID', 3)
        self.assertEqual(self.service.scale_in_cluster.return_value, res)
        self.service.scale_in_cluster.assert_called_once_with(
            'FAKE_ID', 3)

    def test_cluster_scale_out(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.cluster_scale_out('FAKE_ID', 3)
        self.assertEqual(self.service.scale_out_cluster.return_value, res)
        self.service.scale_out_cluster.assert_called_once_with(
            'FAKE_ID', 3)

    def test_cluster_policies(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.cluster_policies('CLUSTER', foo='bar')
        self.assertEqual(self.service.cluster_policies.return_value, res)
        self.service.cluster_policies.assert_called_once_with(
            'CLUSTER', foo='bar')

    def test_get_cluster_policy(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_cluster_policy('PID', 'CID')
        self.assertEqual(self.service.get_cluster_policy.return_value, res)
        self.service.get_cluster_policy.assert_called_once_with(
            'PID', 'CID')

    def test_cluster_attach_policy(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.cluster_attach_policy('FOO', 'BAR', zoo='car')
        self.assertEqual(self.service.attach_policy_to_cluster.return_value,
                         res)
        self.service.attach_policy_to_cluster.assert_called_once_with(
            'FOO', 'BAR', zoo='car')

    def test_cluster_detach_policy(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.cluster_detach_policy('FOO', 'BAR')
        self.assertEqual(self.service.detach_policy_from_cluster.return_value,
                         res)
        self.service.detach_policy_from_cluster.assert_called_once_with(
            'FOO', 'BAR')

    def test_cluster_update_policy(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.cluster_update_policy('FOO', 'BAR', foo='bar')
        self.assertEqual(self.service.update_cluster_policy.return_value, res)
        self.service.update_cluster_policy.assert_called_once_with(
            'FOO', 'BAR', foo='bar')

    def test_check_cluster(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.check_cluster('FAKE_CLUSTER_ID')
        self.assertEqual(self.service.check_cluster.return_value, res)
        self.service.check_cluster.assert_called_once_with('FAKE_CLUSTER_ID')

    def test_recover_cluster(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.recover_cluster('FAKE_CLUSTER_ID')
        self.assertEqual(self.service.recover_cluster.return_value, res)
        self.service.recover_cluster.assert_called_once_with(
            'FAKE_CLUSTER_ID')

    def test_nodes(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.nodes(foo='bar')
        self.assertEqual(self.service.nodes.return_value, res)
        self.service.nodes.assert_called_once_with(foo='bar')

    def test_get_node(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_node('FOOBAR')
        self.assertEqual(self.service.get_node.return_value, res)
        self.service.get_node.assert_called_once_with('FOOBAR', details=False)

    def test_get_node_with_details(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_node('FOOBAR', details=True)
        self.assertEqual(self.service.get_node.return_value, res)
        self.service.get_node.assert_called_once_with(
            'FOOBAR', details=True)

    def test_create_node(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.create_node(name='FAKE_NAME', foo='bar')
        self.assertEqual(self.service.create_node.return_value, res)
        self.service.create_node.assert_called_once_with(
            name='FAKE_NAME', foo='bar')

    def test_update_node(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.update_node('FAKE_ID', foo='bar')
        self.assertEqual(self.service.update_node.return_value, res)
        self.service.update_node.assert_called_once_with(
            'FAKE_ID', foo='bar')

    def test_delete_node(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.delete_node('FAKE_ID', True)
        self.assertEqual(self.service.delete_node.return_value, res)
        self.service.delete_node.assert_called_once_with(
            'FAKE_ID', True, False)

    def test_check_node(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.check_node('FAKE_ID')
        self.assertEqual(self.service.check_node.return_value, res)
        self.service.check_node.assert_called_once_with('FAKE_ID')

    def test_recover_node(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.recover_node('FAKE_ID')
        self.assertEqual(self.service.recover_node.return_value, res)
        self.service.recover_node.assert_called_once_with(
            'FAKE_ID')

    def test_delete_node_ignore_missing(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.delete_node('FAKE_ID', True, False)
        self.assertEqual(self.service.delete_node.return_value, res)
        self.service.delete_node.assert_called_once_with(
            'FAKE_ID', True, False)

    def test_receivers(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.receivers(foo='bar')
        self.assertEqual(self.service.receivers.return_value, res)
        self.service.receivers.assert_called_once_with(foo='bar')

    def test_get_receiver(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_receiver('FOOBAR')
        self.assertEqual(self.service.get_receiver.return_value, res)
        self.service.get_receiver.assert_called_once_with('FOOBAR')

    def test_create_receiver(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.create_receiver(name='FAKE_NAME', foo='bar')
        self.assertEqual(self.service.create_receiver.return_value, res)
        self.service.create_receiver.assert_called_once_with(
            name='FAKE_NAME', foo='bar')

    def test_delete_receiver(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.delete_receiver('FAKE_ID')
        self.assertEqual(self.service.delete_receiver.return_value, res)
        self.service.delete_receiver.assert_called_once_with(
            'FAKE_ID', True)

    def test_delete_receiver_ignore_missing(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.delete_receiver('FAKE_ID', False)
        self.assertEqual(self.service.delete_receiver.return_value, res)
        self.service.delete_receiver.assert_called_once_with(
            'FAKE_ID', False)

    def test_actions(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.actions(foo='bar')
        self.assertEqual(self.service.actions.return_value, res)
        self.service.actions.assert_called_once_with(foo='bar')

    def test_get_action(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_action('FOOBAR')
        self.assertEqual(self.service.get_action.return_value, res)
        self.service.get_action.assert_called_once_with('FOOBAR')

    def test_events(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.events(foo='bar')
        self.assertEqual(self.service.events.return_value, res)
        self.service.events.assert_called_once_with(foo='bar')

    def test_get_event(self, mock_conn):
        mock_conn.return_value = self.conn
        sc = client.Client()

        res = sc.get_event('FOOBAR')
        self.assertEqual(self.service.get_event.return_value, res)
        self.service.get_event.assert_called_once_with('FOOBAR')
