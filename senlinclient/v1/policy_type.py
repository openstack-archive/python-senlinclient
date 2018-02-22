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

"""Clustering v1 policy type action implementations"""

import logging

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions as exc

from senlinclient.common import format_utils
from senlinclient.common.i18n import _


class PolicyTypeList(command.Lister):
    """List the available policy types."""

    log = logging.getLogger(__name__ + ".PolicyTypeList")

    def get_parser(self, prog_name):
        parser = super(PolicyTypeList, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        types = senlin_client.policy_types()
        columns = ['name', 'version', 'support_status']
        results = []
        for t in types:
            if t.support_status:
                for v in t.support_status.keys():
                    st_list = '\n'.join([
                        ' since '.join((item['status'], item['since']))
                        for item in t.support_status[v]
                    ])

                    results.append((t.name, v, st_list))
            else:
                columns = ['name', 'version']
                results.append((t.name.split('-')[0], t.name.split('-')[1]))

        return columns, sorted(results)


class PolicyTypeShow(format_utils.YamlFormat):
    """Get the details about a policy type."""

    log = logging.getLogger(__name__ + ".PolicyTypeShow")

    def get_parser(self, prog_name):
        parser = super(PolicyTypeShow, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<type-name>',
            help=_('Policy type to retrieve')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        try:
            res = senlin_client.get_policy_type(parsed_args.type_name)
        except sdk_exc.ResourceNotFound:
            raise exc.CommandError(_('Policy Type not found: %s')
                                   % parsed_args.type_name)
        data = res.to_dict()
        rows = data.values()
        columns = data.keys()
        return columns, rows
