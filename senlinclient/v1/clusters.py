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


class Cluster(base.Resource):
    def __repr__(self):
        return "<Cluster %s>" % self._info

    def create(self, **fields):
        return self.manager.create(self.identifier, **fields)

    def update(self, **fields):
        self.manager.update(self.identifier, **fields)

    def delete(self):
        return self.manager.delete(self.identifier)

    def get(self):
        # set_loaded() first ... so if we have to bail, we know we tried.
        self._loaded = True
        if not hasattr(self.manager, 'get'):
            return

        new = self.manager.get(self.identifier)
        if new:
            self._add_details(new._info)

    @property
    def identifier(self):
        return '%s/%s' % (self.name, self.id)


class ClusterManager(base.BaseManager):
    resource_class = Cluster

    def list(self, **kwargs):
        """Get a list of clusters.
        :param limit: maximum number of clusters to return
        :param marker: begin returning clusters that appear later in the
                       cluster list than that represented by this cluster id
        :param filters: dict of direct comparison filters that mimics the
                        structure of a cluster object
        :rtype: list of :class:`Cluster`
        """
        def paginate(params):
            '''Paginate clusters, even if more than API limit.'''
            current_limit = int(params.get('limit') or 0)
            url = '/clusters?%s' % parse.urlencode(params, True)
            clusters = self._list(url, 'clusters')
            for cluster in clusters:
                yield cluster

            count = len(clusters)
            remaining = current_limit - count
            if remaining > 0 and count > 0:
                params['limit'] = remaining
                params['marker'] = cluster.id
                for cluster in paginate(params):
                    yield cluster

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
            '/clusters',
            data=kwargs, headers=headers)
        return body

    def update(self, cluster_id, **kwargs):
        headers = self.client.credentials_headers()
        resp, body = self.client.json_request(
            'PUT',
            '/clusters/%s' % cluster_id,
            data=kwargs, headers=headers)

    def delete(self, cluster_id):
        """Delete a cluster."""
        self._delete("/clusters/%s" % cluster_id)

    def attach_policy(self, cluster_id, policy_id):
        """Attach a policy to a cluster."""
        cluster = self.get(cluster_id)
        data = {'policy_id': policy_id}
        resp, body = self.client.json_request(
            'POST',
            '/clusters/%s/policies' % cluster.identifier,
            data=data)
        return body

    def show_policy(self, cluster_id, policy_id):
        cluster = self.get(cluster_id)
        resp, body = self.client.json_request(
            'GET',
            '/clusters/%s/policies/%s' % (cluster.identifier, policy_id))
        return body

    def detach_policy(self, cluster_id, policy_id):
        cluster = self.get(cluster_id)
        resp, body = self.client.json_request(
            'DELETE',
            '/clusters/%s/policies/%s' % (cluster.identifier, policy_id))
        return body

    def policy_list(self, cluster_id):
        cluster = self.get(cluster_id)
        resp, body = self.client.json_request(
            'GET',
            '/clusters/%s/policies' % cluster.identifier)
        return body

    def get(self, cluster_id):
        resp, body = self.client.json_request(
            'GET',
            '/clusters/%s' % cluster_id)
        return Cluster(self, body['cluster'])

    def profile(self, cluster_id):
        '''Get the profile spec for a specific cluster as a parsed Json.'''
        resp, body = self.client.json_request(
            'GET',
            '/clusters/%s/profile' % cluster_id)
        return body
