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

from openstack import exceptions as sdk_exc
from senlinclient.common import exc
from senlinclient.common.i18n import _
from senlinclient.common.i18n import _LW
from senlinclient.common import utils

logger = logging.getLogger(__name__)


def show_deprecated(deprecated, recommended):
    logger.warning(_LW('"%(old)s" is deprecated, '
                       'please use "%(new)s" instead.'),
                   {'old': deprecated,
                    'new': recommended}
                   )


def do_build_info(service, args=None):
    """Retrieve build information.

    :param sc: Instance of senlinclient.
    :param args: Additional command line arguments, if any.
    """
    show_deprecated('senlin build-info', 'openstack cluster build info')
    result = service.get_build_info()

    formatters = {
        'api': utils.json_formatter,
        'engine': utils.json_formatter,
    }
    utils.print_dict(result, formatters=formatters)


# PROFILE TYPES


def do_profile_type_list(service, args=None):
    """List the available profile types.

    :param sc: Instance of senlinclient.
    :param args: Additional command line arguments, if any.
    """
    show_deprecated('senlin profile-type-list',
                    'openstack cluster profile type list')
    types = service.profile_types()
    utils.print_list(types, ['name'], sortby_index=0)


@utils.arg('type_name', metavar='<TYPE_NAME>',
           help=_('Profile type to retrieve.'))
@utils.arg('-F', '--format', metavar='<FORMAT>',
           choices=utils.supported_formats.keys(),
           help=_("The template output format, one of: %s.")
                 % ', '.join(utils.supported_formats.keys()))
def do_profile_type_show(service, args):
    """Get the details about a profile type."""
    show_deprecated('senlin profile-type-show',
                    'openstack cluster profile type show')
    try:
        res = service.get_profile_type(args.type_name)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(
            _('Profile Type not found: %s') % args.type_name)

    pt = res.to_dict()

    if args.format:
        print(utils.format_output(pt, format=args.format))
    else:
        print(utils.format_output(pt))


# PROFILES

@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned profiles. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of profiles returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return profiles that appear after the given ID.'))
@utils.arg('-o', '--sort', metavar='<KEY:DIR>',
           help=_('Sorting option which is a string containing a list of keys '
                  'separated by commas. Each key can be optionally appended '
                  'by a sort direction (:asc or :desc)'))
@utils.arg('-g', '--global-project', default=False, action="store_true",
           help=_('Indicate that the list should include profiles from'
                  ' all projects. This option is subject to access policy '
                  'checking. Default is False.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_profile_list(service, args=None):
    """List profiles that meet the criteria."""
    show_deprecated('senlin profile-list', 'openstack cluster profile list')
    fields = ['id', 'name', 'type', 'created_at']
    queries = {
        'limit': args.limit,
        'marker': args.marker,
        'sort': args.sort,
        'global_project': args.global_project,
    }
    if args.filters:
        queries.update(utils.format_parameters(args.filters))

    sortby_index = None if args.sort else 1

    profiles = service.profiles(**queries)
    formatters = {}
    if not args.full_id:
        formatters = {
            'id': lambda x: x.id[:8],
        }
    utils.print_list(profiles, fields, formatters=formatters,
                     sortby_index=sortby_index)


def _show_profile(service, profile_id):
    try:
        profile = service.get_profile(profile_id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Profile not found: %s') % profile_id)

    formatters = {
        'metadata': utils.json_formatter,
    }

    formatters['spec'] = utils.nested_dict_formatter(
        ['type', 'version', 'properties'],
        ['property', 'value'])

    utils.print_dict(profile.to_dict(), formatters=formatters)


@utils.arg('-s', '--spec-file', metavar='<SPEC FILE>', required=True,
           help=_('The spec file used to create the profile.'))
@utils.arg('-M', '--metadata', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Metadata values to be attached to the profile. '
                  'This can be specified multiple times, or once with '
                  'key-value pairs separated by a semicolon.'),
           action='append')
@utils.arg('name', metavar='<PROFILE_NAME>',
           help=_('Name of the profile to create.'))
def do_profile_create(service, args):
    """Create a profile."""
    show_deprecated('senlin profile-create',
                    'openstack cluster profile create')
    spec = utils.get_spec_content(args.spec_file)
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
        stack_properties = utils.process_stack_spec(properties)
        spec['properties'] = stack_properties

    params = {
        'name': args.name,
        'spec': spec,
        'metadata': utils.format_parameters(args.metadata),
    }

    profile = service.create_profile(**params)
    _show_profile(service, profile.id)


@utils.arg('id', metavar='<PROFILE>',
           help=_('Name or ID of profile to show.'))
def do_profile_show(service, args):
    """Show the profile details."""
    show_deprecated('senlin profile-show', 'openstack cluster profile show')
    _show_profile(service, args.id)


@utils.arg('-n', '--name', metavar='<NAME>',
           help=_('The new name for the profile.'))
@utils.arg('-M', '--metadata', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Metadata values to be attached to the profile. '
                  'This can be specified multiple times, or once with '
                  'key-value pairs separated by a semicolon.'),
           action='append')
@utils.arg('id', metavar='<PROFILE_ID>',
           help=_('Name or ID of the profile to update.'))
def do_profile_update(service, args):
    """Update a profile."""
    show_deprecated('senlin profile-update',
                    'openstack cluster profile update')
    params = {
        'name': args.name,
    }
    if args.metadata:
        params['metadata'] = utils.format_parameters(args.metadata)

    # Find the profile first, we need its id
    try:
        profile = service.get_profile(args.id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Profile not found: %s') % args.id)
    service.update_profile(profile.id, **params)
    _show_profile(service, profile.id)


@utils.arg('id', metavar='<PROFILE>', nargs='+',
           help=_('Name or ID of profile(s) to delete.'))
def do_profile_delete(service, args):
    """Delete profile(s)."""
    show_deprecated('senlin profile-delete',
                    'openstack cluster profile delete')
    failure_count = 0

    for pid in args.id:
        try:
            service.delete_profile(pid, False)
        except Exception as ex:
            failure_count += 1
            print(ex)
    if failure_count > 0:
        msg = _('Failed to delete some of the specified profile(s).')
        raise exc.CommandError(msg)
    print('Profile deleted: %s' % args.id)


# POLICY TYPES


def do_policy_type_list(service, args):
    """List the available policy types."""
    show_deprecated('senlin policy-type-list',
                    'openstack cluster policy type list')
    types = service.policy_types()
    utils.print_list(types, ['name'], sortby_index=0)


@utils.arg('type_name', metavar='<TYPE_NAME>',
           help=_('Policy type to retrieve.'))
@utils.arg('-F', '--format', metavar='<FORMAT>',
           choices=utils.supported_formats.keys(),
           help=_("The template output format, one of: %s.")
                 % ', '.join(utils.supported_formats.keys()))
def do_policy_type_show(service, args):
    """Get the details about a policy type."""
    show_deprecated('senlin policy-type-show',
                    'openstack cluster policy type show')
    try:
        res = service.get_policy_type(args.type_name)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Policy type not found: %s') % args.type_name)

    pt = res.to_dict()
    if args.format:
        print(utils.format_output(pt, format=args.format))
    else:
        print(utils.format_output(pt))


# POLICIES

@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned policies. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of policies returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return policies that appear after the given ID.'))
@utils.arg('-o', '--sort', metavar='<KEY:DIR>',
           help=_('Sorting option which is a string containing a list of keys '
                  'separated by commas. Each key can be optionally appended '
                  'by a sort direction (:asc or :desc)'))
@utils.arg('-g', '--global-project', default=False, action="store_true",
           help=_('Indicate that the list should include policies from'
                  ' all projects. This option is subject to access policy '
                  'checking. Default is False.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_policy_list(service, args=None):
    """List policies that meet the criteria."""
    show_deprecated('senlin policy-list', 'openstack cluster policy list')
    fields = ['id', 'name', 'type', 'created_at']
    queries = {
        'limit': args.limit,
        'marker': args.marker,
        'sort': args.sort,
        'global_project': args.global_project,
    }
    if args.filters:
        queries.update(utils.format_parameters(args.filters))

    sortby_index = None if args.sort else 1
    policies = service.policies(**queries)
    formatters = {}
    if not args.full_id:
        formatters = {
            'id': lambda x: x.id[:8]
        }
    utils.print_list(policies, fields, formatters=formatters,
                     sortby_index=sortby_index)


def _show_policy(service, policy_id):
    try:
        policy = service.get_policy(policy_id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Policy not found: %s') % policy_id)

    formatters = {
        'metadata': utils.json_formatter,
        'spec': utils.json_formatter,
    }
    utils.print_dict(policy.to_dict(), formatters=formatters)


@utils.arg('-s', '--spec-file', metavar='<SPEC_FILE>', required=True,
           help=_('The spec file used to create the policy.'))
@utils.arg('name', metavar='<NAME>',
           help=_('Name of the policy to create.'))
def do_policy_create(service, args):
    """Create a policy."""
    show_deprecated('senlin policy-create', 'openstack cluster policy create')
    spec = utils.get_spec_content(args.spec_file)
    attrs = {
        'name': args.name,
        'spec': spec,
    }

    policy = service.create_policy(**attrs)
    _show_policy(service, policy.id)


@utils.arg('id', metavar='<POLICY>',
           help=_('Name of the policy to be updated.'))
def do_policy_show(service, args):
    """Show the policy details."""
    show_deprecated('senlin policy-show', 'openstack cluster policy show')
    _show_policy(service, policy_id=args.id)


@utils.arg('-n', '--name', metavar='<NAME>',
           help=_('New name of the policy to be updated.'))
@utils.arg('id', metavar='<POLICY>',
           help=_('Name of the policy to be updated.'))
def do_policy_update(service, args):
    """Update a policy."""
    show_deprecated('senlin policy-update', 'openstack cluster policy update')
    params = {
        'name': args.name,
    }

    policy = service.get_policy(args.id)
    if policy is not None:
        service.update_policy(policy.id, **params)
        _show_policy(service, policy_id=policy.id)


@utils.arg('id', metavar='<POLICY>', nargs='+',
           help=_('Name or ID of policy(s) to delete.'))
def do_policy_delete(service, args):
    """Delete policy(s)."""
    show_deprecated('senlin policy-delete', 'openstack cluster policy delete')
    failure_count = 0

    for pid in args.id:
        try:
            service.delete_policy(pid, False)
        except Exception as ex:
            failure_count += 1
            print(ex)
    if failure_count > 0:
        msg = _('Failed to delete some of the specified policy(s).')
        raise exc.CommandError(msg)
    print('Policy deleted: %s' % args.id)


# CLUSTERS


@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned clusters. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-o', '--sort', metavar='<KEY:DIR>',
           help=_('Sorting option which is a string containing a list of keys '
                  'separated by commas. Each key can be optionally appended '
                  'by a sort direction (:asc or :desc)'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of clusters returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return clusters that appear after the given cluster '
                  'ID.'))
@utils.arg('-g', '--global-project', default=False, action="store_true",
           help=_('Indicate that the cluster list should include clusters from'
                  ' all projects. This option is subject to access policy '
                  'checking. Default is False.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_cluster_list(service, args=None):
    """List the user's clusters."""
    show_deprecated('senlin cluster-list', 'openstack cluster list')
    fields = ['id', 'name', 'status', 'created_at', 'updated_at']
    queries = {
        'limit': args.limit,
        'marker': args.marker,
        'sort': args.sort,
        'global_project': args.global_project,
    }
    if args.filters:
        queries.update(utils.format_parameters(args.filters))

    sortby_index = None if args.sort else 3

    clusters = service.clusters(**queries)
    formatters = {}
    if not args.full_id:
        formatters = {
            'id': lambda x: x.id[:8]
        }
    utils.print_list(clusters, fields, formatters=formatters,
                     sortby_index=sortby_index)


def _show_cluster(service, cluster_id):
    try:
        cluster = service.get_cluster(cluster_id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Cluster not found: %s') % cluster_id)

    formatters = {
        'metadata': utils.json_formatter,
        'nodes': utils.list_formatter,
    }
    utils.print_dict(cluster.to_dict(), formatters=formatters)


@utils.arg('-p', '--profile', metavar='<PROFILE>', required=True,
           help=_('Profile Id used for this cluster.'))
@utils.arg('-n', '--min-size', metavar='<MIN-SIZE>', default=0,
           help=_('Min size of the cluster. Default to 0.'))
@utils.arg('-m', '--max-size', metavar='<MAX-SIZE>', default=-1,
           help=_('Max size of the cluster. Default to -1, means unlimited.'))
@utils.arg('-c', '--desired-capacity', metavar='<DESIRED-CAPACITY>', default=0,
           help=_('Desired capacity of the cluster. Default to min_size if '
                  'min_size is specified else 0.'))
@utils.arg('-t', '--timeout', metavar='<TIMEOUT>', type=int,
           help=_('Cluster creation timeout in seconds.'))
@utils.arg('-M', '--metadata', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Metadata values to be attached to the cluster. '
                  'This can be specified multiple times, or once with '
                  'key-value pairs separated by a semicolon.'),
           action='append')
@utils.arg('name', metavar='<CLUSTER_NAME>',
           help=_('Name of the cluster to create.'))
def do_cluster_create(service, args):
    """Create the cluster."""
    show_deprecated('senlin cluster-create', 'openstack cluster create')
    if args.min_size and not args.desired_capacity:
        args.desired_capacity = args.min_size
    attrs = {
        'name': args.name,
        'profile_id': args.profile,
        'min_size': args.min_size,
        'max_size': args.max_size,
        'desired_capacity': args.desired_capacity,
        'metadata': utils.format_parameters(args.metadata),
        'timeout': args.timeout
    }

    cluster = service.create_cluster(**attrs)
    _show_cluster(service, cluster.id)


@utils.arg('id', metavar='<CLUSTER>', nargs='+',
           help=_('Name or ID of cluster(s) to delete.'))
def do_cluster_delete(service, args):
    """Delete the cluster(s)."""
    show_deprecated('senlin cluster-delete', 'openstack cluster delete')
    failure_count = 0

    for cid in args.id:
        try:
            service.delete_cluster(cid, False)
        except Exception as ex:
            failure_count += 1
            print(ex)
    if failure_count > 0:
        msg = _('Failed to delete some of the specified clusters.')
        raise exc.CommandError(msg)
    print('Request accepted')


@utils.arg('-p', '--profile', metavar='<PROFILE>',
           help=_('ID of new profile to use.'))
@utils.arg('-t', '--timeout', metavar='<TIMEOUT>',
           help=_('New timeout (in seconds) value for the cluster.'))
@utils.arg('-M', '--metadata', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Metadata values to be attached to the cluster. '
                  'This can be specified multiple times, or once with '
                  'key-value pairs separated by a semicolon.'),
           action='append')
@utils.arg('-n', '--name', metavar='<NAME>',
           help=_('New name for the cluster to update.'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to be updated.'))
def do_cluster_update(service, args):
    """Update the cluster."""
    show_deprecated('senlin cluster-update', 'openstack cluster update')
    cluster = service.get_cluster(args.id)
    attrs = {
        'name': args.name,
        'profile_id': args.profile,
        'metadata': utils.format_parameters(args.metadata),
        'timeout': args.timeout,
    }

    service.update_cluster(cluster.id, **attrs)
    _show_cluster(service, cluster.id)


@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to show.'))
def do_cluster_show(service, args):
    """Show details of the cluster."""
    show_deprecated('senlin cluster-show', 'openstack cluster show')
    _show_cluster(service, args.id)


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
def do_cluster_node_list(service, args):
    """List nodes from cluster."""
    show_deprecated('senlin cluster-node-list',
                    'openstack cluster node members list')
    queries = {
        'cluster_id': args.id,
        'limit': args.limit,
        'marker': args.marker,
    }
    if args.filters:
        queries.update(utils.format_parameters(args.filters))

    nodes = service.nodes(**queries)
    if not args.full_id:
        formatters = {
            'id': lambda x: x.id[:8],
            'physical_id': lambda x: x.physical_id[:8] if x.physical_id else ''
        }
    else:
        formatters = {}

    fields = ['id', 'name', 'index', 'status', 'physical_id', 'created_at']
    utils.print_list(nodes, fields, formatters=formatters, sortby_index=5)


@utils.arg('-n', '--nodes', metavar='<NODES>', required=True,
           help=_('ID of nodes to be added; multiple nodes can be separated '
                  'with ","'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_node_add(service, args):
    """Add specified nodes to cluster."""
    show_deprecated('senlin cluster-node-add',
                    'openstack cluster node members add')
    node_ids = args.nodes.split(',')
    resp = service.cluster_add_nodes(args.id, node_ids)
    print('Request accepted by action: %s' % resp['action'])


@utils.arg('-n', '--nodes', metavar='<NODES>', required=True,
           help=_('ID of nodes to be deleted; multiple nodes can be separated '
                  'with ",".'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_node_del(service, args):
    """Delete specified nodes from cluster."""
    show_deprecated('senlin cluster-node-del',
                    'openstack cluster node members del')
    node_ids = args.nodes.split(',')
    resp = service.cluster_del_nodes(args.id, node_ids)
    print('Request accepted by action: %s' % resp['action'])


@utils.arg('-c', '--capacity', metavar='<CAPACITY>', type=int,
           help=_('The desired number of nodes of the cluster.'))
@utils.arg('-a', '--adjustment', metavar='<ADJUSTMENT>', type=int,
           help=_('A positive integer meaning the number of nodes to add, '
                  'or a negative integer indicating the number of nodes to '
                  'remove.'))
@utils.arg('-p', '--percentage', metavar='<PERCENTAGE>', type=float,
           help=_('A value that is interpreted as the percentage of size '
                  'adjustment. This value can be positive or negative.'))
@utils.arg('-t', '--min-step', metavar='<MIN_STEP>', type=int,
           help=_('An integer specifying the number of nodes for adjustment '
                  'when <PERCENTAGE> is specified.'))
@utils.arg('-s', '--strict',  action='store_true', default=False,
           help=_('A boolean specifying whether the resize should be '
                  'performed on a best-effort basis when the new capacity '
                  'may go beyond size constraints.'))
@utils.arg('-n', '--min-size', metavar='MIN', type=int,
           help=_('New lower bound of cluster size.'))
@utils.arg('-m', '--max-size', metavar='MAX', type=int,
           help=_('New upper bound of cluster size. A value of -1 indicates '
                  'no upper limit on cluster size.'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_resize(service, args):
    """Resize a cluster."""
    # validate parameters
    # NOTE: this will be much simpler if cliutils supports exclusive groups
    show_deprecated('senlin cluster-resize', 'openstack cluster resize')
    action_args = {}

    capacity = args.capacity
    adjustment = args.adjustment
    percentage = args.percentage
    min_size = args.min_size
    max_size = args.max_size
    min_step = args.min_step

    if sum(v is not None for v in (capacity, adjustment, percentage)) > 1:
        raise exc.CommandError(_("Only one of 'capacity', 'adjustment' and "
                                 "'percentage' can be specified."))

    action_args['adjustment_type'] = None
    action_args['number'] = None

    if capacity is not None:
        if capacity < 0:
            raise exc.CommandError(_('Cluster capacity must be larger than '
                                     ' or equal to zero.'))
        action_args['adjustment_type'] = 'EXACT_CAPACITY'
        action_args['number'] = capacity

    if adjustment is not None:
        if adjustment == 0:
            raise exc.CommandError(_('Adjustment cannot be zero.'))
        action_args['adjustment_type'] = 'CHANGE_IN_CAPACITY'
        action_args['number'] = adjustment

    if percentage is not None:
        if (percentage == 0 or percentage == 0.0):
            raise exc.CommandError(_('Percentage cannot be zero.'))
        action_args['adjustment_type'] = 'CHANGE_IN_PERCENTAGE'
        action_args['number'] = percentage

    if min_step is not None:
        if percentage is None:
            raise exc.CommandError(_('Min step is only used with percentage.'))

    if min_size is not None:
        if min_size < 0:
            raise exc.CommandError(_('Min size cannot be less than zero.'))
        if max_size is not None and max_size >= 0 and min_size > max_size:
            raise exc.CommandError(_('Min size cannot be larger than '
                                     'max size.'))
        if capacity is not None and min_size > capacity:
            raise exc.CommandError(_('Min size cannot be larger than the '
                                     'specified capacity'))

    if max_size is not None:
        if capacity is not None and max_size > 0 and max_size < capacity:
            raise exc.CommandError(_('Max size cannot be less than the '
                                     'specified capacity.'))
        # do a normalization
        if max_size < 0:
            max_size = -1

    action_args['min_size'] = min_size
    action_args['max_size'] = max_size
    action_args['min_step'] = min_step
    action_args['strict'] = args.strict

    resp = service.cluster_resize(args.id, **action_args)
    print('Request accepted by action: %s' % resp['action'])


@utils.arg('-c', '--count', metavar='<COUNT>',
           help=_('Number of nodes to be added to the specified cluster.'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_scale_out(service, args):
    """Scale out a cluster by the specified number of nodes."""
    show_deprecated('senlin cluster-scale-out', 'openstack cluster scale out')
    resp = service.cluster_scale_out(args.id, args.count)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-c', '--count', metavar='<COUNT>',
           help=_('Number of nodes to be deleted from the specified cluster.'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_scale_in(service, args):
    """Scale in a cluster by the specified number of nodes."""
    show_deprecated('senlin cluster-scale-in', 'openstack cluster scale in')
    resp = service.cluster_scale_in(args.id, args.count)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned results. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-o', '--sort', metavar='<SORT_STRING>',
           help=_('Sorting option which is a string containing a list of keys '
                  'separated by commas. Each key can be optionally appended '
                  'by a sort direction (:asc or :desc)'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('Name or ID of cluster to query on.'))
def do_cluster_policy_list(service, args):
    """List policies from cluster."""
    show_deprecated('senlin cluster-policy-list',
                    'openstack cluster policy binding list')
    fields = ['policy_id', 'policy_name', 'policy_type', 'enabled']

    cluster = service.get_cluster(args.id)
    queries = {
        'sort': args.sort,
    }

    if args.filters:
        queries.update(utils.format_parameters(args.filters))

    sortby_index = None if args.sort else 3
    policies = service.cluster_policies(cluster.id, **queries)
    formatters = {}
    if not args.full_id:
        formatters = {
            'policy_id': lambda x: x.id[:8]
        }

    utils.print_list(policies, fields, formatters=formatters,
                     sortby_index=sortby_index)


@utils.arg('-p', '--policy', metavar='<POLICY>', required=True,
           help=_('ID or name of the policy to query on.'))
@utils.arg('id', metavar='<CLUSTER>',
           help=_('ID or name of the cluster to query on.'))
def do_cluster_policy_show(service, args):
    """Show a specific policy that is bound to the specified cluster."""
    show_deprecated('senlin cluster-policy-show',
                    'openstack cluster policy binding show')
    binding = service.get_cluster_policy(args.policy, args.id)
    utils.print_dict(binding.to_dict())


@utils.arg('-p', '--policy', metavar='<POLICY>', required=True,
           help=_('ID or name of policy to be attached.'))
@utils.arg('-e', '--enabled', default=True, action="store_true",
           help=_('Whether the policy should be enabled once attached. '
                  'Default to enabled.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_attach(service, args):
    """Attach policy to cluster."""
    show_deprecated('senlin cluster-policy-attach',
                    'openstack cluster policy attach')
    kwargs = {
        'enabled': args.enabled,
    }

    resp = service.cluster_attach_policy(args.id, args.policy, **kwargs)
    print('Request accepted by action: %s' % resp['action'])


@utils.arg('-p', '--policy', metavar='<POLICY>', required=True,
           help=_('ID or name of policy to be detached.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_detach(service, args):
    """Detach policy from cluster."""
    show_deprecated('senlin cluster-policy-detach',
                    'openstack cluster policy detach')
    resp = service.cluster_detach_policy(args.id, args.policy)
    print('Request accepted by action %s' % resp['action'])


@utils.arg('-p', '--policy', metavar='<POLICY>', required=True,
           help=_('ID or name of policy to be updated.'))
@utils.arg('-e', '--enabled', metavar='<BOOLEAN>',
           help=_('Whether the policy should be enabled.'))
@utils.arg('id', metavar='<NAME or ID>',
           help=_('Name or ID of cluster to operate on.'))
def do_cluster_policy_update(service, args):
    """Update a policy's properties on a cluster."""
    show_deprecated('senlin cluster-policy-update',
                    'openstack cluster policy binding update')
    kwargs = {
        'enabled': args.enabled,
    }

    resp = service.cluster_update_policy(args.id, args.policy, **kwargs)
    print('Request accepted by action: %s' % resp['action'])


@utils.arg('id', metavar='<CLUSTER>', nargs='+',
           help=_('ID or name of cluster(s) to operate on.'))
def do_cluster_check(service, args):
    """Check the cluster(s)."""
    show_deprecated('senlin cluster-check', 'openstack cluster check')
    for cid in args.id:
        resp = service.check_cluster(cid)
        print('Cluster check request on cluster %(cid)s is accepted by '
              'action %(action)s.' % {'cid': cid, 'action': resp['action']})


@utils.arg('id', metavar='<CLUSTER>', nargs='+',
           help=_('ID or name of cluster(s) to operate on.'))
def do_cluster_recover(service, args):
    """Recover the cluster(s)."""
    show_deprecated('senlin cluster-recover', 'openstack cluster recover')
    for cid in args.id:
        resp = service.recover_cluster(cid)
        print('Cluster recover request on cluster %(cid)s is accepted by '
              'action %(action)s.' % {'cid': cid, 'action': resp['action']})


# NODES


@utils.arg('-c', '--cluster', metavar='<CLUSTER>',
           help=_('ID or name of cluster from which nodes are to be listed.'))
@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned nodes. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-o', '--sort', metavar='<KEY:DIR>',
           help=_('Sorting option which is a string containing a list of keys '
                  'separated by commas. Each key can be optionally appended '
                  'by a sort direction (:asc or :desc)'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of nodes returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return nodes that appear after the given node ID.'))
@utils.arg('-g', '--global-project', default=False, action="store_true",
           help=_('Indicate that this node list should include nodes from '
                  'all projects. This option is subject to access policy '
                  'checking. Default is False.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_node_list(service, args):
    """Show list of nodes."""
    show_deprecated('senlin node-list', 'openstack cluster node list')

    fields = ['id', 'name', 'index', 'status', 'cluster_id', 'physical_id',
              'profile_name', 'created_at', 'updated_at']
    queries = {
        'cluster_id': args.cluster,
        'sort': args.sort,
        'limit': args.limit,
        'marker': args.marker,
        'global_project': args.global_project,
    }

    if args.filters:
        queries.update(utils.format_parameters(args.filters))

    sortby_index = None if args.sort else 6

    nodes = service.nodes(**queries)

    if not args.full_id:
        formatters = {
            'id': lambda x: x.id[:8],
            'cluster_id': lambda x: x.cluster_id[:8] if x.cluster_id else '',
            'physical_id': lambda x: x.physical_id[:8] if x.physical_id else ''
        }
    else:
        formatters = {}

    utils.print_list(nodes, fields, formatters=formatters,
                     sortby_index=sortby_index)


def _show_node(service, node_id, show_details=False):
    """Show detailed info about the specified node."""
    args = {'show_details': True} if show_details else None
    try:
        node = service.get_node(node_id, args=args)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Node not found: %s') % node_id)

    formatters = {
        'metadata': utils.json_formatter,
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
@utils.arg('-M', '--metadata', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Metadata values to be attached to the node. '
                  'This can be specified multiple times, or once with '
                  'key-value pairs separated by a semicolon.'),
           action='append')
@utils.arg('name', metavar='<NODE_NAME>',
           help=_('Name of the node to create.'))
def do_node_create(service, args):
    """Create the node."""
    show_deprecated('senlin node-create', 'openstack cluster node create')
    attrs = {
        'name': args.name,
        'cluster_id': args.cluster,
        'profile_id': args.profile,
        'role': args.role,
        'metadata': utils.format_parameters(args.metadata),
    }

    node = service.create_node(**attrs)
    _show_node(service, node.id)


@utils.arg('-D', '--details', default=False, action="store_true",
           help=_('Include physical object details.'))
@utils.arg('id', metavar='<NODE>',
           help=_('Name or ID of the node to show the details for.'))
def do_node_show(service, args):
    """Show detailed info about the specified node."""
    show_deprecated('senlin node-show', 'openstack cluster node show')
    _show_node(service, args.id, args.details)


@utils.arg('id', metavar='<NODE>', nargs='+',
           help=_('Name or ID of node(s) to delete.'))
def do_node_delete(service, args):
    """Delete the node(s)."""
    show_deprecated('senlin node-delete', 'openstack cluster node delete')
    failure_count = 0

    for nid in args.id:
        try:
            service.delete_node(nid, False)
        except Exception as ex:
            failure_count += 1
            print(ex)
    if failure_count > 0:
        msg = _('Failed to delete some of the specified nodes.')
        raise exc.CommandError(msg)
    print('Request accepted')


@utils.arg('-n', '--name', metavar='<NAME>',
           help=_('New name for the node.'))
@utils.arg('-p', '--profile', metavar='<PROFILE ID>',
           help=_('ID of new profile to use.'))
@utils.arg('-r', '--role', metavar='<ROLE>',
           help=_('Role for this node in the specific cluster.'))
@utils.arg('-M', '--metadata', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Metadata values to be attached to the node. '
                  'Metadata can be specified multiple times, or once with '
                  'key-value pairs separated by a semicolon.'),
           action='append')
@utils.arg('id', metavar='<NODE>',
           help=_('Name or ID of node to update.'))
def do_node_update(service, args):
    """Update the node."""
    show_deprecated('senlin node-update', 'openstack cluster node update')
    # Find the node first, we need its UUID
    try:
        node = service.get_node(args.id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Node not found: %s') % args.id)

    attrs = {
        'name': args.name,
        'role': args.role,
        'profile_id': args.profile,
        'metadata': utils.format_parameters(args.metadata),
    }

    service.update_node(args.id, **attrs)
    _show_node(service, node.id)


@utils.arg('id', metavar='<NODE>', nargs='+',
           help=_('ID of node(s) to check.'))
def do_node_check(service, args):
    """Check the node(s)."""
    show_deprecated('senlin node-check', 'openstack cluster node check')
    failure_count = 0

    for nid in args.id:
        try:
            service.check_node(nid)
        except exc.HTTPNotFound:
            failure_count += 1
            print('Node id "%s" not found' % nid)
    if failure_count > 0:
        msg = _('Failed to check some of the specified nodes.')
        raise exc.CommandError(msg)
    print('Request accepted')


@utils.arg('id', metavar='<NODE>', nargs='+',
           help=_('ID of node(s) to recover.'))
def do_node_recover(service, args):
    """Recover the node(s)."""
    show_deprecated('senlin node-recover', 'openstack cluster node recover')
    failure_count = 0

    for nid in args.id:
        try:
            service.recover_node(nid)
        except exc.HTTPNotFound:
            failure_count += 1
            print('Node id "%s" not found' % nid)
    if failure_count > 0:
        msg = _('Failed to recover some of the specified nodes.')
        raise exc.CommandError(msg)
    print('Request accepted')


# RECEIVERS


@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned receivers. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of receivers returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return receivers that appear after the given ID.'))
@utils.arg('-o', '--sort', metavar='<KEY:DIR>',
           help=_('Sorting option which is a string containing a list of keys '
                  'separated by commas. Each key can be optionally appended '
                  'by a sort direction (:asc or :desc)'))
@utils.arg('-g', '--global-project', default=False, action="store_true",
           help=_('Indicate that the list should include receivers from'
                  ' all projects. This option is subject to access policy '
                  'checking. Default is False.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_receiver_list(service, args):
    """List receivers that meet the criteria."""
    show_deprecated('senlin receiver-list', 'openstack cluster receiver list')
    fields = ['id', 'name', 'type', 'cluster_id', 'action', 'created_at']
    queries = {
        'limit': args.limit,
        'marker': args.marker,
        'sort': args.sort,
        'global_project': args.global_project,
    }

    if args.filters:
        queries.update(utils.format_parameters(args.filters))

    sortby_index = None if args.sort else 0

    receivers = service.receivers(**queries)
    formatters = {}
    if not args.full_id:
        formatters = {
            'id': lambda x: x.id[:8],
            'cluster_id': lambda x: x.cluster_id[:8],
        }
    utils.print_list(receivers, fields, formatters=formatters,
                     sortby_index=sortby_index)


def _show_receiver(service, receiver_id):
    try:
        receiver = service.get_receiver(receiver_id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Receiver not found: %s') % receiver_id)

    formatters = {
        'actor': utils.json_formatter,
        'params': utils.json_formatter,
        'channel': utils.json_formatter,
    }

    utils.print_dict(receiver.to_dict(), formatters=formatters)


@utils.arg('id', metavar='<RECEIVER>',
           help=_('Name or ID of the receiver to show.'))
def do_receiver_show(service, args):
    """Show the receiver details."""
    show_deprecated('senlin receiver-show', 'openstack cluster receiver show')
    _show_receiver(service, receiver_id=args.id)


@utils.arg('-t', '--type', metavar='<TYPE>', default='webhook',
           help=_('Type of the receiver to create.'))
@utils.arg('-c', '--cluster', metavar='<CLUSTER>', required=True,
           help=_('Targeted cluster for this receiver.'))
@utils.arg('-a', '--action', metavar='<ACTION>', required=True,
           help=_('Name or ID of the targeted action to be triggered.'))
@utils.arg('-P', '--params', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('A dictionary of parameters that will be passed to target '
                  'action when the receiver is triggered.'),
           action='append')
@utils.arg('name', metavar='<NAME>',
           help=_('Name of the receiver to create.'))
def do_receiver_create(service, args):
    """Create a receiver."""
    show_deprecated('senlin receiver-create',
                    'openstack cluster receiver create')

    params = {
        'name': args.name,
        'type': args.type,
        'cluster_id': args.cluster,
        'action': args.action,
        'params': utils.format_parameters(args.params)
    }

    receiver = service.create_receiver(**params)
    _show_receiver(service, receiver.id)


@utils.arg('id', metavar='<RECEIVER>', nargs='+',
           help=_('Name or ID of receiver(s) to delete.'))
def do_receiver_delete(service, args):
    """Delete receiver(s)."""
    show_deprecated('senlin receiver-delete',
                    'openstack cluster receiver delete')
    failure_count = 0

    for wid in args.id:
        try:
            service.delete_receiver(wid, False)
        except Exception as ex:
            failure_count += 1
            print(ex)
    if failure_count > 0:
        msg = _('Failed to delete some of the specified receiver(s).')
        raise exc.CommandError(msg)
    print('Receivers deleted: %s' % args.id)


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
@utils.arg('-o', '--sort', metavar='<KEY:DIR>',
           help=_('Sorting option which is a string containing a list of keys '
                  'separated by commas. Each key can be optionally appended '
                  'by a sort direction (:asc or :desc)'))
@utils.arg('-g', '--global-project', default=False, action="store_true",
           help=_('Whether events from all projects should be listed. '
                  ' Default to False. Setting this to True may demand '
                  'for an admin privilege.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_event_list(service, args):
    """List events."""
    show_deprecated('senlin event-list', 'openstack cluster event list')
    fields = ['id', 'timestamp', 'obj_type', 'obj_id', 'obj_name', 'action',
              'status', 'status_reason', 'level']
    queries = {
        'sort': args.sort,
        'limit': args.limit,
        'marker': args.marker,
        'global_project': args.global_project,
    }

    if args.filters:
        queries.update(utils.format_parameters(args.filters))

    formatters = {}
    if not args.full_id:
        formatters['id'] = lambda x: x.id[:8]
        formatters['obj_id'] = lambda x: x.obj_id[:8] if x.obj_id else ''

    events = service.events(**queries)
    utils.print_list(events, fields, formatters=formatters)


@utils.arg('id', metavar='<EVENT>',
           help=_('ID of event to display details for.'))
def do_event_show(service, args):
    """Describe the event."""
    show_deprecated('senlin event-show', 'openstack cluster event show')
    try:
        event = service.get_event(args.id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_("Event not found: %s") % args.id)

    utils.print_dict(event.to_dict())


# ACTIONS


@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned actions. '
                  'This can be specified multiple times, or once with '
                  'parameters separated by a semicolon.'),
           action='append')
@utils.arg('-o', '--sort', metavar='<KEY:DIR>',
           help=_('Sorting option which is a string containing a list of keys '
                  'separated by commas. Each key can be optionally appended '
                  'by a sort direction (:asc or :desc)'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of actions returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return actions that appear after the given node ID.'))
@utils.arg('-F', '--full-id', default=False, action="store_true",
           help=_('Print full IDs in list.'))
def do_action_list(service, args):
    """List actions."""
    show_deprecated('senlin action-list', 'openstack cluster action list')
    fields = ['id', 'name', 'action', 'status', 'target', 'depends_on',
              'depended_by', 'created_at']

    queries = {
        'sort': args.sort,
        'limit': args.limit,
        'marker': args.marker,
    }

    if args.filters:
        queries.update(utils.format_parameters(args.filters))

    sortby_index = None if args.sort else 0

    actions = service.actions(**queries)

    formatters = {}
    if args.full_id:
        f_depon = lambda x: '\n'.join(a for a in x.depends_on)
        f_depby = lambda x: '\n'.join(a for a in x.depended_by)

        formatters['depends_on'] = f_depon
        formatters['depended_by'] = f_depby
    else:
        formatters['id'] = lambda x: x.id[:8]
        formatters['target'] = lambda x: x.target[:8]
        f_depon = lambda x: '\n'.join(a[:8] for a in x.depends_on)
        f_depby = lambda x: '\n'.join(a[:8] for a in x.depended_by)
        formatters['depends_on'] = f_depon
        formatters['depended_by'] = f_depby

    utils.print_list(actions, fields, formatters=formatters,
                     sortby_index=sortby_index)


@utils.arg('id', metavar='<ACTION>',
           help=_('Name or ID of the action to show the details for.'))
def do_action_show(service, args):
    """Show detailed info about the specified action."""
    show_deprecated('senlin action-show', 'openstack cluster action show')
    try:
        action = service.get_action(args.id)
    except sdk_exc.ResourceNotFound:
        raise exc.CommandError(_('Action not found: %s') % args.id)

    formatters = {
        'inputs': utils.json_formatter,
        'outputs': utils.json_formatter,
        'metadata': utils.json_formatter,
        'data': utils.json_formatter,
        'depends_on': utils.list_formatter,
        'depended_by': utils.list_formatter,
    }

    utils.print_dict(action.to_dict(), formatters=formatters)
