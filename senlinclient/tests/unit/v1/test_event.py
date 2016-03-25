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

from openstack.cluster.v1 import event as sdk_event
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc

from senlinclient.tests.unit.v1 import fakes
from senlinclient.v1 import event as osc_event


class TestEvent(fakes.TestClusteringv1):
    def setUp(self):
        super(TestEvent, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestEventList(TestEvent):

    columns = ['id', 'timestamp', 'obj_type', 'obj_id', 'obj_name', 'action',
               'status', 'status_reason', 'level']

    response = {"events": [
        {
            "action": "create",
            "cluster_id": 'null',
            "id": "2d255b9c-8f36-41a2-a137-c0175ccc29c3",
            "level": "20",
            "obj_id": "0df0931b-e251-4f2e-8719-4ebfda3627ba",
            "obj_name": "node009",
            "obj_type": "NODE",
            "project": "6e18cc2bdbeb48a5b3cad2dc499f6804",
            "status": "CREATING",
            "status_reason": "Initializing",
            "timestamp": "2015-03-05T08:53:15",
            "user": "a21ded6060534d99840658a777c2af5a"
        }
    ]}

    defaults = {
        'global_project': False,
        'marker': None,
        'limit': None,
        'sort': None,
    }

    def setUp(self):
        super(TestEventList, self).setUp()
        self.cmd = osc_event.ListEvent(self.app, None)
        self.mock_client.events = mock.Mock(
            return_value=sdk_event.Event(None, {}))

    def test_event_list_defaults(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.events.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_event_list_full_id(self):
        arglist = ['--full-id']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.events.assert_called_with(**self.defaults)
        self.assertEqual(self.columns, columns)

    def test_event_list_limit(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['limit'] = '3'
        arglist = ['--limit', '3']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.events.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_event_list_sort(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:asc'
        arglist = ['--sort', 'name:asc']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.events.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_event_list_sort_invalid_key(self):
        self.mock_client.events = mock.Mock(
            return_value=self.response)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'bad_key'
        arglist = ['--sort', 'bad_key']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.events.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_event_list_sort_invalid_direction(self):
        self.mock_client.events = mock.Mock(
            return_value=self.response)
        kwargs = copy.deepcopy(self.defaults)
        kwargs['sort'] = 'name:bad_direction'
        arglist = ['--sort', 'name:bad_direction']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.events.side_effect = sdk_exc.HttpException()
        self.assertRaises(sdk_exc.HttpException,
                          self.cmd.take_action, parsed_args)

    def test_event_list_filter(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['name'] = 'my_event'
        arglist = ['--filter', 'name=my_event']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.events.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)

    def test_event_list_marker(self):
        kwargs = copy.deepcopy(self.defaults)
        kwargs['marker'] = 'a9448bf6'
        arglist = ['--marker', 'a9448bf6']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.events.assert_called_with(**kwargs)
        self.assertEqual(self.columns, columns)


class TestEventShow(TestEvent):
    get_response = {"event": {
        "action": "create",
        "cluster_id": 'null',
        "id": "2d255b9c-8f36-41a2-a137-c0175ccc29c3",
        "level": "20",
        "obj_id": "0df0931b-e251-4f2e-8719-4ebfda3627ba",
        "obj_name": "node009",
        "obj_type": "NODE",
        "project": "6e18cc2bdbeb48a5b3cad2dc499f6804",
        "status": "CREATING",
        "status_reason": "Initializing",
        "timestamp": "2015-03-05T08:53:15",
        "user": "a21ded6060534d99840658a777c2af5a"
    }}

    def setUp(self):
        super(TestEventShow, self).setUp()
        self.cmd = osc_event.ShowEvent(self.app, None)
        self.mock_client.get_event = mock.Mock(
            return_value=sdk_event.Event(None, self.get_response))

    def test_event_show(self):
        arglist = ['my_event']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_event.assert_called_with('my_event')

    def test_event_show_not_found(self):
        arglist = ['my_event']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_event.side_effect = sdk_exc.ResourceNotFound()
        error = self.assertRaises(exc.CommandError, self.cmd.take_action,
                                  parsed_args)
        self.assertEqual('Event not found: my_event', str(error))
