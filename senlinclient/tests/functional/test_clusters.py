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

from senlinclient.tests.functional import base


class ClusterTest(base.OpenStackClientTestBase):
    """Test for clusters"""

    def test_cluster_list(self):
        result = self.openstack('cluster list')
        cluster_list = self.parser.listing(result)
        self.assertTableStruct(cluster_list, ['id', 'name', 'status',
                                              'created_at', 'updated_at'])

    def test_cluster_list_filters(self):
        params = {'name': 'test1', 'status': 'ACTIVE'}
        for k, v in params.items():
            cmd = ('cluster list --filters %s=%s' % (k, v))
            self.openstack(cmd)

    def test_cluster_list_sort(self):
        params = ['name', 'status', 'init_at', 'created_at', 'updated_at']
        for param in params:
            cmd = 'cluster list --sort %s' % param
            self.openstack(cmd)

    def test_cluster_full_id(self):
        self.openstack('cluster list --full-id')

    def test_cluster_limit(self):
        self.openstack('cluster list --limit 1')

    def test_cluster_create(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name, 1)
        self.addCleanup(self.cluster_delete, cluster['id'])
        cluster_raw = self.openstack('cluster show %s' % name)
        cluster_data = self.show_to_dict(cluster_raw)
        self.assertEqual(cluster_data['name'], name)
        self.assertEqual(cluster_data['status'], 'ACTIVE')
        self.assertEqual(cluster_data['desired_capacity'], '1')

    def test_cluster_update(self):
        old_name = self.name_generate()
        old_pf = self.profile_create(old_name)
        self.addCleanup(self.profile_delete, old_pf['id'])
        new_name = self.name_generate()
        new_pf = self.profile_create(new_name)
        self.addCleanup(self.profile_delete, new_pf['id'])
        cluster = self.cluster_create(old_pf['id'], old_name, 1)
        self.addCleanup(self.cluster_delete, cluster['id'])
        self.assertEqual(cluster['name'], old_name)

        # cluster update
        cmd = ('cluster update --name %s --profile %s --timeout 300 %s'
               % (old_name, new_pf['id'], cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)

        cluster_raw = self.openstack('cluster show %s' % cluster['id'])
        cluster_data = self.show_to_dict(cluster_raw)
        node_raw = self.openstack('cluster node show %s' %
                                  cluster_data['node_ids'])
        node_data = self.show_to_dict(node_raw)

        # if not profile-only, change all profile
        self.assertEqual(cluster['name'], cluster_data['name'])
        self.assertEqual(cluster_data['profile_id'], new_pf['id'])
        self.assertEqual(cluster_data['timeout'], '300')
        self.assertEqual(new_pf['name'], node_data['profile_name'])

    def test_cluster_update_profile_only(self):
        old_name = self.name_generate()
        old_pf = self.profile_create(old_name)
        self.addCleanup(self.profile_delete, old_pf['id'])
        new_name = self.name_generate()
        new_pf = self.profile_create(new_name)
        self.addCleanup(self.profile_delete, new_pf['id'])
        cluster = self.cluster_create(old_pf['id'], old_name, 1)
        self.addCleanup(self.cluster_delete, cluster['id'])
        self.assertEqual(cluster['name'], old_name)

        cmd = ('cluster update --name %s --profile %s --profile-only true'
               ' --timeout 300 %s' % (new_name, new_pf['id'], cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)

        cluster_raw = self.openstack('cluster show %s' % cluster['id'])
        cluster_data = self.show_to_dict(cluster_raw)
        node_raw = self.openstack('cluster node show %s' %
                                  cluster_data['node_ids'])
        node_data = self.show_to_dict(node_raw)

        # if profile-only true, not change exist node profile
        self.assertNotEqual(cluster['name'], cluster_data['name'])
        self.assertNotEqual(cluster_data['profile_id'], cluster['profile_id'])
        self.assertEqual(cluster_data['profile_id'], new_pf['id'])
        self.assertEqual(cluster_data['timeout'], '300')
        self.assertNotEqual(new_name, node_data['profile_name'])

    def test_cluster_show(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name)
        self.addCleanup(self.cluster_delete, cluster['id'])
        cluster_raw = self.openstack('cluster show %s' % name)
        cluster_data = self.show_to_dict(cluster_raw)
        self.assertIn('node_ids', cluster_data)
        self.assertIn('timeout', cluster_data)

    def test_cluster_expand_and_shrink(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name)
        self.addCleanup(self.cluster_delete, cluster['id'])
        cluster_raw = self.openstack('cluster show %s' % name)
        cluster_data = self.show_to_dict(cluster_raw)

        # cluster expand
        self.openstack('cluster expand --count 1 %s' % name)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)
        expand_raw = self.openstack('cluster show %s' % name)
        expand_data = self.show_to_dict(expand_raw)
        self.assertNotEqual(cluster_data['desired_capacity'],
                            expand_data['desired_capacity'])
        self.assertEqual(expand_data['desired_capacity'], '1')

        # cluster shrink
        self.openstack('cluster shrink --count 1 %s' % name)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)
        shrink_raw = self.openstack('cluster show %s' % name)
        shrink_data = self.show_to_dict(shrink_raw)
        self.assertNotEqual(shrink_data['desired_capacity'],
                            expand_data['desired_capacity'])
        self.assertEqual(cluster_data['desired_capacity'],
                         shrink_data['desired_capacity'])

    # NOTE(chenyb4): Since functional tests only focus on the client/server
    # interaction without invovling other OpenStack services, it is not
    # possible to mock a cluster failure and then test if the check logic
    # works. Such tests would be left to integration tests instead.
    def test_cluster_check(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name, 1)
        self.addCleanup(self.cluster_delete, cluster['id'])
        self.openstack('cluster check %s' % cluster['id'])
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)
        check_raw = self.openstack('cluster show %s' % name)
        check_data = self.show_to_dict(check_raw)
        self.assertIn('CLUSTER_CHECK', check_data['status_reason'])
        cluster_status = ['ACTIVE', 'WARNING']
        self.assertIn(check_data['status'], cluster_status)

    # NOTE(chenyb4): A end-to-end test of the cluster recover operation needs
    # to be done with other OpenStack services involved, thus out of scope
    # for functional tests. Such tests would be left to integration tests
    # instead.
    def test_cluster_recover(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name, 1)
        self.addCleanup(self.cluster_delete, cluster['id'])
        cmd = ('cluster recover --check true %s' % cluster['id'])
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)
        recover_raw = self.openstack('cluster show %s' % name)
        recover_data = self.show_to_dict(recover_raw)
        self.assertIn('CLUSTER_RECOVER', recover_data['status_reason'])
        self.assertEqual('ACTIVE', recover_data['status'])

    def test_cluster_resize(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name)
        self.addCleanup(self.cluster_delete, cluster['id'])
        cluster_raw = self.openstack('cluster show %s' % name)
        cluster_data = self.show_to_dict(cluster_raw)
        self.assertEqual(cluster_data['desired_capacity'], '0')
        self.assertEqual(cluster_data['max_size'], '-1')
        self.assertEqual(cluster_data['min_size'], '0')
        cmd = ('cluster resize --max-size 5 --min-size 1 --adjustment 2 %s'
               % cluster['id'])
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)
        resize_raw = self.openstack('cluster show %s' % name)
        resize_data = self.show_to_dict(resize_raw)
        self.assertEqual(resize_data['desired_capacity'], '2')
        self.assertEqual(resize_data['max_size'], '5')
        self.assertEqual(resize_data['min_size'], '1')

    def test_cluster_members_list(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name)
        self.addCleanup(self.cluster_delete, cluster['id'])
        result = self.openstack('cluster members list --full-id %s'
                                % cluster['id'])
        members_list = self.parser.listing(result)
        self.assertTableStruct(members_list, ['id', 'name', 'index',
                                              'status', 'physical_id',
                                              'created_at'])

    def test_cluster_members_add_and_del(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name)
        self.addCleanup(self.cluster_delete, cluster['name'])
        node = self.node_create(pf['id'], name)
        self.addCleanup(self.node_delete, node['id'])
        cluster_raw = self.openstack('cluster show %s' % name)
        cluster_data = self.show_to_dict(cluster_raw)
        self.assertEqual('', cluster_data['node_ids'])

        # Add exist node to cluster
        cmd = ('cluster members add --nodes %s %s' % (node['name'],
                                                      cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)

        mem_ad_raw = self.openstack('cluster show %s' % name)
        mem_ad_data = self.show_to_dict(mem_ad_raw)
        self.assertNotEqual('', mem_ad_data['node_ids'])
        self.assertIn(node['id'], mem_ad_data['node_ids'])

        # Delete node from cluster
        cmd = ('cluster members del --nodes %s %s' % (node['name'],
                                                      cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)
        mem_del_raw = self.openstack('cluster show %s' % name)
        mem_del_data = self.show_to_dict(mem_del_raw)
        self.assertEqual('', mem_del_data['node_ids'])
        self.assertNotIn(node['id'], mem_del_data['node_ids'])

    def test_cluster_members_replace(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name, 1)
        self.addCleanup(self.cluster_delete, cluster['id'])
        cluster_raw = self.openstack('cluster show %s' % name)
        cluster_data = self.show_to_dict(cluster_raw)

        # Create replace node
        new_node = self.node_create(pf['id'], name)
        self.addCleanup(self.node_delete, new_node['id'])
        self.assertNotIn(new_node['id'], cluster_data['node_ids'])

        # Cluster node replace
        old_node = cluster_data['node_ids']
        self.addCleanup(self.node_delete, old_node)
        cmd = ('cluster members replace --nodes %s=%s %s'
               % (old_node, new_node['id'], cluster['id']))
        self.openstack(cmd, flags='--debug')
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)
        replace_raw = self.openstack('cluster show %s' % name)
        replace_data = self.show_to_dict(replace_raw)
        self.assertIn(new_node['id'], replace_data['node_ids'])
        self.assertNotIn(old_node, replace_data['node_ids'])
