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

"""OpenStackClient plugin for Clustering service."""

import logging

from openstack.config import cloud_region
from openstack.config import defaults as config_defaults
from openstack import connection
from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_CLUSTERING_API_VERSION = '1'
API_VERSION_OPTION = 'os_clustering_api_version'
API_NAME = 'clustering'
CURRENT_API_VERSION = '1.12'


def _make_key(service_type, key):
    if not service_type:
        return key
    else:
        service_type = service_type.lower().replace('-', '_')
        return "_".join([service_type, key])


def _get_config_from_profile(profile, **kwargs):
    # Deal with clients still trying to use legacy profile objects
    region_name = None
    for service in profile.get_services():
        if service.region:
            region_name = service.region
        service_type = service.service_type
        if service.interface:
            key = _make_key(service_type, 'interface')
            kwargs[key] = service.interface
        if service.version:
            version = service.version
            if version.startswith('v'):
                version = version[1:]
            key = _make_key(service_type, 'api_version')
            kwargs[key] = version
        if service.api_version:
            version = service.api_version
            key = _make_key(service_type, 'default_microversion')
            kwargs[key] = version

    config_kwargs = config_defaults.get_defaults()
    config_kwargs.update(kwargs)
    config = cloud_region.CloudRegion(
        region_name=region_name, config=config_kwargs)
    return config


def create_connection(prof=None, cloud_region=None, **kwargs):
    version_key = _make_key(API_NAME, 'api_version')
    kwargs[version_key] = CURRENT_API_VERSION

    if not cloud_region:
        if prof:
            cloud_region = _get_config_from_profile(prof, **kwargs)
    else:
        # If we got the CloudRegion from python-openstackclient and it doesn't
        # already have a default microversion set, set it here.
        microversion_key = _make_key(API_NAME, 'default_microversion')
        cloud_region.config.setdefault(microversion_key, CURRENT_API_VERSION)

    user_agent = kwargs.pop('user_agent', None)
    app_name = kwargs.pop('app_name', None)
    app_version = kwargs.pop('app_version', None)
    if user_agent is not None and (not app_name and not app_version):
        app_name, app_version = user_agent.split('/', 1)

    return connection.Connection(
        config=cloud_region,
        app_name=app_name,
        app_version=app_version, **kwargs)


def make_client(instance):
    """Returns a clustering proxy"""
    # TODO(mordred) the ClientManager already has an OpenStackSDK connection,
    # but it only has it once setup_auth has been called. For things that
    # don't require auth, this is problematic, so we have to make our own.
    # Use the CloudRegion stored on the ClientManager for now.
    conn = create_connection(
        cloud_region=instance._cli_options,
    )

    LOG.debug('Connection: %s', conn)
    LOG.debug('Clustering client initialized using OpenStackSDK: %s',
              conn.clustering)
    return conn.clustering


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
