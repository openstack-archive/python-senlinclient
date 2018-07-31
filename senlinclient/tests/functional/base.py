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

import os
import six
import time

from oslo_utils import uuidutils
from tempest.lib.cli import base
from tempest.lib.cli import output_parser
from tempest.lib import exceptions as tempest_lib_exc


class OpenStackClientTestBase(base.ClientTestBase):
    """Command line client base functions."""

    def setUp(self):
        super(OpenStackClientTestBase, self).setUp()
        self.parser = output_parser

    def _get_clients(self):
        cli_dir = os.environ.get(
            'OS_SENLINCLIENT_EXEC_DIR',
            os.path.join(os.path.abspath('.'), '.tox/functional/bin'))

        return base.CLIClient(
            username=os.environ.get('OS_USERNAME'),
            password=os.environ.get('OS_PASSWORD'),
            tenant_name=os.environ.get('OS_TENANT_NAME'),
            uri=os.environ.get('OS_AUTH_URL'),
            cli_dir=cli_dir)

    def openstack(self, *args, **kwargs):
        return self.clients.openstack(*args, **kwargs)

    def show_to_dict(self, output):
        obj = {}
        items = self.parser.listing(output)
        for item in items:
            obj[item['Field']] = six.text_type(item['Value'])
        return dict((self._key_name(k), v) for k, v in obj.items())

    def _key_name(self, key):
        return key.lower().replace(' ', '_')

    def name_generate(self):
        """Generate randomized name for some entity."""
        name = uuidutils.generate_uuid()[:8]
        return name

    def _get_profile_path(self, profile_name):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'profiles/%s' % profile_name)

    def _get_policy_path(self, policy_name):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'policies/%s' % policy_name)

    def wait_for_status(self, name, status, check_type, timeout=60,
                        poll_interval=5):
        """Wait until name reaches given status.

        :param name: node or cluster name
        :param status: expected status of node or cluster
        :param timeout: timeout in seconds
        :param poll_interval: poll interval in seconds
        """
        if check_type == 'node':
            cmd = ('cluster node show %s' % name)
        elif check_type == 'cluster':
            cmd = ('cluster show %s' % name)
        time.sleep(poll_interval)
        start_time = time.time()
        while time.time() - start_time < timeout:
            check_status = self.openstack(cmd)
            result = self.show_to_dict(check_status)
            if result['status'] == status:
                break
            time.sleep(poll_interval)
        else:
            message = ("%s %s did not reach status %s after %d s"
                       % (check_type, name, status, timeout))
            raise tempest_lib_exc.TimeoutException(message)

    def wait_for_delete(self, name, check_type, timeout=60,
                        poll_interval=5):
        """Wait until delete finish"""
        if check_type == 'node':
            cmd = ('cluster node show %s' % name)
        if check_type == 'cluster':
            cmd = ('cluster show %s' % name)
        time.sleep(poll_interval)
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.openstack(cmd)
            except tempest_lib_exc.CommandFailed as ex:
                if "No Node found" or "No Cluster found" in ex.stderr:
                    break
            time.sleep(poll_interval)
        else:

            message = ("failed in deleting %s %s after %d seconds"
                       % (check_type, name, timeout))
            raise tempest_lib_exc.TimeoutException(message)

    def policy_create(self, name, policy='deletion_policy.yaml'):
        pf = self._get_policy_path(policy)
        cmd = ('cluster policy create --spec-file %s %s'
               % (pf, name))
        policy_raw = self.openstack(cmd)
        result = self.show_to_dict(policy_raw)
        return result

    def policy_delete(self, name_or_id):
        cmd = ('cluster policy delete %s --force' % name_or_id)
        self.openstack(cmd)

    def profile_create(self, name, profile='cirros_basic.yaml'):
        pf = self._get_profile_path(profile)
        cmd = ('cluster profile create --spec-file %s %s'
               % (pf, name))
        profile_raw = self.openstack(cmd)
        result = self.show_to_dict(profile_raw)
        return result

    def profile_delete(self, name_or_id):
        cmd = ('cluster profile delete %s --force' % name_or_id)
        self.openstack(cmd)

    def node_create(self, profile, name):
        cmd = ('cluster node create --profile %s %s'
               % (profile, name))
        node_raw = self.openstack(cmd)
        result = self.show_to_dict(node_raw)
        self.wait_for_status(name, 'ACTIVE', 'node', 120)
        return result

    def node_delete(self, name_or_id):
        cmd = ('cluster node delete %s --force' % name_or_id)
        self.openstack(cmd)
        self.wait_for_delete(name_or_id, 'node', 120)

    def cluster_create(self, profile, name, desired_capacity=0):
        cmd = ('cluster create --profile %s --desired-capacity %d %s'
               % (profile, desired_capacity, name))
        cluster_raw = self.openstack(cmd)
        result = self.show_to_dict(cluster_raw)
        self.wait_for_status(name, 'ACTIVE', 'cluster', 120)
        return result

    def cluster_delete(self, name_or_id):
        cmd = ('cluster delete %s --force' % name_or_id)
        self.openstack(cmd)
        self.wait_for_delete(name_or_id, 'cluster', 120)

    def receiver_create(self, name, cluster, action='CLUSTER_SCALE_OUT',
                        rt='webhook'):
        cmd = ('cluster receiver create --cluster %s --action %s --type %s '
               '%s' % (cluster, action, rt, name))
        receiver_raw = self.openstack(cmd)
        result = self.show_to_dict(receiver_raw)
        return result

    def receiver_delete(self, name_or_id):
        cmd = ('cluster receiver delete %s --force' % name_or_id)
        self.openstack(cmd)
