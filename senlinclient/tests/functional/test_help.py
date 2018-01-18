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


class HelpTest(base.OpenStackClientTestBase):
    """Test for help commands"""

    def test_help_cmd(self):
        help_text = self.openstack('help cluster list')
        lines = help_text.split('\n')
        self.assertFirstLineStartsWith(lines, 'usage: openstack cluster list')
