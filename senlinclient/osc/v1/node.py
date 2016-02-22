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

"""Clustering v1 node action implementations"""

import logging
import six

from cliff import lister
from cliff import show
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc
from openstackclient.common import utils

from senlinclient.common.i18n import _
from senlinclient.common import utils as senlin_utils


class ListNode(lister.Lister):
    """Show list of nodes."""

    log = logging.getLogger(__name__ + ".ListNode")

    def get_parser(self, prog_name):
        parser = super(ListNode, self).get_parser(prog_name)
        parser.add_argument(
            '--cluster',
            metavar='<cluster>',
            help=_('ID or name of cluster from which nodes are to be listed')
        )
        parser.add_argument(
            '--filters',
            metavar='<key1=value1;key2=value2...>',
            help=_("Filter parameters to apply on returned nodes. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter"
                   " keys are: ['status','name']"),
            action='append'
        )
        parser.add_argument(
            '--sort',
            metavar='<key:direction>',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc). The valid "
                   "sort keys are:'['index', 'name', 'status', 'init_at', "
                   "'created_at', 'updated_at']'")
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
            '--global-project',
            default=False, action="store_true",
            help=_('Indicate that this node list should include nodes from '
                   'all projects. This option is subject to access policy '
                   'checking. Default is False')
        )
        parser.add_argument(
            '--full-id',
            default=False, action="store_true",
            help=_('Print full IDs in list')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering

        columns = ['id', 'name', 'index', 'status', 'cluster_id',
                   'physical_id', 'profile_name', 'created_at', 'updated_at']
        queries = {
            'cluster_id': parsed_args.cluster,
            'sort': parsed_args.sort,
            'limit': parsed_args.limit,
            'marker': parsed_args.marker,
            'global_project': parsed_args.global_project,
        }

        if parsed_args.filters:
            queries.update(senlin_utils.format_parameters(parsed_args.filters))

        nodes = senlin_client.nodes(**queries)

        if not parsed_args.full_id:
            formatters = {
                'id': lambda x: x[:8],
                'cluster_id': lambda x: x[:8] if x else '',
                'physical_id': lambda x: x[:8] if x else ''
            }
        else:
            formatters = {}

        return (
            columns,
            (utils.get_item_properties(n, columns, formatters=formatters)
             for n in nodes)
        )


class ShowNode(show.ShowOne):
    """Show detailed info about the specified node."""

    log = logging.getLogger(__name__ + ".ShowNode")

    def get_parser(self, prog_name):
        parser = super(ShowNode, self).get_parser(prog_name)
        parser.add_argument(
            '--details',
            default=False,
            action="store_true",
            help=_('Include physical object details')
        )
        parser.add_argument(
            'node',
            metavar='<node>',
            help=_('Name or ID of the node to show the details for')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        return _show_node(senlin_client, parsed_args.node, parsed_args.details)


def _show_node(senlin_client, node_id, show_details=False):
    """Show detailed info about the specified node."""

    args = {'show_details': True} if show_details else None
    try:
        node = senlin_client.get_node(node_id, args=args)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Node not found: %s') % node_id)

    formatters = {
        'metadata': senlin_utils.json_formatter,
        'data': senlin_utils.json_formatter,
    }
    if show_details and node:
        formatters['details'] = senlin_utils.nested_dict_formatter(
            list(node['details'].keys()), ['property', 'value'])

    columns = list(six.iterkeys(node))
    return columns, utils.get_dict_properties(node.to_dict(), columns,
                                              formatters=formatters)
