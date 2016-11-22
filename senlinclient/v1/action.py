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

"""Clustering v1 action implementations"""

import logging

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions as exc
from osc_lib import utils

from senlinclient.common.i18n import _
from senlinclient.common import utils as senlin_utils


class ListAction(command.Lister):
    """List actions."""

    log = logging.getLogger(__name__ + ".ListAction")

    def get_parser(self, prog_name):
        parser = super(ListAction, self).get_parser(prog_name)
        parser.add_argument(
            '--filters',
            metavar='<"key1=value1;key2=value2...">',
            help=_("Filter parameters to apply on returned actions. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['name', 'target', 'action', 'status']. "
                   "NOTICE: The value of 'target', if provided, "
                   "must be a full ID."),
            action='append'
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc). The valid "
                   "sort keys are: ['name', 'target', 'action', 'created_at',"
                   " 'status']")
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of actions returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return actions that appear after the given action ID')
        )
        parser.add_argument(
            '--global-project',
            default=False,
            action="store_true",
            help=_('Whether actions from all projects should be listed. '
                   ' Default to False. Setting this to True may demand '
                   'for an admin privilege')
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

        columns = ['id', 'name', 'action', 'status', 'target_id', 'depends_on',
                   'depended_by', 'created_at']

        queries = {
            'sort': parsed_args.sort,
            'limit': parsed_args.limit,
            'marker': parsed_args.marker,
            'global_project': parsed_args.global_project,
        }

        if parsed_args.filters:
            queries.update(senlin_utils.format_parameters(parsed_args.filters))

        actions = senlin_client.actions(**queries)

        formatters = {}
        s = None
        if not parsed_args.full_id:
            s = 8
            formatters['id'] = lambda x: x[:s]
            formatters['target_id'] = lambda x: x[:s]

        formatters['depends_on'] = lambda x: '\n'.join(a[:s] for a in x)
        formatters['depended_by'] = lambda x: '\n'.join(a[:s] for a in x)

        return (
            columns,
            (utils.get_item_properties(a, columns,
                                       formatters=formatters)
             for a in actions)
        )


class ShowAction(command.ShowOne):
    """Show detailed info about the specified action."""

    log = logging.getLogger(__name__ + ".ShowAction")

    def get_parser(self, prog_name):
        parser = super(ShowAction, self).get_parser(prog_name)
        parser.add_argument(
            'action',
            metavar='<action>',
            help=_('Name or ID of the action to show the details for')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        try:
            action = senlin_client.get_action(parsed_args.action)
        except sdk_exc.ResourceNotFound:
            raise exc.CommandError(_('Action not found: %s')
                                   % parsed_args.action)

        formatters = {
            'inputs': senlin_utils.json_formatter,
            'outputs': senlin_utils.json_formatter,
            'metadata': senlin_utils.json_formatter,
            'data': senlin_utils.json_formatter,
            'depends_on': senlin_utils.list_formatter,
            'depended_by': senlin_utils.list_formatter,
        }
        data = action.to_dict()
        columns = sorted(data.keys())
        return columns, utils.get_dict_properties(data, columns,
                                                  formatters=formatters)
