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


class PolicyTest(base.OpenStackClientTestBase):
    """Test for policies"""

    def test_policy_list(self):
        result = self.openstack('cluster policy list')
        policy_list = self.parser.listing(result)
        self.assertTableStruct(policy_list, ['id', 'name', 'type',
                                             'created_at'])

    def test_policy_create(self):
        name = self.name_generate()
        result = self.policy_create(name, 'deletion_policy.yaml')
        self.assertEqual(result['name'], name)
        self.addCleanup(self.policy_delete, result['id'])

    def test_policy_update(self):
        old_name = self.name_generate()
        pc1 = self.policy_create(old_name, 'deletion_policy.yaml')
        new_name = self.name_generate()
        cmd = ('cluster policy update --name %s %s' % (new_name, pc1['id']))
        result = self.openstack(cmd)
        pc2 = self.show_to_dict(result)
        self.assertEqual(pc2['name'], new_name)
        self.assertNotEqual(pc1['name'], pc2['name'])
        self.addCleanup(self.policy_delete, pc2['id'])
