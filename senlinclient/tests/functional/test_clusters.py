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
