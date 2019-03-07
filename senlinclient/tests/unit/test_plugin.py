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

import mock
from openstack import connection as sdk_connection
import testtools

from senlinclient import plugin


class TestPlugin(testtools.TestCase):

    @mock.patch.object(sdk_connection, 'Connection')
    def test_create_connection_with_profile(self, mock_connection):
        class FakeService(object):
            interface = 'public'
            region = 'a_region'
            version = '1'
            api_version = None
            service_type = 'clustering'

        mock_prof = mock.Mock()
        mock_prof.get_services.return_value = [FakeService()]
        mock_conn = mock.Mock()
        mock_connection.return_value = mock_conn
        kwargs = {
            'user_id': '123',
            'password': 'abc',
            'auth_url': 'test_url'
        }
        res = plugin.create_connection(mock_prof, **kwargs)
        mock_connection.assert_called_once_with(
            app_name=None, app_version=None,
            config=mock.ANY,
            clustering_api_version=plugin.CURRENT_API_VERSION,
            **kwargs
        )
        self.assertEqual(mock_conn, res)

    @mock.patch.object(sdk_connection, 'Connection')
    def test_create_connection_without_profile(self, mock_connection):
        mock_conn = mock.Mock()
        mock_connection.return_value = mock_conn
        kwargs = {
            'interface': 'public',
            'region_name': 'RegionOne',
            'user_id': '123',
            'password': 'abc',
            'auth_url': 'test_url'
        }
        res = plugin.create_connection(**kwargs)

        mock_connection.assert_called_once_with(
            app_name=None, app_version=None,
            auth_url='test_url',
            clustering_api_version=plugin.CURRENT_API_VERSION,
            config=None,
            interface='public',
            password='abc',
            region_name='RegionOne',
            user_id='123'
        )
        self.assertEqual(mock_conn, res)
