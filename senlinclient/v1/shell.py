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

import logging

from senlinclient.common.i18n import _
from senlinclient.common import utils

logger = logging.getLogger(__name__)


@utils.arg('-s', '--show-deleted', default=False, action="store_true",
           help=_('Include soft-deleted clusters if any.'))
@utils.arg('-n', '--show-nested', default=False, action="store_true",
           help=_('Include nested clusters if any.'))
@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned clusters. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of clusters returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return clusters that appear after the given cluster '
                  'ID.'))
@utils.arg('-g', '--global-tenant', action='store_true', default=False,
           help=_('List clusters from all tenants. Operation only authorized '
                  'for users who match the policy in policy file.'))
@utils.arg('-o', '--show-parent', action='store_true', default=False,
           help=_('Show cluster parent information. This is automatically '
                  'enabled when using %(arg)s.') % {'arg': '--global-tenant'})
def do_cluster_list(sc, args=None):
    '''List the user's clusters.'''
    kwargs = {}
    fields = ['id', 'cluster_name', 'status', 'created_time']
    if args:
        kwargs = {'limit': args.limit,
                  'marker': args.marker,
                  'filters': utils.format_parameters(args.filters),
                  'global_tenant': args.global_tenant,
                  'show_deleted': args.show_deleted}
        if args.show_nested:
            fields.append('parent')
            kwargs['show_nested'] = True

        if args.global_tenant or args.show_parent:
            fields.insert(2, 'parent')
        if args.global_tenant:
            fields.insert(2, 'project')

    clusters = sc.clusters.list(**kwargs)
    utils.print_list(clusters, fields, sortby_index=3)
