# Copyright 2016 Spirent Communications.
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
Code to integrate Spirent TestCenter with the vsperf test framework.

Provides a model for Spirent TestCenter as a test tool for implementing
various performance tests of a virtual switch.
"""

import csv
import logging
import os
import subprocess

from conf import settings
from core.results.results_constants import ResultsConstants
from tools.pkt_gen import trafficgen


class TestCenter(trafficgen.ITrafficGenerator):
    """
    Spirent TestCenter
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
        pass

    def send_burst_traffic(self, traffic=None, numpkts=100, duration=20):
        """
        Do nothing.
        """
        return None

    def send_cont_traffic(self, traffic=None, duration=30):
        """
        Do nothing.
        """
        return None

    def send_rfc2544_throughput(self, traffic=None, trials=3, duration=20,
                                lossrate=0.0):
        """
        Send traffic per RFC2544 throughput test specifications.
        """
        verbose = False
        framesize = settings.getValue("TRAFFICGEN_STC_FRAME_SIZE")
        if traffic and 'l2' in traffic:
            if 'framesize' in traffic['l2']:
                framesize = traffic['l2']['framesize']
        args = [settings.getValue("TRAFFICGEN_STC_PYTHON2_PATH"),
                os.path.join(
                    settings.getValue("TRAFFICGEN_STC_TESTCENTER_PATH"),
                    settings.getValue(
                        "TRAFFICGEN_STC_RFC2544_TPUT_TEST_FILE_NAME")),
                "--lab_server_addr",
                settings.getValue("TRAFFICGEN_STC_LAB_SERVER_ADDR"),
                "--license_server_addr",
                settings.getValue("TRAFFICGEN_STC_LICENSE_SERVER_ADDR"),
                "--east_chassis_addr",
                settings.getValue("TRAFFICGEN_STC_EAST_CHASSIS_ADDR"),
                "--east_slot_num",
                settings.getValue("TRAFFICGEN_STC_EAST_SLOT_NUM"),
                "--east_port_num",
                settings.getValue("TRAFFICGEN_STC_EAST_PORT_NUM"),
                "--west_chassis_addr",
                settings.getValue("TRAFFICGEN_STC_WEST_CHASSIS_ADDR"),
                "--west_slot_num",
                settings.getValue("TRAFFICGEN_STC_WEST_SLOT_NUM"),
                "--west_port_num",
                settings.getValue("TRAFFICGEN_STC_WEST_PORT_NUM"),
                "--test_session_name",
                settings.getValue("TRAFFICGEN_STC_TEST_SESSION_NAME"),
                "--results_dir",
                settings.getValue("TRAFFICGEN_STC_RESULTS_DIR"),
                "--csv_results_file_prefix",
                settings.getValue("TRAFFICGEN_STC_CSV_RESULTS_FILE_PREFIX"),
                "--num_trials",
                settings.getValue("TRAFFICGEN_STC_NUMBER_OF_TRIALS"),
                "--trial_duration_sec",
                settings.getValue("TRAFFICGEN_STC_TRIAL_DURATION_SEC"),
                "--traffic_pattern",
                settings.getValue("TRAFFICGEN_STC_TRAFFIC_PATTERN"),
                "--search_mode",
                settings.getValue("TRAFFICGEN_STC_SEARCH_MODE"),
                "--learning_mode",
                settings.getValue("TRAFFICGEN_STC_LEARNING_MODE"),
                "--rate_lower_limit_pct",
                settings.getValue("TRAFFICGEN_STC_RATE_LOWER_LIMIT_PCT"),
                "--rate_upper_limit_pct",
                settings.getValue("TRAFFICGEN_STC_RATE_UPPER_LIMIT_PCT"),
                "--rate_initial_pct",
                settings.getValue("TRAFFICGEN_STC_RATE_INITIAL_PCT"),
                "--rate_step_pct",
                settings.getValue("TRAFFICGEN_STC_RATE_STEP_PCT"),
                "--resolution_pct",
                settings.getValue("TRAFFICGEN_STC_RESOLUTION_PCT"),
                "--frame_size_list",
                str(framesize),
                "--acceptable_frame_loss_pct",
                settings.getValue("TRAFFICGEN_STC_ACCEPTABLE_FRAME_LOSS_PCT"),
                "--east_intf_addr",
                settings.getValue("TRAFFICGEN_STC_EAST_INTF_ADDR"),
                "--east_intf_gateway_addr",
                settings.getValue("TRAFFICGEN_STC_EAST_INTF_GATEWAY_ADDR"),
                "--west_intf_addr",
                settings.getValue("TRAFFICGEN_STC_WEST_INTF_ADDR"),
                "--west_intf_gateway_addr",
                settings.getValue("TRAFFICGEN_STC_WEST_INTF_GATEWAY_ADDR")]

        if settings.getValue("TRAFFICGEN_STC_VERBOSE") is "True":
            args.append("--verbose")
            verbose = True
            self._logger.debug("Arguments used to call test: %s", args)
        subprocess.check_call(args)

        filec = os.path.join(settings.getValue("TRAFFICGEN_STC_RESULTS_DIR"),
                             settings.getValue(
                                 "TRAFFICGEN_STC_CSV_RESULTS_FILE_PREFIX") +
                             ".csv")

        if verbose:
            self._logger.info("file: %s", filec)

        result = {}

        with open(filec, "r") as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                self._logger.info("Row: %s", row)
                result[ResultsConstants.TX_RATE_FPS] = 0.0
                result[ResultsConstants.THROUGHPUT_RX_FPS] = 0.0
                result[ResultsConstants.TX_RATE_MBPS] = 0.0
                result[ResultsConstants.THROUGHPUT_RX_MBPS] = 0.0
                result[ResultsConstants.TX_RATE_PERCENT] = float(
                    row["OfferedLoad(%)"])
                result[ResultsConstants.THROUGHPUT_RX_PERCENT] = float(
                    row["Throughput(%)"])
                result[ResultsConstants.MIN_LATENCY_NS] = float(
                    row["MinimumLatency(us)"]) * 1000
                result[ResultsConstants.MAX_LATENCY_NS] = float(
                    row["MaximumLatency(us)"]) * 1000
                result[ResultsConstants.AVG_LATENCY_NS] = float(
                    row["AverageLatency(us)"]) * 1000
                result[ResultsConstants.FRAME_LOSS_PERCENT] = float(
                    row["PercentLoss"])
        return result

    def send_rfc2544_back2back(self, traffic=None, trials=1, duration=20,
                               lossrate=0.0):
        """
        Send traffic per RFC2544 BacktoBack test specifications.
        """
        verbose = False
        framesize = settings.getValue("TRAFFICGEN_STC_FRAME_SIZE")
        if traffic and 'l2' in traffic:
            if 'framesize' in traffic['l2']:
                framesize = traffic['l2']['framesize']
        args = [settings.getValue("TRAFFICGEN_STC_PYTHON2_PATH"),
                os.path.join(
                    settings.getValue("TRAFFICGEN_STC_TESTCENTER_PATH"),
                    settings.getValue(
                        "TRAFFICGEN_STC_RFC2544_B2B_TEST_FILE_NAME")),
                "--metric",
                settings.getValue("TRAFFICGEN_STC_RFC2544_METRIC"),
                "--lab_server_addr",
                settings.getValue("TRAFFICGEN_STC_LAB_SERVER_ADDR"),
                "--license_server_addr",
                settings.getValue("TRAFFICGEN_STC_LICENSE_SERVER_ADDR"),
                "--east_chassis_addr",
                settings.getValue("TRAFFICGEN_STC_EAST_CHASSIS_ADDR"),
                "--east_slot_num",
                settings.getValue("TRAFFICGEN_STC_EAST_SLOT_NUM"),
                "--east_port_num",
                settings.getValue("TRAFFICGEN_STC_EAST_PORT_NUM"),
                "--west_chassis_addr",
                settings.getValue("TRAFFICGEN_STC_WEST_CHASSIS_ADDR"),
                "--west_slot_num",
                settings.getValue("TRAFFICGEN_STC_WEST_SLOT_NUM"),
                "--west_port_num",
                settings.getValue("TRAFFICGEN_STC_WEST_PORT_NUM"),
                "--test_session_name",
                settings.getValue("TRAFFICGEN_STC_TEST_SESSION_NAME"),
                "--results_dir",
                settings.getValue("TRAFFICGEN_STC_RESULTS_DIR"),
                "--csv_results_file_prefix",
                settings.getValue("TRAFFICGEN_STC_CSV_RESULTS_FILE_PREFIX"),
                "--num_trials",
                settings.getValue("TRAFFICGEN_STC_NUMBER_OF_TRIALS"),
                "--trial_duration_sec",
                settings.getValue("TRAFFICGEN_STC_TRIAL_DURATION_SEC"),
                "--traffic_pattern",
                settings.getValue("TRAFFICGEN_STC_TRAFFIC_PATTERN"),
                "--search_mode",
                settings.getValue("TRAFFICGEN_STC_SEARCH_MODE"),
                "--learning_mode",
                settings.getValue("TRAFFICGEN_STC_LEARNING_MODE"),
                "--latency_type",
                settings.getValue("TRAFFICGEN_STC_LATENCY_TYPE"),
                "--rate_lower_limit_pct",
                settings.getValue("TRAFFICGEN_STC_RATE_LOWER_LIMIT_PCT"),
                "--rate_upper_limit_pct",
                settings.getValue("TRAFFICGEN_STC_RATE_UPPER_LIMIT_PCT"),
                "--rate_initial_pct",
                settings.getValue("TRAFFICGEN_STC_RATE_INITIAL_PCT"),
                "--rate_step_pct",
                settings.getValue("TRAFFICGEN_STC_RATE_STEP_PCT"),
                "--resolution_pct",
                settings.getValue("TRAFFICGEN_STC_RESOLUTION_PCT"),
                "--frame_size_list",
                str(framesize),
                "--acceptable_frame_loss_pct",
                settings.getValue("TRAFFICGEN_STC_ACCEPTABLE_FRAME_LOSS_PCT"),
                "--east_intf_addr",
                settings.getValue("TRAFFICGEN_STC_EAST_INTF_ADDR"),
                "--east_intf_gateway_addr",
                settings.getValue("TRAFFICGEN_STC_EAST_INTF_GATEWAY_ADDR"),
                "--west_intf_addr",
                settings.getValue("TRAFFICGEN_STC_WEST_INTF_ADDR"),
                "--west_intf_gateway_addr",
                settings.getValue("TRAFFICGEN_STC_WEST_INTF_GATEWAY_ADDR")]

        if settings.getValue("TRAFFICGEN_STC_VERBOSE") is "True":
            args.append("--verbose")
            verbose = True
            self._logger.info("Arguments used to call test: %s", args)
        subprocess.check_call(args)

        filecs = os.path.join(settings.getValue("TRAFFICGEN_STC_RESULTS_DIR"),
                              settings.getValue(
                                  "TRAFFICGEN_STC_CSV_RESULTS_FILE_PREFIX") +
                              ".csv")
        if verbose:
            self._logger.debug("file: %s", filecs)

        result = {}

        with open(filecs, "r") as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                self._logger.info("Row: %s", row)
                result[ResultsConstants.TX_RATE_FPS] = 0.0
                result[ResultsConstants.THROUGHPUT_RX_FPS] = 0.0
                result[ResultsConstants.TX_RATE_MBPS] = 0.0
                result[ResultsConstants.THROUGHPUT_RX_MBPS] = 0.0
                result[ResultsConstants.TX_RATE_PERCENT] = float(
                    row["OfferedLoad(%)"])
                result[ResultsConstants.THROUGHPUT_RX_PERCENT] = float(
                    row["Throughput(%)"])
                result[ResultsConstants.MIN_LATENCY_NS] = float(
                    row["MinimumLatency(us)"]) * 1000
                result[ResultsConstants.MAX_LATENCY_NS] = float(
                    row["MaximumLatency(us)"]) * 1000
                result[ResultsConstants.AVG_LATENCY_NS] = float(
                    row["AverageLatency(us)"]) * 1000
                result[ResultsConstants.FRAME_LOSS_PERCENT] = float(
                    row["PercentLoss"])
        return result

if __name__ == '__main__':
    TRAFFIC = {
        'l3': {
            'proto': 'tcp',
            'srcip': '1.1.1.1',
            'dstip': '90.90.90.90',
        },
    }
    with TestCenter() as dev:
        print(dev.send_rfc2544_throughput(traffic=TRAFFIC))
        print(dev.send_rfc2544_backtoback(traffic=TRAFFIC))
