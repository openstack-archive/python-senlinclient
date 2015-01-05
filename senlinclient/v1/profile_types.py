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


class ProfileType(base.Resource):
    def __repr__(self):
        return "<ProfileType %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)

    def _add_details(self, info):
        self.profile_type = info


class ProfileTypeManager(base.BaseManager):
    resource_class = ProfileType

    def list(self):
        """Get a list of profile types.
        :rtype: list of :class:`ProfileType`
        """
        return self._list('/profile_types', 'profile_types')

    def get(self, profile_type):
        '''Get the details for a specific profile_type.'''
        url_str = parse.quote(encodeutils.safe_encode(profile_type), '')
        resp, body = self.client.json_request(
            'GET',
            '/profile_types/%s' % url_str)
        return body

    def generate_template(self, profile_type):
        url_str = parse.quote(encodeutils.safe_encode(profile_type), '')
        resp, body = self.client.json_request(
            'GET',
            '/profile_types/%s/template' % url_str)
        return body
