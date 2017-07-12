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

"""Clustering v1 profile action implementations"""

import logging
import sys

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions as exc
from osc_lib import utils

from senlinclient.common.i18n import _
from senlinclient.common import utils as senlin_utils


class ShowProfile(command.ShowOne):
    """Show profile details."""

    log = logging.getLogger(__name__ + ".ShowProfile")

    def get_parser(self, prog_name):
        parser = super(ShowProfile, self).get_parser(prog_name)
        parser.add_argument(
            'profile',
            metavar='<profile>',
            help='Name or ID of profile to show',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        senlin_client = self.app.client_manager.clustering
        return _show_profile(senlin_client, profile_id=parsed_args.profile)


def _show_profile(senlin_client, profile_id):
    try:
        data = senlin_client.get_profile(profile_id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError('Profile not found: %s' % profile_id)
    else:
        formatters = {}
        formatters['metadata'] = senlin_utils.json_formatter
        formatters['spec'] = senlin_utils.nested_dict_formatter(
            ['type', 'version', 'properties'],
            ['property', 'value'])

        data = data.to_dict()
        columns = sorted(data.keys())
        return columns, utils.get_dict_properties(data, columns,
                                                  formatters=formatters)


class ListProfile(command.Lister):
    """List profiles that meet the criteria."""

    log = logging.getLogger(__name__ + ".ListProfile")

    def get_parser(self, prog_name):
        parser = super(ListProfile, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            help=_('Limit the number of profiles returned')
        )
        parser.add_argument(
            '--marker',
            metavar='<id>',
            help=_('Only return profiles that appear after the given profile '
                   'ID')
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of keys"
                   " separated by commas. Each key can be optionally appended "
                   "by a sort direction (:asc or :desc). The valid sort_keys "
                   "are:['type', 'name', 'created_at', 'updated_at']")
        )
        parser.add_argument(
            '--filters',
            metavar='<"key1=value1;key2=value2...">',
            help=_("Filter parameters to apply on returned profiles. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['type', 'name']"),
            action='append'
        )
        parser.add_argument(
            '--global-project',
            default=False,
            action="store_true",
            help=_('Indicate that the list should include profiles from'
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
        data = senlin_client.profiles(**queries)

        formatters = {}
        if parsed_args.global_project:
            columns.append('project_id')
        if not parsed_args.full_id:
            formatters = {
                'id': lambda x: x[:8],
            }
            if 'project_id' in columns:
                formatters['project_id'] = lambda x: x[:8]

        return (
            columns,
            (utils.get_item_properties(p, columns, formatters=formatters)
             for p in data)
        )


class DeleteProfile(command.Command):
    """Delete profile(s)."""

    log = logging.getLogger(__name__ + ".DeleteProfile")

    def get_parser(self, prog_name):
        parser = super(DeleteProfile, self).get_parser(prog_name)
        parser.add_argument(
            'profile',
            metavar='<profile>',
            nargs='+',
            help=_('Name or ID of profile(s) to delete')
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
                    _("Are you sure you want to delete this profile(s)"
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
        for pid in parsed_args.profile:
            try:
                senlin_client.delete_profile(pid, False)
            except Exception as ex:
                failure_count += 1
                print(ex)
        if failure_count:
            raise exc.CommandError(_('Failed to delete %(count)s of the '
                                     '%(total)s specified profile(s).') %
                                   {'count': failure_count,
                                   'total': len(parsed_args.profile)})
        print('Profile deleted: %s' % parsed_args.profile)


class CreateProfile(command.ShowOne):
    """Create a profile."""

    log = logging.getLogger(__name__ + ".CreateProfile")

    def get_parser(self, prog_name):
        parser = super(CreateProfile, self).get_parser(prog_name)
        parser.add_argument(
            '--metadata',
            metavar='<"key1=value1;key2=value2...">',
            help=_('Metadata values to be attached to the profile. '
                   'This can be specified multiple times, or once with '
                   'key-value pairs separated by a semicolon'),
            action='append'
        )
        parser.add_argument(
            '--spec-file',
            metavar='<spec-file>',
            required=True,
            help=_('The spec file used to create the profile')
        )
        parser.add_argument(
            'name',
            metavar='<profile-name>',
            help=_('Name of the profile to create')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        spec = senlin_utils.get_spec_content(parsed_args.spec_file)
        type_name = spec.get('type', None)
        type_version = spec.get('version', None)
        properties = spec.get('properties', None)
        if type_name is None:
            raise exc.CommandError(_("Missing 'type' key in spec file."))
        if type_version is None:
            raise exc.CommandError(_("Missing 'version' key in spec file."))
        if properties is None:
            raise exc.CommandError(_("Missing 'properties' key in spec file."))

        if type_name == 'os.heat.stack':
            stack_properties = senlin_utils.process_stack_spec(properties)
            spec['properties'] = stack_properties

        params = {
            'name': parsed_args.name,
            'spec': spec,
            'metadata': senlin_utils.format_parameters(parsed_args.metadata),
        }

        profile = senlin_client.create_profile(**params)
        return _show_profile(senlin_client, profile_id=profile.id)


class UpdateProfile(command.ShowOne):
    """Update a profile."""

    log = logging.getLogger(__name__ + ".UpdateProfile")

    def get_parser(self, prog_name):
        parser = super(UpdateProfile, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('The new name for the profile')
        )
        parser.add_argument(
            '--metadata',
            metavar='<"key1=value1;key2=value2...">',
            help=_("Metadata values to be attached to the profile. "
                   "This can be specified multiple times, or once with "
                   "key-value pairs separated by a semicolon. Use '{}' "
                   "can clean metadata "),
            action='append'
        )
        parser.add_argument(
            'profile',
            metavar='<profile>',
            help=_('Name or ID of the profile to update')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        params = {
            'name': parsed_args.name,
        }
        if parsed_args.metadata:
            params['metadata'] = senlin_utils.format_parameters(
                parsed_args.metadata)

        # Find the profile first, we need its id
        profile = senlin_client.find_profile(parsed_args.profile)
        if profile is None:
            raise exc.CommandError(_('Profile not found: %s') %
                                   parsed_args.profile)
        senlin_client.update_profile(profile.id, **params)
        return _show_profile(senlin_client, profile_id=profile.id)


class ValidateProfile(command.ShowOne):
    """Validate a profile."""

    log = logging.getLogger(__name__ + ".ValidateProfile")

    def get_parser(self, prog_name):
        parser = super(ValidateProfile, self).get_parser(prog_name)
        parser.add_argument(
            '--spec-file',
            metavar='<spec-file>',
            required=True,
            help=_('The spec file of the profile to be validated')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        spec = senlin_utils.get_spec_content(parsed_args.spec_file)
        type_name = spec.get('type', None)
        type_version = spec.get('version', None)
        properties = spec.get('properties', None)
        if type_name is None:
            raise exc.CommandError(_("Missing 'type' key in spec file."))
        if type_version is None:
            raise exc.CommandError(_("Missing 'version' key in spec file."))
        if properties is None:
            raise exc.CommandError(_("Missing 'properties' key in spec file."))

        if type_name == 'os.heat.stack':
            stack_properties = senlin_utils.process_stack_spec(properties)
            spec['properties'] = stack_properties

        params = {
            'spec': spec,
        }

        profile = senlin_client.validate_profile(**params)

        formatters = {}
        formatters['metadata'] = senlin_utils.json_formatter
        formatters['spec'] = senlin_utils.nested_dict_formatter(
            ['type', 'version', 'properties'],
            ['property', 'value'])

        columns = [
            'created_at',
            'domain',
            'id',
            'metadata',
            'name',
            'project_id',
            'spec',
            'type',
            'updated_at',
            'user_id'
        ]
        return columns, utils.get_dict_properties(profile.to_dict(), columns,
                                                  formatters=formatters)
