======
senlin
======

.. program:: senlin

SYNOPSIS
========

  `senlin` [options] <command> [command-options]

  `senlin help`

  `senlin help` <command>


DESCRIPTION
===========

`senlin` is a command line client for controlling OpenStack Senlin.

Before the `senlin` command is issued, ensure the environment contains
the necessary variables so that the CLI can pass user credentials to
the server.
See `Getting Credentials for a CLI`  section of `OpenStack CLI Guide`
for more info.


OPTIONS
=======

To get a list of available commands and options run::

    senlin help

To get usage and options of a command run::

    senlin help <command>


EXAMPLES
========

Get information about profile-create command::

    senlin help profile-create

List available profiles::

    senlin profile-list

List available clusters::

    senlin cluster-list

Create a profile::

    senlin profile-create -t os.heat.stack -s profile.spec myprofile

View profile information::

    senlin profile-show myprofile

Create a cluster::

    senlin cluster-create -p myprofile -n 2 mycluster

List events::

    senlin event-list

Delete a cluster::

    senlin cluster-delete mycluster

BUGS
====

Senlin client is hosted in Launchpad so you can view current bugs
at https://bugs.launchpad.net/python-senlinclient/.
