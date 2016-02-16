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

from openstackclient.tests import utils
from senlinclient.tests.unit.osc import fakes


class FakeClusteringv1Client(object):
    def __init__(self, **kwargs):
        self.http_client = mock.Mock()
        self.http_client.auth_token = kwargs['token']
        self.profiles = fakes.FakeResource(None, {})


class TestClusteringv1(utils.TestCommand):
    def setUp(self):
        super(TestClusteringv1, self).setUp()

        self.app.client_manager.clustering = FakeClusteringv1Client(
            token=fakes.AUTH_TOKEN,
            auth_url=fakes.AUTH_URL
        )
