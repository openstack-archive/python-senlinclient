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

==================
SenlinClient Tests
==================

Unit Tests
==========

Senlinclient contains a suite of unit tests, in the senlinclient/tests/unit
directory.

Any proposed code change will be automatically rejected by the OpenStack
Jenkins server if the change causes unit test failures.

Running the tests
-----------------
There are a number of ways to run unit tests currently, and there's a
combination of frameworks used depending on what commands you use.  The
preferred method is to use tox, which calls stestr via the tox.ini file.
To run all tests simply run::

    tox

This will create a virtual environment, load all the packages from
test-requirements.txt and run all unit tests as well as run flake8 and hacking
checks against the code.

Note that you can inspect the tox.ini file to get more details on the available
options and what the test run does by default.

Running a subset of tests using tox
-----------------------------------
One common activity is to just run a single test, you can do this with tox
simply by specifying to just run py27 or py35 tests against a single test::

    tox -epy27 senlinclient.tests.unit.v1.test_node.TestNodeList.test_node_list_defaults

Or all tests in the test_node.py file::

    tox -epy27 senlinclient.tests.unit.v1.test_node

For more information on these options and how to run tests, please see the
`stestr documentation <https://stestr.readthedocs.io/en/latest/index.html>`_.
