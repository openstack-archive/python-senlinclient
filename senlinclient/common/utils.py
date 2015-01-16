# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
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

import prettytable
import yaml

from oslo_serialization import jsonutils
from oslo_utils import importutils

from senlinclient.openstack.common import cliutils


# Using common methods from oslo cliutils
# Will change when the module graduates
arg = cliutils.arg
env = cliutils.env
print_list = cliutils.print_list
exit = cliutils.exit

supported_formats = {
    "json": lambda x: jsonutils.dumps(x, indent=2),
    "yaml": yaml.safe_dump
}


def import_versioned_module(version, submodule=None):
    module = 'senlinclient.v%s' % version
    if submodule:
        module = '.'.join((module, submodule))
    return importutils.import_module(module)


def json_formatter(js):
    return jsonutils.dumps(js, indent=2, ensure_ascii=False)


def print_dict(d, formatters=None):
    formatters = formatters or {}
    pt = prettytable.PrettyTable(['Property', 'Value'],
                                 caching=False, print_empty=False)
    pt.align = 'l'

    for field in d.keys():
        if field in formatters:
            pt.add_row([field, formatters[field](d[field])])
        else:
            pt.add_row([field, d[field]])
    print(pt.get_string(sortby='Property'))
