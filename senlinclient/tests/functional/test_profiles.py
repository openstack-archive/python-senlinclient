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


class ProfileTest(base.OpenStackClientTestBase):
    """Test for profiles"""

    def test_profile_list(self):
        result = self.openstack('cluster profile list')
        profile_list = self.parser.listing(result)
        self.assertTableStruct(profile_list, ['id', 'name', 'type',
                                              'created_at'])

    def test_pofile_create(self):
        name = self.name_generate()
        result = self.profile_create(name, 'cirros_basic.yaml')
        self.assertEqual(result['name'], name)
        self.addCleanup(self.profile_delete, result['id'])

    def test_profile_update(self):
        old_name = self.name_generate()
        pf1 = self.profile_create(old_name, 'cirros_basic.yaml')
        new_name = self.name_generate()
        cmd = ('cluster profile update --name %s %s' % (new_name, pf1['id']))
        result = self.openstack(cmd)
        pf2 = self.show_to_dict(result)
        self.assertEqual(pf2['name'], new_name)
        self.assertNotEqual(pf1['name'], pf2['name'])
        self.addCleanup(self.profile_delete, pf2['id'])
