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

import collections
import mock
import six
import sys
import testtools

from heatclient.common import template_utils
from senlinclient.common import exc
from senlinclient.common.i18n import _
from senlinclient.common import utils
from six import moves


class CaptureStdout(object):
    """Context manager for capturing stdout from statements in its block."""
    def __enter__(self):
        self.real_stdout = sys.stdout
        self.stringio = moves.StringIO()
        sys.stdout = self.stringio
        return self

    def __exit__(self, *args):
        sys.stdout = self.real_stdout
        self.stringio.seek(0)
        self.read = self.stringio.read


class shellTest(testtools.TestCase):

    def test_format_parameter(self):
        params = ['status=ACTIVE;name=cluster1']
        format_params = {'status': 'ACTIVE', 'name': 'cluster1'}
        self.assertEqual(format_params,
                         utils.format_parameters(params))

    def test_format_parameter_split(self):
        params = ['status=ACTIVE', 'name=cluster1']
        format_params = {'status': 'ACTIVE', 'name': 'cluster1'}
        self.assertEqual(format_params,
                         utils.format_parameters(params))

    def test_format_parameter_none(self):
        self.assertEqual({}, utils.format_parameters(None))

    def test_format_parameter_bad_format(self):
        params = ['status:ACTIVE;name:cluster1']
        ex = self.assertRaises(exc.CommandError,
                               utils.format_parameters,
                               params)
        msg = _('Malformed parameter(status:ACTIVE). '
                'Use the key=value format.')
        self.assertEqual(msg, six.text_type(ex))

    @mock.patch.object(template_utils,
                       'process_multiple_environments_and_files')
    @mock.patch.object(template_utils, 'get_template_contents')
    def test_process_stack_spec(self, mock_get_temp, mock_process):
        spec = {
            'template': 'temp.yaml',
            'disable_rollback': True,
            'context': {
                'region_name': 'RegionOne'
            },
        }
        tpl_files = {'fake_key1': 'fake_value1'}
        template = mock.Mock()
        mock_get_temp.return_value = tpl_files, template
        env_files = {'fake_key2': 'fake_value2'}
        env = mock.Mock()
        mock_process.return_value = env_files, env
        new_spec = utils.process_stack_spec(spec)
        stack_spec = {
            'disable_rollback': True,
            'context': {
                'region_name': 'RegionOne',
            },
            'parameters': {},
            'timeout': 60,
            'template': template,
            'files': {
                'fake_key1': 'fake_value1',
                'fake_key2': 'fake_value2',
            },
            'environment': env
        }
        self.assertEqual(stack_spec, new_spec)
        mock_get_temp.assert_called_once_with(template_file='temp.yaml')
        mock_process.assert_called_once_with(env_paths=None)

    def test_json_formatter_with_empty_json(self):
        params = {}
        self.assertEqual('{}', utils.json_formatter(params))

    def test_list_formatter_with_list(self):
        params = ['foo', 'bar']
        self.assertEqual('foo\nbar', utils.list_formatter(params))

    def test_list_formatter_with_empty_list(self):
        params = []
        self.assertEqual('', utils.list_formatter(params))


class PrintListTestCase(testtools.TestCase):

    def test_print_list_with_list(self):
        Row = collections.namedtuple('Row', ['foo', 'bar'])
        to_print = [Row(foo='fake_foo1', bar='fake_bar2'),
                    Row(foo='fake_foo2', bar='fake_bar1')]
        with CaptureStdout() as cso:
            utils.print_list(to_print, ['foo', 'bar'])
        # Output should be sorted by the first key (foo)
        self.assertEqual("""\
+-----------+-----------+
| foo       | bar       |
+-----------+-----------+
| fake_foo1 | fake_bar2 |
| fake_foo2 | fake_bar1 |
+-----------+-----------+
""", cso.read())

    def test_print_list_with_None_data(self):
        Row = collections.namedtuple('Row', ['foo', 'bar'])
        to_print = [Row(foo='fake_foo1', bar='None'),
                    Row(foo='fake_foo2', bar='fake_bar1')]
        with CaptureStdout() as cso:
            utils.print_list(to_print, ['foo', 'bar'])
        # Output should be sorted by the first key (foo)
        self.assertEqual("""\
+-----------+-----------+
| foo       | bar       |
+-----------+-----------+
| fake_foo1 | None      |
| fake_foo2 | fake_bar1 |
+-----------+-----------+
""", cso.read())

    def test_print_list_with_list_sortby(self):
        Row = collections.namedtuple('Row', ['foo', 'bar'])
        to_print = [Row(foo='fake_foo1', bar='fake_bar2'),
                    Row(foo='fake_foo2', bar='fake_bar1')]
        with CaptureStdout() as cso:
            utils.print_list(to_print, ['foo', 'bar'], sortby_index=1)
        # Output should be sorted by the first key (bar)
        self.assertEqual("""\
+-----------+-----------+
| foo       | bar       |
+-----------+-----------+
| fake_foo2 | fake_bar1 |
| fake_foo1 | fake_bar2 |
+-----------+-----------+
""", cso.read())

    def test_print_list_with_list_no_sort(self):
        Row = collections.namedtuple('Row', ['foo', 'bar'])
        to_print = [Row(foo='fake_foo2', bar='fake_bar1'),
                    Row(foo='fake_foo1', bar='fake_bar2')]
        with CaptureStdout() as cso:
            utils.print_list(to_print, ['foo', 'bar'], sortby_index=None)
        # Output should be in the order given
        self.assertEqual("""\
+-----------+-----------+
| foo       | bar       |
+-----------+-----------+
| fake_foo2 | fake_bar1 |
| fake_foo1 | fake_bar2 |
+-----------+-----------+
""", cso.read())

    def test_print_list_with_generator(self):
        Row = collections.namedtuple('Row', ['foo', 'bar'])

        def gen_rows():
            for row in [Row(foo='fake_foo1', bar='fake_bar2'),
                        Row(foo='fake_foo2', bar='fake_bar1')]:
                yield row
        with CaptureStdout() as cso:
            utils.print_list(gen_rows(), ['foo', 'bar'])
        self.assertEqual("""\
+-----------+-----------+
| foo       | bar       |
+-----------+-----------+
| fake_foo1 | fake_bar2 |
| fake_foo2 | fake_bar1 |
+-----------+-----------+
""", cso.read())


class PrintDictTestCase(testtools.TestCase):

    def test_print_dict(self):
        data = {'foo': 'fake_foo', 'bar': 'fake_bar'}
        with CaptureStdout() as cso:
            utils.print_dict(data)
        # Output should be sorted by the Property
        self.assertEqual("""\
+----------+----------+
| Property | Value    |
+----------+----------+
| bar      | fake_bar |
| foo      | fake_foo |
+----------+----------+
""", cso.read())
