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


class NodeTest(base.OpenStackClientTestBase):
    """Test for nodes"""

    def test_node_list(self):
        result = self.openstack('cluster node list')
        node_list = self.parser.listing(result)
        self.assertTableStruct(node_list, ['id', 'name', 'index', 'status',
                                           'cluster_id', 'physical_id',
                                           'profile_name', 'created_at',
                                           'updated_at'])

    def test_node_create(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        node = self.node_create(pf['id'], name)
        self.assertEqual(node['name'], name)
        self.node_delete(node['id'])
        self.addCleanup(self.profile_delete, pf['id'])

    def test_node_update(self):
        old_name = self.name_generate()
        pf = self.profile_create(old_name)
        n1 = self.node_create(pf['id'], old_name)
        new_name = self.name_generate()
        pf_new = self.profile_create(new_name)
        role = 'master'
        cmd = ('cluster node update --name %s --role %s --profile %s %s'
               % (new_name, role, pf_new['id'], n1['id']))
        self.openstack(cmd)
        self.wait_for_status(n1['id'], 'ACTIVE', 'node', 120)
        raw_node = self.openstack('cluster node show %s' % n1['id'])
        node_data = self.show_to_dict(raw_node)
        self.assertEqual(node_data['name'], new_name)
        self.assertNotEqual(node_data['name'], old_name)
        self.assertEqual(node_data['role'], role)
        self.assertEqual(node_data['profile_id'], pf_new['id'])
        self.node_delete(new_name)
        self.addCleanup(self.profile_delete, pf['id'])
        self.addCleanup(self.profile_delete, pf_new['id'])

    def test_node_detail(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        node = self.node_create(pf['id'], name)
        cmd = ('cluster node show --details %s' % name)
        raw_node = self.openstack(cmd)
        node_data = self.show_to_dict(raw_node)
        self.assertIn('details', node_data)
        self.assertIsNotNone(node_data['details'])
        self.node_delete(node['id'])
        self.addCleanup(self.profile_delete, pf['id'])

    # NOTE(Qiming): Since functional tests only focus on the client/server
    # interaction without invovling other OpenStack services, it is not
    # possible to mock a node failure and then test if the check logic works.
    # Such tests would be left to integration tests instead.
    def test_node_check(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        node = self.node_create(pf['id'], name)
        cmd = ('cluster node check %s' % node['id'])
        self.openstack(cmd)
        check_raw = self.openstack('cluster node show %s' % name)
        check_data = self.show_to_dict(check_raw)
        self.assertIn('Check', check_data['status_reason'])
        node_status = ['ACTIVE', 'ERROR']
        self.assertIn(check_data['status'], node_status)
        self.node_delete(node['id'])
        self.addCleanup(self.profile_delete, pf['id'])

    # NOTE(Qiming): A end-to-end test of the node recover operation needs to
    # be done with other OpenStack services involved, thus out of scope for
    # functional tests. Such tests would be left to integration tests instead.
    def test_node_recover(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        node = self.node_create(pf['id'], name)
        cmd = ('cluster node recover --check true %s' % node['id'])
        self.openstack(cmd)
        self.wait_for_status(name, 'ACTIVE', 'node', 120)
        recover_raw = self.openstack('cluster node show %s' % name)
        recover_data = self.show_to_dict(recover_raw)
        self.assertIn('Recover', recover_data['status_reason'])
        self.assertEqual('ACTIVE', recover_data['status'])
        self.node_delete(node['id'])
        self.addCleanup(self.profile_delete, pf['id'])
