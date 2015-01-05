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

import six
from six.moves.urllib import parse

from senlinclient.openstack.common.apiclient import base


class Profile(base.Resource):
    def __repr__(self):
        return "<Profile %s>" % self._info

    def create(self, **fields):
        return self.manager.create(self.identifier, **fields)

    def update(self, **fields):
        self.manager.update(self.identifier, **fields)

    def delete(self):
        return self.manager.delete(self.identifier)

    def get(self):
        # set _loaded() first ... so if we have to bail, we know we tried.
        self._loaded = True
        if not hasattr(self.manager, 'get'):
            return

        new = self.manager.get(self.identifier)
        if new:
            self._add_details(new._info)

    @property
    def identifier(self):
        return '%s/%s' % (self.name, self.id)


class ProfileManager(base.BaseManager):
    resource_class = Profile

    def list(self, **kwargs):
        """Get a list of profiles.
        :param limit: maximum number of profiles to return
        :param marker: begin returning profiles that appear later in the
                       list than that represented by this profile id
        :param filters: dict of direct comparison filters that mimics the
                        structure of a profile object
        :rtype: list of :class:`Profile`
        """
        def paginate(params):
            '''Paginate profiles, even if more than API limit.'''
            current_limit = int(params.get('limit') or 0)
            url = '/profiles?%s' % parse.urlencode(params, True)
            profiles = self._list(url, 'profiles')
            for profile in profiles:
                yield profile

            count = len(profiles)
            remaining = current_limit - count
            if remaining > 0 and count > 0:
                params['limit'] = remaining
                params['marker'] = profile.id
                for profile in paginate(params):
                    yield profile

        params = {}
        if 'filters' in kwargs:
            filters = kwargs.pop('filters')
            params.update(filters)

        for key, value in six.iteritems(kwargs):
            if value:
                params[key] = value

        return paginate(params)

    def create(self, **kwargs):
        headers = self.client.credentials_headers()
        resp, body = self.client.json_request(
            'POST',
            '/profiles',
            data=kwargs, headers=headers)
        return body

    def update(self, profile_id, **kwargs):
        '''We don't allow update to a profile.'''
        return None

    def delete(self, profile_id):
        """Delete a profile."""
        self._delete("/profiles/%s" % profile_id)

    def get(self, profile_id):
        resp, body = self.client.json_request(
            'GET',
            '/profiles/%s' % profile_id)
        return Profile(self, body['profile'])
