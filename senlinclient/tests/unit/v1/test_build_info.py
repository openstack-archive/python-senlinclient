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

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import build_info as osc_build_info


class TestBuildInfo(fakes.TestClusteringv1):

    def setUp(self):
        super(TestBuildInfo, self).setUp()
        self.cmd = osc_build_info.BuildInfo(self.app, None)
        self.mock_client = self.app.client_manager.clustering
        fake_bi = mock.Mock(
            api={"revision": "1.0"},
            engine={"revision": "1.0"}
        )
        self.mock_client.get_build_info = mock.Mock(return_value=fake_bi)

    def test_build_info(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_build_info.assert_called_with()
