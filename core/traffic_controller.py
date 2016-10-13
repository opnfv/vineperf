# Copyright 2015-2016 Intel Corporation.
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
from conf import get_test_param

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
        self._duration = int(get_test_param('duration', 30))
        self._lossrate = float(get_test_param('lossrate', 0.0))
        self._mode = settings.getValue('mode').lower()
        self._results = []

        # If set, comma separated packet_sizes value from --test_params
        # on cli takes precedence over value in settings file.
        self._packet_sizes = None
        packet_sizes_cli = get_test_param('pkt_sizes')
        if packet_sizes_cli:
            self._packet_sizes = [int(x.strip())
                                  for x in packet_sizes_cli.split(',')]
        else:
            self._packet_sizes = settings.getValue('TRAFFICGEN_PKT_SIZES')

    def __enter__(self):
        """Call initialisation function.
        """
        self._traffic_gen_class.connect()

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

    def send_traffic(self, dummy_traffic):
        """Triggers traffic to be sent from the traffic generator.

        This is a blocking function.

        :param traffic: A dictionary describing the traffic to send.
        """
        raise NotImplementedError(
            "The TrafficController does not implement",
            "the \"send_traffic\" function.")

    def send_traffic_async(self, dummy_traffic, dummy_function):
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
        raise NotImplementedError(
            "The TrafficController does not implement",
            "the \"send_traffic_async\" function.")

    def stop_traffic(self):
        """Kills traffic being sent from the traffic generator.
        """
        self._logger.debug("stop_traffic()")

    def print_results(self):
        """IResult interface implementation.
        """
        counter = 0
        for item in self._results:
            logging.info("Record: " + str(counter))
            counter += 1
            for(key, value) in list(item.items()):
                logging.info("         Key: " + str(key) +
                             ", Value: " + str(value))

    def get_results(self):
        """IResult interface implementation.
        """
        return self._results

    def validate_send_traffic(self, dummy_result, dummy_traffic):
        """Verify that send traffic has succeeded
        """
        if len(self._results):
            if 'b2b_frames' in self._results[-1]:
                return float(self._results[-1]['b2b_frames']) > 0
            elif 'throughput_rx_fps' in self._results[-1]:
                return float(self._results[-1]['throughput_rx_fps']) > 0
            else:
                return True
        else:
            return False
