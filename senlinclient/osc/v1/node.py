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
            metavar='<key>[:<direction>]',
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

    columns = sorted(list(six.iterkeys(node)))
    return columns, utils.get_dict_properties(node.to_dict(), columns,
                                              formatters=formatters)


class CreateNode(show.ShowOne):
    """Create the node."""

    log = logging.getLogger(__name__ + ".CreateNode")

    def get_parser(self, prog_name):
        parser = super(CreateNode, self).get_parser(prog_name)
        parser.add_argument(
            '--profile',
            metavar='<profile>',
            required=True,
            help=_('Profile Id or Name used for this node')
        )
        parser.add_argument(
            '--cluster',
            metavar='<cluster>',
            help=_('Cluster Id or Name for this node')
        )
        parser.add_argument(
            '--role',
            metavar='<role>',
            help=_('Role for this node in the specific cluster')
        )
        parser.add_argument(
            '--metadata',
            metavar='<key1=value1;key2=value2...>',
            help=_('Metadata values to be attached to the node. '
                   'This can be specified multiple times, or once with '
                   'key-value pairs separated by a semicolon'),
            action='append'
        )
        parser.add_argument(
            'name',
            metavar='<node-name>',
            help=_('Name of the node to create')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        attrs = {
            'name': parsed_args.name,
            'cluster_id': parsed_args.cluster,
            'profile_id': parsed_args.profile,
            'role': parsed_args.role,
            'metadata': senlin_utils.format_parameters(parsed_args.metadata),
        }

        node = senlin_client.create_node(**attrs)
        return _show_node(senlin_client, node.id)


class UpdateNode(show.ShowOne):
    """Update the node."""

    log = logging.getLogger(__name__ + ".UpdateNode")

    def get_parser(self, prog_name):
        parser = super(UpdateNode, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New name for the node')
        )
        parser.add_argument(
            '--profile',
            metavar='<profile-id>',
            help=_('ID of new profile to use')
        )
        parser.add_argument(
            '--role',
            metavar='<role>',
            help=_('Role for this node in the specific cluster')
        )
        parser.add_argument(
            '--metadata',
            metavar='<key1=value1;key2=value2...>',
            help=_('Metadata values to be attached to the node. '
                   'Metadata can be specified multiple times, or once with '
                   'key-value pairs separated by a semicolon'),
            action='append'
        )
        parser.add_argument(
            'node',
            metavar='<node>',
            help=_('Name or ID of node to update')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering

        # Find the node first, we need its UUID
        node = senlin_client.find_node(parsed_args.node)
        if node is None:
            raise exc.CommandError(_('Node not found: %s') % parsed_args.node)

        attrs = {
            'name': parsed_args.name,
            'role': parsed_args.role,
            'profile_id': parsed_args.profile,
            'metadata': senlin_utils.format_parameters(parsed_args.metadata),
        }

        senlin_client.update_node(node.id, **attrs)
        return _show_node(senlin_client, node.id)


class DeleteNode(command.Command):
    """Delete the node(s)."""

    log = logging.getLogger(__name__ + ".DeleteNode")

    def get_parser(self, prog_name):
        parser = super(DeleteNode, self).get_parser(prog_name)
        parser.add_argument(
            'node',
            metavar='<node>',
            nargs='+',
            help=_('Name or ID of node(s) to delete')
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
                    _("Are you sure you want to delete this node(s)"
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

        for nid in parsed_args.node:
            try:
                senlin_client.delete_node(nid, False)
            except Exception as ex:
                failure_count += 1
                print(ex)
        if failure_count:
            raise exc.CommandError(_('Failed to delete %(count)s of the '
                                     '%(total)s specified node(s).') %
                                   {'count': failure_count,
                                   'total': len(parsed_args.node)})
        print('Request accepted')


class CheckNode(command.Command):
    """Check the node(s)."""
    log = logging.getLogger(__name__ + ".CheckNode")

    def get_parser(self, prog_name):
        parser = super(CheckNode, self).get_parser(prog_name)
        parser.add_argument(
            'node',
            metavar='<node>',
            nargs='+',
            help=_('ID or name of node(s) to check.')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        for nid in parsed_args.node:
            try:
                resp = senlin_client.check_node(nid)
            except sdk_exc.ResourceNotFound:
                raise exc.CommandError(_('Node not found: %s') % nid)
            print('Node check request on node %(nid)s is accepted by '
                  'action %(action)s.'
                  % {'nid': nid, 'action': resp['action']})


class RecoverNode(command.Command):
    """Recover the node(s)."""
    log = logging.getLogger(__name__ + ".RecoverNode")

    def get_parser(self, prog_name):
        parser = super(RecoverNode, self).get_parser(prog_name)
        parser.add_argument(
            'node',
            metavar='<node>',
            nargs='+',
            help=_('ID or name of node(s) to recover.')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        for nid in parsed_args.node:
            try:
                resp = senlin_client.recover_node(nid)
            except sdk_exc.ResourceNotFound:
                raise exc.CommandError(_('Node not found: %s') % nid)
            print('Node recover request on node %(nid)s is accepted by '
                  'action %(action)s.'
                  % {'nid': nid, 'action': resp['action']})
