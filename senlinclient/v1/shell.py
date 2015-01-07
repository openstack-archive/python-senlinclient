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

from oslo.serialization import jsonutils

from senlinclient.common import exc
from senlinclient.common.i18n import _
from senlinclient.common import utils

logger = logging.getLogger(__name__)


def do_build_info(sc, args):
    '''Retrieve build information.'''
    result = sc.build_info.build_info()
    formatters = {
        'api': utils.json_formatter,
        'engine': utils.json_formatter,
    }
    utils.print_dict(result, formatters=formatters)


#### PROFILE TYPES


def do_profile_type_list(sc, args):
    '''List the available profile types.'''
    types = sc.profile_types.list()
    utils.print_list(types, ['profile_type'], sortby_index=0)


@utils.arg('profile_type', metavar='<PROFILE_TYPE>',
           help=_('Profile type to get the details for.'))
def do_profile_type_show(sc, args):
    '''Show the profile type.'''
    try:
        profile_type = sc.profile_types.get(args.profile_type)
    except exc.HTTPNotFound:
        raise exc.CommandError(
            _('Profile Type not found: %s') % args.profile_type)
    else:
        print(jsonutils.dumps(profile_type, indent=2))


@utils.arg('profile_type', metavar='<PROFILE_TYPE>',
           help=_('Profile type to generate a template for.'))
@utils.arg('-F', '--format', metavar='<FORMAT>',
           help=_("The template output format, one of: %s.")
                 % ', '.join(utils.supported_formats.keys()))
def do_profile_type_template(sc, args):
    '''Generate a template based on a profile type.'''
    try:
        template = sc.profile_types.generate_template(args.profile_type)
    except exc.HTTPNotFound:
        raise exc.CommandError(
            _('Profile Type %s not found.') % args.profile_type)

    if args.format:
        print(utils.format_output(template, format=args.format))
    else:
        print(utils.format_output(template))


#### PROFILES


#### POLICY TYPES


def do_policy_type_list(sc, args):
    '''List the available policy types.'''
    types = sc.policy_types.list()
    utils.print_list(types, ['policy_type'], sortby_index=0)


@utils.arg('policy_type', metavar='<POLICY_TYPE>',
           help=_('Policy type to get the details for.'))
def do_policy_type_show(sc, args):
    '''Show the policy type.'''
    try:
        policy_type = sc.policy_types.get(args.policy_type)
    except exc.HTTPNotFound:
        raise exc.CommandError(
            _('Policy Type not found: %s') % args.policy_type)
    else:
        print(jsonutils.dumps(policy_type, indent=2))


@utils.arg('policy_type', metavar='<POLICY_TYPE>',
           help=_('Policy type to generate a template for.'))
@utils.arg('-F', '--format', metavar='<FORMAT>',
           help=_("The template output format, one of: %s.")
                 % ', '.join(utils.supported_formats.keys()))
def do_policy_type_template(sc, args):
    '''Generate a template based on a policy type.'''
    try:
        template = sc.policy_types.generate_template(args.policy_type)
    except exc.HTTPNotFound:
        raise exc.CommandError(
            _('Policy Type %s not found.') % args.policy_type)

    if args.format:
        print(utils.format_output(template, format=args.format))
    else:
        print(utils.format_output(template))


#### POLICIES


#### CLUSTERS


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
def do_cluster_list(sc, args=None):
    '''List the user's clusters.'''
    kwargs = {}
    fields = ['id', 'cluster_name', 'status', 'created_time']
    if args:
        kwargs = {'limit': args.limit,
                  'marker': args.marker,
                  'filters': utils.format_parameters(args.filters),
                  'show_deleted': args.show_deleted,
                  'show_nested': args.show_nested}
        if args.show_nested:
            fields.append('parent')

#        if args.global_tenant:
#            fields.insert(2, 'project')

    clusters = sc.clusters.list(**kwargs)
    utils.print_list(clusters, fields, sortby_index=3)


@utils.arg('-p', '--profile', metavar='<PROFILE ID>',
           help=_('Profile Id used for this cluster.'))
@utils.arg('-n', '--size', metavar='<NUMBER>',
           help=_('Initial size of the cluster.'))
@utils.arg('-t', '--timeout', metavar='<TIMEOUT>',
           type=int,
           help=_('Cluster creation timeout in minutes.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the cluster. '
           'This can be specified multiple times, or once with tags'
           'separated by a semicolon.'),
           action='append')
@utils.arg('name', metavar='<CLUSTER_NAME>',
           help=_('Name of the cluster to create.'))
def do_cluster_create(sc, args):
    '''Create the cluster.'''
    fields = {
        'name': args.name,
        'profile_id': args.profile,
        'tags': utils.format_parameters(args.tags),
        'size': args.size,
        'timeout': args.timeout
    }

    sc.clusters.create(**fields)
    do_cluster_list(sc)


@utils.arg('id', metavar='<NAME or ID>', nargs='+',
           help=_('Name or ID of cluster(s) to delete.'))
def do_cluster_delete(sc, args):
    '''Delete the cluster(s).'''
    failure_count = 0

    for cid in args.id:
        try:
            sc.clusters.delete(cid)
        except exc.HTTPNotFound as ex:
            failure_count += 1
            print(ex)
    if failure_count == len(args.id):
        msg = _('Failed to delete any of the specified clusters.')
        raise exc.CommandError(msg)
    do_cluster_list(sc)


@utils.arg('-p', '--profile', metavar='<PROFILE ID>',
           help=_('ID of new profile to use.'))
@utils.arg('-n', '--size', metavar='<NUMBER>',
           help=_('Initial size of the cluster.'))
@utils.arg('-t', '--timeout', metavar='<TIMEOUT>',
           type=int,
           help=_('Cluster update timeout in minutes.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the cluster. '
           'This can be specified multiple times, or once with tags'
           'separated by a semicolon.'),
           action='append')
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to update.'))
def do_cluster_update(sc, args):
    '''Update the cluster.'''

    fields = {
        'profile_id': args.profile,
        'size': args.size,
        'tags': utils.format_parameters(args.tags),
    }

    if args.timeout:
        fields['timeout'] = args.timeout

    sc.clusters.update(**fields)
    do_cluster_list(sc)


@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to show.'))
def do_cluster_show(sc, args):
    '''Show details of the cluster.'''
    try:
        cluster = sc.clusters.get(args.id)
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Cluster not found: %s') % args.id)
    else:
        formatters = {
            'profile': utils.json_formatter,
            'status': utils.text_wrap_formatter,
            'status_reason': utils.text_wrap_formatter,
            'tags': utils.json_formatter,
            'links': utils.link_formatter
        }
        utils.print_dict(cluster.to_dict(), formatters=formatters)


@utils.arg('-s', '--show-deleted', default=False, action="store_true",
           help=_('Include soft-deleted nodes if any.'))
@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned nodes. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of nodes returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return nodes that appear after the given node ID.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to nodes from.'))
def do_cluster_node_list(sc, args):
    '''List nodes from cluster.'''
    fields = ['id', 'name', 'index', 'status', 'physical_id', 'created_time']

    kwargs = {
        'cluster_id': args.id,
        'show_deleted': args.show_deleted,
        'filters': utils.format_parameters(args.filters),
        'limit': args.limit,
        'marker': args.marker,
    }

    try:
        nodes = sc.nodes.list(**kwargs)
    except exc.HTTPNotFound:
        msg = _('No node matching criteria is found')
        raise exc.CommandError(msg)

    utils.print_list(nodes, fields, sortby_index=5)


@utils.arg('-n', '--nodes', metavar='<NODE_IDs>',
           help=_('ID of nodes to be added.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_node_add(sc, args):
    '''Add specified nodes to cluster.'''
    failure_count = 0
    for nid in args.nodes:
        try:
            sc.clusters.add_node(args.id, nid)
        except Exception as ex:
            failure_count += 1
            print(ex)
    if failure_count == len(args.nodes):
        msg = _('Failed to add any of the specified nodes.')
        raise exc.CommandError(msg)

    do_cluster_node_list(sc, id=args.id)


@utils.arg('-n', '--nodes', metavar='<NODE_IDs>',
           help=_('ID of nodes to be deleted.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_node_del(sc, args):
    '''Delete specified nodes from cluster.'''
    failure_count = 0
    for nid in args.nodes:
        try:
            sc.clusters.del_node(args.id, nid)
        except Exception as ex:
            failure_count += 1
            print(ex)
    if failure_count == len(args.nodes):
        msg = _('Failed to delete any of the specified nodes.')
        raise exc.CommandError(msg)

    do_cluster_node_list(sc, id=args.id)


@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_list(sc, args):
    '''List policies from cluster.'''
    policies = sc.clusters.list_policy(args.id)
    fields = ['id', 'name', 'enabled', 'level']
    utils.print_list(policies, fields, sortby_index=1)


@utils.arg('-p', '--policy', metavar='<POLICY_ID>',
           help=_('ID of policy to be attached.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_attach(sc, args):
    '''Attach policy to cluster.'''
    sc.clusters.attach_policy(args.id, args.policy)
    do_cluster_policy_list(sc, args.id)


@utils.arg('-p', '--policy', metavar='<POLICY_ID>',
           help=_('ID of policy to be detached.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_detach(sc, args):
    '''Detach policy from cluster.'''
    sc.clusters.detach_policy(args.id, args.policy)
    do_cluster_policy_list(sc, args.id)


@utils.arg('-p', '--policy', metavar='<POLICY_ID>',
           help=_('ID of policy to be enabled.'))
@utils.arg('-c', '--cooldown', metavar='<COOLDOWN>',
           help=_('Cooldown interval in seconds.'))
@utils.arg('-l', '--level', metavar='<LEVEL>',
           help=_('Enforcement level.'))
@utils.arg('-e', '--enabled', metavar='<BOOLEAN>',
           help=_('Specify whether to enable policy.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_update(sc, args):
    '''Enable policy on cluster.'''
    kwargs = {
        'policy_id': args.policy,
        'cooldown': args.cooldown,
        'enabled': args.enabled,
        'level': args.level,
    }
    sc.clusters.update_policy(args.id, **kwargs)
    do_cluster_policy_list(sc, args.id)


#### NODES


@utils.arg('-c', '--cluster', metavar='<CLUSTER_ID>',
           help=_('Cluster Id for this node.'))
@utils.arg('-p', '--profile', metavar='<PROFILE_ID>',
           help=_('Profile Id used for this node.'))
@utils.arg('-r', '--role', metavar='<ROLE>',
           help=_('Role for this node in the specific cluster.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the cluster. '
           'This can be specified multiple times, or once with tags'
           'separated by a semicolon.'),
           action='append')
@utils.arg('name', metavar='<NODE_NAME>',
           help=_('Name of the node to create.'))
def do_node_create(sc, args):
    '''Create the node.'''
    fields = {
        'name': args.name,
        'cluster_id': args.cluster,
        'profile_id': args.profile,
        'role': args.role,
        'tags': utils.format_parameters(args.tags),
    }

    sc.nodes.create(**fields)
    do_node_list(sc)


@utils.arg('id', metavar='<NAME or ID>', nargs='+',
           help=_('Name or ID of node(s) to delete.'))
def do_node_delete(sc, args):
    '''Delete the node(s).'''
    failure_count = 0

    for nid in args.id:
        try:
            sc.nodes.delete(nid)
        except exc.HTTPNotFound as ex:
            failure_count += 1
            print(ex)
    if failure_count == len(args.id):
        msg = _('Failed to delete any of the specified nodes.')
        raise exc.CommandError(msg)
    do_node_list(sc)


@utils.arg('-p', '--profile', metavar='<PROFILE ID>',
           help=_('ID of new profile to use.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the node. '
           'This can be specified multiple times, or once with tags'
           'separated by a semicolon.'),
           action='append')
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of node to update.'))
def do_node_update(sc, args):
    '''Update the node.'''
    fields = {
        'id': args.id,
        'profile': args.profile,
        'tags': utils.format_parameters(args.tags),
    }

    sc.nodes.update(**fields)
    do_node_list(sc)


@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of node to operate on.'))
def do_node_leave(sc, args):
    '''Make node leave its current cluster.'''
    sc.nodes.leave(args.id)
    do_node_list(sc)


@utils.arg('-c', '--cluster',
           help=_('ID or name of cluster for node to join.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of node to operate on.'))
def do_node_join(sc, args):
    '''Make node join the specified cluster.'''
    sc.nodes.join(args.id, args.cluster)
    do_node_list(sc)


@utils.arg('-c', '--cluster', default=None,
           help=_('ID or name of cluster for nodes to list.'))
@utils.arg('-s', '--show-deleted', default=False, action="store_true",
           help=_('Include soft-deleted nodes if any.'))
@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned nodes. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of nodes returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return nodes that appear after the given node ID.'))
@utils.arg('-g', '--global-tenant', action='store_true', default=False,
           help=_('List nodes from all tenants. Operation only authorized '
                  'for users who match the policy in policy file.'))
def do_node_list(sc, args):
    '''Show list of nodes.'''
    fields = ['id', 'name', 'status', 'cluster_id', 'physical_id',
              'created_time']
    if args.global_tenant:
        fields.insert(2, 'project')

    kwargs = {
        'cluster_id': args.cluster,
        'show_deleted': args.show_deleted,
        'filters': utils.format_parameters(args.filters),
        'limit': args.limit,
        'marker': args.marker,
        'global_tenant': args.global_tenant,
    }

    try:
        nodes = sc.nodes.list(**kwargs)
    except exc.HTTPNotFound:
        msg = _('No node matching criteria is found')
        raise exc.CommandError(msg)

    utils.print_list(nodes, fields, sortby_index=5)


@utils.arg('id', metavar='<NODE ID>',
           help=_('Name or ID of the node to show the details for.'))
def do_node_show(sc, args):
    '''Show detailed info about the specified node.'''
    try:
        node = sc.nodes.get(args.id)
    except exc.HTTPNotFound:
        msg = _('Node %(id)s is not found') % args.id
        raise exc.CommandError(msg)

    formatters = {
        'links': utils.link_formatter,
        'required_by': utils.newline_list_formatter
    }

    utils.print_dict(node.to_dict(), formatters=formatters)


##### EVENTS


@utils.arg('-i', '--id', metavar='<NAME or ID>',
           help=_('Name or ID of objects to show the events for.'))
@utils.arg('-t', '--type', metavar='<OBJECT TYPE>',
           help=_('Types of the objects to filter events by.'
                  'The types can be CLUSTER, NODE, PROFILE, POLICY.'))
@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned events. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of events returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return events that appear after the given event ID.'))
def do_event_list(sc, args):
    '''List events.'''
    fields = {'obj_id': args.id,
              'obj_type': args.type,
              'limit': args.limit,
              'marker': args.marker,
              'filters': utils.format_parameters(args.filters)}
    try:
        events = sc.events.list(**fields)
    except exc.HTTPNotFound as ex:
        raise exc.CommandError(str(ex))

    fields = ['timestamp', 'obj_type', 'obj_id', 'action', 'status',
              'status_reason']
    utils.print_list(events, fields, sortby_index=0)


@utils.arg('event', metavar='<EVENT>',
           help=_('ID of event to display details for.'))
def do_event_show(sc, args):
    '''Describe the event.'''
    try:
        event = sc.events.get(args.event)
    except exc.HTTPNotFound as ex:
        raise exc.CommandError(str(ex))

    utils.print_dict(event.to_dict())


#### EVENTS


@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned actions. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of actions returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return action that appear after the given action ID.'))
def do_action_list(sc, args):
    '''List actions.'''
    fields = {
        'limit': args.limit,
        'marker': args.marker,
        'filters': utils.format_parameters(args.filters)
    }

    try:
        actions = sc.actions.list(**fields)
    except exc.HTTPNotFound as ex:
        raise exc.CommandError(str(ex))

    fields = ['name', 'action', 'status', 'status_reason', 'depends_on',
              'depended_by']

    utils.print_list(actions, fields, sortby_index=0)
