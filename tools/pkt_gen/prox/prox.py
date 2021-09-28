# Copyright 2021 Spirent Communications.
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

"""
Code to integrate Prox Traffic generator with vineperf test framework.

"""

#import csv
import logging
import os
#import subprocess

from conf import settings
from core.results.results_constants import ResultsConstants
#from runrapid import RapidTestManager
from tools import tasks
from tools.pkt_gen.prox import render

class Prox():
    """
    Prox Traffic Generator
    """
    _logger = logging.getLogger(__name__)

    def connect(self):
        """
        Do nothing.
        """
        return self

    def disconnect(self):
        """
        Do nothing.
        """
        return self

    def send_burst_traffic(self, traffic=None, duration=20):
        """
        Do nothing.
        """
        raise NotImplementedError('Not implemented by PROX')

    def send_rfc2889_forwarding(self, traffic=None, tests=1, _duration=20):
        """
        Send traffic per RFC2889 Forwarding test specifications.
        """
        raise NotImplementedError('Not implemented by PROX')

    def send_rfc2889_caching(self, traffic=None, tests=1, _duration=20):
        """
        Send as per RFC2889 Addr-Caching test specifications.
        """
        raise NotImplementedError('Not implemented by PROX')

    def send_rfc2889_learning(self, traffic=None, tests=1, _duration=20):
        """
        Send traffic per RFC2889 Addr-Learning test specifications.
        """
        raise NotImplementedError('Not implemented by PROX')

    def send_cont_traffic(self, traffic=None, duration=30):
        """
        Send Custom - Continuous Test traffic
        Reuse RFC2544 throughput test specifications along with
        'custom' configuration
        """
        raise NotImplementedError('Not implemented by PROX')

    def get_rfc2544_results(self, output):
        """
        Reads the output and return the results
        """
        result = {}
        values = None
        for line in output.splitlines():
            if line.startswith('|') and 'different number' in line:
                pktsize = line.split(',')[1]
                try:
                    int(pktsize)
                except ValueError:
                    self._logger.info("Pkt Size is not an Int\n")
                    return result
            if line.startswith('|') and '%' in line:
                values = line.split('|')
                if values and len(values) > 12:
                    tx_pps = float(values[4].strip().split(' ')[0]) * 1000000
                    rx_pps = float(values[7].strip().split(' ')[0]) * 1000000
                    rx_mbps = float(values[6].strip().split(' ')[0]) * 1000
                    max_lat = float(values[10].strip().split(' ')[0]) * 1000
                    avg_lat = float(values[8].strip().split(' ')[0]) * 1000
                    loss_percentage = ((float(values[11].strip()) -
                        float(values[12].strip()))/float(values[11].strip())) * 100
                    result[ResultsConstants.TX_RATE_FPS] = tx_pps
                    result[ResultsConstants.THROUGHPUT_RX_FPS] = rx_pps
                    result[ResultsConstants.TX_RATE_MBPS] = 0
                    result[ResultsConstants.THROUGHPUT_RX_MBPS] = rx_mbps
                    result[ResultsConstants.TX_RATE_PERCENT] = 0
                    result[ResultsConstants.THROUGHPUT_RX_PERCENT] = 0
                    result[ResultsConstants.MIN_LATENCY_NS] = 0
                    result[ResultsConstants.MAX_LATENCY_NS] = max_lat
                    result[ResultsConstants.AVG_LATENCY_NS] = avg_lat
                    result[ResultsConstants.FRAME_LOSS_PERCENT] = loss_percentage
        return result

    def send_rfc2544_throughput(self, traffic=None, tests=1, duration=20,
                                lossrate=0.0):
        """
        Send traffic per RFC2544 throughput test specifications.
        """
        print("Run with Duration: {}, Tests: {} & Lossrate: {}".format(
            duration, tests, lossrate))
        pkt_size = None
        if traffic and 'l2' in traffic:
            if 'framesize' in traffic['l2']:
                framesize = traffic['l2']['framesize']
                pkt_size = '['+str(framesize)+']'
        if not settings.getValue('K8S'):
            # First render all the configurations and place it
            filesdir = settings.getValue('TRAFFICGEN_PROX_FILES_DIR')
            confdir = settings.getValue('TRAFFICGEN_PROX_CONF_DIR')
            render.render_content_jinja(pkt_size)
            # copy some static files to config folder.
            for stfile in settings.getValue('TRAFFICGEN_PROX_STATIC_CONF_FILES'):
                srcfile = os.path.join(filesdir, stfile)
                if os.path.exists(srcfile):
                    cmd = ['cp', srcfile, confdir ]
                    tasks.run_task(cmd, self._logger, 'Copying Static Conf. Files')
            # in appropriate folder: pick /tmp or /opt or $HOME
            envfile = os.path.join(confdir, settings.getValue('TRAFFICGEN_PROX_ENV_FILE'))
            tstfile = os.path.join(confdir, settings.getValue('TRAFFICGEN_PROX_TEST_FILE'))
            mmapfile = os.path.join(confdir, 'machine.map')
            cmd = ['python', '-m', 'runrapid',
                   '--env', envfile,
                   '--test', tstfile,
                   '--map', mmapfile,
                   '--runtime', settings.getValue('TRAFFICGEN_PROX_RUNTIME')]
            output, error = tasks.run_task(cmd, self._logger, 'Running RUN-RAPID command')
            if output:
                return self.get_rfc2544_results(output)
            else:
                self._logger.info(error)
                return None
        else:
            self._logger.info("Only Baremetal Support is included.")
            print("Only Baremetal Support is included")
            return None


    def send_rfc2544_back2back(self, traffic=None, tests=1, duration=20,
                               lossrate=0.0):
        """
        Send traffic per RFC2544 BacktoBack test specifications.
        """
        raise NotImplementedError('Not implemented by PROX')

    def start_cont_traffic(self, traffic=None, duration=30):
        """Non-blocking version of 'send_cont_traffic'.

        See ITrafficGenerator for description
        """
        raise NotImplementedError('Not implemented by PROX')

    def stop_cont_traffic(self):
        """Stop continuous transmission and return results.
        """
        raise NotImplementedError('Not implemented by PROX')

    def start_rfc2544_back2back(self, traffic=None, tests=1, duration=20,
                                lossrate=0.0):
        """Send traffic per RFC2544 back2back test specifications.

        See ITrafficGenerator for description
        """
        raise NotImplementedError('Not implemented by PROX')

    def wait_rfc2544_back2back(self):
        """Wait and set results of RFC2544 test.
        """
        raise NotImplementedError('Not implemented by PROX')

    def start_rfc2544_throughput(self, traffic=None, tests=1, duration=20,
                                 lossrate=0.0):
        """Non-blocking version of 'send_rfc2544_throughput'.
        See ITrafficGenerator for description
        """
        raise NotImplementedError('Not implemented by PROX')

    def wait_rfc2544_throughput(self):
        """Wait and set results of RFC2544 test.
        """
        raise NotImplementedError('Not implemented by PROX')
