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
from openstack import connection
from openstack import exceptions
from openstack import profile
from openstack import resource as base
from openstack import utils
import os

from six.moves.urllib import parse as url_parse

from senlinclient.common import exc

# Alias here for consistency
prop = base.prop


class ProfileAction(argparse.Action):
    """A custom action to parse user proferences as key=value pairs

    Stores results in users proferences object.
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


class Resource(base.Resource):
    '''Senlin version of resource.

    These classes are here because the OpenStack SDK base version is making
    some assumptions about operations that cannot be satisfied in Senlin.
    '''

    def create(self, session, extra_attrs=False):
        """Create a remote resource from this instance.

        :param extra_attrs: If true, all attributions that
        included in response will be collected and returned
        to user after resource creation

        """
        resp = self.create_by_id(session, self._attrs, self.id, path_args=self)
        self._attrs[self.id_attribute] = resp[self.id_attribute]
        if extra_attrs:
            for attr in resp:
                self._attrs[attr] = resp[attr]
        self._reset_dirty()

        return self

    @classmethod
    def get_data_with_args(cls, session, resource_id, args=None):
        if not cls.allow_retrieve:
            raise exceptions.MethodNotSupported('list')

        url = utils.urljoin(cls.base_path, resource_id)
        if args:
            args.pop('id')
            url = '%s?%s' % (url, url_parse.urlencode(args))
        resp = session.get(url, service=cls.service)
        body = resp.body
        if cls.resource_key:
            body = body[cls.resource_key]

        return body

    def get_with_args(self, session, args=None):
        body = self.get_data_with_args(session, self.id, args=args)

        self._attrs.update(body)
        self._loaded = True

        return self


def create_connection(preferences=None, user_agent=None, **kwargs):
        try:
            conn = connection.Connection(profile=preferences,
                                         user_agent=user_agent,
                                         **kwargs)
        except exceptions.HttpException as ex:
            exc.parse_exception(ex.details)

        return conn
