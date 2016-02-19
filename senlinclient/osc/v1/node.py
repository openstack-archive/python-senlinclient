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

from cliff import lister
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
