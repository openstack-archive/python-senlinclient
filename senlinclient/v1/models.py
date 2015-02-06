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

from openstack import utils

from senlinclient.common import sdk as resource
from senlinclient.openstack.clustering import clustering_service


class Version(resource.Resource):
    resource_key = 'version'
    resources_key = 'versions'
    base_path = '/'
    service = clustering_service.ClusteringService(
        version=clustering_service.ClusteringService.UNVERSIONED
    )

    # capabilities
    allow_list = True

    # Properties
    links = resource.prop('links')
    status = resource.prop('status')


class BuildInfo(resource.Resource):
    base_path = '/build_info'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_retrieve = True

    # Properties
    api = resource.prop('api')
    engine = resource.prop('engine')


class ProfileType(resource.Resource):
    resource_key = None
    resources_key = 'profile_types'
    base_path = '/profile_types'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_list = True
    allow_retrieve = True

    # Properties
    name = resource.prop('name')


class ProfileTypeSchema(resource.Resource):
    base_path = '/profile_types/%(profile_type)s'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_retrieve = True

    # Properties
    schema = resource.prop('schema', type=dict)


class ProfileTypeTemplate(resource.Resource):
    resource_key = 'template'
    base_path = '/profile_types/%(profile_type)s/template'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_retrieve = True

    # Properties
    template = resource.prop('template', type=dict)


class Profile(resource.Resource):
    resource_key = 'profile'
    resources_key = 'profiles'
    base_path = '/profiles'
    service = clustering_service.ClusteringService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_delete = True
    allow_list = True

    # properties
    id = resource.prop('id')
    name = resource.prop('name')
    type = resource.prop('type')
    spec = resource.prop('spec', type=dict)
    permission = resource.prop('permission')
    tags = resource.prop('tags', type=dict)
    created_time = resource.prop('created_time')
    deleted_time = resource.prop('deleted_time')

    def to_dict(self):
        pb_dict = {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'permission': self.permission,
            'spec': self.spec,
            'tags': self.tags,
            'created_time': self.created_time,
            'deleted_time': self.deleted_time,
        }
        return pb_dict


class PolicyType(resource.Resource):
    resources_key = 'policy_types'
    base_path = '/policy_types'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_list = True
    allow_retrieve = True

    # Properties
    name = resource.prop('name')


class PolicyTypeSchema(resource.Resource):
    base_path = '/policy_types/%(policy_type)s'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_retrieve = True

    # Properties
    schema = resource.prop('schema', type=dict)


class PolicyTypeTemplate(resource.Resource):
    resource_key = 'template'
    base_path = '/policy_types/%(policy_type)s/template'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_retrieve = True

    # Properties
    template = resource.prop('template', type=dict)


class Policy(resource.Resource):
    resources_key = 'policies'
    base_path = '/policies'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_list = True
    allow_retrieve = True
    allow_create = True
    allow_delete = True
    allow_update = True

    # Properties
    id = resource.prop('id')
    name = resource.prop('name')
    type = resource.prop('type')
    cooldown = resource.prop('cooldown')
    level = resource.prop('level', type=int)
    deleted_time = resource.prop('deleted_time')
    spec = resource.prop('spec', type=dict)
    data = resource.prop('data', type=dict)


class Cluster(resource.Resource):
    resource_key = 'cluster'
    resources_key = 'clusters'
    base_path = '/clusters'
    service = clustering_service.ClusteringService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

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
    deleted_time = resource.prop('deleted_time')
    size = resource.prop('size', type=int)
    timeout = resource.prop('timeout')
    status = resource.prop('status')
    status_reason = resource.prop('status_reason')
    tags = resource.prop('tags', type=dict)
    data = resource.prop('data', type=dict)

    nodes = resource.prop('nodes')

    profile_name = resource.prop('profile_name')
    # action = resource.prop('action')

    def action(self, session, body):
        url = utils.urljoin(self.base_path, self.id, 'action')
        resp = session.put(url, service=self.service, json=body).body
        return resp

    def add_nodes(self, session, nodes):
        body = {
            'add_nodes': {
                'nodes': nodes,
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
            'deleted_time': self.deleted_time,
            'size': self.size,
            'timeout': self.timeout,
            'status': self.status,
            'status_reason': self.status_reason,
            'tags': self.tags or {},
            'data': self.data or {},
            'nodes': self.nodes or [],
            'profile_name': self.profile_name,
        }
        return info


class ClusterPolicy(resource.Resource):
    resources_key = 'policies'
    base_path = '/clusters/%(cluster_id)s/policies'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_list = True
    allow_retrieve = True
    allow_create = True
    allow_delete = True
    allow_update = True

    # Properties
    id = resource.prop('id')
    cluster_id = resource.prop('cluster_id')
    policy_id = resource.prop('policy_id')
    cooldown = resource.prop('cooldown')
    level = resource.prop('level', type=int)
    enabled = resource.prop('enabled')


class ClusterNode(resource.Resource):
    resources_key = 'nodes'
    base_path = '/clusters/%(cluster_id)s/nodes'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_list = True
    allow_create = True
    allow_delete = True

    # Properties
    id = resource.prop('id')
    cluster_id = resource.prop('cluster_id')
    policy_id = resource.prop('node_id')


class Node(resource.Resource):
    resource_key = 'node'
    resources_key = 'nodes'
    base_path = '/nodes'
    service = clustering_service.ClusteringService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    id = resource.prop('id')
    name = resource.prop('name')
    physical_id = resource.prop('physical_id')
    cluster_id = resource.prop('cluster_id')
    profile_id = resource.prop('profile_id')
    profile_name = resource.prop('profile_name')
    index = resource.prop('index', type=int)
    role = resource.prop('role')
    init_time = resource.prop('init_time')
    created_time = resource.prop('created_time')
    updated_time = resource.prop('updated_time')
    deleted_time = resource.prop('deleted_time')
    status = resource.prop('status')
    status_reason = resource.prop('status_reason')
    tags = resource.prop('tags', type=dict)
    data = resource.prop('data', type=dict)

    action = resource.prop('action')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'physical_id': self.physical_id,
            'cluster_id': self.cluster_id,
            'profile_id': self.profile_id,
            'profile_name': self.profile_name,
            'index': self.index,
            'role': self.role,
            'init_time': self.init_time,
            'created_time': self.created_time,
            'updated_time': self.updated_time,
            'deleted_time': self.deleted_time,
            'status': self.status,
            'status_reason': self.status_reason,
            'tags': self.tags,
            'data': self.data,
        }


class Action(resource.Resource):
    resources_key = 'actions'
    base_path = '/actions'
    service = clustering_service.ClusteringService()

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


class Event(resource.Resource):
    resources_key = 'events'
    base_path = '/events'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_list = True
    allow_retrieve = True

    # Properties
    id = resource.prop('id')
    timestamp = resource.prop('timestamp')
    obj_id = resource.prop('obj_id')
    obj_name = resource.prop('obj_name')
    obj_type = resource.prop('obj_type')
    level = resource.prop('level')
    user = resource.prop('user')
    action = resource.prop('action')
    status = resource.prop('status')
    status_reason = resource.prop('status_reason')
