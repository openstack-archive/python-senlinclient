# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from senlinclient.common import sdk


class Client(object):

    def __init__(self, preferences=None, user_agent=None, **kwargs):
        self.conn = sdk.create_connection(preferences, user_agent, **kwargs)
        self.service = self.conn.cluster

    ######################################################################
    # The following operations are interfaces exposed to other software
    # which invokes senlinclient today.
    # These methods form a temporary translation layer. This layer will be
    # useless when OpenStackSDK has been adopted all senlin resources.
    ######################################################################

    def profile_types(self, **query):
        return self.service.profile_types(**query)

    def get_profile_type(self, profile_type):
        return self.service.get_profile_type(profile_type)

    def profiles(self, **query):
        return self.service.profiles(**query)

    def create_profile(self, **attrs):
        return self.service.create_profile(**attrs)

    def get_profile(self, profile):
        return self.service.get_profile(profile)

    def update_profile(self, profile, **attrs):
        return self.service.update_profile(profile, **attrs)

    def delete_profile(self, profile, ignore_missing=True):
        return self.service.delete_profile(profile, ignore_missing)

    def policy_types(self, **query):
        return self.service.policy_types(**query)

    def get_policy_type(self, policy_type):
        return self.service.get_policy_type(policy_type)

    def policies(self, **query):
        return self.service.policies(**query)

    def create_policy(self, **attrs):
        return self.service.create_policy(**attrs)

    def get_policy(self, policy):
        return self.service.get_policy(policy)

    def update_policy(self, policy, **attrs):
        return self.service.update_policy(policy, **attrs)

    def delete_policy(self, policy, ignore_missing=True):
        return self.service.delete_policy(policy, ignore_missing)

    def clusters(self, **queries):
        return self.service.clusters(**queries)

    def create_cluster(self, **attrs):
        return self.service.create_cluster(**attrs)

    def get_cluster(self, cluster):
        return self.service.get_cluster(cluster)

    def update_cluster(self, cluster, **attrs):
        return self.service.update_cluster(cluster, **attrs)

    def delete_cluster(self, cluster, ignore_missing=True):
        return self.service.delete_cluster(cluster, ignore_missing)

    def cluster_add_nodes(self, cluster, nodes):
        return self.service.cluster_add_nodes(cluster, nodes)

    def cluster_del_nodes(self, cluster, nodes):
        return self.service.cluster_del_nodes(cluster, nodes)

    def cluster_resize(self, cluster, **params):
        return self.service.cluster_resize(cluster, **params)

    def cluster_scale_out(self, cluster, count):
        return self.service.cluster_scale_out(cluster, count)

    def cluster_scale_in(self, cluster, count):
        return self.service.cluster_scale_in(cluster, count)

    def cluster_policies(self, cluster, **queries):
        return self.service.cluster_policies(cluster, **queries)

    def get_cluster_policy(self, policy, cluster):
        return self.service.get_cluster_policy(policy, cluster)

    def cluster_attach_policy(self, cluster, policy, **attrs):
        return self.service.cluster_attach_policy(cluster, policy, **attrs)

    def cluster_detach_policy(self, cluster, policy):
        return self.service.cluster_detach_policy(cluster, policy)

    def cluster_update_policy(self, cluster, policy, **attrs):
        return self.service.cluster_update_policy(cluster, policy, **attrs)

    def nodes(self, **queries):
        return self.service.nodes(**queries)

    def create_node(self, **attrs):
        return self.service.create_node(**attrs)

    def get_node(self, node, args=None):
        return self.service.get_node(node, args=args)

    def update_node(self, node, **attrs):
        return self.service.update_node(node, **attrs)

    def delete_node(self, node, ignore_missing=True):
        return self.service.delete_node(node, ignore_missing)

    def receivers(self, **queries):
        return self.service.receivers(**queries)

    def create_receiver(self, **attrs):
        return self.service.create_receiver(**attrs)

    def get_receiver(self, receiver):
        return self.service.get_receiver(receiver)

    def delete_receiver(self, receiver, ignore_missing=True):
        return self.service.delete_receiver(receiver, ignore_missing)

    def events(self, **queries):
        return self.service.events(**queries)

    def get_event(self, event):
        return self.service.get_event(event)

    def actions(self, **queries):
        return self.service.actions(**queries)

    def get_action(self, action):
        return self.service.get_action(action)
