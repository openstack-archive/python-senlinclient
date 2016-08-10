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
from openstack import exceptions
from openstack import profile
from openstack import resource as base

from senlinclient.common import exc

# Alias here for consistency
prop = base.prop


class ProfileAction(argparse.Action):
    """A custom action to parse user preferences as key=value pairs

    Stores results in users preferences object.
    """
    prof = profile.Profile()

    @classmethod
    def env(cls, *vars):
        for v in vars:
            values = os.environ.get(v, None)
            if values is None:
                continue
            cls.set_option(v, values)
            return cls.prof
        return cls.prof

    @classmethod
    def set_option(cls, var, values):
        if var == '--os-extensions':
            cls.prof.load_extension(values)
            return
        if var == 'OS_REGION_NAME':
            var = 'region'
        var = var.replace('--os-api-', '')
        var = var.replace('OS_API_', '')
        var = var.lower()
        for kvp in values.split(','):
            if '=' in kvp:
                service, value = kvp.split('=')
            else:
                service = cls.prof.ALL
                value = kvp
            if var == 'name':
                cls.prof.set_name(service, value)
            elif var == 'region':
                cls.prof.set_region(service, value)
            elif var == 'version':
                cls.prof.set_version(service, value)
            elif var == 'interface':
                cls.prof.set_interface(service, value)

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, ProfileAction.prof)
        self.set_option(option_string, values)


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
