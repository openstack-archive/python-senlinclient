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

from oslo_serialization import jsonutils
from openstack import exceptions as sdkexc

from senlinclient.common.i18n import _

verbose = False


class BaseException(Exception):
    '''An error occurred.'''
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message or self.__class__.__doc__


class CommandError(BaseException):
    '''Invalid usage of CLI.'''


class FileFormatError(BaseException):
    '''Illegal file format detected.'''


class HTTPException(BaseException):
    """Base exception for all HTTP-derived exceptions."""
    code = 'N/A'

    def __init__(self, details=None):
        super(HTTPException, self).__init__(details)
        try:
            self.error = jsonutils.loads(details)
            if 'error' not in self.error:
                raise KeyError(_('Key "error" not exists'))
        except KeyError:
            # If key 'error' does not exist, self.message becomes
            # no sense. In this case, we return doc of current
            # exception class instead.
            self.error = {'error': { 'message': self.__class__.__doc__}}
        except Exception:
            self.error = {'error':
                          {'message': self.message or self.__class__.__doc__}}

    def __str__(self):
        message = self.error['error'].get('message', 'Internal Error')
        if verbose:
            traceback = self.error['error'].get('traceback', '')
            return (_('ERROR: %(message)s\n%(traceback)s') %
                    {'message': message, 'traceback': traceback})
        else:
            return _('ERROR: %s') % message

class HTTPNotFound(HTTPException):
    code = '404'
