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


class Event(base.Resource):
    def __repr__(self):
        return "<Event %s>" % self._info

    def update(self, **fields):
        self.manager.update(self, **fields)

    def delete(self):
        return self.manager.delete(self)

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class EventManager(base.BaseManager):
    resource_class = Event

    def list(self, **kwargs):
        """Get a list of events.
        :param limit: maximum number of events to return
        :param marker: begin returning events that appear later in the
                       list than that represented by this event id
        :param filters: dict of direct comparison filters that mimics the
                        structure of a event object
        :rtype: list of :class:`Event`
        """
        def paginate(params):
            '''Paginate events, even if more than API limit.'''
            current_limit = int(params.get('limit') or 0)
            url = '/events?%s' % parse.urlencode(params, True)
            events = self._list(url, 'events')
            for event in events:
                yield event

            count = len(events)
            remaining = current_limit - count
            if remaining > 0 and count > 0:
                params['limit'] = remaining
                params['marker'] = event.id
                for event in paginate(params):
                    yield event

        params = {}
        if 'filters' in kwargs:
            filters = kwargs.pop('filters')
            params.update(filters)

        for key, value in six.iteritems(kwargs):
            if value:
                params[key] = value

        return paginate(params)

    def delete(self, event_id):
        self._delete("/events/%s" % event_id)

    def get(self, event_id):
        '''Get the details for a specific event.'''
        resp, body = self.client.json_request(
            'GET',
            '/events/%s' % event_id)
        return Event(self, body['event'])
