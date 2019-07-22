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
from openstack import exceptions

from senlinclient.common import exc
from senlinclient import plugin


class Client(object):
    def __init__(self, prof=None, user_agent=None, **kwargs):
        try:
            conn = plugin.create_connection(prof=prof,
                                            user_agent=user_agent,
                                            **kwargs)
        except exceptions.HttpException as ex:
            exc.parse_exception(ex.details)

        self.conn = conn
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
        https://docs.openstack.org/api-ref/clustering/#list-profile-types
        """
        return self.service.profile_types(**query)

    def get_profile_type(self, profile_type):
        """Show profile type details

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #show-profile-type-details
        """
        return self.service.get_profile_type(profile_type)

    def list_profile_type_operations(self, profile_type):
        """Show profile type operations

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #show-profile-type-details
        """
        return self.service.list_profile_type_operations(profile_type)

    def profiles(self, **query):
        """List profiles

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#list-profiles
        """
        return self.service.profiles(**query)

    def create_profile(self, **attrs):
        """Create a profile

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#create-profile
        """
        return self.service.create_profile(**attrs)

    def get_profile(self, profile):
        """Show profile details

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#show-profile-details
        """
        return self.service.get_profile(profile)

    def update_profile(self, profile, **attrs):
        """Update a profile

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#update-profile
        """
        return self.service.update_profile(profile, **attrs)

    def delete_profile(self, profile, ignore_missing=True):
        """Delete a profile

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#delete-profile
        """
        return self.service.delete_profile(profile, ignore_missing)

    def validate_profile(self, **attrs):
        """Validate a profile spec

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#validate-profile
        """
        return self.service.validate_profile(**attrs)

    def policy_types(self, **query):
        """List policy types

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#list-policy-types
        """
        return self.service.policy_types(**query)

    def get_policy_type(self, policy_type):
        """Show policy type details

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #show-policy-type-details
        """
        return self.service.get_policy_type(policy_type)

    def policies(self, **query):
        """List policies

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#list-policies
        """
        return self.service.policies(**query)

    def create_policy(self, **attrs):
        """Create a policy

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#create-policy
        """
        return self.service.create_policy(**attrs)

    def get_policy(self, policy):
        """Show policy details

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#show-policy-details
        """
        return self.service.get_policy(policy)

    def update_policy(self, policy, **attrs):
        """Update policy

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#update-policy
        """
        return self.service.update_policy(policy, **attrs)

    def delete_policy(self, policy, ignore_missing=True):
        """Delete policy

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#delete-policy
        """
        return self.service.delete_policy(policy, ignore_missing)

    def validate_policy(self, **attrs):
        """validate a policy spec

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#validate-policy
        """
        return self.service.validate_policy(**attrs)

    def clusters(self, **queries):
        """List clusters

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#list-clusters
        """
        return self.service.clusters(**queries)

    def create_cluster(self, **attrs):
        """Create a cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#create-cluster
        """
        return self.service.create_cluster(**attrs)

    def get_cluster(self, cluster):
        """Show cluster details

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#show-cluster-details
        """
        return self.service.get_cluster(cluster)

    def update_cluster(self, cluster, **attrs):
        """Update cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#update-cluster
        """
        return self.service.update_cluster(cluster, **attrs)

    def delete_cluster(self, cluster, ignore_missing=True, force_delete=False):
        """Delete cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#delete-cluster
        """
        return self.service.delete_cluster(cluster, ignore_missing,
                                           force_delete)

    def cluster_add_nodes(self, cluster, nodes):
        """Add a node to cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #add-nodes-to-a-cluster
        """
        return self.service.add_nodes_to_cluster(cluster, nodes)

    def cluster_del_nodes(self, cluster, nodes):
        """Delete a node belongs to cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #remove-nodes-from-a-cluster
        """
        return self.service.remove_nodes_from_cluster(cluster, nodes)

    def cluster_replace_nodes(self, cluster, nodes):
        """Replace the nodes in a cluster with specified nodes

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #replace-nodes-in-a-cluster
        """
        return self.service.replace_nodes_in_cluster(cluster, nodes)

    def cluster_resize(self, cluster, **params):
        """Resize cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#resize-a-cluster
        """
        return self.service.resize_cluster(cluster, **params)

    def cluster_scale_out(self, cluster, count):
        """Scale out cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#scale-out-a-cluster
        """
        return self.service.scale_out_cluster(cluster, count)

    def cluster_scale_in(self, cluster, count):
        """Scale in cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#scale-in-a-cluster
        """
        return self.service.scale_in_cluster(cluster, count)

    def cluster_policies(self, cluster, **queries):
        """List all policies attached to cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #list-all-cluster-policies
        """
        return self.service.cluster_policies(cluster, **queries)

    def get_cluster_policy(self, policy, cluster):
        """Show details of a policy attached to cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #show-cluster-policy-details
        """
        return self.service.get_cluster_policy(policy, cluster)

    def cluster_attach_policy(self, cluster, policy, **attrs):
        """Attach a policy to cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #attach-a-policy-to-a-cluster
        """
        return self.service.attach_policy_to_cluster(cluster, policy, **attrs)

    def cluster_detach_policy(self, cluster, policy):
        """Detach a policy from cluster

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #detach-a-policy-from-a-cluster
        """
        return self.service.detach_policy_from_cluster(cluster, policy)

    def cluster_update_policy(self, cluster, policy, **attrs):
        """Update the policy attachment

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #update-a-policy-on-a-cluster
        """
        return self.service.update_cluster_policy(cluster, policy, **attrs)

    def collect_cluster_attrs(self, cluster, path):
        """Collect cluster attributes

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #collect-attributes-across-a-cluster
        """
        return self.service.collect_cluster_attrs(cluster, path)

    def check_cluster(self, cluster, **params):
        """Check cluster's health status

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #check-a-cluster-s-health-status
        """
        return self.service.check_cluster(cluster, **params)

    def recover_cluster(self, cluster, **params):
        """Recover cluster from failure state

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #recover-a-cluster-to-a-healthy-status
        """
        return self.service.recover_cluster(cluster, **params)

    def perform_operation_on_cluster(self, cluster, operation, **params):
        """Perform an operation on a cluster.

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #perform-an-operation-on-a-cluster
        """
        return self.service.perform_operation_on_cluster(cluster, operation,
                                                         **params)

    def nodes(self, **queries):
        """List nodes

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#list-nodes
        """
        return self.service.nodes(**queries)

    def create_node(self, **attrs):
        """Create a node

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#create-node
        """
        return self.service.create_node(**attrs)

    def adopt_node(self, preview=False, **attrs):
        """Adopt a node

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#adopt-node
        https://docs.openstack.org/api-ref/clustering/#adopt-node-preview
        """
        return self.service.adopt_node(preview, **attrs)

    def get_node(self, node, details=False):
        """Show node details

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#show-node-details
        """
        return self.service.get_node(node, details=details)

    def update_node(self, node, **attrs):
        """Update node

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#update-node
        """
        return self.service.update_node(node, **attrs)

    def delete_node(self, node, ignore_missing=True, force_delete=False):
        """Delete node

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#delete-node
        """
        return self.service.delete_node(node, ignore_missing, force_delete)

    def check_node(self, node, **params):
        """Check node's health status

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#check-a-node-s-health
        """
        return self.service.check_node(node, **params)

    def recover_node(self, node, **params):
        """Recover node from failure state

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #recover-a-node-to-healthy-status
        """
        return self.service.recover_node(node, **params)

    def perform_operation_on_node(self, node, operation, **params):
        """Perform an operation on a node.

        Doc link:
        https://docs.openstack.org/api-ref/clustering/
        #perform-an-operation-on-a-node
        """
        return self.service.perform_operation_on_node(node, operation,
                                                      **params)

    def receivers(self, **queries):
        """List receivers

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#list-receivers
        """
        return self.service.receivers(**queries)

    def create_receiver(self, **attrs):
        """Creare a receiver

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#create-receiver
        """
        return self.service.create_receiver(**attrs)

    def get_receiver(self, receiver):
        """Show receiver details

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#show-receiver-details
        """
        return self.service.get_receiver(receiver)

    def update_receiver(self, receiver, **attrs):
        """Update receiver

        Doc link:
        https://docs.openstack.org/api-ref-clustering-v1.html#updateReceiver
        """
        return self.service.update_receiver(receiver, **attrs)

    def delete_receiver(self, receiver, ignore_missing=True):
        """Delete receiver

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#delete-receiver
        """
        return self.service.delete_receiver(receiver, ignore_missing)

    def events(self, **queries):
        """List events

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#list-events
        """
        return self.service.events(**queries)

    def get_event(self, event):
        """Show event details

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#shows-event-details
        """
        return self.service.get_event(event)

    def actions(self, **queries):
        """List actions

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#list-actions
        """
        return self.service.actions(**queries)

    def get_action(self, action):
        """Show action details

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#show-action-details
        """
        return self.service.get_action(action)

    def services(self, **queries):
        """List services

        Doc link:
        https://docs.openstack.org/api-ref/clustering/#list-services
        """
        return self.service.services(**queries)
