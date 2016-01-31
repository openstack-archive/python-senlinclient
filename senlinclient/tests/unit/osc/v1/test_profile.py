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

import mock

from openstack.cluster.v1 import profile as sdk_profile
from openstack import exceptions as sdk_exc
from openstackclient.common import exceptions as exc
from openstackclient.common import utils

from senlinclient.osc.v1 import profile as osc_profile
from senlinclient.tests.unit.osc.v1 import fakes


class TestProfile(fakes.TestClusteringv1):
    def setUp(self):
        super(TestProfile, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestProfileShow(TestProfile):
    get_response = {"profile": {
        "created_at": "2015-03-01T14:28:25",
        "domain": 'false',
        "id": "7fa885cd-fa39-4531-a42d-780af95c84a4",
        "metadata": {},
        "name": "test_prof1",
        "project": "42d9e9663331431f97b75e25136307ff",
        "spec": {
            "disable_rollback": 'false',
            "environment": {
                "resource_registry": {
                    "os.heat.server": "OS::Heat::Server"
                }
            },
            "files": {
                "file:///opt/stack/senlin/examples/profiles/test_script.sh":
                    "#!/bin/bash\n\necho \"this is a test script file\"\n"
            },
            "parameters": {},
            "template": {
                "heat_template_version": "2014-10-16",
                "outputs": {
                    "result": {
                        "value": {
                            "get_attr": [
                                "random",
                                "value"
                            ]
                        }
                    }
                },
                "parameters": {
                    "file": {
                        "default": {
                            "get_file": "file:///opt/stack/senlin/"
                                        "examples/profiles/test_script.sh"
                        },
                        "type": "string"
                    }
                },
                "resources": {
                    "random": {
                        "properties": {
                            "length": 64
                        },
                        "type": "OS::Heat::RandomString"
                    }
                },
                "timeout": 60
            },
            "type": "os.heat.stack",
            "version": "1.0"
        },
        "type": "os.heat.stack-1.0",
        "updated_at": 'null',
        "user": "5e5bf8027826429c96af157f68dc9072"
    }}

    def setUp(self):
        super(TestProfileShow, self).setUp()
        self.cmd = osc_profile.ShowProfile(self.app, None)
        self.mock_client.get_profile = mock.Mock(
            return_value=sdk_profile.Profile(None, self.get_response))
        utils.get_dict_properties = mock.Mock(return_value='')

    def test_profile_show(self):
        arglist = ['my_profile']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
        self.mock_client.get_profile.assert_called_with('my_profile')

    def test_profile_show_not_found(self):
        arglist = ['my_profile']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.mock_client.get_profile.side_effect = sdk_exc.ResourceNotFound()
        self.assertRaises(
            exc.CommandError,
            self.cmd.take_action,
            parsed_args)
