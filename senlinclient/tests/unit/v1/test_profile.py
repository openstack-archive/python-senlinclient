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

from openstack.cluster.v1 import profile as sdk_profile
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc
from openstackclient.common import utils

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import profile as osc_profile


class TestProfile(fakes.TestClusteringv1):
    def setUp(self):
        super(TestProfile, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestProfileShow(TestProfile):
    get_response = {"profile": {
        "created_at": "2015-03-01T14:28:25",
        "domain": 'false',
        "id": "7fa885cd-fa39-4531-a42d-780af95c84a4",
        "metadata": {},
        "name": "test_prof1",
        "project": "42d9e9663331431f97b75e25136307ff",
        "spec": {
            "disable_rollback": 'false',
            "environment": {
                "resource_registry": {
                    "os.heat.server": "OS::Heat::Server"
                }
            },
            "files": {
                "file:///opt/stack/senlin/examples/profiles/test_script.sh":
                    "#!/bin/bash\n\necho \"this is a test script file\"\n"
            },
            "parameters": {},
            "template": {
                "heat_template_version": "2014-10-16",
                "outputs": {
                    "result": {
                        "value": {
                            "get_attr": [
                                "random",
                                "value"
                            ]
                        }
                    }
                },
                "parameters": {
                    "file": {
                        "default": {
                            "get_file": "file:///opt/stack/senlin/"
                                        "examples/profiles/test_script.sh"
                        },
                        "type": "string"
                    }
                },
                "resources": {
                    "random": {
                        "properties": {
                            "length": 64
                        },
                        "type": "OS::Heat::RandomString"
                    }
                },
                "timeout": 60
            },
            "type": "os.heat.stack",
            "version": "1.0"
        },
        "type": "os.heat.stack-1.0",
        "updated_at": 'null',
        "user": "5e5bf8027826429c96af157f68dc9072"
    }}

    def setUp(self):
        super(TestProfileShow, self).setUp()
        self.cmd = osc_profile.ShowProfile(self.app, None)
        self.mock_client.get_profile = mock.Mock(
            return_value=sdk_profile.Profile(
                attrs=self.get_response['profile']))
        utils.get_dict_properties = mock.Mock(return_value='')

    def test_profile_show(self):
        arglist = ['my_profile']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_profile.assert_called_with('my_profile')

    def test_profile_show_not_found(self):
        arglist = ['my_profile']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_profile.side_effect = sdk_exc.ResourceNotFound()
        self.assertRaises(
            exc.CommandError,
            self.cmd.take_action,
            parsed_args)


class TestProfileList(TestProfile):
    columns = ['id', 'name', 'type', 'created_at']
    data = {"profiles": [
        {
            "created_at": "2016-02-17T13:01:05",
            "domain": None,
            "id": "757347e0-6526-4a77-a16d-e099fecde123",
            "metadata": {},
            "name": "my_profile",
            "project": "5f1cc92b578e4e25a3b284179cf20a9b",
            "spec": {
                "properties": {
                    "flavor": 1,
                    "name": "cirros_server"
                },
                "type": "os.nova.server",
                "version": 1
            },
            "type": "os.nova.server-1.0",
            "updated_at": None,
            "user": "2d7aca950f3e465d8ef0c81720faf6ff"
        }
    ]}
    defaults = {
        'limit': None,
        'marker': None,
        'sort': None,
        'global_project': False,
    }

    def setUp(self):
        super(TestProfileList, self).setUp()
        self.cmd = osc_profile.ListProfile(self.app, None)
        self.mock_client.profiles = mock.Mock(
            return_value=self.data)

    def test_profile_list_defaults(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.profiles.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_profile_list_full_id(self):
        arglist = ['--full-id']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.profiles.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_profile_list_limit(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['limit'] = '3'
        arglist = ['--limit', '3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.profiles.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_profile_list_sort(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'id:asc'
        arglist = ['--sort', 'id:asc']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.profiles.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_profile_list_sort_invalid_key(self):
        self.mock_client.profiles = mock.Mock(
            return_value=self.data)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'bad_key'
        arglist = ['--sort', 'bad_key']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.profiles.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_profile_list_sort_invalid_direction(self):
        self.mock_client.profiles = mock.Mock(
            return_value=self.data)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'id:bad_direction'
        arglist = ['--sort', 'id:bad_direction']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.profiles.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_profile_list_filter(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['name'] = 'my_profile'
        arglist = ['--filter', 'name=my_profile']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.profiles.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)


class TestProfileDelete(TestProfile):
    def setUp(self):
        super(TestProfileDelete, self).setUp()
        self.cmd = osc_profile.DeleteProfile(self.app, None)
        self.mock_client.delete_profile = mock.Mock()

    def test_profile_delete(self):
        arglist = ['profile1', 'profile2', 'profile3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_profile.assert_has_calls(
            [mock.call('profile1', False), mock.call('profile2', False),
             mock.call('profile3', False)]
        )

    def test_profile_delete_force(self):
        arglist = ['profile1', 'profile2', 'profile3', '--force']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_profile.assert_has_calls(
            [mock.call('profile1', False), mock.call('profile2', False),
             mock.call('profile3', False)]
        )

    def test_profile_delete_not_found(self):
        arglist = ['my_profile']
        self.mock_client.delete_profile.side_effect = sdk_exc.ResourceNotFound
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Failed to delete 1 of the 1 specified profile(s).',
                      str(error))

    def test_profile_delete_one_found_one_not_found(self):
        arglist = ['profile1', 'profile2']
        self.mock_client.delete_profile.side_effect = (
            [None, sdk_exc.ResourceNotFound]
        )
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action, parsed_args)
        self.mock_client.delete_profile.assert_has_calls(
            [mock.call('profile1', False), mock.call('profile2', False)]
        )
        self.assertEqual('Failed to delete 1 of the 2 specified profile(s).',
                         str(error))

    @mock.patch('sys.stdin', spec=six.StringIO)
    def test_profile_delete_prompt_yes(self, mock_stdin):
        arglist = ['my_profile']
        mock_stdin.isatty.return_value = True
        mock_stdin.readline.return_value = 'y'
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        mock_stdin.readline.assert_called_with()
        self.mock_client.delete_profile.assert_called_with('my_profile',
                                                           False)

    @mock.patch('sys.stdin', spec=six.StringIO)
    def test_profile_delete_prompt_no(self, mock_stdin):
        arglist = ['my_profile']
        mock_stdin.isatty.return_value = True
        mock_stdin.readline.return_value = 'n'
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        mock_stdin.readline.assert_called_with()
        self.mock_client.delete_profile.assert_not_called()


class TestProfileCreate(TestProfile):

    spec_path = 'senlinclient/tests/test_specs/nova_server.yaml'
    response = {"profile": {
        "created_at": "2016-02-17T12:10:57",
        "domain": None,
        "id": "e3057c77-a178-4265-bafd-16b2fae50eea",
        "metadata": {},
        "name": "pro-nova",
        "project": "5f1cc92b578e4e25a3b284179cf20a9b",
        "spec": {"properties": {
            "flavor": 1,
            "image": "cirros-0.3.4-x86_64-uec",
            "name": "cirros_server"},
            "type": "os.nova.server",
            "version": 1.0},
        "type": "os.nova.server-1.0",
        "updated_at": None,
        "user": "2d7aca950f3e465d8ef0c81720faf6ff"}}

    defaults = {"spec": {
        "version": 1.0,
        "type": "os.nova.server",
        "properties": {
            "flavor": 1,
            "name": "cirros_server",
            "image": "cirros-0.3.4-x86_64-uec"}
        },
        "name": "my_profile",
        "metadata": {}
    }

    def setUp(self):
        super(TestProfileCreate, self).setUp()
        self.cmd = osc_profile.CreateProfile(self.app, None)
        self.mock_client.create_profile = mock.Mock(
            return_value=sdk_profile.Profile(attrs=self.response['profile']))
        self.mock_client.get_profile = mock.Mock(
            return_value=sdk_profile.Profile(attrs=self.response['profile']))
        utils.get_dict_properties = mock.Mock(return_value='')

    def test_profile_create_defaults(self):
        arglist = ['my_profile', '--spec-file', self.spec_path]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_profile.assert_called_with(**self.defaults)

    def test_profile_create_metadata(self):
        arglist = ['my_profile', '--spec-file', self.spec_path,
                   '--metadata', 'key1=value1']
        kwargs = copy.deepcopy(self.defaults)
        kwargs['metadata'] = {'key1': 'value1'}
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_profile.assert_called_with(**kwargs)


class TestProfileUpdate(TestProfile):

    response = {"profile": {
        "created_at": "2016-02-17T12:10:57",
        "domain": None,
        "id": "e3057c77-a178-4265-bafd-16b2fae50eea",
        "metadata": {
            "nk1": "nv1",
            "nk2": "nv2",
        },
        "name": "new_profile",
        "project": "5f1cc92b578e4e25a3b284179cf20a9b",
        "spec": {"properties": {
            "flavor": 1,
            "image": "cirros-0.3.4-x86_64-uec",
            "name": "cirros_server"},
            "type": "os.nova.server",
            "version": 1.0},
        "type": "os.nova.server-1.0",
        "updated_at": None,
        "user": "2d7aca950f3e465d8ef0c81720faf6ff"}}

    defaults = {
        "name": "new_profile",
        "metadata": {
            "nk1": "nv1",
            "nk2": "nv2",
        }
    }

    def setUp(self):
        super(TestProfileUpdate, self).setUp()
        self.cmd = osc_profile.UpdateProfile(self.app, None)
        self.mock_client.update_profile = mock.Mock(
            return_value=sdk_profile.Profile(attrs=self.response['profile']))
        self.mock_client.get_profile = mock.Mock(
            return_value=sdk_profile.Profile(attrs=self.response['profile']))
        self.mock_client.find_profile = mock.Mock(
            return_value=sdk_profile.Profile(attrs=self.response['profile']))
        utils.get_dict_properties = mock.Mock(return_value='')

    def test_profile_update_defaults(self):
        arglist = ['--name', 'new_profile', '--metadata', 'nk1=nv1;nk2=nv2',
                   'e3057c77']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.update_profile.assert_called_with(
            'e3057c77-a178-4265-bafd-16b2fae50eea', **self.defaults)

    def test_profile_update_not_found(self):
        arglist = ['--name', 'new_profile', '--metadata', 'nk1=nv1;nk2=nv2',
                   'c6b8b252']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.find_profile.return_value = None
        error = self.assertRaises(
            exc.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn('Profile not found: c6b8b252', str(error))
