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
from openstack.identity import identity_service


class SenlinConnection(connection.Connection):
    '''Connection object
    It has 'session' property
    '''
    def __init__(**kwargs):
        ''' openstacksdk expects the followin arguments
        auth_plugin
        auth_url
        project_name
        domain_name
        project_domain_name
        user_domain_name
        user_name
        password
        verify
        token
        '''
        preference = kwargs.pop('user_preferences', {})
        super(SenlinConnection, self).__init__(preference=preference, **kwargs)



def run_create(connection, **kwargs):
    cls = senlinclient.v1.client.
    obj = cls.new(**kwargs)
    obj.create(sess)


def run_get(connection, **kwargs):
    sess = conneciton.session
    obj = cls.new(**kwargs)
    obj.get(sess)


def run_list(connection):
    sess = connection.session
    return cls.list(sess, path_args=**kwargs)
