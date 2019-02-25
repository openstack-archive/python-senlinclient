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

import sys

import mock
from osc_lib.tests import utils
import requests

from oslo_serialization import jsonutils

AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"
USERNAME = "itchy"
PASSWORD = "scratchy"

TEST_RESPONSE_DICT_V3 = {
    "token": {
        "audit_ids": [
            "a"
        ],
        "catalog": [
        ],
        "expires_at": "2034-09-29T18:27:15.978064Z",
        "extras": {},
        "issued_at": "2014-09-29T17:27:15.978097Z",
        "methods": [
            "password"
        ],
        "project": {
            "domain": {
                "id": "default",
                "name": "Default"
            },
            "id": "bbb",
            "name": "project"
        },
        "roles": [
        ],
        "user": {
            "domain": {
                "id": "default",
                "name": "Default"
            },
            "id": "aaa",
            "name": USERNAME
        }
    }
}
TEST_VERSIONS = {
    "versions": {
        "values": [
            {
                "id": "v3.0",
                "links": [
                    {
                        "href": AUTH_URL,
                        "rel": "self"
                    }
                ],
                "media-types": [
                    {
                        "base": "application/json",
                        "type": "application/vnd.openstack.identity-v3+json"
                    },
                    {
                        "base": "application/xml",
                        "type": "application/vnd.openstack.identity-v3+xml"
                    }
                ],
                "status": "stable",
                "updated": "2013-03-06T00:00:00Z"
            }
        ]
    }
}


class FakeStdout(object):
    def __init__(self):
        self.content = []

    def write(self, text):
        self.content.append(text)

    def make_string(self):
        result = ''
        for line in self.content:
            result = result + line
        return result


class FakeApp(object):
    def __init__(self, _stdout):
        self.stdout = _stdout
        self.client_manager = None
        self.stdin = sys.stdin
        self.stdout = _stdout or sys.stdout
        self.stderr = sys.stderr


class FakeClient(object):
    def __init__(self, **kwargs):
        self.auth_url = kwargs['auth_url']
        self.token = kwargs['token']


class FakeClientManager(object):
    def __init__(self):
        self.compute = None
        self.identity = None
        self.image = None
        self.object_store = None
        self.volume = None
        self.network = None
        self.session = None
        self.auth_ref = None


class FakeModule(object):
    def __init__(self, name, version):
        self.name = name
        self.__version__ = version


class FakeResource(object):
    def __init__(self, manager, info, loaded=False):
        self.manager = manager
        self._info = info
        self._add_details(info)
        self._loaded = loaded

    def _add_details(self, info):
        for (k, v) in info.items():
            setattr(self, k, v)

    def __repr__(self):
        reprkeys = sorted(k for k in self.__dict__.keys() if k[0] != '_' and
                          k != 'manager')
        info = ", ".join("%s=%s" % (k, getattr(self, k)) for k in reprkeys)
        return "<%s %s>" % (self.__class__.__name__, info)


class FakeResponse(requests.Response):
    def __init__(self, headers={}, status_code=200, data=None, encoding=None):
        super(FakeResponse, self).__init__()

        self.status_code = status_code

        self.headers.update(headers)
        self._content = jsonutils.dump_as_bytes(data)


class FakeClusteringv1Client(object):
    def __init__(self, **kwargs):
        self.http_client = mock.Mock()
        self.http_client.auth_token = kwargs['token']
        self.profiles = FakeResource(None, {})


class TestClusteringv1(utils.TestCommand):
    def setUp(self):
        super(TestClusteringv1, self).setUp()

        self.app.client_manager.clustering = FakeClusteringv1Client(
            token=AUTH_TOKEN, auth_url=AUTH_URL
        )
