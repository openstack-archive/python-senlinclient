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

"""Clustering v1 cluster action implementations"""

import logging
import subprocess
import sys
import threading
import time

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions as exc
from osc_lib import utils
from oslo_utils import strutils
import six

from senlinclient.common.i18n import _
from senlinclient.common import utils as senlin_utils


class ListCluster(command.Lister):
    """List clusters."""

    log = logging.getLogger(__name__ + ".ListCluster")

    def get_parser(self, prog_name):
        parser = super(ListCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--filters',
            metavar='<"key1=value1;key2=value2...">',
            help=_("Filter parameters to apply on returned clusters. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter"
                   " keys are: ['status', 'name']"),
            action='append'
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc). The valid "
                   "sort keys are: ['name', 'status', 'init_at', "
                   "'created_at', 'updated_at']"))
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of clusters returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return clusters that appear after the given cluster '
                   'ID')
        )
        parser.add_argument(
            '--global-project',
            default=False,
            action="store_true",
            help=_('Indicate that the cluster list should include clusters '
                   'from all projects. This option is subject to access '
                   'policy checking. Default is False')
        )
        parser.add_argument(
            '--full-id',
            default=False,
            action="store_true",
            help=_('Print full IDs in list')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        columns = ['id', 'name', 'status', 'created_at', 'updated_at']
        queries = {
            'limit': parsed_args.limit,
            'marker': parsed_args.marker,
            'sort': parsed_args.sort,
            'global_project': parsed_args.global_project,
        }
        if parsed_args.filters:
            queries.update(senlin_utils.format_parameters(parsed_args.filters))

        clusters = senlin_client.clusters(**queries)
        formatters = {}
        if parsed_args.global_project:
            columns.append('project_id')
        if not parsed_args.full_id:
            formatters = {
                'id': lambda x: x[:8]
            }
            if 'project_id' in columns:
                formatters['project_id'] = lambda x: x[:8]

        return (
            columns,
            (utils.get_item_properties(c, columns, formatters=formatters)
             for c in clusters)
        )


class ShowCluster(command.ShowOne):
    """Show details of the cluster."""

    log = logging.getLogger(__name__ + ".ShowCluster")

    def get_parser(self, prog_name):
        parser = super(ShowCluster, self).get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to show')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        return _show_cluster(senlin_client, parsed_args.cluster)


def _show_cluster(senlin_client, cluster_id):
    try:
        cluster = senlin_client.get_cluster(cluster_id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Cluster not found: %s') % cluster_id)

    formatters = {
        'config': senlin_utils.json_formatter,
        'metadata': senlin_utils.json_formatter,
        'node_ids': senlin_utils.list_formatter
    }
    data = cluster.to_dict()
    if 'is_profile_only' in data:
        data.pop('is_profile_only')
    columns = sorted(data.keys())
    return columns, utils.get_dict_properties(data, columns,
                                              formatters=formatters)


class CreateCluster(command.ShowOne):
    """Create the cluster."""

    log = logging.getLogger(__name__ + ".CreateCluster")

    def get_parser(self, prog_name):
        parser = super(CreateCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--config',
            metavar='<"key1=value1;key2=value2...">',
            help=_('Configuration of the cluster. Default to {}. '
                   'This can be specified multiple times, or once with '
                   'key-value pairs separated by a semicolon.'),
            action='append'
        )
        parser.add_argument(
            '--min-size',
            metavar='<min-size>',
            default=0,
            help=_('Min size of the cluster. Default to 0')
        )
        parser.add_argument(
            '--max-size',
            metavar='<max-size>',
            default=-1,
            help=_('Max size of the cluster. Default to -1, means unlimited')
        )
        parser.add_argument(
            '--desired-capacity',
            metavar='<desired-capacity>',
            default=0,
            help=_('Desired capacity of the cluster. Default to min_size if '
                   'min_size is specified else 0.')
        )
        parser.add_argument(
            '--timeout',
            metavar='<timeout>',
            type=int,
            help=_('Cluster creation timeout in seconds')
        )
        parser.add_argument(
            '--metadata',
            metavar='<"key1=value1;key2=value2...">',
            help=_('Metadata values to be attached to the cluster. '
                   'This can be specified multiple times, or once with '
                   'key-value pairs separated by a semicolon.'),
            action='append'
        )
        parser.add_argument(
            '--profile',
            metavar='<profile>',
            required=True,
            help=_('Default profile Id or name used for this cluster')
        )
        parser.add_argument(
            'name',
            metavar='<cluster-name>',
            help=_('Name of the cluster to create')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        if parsed_args.min_size and not parsed_args.desired_capacity:
            parsed_args.desired_capacity = parsed_args.min_size
        attrs = {
            'config': senlin_utils.format_parameters(parsed_args.config),
            'name': parsed_args.name,
            'profile_id': parsed_args.profile,
            'min_size': parsed_args.min_size,
            'max_size': parsed_args.max_size,
            'desired_capacity': parsed_args.desired_capacity,
            'metadata': senlin_utils.format_parameters(parsed_args.metadata),
            'timeout': parsed_args.timeout
        }

        cluster = senlin_client.create_cluster(**attrs)
        return _show_cluster(senlin_client, cluster.id)


class UpdateCluster(command.ShowOne):
    """Update the cluster."""

    log = logging.getLogger(__name__ + ".UpdateCluster")

    def get_parser(self, prog_name):
        parser = super(UpdateCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--config',
            metavar='<"key1=value1;key2=value2...">',
            help=_('s of the cluster. Default to {}. '
                   'This can be specified multiple times, or once with '
                   'key-value pairs separated by a semicolon.'),
            action='append'
        )
        parser.add_argument(
            '--profile',
            metavar='<profile>',
            help=_('ID or name of new profile to use')
        )
        parser.add_argument(
            '--profile-only',
            default=False, metavar='<boolean>',
            help=_("Whether the cluster should be updated profile only. "
                   "If false, it will be applied to all existing nodes. "
                   "If true, any newly created nodes will use the new profile,"
                   "but existing nodes will not be changed. Default is False.")

        )
        parser.add_argument(
            '--timeout',
            metavar='<timeout>',
            help=_('New timeout (in seconds) value for the cluster')
        )
        parser.add_argument(
            '--metadata',
            metavar='<"key1=value1;key2=value2...">',
            help=_("Metadata values to be attached to the cluster. "
                   "This can be specified multiple times, or once with "
                   "key-value pairs separated by a semicolon. Use '{}' "
                   "can clean metadata "),
            action='append'
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New name for the cluster to update')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to be updated')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        cluster = senlin_client.find_cluster(parsed_args.cluster)
        if cluster is None:
            raise exc.CommandError(_('Cluster not found: %s') %
                                   parsed_args.cluster)
        attrs = {
            'name': parsed_args.name,
            'profile_id': parsed_args.profile,
            'profile_only': strutils.bool_from_string(
                parsed_args.profile_only,
                strict=True,
            ),
            'metadata': senlin_utils.format_parameters(parsed_args.metadata),
            'timeout': parsed_args.timeout,
        }

        senlin_client.update_cluster(cluster, **attrs)
        return _show_cluster(senlin_client, cluster.id)


class DeleteCluster(command.Command):
    """Delete the cluster(s)."""

    log = logging.getLogger(__name__ + ".DeleteCluster")

    def get_parser(self, prog_name):
        parser = super(DeleteCluster, self).get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            nargs='+',
            help=_('Name or ID of cluster(s) to delete.')
        )
        parser.add_argument(
            '--force-delete',
            action='store_true',
            help=_('Force to delete cluster(s).')
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help=_('Skip yes/no prompt (assume yes).')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        try:
            if not parsed_args.force and sys.stdin.isatty():
                sys.stdout.write(
                    _("Are you sure you want to delete this cluster(s)"
                      " [y/N]?"))
                prompt_response = sys.stdin.readline().lower()
                if not prompt_response.startswith('y'):
                    return
        except KeyboardInterrupt:  # Ctrl-c
            self.log.info('Ctrl-c detected.')
            return
        except EOFError:  # Ctrl-d
            self.log.info('Ctrl-d detected')
            return

        result = {}
        for cid in parsed_args.cluster:
            try:
                cluster_delete_action = senlin_client.delete_cluster(
                    cid, False, parsed_args.force_delete)
                result[cid] = ('OK', cluster_delete_action['id'])
            except Exception as ex:
                result[cid] = ('ERROR', six.text_type(ex))

        for rid, res in result.items():
            senlin_utils.print_action_result(rid, res)


class ResizeCluster(command.Command):
    """Resize a cluster."""

    log = logging.getLogger(__name__ + ".ResizeCluster")

    def get_parser(self, prog_name):
        parser = super(ResizeCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--capacity',
            metavar='<capacity>',
            type=int,
            help=_('The desired number of nodes of the cluster')
        )
        parser.add_argument(
            '--adjustment',
            metavar='<adjustment>',
            type=int,
            help=_('A positive integer meaning the number of nodes to add, '
                   'or a negative integer indicating the number of nodes to '
                   'remove')
        )
        parser.add_argument(
            '--percentage',
            metavar='<percentage>',
            type=float,
            help=_('A value that is interpreted as the percentage of size '
                   'adjustment. This value can be positive or negative')
        )
        parser.add_argument(
            '--min-step',
            metavar='<min-step>',
            type=int,
            help=_('An integer specifying the number of nodes for adjustment '
                   'when <PERCENTAGE> is specified')
        )
        parser.add_argument(
            '--strict',
            action='store_true',
            default=False,
            help=_('A boolean specifying whether the resize should be '
                   'performed on a best-effort basis when the new capacity '
                   'may go beyond size constraints')
        )
        parser.add_argument(
            '--min-size',
            metavar='min',
            type=int,
            help=_('New lower bound of cluster size')
        )
        parser.add_argument(
            '--max-size',
            metavar='max',
            type=int,
            help=_('New upper bound of cluster size. A value of -1 indicates '
                   'no upper limit on cluster size')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to operate on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        action_args = {}

        capacity = parsed_args.capacity
        adjustment = parsed_args.adjustment
        percentage = parsed_args.percentage
        min_size = parsed_args.min_size
        max_size = parsed_args.max_size
        min_step = parsed_args.min_step

        if sum(v is not None for v in (capacity, adjustment, percentage,
                                       min_size, max_size)) == 0:
            raise exc.CommandError(_("At least one parameter of 'capacity', "
                                     "'adjustment', 'percentage', 'min_size' "
                                     "and 'max_size' should be specified."))

        if sum(v is not None for v in (capacity, adjustment, percentage)) > 1:
            raise exc.CommandError(_("Only one of 'capacity', 'adjustment' and"
                                     " 'percentage' can be specified."))

        action_args['adjustment_type'] = None
        action_args['number'] = None

        if capacity is not None:
            if capacity < 0:
                raise exc.CommandError(_('Cluster capacity must be larger than'
                                         ' or equal to zero.'))
            action_args['adjustment_type'] = 'EXACT_CAPACITY'
            action_args['number'] = capacity

        if adjustment is not None:
            if adjustment == 0:
                raise exc.CommandError(_('Adjustment cannot be zero.'))
            action_args['adjustment_type'] = 'CHANGE_IN_CAPACITY'
            action_args['number'] = adjustment

        if percentage is not None:
            if (percentage == 0 or percentage == 0.0):
                raise exc.CommandError(_('Percentage cannot be zero.'))
            action_args['adjustment_type'] = 'CHANGE_IN_PERCENTAGE'
            action_args['number'] = percentage

        if min_step is not None and percentage is None:
            raise exc.CommandError(_('Min step is only used with '
                                     'percentage.'))

        if min_size is not None:
            if min_size < 0:
                raise exc.CommandError(_('Min size cannot be less than zero.'))
            if max_size is not None and max_size >= 0 and min_size > max_size:
                raise exc.CommandError(_('Min size cannot be larger than '
                                         'max size.'))
            if capacity is not None and min_size > capacity:
                raise exc.CommandError(_('Min size cannot be larger than the '
                                         'specified capacity'))

        if max_size is not None:
            if capacity is not None and max_size > 0 and max_size < capacity:
                raise exc.CommandError(_('Max size cannot be less than the '
                                         'specified capacity.'))
            # do a normalization
            if max_size < 0:
                max_size = -1

        action_args['min_size'] = min_size
        action_args['max_size'] = max_size
        action_args['min_step'] = min_step
        action_args['strict'] = parsed_args.strict

        resp = senlin_client.resize_cluster(parsed_args.cluster, **action_args)
        if 'action' in resp:
            print('Request accepted by action: %s' % resp['action'])
        else:
            print('Request error: %s' % resp)


class ScaleInCluster(command.Command):
    """Scale in a cluster by the specified number of nodes."""

    log = logging.getLogger(__name__ + ".ScaleInCluster")

    def get_parser(self, prog_name):
        parser = super(ScaleInCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--count',
            metavar='<count>',
            help=_('Number of nodes to be deleted from the specified cluster')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to operate on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        resp = senlin_client.scale_in_cluster(parsed_args.cluster,
                                              parsed_args.count)
        status_code = resp.get('code', None)
        if status_code in [409]:
            raise exc.CommandError(_(
                'Unable to scale in cluster: %s') % resp['error']['message'])
        if 'action' in resp:
            print('Request accepted by action: %s' % resp['action'])
        else:
            print('Request error: %s' % resp)


class ScaleOutCluster(command.Command):
    """Scale out a cluster by the specified number of nodes."""

    log = logging.getLogger(__name__ + ".ScaleOutCluster")

    def get_parser(self, prog_name):
        parser = super(ScaleOutCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--count',
            metavar='<count>',
            help=_('Number of nodes to be added to the specified cluster')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to operate on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        resp = senlin_client.scale_out_cluster(parsed_args.cluster,
                                               parsed_args.count)
        status_code = resp.get('code', None)
        if status_code in [409]:
            raise exc.CommandError(_(
                'Unable to scale out cluster: %s') % resp['error']['message'])
        if 'action' in resp:
            print('Request accepted by action: %s' % resp['action'])
        else:
            print('Request error: %s' % resp)


class ClusterPolicyAttach(command.Command):
    """Attach policy to cluster."""

    log = logging.getLogger(__name__ + ".ClusterPolicyAttach")

    def get_parser(self, prog_name):
        parser = super(ClusterPolicyAttach, self).get_parser(prog_name)
        parser.add_argument(
            '--enabled',
            metavar='<boolean>',
            default=True,
            help=_('Whether the policy should be enabled once attached. '
                   'Default to True')
        )
        parser.add_argument(
            '--policy',
            metavar='<policy>',
            required=True,
            help=_('ID or name of policy to be attached')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to operate on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        kwargs = {
            'enabled': strutils.bool_from_string(parsed_args.enabled,
                                                 strict=True),
        }

        resp = senlin_client.attach_policy_to_cluster(parsed_args.cluster,
                                                      parsed_args.policy,
                                                      **kwargs)
        if 'action' in resp:
            print('Request accepted by action: %s' % resp['action'])
        else:
            print('Request error: %s' % resp)


class ClusterPolicyDetach(command.Command):
    """Detach policy from cluster."""

    log = logging.getLogger(__name__ + ".ClusterPolicyDetach")

    def get_parser(self, prog_name):
        parser = super(ClusterPolicyDetach, self).get_parser(prog_name)
        parser.add_argument(
            '--policy',
            metavar='<policy>',
            required=True,
            help=_('ID or name of policy to be detached')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to operate on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        resp = senlin_client.detach_policy_from_cluster(parsed_args.cluster,
                                                        parsed_args.policy)
        if 'action' in resp:
            print('Request accepted by action: %s' % resp['action'])
        else:
            print('Request error: %s' % resp)


class ClusterNodeList(command.Lister):
    """List nodes from cluster."""

    log = logging.getLogger(__name__ + ".ClusterNodeList")

    def get_parser(self, prog_name):
        parser = super(ClusterNodeList, self).get_parser(prog_name)
        parser.add_argument(
            '--filters',
            metavar='<key1=value1;key2=value2...>',
            help=_("Filter parameters to apply on returned nodes. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['status', 'name']"),
            action='append'
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc)' The valid "
                   "sort keys are:['index', 'name', 'status', 'init_at', "
                   "'created_at', 'updated_at']")
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of nodes returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return nodes that appear after the given node ID')
        )
        parser.add_argument(
            '--full-id',
            default=False,
            action="store_true",
            help=_('Print full IDs in list')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to nodes from')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        queries = {
            'cluster_id': parsed_args.cluster,
            'sort': parsed_args.sort,
            'limit': parsed_args.limit,
            'marker': parsed_args.marker,
        }
        if parsed_args.filters:
            queries.update(senlin_utils.format_parameters(parsed_args.filters))

        nodes = senlin_client.nodes(**queries)
        if not parsed_args.full_id:
            formatters = {
                'id': lambda x: x[:8],
                'physical_id': lambda x: x[:8] if x else ''
            }
        else:
            formatters = {}

        columns = ['id', 'name', 'index', 'status', 'physical_id',
                   'created_at']
        return (
            columns,
            (utils.get_item_properties(n, columns, formatters=formatters)
             for n in nodes)
        )


class ClusterNodeAdd(command.Command):
    """Add specified nodes to cluster."""
    log = logging.getLogger(__name__ + ".ClusterNodeAdd")

    def get_parser(self, prog_name):
        parser = super(ClusterNodeAdd, self).get_parser(prog_name)
        parser.add_argument(
            '--nodes',
            metavar='<nodes>',
            required=True,
            help=_('ID or name of nodes to be added; multiple nodes can be'
                   ' separated with ","')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to operate on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        node_ids = parsed_args.nodes.split(',')
        resp = senlin_client.add_nodes_to_cluster(parsed_args.cluster,
                                                  node_ids)
        if 'action' in resp:
            print('Request accepted by action: %s' % resp['action'])
        else:
            print('Request error: %s' % resp)


class ClusterNodeDel(command.Command):
    """Delete specified nodes from cluster."""
    log = logging.getLogger(__name__ + ".ClusterNodeDel")

    def get_parser(self, prog_name):
        parser = super(ClusterNodeDel, self).get_parser(prog_name)
        parser.add_argument(
            '--nodes',
            metavar='<nodes>',
            required=True,
            help=_('Name or ID of nodes to be deleted; multiple nodes can be '
                   'separated with ","')
        )
        parser.add_argument(
            '-d',
            '--destroy-after-deletion',
            required=False,
            default=False,
            help=_('Whether nodes should be destroyed after deleted. '
                   'Default is False.')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to operate on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        node_ids = parsed_args.nodes.split(',')
        destroy = parsed_args.destroy_after_deletion
        destroy = strutils.bool_from_string(destroy, strict=True)
        kwargs = {"destroy_after_deletion": destroy}
        resp = senlin_client.remove_nodes_from_cluster(
            parsed_args.cluster, node_ids, **kwargs)
        if 'action' in resp:
            print('Request accepted by action: %s' % resp['action'])
        else:
            print('Request error: %s' % resp)


class ClusterNodeReplace(command.Command):
    """Replace the nodes in a cluster with specified nodes."""
    log = logging.getLogger(__name__ + ".ClusterNodeReplace")

    def get_parser(self, prog_name):
        parser = super(ClusterNodeReplace, self).get_parser(prog_name)
        parser.add_argument(
            '--nodes',
            metavar='<OLD_NODE1=NEW_NODE1>',
            required=True,
            help=_("OLD_NODE is the name or ID of a node to be replaced, "
                   "NEW_NODE is the name or ID of a node as replacement. "
                   "This can be specified multiple times, or once with "
                   "node-pairs separated by a comma ','."),
            action='append'
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to operate on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        nodepairs = {}
        for nodepair in parsed_args.nodes:
            key = nodepair.split('=')[0]
            value = nodepair.split('=')[1]
            nodepairs[key] = value
        resp = senlin_client.replace_nodes_in_cluster(parsed_args.cluster,
                                                      nodepairs)
        if 'action' in resp:
            print('Request accepted by action: %s' % resp['action'])
        else:
            print('Request error: %s' % resp)


class CheckCluster(command.Command):
    """Check the cluster(s)."""
    log = logging.getLogger(__name__ + ".CheckCluster")

    def get_parser(self, prog_name):
        parser = super(CheckCluster, self).get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            nargs='+',
            help=_('ID or name of cluster(s) to operate on.')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        for cid in parsed_args.cluster:
            try:
                resp = senlin_client.check_cluster(cid)
            except sdk_exc.ResourceNotFound:
                raise exc.CommandError(_('Cluster not found: %s') % cid)
            if 'action' in resp:
                print('Cluster check request on cluster %(cid)s is '
                      'accepted by action %(action)s.'
                      % {'cid': cid, 'action': resp['action']})
            else:
                print('Request error: %s' % resp)


class RecoverCluster(command.Command):
    """Recover the cluster(s)."""
    log = logging.getLogger(__name__ + ".RecoverCluster")

    def get_parser(self, prog_name):
        parser = super(RecoverCluster, self).get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            nargs='+',
            help=_('ID or name of cluster(s) to operate on.')
        )

        parser.add_argument(
            '--check',
            metavar='<boolean>',
            default=False,
            help=_("Whether the cluster should check it's nodes status before "
                   "doing cluster recover. Default is false")
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        params = {
            'check': strutils.bool_from_string(parsed_args.check, strict=True)
        }

        for cid in parsed_args.cluster:
            try:
                resp = senlin_client.recover_cluster(cid, **params)
            except sdk_exc.ResourceNotFound:
                raise exc.CommandError(_('Cluster not found: %s') % cid)
            if 'action' in resp:
                print('Cluster recover request on cluster %(cid)s is '
                      'accepted by action %(action)s.'
                      % {'cid': cid, 'action': resp['action']})
            else:
                print('Request error: %s' % resp)


class ClusterCollect(command.Lister):
    """Collect attributes across a cluster."""
    log = logging.getLogger(__name__ + ".ClusterCollect")

    def get_parser(self, prog_name):
        parser = super(ClusterCollect, self).get_parser(prog_name)
        parser.add_argument(
            '--full-id',
            default=False,
            action="store_true",
            help=_('Print full IDs in list')
        )
        parser.add_argument(
            '--path',
            metavar='<path>',
            required=True,
            help=_('JSON path expression for attribute to be collected')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('ID or name of cluster(s) to operate on.')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        attrs = senlin_client.collect_cluster_attrs(parsed_args.cluster,
                                                    parsed_args.path)
        columns = ['node_id', 'attr_value']
        formatters = {}
        if not parsed_args.full_id:
            formatters = {
                'node_id': lambda x: x[:8]
            }
        return (columns,
                (utils.get_item_properties(a, columns, formatters=formatters)
                 for a in attrs))


class ClusterOp(command.Lister):
    """Perform an operation on all nodes across a cluster."""
    log = logging.getLogger(__name__ + ".ClusterOp")

    def get_parser(self, prog_name):
        parser = super(ClusterOp, self).get_parser(prog_name)
        parser.add_argument(
            '--operation',
            metavar='<operation>',
            required=True,
            help=_('Operation to be performed on the cluster')
        )
        parser.add_argument(
            '--params',
            metavar='<key1=value1;key2=value2...>',
            help=_("Parameters to for the specified operation. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon."),
            action='append'
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('ID or name of cluster to operate on.')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        cid = parsed_args.cluster
        if parsed_args.params:
            params = senlin_utils.format_parameters(parsed_args.params)
        else:
            params = {}

        try:
            resp = senlin_client.perform_operation_on_cluster(
                cid, parsed_args.operation, **params)
        except sdk_exc.ResourceNotFound:
            raise exc.CommandError(_('Cluster not found: %s') % cid)
        if 'action' in resp:
            print('Request accepted by action: %s' % resp['action'])
        else:
            print('Request error: %s' % resp)


class ClusterRun(command.Command):
    """Run scripts on cluster."""
    log = logging.getLogger(__name__ + ".ClusterRun")

    def get_parser(self, prog_name):
        parser = super(ClusterRun, self).get_parser(prog_name)
        parser.add_argument(
            '--port',
            metavar='<port>',
            type=int,
            default=22,
            help=_('The TCP port to use for SSH connection')
        )
        parser.add_argument(
            '--address-type',
            metavar='<address_type>',
            default='floating',
            help=_("The type of IP address to use. Possible values include "
                   "'fixed' and 'floating' (the default)")
        )
        parser.add_argument(
            '--network',
            metavar='<network>',
            default='',
            help=_("The network to use for SSH connection")
        )
        parser.add_argument(
            '--ipv6',
            action="store_true",
            default=False,
            help=_("Whether the IPv6 address should be used for SSH. Default "
                   "to use IPv4 address.")
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            default='root',
            help=_("The login name to use for SSH connection. Default to "
                   "'root'.")
        )
        parser.add_argument(
            '--identity-file',
            metavar='<identity_file>',
            help=_("The private key file to use, same as the '-i' SSH option")
        )
        parser.add_argument(
            '--ssh-options',
            metavar='<ssh_options>',
            default="",
            help=_("Extra options to pass to SSH. See: man ssh.")
        )
        parser.add_argument(
            '--script',
            metavar='<script>',
            required=True,
            help=_("Path name of the script file to run")
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('ID or name of cluster(s) to operate on.')
        )
        return parser

    def take_action(self, args):
        self.log.debug("take_action(%s)", args)
        service = self.app.client_manager.clustering

        if '@' in args.cluster:
            user, cluster = args.cluster.split('@', 1)
            args.user = user
            args.cluster = cluster

        try:
            attributes = service.collect_cluster_attrs(args.cluster, 'details')
        except sdk_exc.ResourceNotFound:
            raise exc.CommandError(_("Cluster not found: %s") % args.cluster)

        try:
            f = open(args.script, 'r')
            script = f.read()
        except Exception:
            raise exc.CommandError(_("Could not open script file: %s") %
                                   args.script)

        tasks = dict()
        for attr in attributes:
            node_id = attr.node_id
            addr = attr.attr_value['addresses']

            output = dict()
            th = threading.Thread(
                target=self._run_script,
                args=(node_id, addr, args.network, args.address_type,
                      args.port, args.user, args.ipv6, args.identity_file,
                      script, args.ssh_options),
                kwargs={'output': output})
            th.start()
            tasks[th] = (node_id, output)

        for t in tasks:
            t.join()

        for t in tasks:
            node_id, result = tasks[t]
            print("node: %s" % node_id)
            print("status: %s" % result.get('status'))
            if "reason" in result:
                print("reason: %s" % result.get('reason'))
            if "output" in result:
                print("output:\n%s" % result.get('output'))
            if "error" in result:
                print("error:\n%s" % result.get('error'))

    def _run_script(self, node_id, addr, net, addr_type, port, user, ipv6,
                    identity_file, script, options, output=None):
        version = 6 if ipv6 else 4

        # Select the network to use.
        if net:
            addresses = addr.get(net)
            if not addresses:
                output['status'] = _('FAILED')
                output['error'] = _("Node '%(node)s' is not attached to "
                                    "network '%(net)s'.") % {'node': node_id,
                                                             'net': net}
                return
        else:
            # network not specified
            if len(addr) > 1:
                output['status'] = _('FAILED')
                output['error'] = _("Node '%(node)s' is attached to more "
                                    "than one network. Please pick the "
                                    "network to use.") % {'node': node_id}
                return
            elif not addr:
                output['status'] = _('FAILED')
                output['error'] = _("Node '%(node)s' is not attached to any "
                                    "network.") % {'node': node_id}
                return
            else:
                addresses = list(addr.values())[0]

        # Select the address in the selected network.
        # If the extension is not present, we assume the address to be
        # floating.
        matching_addresses = []
        for a in addresses:
            a_type = a.get('OS-EXT-IPS:type', 'floating')
            a_version = a.get('version')
            if (a_version == version and a_type == addr_type):
                matching_addresses.append(a.get('addr'))

        if not matching_addresses:
            output['status'] = _('FAILED')
            output['error'] = _("No address that matches network '%(net)s' "
                                "and type '%(type)s' of IPv%(ver)s has been "
                                "found for node '%(node)s'."
                                ) % {'net': net, 'type': addr_type,
                                     'ver': version, 'node': node_id}
            return

        if len(matching_addresses) > 1:
            output['status'] = _('FAILED')
            output['error'] = _("More than one IPv%(ver)s %(type)s address "
                                "found.") % {'ver': version,
                                             'type': addr_type}
            return

        ip_address = str(matching_addresses[0])
        identity = '-i %s' % identity_file if identity_file else ''

        cmd = [
            'ssh',
            '-%d' % version,
            '-p%d' % port,
            identity,
            options,
            '%s@%s' % (user, ip_address),
            '%s' % script
        ]

        self.log.debug("%s" % cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()

        while proc.returncode is None:
            time.sleep(1)

        if proc.returncode == 0:
            output['status'] = _('SUCCEEDED (0)')
            output['output'] = stdout
            if stderr:
                output['error'] = stderr
        else:
            output['status'] = _('FAILED (%d)') % proc.returncode
            output['output'] = stdout
            if stderr:
                output['error'] = stderr
