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

"""Clustering v1 event action implementations"""

import logging

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions as exc
from osc_lib import utils

from senlinclient.common.i18n import _
from senlinclient.common import utils as senlin_utils


class ListEvent(command.Lister):
    """List events."""

    log = logging.getLogger(__name__ + ".ListEvent")

    def get_parser(self, prog_name):
        parser = super(ListEvent, self).get_parser(prog_name)
        parser.add_argument(
            '--filters',
            metavar='<"key1=value1;key2=value2...">',
            help=_("Filter parameters to apply on returned events. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['level', 'otype', 'oid' ,'cluster_id', "
                   "'oname', 'action']. "
                   "NOTICE: The value of 'oid' or 'cluster_id', "
                   "if provided, must be a full ID."),
            action='append'
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of events returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return events that appear after the given event ID')
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc). The valid "
                   "sort keys are: ['timestamp', 'level', 'oid', 'otype', "
                   "'oname', 'action', 'status']")
        )
        parser.add_argument(
            '--global-project',
            default=False,
            action="store_true",
            help=_('Whether events from all projects should be listed. '
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
        columns = ['id', 'generated_at', 'obj_type', 'obj_id', 'obj_name',
                   'action', 'status', 'level', 'cluster_id']
        queries = {
            'sort': parsed_args.sort,
            'limit': parsed_args.limit,
            'marker': parsed_args.marker,
            'global_project': parsed_args.global_project,
        }

        if parsed_args.filters:
            queries.update(senlin_utils.format_parameters(parsed_args.filters))

        formatters = {}
        if parsed_args.global_project:
            columns.append('project_id')
        if not parsed_args.full_id:
            formatters['id'] = lambda x: x[:8]
            formatters['obj_id'] = lambda x: x[:8] if x else ''
            if 'project_id' in columns:
                formatters['project_id'] = lambda x: x[:8]
            formatters['cluster_id'] = lambda x: x[:8] if x else ''

        events = senlin_client.events(**queries)
        return (columns,
                (utils.get_item_properties(e, columns,
                                           formatters=formatters)
                 for e in events))


class ShowEvent(command.ShowOne):
    """Show the event details."""

    log = logging.getLogger(__name__ + ".ShowEvent")

    def get_parser(self, prog_name):
        parser = super(ShowEvent, self).get_parser(prog_name)
        parser.add_argument(
            'event',
            metavar='<event>',
            help=_('ID of event to display details for')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        try:
            event = senlin_client.get_event(parsed_args.event)
        except sdk_exc.ResourceNotFound:
            raise exc.CommandError(_("Event not found: %s")
                                   % parsed_args.event)
        data = event.to_dict()
        columns = sorted(data.keys())
        return columns, utils.get_dict_properties(data, columns)
