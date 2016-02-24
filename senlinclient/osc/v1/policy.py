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

"""Clustering v1 policy action implementations"""

import logging

from cliff import lister
from openstackclient.common import utils

from senlinclient.common.i18n import _
from senlinclient.common import utils as senlin_utils


class ListPolicy(lister.Lister):
    """List policies that meet the criteria."""

    log = logging.getLogger(__name__ + ".ListPolicy")

    def get_parser(self, prog_name):
        parser = super(ListPolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of policies returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return policies that appear after the given ID')
        )
        parser.add_argument(
            '--sort',
            metavar='<key:dir>',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc). The valid "
                   "sort keys are: ['type', 'name', 'created_at', "
                   "'updated_at']")
        )
        parser.add_argument(
            '--filters',
            metavar='<key1=value1;key2=value2...>',
            help=_("Filter parameters to apply on returned policies. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['type', 'name']"),
            action='append'
        )
        parser.add_argument(
            '--global-project',
            default=False,
            action="store_true",
            help=_('Indicate that the list should include policies from'
                   ' all projects. This option is subject to access policy '
                   'checking. Default is False')
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
        columns = ['id', 'name', 'type', 'created_at']
        queries = {
            'limit': parsed_args.limit,
            'marker': parsed_args.marker,
            'sort': parsed_args.sort,
            'global_project': parsed_args.global_project,
        }
        if parsed_args.filters:
            queries.update(senlin_utils.format_parameters(parsed_args.filters))

        policies = senlin_client.policies(**queries)
        formatters = {}
        if not parsed_args.full_id:
            formatters = {
                'id': lambda x: x[:8]
            }
        return (
            columns,
            (utils.get_item_properties(p, columns, formatters=formatters)
             for p in policies)
        )
