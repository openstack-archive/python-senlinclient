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

from heatclient.common import template_utils

from oslo_serialization import jsonutils
from oslo_utils import importutils
import prettytable
import six
import yaml

from senlinclient.common import exc
from senlinclient.common.i18n import _
from senlinclient.openstack.common import cliutils


# Using common methods from oslo cliutils
# Will change when the module graduates
arg = cliutils.arg
env = cliutils.env
print_list = cliutils.print_list
exit = cliutils.exit

supported_formats = {
    "json": lambda x: jsonutils.dumps(x, indent=2),
    "yaml": lambda x: yaml.safe_dump(x, default_flow_style=False)
}


def import_versioned_module(version, submodule=None):
    module = 'senlinclient.v%s' % version
    if submodule:
        module = '.'.join((module, submodule))
    return importutils.import_module(module)


def format_nested_dict(d, fields, column_names):
    if d is None:
        return ''
    pt = prettytable.PrettyTable(caching=False, print_empty=False,
                                 header=True, field_names=column_names)
    for n in column_names:
        pt.align[n] = 'l'

    for field in d.keys():
        value = d[field]
        if value is six.string_types:
            pt.add_row([field, value])
        else:
            pt.add_row([field, jsonutils.dumps(value, indent=2,
                                               ensure_ascii=False)])

    return pt.get_string()


def nested_dict_formatter(d, column_names):
    return lambda o: format_nested_dict(o, d, column_names)


def json_formatter(js):
    return jsonutils.dumps(js, indent=2, ensure_ascii=False)


def list_formatter(record):
    return '\n'.join(record or [])


def print_list(objs, fields, formatters=None, sortby_index=0,
               mixed_case_fields=None, field_labels=None):
    # This wrapper is needed because sdk may yield a generator that will
    # escape the exception catching previously
    if not objs:
        objs = []

    try:
        cliutils.print_list(objs, fields, formatters=formatters,
                            sortby_index=sortby_index,
                            mixed_case_fields=mixed_case_fields,
                            field_labels=field_labels)
    except Exception as ex:
        exc.parse_exception(ex)


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


def format_parameters(params, parse_semicolon=True):
    '''Reformat parameters into dict of format expected by the API.'''
    if not params:
        return {}

    if parse_semicolon:
        # expect multiple invocations of --parameters but fall back to ';'
        # delimited if only one --parameters is specified
        if len(params) == 1:
            params = params[0].split(';')

    parameters = {}
    for p in params:
        try:
            (n, v) = p.split(('='), 1)
        except ValueError:
            msg = _('Malformed parameter(%s). Use the key=value format.') % p
            raise exc.CommandError(msg)

        if n not in parameters:
            parameters[n] = v
        else:
            if not isinstance(parameters[n], list):
                parameters[n] = [parameters[n]]
            parameters[n].append(v)

    return parameters


def get_spec_content(filename):
    with open(filename, 'r') as f:
        try:
            data = yaml.load(f)
        except Exception as ex:
            raise exc.CommandError(_('The specified file is not a valid '
                                     'YAML file: %s') % six.text_type(ex))
    return data


def process_stack_spec(spec):
    # Heat stack is a headache, because it demands for client side file
    # content processing
    try:
        tmplfile = spec.get('template', None)
    except AttributeError as ex:
        raise exc.FileFormatError(_('The specified file is not a valid '
                                    'YAML file: %s') % six.text_type(ex))
    if not tmplfile:
        raise exc.FileFormatError(_('No template found in the given '
                                    'spec file'))

    tpl_files, template = template_utils.get_template_contents(
        template_file=tmplfile)

    env_files, env = template_utils.process_multiple_environments_and_files(
        env_paths=spec.get('environment', None))

    new_spec = {
        # TODO(Qiming): add context support
        'disable_rollback': spec.get('disable_rollback', True),
        'context':  spec.get('context', {}),
        'parameters': spec.get('parameters', {}),
        'timeout': spec.get('timeout', 60),
        'template': template,
        'files': dict(list(tpl_files.items()) + list(env_files.items())),
        'environment': env
    }

    return new_spec


def format_output(output, format='yaml'):
    fmt = format.lower()
    try:
        return supported_formats[fmt](output)
    except KeyError:
        raise exc.HTTPUnsupported(_('The format(%s) is unsupported.')
                                  % fmt)
