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


# PROFILE TYPES


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
def do_profile_type_schema(sc, args):
    '''Get the spec of a profile type.'''
    try:
        params = {'profile_type': args.profile_type}
        schema = sc.get(models.ProfileTypeSchema, params)
    except exc.HTTPNotFound:
        raise exc.CommandError(
            _('Profile Type %s not found.') % args.profile_type)

    schema = dict(schema)

    if args.format:
        print(utils.format_output(schema, format=args.format))
    else:
        print(utils.format_output(schema))


# PROFILES


@utils.arg('-d', '--show-deleted', default=False, action="store_true",
           help=_('Include soft-deleted profiles if any.'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of profiles returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return profiles that appear after the given ID.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_profile_list(sc, args=None):
    '''List profiles that meet the criteria.'''
    def _short_id(obj):
        return obj.id[:8]

    fields = ['id', 'name', 'type', 'permission', 'created_time']
    queries = {
        'show_deleted': args.show_deleted,
        'limit': args.limit,
        'marker': args.marker,
    }

    profiles = sc.list(models.Profile, **queries)
    formatters = {}
    if not args.full_id:
        formatters = {
            'id': _short_id,
        }
    utils.print_list(profiles, fields, formatters=formatters, sortby_index=1)


def _show_profile(sc, profile_id):
    try:
        params = {'id': profile_id}
        profile = sc.get(models.Profile, params)
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Profile not found: %s') % profile_id)

    formatters = {
        'tags': utils.json_formatter,
    }

    if profile.type == 'os.heat.stack':
        formatters['spec'] = utils.nested_dict_formatter(
            ['disable_rollback', 'environment', 'files', 'parameters',
             'template', 'timeout'],
            ['property', 'value'])

    utils.print_dict(profile.to_dict(), formatters=formatters)


@utils.arg('-t', '--profile-type', metavar='<TYPE NAME>', required=True,
           help=_('Profile type used for this profile.'))
@utils.arg('-s', '--spec-file', metavar='<SPEC FILE>', required=True,
           help=_('The spec file used to create the profile.'))
@utils.arg('-p', '--permission', metavar='<PERMISSION>', default='',
           help=_('A string format permission for this profile.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the profile. '
                  'This can be specified multiple times, or once with tags '
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
    _show_profile(sc, profile.id)


@utils.arg('id', metavar='<PROFILE>',
           help=_('Name or ID of profile to show.'))
def do_profile_show(sc, args):
    '''Show the profile details.'''
    _show_profile(sc, args.id)


@utils.arg('-n', '--name', metavar='<NAME>',
           help=_('The new name for the profile.'))
@utils.arg('-s', '--spec-file', metavar='<SPEC FILE>',
           help=_('The new spec file for the profile.'))
@utils.arg('-p', '--permission', metavar='<PERMISSION>', default='',
           help=_('A string format permission for this profile.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the profile. '
                  'This can be specified multiple times, or once with tags '
                  'separated by a semicolon.'),
           action='append')
@utils.arg('-t', '--profile-type', metavar='<TYPE NAME>', required=True,
           help=_('Profile type used for this profile.'))
@utils.arg('id', metavar='<PROFILE_ID>',
           help=_('Name or ID of the profile to update.'))
def do_profile_update(sc, args):
    '''Update a profile.'''
    spec = None
    if args.spec_file:
        spec = utils.get_spec_content(args.spec_file)
        if args.profile_type == 'os.heat.stack':
            spec = utils.process_stack_spec(spec)
    params = {
        'name': args.name,
        'spec': spec,
        'permission': args.permission,
        'tags': utils.format_parameters(args.tags),
    }

    # Find the profile first, we need its id
    try:
        profile = sc.get(models.Profile, {'id': args.id})
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Profile not found: %s') % args.id)

    params['id'] = profile.id
    sc.update(models.Profile, params)
    _show_profile(sc, args.id)


@utils.arg('-f', '--force', default=False, action="store_true",
           help=_('Delete the profile completely from database.'))
@utils.arg('id', metavar='<PROFILE>', nargs='+',
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


# POLICY TYPES


def do_policy_type_list(sc, args):
    '''List the available policy types.'''
    types = sc.list_short(models.PolicyType, {})
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
def do_policy_type_schema(sc, args):
    '''Get the spec of a policy type.'''
    try:
        params = {'policy_type': args.policy_type}
        schema = sc.get(models.PolicyTypeSchema, params)
    except exc.HTTPNotFound:
        raise exc.CommandError(
            _('Policy type %s not found.') % args.policy_type)

    schema = dict(schema)

    if args.format:
        print(utils.format_output(schema, format=args.format))
    else:
        print(utils.format_output(schema))


# WEBHOOKS


@utils.arg('-d', '--show-deleted', default=False, action="store_true",
           help=_('Include deleted webhooks if any.'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of webhooks returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return webhooks that appear after the given ID.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_webhook_list(sc, args=None):
    '''List webhooks that meet the criteria.'''
    def _short_id(obj):
        return obj.id[:8]

    fields = ['id', 'name', 'obj_id', 'obj_type', 'action', 'created_time']
    queries = {
        'show_deleted': args.show_deleted,
        'limit': args.limit,
        'marker': args.marker,
    }

    webhooks = sc.list(models.Webhook, **queries)
    formatters = {}
    if not args.full_id:
        formatters = {
            'id': _short_id,
        }
    utils.print_list(webhooks, fields, formatters=formatters, sortby_index=1)


def _show_webhook(sc, webhook_id=None, webhook=None):
    if webhook is None:
        try:
            params = {'id': webhook_id}
            webhook = sc.get(models.Webhook, params)
        except exc.HTTPNotFound:
            raise exc.CommandError(_('Webhook not found: %s') % webhook_id)

    formatters = {}
    utils.print_dict(webhook.to_dict(), formatters=formatters)


@utils.arg('id', metavar='<WEBHOOK>',
           help=_('Name of the webhook to be updated.'))
def do_webhook_show(sc, args):
    '''Show the webhook details.'''
    _show_webhook(sc, webhook_id=args.id)


@utils.arg('-t', '--obj-type', metavar='<OBJECT_TYPE>', required=True,
           help=_('Object type name used for this webhook.'))
@utils.arg('-i', '--obj-id', metavar='<OBJECT_ID>', required=True,
           help=_('Object id used for this webhook.'))
@utils.arg('-a', '--action', metavar='<ACTION>', required=True,
           help=_('Name of action used for this webhook.'))
@utils.arg('-c', '--credential', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           required=True,
           help=_('The credential used when triggering the webhook.'),
           action='append')
@utils.arg('-p', '--params', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('A dictionary of parameters that will be passed to object '
                  'action when webhook is triggered.'),
           action='append')
@utils.arg('name', metavar='<NAME>',
           help=_('Name of the webhook to create.'))
def do_webhook_create(sc, args):
    '''Create a webhook.'''
    params = {
        'name': args.name,
        'obj_id': args.obj_id,
        'obj_type': args.obj_type,
        'action': args.action,
        'credential': utils.format_parameters(args.credential),
        'params': utils.format_parameters(args.params)
    }

    webhook = sc.create(models.Webhook, params, True)
    _show_webhook(sc, webhook=webhook)


@utils.arg('id', metavar='<WEBHOOK>', nargs='+',
           help=_('Name or ID of webhook(s) to delete.'))
def do_webhook_delete(sc, args):
    '''Delete webhook(s).'''
    failure_count = 0

    for cid in args.id:
        try:
            query = {
                'id': cid,
            }
            sc.delete(models.Webhook, query)
        except exc.HTTPNotFound as ex:
            failure_count += 1
            print(ex)
    if failure_count == len(args.id):
        msg = _('Failed to delete any of the specified webhook(s).')
        raise exc.CommandError(msg)
    print('Webhook deleted: %s' % args.id)


# POLICIES


@utils.arg('-d', '--show-deleted', default=False, action="store_true",
           help=_('Include soft-deleted policies if any.'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of policies returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return policies that appear after the given ID.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_policy_list(sc, args=None):
    '''List policies that meet the criteria.'''
    def _short_id(obj):
        return obj.id[:8]

    fields = ['id', 'name', 'type', 'level', 'cooldown', 'created_time']
    queries = {
        'show_deleted': args.show_deleted,
        'limit': args.limit,
        'marker': args.marker,
    }

    policies = sc.list(models.Policy, **queries)
    formatters = {}
    if not args.full_id:
        formatters = {
            'id': _short_id,
        }
    utils.print_list(policies, fields, formatters=formatters, sortby_index=1)


def _show_policy(sc, policy_id=None, policy=None):
    if policy is None:
        try:
            params = {'id': policy_id}
            policy = sc.get(models.Policy, params)
        except exc.HTTPNotFound:
            raise exc.CommandError(_('Policy not found: %s') % policy_id)

    formatters = {
        'tags': utils.json_formatter,
        'spec': utils.json_formatter,
    }
    utils.print_dict(policy.to_dict(), formatters=formatters)


@utils.arg('-t', '--policy-type', metavar='<TYPE_NAME>', required=True,
           help=_('Policy type used for this policy.'))
@utils.arg('-s', '--spec-file', metavar='<SPEC_FILE>', required=True,
           help=_('The spec file used to create the policy.'))
@utils.arg('-c', '--cooldown', metavar='<SECONDS>', default=0,
           help=_('An integer indicating the cooldown seconds once the '
                  'policy is effected. Default to 0.'))
@utils.arg('-l', '--enforcement-level', metavar='<LEVEL>', default=0,
           help=_('An integer beteen 0 and 100 representing the enforcement '
                  'level. Default to 0.'))
@utils.arg('name', metavar='<NAME>',
           help=_('Name of the policy to create.'))
def do_policy_create(sc, args):
    '''Create a policy.'''
    spec = utils.get_spec_content(args.spec_file)
    params = {
        'name': args.name,
        'type': args.policy_type,
        'spec': spec,
        'cooldown': args.cooldown,
        'level': args.enforcement_level,
    }

    policy = sc.create(models.Policy, params)
    _show_policy(sc, policy=policy)


@utils.arg('id', metavar='<POLICY>',
           help=_('Name of the policy to be updated.'))
def do_policy_show(sc, args):
    '''Show the policy details.'''
    _show_policy(sc, policy_id=args.id)


@utils.arg('-c', '--cooldown', metavar='<SECONDS>',
           help=_('An integer indicating the cooldown seconds once the '
                  'policy is effected. Default to 0.'))
@utils.arg('-l', '--enforcement-level', metavar='<LEVEL>',
           help=_('An integer beteen 0 and 100 representing the enforcement '
                  'level. Default to 0.'))
@utils.arg('-n', '--name', metavar='<NAME>',
           help=_('New name of the policy to be updated.'))
@utils.arg('id', metavar='<POLICY>',
           help=_('Name of the policy to be updated.'))
def do_policy_update(sc, args):
    '''Update a policy.'''
    params = {
        'name': args.name,
        'cooldown': args.cooldown,
        'level': args.enforcement_level,
    }

    policy = sc.get(models.Policy, {'id': args.id})
    if policy is not None:
        params['id'] = policy.id
        sc.update(models.Policy, params)
        _show_policy(sc, policy_id=policy.id)


@utils.arg('-f', '--force', default=False, action="store_true",
           help=_('Delete the policy completely from database.'))
@utils.arg('id', metavar='<POLICY>', nargs='+',
           help=_('Name or ID of policy(s) to delete.'))
def do_policy_delete(sc, args):
    '''Delete policy(s).'''
    failure_count = 0

    for cid in args.id:
        try:
            query = {
                'id': cid,
                'force': args.force
            }
            sc.delete(models.Policy, query)
        except exc.HTTPNotFound as ex:
            failure_count += 1
            print(ex)
    if failure_count == len(args.id):
        msg = _('Failed to delete any of the specified policy(s).')
        raise exc.CommandError(msg)
    print('Policy deleted: %s' % args.id)


# CLUSTERS


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
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_cluster_list(sc, args=None):
    '''List the user's clusters.'''
    def _short_id(obj):
        return obj.id[:8]

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
    formatters = {}
    if not args.full_id:
        formatters = {
            'id': _short_id,
        }
    utils.print_list(clusters, fields, formatters=formatters, sortby_index=3)


def _show_cluster(sc, cluster_id):
    try:
        query = {'id': cluster_id}
        cluster = sc.get(models.Cluster, query)
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Cluster %s is not found') % cluster_id)

    formatters = {
        'tags': utils.json_formatter,
        'nodes': utils.list_formatter,
    }
    utils.print_dict(cluster.to_dict(), formatters=formatters)


@utils.arg('-p', '--profile', metavar='<PROFILE>', required=True,
           help=_('Profile Id used for this cluster.'))
@utils.arg('-c', '--desired-capacity', metavar='<DESIRED-CAPACITY>', default=0,
           help=_('Desired capacity of the cluster. Default to 0.'))
@utils.arg('-o', '--parent', metavar='<PARENT_ID>',
           help=_('ID of the parent cluster, if exists.'))
@utils.arg('-t', '--timeout', metavar='<TIMEOUT>', type=int,
           help=_('Cluster creation timeout in minutes.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the cluster. '
                  'This can be specified multiple times, or once with tags '
                  'separated by a semicolon.'),
           action='append')
@utils.arg('name', metavar='<CLUSTER_NAME>',
           help=_('Name of the cluster to create.'))
def do_cluster_create(sc, args):
    '''Create the cluster.'''
    params = {
        'name': args.name,
        'profile_id': args.profile,
        'desired_capacity': args.desired_capacity,
        'parent': args.parent,
        'tags': utils.format_parameters(args.tags),
        'timeout': args.timeout
    }

    cluster = sc.create(models.Cluster, params)
    _show_cluster(sc, cluster.id)


@utils.arg('id', metavar='<CLUSTER>', nargs='+',
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


@utils.arg('-p', '--profile', metavar='<PROFILE>',
           help=_('ID of new profile to use.'))
@utils.arg('-t', '--timeout', metavar='<TIMEOUT>',
           help=_('New timeout (in minutes) value for the cluster.'))
@utils.arg('-r', '--parent', metavar='<PARENT>',
           help=_('ID of parent cluster for the cluster.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the cluster. '
                  'This can be specified multiple times, or once with tags '
                  'separated by a semicolon.'),
           action='append')
@utils.arg('-n', '--name', metavar='<NAME>',
           help=_('New name for the cluster to update.'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to be updated.'))
def do_cluster_update(sc, args):
    '''Update the cluster.'''
    cluster = sc.get(models.Cluster, {'id': args.id})
    params = {
        'id': cluster.id,
        'name': args.name,
        'profile_id': args.profile,
        'parent': args.parent,
        'tags': utils.format_parameters(args.tags),
        'timeout': args.timeout,
    }

    sc.update(models.Cluster, params)
    _show_cluster(sc, cluster.id)


@utils.arg('id', metavar='<CLUSTER>',
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
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to nodes from.'))
def do_cluster_node_list(sc, args):
    '''List nodes from cluster.'''
    def _short_id(obj):
        return obj.id[:8]

    def _short_physical_id(obj):
        return obj.physical_id[:8]

    query = {
        'cluster_id': args.id,
        'show_deleted': args.show_deleted,
        'filters': utils.format_parameters(args.filters),
        'limit': args.limit,
        'marker': args.marker,
    }

    try:
        nodes = sc.list(models.Node, **query)
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

    fields = ['id', 'name', 'index', 'status', 'physical_id', 'created_time']
    utils.print_list(nodes, fields, formatters=formatters, sortby_index=5)


@utils.arg('-n', '--nodes', metavar='<NODES>', required=True,
           help=_('ID of nodes to be added; multiple nodes can be separated '
                  'with ","'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_node_add(sc, args):
    '''Add specified nodes to cluster.'''
    node_ids = args.nodes.split(',')
    params = {
        'id': args.id,
        'action': 'add_nodes',
        'action_args': {
            'nodes': node_ids,
        }
    }
    resp = sc.action(models.Cluster, params)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-n', '--nodes', metavar='<NODES>', required=True,
           help=_('ID of nodes to be deleted; multiple nodes can be separated'
                  'with ",".'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_node_del(sc, args):
    '''Delete specified nodes from cluster.'''
    node_ids = args.nodes.split(',')
    params = {
        'id': args.id,
        'action': 'del_nodes',
        'action_args': {
            'nodes': node_ids,
        }
    }
    resp = sc.action(models.Cluster, params)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-c', '--count', metavar='<COUNT>',
           help=_('Number of nodes to be added.'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_scale_out(sc, args):
    '''Scale out a cluster by the specified number of nodes.'''
    params = {
        'id': args.id,
        'action': 'scale_out',
        'action_args': {
            'count': args.count
        }
    }

    resp = sc.action(models.Cluster, params)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-c', '--count', metavar='<COUNT>',
           help=_('Number of nodes to be added.'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_scale_in(sc, args):
    '''Scale in a cluster by the specified number of nodes.'''
    if args.count is not None:
        action_args = {'count': args.count}
    else:
        action_args = {}

    params = {
        'id': args.id,
        'action': 'scale_in',
        'action_args': action_args,
    }
    resp = sc.action(models.Cluster, params)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned results. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-k', '--sort-keys', metavar='<KEYS>',
           help=_('Name of keys used for sorting the returned events.'))
@utils.arg('-d', '--sort-dir', metavar='<DIR>',
           help=_('Direction for sorting, where DIR can be "asc" or "desc".'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to query on.'))
def do_cluster_policy_list(sc, args):
    '''List policies from cluster.'''
    query = {'id': args.id}
    cluster = sc.get(models.Cluster, query)

    queries = {
        'filters': utils.format_parameters(args.filters),
        'sort_keys': args.sort_keys,
        'sort_dir': args.sort_dir,
    }
    policies = sc.list(models.ClusterPolicy,
                       path_args={'cluster_id': cluster.id},
                       **queries)
    fields = ['policy_id', 'policy', 'type', 'priority', 'level',
              'cooldown', 'enabled']
    utils.print_list(policies, fields, sortby_index=3)


@utils.arg('-p', '--policy', metavar='<POLICY>', required=True,
           help=_('ID or name of the policy to query on.'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('ID or name of the cluster to query on.'))
def do_cluster_policy_show(sc, args):
    '''Show a specific policy that is bound to the specified cluster.'''
    queries = {
        'cluster_id': args.id,
        'policy_id': args.policy
    }
    binding = sc.get(models.ClusterPolicy, queries)
    utils.print_dict(binding.to_dict())


@utils.arg('-p', '--policy', metavar='<POLICY>', required=True,
           help=_('ID or name of policy to be attached.'))
@utils.arg('-r', '--priority', metavar='<PRIORITY>', default=50,
           help=_('An integer specifying the relative priority among '
                  'all policies attached to a cluster. The lower the '
                  'value, the higher the priority. Default is 50.'))
@utils.arg('-l', '--enforcement-level', metavar='<LEVEL>', default=50,
           help=_('An integer beteen 0 and 100 representing the enforcement '
                  'level. Default to enforcement level of policy.'))
@utils.arg('-c', '--cooldown', metavar='<SECONDS>', default=0,
           help=_('An integer indicating the cooldown seconds once the '
                  'policy is effected. Default to cooldown of policy.'))
@utils.arg('-e', '--enabled', default=True, action="store_true",
           help=_('Whether the policy should be enabled once attached. '
                  'Default to enabled.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_attach(sc, args):
    '''Attach policy to cluster.'''
    params = {
        'id': args.id,
        'action': 'policy_attach',
        'action_args': {
            'policy_id': args.policy,
            'priority': args.priority,
            'level': args.enforcement_level,
            'cooldown': args.cooldown,
            'enabled': args.enabled,
        }
    }

    resp = sc.action(models.Cluster, params)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-p', '--policy', metavar='<POLICY>', required=True,
           help=_('ID or name of policy to be detached.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_detach(sc, args):
    '''Detach policy from cluster.'''
    params = {
        'id': args.id,
        'action': 'policy_detach',
        'action_args': {
            'policy_id': args.policy,
        }
    }

    resp = sc.action(models.Cluster, params)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-p', '--policy', metavar='<POLICY>', required=True,
           help=_('ID or name of policy to be updated.'))
@utils.arg('-r', '--priority', metavar='<PRIORITY>',
           help=_('An integer specifying the relative priority among '
                  'all policies attached to a cluster. The lower the '
                  'value, the higher the priority. Default is 50.'))
@utils.arg('-l', '--enforcement-level', metavar='<LEVEL>',
           help=_('New enforcement level.'))
@utils.arg('-c', '--cooldown', metavar='<COOLDOWN>',
           help=_('Cooldown interval in seconds.'))
@utils.arg('-e', '--enabled', metavar='<BOOLEAN>',
           help=_('Whether the policy should be enabled.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_update(sc, args):
    '''Update a policy on cluster.'''
    params = {
        'id': args.id,
        'action': 'policy_update',
        'action_args': {
            'policy_id': args.policy,
            'priority': args.priority,
            'level': args.enforcement_level,
            'cooldown': args.cooldown,
            'enabled': args.enabled,
        }
    }

    resp = sc.action(models.Cluster, params)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-p', '--policy', metavar='<POLICY>', required=True,
           help=_('ID or name of policy to be enabled.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_enable(sc, args):
    '''Enable a policy on cluster.'''
    params = {
        'id': args.id,
        'action': 'policy_enable',
        'action_args': {
            'policy_id': args.policy,
        }
    }
    resp = sc.action(models.Cluster, params)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-p', '--policy', metavar='<POLICY>', required=True,
           help=_('ID or name of policy to be disabled.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_disable(sc, args):
    '''Disable a policy on a cluster.'''
    params = {
        'id': args.id,
        'action': 'policy_disable',
        'action_args': {
            'policy_id': args.policy,
        }
    }
    resp = sc.action(models.Cluster, params)
    print('Request accepted by action %s' % resp['action'])


# NODES


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
@utils.arg('-g', '--global-tenant', default=False, action="store_true",
           help=_('Indicate that this node list should include nodes from '
                  'all tenants. This option is subject to access policy '
                  'checking. Default is False.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_node_list(sc, args):
    '''Show list of nodes.'''
    def _short_id(obj):
        return obj.id[:8]

    def _short_cluster_id(obj):
        return obj.cluster_id[:8] if obj.cluster_id else ''

    def _short_physical_id(obj):
        return obj.physical_id[:8] if obj.physical_id else ''

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
        'global_tenant': args.global_tenant,
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

    utils.print_list(nodes, fields, formatters=formatters, sortby_index=6)


def _show_node(sc, node_id, show_details=False):
    '''Show detailed info about the specified node.'''
    try:
        query = {
            'id': node_id,
            'show_details': show_details,
        }
        node = sc.get_with_args(models.Node, query)
    except exc.HTTPNotFound:
        msg = _('Node %s is not found') % node_id
        raise exc.CommandError(msg)

    formatters = {
        'tags': utils.json_formatter,
        'data': utils.json_formatter,
    }
    data = node.to_dict()
    if show_details:
        formatters['details'] = utils.nested_dict_formatter(
            list(node['details'].keys()), ['property', 'value'])

    utils.print_dict(data, formatters=formatters)


@utils.arg('-p', '--profile', metavar='<PROFILE>', required=True,
           help=_('Profile Id used for this node.'))
@utils.arg('-c', '--cluster', metavar='<CLUSTER>',
           help=_('Cluster Id for this node.'))
@utils.arg('-r', '--role', metavar='<ROLE>',
           help=_('Role for this node in the specific cluster.'))
@utils.arg('-g', '--tags', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Tag values to be attached to the cluster. '
                  'This can be specified multiple times, or once with tags '
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


@utils.arg('-D', '--details', default=False, action="store_true",
           help=_('Include physical object details.'))
@utils.arg('id', metavar='<NODE>',
           help=_('Name or ID of the node to show the details for.'))
def do_node_show(sc, args):
    '''Show detailed info about the specified node.'''
    _show_node(sc, args.id, args.details)


@utils.arg('id', metavar='<NODE>', nargs='+',
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
                  'This can be specified multiple times, or once with tags '
                  'separated by a semicolon.'),
           action='append')
@utils.arg('id', metavar='<NODE>',
           help=_('Name or ID of node to update.'))
def do_node_update(sc, args):
    '''Update the node.'''
    # Find the node first, we need its UUID
    try:
        node = sc.get(models.Node, {'id': args.id})
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Node not found: %s') % args.id)

    params = {
        'id': node.id,
        'name': args.name,
        'role': args.role,
        'profile': args.profile,
        'tags': utils.format_parameters(args.tags),
    }

    sc.update(models.Node, params)
    _show_node(sc, node.id)


@utils.arg('-c', '--cluster', required=True,
           help=_('ID or name of cluster for node to join.'))
@utils.arg('id', metavar='<NODE>',
           help=_('Name or ID of node to operate on.'))
def do_node_join(sc, args):
    '''Make node join the specified cluster.'''
    params = {
        'id': args.id,
        'action': 'join',
        'action_args': {
            'cluster_id': args.cluster,
        }
    }
    resp = sc.action(models.Node, params)
    print('Request accepted by action %s' % resp['action'])
    _show_node(sc, args.id)


@utils.arg('id', metavar='<NODE>',
           help=_('Name or ID of node to operate on.'))
def do_node_leave(sc, args):
    '''Make node leave its current cluster.'''
    params = {
        'id': args.id,
        'action': 'leave',
    }
    resp = sc.action(models.Node, params)
    print('Request accepted by action %s' % resp['action'])
    _show_node(sc, args.id)


# EVENTS


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
@utils.arg('-g', '--global-tenant', default=False, action="store_true",
           help=_('Whether events from all projects(tenants) should be '
                  'listed. Default to False. Setting this to True may demand '
                  'for an admin privilege.'))
@utils.arg('-D', '--show-deleted', default=False, action="store_true",
           help=_('Whether deleted events should be listed as well. '
                  'Default to False.'))
def do_event_list(sc, args):
    '''List events.'''
    queries = {
        'filters': utils.format_parameters(args.filters),
        'sort_keys': args.sort_keys,
        'sort_dir': args.sort_dir,
        'limit': args.limit,
        'marker': args.marker,
        'global_tenant': args.global_tenant,
        'show_deleted': args.show_deleted,
    }

    try:
        events = sc.list(models.Event, **queries)
    except exc.HTTPNotFound as ex:
        raise exc.CommandError(str(ex))

    fields = ['id', 'timestamp', 'obj_type', 'obj_id', 'action', 'status',
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


# ACTIONS


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
        return obj.id[:8]

    def _short_target(obj):
        return obj.target[:8]

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


@utils.arg('id', metavar='<ACTION>',
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
