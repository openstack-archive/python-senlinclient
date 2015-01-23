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

import argparse
import os

from openstack import connection
from openstack import user_preference 
from openstack.identity import identity_service
from openstack import resource as base

# Alias here for consistency
prop = base.prop

class UserPreferenceAction(argparse.Action):
    '''
    A custom action to parse user preferences as key=value pairs

    Stores results in users preferences object.
    '''
    pref = user_preference.UserPreference()

    @classmethod
    def env(cls, *vars):
        for v in vars:
            values = os.environ.get(v, None)
            if values is None:
                continue
            cls.set_option(v, values)
            return cls.pref
        return cls.pref

    @classmethod
    def set_option(cls, var, values):
        if var == 'OS_REGION_NAME':
            var = 'region'
        var = var.replace('--os-api-', '')
        var = var.replace('OS_API_', '')
        var = var.lower()
        for kvp in values.split(','):
            if var == 'region':
                if '=' in kvp:
                    service, value = kvp.split('=')
                else:
                    service = cls.pref.ALL
                    value = kvp
            else:
                if '=' in kvp:
                    service, value = kvp.split('=')
                else:
                    service = cls.pref.ALL
                    value = kvp
            if var == 'name':
                cls.pref.set_name(service, value)
            elif var == 'region':
                cls.pref.set_region(service, value)
            elif var == 'version':
                cls.pref.set_version(service, value)
            elif var == 'visibility':
                cls.pref.set_visibility(service, value)

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, UserPreferenceAction.pref)
        self.set_option(option_string, values)


class Resource(base.Resource):
    '''
    Senlin version of resource.

    These classes are here because the OpenStack SDK base version is making
    some assumptions about operations that cannot be satisfied in Senlin.
    '''
    @classmethod
    def list_short(cls, session, path_args=None, **params):
        '''
        Return a generator that will page through results of GET requests.

        This method bypasses the DB session support and retrieves list that
        is directly exposed by server.
        '''
        if not cls.allow_list:
            raise exceptions.MethodNotSupported('list')

        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path

        resp = session.get(url, service=cls.service, params=params).body
        if cls.resources_key:
            resp = resp[cls.resources_key]

        for data in resp:
            value = cls.existing(**data)
            yield value

    def create(self, session):
        '''
        Overriden version of the create method.
        We want to know more about the object being created, so the response
        should not be just thrown away
        '''
        resp = self.create_by_id(session, self._attrs, self.id, path_args=self)
        self._attrs[self.id_attribute] = resp[self.id_attribute]
        self._reset_dirty()
        return self, resp
