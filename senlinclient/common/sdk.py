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

from openstack import connection
from openstack import exceptions
from openstack import profile

from senlinclient.common import exc


def create_connection(prof=None, user_agent=None, **kwargs):
        if not prof:
            prof = profile.Profile()
        interface = kwargs.pop('interface', None)
        region_name = kwargs.pop('region_name', None)
        if interface:
            prof.set_interface('clustering', interface)
        if region_name:
            prof.set_region('clustering', region_name)

        prof.set_api_version('clustering', '1.2')
        try:
            conn = connection.Connection(profile=prof, user_agent=user_agent,
                                         **kwargs)
        except exceptions.HttpException as ex:
            exc.parse_exception(ex.details)

        return conn
