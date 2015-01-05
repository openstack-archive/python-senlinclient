#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import six
from six.moves.urllib import parse

from senlinclient.openstack.common.apiclient import base


class Action(base.Resource):
    def __repr__(self):
        return "<Action %s>" % self._info

    def update(self, **fields):
        self.manager.update(self, **fields)

    def delete(self):
        return self.manager.delete(self)

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class ActionManager(base.BaseManager):
    resource_class = Action

    def list(self, **kwargs):
        """Get a list of actions.
        :param limit: maximum number of actions to return
        :param marker: begin returning actions that appear later in the
                       list than that represented by this action id
        :param filters: dict of direct comparison filters that mimics the
                        structure of a action object
        :rtype: list of :class:`Action`
        """
        def paginate(params):
            '''Paginate actions, even if more than API limit.'''
            current_limit = int(params.get('limit') or 0)
            url = '/actions?%s' % parse.urlencode(params, True)
            actions = self._list(url, 'actions')
            for action in actions:
                yield action

            count = len(actions)
            remaining = current_limit - count
            if remaining > 0 and count > 0:
                params['limit'] = remaining
                params['marker'] = action.id
                for action in paginate(params):
                    yield action

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
            '/actions',
            data=kwargs, headers=headers)
        return body

    def cancel(self, action_id):
        headers = self.client.credentials_headers()
        resp, body = self.client.json_request(
            'POST',
            '/actions/%s/cancel' % action_id,
            headers=headers)
        return body

    def delete(self, action_id):
        self._delete('/actions/%s' % action_id)
