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
            metavar='<key:dir>',
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
    columns = list(six.iterkeys(cluster))
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
            metavar='<cluster_name>',
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
        cluster = senlin_client.get_cluster(parsed_args.cluster)
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
