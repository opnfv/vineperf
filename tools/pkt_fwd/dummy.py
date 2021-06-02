# Copyright 2016-2017 Intel Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""VSPERF TestPMD implementation
"""

import logging
from conf import settings

_LOGGER = logging.getLogger(__name__)

class Dummy(IPktFwd):
    """Dummy implementation

    """

    _logger = logging.getLogger()

    def __init__(self, guest=False):
        self._logger.info("Initializing Dummy...")

    def start(self):
        """See IPktFwd for general description

        Activates testpmd.
        """
        self._logger.info("Starting Dummy...")

    def start_for_guest(self):
        """See IPktFwd for general description

        Activates testpmd for guest config
        """
        self._logger.info("Starting Dummy for one guest...")

    def stop(self):
        """See IPktFwd for general description

        Kills testpmd.
        """
        self._logger.info("Stopping Dummy ....")

    # Method could be a function
    # pylint: disable=no-self-use
    def get_version(self):
        """
        Get product version
        :return: None
        """
        # No way to read Dummy version
        return []
