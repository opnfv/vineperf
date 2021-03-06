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

"""Base class for traffic controllers
"""

import logging
import os
import time

from core.results.results_constants import ResultsConstants
from conf import settings

class TrafficController(object):
    """Base class which defines a common functionality for all traffic
       controller classes.

    Used to setup and control a traffic generator for a particular deployment
    scenario.
    """
    def __init__(self, traffic_gen_class):
        """Initialization common for all types of traffic controllers

        :param traffic_gen_class: The traffic generator class to be used.
        """
        self._type = None
        self._logger = logging.getLogger(__name__)
        self._logger.debug("__init__")
        self._traffic_gen_class = traffic_gen_class()
        self._traffic_started = False
        self._traffic_started_call_count = 0
        self._duration = None
        self._lossrate = None
        self._packet_sizes = None
        self._connected = False

        self._mode = str(settings.getValue('mode')).lower()
        self._results = []

    def configure(self, traffic):
        """Set configuration values just before test execution so they
           can be changed during runtime by test steps.
        """
        if not self._connected:
            self._traffic_gen_class.connect()
            self._connected = True

        self._duration = int(settings.getValue('TRAFFICGEN_DURATION'))
        self._lossrate = float(settings.getValue('TRAFFICGEN_LOSSRATE'))
        self._packet_sizes = settings.getValue('TRAFFICGEN_PKT_SIZES')
        self._results = []

        # update type with detailed traffic value
        self._type = traffic['traffic_type']

    def __enter__(self):
        """Call initialisation function.
        """
        pass

    def __exit__(self, type_, value, traceback):
        """Stop traffic, clean up.
        """
        if self._traffic_started:
            self.stop_traffic()

    def _append_results(self, result_dict, packet_size):
        """Adds common values to traffic generator results.

        :param result_dict: Dictionary containing results from trafficgen
        :param packet_size: Packet size value.

        :returns: dictionary of results with additional entries.
        """

        ret_value = result_dict

        ret_value[ResultsConstants.TYPE] = self._type
        ret_value[ResultsConstants.PACKET_SIZE] = str(packet_size)

        return ret_value

    def traffic_required(self):
        """Checks selected '--mode' of traffic generator and performs
           its specific handling.

        :returns: True - in case that traffic generator should be executed
                  False - if traffic generation is not required
        """
        if self._mode == 'trafficgen-off':
            time.sleep(2)
            self._logger.debug("All is set. Please run traffic generator manually.")
            input(os.linesep + "Press Enter to terminate vswitchperf..." +
                  os.linesep + os.linesep)
            return False
        elif self._mode == 'trafficgen-pause':
            time.sleep(2)
            while True:
                choice = input(os.linesep + 'Transmission paused, should'
                               ' transmission be resumed? [y/n]' + os.linesep).lower()
                if choice in ('yes', 'y', 'ye'):
                    return True
                elif choice in ('no', 'n'):
                    self._logger.info("Traffic transmission will be skipped.")
                    return False
                else:
                    print("Please respond with 'yes', 'y', 'no' or 'n' ", end='')
        return True

    def send_traffic(self, traffic):
        """Triggers traffic to be sent from the traffic generator.

        This is a blocking function.

        :param traffic: A dictionary describing the traffic to send.
        """
        self._logger.debug('send_traffic with %s',
                           str(self._traffic_gen_class))
        self.configure(traffic)

    def send_traffic_async(self, traffic, dummy_function):
        """Triggers traffic to be sent  asynchronously.

        This is not a blocking function.

        :param traffic: A dictionary describing the traffic to send.
        :param function: A dictionary describing the function to call between
             send and wait in the form:
             function = {
                 'function' : package.module.function,
                 'args' : args
             }
             If this function requires more than one argument, all should be
             should be passed using the args list and appropriately handled.
         """
        # pylint: disable=unused-argument
        self._logger.debug('send_traffic_async with %s',
                           str(self._traffic_gen_class))
        self.configure(traffic)

    def stop_traffic(self):
        """Kills traffic being sent from the traffic generator.
        """
        self._logger.debug("stop_traffic()")

    def print_results(self):
        """IResult interface implementation.
        """
        counter = 0
        for item in self._results:
            logging.info("Record: %s", str(counter))
            counter += 1
            for(key, value) in list(item.items()):
                logging.info("         Key: " + str(key) +
                             ", Value: " + str(value))
                if settings.getValue('CLEAN_OUTPUT'):
                    print(str(key) + ", " + str(value))

    def get_results(self):
        """IResult interface implementation.
        """
        return self._results

    def validate_send_traffic(self, _dummy_result, _dummy_traffic):
        """Verify that send traffic has succeeded
        """
        if self._results:
            if 'b2b_frames' in self._results[-1]:
                return float(self._results[-1]['b2b_frames']) > 0
            elif 'throughput_rx_fps' in self._results[-1]:
                return float(self._results[-1]['throughput_rx_fps']) > 0
            else:
                return True
        else:
            return False

    def validate_get_results(self, result):
        """Verify that results has been returned
        """
        return self._results == result
