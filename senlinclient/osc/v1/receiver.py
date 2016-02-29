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

"""Clustering v1 receiver action implementations"""

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


class ListReceiver(lister.Lister):
    """List receivers that meet the criteria."""

    log = logging.getLogger(__name__ + ".ListReceiver")

    def get_parser(self, prog_name):
        parser = super(ListReceiver, self).get_parser(prog_name)
        parser.add_argument(
            '--filters',
            metavar='<key1=value1;key2=value2...>',
            help=_("Filter parameters to apply on returned receivers. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['name', 'type', 'action', 'cluster_id']"),
            action='append'
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of receivers returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return receivers that appear after the given ID')
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc). The valid "
                   "sort keys are: ['name', 'type', 'action', 'cluster_id', "
                   "'created_at']")
        )
        parser.add_argument(
            '--global-project',
            default=False,
            action="store_true",
            help=_('Indicate that the list should include receivers from'
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

        columns = ['id', 'name', 'type', 'cluster_id', 'action', 'created_at']
        queries = {
            'limit': parsed_args.limit,
            'marker': parsed_args.marker,
            'sort': parsed_args.sort,
            'global_project': parsed_args.global_project,
        }

        if parsed_args.filters:
            queries.update(senlin_utils.format_parameters(parsed_args.filters))

        receivers = senlin_client.receivers(**queries)
        formatters = {}
        if not parsed_args.full_id:
            formatters = {
                'id': lambda x: x[:8],
                'cluster_id': lambda x: x[:8],
            }

        return (
            columns,
            (utils.get_item_properties(r, columns, formatters=formatters)
             for r in receivers)
        )


class ShowReceiver(show.ShowOne):
    """Show the receiver details."""

    log = logging.getLogger(__name__ + ".ShowReceiver")

    def get_parser(self, prog_name):
        parser = super(ShowReceiver, self).get_parser(prog_name)
        parser.add_argument(
            'receiver',
            metavar='<receiver>',
            help=_('Name or ID of the receiver to show')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        return _show_receiver(senlin_client, parsed_args.receiver)


def _show_receiver(senlin_client, receiver_id):
    try:
        receiver = senlin_client.get_receiver(receiver_id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Receiver not found: %s') % receiver_id)

    formatters = {
        'actor': senlin_utils.json_formatter,
        'params': senlin_utils.json_formatter,
        'channel': senlin_utils.json_formatter,
    }
    columns = sorted(list(six.iterkeys(receiver)))
    return columns, utils.get_dict_properties(receiver.to_dict(), columns,
                                              formatters=formatters)


class CreateReceiver(show.ShowOne):
    """Create a receiver."""

    log = logging.getLogger(__name__ + ".CreateReceiver")

    def get_parser(self, prog_name):
        parser = super(CreateReceiver, self).get_parser(prog_name)
        parser.add_argument(
            '--type',
            metavar='<type>',
            default='webhook',
            help=_('Type of the receiver to create')
        )
        parser.add_argument(
            '--cluster',
            metavar='<cluster>',
            required=True,
            help=_('Targeted cluster for this receiver')
        )
        parser.add_argument(
            '--action',
            metavar='<action>',
            required=True,
            help=_('Name or ID of the targeted action to be triggered')
        )
        parser.add_argument(
            '--params',
            metavar='<key1=value1;key2=value2...>',
            help=_('A dictionary of parameters that will be passed to target '
                   'action when the receiver is triggered'),
            action='append'
        )
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the receiver to create')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        params = {
            'name': parsed_args.name,
            'type': parsed_args.type,
            'cluster_id': parsed_args.cluster,
            'action': parsed_args.action,
            'params': senlin_utils.format_parameters(parsed_args.params)
        }

        receiver = senlin_client.create_receiver(**params)
        return _show_receiver(senlin_client, receiver.id)


class DeleteReceiver(command.Command):
    """Delete receiver(s)."""

    log = logging.getLogger(__name__ + ".DeleteReceiver")

    def get_parser(self, prog_name):
        parser = super(DeleteReceiver, self).get_parser(prog_name)
        parser.add_argument(
            'receiver',
            metavar='<receiver>',
            nargs='+',
            help=_('Name or ID of receiver(s) to delete')
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
                    _("Are you sure you want to delete this receiver(s)"
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

        for rid in parsed_args.receiver:
            try:
                senlin_client.delete_receiver(rid, False)
            except Exception as ex:
                failure_count += 1
                print(ex)
        if failure_count:
            raise exc.CommandError(_('Failed to delete %(count)s of the '
                                     '%(total)s specified receiver(s).') %
                                   {'count': failure_count,
                                   'total': len(parsed_args.receiver)})
        print('Receiver deleted: %s' % parsed_args.receiver)
