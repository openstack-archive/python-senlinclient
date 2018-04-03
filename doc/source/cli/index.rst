..
  Licensed under the Apache License, Version 2.0 (the "License"); you may
  not use this file except in compliance with the License. You may obtain
  a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
  License for the specific language governing permissions and limitations
  under the License.

===================
Senlin CLI man page
===================


SYNOPSIS
========

The Senlin clustering service doesn't provide its own command line tool
since Queens release. Users are supposed to use :program:`openstack cluster`
commands instead. The python-senlinclient project is an implementation of the
OpenStackClient (OSC) plugin that interacts with the Senlin clustering service.

:program:`openstack` [options] <command> [command-options]

:program:`openstack help cluster`


DESCRIPTION
===========

The :program:`openstack cluster` command line utility interacts with OpenStack Cluster
Service (Senlin).

In order to use the CLI, you must provide your OpenStack username, password,
project (historically called tenant), and auth endpoint. You can use
configuration options `--os-username`, `--os-password`, `--os-project-name`,
`--os-identity-api-version`, `-os-user-domain-name`, `--os-project-domain-name`
and `--os-auth-url` or set corresponding environment
variables::

    export OS_USERNAME=user
    export OS_PASSWORD=pass
    export OS_PROJECT_NAME=myproject
    export OS_IDENTITY_API_VERSION=3
    export OS_AUTH_URL=http://auth.example.com:5000/v3
    export OS_USER_DOMAIN_NAME=Default
    export OS_PROJECT_DOMAIN_NAME=Default

OPTIONS
=======

To get a list of available commands and options run::

    openstack help cluster

To get usage and options of a command::

    openstack help cluster <command>

EXAMPLES
========

Get help for profile create command::

    openstack help cluster profile create

List all the profiles::

    openstack cluster profile list

Create new profile::

    openstack cluster profile create --spec-file cirros_basic.yaml PF001

Show a specific profile details::

    openstack cluster profile show PF001

Create a node::

    openstack cluster node create --profile PF001 NODE001

For more information, please see the senlin documentation.
`https://docs.openstack.org/senlin/latest/tutorial/basics.html`
