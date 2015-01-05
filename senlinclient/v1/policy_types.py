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

from six.moves.urllib import parse

from oslo.utils import encodeutils

from senlinclient.openstack.common.apiclient import base


class PolicyType(base.Resource):
    def __repr__(self):
        return "<PolicyType %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)

    def _add_details(self, info):
        self.policy_type = info


class PolicyTypeManager(base.BaseManager):
    resource_class = PolicyType

    def list(self):
        """Get a list of policy types.
        :rtype: list of :class:`PolicyType`
        """
        return self._list('/policy_types', 'policy_types')

    def get(self, policy_type):
        '''Get the details for a specific policy_type.'''
        url_str = parse.quote(encodeutils.safe_encode(policy_type), '')
        resp, body = self.client.json_request(
            'GET',
            '/policy_types/%s' % url_str)
        return body

    def generate_template(self, policy_type):
        url_str = parse.quote(encodeutils.safe_encode(policy_type), '')
        resp, body = self.client.json_request(
            'GET',
            '/policy_types/%s/template' % url_str)
        return body
