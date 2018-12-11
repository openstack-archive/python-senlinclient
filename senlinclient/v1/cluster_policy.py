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

"""Clustering v1 cluster policy action implementations"""

import logging

from osc_lib.command import command
from osc_lib import utils
from oslo_utils import strutils

from senlinclient.common.i18n import _
from senlinclient.common import utils as senlin_utils


class ClusterPolicyList(command.Lister):
    """List policies from cluster."""

    log = logging.getLogger(__name__ + ".ClusterPolicyList")

    def get_parser(self, prog_name):
        parser = super(ClusterPolicyList, self).get_parser(prog_name)
        parser.add_argument(
            '--filters',
            metavar='<"key1=value1;key2=value2...">',
            help=_("Filter parameters to apply on returned results. "
                   "This can be specified multiple times, or once with "
                   "parameters separated by a semicolon. The valid filter "
                   "keys are: ['is_enabled', 'policy_type', 'policy_name']"),
            action='append'
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            help=_("Sorting option which is a string containing a list of "
                   "keys separated by commas. Each key can be optionally "
                   "appended by a sort direction (:asc or :desc).  The valid "
                   "sort keys are: ['enabled']")
        )
        parser.add_argument(
            '--full-id',
            default=False,
            action="store_true",
            help=_('Print full IDs in list')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to query on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering

        columns = ['policy_id', 'policy_name', 'policy_type', 'is_enabled']
        cluster = senlin_client.get_cluster(parsed_args.cluster)
        queries = {
            'sort': parsed_args.sort,
        }

        if parsed_args.filters:
            queries.update(senlin_utils.format_parameters(parsed_args.filters))

        policies = senlin_client.cluster_policies(cluster.id, **queries)
        formatters = {}
        if not parsed_args.full_id:
            formatters = {
                'policy_id': lambda x: x[:8]
            }
        return (
            columns,
            (utils.get_item_properties(p, columns,
                                       formatters=formatters)
             for p in policies)
        )


class ClusterPolicyShow(command.ShowOne):
    """Show a specific policy that is bound to the specified cluster."""

    log = logging.getLogger(__name__ + ".ClusterPolicyShow")

    def get_parser(self, prog_name):
        parser = super(ClusterPolicyShow, self).get_parser(prog_name)
        parser.add_argument(
            '--policy',
            metavar='<policy>',
            required=True,
            help=_('ID or name of the policy to query on')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('ID or name of the cluster to query on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        policy = senlin_client.get_cluster_policy(parsed_args.policy,
                                                  parsed_args.cluster)
        data = policy.to_dict()
        columns = sorted(data.keys())
        return columns, utils.get_dict_properties(data, columns)


class ClusterPolicyUpdate(command.Command):
    """Update a policy's properties on a cluster."""

    log = logging.getLogger(__name__ + ".ClusterPolicyUpdate")

    def get_parser(self, prog_name):
        parser = super(ClusterPolicyUpdate, self).get_parser(prog_name)
        parser.add_argument(
            '--policy',
            metavar='<policy>',
            required=True,
            help=_('ID or name of policy to be updated')
        )
        parser.add_argument(
            '--enabled',
            metavar='<boolean>',
            required=True,
            help=_('Whether the policy should be enabled')
        )
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name or ID of cluster to operate on')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        kwargs = {
            'enabled': strutils.bool_from_string(parsed_args.enabled,
                                                 strict=True),
        }

        resp = senlin_client.update_cluster_policy(parsed_args.cluster,
                                                   parsed_args.policy,
                                                   **kwargs)
        if 'action' in resp:
            print('Request accepted by action: %s' % resp['action'])
        else:
            print('Request error: %s' % resp)
