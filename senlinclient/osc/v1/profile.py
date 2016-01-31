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

from cliff import show
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc
from openstackclient.common import utils

from senlinclient.common import utils as senlin_utils


class ShowProfile(show.ShowOne):
    """Show profile details."""

    log = logging.getLogger(__name__ + ".ShowProfile")

    def get_parser(self, prog_name):
        parser = super(ShowProfile, self).get_parser(prog_name)
        parser.add_argument(
            'profile',
            metavar='<PROFILE>',
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

        columns = [
            'created_at',
            'domain',
            'id',
            'metadata',
            'name',
            'permission',
            'project',
            'spec',
            'type',
            'updated_at',
            'user'
        ]
        return columns, utils.get_dict_properties(data.to_dict(), columns,
                                                  formatters=formatters)
