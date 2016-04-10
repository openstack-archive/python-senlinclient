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
        """List profile types

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html
        #listProfileTypes
        """
        return self.service.profile_types(**query)

    def get_profile_type(self, profile_type):
        """Show profile type details

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#showProfileType
        """
        return self.service.get_profile_type(profile_type)

    def profiles(self, **query):
        """List profiles

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#listProfiles
        """
        return self.service.profiles(**query)

    def create_profile(self, **attrs):
        """Create a profile

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#createProfile
        """
        return self.service.create_profile(**attrs)

    def get_profile(self, profile):
        """Show profile details

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#showProfile
        """
        return self.service.get_profile(profile)

    def update_profile(self, profile, **attrs):
        """Update a profile

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#updateProfile
        """
        return self.service.update_profile(profile, **attrs)

    def delete_profile(self, profile, ignore_missing=True):
        """Delete a profile

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#deleteProfile
        """
        return self.service.delete_profile(profile, ignore_missing)

    def policy_types(self, **query):
        """List policy types

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html
        #listPolicyType
        """
        return self.service.policy_types(**query)

    def get_policy_type(self, policy_type):
        """Show policy type details

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html
        #showPolicyType
        """
        return self.service.get_policy_type(policy_type)

    def policies(self, **query):
        """List policies

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#listPolicies
        """
        return self.service.policies(**query)

    def create_policy(self, **attrs):
        """Create a policy

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#createPolicy
        """
        return self.service.create_policy(**attrs)

    def get_policy(self, policy):
        """Show policy details

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#showPolicy
        """
        return self.service.get_policy(policy)

    def update_policy(self, policy, **attrs):
        """Update policy

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#updatePolicy
        """
        return self.service.update_policy(policy, **attrs)

    def delete_policy(self, policy, ignore_missing=True):
        """Delete policy

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#deletePolicy
        """
        return self.service.delete_policy(policy, ignore_missing)

    def clusters(self, **queries):
        """List clusters

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#listClusters
        """
        return self.service.clusters(**queries)

    def create_cluster(self, **attrs):
        """Create a cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#createCluster
        """
        return self.service.create_cluster(**attrs)

    def get_cluster(self, cluster):
        """Show cluster details

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#showCluster
        """
        return self.service.get_cluster(cluster)

    def update_cluster(self, cluster, **attrs):
        """Update cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#updateCluster
        """
        return self.service.update_cluster(cluster, **attrs)

    def delete_cluster(self, cluster, ignore_missing=True):
        """Delete cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#deleteCluster
        """
        return self.service.delete_cluster(cluster, ignore_missing)

    def cluster_add_nodes(self, cluster, nodes):
        """Add a node to cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#clusterAction
        """
        return self.service.cluster_add_nodes(cluster, nodes)

    def cluster_del_nodes(self, cluster, nodes):
        """Delete a node belongs to cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#clusterAction
        """
        return self.service.cluster_del_nodes(cluster, nodes)

    def cluster_resize(self, cluster, **params):
        """Resize cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#clusterAction
        """
        return self.service.cluster_resize(cluster, **params)

    def cluster_scale_out(self, cluster, count):
        """Scale out cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#clusterAction
        """
        return self.service.cluster_scale_out(cluster, count)

    def cluster_scale_in(self, cluster, count):
        """Scale in cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#clusterAction
        """
        return self.service.cluster_scale_in(cluster, count)

    def cluster_policies(self, cluster, **queries):
        """List all policies attached to cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html
        #listClusterPolicies
        """
        return self.service.cluster_policies(cluster, **queries)

    def get_cluster_policy(self, policy, cluster):
        """Show details of a policy attached to cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html
        #showClusterPolicy
        """
        return self.service.get_cluster_policy(policy, cluster)

    def cluster_attach_policy(self, cluster, policy, **attrs):
        """Attach a policy to cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#clusterAction
        """
        return self.service.cluster_attach_policy(cluster, policy, **attrs)

    def cluster_detach_policy(self, cluster, policy):
        """Detach a policy from cluster

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#clusterAction
        """
        return self.service.cluster_detach_policy(cluster, policy)

    def cluster_update_policy(self, cluster, policy, **attrs):
        """Update the policy attachment

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#clusterAction
        """
        return self.service.cluster_update_policy(cluster, policy, **attrs)

    def check_cluster(self, cluster, **params):
        """Check cluster's health status

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#clusterAction
        """
        return self.service.check_cluster(cluster, **params)

    def recover_cluster(self, cluster, **params):
        """Recover cluster from failure state

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#clusterAction
        """
        return self.service.recover_cluster(cluster, **params)

    def nodes(self, **queries):
        """List nodes

        Doc link: http://developer.openstack.org/api-ref-clustering-v1.html
                  #listNodes
        """
        return self.service.nodes(**queries)

    def create_node(self, **attrs):
        """Create a node

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#createNode
        """
        return self.service.create_node(**attrs)

    def get_node(self, node, args=None):
        """Show node details

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#showNode
        """
        return self.service.get_node(node, args=args)

    def update_node(self, node, **attrs):
        """Update node

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#updateNode
        """
        return self.service.update_node(node, **attrs)

    def delete_node(self, node, ignore_missing=True):
        """Delete node

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#deleteNode
        """
        return self.service.delete_node(node, ignore_missing)

    def check_node(self, node, **params):
        """Check node's health status

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#nodeAction
        """
        return self.service.check_node(node, **params)

    def recover_node(self, node, **params):
        """Recover node from failure state

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#nodeAction
        """
        return self.service.recover_node(node, **params)

    def receivers(self, **queries):
        """List receivers

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#listReceivers
        """
        return self.service.receivers(**queries)

    def create_receiver(self, **attrs):
        """Creare a receiver

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html
        #createReceiver
        """
        return self.service.create_receiver(**attrs)

    def get_receiver(self, receiver):
        """Show receiver details

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#showReceiver
        """
        return self.service.get_receiver(receiver)

    def delete_receiver(self, receiver, ignore_missing=True):
        """Delete receiver

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html
        #deleteReceiver
        """
        return self.service.delete_receiver(receiver, ignore_missing)

    def events(self, **queries):
        """List events

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#listEvents
        """
        return self.service.events(**queries)

    def get_event(self, event):
        """Show event details

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#showEvent
        """
        return self.service.get_event(event)

    def actions(self, **queries):
        """List actions

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#listActions
        """
        return self.service.actions(**queries)

    def get_action(self, action):
        """Show action details

        Doc link:
        http://developer.openstack.org/api-ref-clustering-v1.html#showAction
        """
        return self.service.get_action(action)
