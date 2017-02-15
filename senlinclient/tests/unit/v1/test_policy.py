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
from openstack import exceptions as sdk_exc
from osc_lib import exceptions as exc
import six

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import policy as osc_policy


class TestPolicy(fakes.TestClusteringv1):
    def setUp(self):
        super(TestPolicy, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestPolicyList(TestPolicy):
    columns = ['id', 'name', 'type', 'created_at']
    response = {"policies": [
        {
        }
    ]}
    defaults = {
        'global_project': False,
        'marker': None,
        'limit': None,
        'sort': None,
    }

    def setUp(self):
        super(TestPolicyList, self).setUp()
        self.cmd = osc_policy.ListPolicy(self.app, None)
        fake_policy = mock.Mock(
            created_at="2015-02-15T08:33:13.000000",
            data={},
            domain=None,
            id="7192d8df-73be-4e98-ab99-1cf6d5066729",
            project_id="42d9e9663331431f97b75e25136307ff",
            spec={
                "description": "A test policy",
                "properties": {
                    "criteria": "OLDEST_FIRST",
                    "destroy_after_deletion": True,
                    "grace_period": 60,
                    "reduce_desired_capacity": False
                },
                "type": "senlin.policy.deletion",
                "version": "1.0"
            },
            type="senlin.policy.deletion-1.0",
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_policy.name = "test_policy_1"
        fake_policy.to_dict = mock.Mock(return_value={})
        self.mock_client.policies = mock.Mock(
            return_value=self.response)

    def test_policy_list_defaults(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_policy_list_full_id(self):
        arglist = ['--full-id']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_policy_list_limit(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['limit'] = '3'
        arglist = ['--limit', '3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_policy_list_sort(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:asc'
        arglist = ['--sort', 'name:asc']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_policy_list_sort_invalid_key(self):
        self.mock_client.policies = mock.Mock(
            return_value=self.response)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'bad_key'
        arglist = ['--sort', 'bad_key']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.policies.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_policy_list_sort_invalid_direction(self):
        self.mock_client.policies = mock.Mock(
            return_value=self.response)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:bad_direction'
        arglist = ['--sort', 'name:bad_direction']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.policies.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_policy_list_marker(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['marker'] = 'a9448bf6'
        arglist = ['--marker', 'a9448bf6']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_policy_list_filter(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['name'] = 'my_policy'
        arglist = ['--filter', 'name=my_policy']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.policies.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)


class TestPolicyShow(TestPolicy):
    response = {"policy": {
    }}

    def setUp(self):
        super(TestPolicyShow, self).setUp()
        self.cmd = osc_policy.ShowPolicy(self.app, None)
        fake_policy = mock.Mock(
            created_at="2015-03-02T07:40:31",
            data={},
            domain_id=None,
            id="02f62195-2198-4797-b0a9-877632208527",
            project_id="42d9e9663331431f97b75e25136307ff",
            spec={
                "properties": {
                    "adjustment": {
                        "best_effort": True,
                        "min_step": 1,
                        "number": 1,
                        "type": "CHANGE_IN_CAPACITY"
                    },
                    "event": "CLUSTER_SCALE_IN"
                },
                "type": "senlin.policy.scaling",
                "version": "1.0"
            },
            type="senlin.policy.scaling-1.0",
            updated_at=None,
            user_id="5e5bf8027826429c96af157f68dc9072"
        )
        fake_policy.name = "sp001"
        fake_policy.to_dict = mock.Mock(return_value={})
        self.mock_client.get_policy = mock.Mock(return_value=fake_policy)

    def test_policy_show(self):
        arglist = ['sp001']
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        self.mock_client.get_policy.assert_called_with('sp001')
        policy = self.mock_client.get_policy('sp001')
        self.assertEqual("2015-03-02T07:40:31", policy.created_at)
        self.assertEqual({}, policy.data)
        self.assertEqual("02f62195-2198-4797-b0a9-877632208527", policy.id)
        self.assertEqual("sp001", policy.name)
        self.assertEqual("42d9e9663331431f97b75e25136307ff", policy.project_id)
        self.assertEqual("senlin.policy.scaling-1.0", policy.type)
        self.assertIsNone(policy.updated_at)

    def test_policy_show_not_found(self):
        arglist = ['sp001']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_policy.side_effect = sdk_exc.ResourceNotFound()
        self.assertRaises(exc.CommandError, self.cmd.take_action, parsed_args)


class TestPolicyCreate(TestPolicy):
    spec_path = 'senlinclient/tests/test_specs/deletion_policy.yaml'
    defaults = {
        "name": "my_policy",
        "spec": {
            "version": 1,
            "type": "senlin.policy.deletion",
            "description": "A policy for choosing victim node(s) from a "
                           "cluster for deletion.",
            "properties": {
                "destroy_after_deletion": True,
                "grace_period": 60,
                "reduce_desired_capacity": False,
                "criteria": "OLDEST_FIRST"
            }
        }
    }

    def setUp(self):
        super(TestPolicyCreate, self).setUp()
        self.cmd = osc_policy.CreatePolicy(self.app, None)
        fake_policy = mock.Mock(
            created_at="2016-02-21T02:38:36",
            data={},
            domain_id=None,
            id="9f779ddf-744e-48bd-954c-acef7e11116c",
            project_id="5f1cc92b578e4e25a3b284179cf20a9b",
            spec={
                "description": "A policy for choosing victim node(s) from a "
                               "cluster for deletion.",
                "properties": {
                    "criteria": "OLDEST_FIRST",
                    "destroy_after_deletion": True,
                    "grace_period": 60,
                    "reduce_desired_capacity": False
                },
                "type": "senlin.policy.deletion",
                "version": 1.0
            },
            type="senlin.policy.deletion-1.0",
            updated_at=None,
            user_id="2d7aca950f3e465d8ef0c81720faf6ff"
        )
        fake_policy.name = "my_policy"
        fake_policy.to_dict = mock.Mock(return_value={})
        self.mock_client.create_policy = mock.Mock(return_value=fake_policy)
        self.mock_client.get_policy = mock.Mock(return_value=fake_policy)

    def test_policy_create_defaults(self):
        arglist = ['my_policy', '--spec-file', self.spec_path]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.create_policy.assert_called_with(**self.defaults)


class TestPolicyUpdate(TestPolicy):

    def setUp(self):
        super(TestPolicyUpdate, self).setUp()
        self.cmd = osc_policy.UpdatePolicy(self.app, None)
        fake_policy = mock.Mock(
            created_at="2016-02-21T02:38:36",
            data={},
            domain_id=None,
            id="9f779ddf-744e-48bd-954c-acef7e11116c",
            project_id="5f1cc92b578e4e25a3b284179cf20a9b",
            spec={
                "description": "A policy for choosing victim node(s) from a "
                               "cluster for deletion.",
                "properties": {
                    "criteria": "OLDEST_FIRST",
                    "destroy_after_deletion": True,
                    "grace_period": 60,
                    "reduce_desired_capacity": False
                },
                "type": "senlin.policy.deletion",
                "version": 1.0
            },
            type="senlin.policy.deletion-1.0",
            updated_at=None,
            user_id="2d7aca950f3e465d8ef0c81720faf6ff"
        )
        fake_policy.name = "new_policy"
        fake_policy.to_dict = mock.Mock(return_value={})
        self.mock_client.update_policy = mock.Mock(return_value=fake_policy)
        self.mock_client.get_policy = mock.Mock(return_value=fake_policy)
        self.mock_client.find_policy = mock.Mock(return_value=fake_policy)

    def test_policy_update_defaults(self):
        arglist = ['--name', 'new_policy', '9f779ddf']
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        self.mock_client.update_policy.assert_called_with(
            '9f779ddf-744e-48bd-954c-acef7e11116c', name="new_policy")

    def test_policy_update_not_found(self):
        arglist = ['--name', 'new_policy', 'c6b8b252']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.find_policy.return_value = None
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Policy not found: c6b8b252', str(error))


class TestPolicyDelete(TestPolicy):
    def setUp(self):
        super(TestPolicyDelete, self).setUp()
        self.cmd = osc_policy.DeletePolicy(self.app, None)
        self.mock_client.delete_policy = mock.Mock()

    def test_policy_delete(self):
        arglist = ['policy1', 'policy2', 'policy3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_policy.assert_has_calls(
            [mock.call('policy1', False), mock.call('policy2', False),
             mock.call('policy3', False)]
        )

    def test_policy_delete_force(self):
        arglist = ['policy1', 'policy2', 'policy3', '--force']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.delete_policy.assert_has_calls(
            [mock.call('policy1', False), mock.call('policy2', False),
             mock.call('policy3', False)]
        )

    def test_policy_delete_not_found(self):
        arglist = ['my_policy']
        self.mock_client.delete_policy.side_effect = sdk_exc.ResourceNotFound
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertIn('Failed to delete 1 of the 1 specified policy(s).',
                      str(error))

    def test_policy_delete_one_found_one_not_found(self):
        arglist = ['policy1', 'policy2']
        self.mock_client.delete_policy.side_effect = (
            [None, sdk_exc.ResourceNotFound]
        )
        parsed_args = self.check_parser(self.cmd, arglist, [])
        error = self.assertRaises(exc.CommandError,
                                  self.cmd.take_action, parsed_args)
        self.mock_client.delete_policy.assert_has_calls(
            [mock.call('policy1', False), mock.call('policy2', False)]
        )
        self.assertEqual('Failed to delete 1 of the 2 specified policy(s).',
                         str(error))

    @mock.patch('sys.stdin', spec=six.StringIO)
    def test_policy_delete_prompt_yes(self, mock_stdin):
        arglist = ['my_policy']
        mock_stdin.isatty.return_value = True
        mock_stdin.readline.return_value = 'y'
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        mock_stdin.readline.assert_called_with()
        self.mock_client.delete_policy.assert_called_with('my_policy',
                                                          False)

    @mock.patch('sys.stdin', spec=six.StringIO)
    def test_policy_delete_prompt_no(self, mock_stdin):
        arglist = ['my_policy']
        mock_stdin.isatty.return_value = True
        mock_stdin.readline.return_value = 'n'
        parsed_args = self.check_parser(self.cmd, arglist, [])

        self.cmd.take_action(parsed_args)

        mock_stdin.readline.assert_called_with()
        self.mock_client.delete_policy.assert_not_called()


class TestPolicyValidate(TestPolicy):
    spec_path = 'senlinclient/tests/test_specs/deletion_policy.yaml'
    defaults = {
        "spec": {
            "version": 1,
            "type": "senlin.policy.deletion",
            "description": "A policy for choosing victim node(s) from a "
                           "cluster for deletion.",
            "properties": {
                "destroy_after_deletion": True,
                "grace_period": 60,
                "reduce_desired_capacity": False,
                "criteria": "OLDEST_FIRST"
            }
        }
    }

    def setUp(self):
        super(TestPolicyValidate, self).setUp()
        self.cmd = osc_policy.ValidatePolicy(self.app, None)
        fake_policy = mock.Mock(
            created_at=None,
            data={},
            domain_id=None,
            id=None,
            project_id="5f1cc92b578e4e25a3b284179cf20a9b",
            spec={
                "description": "A policy for choosing victim node(s) from a "
                               "cluster for deletion.",
                "properties": {
                    "criteria": "OLDEST_FIRST",
                    "destroy_after_deletion": True,
                    "grace_period": 60,
                    "reduce_desired_capacity": False
                },
                "type": "senlin.policy.deletion",
                "version": 1.0
            },
            type="senlin.policy.deletion-1.0",
            updated_at=None,
            user_id="2d7aca950f3e465d8ef0c81720faf6ff"
        )
        fake_policy.name = "validated_policy"
        fake_policy.to_dict = mock.Mock(return_value={})
        self.mock_client.validate_policy = mock.Mock(return_value=fake_policy)

    def test_policy_validate(self):
        arglist = ['--spec-file', self.spec_path]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.validate_policy.assert_called_with(**self.defaults)

        policy = self.mock_client.validate_policy(**self.defaults)

        self.assertEqual("5f1cc92b578e4e25a3b284179cf20a9b", policy.project_id)
        self.assertEqual({}, policy.data)
        self.assertIsNone(policy.id)
        self.assertEqual("validated_policy", policy.name)
        self.assertEqual("senlin.policy.deletion-1.0", policy.type)
        self.assertIsNone(policy.updated_at)
