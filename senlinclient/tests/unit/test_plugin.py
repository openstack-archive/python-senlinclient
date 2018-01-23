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
from openstack import profile as sdk_profile
import testtools

from senlinclient import plugin


class TestPlugin(testtools.TestCase):

    @mock.patch.object(sdk_connection, 'Connection')
    def test_create_connection_with_profile(self, mock_connection):
        mock_prof = mock.Mock()
        mock_conn = mock.Mock()
        mock_connection.return_value = mock_conn
        kwargs = {
            'user_id': '123',
            'password': 'abc',
            'auth_url': 'test_url'
        }
        res = plugin.create_connection(mock_prof, **kwargs)
        mock_connection.assert_called_once_with(profile=mock_prof,
                                                user_agent=None,
                                                user_id='123',
                                                password='abc',
                                                auth_url='test_url')
        self.assertEqual(mock_conn, res)

    @mock.patch.object(sdk_connection, 'Connection')
    @mock.patch.object(sdk_profile, 'Profile')
    def test_create_connection_without_profile(self, mock_profile,
                                               mock_connection):
        mock_prof = mock.Mock()
        mock_conn = mock.Mock()
        mock_profile.return_value = mock_prof
        mock_connection.return_value = mock_conn
        kwargs = {
            'interface': 'public',
            'region_name': 'RegionOne',
            'user_id': '123',
            'password': 'abc',
            'auth_url': 'test_url'
        }
        res = plugin.create_connection(**kwargs)

        mock_prof.set_interface.assert_called_once_with('clustering', 'public')
        mock_prof.set_region.assert_called_once_with('clustering', 'RegionOne')
        mock_connection.assert_called_once_with(profile=mock_prof,
                                                user_agent=None,
                                                user_id='123',
                                                password='abc',
                                                auth_url='test_url')
        self.assertEqual(mock_conn, res)
