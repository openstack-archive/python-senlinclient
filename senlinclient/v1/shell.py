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

from oslo_serialization import jsonutils

from senlinclient.common import exc
from senlinclient.common.i18n import _
from senlinclient.common import utils
from senlinclient.v1 import models

logger = logging.getLogger(__name__)


def do_build_info(sc, args):
    '''Retrieve build information.'''
    result = sc.get(models.BuildInfo)
    formatters = {
        'api': utils.json_formatter,
        'engine': utils.json_formatter,
    }
    utils.print_dict(result, formatters=formatters)


#### PROFILE TYPES


def do_profile_type_list(sc, args):
    '''List the available profile types.'''
    types = sc.list_short(models.ProfileType, {})
    utils.print_list(types, ['name'], sortby_index=0)


@utils.arg('profile_type', metavar='<PROFILE_TYPE>',
           help=_('Profile type to get the details for.'))
def do_profile_type_show(sc, args):
    '''Show the profile type.'''
    try:
        params = {'profile_type': args.profile_type}
        profile_type = sc.get(models.ProfileTypeSchema, params)
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
        params = {'profile_type': args.profile_type}
        template = sc.get(models.ProfileTypeTemplate, params)
    except exc.HTTPNotFound:
        raise exc.CommandError(
            _('Profile Type %s not found.') % args.profile_type)

    if args.format:
        print(utils.format_output(template, format=args.format))
    else:
        print(utils.format_output(template))


#### PROFILES


@utils.arg('-d', '--show-deleted', default=False, action="store_true",
           help=_('Include soft-deleted profiles if any.'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of profiles returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return profiles that appear after the given ID.'))
def do_profile_list(sc, args=None):
    '''List profiles that meet the criteria.'''
    fields = ['id', 'name', 'type', 'permission', 'created_time']
    queries = {
        'show_deleted': args.show_deleted,
        'limit': args.limit,
        'marker': args.marker,
    }

    profiles = sc.list(models.Profile, **queries)
    utils.print_list(profiles, fields, sortby_index=1)


@utils.arg('-t', '--profile-type', metavar='<TYPE NAME>',
           help=_('Profile type used for this profile.'))
@utils.arg('-s', '--spec-file', metavar='<SPEC FILE>',
           help=_('The spec file used to create the profile.'))
@utils.arg('-p', '--permission', metavar='<PERMISSION>', default='',
           help=_('A string format permission for this profile.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the profile. '
           'This can be specified multiple times, or once with tags'
           'separated by a semicolon.'),
           action='append')
@utils.arg('name', metavar='<PROFILE_NAME>',
           help=_('Name of the profile to create.'))
def do_profile_create(sc, args):
    '''Create a profile.'''
    spec = utils.get_spec_content(args.spec_file)
    if args.profile_type == 'os.heat.stack':
        spec = utils.process_stack_spec(spec)
    params = {
        'name': args.name,
        'type': args.profile_type,
        'spec': spec,
        'permission': args.permission,
        'tags': utils.format_parameters(args.tags),
    }

    profile = sc.create(models.Profile, params)
    if profile:
        print("Profile created: %s" % profile.id)


@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of profile to show.'))
def do_profile_show(sc, args):
    '''Show the profile details.'''
    try:
        params = {'id': args.id}
        profile = sc.get(models.Profile, params)
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Profile not found: %s') % args.id)

    formatters = {
        'tags': utils.json_formatter,
        'spec': utils.nested_dict_formatter(
            ['name', 'rollback', 'parameters', 'environment', 'template'],
            ['property', 'value']),
    }
    print(profile.to_dict())
    utils.print_dict(profile.to_dict(), formatters=formatters)


@utils.arg('-f', '--force', default=False, action="store_true",
           help=_('Delete the profile completely from database.'))
@utils.arg('id', metavar='<NAME or ID>', nargs='+',
           help=_('Name or ID of profile(s) to delete.'))
def do_profile_delete(sc, args):
    '''Delete profile(s).'''
    failure_count = 0

    for cid in args.id:
        try:
            query = {
                'id': cid,
                'force': args.force
            }
            sc.delete(models.Profile, query)
        except exc.HTTPNotFound as ex:
            failure_count += 1
            print(ex)
    if failure_count == len(args.id):
        msg = _('Failed to delete any of the specified profile(s).')
        raise exc.CommandError(msg)
    print('Profile deleted: %s' % args.id)


#### POLICY TYPES


def do_policy_type_list(sc, args):
    '''List the available policy types.'''
    types = sc.list_short(models.PolicyType)
    utils.print_list(types, ['name'], sortby_index=0)


@utils.arg('policy_type', metavar='<POLICY_TYPE>',
           help=_('Policy type to get the details for.'))
def do_policy_type_show(sc, args):
    '''Show the policy type.'''
    try:
        params = {'policy_type': args.policy_type}
        policy_type = sc.get(models.PolicyTypeSchema, params)
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
        params = {'policy_type': args.policy_type}
        template = sc.get(models.PolicyTypeTemplate, params)
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
@utils.arg('-k', '--sort-keys', metavar='<KEYS>',
           help=_('Name of keys used for sorting the returned events.'))
@utils.arg('-d', '--sort-dir', metavar='<DIR>',
           help=_('Direction for sorting, where DIR can be "asc" or "desc".'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of clusters returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return clusters that appear after the given cluster '
                  'ID.'))
def do_cluster_list(sc, args=None):
    '''List the user's clusters.'''
    fields = ['id', 'name', 'status', 'created_time']
    queries = {
        'limit': args.limit,
        'marker': args.marker,
        'filters': utils.format_parameters(args.filters),
        'show_deleted': args.show_deleted,
        'show_nested': args.show_nested
    }
    if args.show_nested:
        fields.append('parent')

    clusters = sc.list(models.Cluster, **queries)
    utils.print_list(clusters, fields, sortby_index=3)


def _show_cluster(sc, cluster_id):
    try:
        query = {'id': cluster_id}
        cluster = sc.get(models.Cluster, query)
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Cluster %s is not found') % args.id)

    formatters = {
        'tags': utils.json_formatter,
        'nodes': utils.list_formatter,
    }
    utils.print_dict(cluster.to_dict(), formatters=formatters)


@utils.arg('-p', '--profile', metavar='<PROFILE ID>',
           help=_('Profile Id used for this cluster.'))
@utils.arg('-n', '--size', metavar='<NUMBER>',
           help=_('Initial size of the cluster.'))
@utils.arg('-o', '--parent', metavar='<PARENT_ID>',
           help=_('ID of the parent cluster, if exists.'))
@utils.arg('-t', '--timeout', metavar='<TIMEOUT>', type=int,
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
    params = {
        'name': args.name,
        'profile_id': args.profile,
        'size': args.size,
        'parent': args.parent,
        'tags': utils.format_parameters(args.tags),
        'timeout': args.timeout
    }

    cluster = sc.create(models.Cluster, params)
    _show_cluster(sc, cluster.id)


@utils.arg('id', metavar='<NAME or ID>', nargs='+',
           help=_('Name or ID of cluster(s) to delete.'))
def do_cluster_delete(sc, args):
    '''Delete the cluster(s).'''
    failure_count = 0

    for cid in args.id:
        try:
            query = {'id': cid}
            sc.delete(models.Cluster, query)
        except exc.HTTPNotFound as ex:
            failure_count += 1
            print(ex)
    if failure_count == len(args.id):
        msg = _('Failed to delete any of the specified clusters.')
        raise exc.CommandError(msg)

    print('Request accepted')


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

    params = {
        'profile_id': args.profile,
        'size': args.size,
        'tags': utils.format_parameters(args.tags),
    }

    if args.timeout:
        params['timeout'] = args.timeout

    sc.update(models.Cluster, params)
    do_cluster_list(sc)


@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to show.'))
def do_cluster_show(sc, args):
    '''Show details of the cluster.'''
    _show_cluster(sc, args.id)


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
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to nodes from.'))
def do_cluster_node_list(sc, args):
    '''List nodes from cluster.'''
    def _short_id(obj):
        return obj.id[:8] + ' ...'

    def _short_physical_id(obj):
        return obj.physical_id[:8] + ' ...'

    fields = ['id', 'name', 'index', 'status', 'physical_id', 'created_time']

    query = {
        'cluster_id': args.id,
        'show_deleted': args.show_deleted,
        'filters': utils.format_parameters(args.filters),
        'limit': args.limit,
        'marker': args.marker,
    }

    try:
        nodes = sc.list(models.ClusterNode, query)
    except exc.HTTPNotFound:
        msg = _('No node matching criteria is found')
        raise exc.CommandError(msg)

    if not args.full_id:
        formatters = {
            'id': _short_id,
            'physical_id': _short_physical_id,
        }
    else:
        formatters = {}

    utils.print_list(nodes, fields, formatters=formatters, sortby_index=5)


@utils.arg('-n', '--nodes', metavar='<NODE_IDs>',
           help=_('ID of nodes to be added.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_node_add(sc, args):
    '''Add specified nodes to cluster.'''
    failure_count = 0
    for nid in args.nodes:
        try:
            params = {'cluster_id': args.id, 'id': nid}
            sc.create(models.ClusterNode, params)
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
            query = {'cluster_id': args.id, 'id': nid}
            sc.delete(models.ClusterNode, query)
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
    query = {'id': args.id}
    policies = sc.list(models.ClusterPolicy, query)
    fields = ['id', 'name', 'enabled', 'level']
    utils.print_list(policies, fields, sortby_index=1)


@utils.arg('-p', '--policy', metavar='<POLICY_ID>',
           help=_('ID of policy to be attached.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_attach(sc, args):
    '''Attach policy to cluster.'''
    params = {'cluster_id': args.id, 'policy_id': args.policy}
    sc.create(models.ClusterPolicy, params)
    do_cluster_policy_list(sc, args.id)


@utils.arg('-p', '--policy', metavar='<POLICY_ID>',
           help=_('ID of policy to be detached.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_detach(sc, args):
    '''Detach policy from cluster.'''
    params = {'cluster_id': args.id, 'policy_id': args.policy}
    sc.delete(models.ClusterPolicy, params)
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
    params = {
        'cluster_id': args.id,
        'policy_id': args.policy,
        'cooldown': args.cooldown,
        'enabled': args.enabled,
        'level': args.level,
    }
    sc.update(models.ClusterPolicy, params)
    do_cluster_policy_list(sc, args.id)


#### NODES


@utils.arg('-c', '--cluster', default=None,
           help=_('ID or name of cluster for nodes to list.'))
@utils.arg('-s', '--show-deleted', default=False, action="store_true",
           help=_('Include soft-deleted nodes if any.'))
@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned nodes. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-k', '--sort-keys', metavar='<KEYS>',
           help=_('Name of keys used for sorting the returned events.'))
@utils.arg('-d', '--sort-dir', metavar='<DIR>',
           help=_('Direction for sorting, where DIR can be "asc" or "desc".'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of nodes returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return nodes that appear after the given node ID.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_node_list(sc, args):
    '''Show list of nodes.'''
    def _short_id(obj):
        return obj.id[:8] + ' ...'

    def _short_cluster_id(obj):
        return obj.cluster_id[:8] + ' ...' if obj.cluster_id else ''

    def _short_physical_id(obj):
        return obj.physical_id[:8] + ' ...' if obj.physical_id else ''

    fields = ['id', 'name', 'status', 'cluster_id', 'physical_id',
              'profile_name', 'created_time', 'updated_time']

    queries = {
        'show_deleted': args.show_deleted,
        'cluster_id': args.cluster,
        'filters': utils.format_parameters(args.filters),
        'sort_keys': args.sort_keys,
        'sort_dir': args.sort_dir,
        'limit': args.limit,
        'marker': args.marker,
    }

    if args.show_deleted:
        fields.append('deleted_time')

    nodes = sc.list(models.Node, **queries)

    if not args.full_id:
        formatters = {
            'id': _short_id,
            'cluster_id': _short_cluster_id,
            'physical_id': _short_physical_id,
        }
    else:
        formatters = {}

    utils.print_list(nodes, fields, formatters=formatters, sortby_index=5)


def _show_node(sc, id):
    '''Show detailed info about the specified node.'''
    try:
        query = {'id': id}
        node = sc.get(models.Node, query)
    except exc.HTTPNotFound:
        msg = _('Node %(id)s is not found') % args.id
        raise exc.CommandError(msg)

    formatters = {
        'tags': utils.json_formatter,
        'data': utils.json_formatter,
    }

    utils.print_dict(node.to_dict(), formatters=formatters)


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
    params = {
        'name': args.name,
        'cluster_id': args.cluster,
        'profile_id': args.profile,
        'role': args.role,
        'tags': utils.format_parameters(args.tags),
    }

    node = sc.create(models.Node, params)
    _show_node(sc, node.id)


@utils.arg('id', metavar='<NODE ID>',
           help=_('Name or ID of the node to show the details for.'))
def do_node_show(sc, args):
    '''Show detailed info about the specified node.'''
    _show_node(sc, args.id)


@utils.arg('id', metavar='<NAME or ID>', nargs='+',
           help=_('Name or ID of node(s) to delete.'))
def do_node_delete(sc, args):
    '''Delete the node(s).'''
    failure_count = 0

    for nid in args.id:
        try:
            query = {'id': nid}
            sc.delete(models.Node, query)
        except exc.HTTPNotFound:
            failure_count += 1
            print('Node id "%s" not found' % nid)
    if failure_count == len(args.id):
        msg = _('Failed to delete any of the specified nodes.')
        raise exc.CommandError(msg)
    print('Request accepted')


@utils.arg('-n', '--name', metavar='<NAME>',
           help=_('New name for the node.'))
@utils.arg('-p', '--profile', metavar='<PROFILE ID>',
           help=_('ID of new profile to use.'))
@utils.arg('-r', '--role', metavar='<ROLE>',
           help=_('Role for this node in the specific cluster.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the node. '
           'This can be specified multiple times, or once with tags'
           'separated by a semicolon.'),
           action='append')
@utils.arg('id', metavar='<ID>',
           help=_('ID of node to update.'))
def do_node_update(sc, args):
    '''Update the node.'''
    params = {
        'id': args.id,
        'name': args.name,
        'role': args.role,
        'profile': args.profile,
        'tags': utils.format_parameters(args.tags),
    }

    sc.update(models.Node, params)
    do_node_list(sc)


@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of node to operate on.'))
def do_node_leave(sc, args):
    '''Make node leave its current cluster.'''
    params = {
        'id': args.id,
        'cluster_id': '',
    }

    sc.update(models.Node, params)
    do_node_list(sc)


@utils.arg('-c', '--cluster',
           help=_('ID or name of cluster for node to join.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of node to operate on.'))
def do_node_join(sc, args):
    '''Make node join the specified cluster.'''
    params = {
        'id': args.id,
        'cluster_id': args.cluster,
    }

    sc.update(models.Node, params)
    do_node_list(sc)


##### EVENTS


@utils.arg('-i', '--id', metavar='<ID>',
           help=_('ID of objects to show the events for.'))
@utils.arg('-n', '--name', metavar='<NAME>',
           help=_('Name of objects to show the events for.'))
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
@utils.arg('-k', '--sort-keys', metavar='<KEYS>',
           help=_('Name of keys used for sorting the returned events.'))
@utils.arg('-d', '--sort-dir', metavar='<DIR>',
           help=_('Direction for sorting, where DIR can be "asc" or "desc".'))
def do_event_list(sc, args):
    '''List events.'''
    queries = {
        'obj_id': args.id,
        'obj_name': args.name,
        'obj_type': args.type,
        'filters': utils.format_parameters(args.filters),
        'sort_keys': args.sort_keys,
        'sort_dir': args.sort_dir,
        'limit': args.limit,
        'marker': args.marker,
    }

    try:
        events = sc.list(models.Event, queries)
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
        query = {'id': args.event}
        event = sc.get(models.Event, query)
    except exc.HTTPNotFound as ex:
        raise exc.CommandError(str(ex))

    utils.print_dict(event.to_dict())


#### EVENTS


@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned actions. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-k', '--sort-keys', metavar='<KEYS>',
           help=_('Name of keys used for sorting the returned events.'))
@utils.arg('-d', '--sort-dir', metavar='<DIR>',
           help=_('Direction for sorting, where DIR can be "asc" or "desc".'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of nodes returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return nodes that appear after the given node ID.'))
@utils.arg('-s', '--show-deleted', default=False, action="store_true",
           help=_('Include soft-deleted nodes if any.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_action_list(sc, args):
    '''List actions.'''
    def _short_id(obj):
        return obj.id[:8] + ' ...'

    def _short_target(obj):
        return obj.target[:8] + ' ...'

    queries = {
        'show_deleted': args.show_deleted,
        'filters': utils.format_parameters(args.filters),
        'sort_keys': args.sort_keys,
        'sort_dir': args.sort_dir,
        'limit': args.limit,
        'marker': args.marker,
    }

    actions = sc.list(models.Action, **queries)

    fields = ['id', 'name', 'action', 'status', 'target', 'depends_on',
              'depended_by']

    if not args.full_id:
        formatters = {
            'id': _short_id,
            'target': _short_target,
        }
    else:
        formatters = {}

    utils.print_list(actions, fields, formatters=formatters, sortby_index=0)


@utils.arg('id', metavar='<ACTION ID>',
           help=_('Name or ID of the action to show the details for.'))
def do_action_show(sc, args):
    '''Show detailed info about the specified action.'''
    try:
        query = {'id': args.id}
        action = sc.get(models.Action, query)
    except exc.HTTPNotFound:
        msg = _('Action %(id)s is not found') % args.id
        raise exc.CommandError(msg)

    formatters = {
        'inputs': utils.json_formatter,
        'outputs': utils.json_formatter,
        'tags': utils.json_formatter,
        'data': utils.json_formatter,
    }

    utils.print_dict(action.to_dict(), formatters=formatters)
