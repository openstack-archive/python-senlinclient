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

"""Clustering v1 policy type action implementations"""

import logging

from cliff import lister


class PolicyTypeList(lister.Lister):
    """List the available policy types."""

    log = logging.getLogger(__name__ + ".PolicyTypeList")

    def get_parser(self, prog_name):
        parser = super(PolicyTypeList, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        senlin_client = self.app.client_manager.clustering
        types = senlin_client.policy_types()
        columns = ['name']
        rows = sorted([t.name] for t in types)
        return columns, rows
