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

import copy
import mock
import six
import testtools

from senlinclient.common import exc
from senlinclient.common.i18n import _
from senlinclient.common import utils
from senlinclient.v1 import shell as sh


class ShellTest(testtools.TestCase):

    def setUp(self):
        super(ShellTest, self).setUp()
        self.profile_args = {
            'spec_file': mock.Mock(),
            'name': 'stack_spec',
            'permission': 'ok',
            'metadata': {'user': 'demo'}
        }
        self.profile_spec = {
            'type': 'os.heat.stack',
            'version': 1.0,
            'properties': {
                'name': 'stack1',
                'template': {"Template": "data"}
            }
        }

    def _make_args(self, args):
        """Convert a dict to an object."""
        class Args(object):
            def __init__(self, entries):
                self.__dict__.update(entries)

        return Args(args)

    @mock.patch.object(utils, 'print_dict')
    def test_do_build_info(self, mock_print):
        client = mock.Mock()
        result = mock.Mock()
        client.conn.cluster.get_build_info.return_value = result
        sh.do_build_info(client)
        formatters = {
            'api': utils.json_formatter,
            'engine': utils.json_formatter,
        }
        mock_print.assert_called_once_with(result, formatters=formatters)
        self.assertTrue(client.conn.cluster.get_build_info.called)

    @mock.patch.object(utils, 'print_list')
    def test_do_profile_type_list(self, mock_print):
        client = mock.Mock()
        types = mock.Mock()
        client.conn.cluster.profile_types.return_value = types
        sh.do_profile_type_list(client)
        mock_print.assert_called_once_with(types, ['name'], sortby_index=0)
        self.assertTrue(client.conn.cluster.profile_types.called)

    @mock.patch.object(utils, 'format_output')
    def test_do_profile_type_show(self, mock_format):
        client = mock.Mock()
        fake_pt = mock.Mock()
        fake_pt.to_dict.return_value = {'foo': 'bar'}
        client.conn.cluster.get_profile_type = mock.Mock(return_value=fake_pt)
        args_dict = {
            'format': 'json',
            'type_name': 'os.nova.server'
        }
        args = self._make_args(args_dict)
        sh.do_profile_type_show(client, args)
        mock_format.assert_called_with({'foo': 'bar'}, format=args.format)
        client.conn.cluster.get_profile_type.assert_called_with(
            'os.nova.server')
        args.format = None
        sh.do_profile_type_show(client, args)
        mock_format.assert_called_with({'foo': 'bar'})

    def test_do_profile_type_show_type_not_found(self):
        client = mock.Mock()
        args = {
            'type_name': 'wrong_type',
            'format': 'json'
        }
        args = self._make_args(args)
        ex = exc.HTTPNotFound
        client.conn.cluster.get_profile_type = mock.Mock(side_effect=ex)
        ex = self.assertRaises(exc.CommandError,
                               sh.do_profile_type_show,
                               client, args)
        self.assertEqual(_('Profile Type wrong_type not found.'),
                         six.text_type(ex))

    @mock.patch.object(utils, 'print_list')
    def test_do_profile_list(self, mock_print):
        client = mock.Mock()
        profiles = mock.Mock()
        client.conn.cluster.profiles.return_value = profiles
        fields = ['id', 'name', 'type', 'created_time']
        args = {
            'show_deleted': False,
            'limit': 20,
            'marker': 'mark_id',
        }
        queries = copy.deepcopy(args)
        formatters = {}
        args = self._make_args(args)
        args.full_id = True
        sh.do_profile_list(client, args)
        client.conn.cluster.profiles.assert_called_once_with(**queries)
        mock_print.assert_called_with(profiles, fields, formatters=formatters,
                                      sortby_index=1)

    @mock.patch.object(utils, 'nested_dict_formatter')
    @mock.patch.object(utils, 'print_dict')
    def test_show_profile(self, mock_print, mock_dict):
        client = mock.Mock()
        profile = mock.Mock()
        profile_id = mock.Mock()
        client.conn.cluster.get_profile.return_value = profile
        pro_to_dict = mock.Mock()
        profile.to_dict.return_value = pro_to_dict
        json_formatter = mock.Mock()
        utils.json_formatter = json_formatter
        dict_formatter = mock.Mock()
        mock_dict.return_value = dict_formatter
        formatters = {
            'metadata': json_formatter,
            'spec': dict_formatter
        }
        sh._show_profile(client, profile_id)
        client.conn.cluster.get_profile.assert_called_once_with(profile_id)
        mock_dict.assert_called_once_with(['type', 'version', 'properties'],
                                          ['property', 'value'])
        mock_print.assert_called_once_with(pro_to_dict, formatters=formatters)

    def test_show_profile_not_found(self):
        client = mock.Mock()
        ex = exc.HTTPNotFound
        client.conn.cluster.get_profile.side_effect = ex
        profile_id = 'wrong_id'
        ex = self.assertRaises(exc.CommandError,
                               sh._show_profile,
                               client, profile_id)
        self.assertEqual(_('Profile not found: wrong_id'), six.text_type(ex))
        client.conn.cluster.get_profile.assert_called_once_with(profile_id)

    @mock.patch.object(sh, '_show_profile')
    @mock.patch.object(utils, 'format_parameters')
    @mock.patch.object(utils, 'process_stack_spec')
    @mock.patch.object(utils, 'get_spec_content')
    def test_do_profile_create(self, mock_get, mock_proc, mock_format,
                               mock_show):
        args = copy.deepcopy(self.profile_args)
        args = self._make_args(args)
        spec = copy.deepcopy(self.profile_spec)
        mock_get.return_value = spec
        stack_properties = mock.Mock()
        mock_proc.return_value = stack_properties
        mock_format.return_value = {'user': 'demo'}
        params = {
            'name': 'stack_spec',
            'spec': spec,
            'permission': 'ok',
            'metadata': {'user': 'demo'},
        }
        client = mock.Mock()
        profile = mock.Mock()
        profile_id = mock.Mock()
        profile.id = profile_id
        client.conn.cluster.create_profile.return_value = profile
        sh.do_profile_create(client, args)
        mock_get.assert_called_once_with(args.spec_file)
        mock_proc.assert_called_once_with(self.profile_spec['properties'])
        mock_format.assert_called_once_with(args.metadata)
        client.conn.cluster.create_profile.assert_called_once_with(**params)
        mock_show.assert_called_once_with(client, profile_id)

        # Miss 'type' key in spec file
        del spec['type']
        ex = self.assertRaises(exc.CommandError,
                               sh.do_profile_create,
                               client, args)
        self.assertEqual(_("Missing 'type' key in spec file."),
                         six.text_type(ex))
        # Miss 'version' key in spec file
        spec['type'] = 'os.heat.stack'
        del spec['version']
        ex = self.assertRaises(exc.CommandError,
                               sh.do_profile_create,
                               client, args)
        self.assertEqual(_("Missing 'version' key in spec file."),
                         six.text_type(ex))
        # Miss 'properties' key in spec file
        spec['version'] = 1.0
        del spec['properties']
        ex = self.assertRaises(exc.CommandError,
                               sh.do_profile_create,
                               client, args)
        self.assertEqual(_("Missing 'properties' key in spec file."),
                         six.text_type(ex))

    @mock.patch.object(sh, '_show_profile')
    def test_do_profile_show(self, mock_show):
        client = mock.Mock()
        args = {'id': 'profile_id'}
        args = self._make_args(args)
        sh.do_profile_show(client, args)
        mock_show.assert_called_once_with(client, args.id)

    @mock.patch.object(sh, '_show_profile')
    @mock.patch.object(utils, 'format_parameters')
    def test_do_profile_update(self, mock_format, mock_show):
        args = copy.deepcopy(self.profile_args)
        args = self._make_args(args)
        mock_format.return_value = {'user': 'demo'}
        client = mock.Mock()
        profile = mock.Mock()
        profile_id = mock.Mock()
        profile.id = profile_id
        args.id = 'FAKE_ID'
        client.conn.cluster.get_profile.return_value = profile
        sh.do_profile_update(client, args)
        mock_format.assert_called_once_with(args.metadata)
        client.conn.cluster.get_profile.assert_called_once_with('FAKE_ID')
        params = {
            'name': 'stack_spec',
            'permission': 'ok',
            'metadata': {'user': 'demo'},
        }
        client.conn.cluster.update_profile.assert_called_once_with(
            profile_id, **params)
        mock_show.assert_called_once_with(client, profile_id)

    @mock.patch.object(utils, 'format_parameters')
    def test_do_profile_update_not_found(self, mock_format):
        client = mock.Mock()
        args = copy.deepcopy(self.profile_args)
        args = self._make_args(args)
        args.id = 'FAKE_ID'
        ex = exc.HTTPNotFound
        client.conn.cluster.get_profile.side_effect = ex
        ex = self.assertRaises(exc.CommandError,
                               sh.do_profile_update,
                               client, args)
        self.assertEqual(_('Profile not found: FAKE_ID'),
                         six.text_type(ex))
        mock_format.assert_called_once_with(args.metadata)

    def test_do_profile_delete(self):
        client = mock.Mock()
        args = {'id': ['profile_id']}
        args = self._make_args(args)
        sh.do_profile_delete(client, args)
        client.conn.cluster.delete_profile.assert_called_with('profile_id')

    def test_do_profile_delete_fail(self):
        client = mock.Mock()
        args = {'id': ['profile1', 'profile2']}
        args = self._make_args(args)
        sh.do_profile_delete(client, args)
        ex = Exception()
        client.conn.cluster.delete_profile.side_effect = ex
        ex = self.assertRaises(exc.CommandError,
                               sh.do_profile_delete,
                               client, args)
        self.assertEqual(_('Failed to delete some of the specified '
                           'profile(s).'), six.text_type(ex))
        client.conn.cluster.delete_profile.assert_called_with('profile2')

    @mock.patch.object(utils, 'print_list')
    def test_do_policy_type_list(self, mock_print):
        client = mock.Mock()
        args = mock.Mock()
        types = mock.Mock()
        client.conn.cluster.policy_types.return_value = types
        sh.do_policy_type_list(client, args)
        mock_print.assert_called_once_with(types, ['name'], sortby_index=0)

    @mock.patch.object(utils, 'format_output')
    def test_do_policy_type_show(self, mock_format):
        client = mock.Mock()
        args = {
            'type_name': 'senlin.policy.deletion',
            'format': 'yaml'
        }
        args = self._make_args(args)
        res = mock.Mock()
        pt = mock.Mock()
        res.to_dict.return_value = pt
        client.conn.cluster.get_policy_type.return_value = res
        sh.do_policy_type_show(client, args)
        mock_format.assert_called_with(pt, format=args.format)

        # no format attribute
        args = {
            'type_name': 'senlin.policy.deletion',
            'format': None
        }
        args = self._make_args(args)
        client.conn.cluster.get_policy_type.return_value = res
        sh.do_policy_type_show(client, args)
        mock_format.assert_called_with(pt)

    def test_do_policy_type_show_not_found(self):
        client = mock.Mock()
        args = {'type_name': 'wrong_policy_type'}
        args = self._make_args(args)
        ex = exc.HTTPNotFound
        client.conn.cluster.get_policy_type.side_effect = ex
        ex = self.assertRaises(exc.CommandError,
                               sh.do_policy_type_show, client, args)
        msg = _('Policy type wrong_policy_type not found.')
        self.assertEqual(msg, six.text_type(ex))

    @mock.patch.object(utils, 'print_list')
    def test_do_receiver_list(self, mock_print):
        client = mock.Mock()
        params = {
            'limit': 10,
            'marker': 'fake_id',
            'sort_keys': 'name',
            'sort_dir': 'asc',
            'filters': ['filter_key=filter_value'],
            'show_deleted': True,
            'global_project': False,
            'full_id': False,
        }
        fields = ['id', 'name', 'type', 'cluster_id', 'action',
                  'created_time', 'deleted_time']
        args = self._make_args(params)
        queries = copy.deepcopy(params)
        del queries['filters']
        queries['filter_key'] = 'filter_value'
        r1 = mock.Mock()
        r1.id = '01234567-abcd-efgh'
        r1.cluster_id = 'abcdefgh-abcd-efgh'
        receivers = [r1]
        client.receivers.return_value = receivers
        formatters = {
            'id': mock.ANY,
            'cluster_id': mock.ANY
        }
        sh.do_receiver_list(client, args)
        mock_print.assert_called_with(receivers, fields,
                                      formatters=formatters,
                                      sortby_index=None)
        # full_id is requested
        args.full_id = True
        sh.do_receiver_list(client, args)
        mock_print.assert_called_with(receivers, fields,
                                      formatters={},
                                      sortby_index=None)

        # default sorting
        args.sort_keys = None
        sh.do_receiver_list(client, args)
        mock_print.assert_called_with(receivers, fields,
                                      formatters={},
                                      sortby_index=0)

    @mock.patch.object(utils, 'print_dict')
    def test_show_receiver(self, mock_print):
        client = mock.Mock()
        receiver = mock.Mock()
        receiver_id = '01234567-abcd-abcd-abcdef'
        receiver.id = receiver_id
        client.get_receiver.return_value = receiver
        receiver_dict = mock.Mock()
        receiver.to_dict.return_value = receiver_dict
        sh._show_receiver(client, receiver_id)
        formatters = {
            'actor': utils.json_formatter,
            'params': utils.json_formatter,
            'channel': utils.json_formatter,
        }
        client.get_receiver.assert_called_once_with(receiver_id)
        mock_print.assert_called_once_with(receiver_dict,
                                           formatters=formatters)

    def test_show_receiver_not_found(self):
        client = mock.Mock()
        receiver = mock.Mock()
        receiver_id = 'wrong_id'
        receiver.id = receiver_id
        ex = exc.HTTPNotFound
        client.get_receiver.side_effect = ex
        ex = self.assertRaises(exc.CommandError,
                               sh._show_receiver, client, receiver_id)
        self.assertEqual(_('Receiver not found: wrong_id'), six.text_type(ex))

    @mock.patch.object(sh, '_show_receiver')
    def test_do_receiver_show(self, mock_show):
        client = mock.Mock()
        args = {'id': 'receiver_id'}
        args = self._make_args(args)
        sh.do_receiver_show(client, args)
        mock_show.assert_called_once_with(client,
                                          receiver_id='receiver_id')

    @mock.patch.object(sh, '_show_receiver')
    def test_do_receiver_create(self, mock_show):
        client = mock.Mock()
        args = {
            'name': 'receiver1',
            'type': 'webhook',
            'cluster': 'cluster1',
            'action': 'CLUSTER_SCALE_IN',
            'params': {}
        }
        args = self._make_args(args)
        params = {
            'name': 'receiver1',
            'type': 'webhook',
            'cluster_id': 'cluster1',
            'action': 'CLUSTER_SCALE_IN',
            'params': {}
        }
        receiver = mock.Mock()
        receiver.id = 'FAKE_ID'
        client.create_receiver.return_value = receiver
        sh.do_receiver_create(client, args)
        client.create_receiver.assert_called_once_with(**params)
        mock_show.assert_called_once_with(client, 'FAKE_ID')

    def test_do_receiver_delete(self):
        client = mock.Mock()
        args = {'id': ['receiver_id']}
        args = self._make_args(args)
        client.delete_receiver = mock.Mock()
        sh.do_receiver_delete(client, args)
        client.delete_receiver.assert_called_once_with('receiver_id')

    def test_do_receiver_delete_not_found(self):
        client = mock.Mock()
        args = {'id': ['receiver_id']}
        args = self._make_args(args)
        ex = exc.HTTPNotFound
        client.delete_receiver.side_effect = ex
        ex = self.assertRaises(exc.CommandError,
                               sh.do_receiver_delete, client, args)
        msg = _('Failed to delete some of the specified receiver(s).')
        self.assertEqual(msg, six.text_type(ex))

    @mock.patch.object(utils, 'print_list')
    def test_do_policy_list(self, mock_print):
        client = mock.Mock()
        fields = ['id', 'name', 'type', 'level', 'cooldown', 'created_time']
        args = {
            'show_deleted': True,
            'limit': 20,
            'marker': 'fake_id',
            'full_id': True
        }
        args = self._make_args(args)
        queries = {
            'show_deleted': True,
            'limit': 20,
            'marker':
            'fake_id',
        }
        policies = mock.Mock()
        client.conn.cluster.policies.return_value = policies
        formatters = {}
        sh.do_policy_list(client, args)
        client.conn.cluster.policies.assert_called_once_with(**queries)
        mock_print.assert_called_once_with(
            policies, fields, formatters=formatters, sortby_index=1)

    @mock.patch.object(utils, 'print_dict')
    def test_show_policy(self, mock_print):
        client = mock.Mock()
        formatters = {
            'metadata': utils.json_formatter,
            'spec': utils.json_formatter,
        }
        policy_id = 'fake_policy_id'
        policy = mock.Mock()
        policy.id = policy_id
        client.conn.cluster.get_policy.return_value = policy
        policy_dict = mock.Mock()
        policy.to_dict.return_value = policy_dict
        sh._show_policy(client, policy_id)
        mock_print.assert_called_once_with(policy_dict,
                                           formatters=formatters)

        # policy not found
        ex = exc.HTTPNotFound
        client.conn.cluster.get_policy.side_effect = ex
        ex = self.assertRaises(exc.CommandError,
                               sh._show_policy,
                               client, policy_id)
        msg = _('Policy not found: fake_policy_id')
        self.assertEqual(msg, six.text_type(ex))

    @mock.patch.object(sh, '_show_policy')
    @mock.patch.object(utils, 'get_spec_content')
    def test_do_policy_create(self, mock_get, mock_show):
        client = mock.Mock()
        spec = mock.Mock()
        mock_get.return_value = spec
        args = {
            'name': 'new_policy',
            'spec_file': 'policy_file',
            'cooldown': 20,
            'enforcement_level': 50
        }
        args = self._make_args(args)
        attrs = {
            'name': 'new_policy',
            'spec': spec,
            'cooldown': 20,
            'level': 50
        }
        policy = mock.Mock()
        policy.id = 'policy_id'
        client.conn.cluster.create_policy.return_value = policy
        sh.do_policy_create(client, args)
        mock_get.assert_called_once_with(args.spec_file)
        client.conn.cluster.create_policy.assert_called_once_with(**attrs)
        mock_show.assert_called_once_with(client, policy.id)

    @mock.patch.object(sh, '_show_policy')
    def test_do_policy_show(self, mock_show):
        client = mock.Mock()
        args = {'id': 'policy_id'}
        args = self._make_args(args)
        sh.do_policy_show(client, args)
        mock_show.assert_called_once_with(client,
                                          policy_id='policy_id')

    @mock.patch.object(sh, '_show_policy')
    def test_do_policy_update(self, mock_show):
        client = mock.Mock()
        args = {
            'name': 'deletion_policy',
            'cooldown': 10,
            'enforcement_level': 50,
            'id': 'policy_id',
        }
        args = self._make_args(args)
        params = {
            'name': 'deletion_policy',
            'cooldown': 10,
            'level': 50,
            'id': 'policy_id'
        }
        policy = mock.Mock()
        client.conn.cluster.get_policy.return_value = policy
        policy.id = 'policy_id'
        sh.do_policy_update(client, args)
        client.conn.cluster.get_policy.assert_called_once_with('policy_id')
        client.conn.cluster.update_policy.assert_called_once_with(
            'policy_id', params)
        mock_show(client, policy_id=policy.id)

    def test_do_policy_delete(self):
        client = mock.Mock()
        args = {'id': ['policy_id']}
        args = self._make_args(args)
        client.conn.cluster.delete_policy = mock.Mock()
        sh.do_policy_delete(client, args)
        client.conn.cluster.delete_policy.assert_called_once_with('policy_id')

    def test_do_policy_delete_not_found(self):
        client = mock.Mock()
        args = {'id': ['policy_id']}
        args = self._make_args(args)
        ex = exc.HTTPNotFound
        client.conn.cluster.delete_policy.side_effect = ex
        ex = self.assertRaises(exc.CommandError,
                               sh.do_policy_delete, client, args)
        msg = _('Failed to delete some of the specified policy(s).')
        self.assertEqual(msg, six.text_type(ex))

    @mock.patch.object(utils, 'print_list')
    def test_do_cluster_list(self, mock_print):
        client = mock.Mock()
        fields = ['id', 'name', 'status', 'created_time', 'updated_time',
                  'parent']
        args = {
            'limit': 20,
            'marker': 'fake_id',
            'sort_keys': 'name',
            'sort_dir': 'asc',
            'show_deleted': True,
            'show_nested': True,
            'global_project': False,
            'filters': ['status=ACTIVE'],
        }
        queries = copy.deepcopy(args)
        del queries['filters']
        queries['status'] = 'ACTIVE'
        args = self._make_args(args)
        clusters = mock.Mock()
        client.clusters.return_value = clusters
        args.full_id = True
        formatters = {}
        sh.do_cluster_list(client, args)
        client.clusters.assert_called_once_with(**queries)
        mock_print.assert_called_once_with(clusters, fields,
                                           formatters=formatters,
                                           sortby_index=None)

        # invalid sort key
        args.sort_keys = 'id'
        ex = exc.CommandError
        ex = self.assertRaises(ex, sh.do_cluster_list, client, args)
        self.assertEqual(_('Invalid sorting key: id'), six.text_type(ex))

    @mock.patch.object(utils, 'print_dict')
    def test_show_cluster(self, mock_print):
        client = mock.Mock()
        cluster_id = 'cluster_id'
        cluster = mock.Mock()
        cluster.id = cluster_id
        client.get_cluster.return_value = cluster
        formatters = {
            'metadata': utils.json_formatter,
            'nodes': utils.list_formatter,
        }
        cluster_dict = mock.Mock()
        cluster.to_dict.return_value = cluster_dict
        sh._show_cluster(client, cluster_id)
        mock_print.assert_called_once_with(cluster_dict, formatters=formatters)

    @mock.patch.object(sh, '_show_cluster')
    def test_do_cluster_create(self, mock_show):
        client = mock.Mock()
        args = {
            'name': 'CLUSTER1',
            'profile': 'profile1',
            'min_size': 1,
            'max_size': 10,
            'desired_capacity': 5,
            'parent': 'CLUSTER',
            'metadata': ['user=demo'],
            'timeout': 200,
        }
        attrs = copy.deepcopy(args)
        attrs['profile_id'] = args['profile']
        args = self._make_args(args)
        del attrs['profile']
        attrs['metadata'] = {'user': 'demo'}
        cluster = mock.Mock()
        client.create_cluster.return_value = cluster
        cluster.id = 'cluster_id'
        sh.do_cluster_create(client, args)
        client.create_cluster.assert_called_once_with(**attrs)
        mock_show.assert_called_once_with(client, 'cluster_id')

    def test_do_cluster_delete(self):
        client = mock.Mock()
        args = {'id': ['cluster_id']}
        args = self._make_args(args)
        client.delete_cluster = mock.Mock()
        sh.do_cluster_delete(client, args)
        client.delete_cluster.assert_called_once_with('cluster_id')

    def test_do_cluster_delete_not_found(self):
        client = mock.Mock()
        args = {'id': ['cluster_id']}
        args = self._make_args(args)
        ex = exc.HTTPNotFound
        client.delete_cluster.side_effect = ex
        ex = self.assertRaises(exc.CommandError,
                               sh.do_cluster_delete, client, args)
        msg = _('Failed to delete some of the specified clusters.')
        self.assertEqual(msg, six.text_type(ex))

    @mock.patch.object(sh, '_show_cluster')
    def test_do_cluster_update(self, mock_show):
        client = mock.Mock()
        args = {
            'profile': 'test_profile',
            'name': 'CLUSTER1',
            'parent': 'parent_cluster',
            'metadata': ['user=demo'],
            'timeout': 100,
        }
        attrs = copy.deepcopy(args)
        attrs['metadata'] = {'user': 'demo'}
        attrs['profile_id'] = 'test_profile'
        del attrs['profile']
        args = self._make_args(args)
        args.id = 'cluster_id'
        cluster = mock.Mock()
        cluster.id = 'cluster_id'
        client.get_cluster.return_value = cluster
        client.update_cluster = mock.Mock()
        sh.do_cluster_update(client, args)
        client.get_cluster.assert_called_once_with('cluster_id')
        client.update_cluster.assert_called_once_with('cluster_id', **attrs)
        mock_show.assert_called_once_with(client, 'cluster_id')

    @mock.patch.object(sh, '_show_cluster')
    def test_do_cluster_show(self, mock_show):
        client = mock.Mock()
        args = {'id': 'cluster_id'}
        args = self._make_args(args)
        sh.do_cluster_show(client, args)
        mock_show.assert_called_once_with(client, 'cluster_id')

    @mock.patch.object(utils, 'print_list')
    def test_do_cluster_node_list(self, mock_print):
        client = mock.Mock()
        args = {
            'id': 'cluster_id',
            'show_deleted': True,
            'limit': 20,
            'marker': 'marker_id',
            'filters': ['status=ACTIVE'],
        }
        queries = copy.deepcopy(args)
        queries['cluster_id'] = args['id']
        del queries['id']
        del queries['filters']
        queries['status'] = 'ACTIVE'
        args = self._make_args(args)
        args.full_id = True
        nodes = mock.Mock()
        client.nodes.return_value = nodes
        formatters = {}
        fields = ['id', 'name', 'index', 'status', 'physical_id',
                  'created_time']
        sh.do_cluster_node_list(client, args)
        client.nodes.assert_called_once_with(**queries)
        mock_print.assert_called_once_with(nodes, fields,
                                           formatters=formatters,
                                           sortby_index=5)

        # node not found
        ex = exc.HTTPNotFound
        client.nodes.side_effect = ex
        ex = self.assertRaises(exc.CommandError,
                               sh.do_cluster_node_list, client, args)
        msg = _('No node matching criteria is found')
        self.assertEqual(msg, six.text_type(ex))

    def test_do_cluster_node_add(self):
        client = mock.Mock()
        args = {
            'id': 'cluster_id',
            'nodes': 'node1,node2'
        }
        args = self._make_args(args)
        node_ids = ['node1', 'node2']
        resp = {'action': 'CLUSTER_NODE_ADD'}
        client.cluster_add_nodes.return_value = resp
        sh.do_cluster_node_add(client, args)
        client.cluster_add_nodes.assert_called_once_with('cluster_id',
                                                         node_ids)

    def test_do_cluster_node_del(self):
        client = mock.Mock()
        args = {
            'id': 'cluster_id',
            'nodes': 'node1,node2'
        }
        args = self._make_args(args)
        node_ids = ['node1', 'node2']
        resp = {'action': 'CLUSTER_NODE_DEL'}
        client.cluster_del_nodes.return_value = resp
        sh.do_cluster_node_del(client, args)
        client.cluster_del_nodes.assert_called_once_with('cluster_id',
                                                         node_ids)

    @mock.patch.object(utils, 'print_list')
    def test_do_node_list(self, mock_print):
        client = mock.Mock()
        fields = ['id', 'name', 'status', 'cluster_id', 'physical_id',
                  'profile_name', 'created_time', 'updated_time',
                  'deleted_time']
        args = {
            'show_deleted': True,
            'cluster': 'cluster1',
            'sort_keys': 'name',
            'sort_dir': 'asc',
            'limit': 20,
            'marker': 'marker_id',
            'global_project': True,
            'filters': ['status=active'],
            'full_id': True,
        }
        queries = {
            'show_deleted': True,
            'cluster_id': 'cluster1',
            'sort_keys': 'name',
            'sort_dir': 'asc',
            'limit': 20,
            'marker': 'marker_id',
            'global_project': True,
            'status': 'active',
        }
        args = self._make_args(args)
        nodes = mock.Mock()
        client.nodes.return_value = nodes
        short_id = mock.Mock()
        sh._short_id = short_id
        short_cluster_id = mock.Mock()
        sh._short_cluster_id = short_cluster_id
        short_physical_id = mock.Mock()
        sh._short_physical_id = short_physical_id
        formatters = {}
        sh.do_node_list(client, args)
        mock_print.assert_called_once_with(nodes, fields,
                                           formatters=formatters,
                                           sortby_index=None)
        client.nodes.assert_called_once_with(**queries)
        # wrong sort key
        args.sort_keys = 'name;wrong_key'
        ex = exc.CommandError
        ex = self.assertRaises(ex, sh.do_node_list, client, args)
        msg = _('Invalid sorting key: wrong_key')
        self.assertEqual(msg, six.text_type(ex))
