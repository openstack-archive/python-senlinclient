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

"""Clustering v1 profile type action implementations"""

import logging
import six

from cliff import lister
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc
from senlinclient.common import format_utils
from senlinclient.common.i18n import _


class ProfileTypeList(lister.Lister):
    """List the available profile types."""

    log = logging.getLogger(__name__ + ".ProfileTypeList")

    def get_parser(self, prog_name):
        parser = super(ProfileTypeList, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        types = senlin_client.profile_types()
        columns = ['name']
        rows = sorted([t.name] for t in types)
        return columns, rows


class ProfileTypeShow(format_utils.YamlFormat):
    """Show the details about a profile type."""

    log = logging.getLogger(__name__ + ".ProfileTypeShow")

    def get_parser(self, prog_name):
        parser = super(ProfileTypeShow, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<type-name>',
            help=_('Profile type to retrieve')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        try:
            res = senlin_client.get_profile_type(parsed_args.type_name)
        except sdk_exc.ResourceNotFound:
            raise exc.CommandError(_('Profile Type not found: %s')
                                   % parsed_args.type_name)
        rows = list(six.itervalues(res))
        columns = list(six.iterkeys(res))
        return columns, rows
