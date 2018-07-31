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


class ReceiverTest(base.OpenStackClientTestBase):
    """Test for receivers"""

    def test_receiver_list(self):
        result = self.openstack('cluster receiver list')
        receiver_list = self.parser.listing(result)
        self.assertTableStruct(receiver_list, ['id', 'name', 'type',
                                               'cluster_id', 'action',
                                               'created_at'])

    def test_receiver_create(self):
        name = self.name_generate()
        pf = self.profile_create(name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], name)
        self.addCleanup(self.cluster_delete, cluster['id'])
        receiver = self.receiver_create(name, cluster['id'])
        self.addCleanup(self.receiver_delete, receiver['id'])
        self.assertEqual(receiver['name'], name)
        self.assertEqual(receiver['type'], 'webhook')
        self.assertEqual(receiver['action'], 'CLUSTER_SCALE_OUT')

    def test_receiver_update(self):
        old_name = self.name_generate()
        pf = self.profile_create(old_name)
        self.addCleanup(self.profile_delete, pf['id'])
        cluster = self.cluster_create(pf['id'], old_name)
        self.addCleanup(self.cluster_delete, cluster['id'])
        receiver = self.receiver_create(old_name, cluster['id'])
        self.addCleanup(self.receiver_delete, receiver['id'])
        new_name = self.name_generate()

        cmd = ('cluster receiver update --name %s --params count=2 '
               '--action CLUSTER_SCALE_IN %s' % (new_name, receiver['id']))
        self.openstack(cmd)
        receiver_raw = self.openstack('cluster receiver show %s'
                                      % receiver['id'])
        receiver_data = self.show_to_dict(receiver_raw)
        self.assertNotEqual(receiver['name'], receiver_data['name'])
        self.assertEqual(receiver_data['name'], new_name)
        self.assertNotEqual(receiver['action'], receiver_data['action'])
        self.assertEqual(receiver_data['action'], 'CLUSTER_SCALE_IN')
