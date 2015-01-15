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

from senlinclient.common import sdk as resource
from senlinclient.openstack.clustering import clustering_service


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
    resources_key = 'profiles'
    base_path = '/profiles'
    service = clustering_service.ClusteringService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_delete = True
    allow_list = True

    # properties
    links = resource.prop('links', type=dict)

    name = resource.prop('name')
    type_name = resource.prop('type')
    spec = resource.prop('spec', type=dict)
    permission = resource.prop('permission')
    tags = resource.prop('tags', type=dict)

    created_time = resource.prop('created_time')
    updated_time = resource.prop('updated_time')
    deleted_time = resource.prop('deleted_time')
    size = resource.prop('size', type=int)
    timeout = resource.prop('timeout')
    status = resource.prop('status')
    status_reason = resource.prop('status_reason')
    tags = resource.prop('tags', type=dict)


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
    links = resource.prop('links', type=dict)
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
    resources_key = 'policies'
    base_path = '/clusters/%(cluster_id)s/nodes'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_create = True
    allow_delete = True

    # Properties
    id = resource.prop('id')
    cluster_id = resource.prop('cluster_id')
    policy_id = resource.prop('policy_id')
    cooldown = resource.prop('cooldown')
    level = resource.prop('level', type=int)
    enabled = resource.prop('enabled')


class Node(resource.Resource):
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
    links = resource.prop('links', type=dict)
    id = resource.prop('id')
    name = resource.prop('name')
    physical_id = resource.prop('physical_id')
    cluster_id = resource.prop('cluster_id')
    profile_id = resource.prop('profile_id')
    index = resource.prop('index', type=int)
    role = resource.prop('role')
    created_time = resource.prop('created_time')
    updated_time = resource.prop('updated_time')
    deleted_time = resource.prop('deleted_time')
    status = resource.prop('status')
    status_reason = resource.prop('status_reason')
    tags = resource.prop('tags', type=dict)
    data = resource.prop('data', type=dict)


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
    context = resource.prop('context')
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
    control = resource.prop('control')
    inputs = resource.prop('inputs', type=dict)
    outputs = resource.prop('outputs', type=dict)
    depends_on = resource.prop('depends_on', type=list)
    depended_by = resource.prop('depended_by', type=list)
    deleted_time = resource.prop('deleted_time')


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
