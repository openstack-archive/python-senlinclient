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

from __future__ import print_function


from heatclient.common import template_utils
from oslo_serialization import jsonutils
from oslo_utils import importutils
import prettytable
import six
import yaml

from senlinclient.common import exc
from senlinclient.common.i18n import _


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

    keys = sorted(d.keys())
    for field in keys:
        value = d[field]
        if not isinstance(value, six.string_types):
            value = jsonutils.dumps(value, indent=2, ensure_ascii=False)
        if value is None:
            value = '-'
        pt.add_row([field, value.strip('"')])

    return pt.get_string()


def nested_dict_formatter(d, column_names):
    return lambda o: format_nested_dict(o, d, column_names)


def json_formatter(js):
    return jsonutils.dumps(js, indent=2, ensure_ascii=False)


def list_formatter(record):
    return '\n'.join(record or [])


def print_action_result(rid, res):
    if res[0] == "OK":
        output = _("accepted by action %s") % res[1]
    else:
        output = _("failed due to '%s'") % res[1]
    print(_(" %(cid)s: %(output)s") % {"cid": rid, "output": output})


def format_parameters(params, parse_semicolon=True):
    """Reformat parameters into dict of format expected by the API."""
    if not params or params == ['{}']:
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


def format_json_parameter(param):
    '''Return JSON dict from JSON formatted param.

    :parameter param  JSON formatted string
    :return JSON dict
    '''
    if not param:
        return {}

    try:
        return jsonutils.loads(param)
    except ValueError:
        msg = _('Malformed parameter(%s). Use the JSON format.') % param
        raise exc.CommandError(msg)


def get_spec_content(filename):
    with open(filename, 'r') as f:
        try:
            data = yaml.safe_load(f)
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
        'context': spec.get('context', {}),
        'parameters': spec.get('parameters', {}),
        'timeout': spec.get('timeout', 60),
        'template': template,
        'files': dict(list(tpl_files.items()) + list(env_files.items())),
        'environment': env
    }

    return new_spec
