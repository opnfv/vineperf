"""
# Copyright (c) 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
#pylint: disable=import-error
from oslo_utils import excutils


class VsperfCException(Exception):
    """Base VSPERF-C Exception.

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    Based on NeutronException class.
    """
    message = "An unknown exception occurred."

    def __init__(self, **kwargs):
        try:
            super(VsperfCException, self).__init__(self.message % kwargs)
            self.msg = self.message % kwargs
        except Exception:  # pylint: disable=broad-except
            with excutils.save_and_reraise_exception() as ctxt:
                if not self.use_fatal_exceptions():
                    ctxt.reraise = False
                    # at least get the core message out if something happened
                    super(VsperfCException, self).__init__(self.message)

    def __str__(self):
        return self.msg

    def use_fatal_exceptions(self):
        """Is the instance using fatal exceptions.

        :returns: Always returns False.
        """ #pylint: disable=no-self-use
        return False


class InvalidType(VsperfCException):
    """Invalid type"""
    message = 'Type "%(type_to_convert)s" is not valid'


class SSHError(VsperfCException):
    """ssh error"""
    message = '%(error_msg)s'


class SSHTimeout(SSHError):
    """ssh timeout""" #pylint: disable=unnecessary-pass
    pass
