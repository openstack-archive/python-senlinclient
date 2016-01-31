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

import logging

from openstack import connection
from openstackclient.common import utils

LOG = logging.getLogger(__name__)

DEFAULT_CLUSTERING_API_VERSION = '1'
API_VERSION_OPTION = 'os_clustering_api_version'
API_NAME = 'clustering'


def make_client(instance):
    """Returns a clustering proxy"""

    conn = connection.Connection(authenticator=instance.session.auth)
    LOG.debug('Connection: %s', conn)
    LOG.debug('Clustering client initialized using OpenStackSDK: %s',
              conn.cluster)
    return conn.cluster


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-clustering-api-version',
        metavar='<clustering-api-version>',
        default=utils.env(
            'OS_CLUSTERING_API_VERSION',
            default=DEFAULT_CLUSTERING_API_VERSION),
        help='Clustering API version, default=' +
             DEFAULT_CLUSTERING_API_VERSION +
             ' (Env: OS_CLUSTERING_API_VERSION)')
    return parser
