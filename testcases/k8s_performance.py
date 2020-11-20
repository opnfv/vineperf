# Copyright 2015-2017 Intel Corporation.
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
"""PerformanceTestCase class
"""

import logging

from testcases.testcase import TestCase
#from tools.report import report

class K8sPerformanceTestCase(TestCase):
    """K8sPerformanceTestCase class

    In this basic form runs RFC2544 throughput test
    """
    def __init__(self, cfg):
        """ Testcase initialization
        """
        self._type = 'k8s_performance'
        super().__init__(cfg)
        self._logger = logging.getLogger(__name__)
        self._k8s = True

    def run_report(self):
        pass
        #super().run_report()
        #if self._tc_results:
        #    report.generate(self)
