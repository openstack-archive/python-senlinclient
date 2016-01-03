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

from openstack.cluster import cluster_service
from openstack import utils
from senlinclient.common import sdk as resource


class Version(resource.Resource):
    resource_key = 'version'
    resources_key = 'versions'
    base_path = '/'
    service = cluster_service.ClusterService(
        version=cluster_service.ClusterService.UNVERSIONED
    )

    # capabilities
    allow_list = True

    # Properties
    links = resource.prop('links')
    status = resource.prop('status')


class Cluster(resource.Resource):
    resource_key = 'cluster'
    resources_key = 'clusters'
    base_path = '/clusters'
    service = cluster_service.ClusterService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    patch_update = True

    # Properties
    id = resource.prop('id')
    name = resource.prop('name')
    profile_id = resource.prop('profile_id')
    user = resource.prop('user')
    project = resource.prop('project')
    domain = resource.prop('domain')
    parent = resource.prop('parent')
    created_time = resource.prop('created_time')
    updated_time = resource.prop('updated_time')
    min_size = resource.prop('min_size', type=int)
    max_size = resource.prop('max_size', type=int)
    desired_capacity = resource.prop('desired_capacity', type=int)
    timeout = resource.prop('timeout')
    status = resource.prop('status')
    status_reason = resource.prop('status_reason')
    metadata = resource.prop('metadata', type=dict)
    data = resource.prop('data', type=dict)

    nodes = resource.prop('nodes')

    profile_name = resource.prop('profile_name')
    # action = resource.prop('action')

    def action(self, session, body):
        url = utils.urljoin(self.base_path, self.id, 'actions')
        resp = session.post(url, endpoint_filter=self.service, json=body)
        return resp.json()

    def add_nodes(self, session, nodes):
        body = {
            'add_nodes': {
                'nodes': nodes,
            }
        }
        return self.action(session, body)

    def del_nodes(self, session, nodes):
        body = {
            'del_nodes': {
                'nodes': nodes,
            }
        }
        return self.action(session, body)

    def resize(self, session, adjustment_type=None, number=None,
               min_size=None, max_size=None, min_step=None, strict=False):
        body = {
            'resize': {
                'adjustment_type': adjustment_type,
                'number': number,
                'min_size': min_size,
                'max_size': max_size,
                'min_step': min_step,
                'strict': strict,
            }
        }
        return self.action(session, body)

    def scale_out(self, session, count=None):
        body = {
            'scale_out': {
                'count': count,
            }
        }
        return self.action(session, body)

    def scale_in(self, session, count=None):
        body = {
            'scale_in': {
                'count': count,
            }
        }
        return self.action(session, body)

    def policy_attach(self, session, policy_id, priority, level, cooldown,
                      enabled):
        body = {
            'policy_attach': {
                'policy_id': policy_id,
                'priority': priority,
                'level': level,
                'cooldown': cooldown,
                'enabled': enabled,
            }
        }
        return self.action(session, body)

    def policy_detach(self, session, policy_id):
        body = {
            'policy_detach': {
                'policy_id': policy_id,
            }
        }
        return self.action(session, body)

    def policy_update(self, session, policy_id, priority, level, cooldown,
                      enabled):

        body = {
            'policy_update': {
                'policy_id': policy_id,
            }
        }
        if priority is not None:
            body['policy_update']['priority'] = priority
        if level is not None:
            body['policy_update']['level'] = level
        if cooldown is not None:
            body['policy_update']['cooldown'] = cooldown
        if enabled is not None:
            body['policy_update']['enabled'] = enabled

        return self.action(session, body)

    def policy_enable(self, session, policy_id):
        body = {
            'policy_update': {
                'policy_id': policy_id,
                'enabled': True,
            }
        }
        return self.action(session, body)

    def policy_disable(self, session, policy_id):
        body = {
            'policy_update': {
                'policy_id': policy_id,
                'enabled': False,
            }
        }
        return self.action(session, body)

    def to_dict(self):
        info = {
            'id': self.id,
            'name': self.name,
            'profile_id': self.profile_id,
            'user': self.user,
            'project': self.project,
            'domain': self.domain,
            'parent': self.parent,
            'created_time': self.created_time,
            'updated_time': self.updated_time,
            'min_size': self.min_size,
            'max_size': self.max_size,
            'desired_capacity': self.desired_capacity,
            'timeout': self.timeout,
            'status': self.status,
            'status_reason': self.status_reason,
            'metadata': self.metadata or {},
            'data': self.data or {},
            'nodes': self.nodes or [],
            'profile_name': self.profile_name,
        }
        return info


class ClusterPolicy(resource.Resource):
    id_attribute = 'policy_id'
    resource_key = 'cluster_policy'
    resources_key = 'cluster_policies'
    base_path = '/clusters/%(cluster_id)s/policies'
    service = cluster_service.ClusterService()

    # Capabilities
    allow_list = True
    allow_retrieve = True

    # Properties
    policy_id = resource.prop('policy_id')
    cluster_id = resource.prop('cluster_id')
    cluster_name = resource.prop('cluster_name')
    policy = resource.prop('policy_name')
    type = resource.prop('policy_type')
    priority = resource.prop('priority')
    level = resource.prop('level', type=int)
    cooldown = resource.prop('cooldown')
    enabled = resource.prop('enabled')

    def to_dict(self):
        info = {
            'cluster_id': self.cluster_id,
            'cluster_name': self.cluster_name,
            'policy_id': self.policy_id,
            'policy': self.policy,
            'type': self.type,
            'priority': self.priority,
            'level': self.level,
            'cooldown': self.cooldown,
            'enabled': self.enabled,
        }
        return info


class Node(resource.Resource):
    resource_key = 'node'
    resources_key = 'nodes'
    base_path = '/nodes'
    service = cluster_service.ClusterService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    patch_update = True

    # Properties
    id = resource.prop('id')
    name = resource.prop('name')
    physical_id = resource.prop('physical_id')
    cluster_id = resource.prop('cluster_id')
    profile_id = resource.prop('profile_id')
    project = resource.prop('project')
    profile_name = resource.prop('profile_name')
    index = resource.prop('index', type=int)
    role = resource.prop('role')
    init_time = resource.prop('init_time')
    created_time = resource.prop('created_time')
    updated_time = resource.prop('updated_time')
    status = resource.prop('status')
    status_reason = resource.prop('status_reason')
    metadata = resource.prop('metadata', type=dict)
    data = resource.prop('data', type=dict)
    details = resource.prop('details', type=dict)

    def action(self, session, body):
        url = utils.urljoin(self.base_path, self.id, 'actions')
        resp = session.post(url, endpoint_filter=self.service, json=body)
        return resp.json()

    def join(self, session, cluster_id):
        body = {
            'join': {
                'cluster_id': cluster_id,
            }
        }
        return self.action(session, body)

    def leave(self, session):
        body = {
            'leave': {}
        }
        return self.action(session, body)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'physical_id': self.physical_id,
            'cluster_id': self.cluster_id,
            'profile_id': self.profile_id,
            'profile_name': self.profile_name,
            'project': self.project,
            'index': self.index,
            'role': self.role,
            'init_time': self.init_time,
            'created_time': self.created_time,
            'updated_time': self.updated_time,
            'status': self.status,
            'status_reason': self.status_reason,
            'metadata': self.metadata,
            'data': self.data,
            'details': self.details,
        }


class Action(resource.Resource):
    resource_key = 'action'
    resources_key = 'actions'
    base_path = '/actions'
    service = cluster_service.ClusterService()

    # Capabilities
    allow_list = True
    allow_retrieve = True

    # Properties
    id = resource.prop('id')
    name = resource.prop('name')
    target = resource.prop('target')
    action = resource.prop('action')
    cause = resource.prop('cause')
    owner = resource.prop('owner')
    interval = resource.prop('interval')
    start_time = resource.prop('start_time')
    end_time = resource.prop('end_time')
    timeout = resource.prop('timeout')
    status = resource.prop('status')
    status_reason = resource.prop('status_reason')
    inputs = resource.prop('inputs', type=dict)
    outputs = resource.prop('outputs', type=dict)
    depends_on = resource.prop('depends_on', type=list)
    depended_by = resource.prop('depended_by', type=list)

    def to_dict(self):
        action_dict = {
            'id': self.id,
            'name': self.name,
            'action': self.action,
            'target': self.target,
            'cause': self.cause,
            'interval': self.interval,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'interval': self.interval,
            'timeout': self.timeout,
            'status': self.status,
            'status_reason': self.status_reason,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'depends_on': self.depends_on,
            'depended_by': self.depended_by,
        }
        return action_dict


class Receiver(resource.Resource):
    resource_key = 'receiver'
    resources_key = 'receivers'
    base_path = '/receivers'
    service = cluster_service.ClusterService()

    # Capabilities
    allow_list = True
    allow_retrieve = True
    allow_create = True
    allow_delete = True

    # Properties
    id = resource.prop('id')
    user = resource.prop('user')
    project = resource.prop('project')
    domain = resource.prop('domain')
    name = resource.prop('name')
    type = resource.prop('type')
    cluster_id = resource.prop('cluster_id')
    action = resource.prop('action')
    created_time = resource.prop('created_time')
    actor = resource.prop('actor', type=dict)
    params = resource.prop('params', type=dict)
    channel = resource.prop('channel', type=dict)


class Event(resource.Resource):
    resource_key = 'event'
    resources_key = 'events'
    base_path = '/events'
    service = cluster_service.ClusterService()

    # Capabilities
    allow_list = True
    allow_retrieve = True

    # Properties
    id = resource.prop('id')
    timestamp = resource.prop('timestamp')
    obj_id = resource.prop('obj_id')
    obj_name = resource.prop('obj_name')
    obj_type = resource.prop('obj_type')
    cluster_id = resource.prop('cluster_id')
    level = resource.prop('level')
    user = resource.prop('user')
    project = resource.prop('project')
    action = resource.prop('action')
    status = resource.prop('status')
    status_reason = resource.prop('status_reason')

    def to_dict(self):
        event_dict = {
            'id': self.id,
            'timestamp': self.timestamp,
            'obj_id': self.obj_id,
            'obj_type': self.obj_type,
            'obj_name': self.obj_name,
            'cluster_id': self.cluster_id,
            'level': self.level,
            'user': self.user,
            'project': self.project,
            'action': self.action,
            'status': self.status,
            'status_reason': self.status_reason,
        }
        return event_dict
