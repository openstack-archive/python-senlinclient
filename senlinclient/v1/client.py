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

from senlinclient.common import http
from senlinclient.v1 import actions
from senlinclient.v1 import build_info
from senlinclient.v1 import clusters
from senlinclient.v1 import events
from senlinclient.v1 import nodes
from senlinclient.v1 import policies
from senlinclient.v1 import policy_types
from senlinclient.v1 import profile_types
from senlinclient.v1 import profiles


class Client(object):
    """Client for the Senlin v1 API.

    :param string endpoint: A user-supplied endpoint URL for the Senlin
                            service.
    :param string token: Token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Senlin v1 API."""
        self.http_client = http._construct_http_client(*args, **kwargs)

        self.clusters = clusters.ClusterManager(self.http_client)
        self.nodes = nodes.NodeManager(self.http_client)
        self.profiles = profiles.ProfileManager(self.http_client)
        self.policies = policies.PolicyManager(self.http_client)
        self.policy_types = policy_types.PolicyTypeManager(self.http_client)
        self.profile_types = profile_types.ProfileTypeManager(self.http_client)
        self.events = events.EventManager(self.http_client)
        self.actions = actions.ActionManager(self.http_client)

        self.build_info = build_info.BuildInfoManager(self.http_client)
