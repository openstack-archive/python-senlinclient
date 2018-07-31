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


class ClusterPolicyTest(base.OpenStackClientTestBase):
    """Test cluster for policy"""

    def test_cluster_policy_attach_and_detach(self):
        name = self.name_generate()
        po = self.policy_create(name)
        self.addCleanup(self.policy_delete, po['id'])
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name)
        self.addCleanup(self.cluster_delete, cluster['id'])

        cp_raw = self.openstack('cluster policy binding list %s'
                                % cluster['id'])
        cp_data = self.show_to_dict(cp_raw)
        self.assertEqual({}, cp_data)

        # Attach policy to cluster
        cmd = ('cluster policy attach --policy %s %s' % (po['id'],
                                                         cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)
        cmd = ('cluster policy binding show --policy %s %s' %
               (po['id'], cluster['id']))
        policy_raw = self.openstack(cmd)
        policy_data = self.show_to_dict(policy_raw)
        self.assertEqual(po['name'], policy_data['policy_name'])
        self.assertEqual(cluster['name'], policy_data['cluster_name'])
        self.assertTrue(policy_data['is_enabled'])

        # Detach policy from cluster
        cmd = ('cluster policy detach --policy %s %s' % (po['id'],
                                                         cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)
        cp_raw = self.openstack('cluster policy binding list %s'
                                % cluster['id'])
        cp_data = self.show_to_dict(cp_raw)
        self.assertEqual({}, cp_data)

    def test_cluster_policy_list(self):
        name = self.name_generate()
        po = self.policy_create(name)
        self.addCleanup(self.policy_delete, po['id'])
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name)
        self.addCleanup(self.cluster_delete, cluster['id'])

        cmd = ('cluster policy attach --policy %s %s' % (po['id'],
                                                         cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)

        # List cluster policy binding
        cmd = ('cluster policy binding list --filters policy_name=%s %s'
               % (po['name'], cluster['id']))
        result = self.openstack(cmd)
        binding_list = self.parser.listing(result)
        self.assertTableStruct(binding_list, ['policy_id', 'policy_name',
                                              'policy_type', 'is_enabled'])
        cmd = ('cluster policy detach --policy %s %s' % (po['id'],
                                                         cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)

    def test_cluster_policy_update(self):
        name = self.name_generate()
        po = self.policy_create(name)
        self.addCleanup(self.policy_delete, po['id'])
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name)
        self.addCleanup(self.cluster_delete, cluster['id'])

        cmd = ('cluster policy attach --policy %s %s' % (po['id'],
                                                         cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)

        # Update cluster policy binding
        cmd = ('cluster policy binding update --policy %s --enabled false %s'
               % (po['id'], cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)

        cp_update = self.openstack('cluster policy binding show --policy %s %s'
                                   % (po['id'], cluster['id']))
        cp_update_data = self.show_to_dict(cp_update)
        self.assertFalse(cp_update_data['is_enabled'].isupper())
        cmd = ('cluster policy detach --policy %s %s' % (po['id'],
                                                         cluster['id']))
        self.openstack(cmd)
        self.wait_for_status(cluster['id'], 'ACTIVE', 'cluster', 120)
