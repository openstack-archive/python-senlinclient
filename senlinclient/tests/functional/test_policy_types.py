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


class PolicyTypeTest(base.OpenStackClientTestBase):
    """Test for policy types"""

    def test_policy_type_list(self):
        result = self.openstack('cluster policy type list')
        policy_type = self.parser.listing(result)
        columns = ['name', 'version']
        if any('support_status' in i for i in policy_type):
            columns.append('support_status')
        self.assertTableStruct(policy_type, columns)

    def test_policy_type_show(self):
        params = ['senlin.policy.affinity-1.0',
                  'senlin.policy.batch-1.0',
                  'senlin.policy.deletion-1.0',
                  'senlin.policy.health-1.0',
                  'senlin.policy.loadbalance-1.1',
                  'senlin.policy.region_placement-1.0',
                  'senlin.policy.zone_placement-1.0']
        for param in params:
            cmd = 'cluster policy type show %s' % param
            self.openstack(cmd)
