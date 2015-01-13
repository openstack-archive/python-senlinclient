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

from senlinclient.common import http
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


class BuildInfo(base.Resource):
    def __repr__(self):
        return "<BuildInfo %s>" % self._info

    def build_info(self):
        return self.manager.build_info()


class BuildInfoManager(base.BaseManager):
    resource_class = BuildInfo

    def build_info(self):
        resp, body = self.client.json_request('GET', '/build_info')
        return body


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

    def add_node(self, cluster_id, node_id):
        headers = self.client.credentials_headers()
        cluster = self.get(cluster_id)
        data = {'node_id': node_id}
        resp, body = self.client.json_request(
            'POST',
            '/clusters/%s/nodes' % cluster.identifier,
            data=data, headers=headers)

    def del_node(self, cluster_id, node_id):
        cluster = self.get(cluster_id)
        resp, body = self.client.json_request(
            'DELETE',
            '/clusters/%s/nodes/%s' % (cluster.identifier, node_id))

    def list_policy(self, cluster_id):
        cluster = self.get(cluster_id)
        resp, body = self.client.json_request(
            'GET',
            '/clusters/%s/policies' % cluster.identifier)
        return body

    def attach_policy(self, cluster_id, policy_id):
        """Attach a policy to a cluster."""
        cluster = self.get(cluster_id)
        data = {'policy_id': policy_id}
        resp, body = self.client.json_request(
            'POST',
            '/clusters/%s/policies' % cluster.identifier,
            data=data)

    def detach_policy(self, cluster_id, policy_id):
        cluster = self.get(cluster_id)
        resp, body = self.client.json_request(
            'DELETE',
            '/clusters/%s/policies/%s' % (cluster.identifier, policy_id))

    def update_policy(self, cluster_id, **kwargs):
        cluster = self.get(cluster_id)
        policy_id = kwargs.pop('policy_id')
        resp, body = self.client.json_request(
            'POST',
            '/clusters/%s/policies/%s' % (cluster.identifier, policy_id),
            data=kwargs)

    def show_policy(self, cluster_id, policy_id):
        cluster = self.get(cluster_id)
        resp, body = self.client.json_request(
            'GET',
            '/clusters/%s/policies/%s' % (cluster.identifier, policy_id))
        return body

    def get(self, cluster_id):
        resp, body = self.client.json_request(
            'GET',
            '/clusters/%s' % cluster_id)
        return Cluster(self, body['cluster'])


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

    def profile(self, node_id):
        '''Get the profile spec for a specific node as a parsed JSON.'''
        resp, body = self.client.json_request(
            'GET',
            '/nodes/%s/profile' % node_id)
        return body


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


class Client(object):
    '''Client for the Senlin v1 API.

    :param endpoint: A user-supplied endpoint URL for the Senlin service.
    :param token: Token for authentication.
    :param timeout: Allows customization of the timeout for client
                    HTTP requests. (optional)
    '''

    def __init__(self, endpoint, **kwargs):
        """Initialize a new client for the Senlin v1 API."""
        self.hc = http.create_http_client(endpoint, **kwargs)

        self.actions = ActionManager(self.hc)
        self.build_info = BuildInfoManager(self.hc)
        self.clusters = ClusterManager(self.hc)
        self.events = EventManager(self.hc)
        self.nodes = NodeManager(self.hc)
        self.profile_types = ProfileTypeManager(self.hc)
        self.profiles = ProfileManager(self.hc)
        self.policy_types = PolicyTypeManager(self.hc)
        self.policies = PolicyManager(self.hc)
