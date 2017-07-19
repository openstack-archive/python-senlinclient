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
from senlinclient.v1 import service as osc_service


class TestServiceList(fakes.TestClusteringv1):
    columns = ['binary', 'host', 'status', 'state', 'updated_at',
               'disabled_reason']

    def setUp(self):
        super(TestServiceList, self).setUp()
        self.mock_client = self.app.client_manager.clustering
        self.cmd = osc_service.ListService(self.app, None)
        fake_service = mock.Mock(
            Binary='senlin-engine',
            Host='Host1',
            Status='enabled',
            State='up',
            Updated_at=None,
            Disabled_Reason=None,
        )
        fake_service.name = 'test_service'
        fake_service.to_dict = mock.Mock(return_value={})
        self.mock_client.services = mock.Mock(return_value=[fake_service])

    def test_service(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.services.assert_called_with()
        self.assertEqual(self.columns, columns)
