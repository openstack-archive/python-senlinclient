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
import six
import sys

from cliff import command
from cliff import lister
from cliff import show
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc
from openstackclient.common import utils

from senlinclient.common.i18n import _
from senlinclient.common.i18n import _LI
from senlinclient.common import utils as senlin_utils


class ListCluster(lister.Lister):
    """List the user's clusters."""

    log = logging.getLogger(__name__ + ".ListCluster")

    def get_parser(self, prog_name):
        parser = super(ListCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--filters',
            metavar='<key1=value1;key=value...>',
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
        if not parsed_args.full_id:
            formatters = {
                'id': lambda x: x[:8]
            }
        return (
            columns,
            (utils.get_item_properties(c, columns, formatters=formatters)
             for c in clusters)
        )


class ShowCluster(show.ShowOne):
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
        'metadata': senlin_utils.json_formatter,
        'nodes': senlin_utils.list_formatter
    }
    columns = sorted(list(six.iterkeys(cluster)))
    return columns, utils.get_dict_properties(cluster.to_dict(), columns,
                                              formatters=formatters)


class CreateCluster(show.ShowOne):
    """Create the cluster."""

    log = logging.getLogger(__name__ + ".CreateCluster")

    def get_parser(self, prog_name):
        parser = super(CreateCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--profile',
            metavar='<profile>',
            required=True,
            help=_('Profile Id used for this cluster')
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
            metavar='<key1=value1;key2=value2...>',
            help=_('Metadata values to be attached to the cluster. '
                   'This can be specified multiple times, or once with '
                   'key-value pairs separated by a semicolon.'),
            action='append'
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


class UpdateCluster(show.ShowOne):
    """Update the cluster."""

    log = logging.getLogger(__name__ + ".UpdateCluster")

    def get_parser(self, prog_name):
        parser = super(UpdateCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--profile',
            metavar='<profile>',
            help=_('ID or name of new profile to use')
        )
        parser.add_argument(
            '--timeout',
            metavar='<timeout>',
            help=_('New timeout (in seconds) value for the cluster')
        )
        parser.add_argument(
            '--metadata',
            metavar='<key1=value1;key2=value2...>',
            help=_('Metadata values to be attached to the cluster. '
                   'This can be specified multiple times, or once with '
                   'key-value pairs separated by a semicolon'),
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
            'metadata': senlin_utils.format_parameters(parsed_args.metadata),
            'timeout': parsed_args.timeout,
        }

        senlin_client.update_cluster(cluster.id, **attrs)
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
            help=_('Name or ID of cluster(s) to delete')
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help=_('Skip yes/no prompt (assume yes)')
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
            self.log.info(_LI('Ctrl-c detected.'))
            return
        except EOFError:  # Ctrl-d
            self.log.info(_LI('Ctrl-d detected'))
            return

        failure_count = 0

        for cid in parsed_args.cluster:
            try:
                senlin_client.delete_cluster(cid, False)
            except Exception as ex:
                failure_count += 1
                print(ex)
        if failure_count:
            raise exc.CommandError(_('Failed to delete %(count)s of the '
                                     '%(total)s specified cluster(s).') %
                                   {'count': failure_count,
                                   'total': len(parsed_args.cluster)})
        print('Request accepted')


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

        if sum(v is not None for v in (capacity, adjustment, percentage)) > 1:
            raise exc.CommandError(_("Only one of 'capacity', 'adjustment' and"
                                     " 'percentage' can be specified."))

        if sum(v is None for v in (capacity, adjustment, percentage)) == 3:
            raise exc.CommandError(_("At least one of 'capacity', "
                                     "'adjustment' and 'percentage' "
                                     "should be specified."))

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

        if min_step is not None:
            if percentage is None:
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

        resp = senlin_client.cluster_resize(parsed_args.cluster, **action_args)
        print('Request accepted by action: %s' % resp['action'])


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

        resp = senlin_client.cluster_scale_in(parsed_args.cluster,
                                              parsed_args.count)
        print('Request accepted by action %s' % resp['action'])


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

        resp = senlin_client.cluster_scale_out(parsed_args.cluster,
                                               parsed_args.count)
        print('Request accepted by action %s' % resp['action'])


class ClusterPolicyAttach(command.Command):
    """Attach policy to cluster."""

    log = logging.getLogger(__name__ + ".ClusterPolicyAttach")

    def get_parser(self, prog_name):
        parser = super(ClusterPolicyAttach, self).get_parser(prog_name)
        parser.add_argument(
            '--policy',
            metavar='<policy>',
            required=True,
            help=_('ID or name of policy to be attached')
        )
        parser.add_argument(
            '--enabled',
            default=True,
            action="store_true",
            help=_('Whether the policy should be enabled once attached. '
                   'Default to True')
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
            'enabled': parsed_args.enabled,
        }

        resp = senlin_client.cluster_attach_policy(parsed_args.cluster,
                                                   parsed_args.policy,
                                                   **kwargs)
        print('Request accepted by action: %s' % resp['action'])


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
        resp = senlin_client.cluster_detach_policy(parsed_args.cluster,
                                                   parsed_args.policy)
        print('Request accepted by action: %s' % resp['action'])


class ClusterNodeList(lister.Lister):
    """List nodes from cluster."""

    log = logging.getLogger(__name__ + ".ClusterNodeList")

    def get_parser(self, prog_name):
        parser = super(ClusterNodeList, self).get_parser(prog_name)
        parser.add_argument(
            '--filters',
            metavar='<key1=value;key2=value2...>',
            help=_('Filter parameters to apply on returned nodes. '
                   'This can be specified multiple times, or once with '
                   'parameters separated by a semicolon'),
            action='append'
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_('Sorting option which is a string containing a list of '
                   'keys separated by commas. Each key can be optionally '
                   'appended by a sort direction (:asc or :desc)')
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
        resp = senlin_client.cluster_add_nodes(parsed_args.cluster, node_ids)
        print('Request accepted by action: %s' % resp['action'])


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
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to operate on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        node_ids = parsed_args.nodes.split(',')
        resp = senlin_client.cluster_del_nodes(parsed_args.cluster, node_ids)
        print('Request accepted by action: %s' % resp['action'])


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
            print('Cluster check request on cluster %(cid)s is accepted by '
                  'action %(action)s.'
                  % {'cid': cid, 'action': resp['action']})


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
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        for cid in parsed_args.cluster:
            try:
                resp = senlin_client.recover_cluster(cid)
            except sdk_exc.ResourceNotFound:
                raise exc.CommandError(_('Cluster not found: %s') % cid)
            print('Cluster recover request on cluster %(cid)s is accepted by '
                  'action %(action)s.'
                  % {'cid': cid, 'action': resp['action']})
