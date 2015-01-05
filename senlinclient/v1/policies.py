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


class Policy(base.Resource):
    def __repr__(self):
        return "<Policy %s>" % self._info

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


class PolicyManager(base.BaseManager):
    resource_class = Policy

    def list(self, **kwargs):
        """Get a list of policies.
        :param limit: maximum number of policies to return
        :param marker: begin returning policies that appear later in the
                       list than that represented by this policy id
        :param filters: dict of direct comparison filters that mimics the
                        structure of a policy object
        :rtype: list of :class:`Policy`
        """
        def paginate(params):
            '''Paginate policies, even if more than API limit.'''
            current_limit = int(params.get('limit') or 0)
            url = '/policies?%s' % parse.urlencode(params, True)
            policies = self._list(url, 'policies')
            for policy in policies:
                yield policy

            count = len(policies)
            remaining = current_limit - count
            if remaining > 0 and count > 0:
                params['limit'] = remaining
                params['marker'] = policy.id
                for policy in paginate(params):
                    yield policy

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
            '/policies',
            data=kwargs, headers=headers)
        return body

    def update(self, policy_id, **kwargs):
        '''We don't allow update to a policy.'''
        return None

    def delete(self, policy_id):
        """Delete a policy."""
        self._delete("/policies/%s" % policy_id)

    def get(self, policy_id):
        resp, body = self.client.json_request(
            'GET',
            '/policies/%s' % policy_id)
        return Policy(self, body['policy'])
