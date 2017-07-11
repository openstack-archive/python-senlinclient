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
import sys

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions as exc
from osc_lib import utils

from senlinclient.common.i18n import _
from senlinclient.common import utils as senlin_utils


class ListPolicy(command.Lister):
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
            help=_('Only return policies that appear after the given policy '
                   'ID')
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc). The valid "
                   "sort keys are: ['type', 'name', 'created_at', "
                   "'updated_at']")
        )
        parser.add_argument(
            '--filters',
            metavar='<"key1=value1;key2=value2...">',
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
        if parsed_args.global_project:
            columns.append('project_id')
        if not parsed_args.full_id:
            formatters = {
                'id': lambda x: x[:8]
            }
            if 'project_id' in columns:
                formatters['project_id'] = lambda x: x[:8]

        return (
            columns,
            (utils.get_item_properties(p, columns, formatters=formatters)
             for p in policies)
        )


class ShowPolicy(command.ShowOne):
    """Show the policy details."""

    log = logging.getLogger(__name__ + ".ShowPolicy")

    def get_parser(self, prog_name):
        parser = super(ShowPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            help=_('Name or Id of the policy to show')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        return _show_policy(senlin_client, policy_id=parsed_args.policy)


def _show_policy(senlin_client, policy_id):
    try:
        policy = senlin_client.get_policy(policy_id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Policy not found: %s') % policy_id)

    formatters = {
        'spec': senlin_utils.json_formatter
    }

    data = policy.to_dict()
    columns = sorted(data.keys())
    return columns, utils.get_dict_properties(data, columns,
                                              formatters=formatters)


class CreatePolicy(command.ShowOne):
    """Create a policy."""

    log = logging.getLogger(__name__ + ".CreatePolicy")

    def get_parser(self, prog_name):
        parser = super(CreatePolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--spec-file',
            metavar='<spec-file>',
            required=True,
            help=_('The spec file used to create the policy')
        )
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the policy to create')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        spec = senlin_utils.get_spec_content(parsed_args.spec_file)
        attrs = {
            'name': parsed_args.name,
            'spec': spec,
        }

        policy = senlin_client.create_policy(**attrs)
        return _show_policy(senlin_client, policy.id)


class UpdatePolicy(command.ShowOne):
    """Update a policy."""

    log = logging.getLogger(__name__ + ".UpdatePolicy")

    def get_parser(self, prog_name):
        parser = super(UpdatePolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New name of the policy to be updated')
        )
        parser.add_argument(
            'policy',
            metavar='<policy>',
            help=_('Name or ID of the policy to be updated')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        params = {
            'name': parsed_args.name,
        }
        policy = senlin_client.find_policy(parsed_args.policy)
        if policy is None:
            raise exc.CommandError(_('Policy not found: %s') %
                                   parsed_args.policy)
        senlin_client.update_policy(policy.id, **params)
        return _show_policy(senlin_client, policy_id=policy.id)


class DeletePolicy(command.Command):
    """Delete policy(s)."""

    log = logging.getLogger(__name__ + ".DeletePolicy")

    def get_parser(self, prog_name):
        parser = super(DeletePolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            nargs='+',
            help=_('Name or ID of policy(s) to delete')
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
                    _("Are you sure you want to delete this policy(s)"
                      " [y/N]?"))
                prompt_response = sys.stdin.readline().lower()
                if not prompt_response.startswith('y'):
                    return
        except KeyboardInterrupt:  # Ctrl-c
            self.log.info('Ctrl-c detected.')
            return
        except EOFError:  # Ctrl-d
            self.log.info('Ctrl-d detected')
            return

        failure_count = 0

        for pid in parsed_args.policy:
            try:
                senlin_client.delete_policy(pid, False)
            except Exception as ex:
                failure_count += 1
                print(ex)
        if failure_count:
            raise exc.CommandError(_('Failed to delete %(count)s of the '
                                     '%(total)s specified policy(s).') %
                                   {'count': failure_count,
                                   'total': len(parsed_args.policy)})
        print('Policy deleted: %s' % parsed_args.policy)


class ValidatePolicy(command.ShowOne):
    """Validate a policy."""

    log = logging.getLogger(__name__ + ".ValidatePolicy")

    def get_parser(self, prog_name):
        parser = super(ValidatePolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--spec-file',
            metavar='<spec-file>',
            required=True,
            help=_('The spec file of the policy to be validated')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        spec = senlin_utils.get_spec_content(parsed_args.spec_file)
        attrs = {
            'spec': spec,
        }

        policy = senlin_client.validate_policy(**attrs)
        formatters = {
            'spec': senlin_utils.json_formatter
        }
        columns = [
            'created_at',
            'data',
            'domain',
            'id',
            'name',
            'project',
            'spec',
            'type',
            'updated_at',
            'user'
        ]
        return columns, utils.get_dict_properties(policy.to_dict(), columns,
                                                  formatters=formatters)
