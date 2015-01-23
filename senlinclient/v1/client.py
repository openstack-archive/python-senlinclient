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

import inspect
import json
import uuid

from openstack import exceptions as exc
from openstack.identity import identity_service
from openstack.network.v2 import thin as thins
from openstack import transport as trans
from senlinclient.common import exc as client_exc

class Client(object):
    def __init__(self, session):
        self.session = session
        self.auth = session.authenticator

    def get_options(self, options):
        return json.loads(options)

    def transport(self, opts):
        '''Create a transport given some options.
        E.g.
        https://region-a.geo-1.identity.hpcloudsvc.com:35357/
        '''
        argument = opts.argument
        xport = trans.Transport(verify=opts.verify)
        return xport.get(argument).text

    def thin(self):
        # Authenticate should be done before this.
        request = thins.Thin()
        for obj in request.list_networks(self.session):
            print(obj['id'])

    def session(self, cls_name):
        if cls_name is None:
            raise Exception("A cls name argument must be specified")

        filtration = identity_service.IdentityService()
        return self.session.get(cls_name, service=filtration).text

    def authenticate(self, options):
        xport = trans.Transport(verify=options.verify)
        print(self.auth.authorize(xport))
        return xport

    def list(self, cls, options=None):
        try:
            result = cls.list(self.session, path_args=None, **options)
            return result
        except exc.HttpException as ex:
            print(ex)
            return None

    def list_short(self, cls, options=None):
        try:
            return cls.list_short(self.session, path_args=None, **options)
        except exc.HttpException as ex:
            print(ex)
            return None

    def create(self, cls, params):
        obj = cls.new(**params)
        return obj.create(self.session)

    def get(self, cls, options=None):
        try:
            obj = cls.new(**options)
            obj.get(self.session)
            return obj
        except exc.HttpException as ex:
            raise client_exc.HTTPException(ex.details)

    def find(self, cls, options):
        return cls.find(self.session, options)

    def update(self, cls, options):
        kwargs = self.get_options(options)
        obj = cls.new(**kwargs)
        obj.update(self.session)

    def delete(self, cls, options):
        obj = cls.new(**options)
        obj.delete(self.session)

    def head(self, cls, options):
        kwargs = self.get_options(options)
        obj = cls.new(**kwargs)
        obj.head(self.session)
        return obj

    def action(self, cls, options):
        '''Examples:
        <cls> --data '{"alarm_id": "33109eea-24dd-45ff-93f7-82292d1dd38c",
                       "action": "change_state",
                       "action_args": {"next_state": "insufficient data"}'

        <cls> --data '{"id": "a1369557-748f-429c-bd3e-fc385aacaec7",
                       "action": "reboot",
                       "action_args": {"reboot_type": "SOFT"}}'
        '''
        def filter_args(method, params):
            expected_args = inspect.getargspec(method).args
            accepted_args = ([a for a in expected_args if a != 'self'])
            filtered_args = [{d: params[d]} for d in accepted_args]
            return filtered_args

        def invoke_method(target, method_name, params):
            action = getattr(target, method_name)
            filtered_args = filter_args(action, params)
            reply = action(**filtered_args)
            return reply

        kwargs = self.get_options(options)
        action = kwargs.pop('action')
        if 'action_args' in kwargs:
            args = kwargs.pop('action_args')
        else:
            args = {}

        args.update(session=self.session)
        obj = cls.new(**kwargs)
        reply = invoke_method(obj, action, args)
        return reply
