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
        '''Convert a dict to an object.'''
        class Args(object):
            def __init__(self, entries):
                self.__dict__.update(entries)

        return Args(args)

    @mock.patch.object(utils, 'print_dict')
    def test_do_build_info(self, mock_print):
        client = mock.Mock()
        result = mock.Mock()
        client.get_build_info = mock.MagicMock(return_value=result)
        sh.do_build_info(client)
        formatters = {
            'api': utils.json_formatter,
            'engine': utils.json_formatter,
        }
        mock_print.assert_called_once_with(result, formatters=formatters)
        self.assertTrue(client.get_build_info.called)

    @mock.patch.object(utils, 'print_list')
    def test_do_profile_type_list(self, mock_print):
        client = mock.Mock()
        types = mock.Mock()
        client.profile_types = mock.MagicMock(return_value=types)
        sh.do_profile_type_list(client)
        mock_print.assert_called_once_with(types, ['name'], sortby_index=0)
        self.assertTrue(client.profile_types.called)

    @mock.patch.object(utils, 'format_output')
    def test_do_profile_type_schema(self, mock_format):
        client = mock.Mock()
        schema = {'foo': 'bar'}
        client.get_profile_type_schema = mock.MagicMock(return_value=schema)
        args = {
            'format': 'list',
            'profile_type': 'os.nova.server'
        }
        args = self._make_args(args)
        sh.do_profile_type_schema(client, args)
        mock_format.assert_called_with(schema, format=args.format)
        client.get_profile_type_schema.assert_called_with(
            'os.nova.server')
        args.format = None
        sh.do_profile_type_schema(client, args)
        mock_format.assert_called_with(schema)

    def test_do_profile_type_schema_type_not_found(self):
        client = mock.Mock()
        args = {'profile_type': 'wrong_type'}
        args = self._make_args(args)
        ex = exc.HTTPNotFound
        client.get_profile_type_schema = mock.MagicMock(side_effect=ex)
        ex = self.assertRaises(exc.CommandError,
                               sh.do_profile_type_schema,
                               client, args)
        self.assertEqual(_('Profile Type wrong_type not found.'),
                         six.text_type(ex))

    @mock.patch.object(utils, 'print_list')
    def test_do_profile_list(self, mock_print):
        client = mock.Mock()
        short_id = mock.Mock()
        sh._short_id = short_id
        profiles = mock.Mock()
        client.profiles = mock.MagicMock(return_value=profiles)
        fields = ['id', 'name', 'type', 'created_time']
        args = {
            'show_deleted': False,
            'limit': 20,
            'marker': 'mark_id',
            'full_id': True
        }
        queries = {
            'show_deleted': False,
            'limit': 20,
            'marker': 'mark_id',
        }
        formatters = {}
        args = self._make_args(args)
        sh.do_profile_list(client, args)
        client.profiles.assert_called_once_with(**queries)
        mock_print.assert_called_with(profiles, fields, formatters=formatters,
                                      sortby_index=1)

        # short_id is requested
        args.full_id = False
        sh.do_profile_list(client, args)
        formatters = {'id': short_id}
        mock_print.assert_called_with(profiles, fields, formatters=formatters,
                                      sortby_index=1)

    @mock.patch.object(utils, 'nested_dict_formatter')
    @mock.patch.object(utils, 'print_dict')
    def test_show_profile(self, mock_print, mock_dict):
        client = mock.Mock()
        profile = mock.Mock()
        profile_id = mock.Mock()
        client.get_profile = mock.MagicMock(return_value=profile)
        pro_to_dict = mock.Mock()
        profile.to_dict = mock.MagicMock(return_value=pro_to_dict)
        json_formatter = mock.Mock()
        utils.json_formatter = json_formatter
        dict_formatter = mock.Mock()
        mock_dict.return_value = dict_formatter
        formatters = {
            'metadata': json_formatter,
            'spec': dict_formatter
        }
        sh._show_profile(client, profile_id)
        client.get_profile.assert_called_once_with(profile_id)
        mock_dict.assert_called_once_with(['type', 'version', 'properties'],
                                          ['property', 'value'])
        mock_print.assert_called_once_with(pro_to_dict, formatters=formatters)

    def test_show_profile_not_found(self):
        client = mock.Mock()
        ex = exc.HTTPNotFound
        client.get_profile = mock.MagicMock(side_effect=ex)
        profile_id = 'wrong_id'
        ex = self.assertRaises(exc.CommandError,
                               sh._show_profile,
                               client, profile_id)
        self.assertEqual(_('Profile not found: wrong_id'), six.text_type(ex))
        client.get_profile.assert_called_once_with(profile_id)

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
        client.create_profile = mock.MagicMock(return_value=profile)
        sh.do_profile_create(client, args)
        mock_get.assert_called_once_with(args.spec_file)
        mock_proc.assert_called_once_with(self.profile_spec['properties'])
        mock_format.assert_called_once_with(args.metadata)
        client.create_profile.assert_called_once_with(**params)
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
        client.get_profile = mock.MagicMock(return_value=profile)
        sh.do_profile_update(client, args)
        mock_format.assert_called_once_with(args.metadata)
        client.get_profile.assert_called_once_with('FAKE_ID')
        params = {
            'name': 'stack_spec',
            'permission': 'ok',
            'metadata': {'user': 'demo'},
            'id': profile_id,
        }
        client.update_profile.assert_called_once_with(params)
        mock_show.assert_called_once_with(client, profile_id)

        # specified profile can't be found
        ex = exc.HTTPNotFound
        client.get_profile = mock.MagicMock(side_effect=ex)
        ex = self.assertRaises(exc.CommandError,
                               sh.do_profile_update,
                               client, args)
        self.assertEqual(_('Profile not found: FAKE_ID'),
                         six.text_type(ex))

    def test_do_profile_delete(self):
        client = mock.Mock()
        args = {'id': ['profile1', 'profile2']}
        args = self._make_args(args)
        sh.do_profile_delete(client, args)
        ex = Exception()
        client.delete_profile = mock.MagicMock(side_effect=ex)
        ex = self.assertRaises(exc.CommandError,
                               sh.do_profile_delete,
                               client, args)
        self.assertEqual(_('Failed to delete some of the specified '
                           'profile(s).'), six.text_type(ex))
        client.delete_profile.assert_called_with('profile2')
