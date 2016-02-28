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

from cliff import lister
from cliff import show
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc
from openstackclient.common import utils

from senlinclient.common.i18n import _
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
