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


class Node(base.Resource):
    def __repr__(self):
        return "<Node %s>" % self._info

    def update(self, **fields):
        self.manager.update(self, **fields)

    def delete(self):
        return self.manager.delete(self)

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class NodeManager(base.BaseManager):
    resource_class = Node

    def list(self, **kwargs):
        """Get a list of nodes.
        :param limit: maximum number of nodes to return
        :param marker: begin returning nodes that appear later in the
                       list than that represented by this node id
        :param filters: dict of direct comparison filters that mimics the
                        structure of a node object
        :rtype: list of :class:`Node`
        """
        def paginate(params):
            '''Paginate nodes, even if more than API limit.'''
            current_limit = int(params.get('limit') or 0)
            url = '/nodes?%s' % parse.urlencode(params, True)
            nodes = self._list(url, 'nodes')
            for node in nodes:
                yield node

            count = len(nodes)
            remaining = current_limit - count
            if remaining > 0 and count > 0:
                params['limit'] = remaining
                params['marker'] = node.id
                for node in paginate(params):
                    yield node

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
            '/nodes', data=kwargs, headers=headers)
        return body

    def delete(self, node_id):
        self._delete('/nodes/%s' % node_id)

    def update(self, node_id, kwargs):
        headers = self.client.credentials_headers()
        resp, body = self.client.json_request(
            'PATCH',
            '/nodes/%s' % node_id,
            data=kwargs, headers=headers)

    def get(self, node_id):
        '''Get the details for a specific node.'''
        resp, body = self.client.json_request(
            'GET',
            '/nodes/%s' % node_id)
        return Node(self, body['node'])

    def join(self, node_id, cluster_id):
        '''Make node join the specified cluster.'''
        headers = self.client.credentials_headers()
        data = {'cluster_id': cluster_id}
        resp, body = self.client.json_request(
            'POST',
            '/nodes/%s/cluster' % node_id,
            data=data, headers=headers)
        return body

    def leave(self, node_id):
        '''Make node leave its current cluster.'''
        resp, body = self.client.json_request(
            'POST',
            '/nodes/%s/cluster' % node_id)
        return body

    def profile(self, node_id):
        '''Get the profile spec for a specific node as a parsed JSON.'''
        resp, body = self.client.json_request(
            'GET',
            '/nodes/%s/profile' % node_id)
        return body
