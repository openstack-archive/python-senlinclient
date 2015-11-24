# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import inspect
from openstack.identity import identity_service

from senlinclient.common import exc as client_exc
from senlinclient.common import sdk
from senlinclient.v1 import models


class Client(object):

    def __init__(self, preferences=None, user_agent=None, **kwargs):
        if 'session' in kwargs:
            session = kwargs['session']
        else:
            conn = sdk.create_connection(preferences, user_agent, **kwargs)
            session = conn.session

        self.session = session

    ######################################################################
    # The following operations are interfaces exposed to other software
    # which invokes senlinclient today.
    # These methods form a temporary translation layer. This layer will be
    # useless when OpenStackSDK has adopted all senlin resources.
    ######################################################################

    def get_build_info(self, **kwargs):
        return self.get(models.BuildInfo)

    def profile_types(self, **kwargs):
        return self.list(models.ProfileType, paginated=False)

    def get_profile_type_schema(self, value):
        params = {'profile_type': value}
        return self.get(models.ProfileTypeSchema, params)

    def profiles(self, **queries):
        return self.list(models.Profile, **queries)

    def create_profile(self, **attrs):
        return self.create(models.Profile, attrs)

    def get_profile(self, value):
        return self.get(models.Profile, dict(id=value))

    def update_profile(self, value, **attrs):
        return self.update(models.Profile, attrs)

    def delete_profile(self, value, ignore_missing=True):
        return self.delete(models.Profile,
                           dict(id=value, ignore_missing=ignore_missing))

    def policy_types(self, **kwargs):
        return self.list(models.PolicyType, paginated=False)

    def get_policy_type_schema(self, value):
        params = {'policy_type': value}
        return self.get(models.PolicyTypeSchema, params)

    def webhooks(self, **queries):
        return self.list(models.Webhook, **queries)

    def create_webhook(self, **attrs):
        return self.create(models.Webhook, attrs, extra_attrs=True)

    def get_webhook(self, value):
        return self.get(models.Webhook, dict(id=value))

    def delete_webhook(self, value, ignore_missing=True):
        return self.delete(models.Webhook,
                           dict(id=value, ignore_missing=ignore_missing))

    def policies(self, **queries):
        return self.list(models.Policy, **queries)

    def create_policy(self, **attrs):
        return self.create(models.Policy, attrs)

    def get_policy(self, value):
        return self.get(models.Policy, dict(id=value))

    def update_policy(self, value, **attrs):
        attrs['id'] = value
        return self.update(models.Policy, attrs)

    def delete_policy(self, value, ignore_missing=True):
        return self.delete(models.Policy,
                           dict(id=value, ignore_missing=ignore_missing))

    def clusters(self, **queries):
        return self.list(models.Cluster, **queries)

    def create_cluster(self, **attrs):
        return self.create(models.Cluster, attrs)

    def get_cluster(self, value):
        return self.get(models.Cluster, dict(id=value))

    def update_cluster(self, value, **attrs):
        attrs['id'] = value
        return self.update(models.Cluster, attrs)

    def delete_cluster(self, value, ignore_missing=True):
        return self.delete(models.Cluster,
                           dict(id=value, ignore_missing=ignore_missing))

    def cluster_add_nodes(self, value, nodes):
        params = {
            'id': value,
            'action': 'add_nodes',
            'action_args': {
                'nodes': nodes,
            }
        }
        return self.action(models.Cluster, params)

    def cluster_del_nodes(self, value, nodes):
        params = {
            'id': value,
            'action': 'del_nodes',
            'action_args': {
                'nodes': nodes,
            }
        }
        return self.action(models.Cluster, params)

    def cluster_resize(self, value, **kwargs):
        params = {
            'id': value,
            'action': 'resize',
            'action_args': kwargs,
        }
        return self.action(models.Cluster, params)

    def cluster_scale_out(self, value, count):
        params = {
            'id': value,
            'action': 'scale_out',
            'action_args': {
                'count': count
            }
        }
        return self.action(models.Cluster, params)

    def cluster_scale_in(self, value, count):
        params = {
            'id': value,
            'action': 'scale_in',
            'action_args': {
                'count': count
            }
        }
        return self.action(models.Cluster, params)

    def cluster_policies(self, value, **queries):
        return self.list(models.ClusterPolicy, path_args={'cluster_id': value},
                         **queries)

    def get_cluster_policy(self, value):
        return self.get(models.ClusterPolicy, value)

    def cluster_attach_policy(self, value, **kwargs):
        params = {
            'id': value,
            'action': 'policy_attach',
            'action_args': kwargs
        }
        return self.action(models.Cluster, params)

    def cluster_detach_policy(self, value, policy):
        params = {
            'id': value,
            'action': 'policy_detach',
            'action_args': {
                'policy_id': policy,
            }
        }
        return self.action(models.Cluster, params)

    def cluster_update_policy(self, value, **attrs):
        params = {
            'id': value,
            'action': 'policy_update',
            'action_args': attrs
        }
        return self.action(models.Cluster, params)

    def cluster_enable_policy(self, value, policy):
        params = {
            'id': value,
            'action': 'policy_enable',
            'action_args': {
                'policy_id': policy
            }
        }
        return self.action(models.Cluster, params)

    def cluster_disable_policy(self, value, policy):
        params = {
            'id': value,
            'action': 'policy_disable',
            'action_args': {
                'policy_id': policy
            }
        }
        return self.action(models.Cluster, params)

    def nodes(self, **queries):
        return self.list(models.Node, **queries)

    def create_node(self, **attrs):
        return self.create(models.Node, attrs)

    def get_node(self, value, show_details=False):
        return self.get_with_args(models.Node,
                                  dict(id=value, show_details=show_details))

    def update_node(self, value, **attrs):
        attrs['id'] = value
        return self.update(models.Node, attrs)

    def delete_node(self, value, ignore_missing=True):
        return self.delete(models.Node,
                           dict(id=value, ignore_missing=ignore_missing))

    def node_join(self, value, cluster):
        params = {
            'id': value,
            'action': 'join',
            'action_args': {
                'cluster_id': cluster,
            }
        }
        return self.action(models.Node, params)

    def node_leave(self, value):
        params = {
            'id': value,
            'action': 'leave',
        }
        return self.action(models.Node, params)

    def triggers(self, **queries):
        return self.list(models.Trigger, **queries)

    def create_trigger(self, **attrs):
        return self.create(models.Trigger, attrs)

    def get_trigger(self, value):
        return self.get(models.Trigger, dict(id=value))

    def delete_trigger(self, value, ignore_missing=True):
        return self.delete(models.Trigger,
                           dict(id=value, ignore_missing=ignore_missing))

    def events(self, **queries):
        return self.list(models.Event, **queries)

    def get_event(self, value):
        return self.get(models.Event, dict(id=value))

    def actions(self, **queries):
        return self.list(models.Action, **queries)

    def get_action(self, value):
        return self.get(models.Action, dict(id=value))

    ######################################################################
    # The operations below should go away when Senlin resources are all
    # adopted into OpenStack SDK.
    ######################################################################

    def session(self, cls_name):
        if cls_name is None:
            raise Exception("A cls name argument must be specified")

        filtration = identity_service.IdentityService()
        return self.session.get(cls_name, service=filtration).text

    def list(self, cls, path_args=None, **options):
        try:
            return cls.list(self.session, path_args=path_args, params=options)
        except Exception as ex:
            client_exc.parse_exception(ex)

    def create(self, cls, params, extra_attrs=False):
        obj = cls.new(**params)
        try:
            return obj.create(self.session, extra_attrs=extra_attrs)
        except Exception as ex:
            client_exc.parse_exception(ex)

    def get_with_args(self, cls, options=None):
        if options is None:
            options = {}
        try:
            obj = cls.new(**options)
            return obj.get_with_args(self.session, options)
        except Exception as ex:
            client_exc.parse_exception(ex)

    def get(self, cls, options=None):
        if options is None:
            options = {}
        try:
            obj = cls.new(**options)
            return obj.get(self.session)
        except Exception as ex:
            client_exc.parse_exception(ex)

    def find(self, cls, options):
        return cls.find(self.session, options)

    def update(self, cls, options):
        obj = cls.new(**options)
        try:
            obj.update(self.session)
        except Exception as ex:
            client_exc.parse_exception(ex)

    def delete(self, cls, options):
        obj = cls.new(**options)
        try:
            obj.delete(self.session)
        except Exception as ex:
            client_exc.parse_exception(ex)

    def action(self, cls, options):
        def filter_args(method, params):
            expected_args = inspect.getargspec(method).args
            accepted_args = ([a for a in expected_args and params
                             if a != 'self'])
            filtered_args = dict((d, params[d]) for d in accepted_args)
            return filtered_args

        def invoke_method(target, method_name, params):
            action = getattr(target, method_name)
            filtered_args = filter_args(action, params)
            reply = action(**filtered_args)
            return reply

        action = options.pop('action')
        if 'action_args' in options:
            args = options.pop('action_args')
        else:
            args = {}

        args.update(session=self.session)
        obj = cls.new(**options)
        try:
            return invoke_method(obj, action, args)
        except Exception as ex:
            client_exc.parse_exception(ex)
