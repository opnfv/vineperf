# Copyright 2016-2017 Spirent Communications.
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
#
# Invalid name of file, must be used '_' instead '-'
# pylint: disable=invalid-name
'''
@author Spirent Communications

This test automates the RFC2544 tests using the Spirent
TestCenter REST APIs. This test supports Python 3.4

'''
import argparse
import collections
import logging
import os
import sqlite3

_LOGGER = logging.getLogger(__name__)

GENOME_PKTSIZE_ENCODING = {"a": 64, "b": 128, "c": 256, "d": 512,
                           "e": 1024, "f": 1280, "g": 1518, "h": 2112}


def genome2weights(sequence):
    """ Convert genome sequence to packetsize weights"""
    weights = collections.defaultdict(int)
    for char in GENOME_PKTSIZE_ENCODING:
        charcount = sequence.count(char)
        if charcount:
            weights[GENOME_PKTSIZE_ENCODING[char]] = charcount
    return weights


def create_dir(path):
    """Create the directory as specified in path """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as ex:
            _LOGGER.error("Failed to create directory %s: %s", path, str(ex))
            raise


def write_histogram_to_csv(results_path, csv_results_file_prefix,
                           counts, ranges):
    """ Write the results of the query to the CSV """
    filec = os.path.join(results_path, csv_results_file_prefix + ".csv")
    with open(filec, "wb") as result_file:
        for key in counts:
            result_file.write(str(key) + "\n")
            result_file.write(str(ranges) + "\n")
            result_file.write(str(counts[key]) + "\n")


def write_query_results_to_csv(results_path, csv_results_file_prefix,
                               query_results):
    """ Write the results of the query to the CSV """
    create_dir(results_path)
    filec = os.path.join(results_path, csv_results_file_prefix + ".csv")
    with open(filec, "wb") as result_file:
        result_file.write(query_results["Columns"].replace(" ", ",") + "\n")
        for row in (query_results["Output"].replace("} {", ",").
                    replace("{", "").replace("}", "").split(",")):
            result_file.write(row.replace(" ", ",") + "\n")


def positive_int(value):
    """ Positive Integer type for Arguments """
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(
            "%s is an invalid positive int value" % value)
    return ivalue


def percent_float(value):
    """ Floating type for Arguments """
    pvalue = float(value)
    if pvalue < 0.0 or pvalue > 100.0:
        raise argparse.ArgumentTypeError(
            "%s not in range [0.0, 100.0]" % pvalue)
    return pvalue


# pylint: disable=too-many-branches, too-many-statements, too-many-locals
def main():
    """ Read the arguments, Invoke Test and Return the results"""
    parser = argparse.ArgumentParser()
    # Required parameters
    required_named = parser.add_argument_group("required named arguments")
    required_named.add_argument("--lab_server_addr",
                                required=True,
                                help=("The IP address of the"
                                      "Spirent Lab Server"),
                                dest="lab_server_addr")
    required_named.add_argument("--license_server_addr",
                                required=True,
                                help=("The IP address of the Spirent"
                                      "License Server"),
                                dest="license_server_addr")
    required_named.add_argument("--east_chassis_addr",
                                required=True,
                                help=("The TestCenter chassis IP address to"
                                      "use for the east test port"),
                                dest="east_chassis_addr")
    required_named.add_argument("--east_slot_num",
                                type=positive_int,
                                required=True,
                                help=("The TestCenter slot number to"
                                      "use for the east test port"),
                                dest="east_slot_num")
    required_named.add_argument("--east_port_num",
                                type=positive_int,
                                required=True,
                                help=("The TestCenter port number to use"
                                      "for the east test port"),
                                dest="east_port_num")
    required_named.add_argument("--west_chassis_addr",
                                required=True,
                                help=("The TestCenter chassis IP address"
                                      "to use for the west test port"),
                                dest="west_chassis_addr")
    required_named.add_argument("--west_slot_num",
                                type=positive_int,
                                required=True,
                                help=("The TestCenter slot number to use"
                                      "for the west test port"),
                                dest="west_slot_num")
    required_named.add_argument("--west_port_num",
                                type=positive_int,
                                required=True,
                                help=("The TestCenter port number to"
                                      "use for the west test port"),
                                dest="west_port_num")
    # Optional parameters
    optional_named = parser.add_argument_group("optional named arguments")
    optional_named.add_argument("--metric",
                                required=False,
                                help=("One among - throughput, latency,\
                                      backtoback and frameloss"),
                                choices=["throughput", "latency",
                                         "backtoback", "frameloss"],
                                default="throughput",
                                dest="metric")
    optional_named.add_argument("--test_session_name",
                                required=False,
                                default="RFC2544 East-West Throughput",
                                help=("The friendly name to identify"
                                      "the Spirent Lab Server test session"),
                                dest="test_session_name")

    optional_named.add_argument("--test_user_name",
                                required=False,
                                default="RFC2544 East-West User",
                                help=("The friendly name to identify the"
                                      "Spirent Lab Server test user"),
                                dest="test_user_name")
    optional_named.add_argument("--results_dir",
                                required=False,
                                default="./Results",
                                help="The directory to copy results to",
                                dest="results_dir")
    optional_named.add_argument("--vsperf_results_dir",
                                required=False,
                                default="./Results",
                                help="The directory to copy results to",
                                dest="vsperf_results_dir")
    optional_named.add_argument("--csv_results_file_prefix",
                                required=False,
                                default="Rfc2544Tput",
                                help="The prefix for the CSV results files",
                                dest="csv_results_file_prefix")
    optional_named.add_argument("--num_trials",
                                type=positive_int,
                                required=False,
                                default=1,
                                help=("The number of trials to execute during"
                                      "the test"),
                                dest="num_trials")
    optional_named.add_argument("--trial_duration_sec",
                                type=positive_int,
                                required=False,
                                default=60,
                                help=("The duration of each trial executed"
                                      "during the test"),
                                dest="trial_duration_sec")
    optional_named.add_argument("--traffic_pattern",
                                required=False,
                                choices=["BACKBONE", "MESH", "PAIR"],
                                default="PAIR",
                                help="The traffic pattern between endpoints",
                                dest="traffic_pattern")
    optional_named.add_argument("--traffic_custom",
                                required=False,
                                default=None,
                                help="The traffic pattern between endpoints",
                                dest="traffic_custom")
    optional_named.add_argument("--search_mode",
                                required=False,
                                choices=["COMBO", "STEP", "BINARY"],
                                default="BINARY",
                                help=("The search mode used to find the"
                                      "throughput rate"),
                                dest="search_mode")
    optional_named.add_argument("--learning_mode",
                                required=False,
                                choices=["AUTO", "L2_LEARNING",
                                         "L3_LEARNING", "NONE"],
                                default="AUTO",
                                help=("The learning mode used during the test,"
                                      "default is 'NONE'"),
                                dest="learning_mode")
    optional_named.add_argument("--rate_lower_limit_pct",
                                type=percent_float,
                                required=False,
                                default=1.0,
                                help=("The minimum percent line rate that"
                                      "will be used during the test"),
                                dest="rate_lower_limit_pct")
    optional_named.add_argument("--rate_upper_limit_pct",
                                type=percent_float,
                                required=False,
                                default=99.0,
                                help=("The maximum percent line rate that"
                                      "will be used during the test"),
                                dest="rate_upper_limit_pct")
    optional_named.add_argument("--rate_initial_pct",
                                type=percent_float,
                                required=False,
                                default=99.0,
                                help=("If Search Mode is BINARY, the percent"
                                      "line rate that will be used at the"
                                      "start of the test"),
                                dest="rate_initial_pct")
    optional_named.add_argument("--rate_step_pct",
                                type=percent_float,
                                required=False,
                                default=10.0,
                                help=("If SearchMode is STEP, the percent"
                                      "load increase per step"),
                                dest="rate_step_pct")
    optional_named.add_argument("--resolution_pct",
                                type=percent_float,
                                required=False,
                                default=1.0,
                                help=("The minimum percentage of load"
                                      "adjustment between iterations"),
                                dest="resolution_pct")
    optional_named.add_argument("--frame_size_list",
                                type=lambda s: [int(item)
                                                for item in s.split(',')],
                                required=False,
                                default=[256],
                                help="A comma-delimited list of frame sizes",
                                dest="frame_size_list")
    optional_named.add_argument("--acceptable_frame_loss_pct",
                                type=percent_float,
                                required=False,
                                default=0.0,
                                help=("The maximum acceptable frame loss"
                                      "percent in any iteration"),
                                dest="acceptable_frame_loss_pct")
    optional_named.add_argument("--east_intf_addr",
                                required=False,
                                default="192.85.1.3",
                                help=("The address to assign to the first"
                                      "emulated device interface on the first"
                                      "east port"),
                                dest="east_intf_addr")
    optional_named.add_argument("--east_intf_gateway_addr",
                                required=False,
                                default="192.85.1.53",
                                help=("The gateway address to assign to the"
                                      "first emulated device interface on the"
                                      "first east port"),
                                dest="east_intf_gateway_addr")
    optional_named.add_argument("--west_intf_addr",
                                required=False,
                                default="192.85.1.53",
                                help=("The address to assign to the first"
                                      "emulated device interface on the"
                                      "first west port"),
                                dest="west_intf_addr")
    optional_named.add_argument("--west_intf_gateway_addr",
                                required=False,
                                default="192.85.1.53",
                                help=("The gateway address to assign to"
                                      "the first emulated device interface"
                                      "on the first west port"),
                                dest="west_intf_gateway_addr")
    optional_named.add_argument("--latency_histogram",
                                required=False,
                                action="store_true",
                                help="latency histogram is required in output?",
                                dest="latency_histogram")
    optional_named.add_argument("--imix",
                                required=False,
                                default="",
                                help=("IMIX specification as genome"
                                      "Encoding - RFC 6985"),
                                dest="imix")
    parser.add_argument("-v",
                        "--verbose",
                        required=False,
                        default=True,
                        help="More output during operation when present",
                        action="store_true",
                        dest="verbose")
    args = parser.parse_args()

    if args.verbose:
        _LOGGER.debug("Creating results directory")
    create_dir(args.results_dir)

    session_name = args.test_session_name
    user_name = args.test_user_name
    # pylint: disable=import-error
    try:
        # Load Spirent REST Library
        from stcrestclient import stchttp

        stc = stchttp.StcHttp(args.lab_server_addr)
        session_id = stc.new_session(user_name, session_name)
        stc.join_session(session_id)
    except RuntimeError as err:
        _LOGGER.error(err)
        raise

    # Get STC system info.
    tx_port_loc = "//%s/%s/%s" % (args.east_chassis_addr,
                                  args.east_slot_num,
                                  args.east_port_num)
    rx_port_loc = "//%s/%s/%s" % (args.west_chassis_addr,
                                  args.west_slot_num,
                                  args.west_port_num)

    # Retrieve and display the server information
    if args.verbose:
        _LOGGER.debug("SpirentTestCenter system version: %s",
                      stc.get("system1", "version"))

    # pylint: disable=too-many-nested-blocks
    try:
        device_list = []
        port_list = []
        if args.verbose:
            _LOGGER.debug("Bring up license server")
        license_mgr = stc.get("system1", "children-licenseservermanager")
        if args.verbose:
            _LOGGER.debug("license_mgr = %s", license_mgr)
        stc.create("LicenseServer", under=license_mgr, attributes={
            "server": args.license_server_addr})

        # Create the root project object
        if args.verbose:
            _LOGGER.debug("Creating project ...")
        project = stc.get("System1", "children-Project")

        # Configure any custom traffic parameters
        if args.traffic_custom == "cont":
            if args.verbose:
                _LOGGER.debug("Configure Continuous Traffic")
            stc.create("ContinuousTestConfig", under=project)

        # Create ports
        if args.verbose:
            _LOGGER.debug("Creating ports ...")
        east_chassis_port = stc.create('port', project)
        if args.verbose:
            _LOGGER.debug("Configuring TX port ...")
        stc.config(east_chassis_port, {'location': tx_port_loc})
        port_list.append(east_chassis_port)

        west_chassis_port = stc.create('port', project)
        if args.verbose:
            _LOGGER.debug("Configuring RX port ...")
        stc.config(west_chassis_port, {'location': rx_port_loc})
        port_list.append(west_chassis_port)

        # Create emulated genparam for east port
        east_device_gen_params = stc.create("EmulatedDeviceGenParams",
                                            under=project,
                                            attributes={"Port":
                                                        east_chassis_port})
        # Create the DeviceGenEthIIIfParams object
        stc.create("DeviceGenEthIIIfParams",
                   under=east_device_gen_params,
                   attributes={'UseDefaultPhyMac': True})

        # Configuring Ipv4 interfaces
        stc.create("DeviceGenIpv4IfParams",
                   under=east_device_gen_params,
                   attributes={"Addr": args.east_intf_addr,
                               "Gateway": args.east_intf_gateway_addr})
        # Create Devices using the Device Wizard
        device_gen_config = stc.perform("DeviceGenConfigExpand",
                                        params={"DeleteExisting": "No",
                                                "GenParams":
                                                east_device_gen_params})
        # Append to the device list
        device_list.append(device_gen_config['ReturnList'])

        # Create emulated genparam for west port
        west_device_gen_params = stc.create("EmulatedDeviceGenParams",
                                            under=project,
                                            attributes={"Port":
                                                        west_chassis_port})
        # Create the DeviceGenEthIIIfParams object
        stc.create("DeviceGenEthIIIfParams",
                   under=west_device_gen_params,
                   attributes={'UseDefaultPhyMac': True})

        # Configuring Ipv4 interfaces
        stc.create("DeviceGenIpv4IfParams",
                   under=west_device_gen_params,
                   attributes={"Addr": args.west_intf_addr,
                               "Gateway": args.west_intf_gateway_addr})
        # Create Devices using the Device Wizard
        device_gen_config = stc.perform("DeviceGenConfigExpand",
                                        params={"DeleteExisting": "No",
                                                "GenParams":
                                                west_device_gen_params})
        # Append to the device list
        device_list.append(device_gen_config['ReturnList'])
        if args.verbose:
            _LOGGER.debug(device_list)

        # Configure Histogram
        if args.latency_histogram:
            # Generic Configuration
            histResOptions = stc.get("project1", 'children-ResultOptions')
            stc.config(histResOptions, {'ResultViewMode': 'HISTOGRAM'})
            # East Port Configuration
            histAnaEast = stc.get(east_chassis_port, 'children-Analyzer')
            histAnaEastConfig = stc.get(histAnaEast, 'children-AnalyzerConfig')
            stc.config(histAnaEastConfig, {'HistogramMode': 'LATENCY'})
            eLatHist = stc.get(histAnaEastConfig, 'children-LatencyHistogram')
            stc.config(eLatHist, {'ConfigMode': 'CONFIG_LIMIT_MODE',
                                  'BucketSizeUnit': 'ten_nanoseconds',
                                  'Active': 'TRUE',
                                  'DistributionMode': 'CENTERED_MODE'})
            # West Port Configuration
            histAnaWest = stc.get(west_chassis_port, 'children-Analyzer')
            histAnaWestConfig = stc.get(histAnaWest, 'children-AnalyzerConfig')
            stc.config(histAnaWestConfig, {'HistogramMode': 'LATENCY'})
            wLatHist = stc.get(histAnaWestConfig, 'children-LatencyHistogram')
            stc.config(wLatHist, {'ConfigMode': 'CONFIG_LIMIT_MODE',
                                  'BucketSizeUnit': 'ten_nanoseconds',
                                  'Active': 'TRUE',
                                  'DistributionMode': 'CENTERED_MODE'})
            gBucketSizeList = stc.get(wLatHist, 'BucketSizeList')
            # gLimitSizeList  = stc.get(wLatHist, 'LimitList')

        # IMIX configuration
        fld = None
        if args.imix:
            args.frame_size_list = []
            weights = genome2weights(args.imix)
            fld = stc.create('FrameLengthDistribution', under=project)
            def_slots = stc.get(fld, "children-framelengthdistributionslot")
            stc.perform("Delete", params={"ConfigList": def_slots})
            for fsize in weights:
                stc.create('framelengthdistributionslot', under=fld,
                           attributes={'FixedFrameLength': fsize,
                                       'Weight': weights[fsize]})

        # Create the RFC 2544 'metric test
        if args.metric == "throughput":
            if args.verbose:
                _LOGGER.debug("Set up the RFC2544 throughput test...")
            stc.perform("Rfc2544SetupThroughputTestCommand",
                        params={"AcceptableFrameLoss":
                                args.acceptable_frame_loss_pct,
                                "Duration": args.trial_duration_sec,
                                "FrameSizeList": args.frame_size_list,
                                "LearningMode": args.learning_mode,
                                "NumOfTrials": args.num_trials,
                                "RateInitial": args.rate_initial_pct,
                                "RateLowerLimit": args.rate_lower_limit_pct,
                                "RateStep": args.rate_step_pct,
                                "RateUpperLimit": args.rate_upper_limit_pct,
                                "Resolution": args.resolution_pct,
                                "SearchMode": args.search_mode,
                                "TrafficPattern": args.traffic_pattern,
                                "FrameSizeDistributionList": fld})
        elif args.metric == "backtoback":
            stc.perform("Rfc2544SetupBackToBackTestCommand",
                        params={"AcceptableFrameLoss":
                                args.acceptable_frame_loss_pct,
                                "Duration": args.trial_duration_sec,
                                "FrameSizeList": args.frame_size_list,
                                "LearningMode": args.learning_mode,
                                "LatencyType": args.latency_type,
                                "NumOfTrials": args.num_trials,
                                "RateInitial": args.rate_initial_pct,
                                "RateLowerLimit": args.rate_lower_limit_pct,
                                "RateStep": args.rate_step_pct,
                                "RateUpperLimit": args.rate_upper_limit_pct,
                                "Resolution": args.resolution_pct,
                                "SearchMode": args.search_mode,
                                "TrafficPattern": args.traffic_pattern})
        elif args.metric == "frameloss":
            stc.perform("Rfc2544SetupFrameLossTestCommand",
                        params={"AcceptableFrameLoss":
                                args.acceptable_frame_loss_pct,
                                "Duration": args.trial_duration_sec,
                                "FrameSizeList": args.frame_size_list,
                                "LearningMode": args.learning_mode,
                                "LatencyType": args.latency_type,
                                "NumOfTrials": args.num_trials,
                                "RateInitial": args.rate_initial_pct,
                                "RateLowerLimit": args.rate_lower_limit_pct,
                                "RateStep": args.rate_step_pct,
                                "RateUpperLimit": args.rate_upper_limit_pct,
                                "Resolution": args.resolution_pct,
                                "SearchMode": args.search_mode,
                                "TrafficPattern": args.traffic_pattern})
        elif args.metric == "latency":
            stc.perform("Rfc2544SetupLatencyTestCommand",
                        params={"AcceptableFrameLoss":
                                args.acceptable_frame_loss_pct,
                                "Duration": args.trial_duration_sec,
                                "FrameSizeList": args.frame_size_list,
                                "LearningMode": args.learning_mode,
                                "LatencyType": args.latency_type,
                                "NumOfTrials": args.num_trials,
                                "RateInitial": args.rate_initial_pct,
                                "RateLowerLimit": args.rate_lower_limit_pct,
                                "RateStep": args.rate_step_pct,
                                "RateUpperLimit": args.rate_upper_limit_pct,
                                "Resolution": args.resolution_pct,
                                "SearchMode": args.search_mode,
                                "TrafficPattern": args.traffic_pattern})

        # Save the configuration
        stc.perform("SaveToTcc", params={"Filename": "2544.tcc"})
        # Connect to the hardware...
        stc.perform("AttachPorts", params={"portList": stc.get(
            "system1.project", "children-port"), "autoConnect": "TRUE"})
        # Apply configuration.
        if args.verbose:
            _LOGGER.debug("Apply configuration...")
        stc.apply()

        if args.verbose:
            _LOGGER.debug("Starting the sequencer...")
        stc.perform("SequencerStart")

        # Wait for sequencer to finish
        _LOGGER.info(
            "Starting test... Please wait for the test to complete...")
        stc.wait_until_complete()
        _LOGGER.info("The test has completed... Saving results...")

        # Determine what the results database filename is...
        lab_server_resultsdb = stc.get(
            "system1.project.TestResultSetting", "CurrentResultFileName")

        if args.verbose:
            _LOGGER.debug("The lab server results database is %s",
                          lab_server_resultsdb)

        # Create Latency Histogram CSV file()
        if args.latency_histogram:
            hist_dict_counts = {}
            for file_url in stc.files():
                if '-FrameSize-' in file_url:
                    stc.download(file_url)
                    filename = file_url.split('/')[-1]
                    if os.path.exists(os.getcwd() + '/' + filename):
                        conn = sqlite3.connect(os.getcwd() + '/' + filename)
                        # cursor = conn.execute(
                        #    'select * from RxEotStreamResults')
                        # names = [desc[0] for desc in cursor.description]
                        counts = conn.execute("SELECT \
                                              HistBin1Count, HistBin2Count,\
                                              HistBin3Count, HistBin4Count,\
                                              HistBin5Count, HistBin6Count,\
                                              HistBin7Count, HistBin8Count,\
                                              HistBin9Count, HistBin10Count,\
                                              HistBin11Count, HistBin12Count,\
                                              HistBin13Count, HistBin14Count, \
                                              HistBin15Count, HistBin16Count \
                                              from RxEotStreamResults")
                        strs = filename.split('-')
                        key = strs[strs.index('FrameSize')+1]
                        if key in hist_dict_counts:
                            hist_dict_counts[key] = [a+b for a, b in
                                                     zip(counts.fetchone(),
                                                         hist_dict_counts[key])]
                        else:
                            hist_dict_counts[key] = counts.fetchone()
                        conn.close()

            write_histogram_to_csv(args.vsperf_results_dir, 'Histogram',
                                   hist_dict_counts,
                                   gBucketSizeList)

        stc.perform("CSSynchronizeFiles",
                    params={"DefaultDownloadDir": args.results_dir})

        resultsdb = args.results_dir + \
            lab_server_resultsdb.split("/Results")[1]

        if not os.path.exists(resultsdb):
            resultsdb = lab_server_resultsdb
            _LOGGER.info("Failed to create the local summary DB File, using"
                         " the remote DB file instead.")
        else:
            _LOGGER.info(
                "The local summary DB file has been saved to %s", resultsdb)

        # The returns the "RFC2544ThroughputTestResultDetailedSummaryView"
        # table view from the results database.
        # There are other views available.

        if args.metric == "throughput":
            resultsdict = (
                stc.perform("QueryResult",
                            params={
                                "DatabaseConnectionString":
                                resultsdb,
                                "ResultPath":
                                ("RFC2544ThroughputTestResultDetailed"
                                 "SummaryView")}))

        # The returns the "RFC2544BacktoBackTestResultDetailedSummaryView"
        # table view from the results database.
        # There are other views available.
        elif args.metric == "backtoback":
            resultsdict = (
                stc.perform("QueryResult",
                            params={
                                "DatabaseConnectionString":
                                resultsdb,
                                "ResultPath":
                                ("RFC2544Back2BackTestResultDetailed"
                                 "SummaryView")}))

        # The returns the "RFC2544LatencyTestResultDetailedSummaryView"
        # table view from the results database.
        # There are other views available.
        elif args.metric == "latency":
            resultsdict = (
                stc.perform("QueryResult",
                            params={
                                "DatabaseConnectionString":
                                resultsdb,
                                "ResultPath":
                                ("RFC2544LatencyTestResultDetailed"
                                 "SummaryView")}))

        # The returns the "RFC2544FrameLossTestResultDetailedSummaryView"
        # table view from the results database.
        # There are other views available.
        elif args.metric == "frameloss":
            resultsdict = (
                stc.perform("QueryResult",
                            params={
                                "DatabaseConnectionString":
                                resultsdb,
                                "ResultPath":
                                ("RFC2544FrameLossTestResultDetailed"
                                 "SummaryView")}))
        if args.verbose:
            _LOGGER.debug("resultsdict[\"Columns\"]: %s",
                          resultsdict["Columns"])
            _LOGGER.debug("resultsdict[\"Output\"]: %s", resultsdict["Output"])
            _LOGGER.debug("Result paths: %s",
                          stc.perform("GetTestResultSettingPaths"))

            # Write results to csv
            _LOGGER.debug("Writing CSV file to results directory %s",
                          args.results_dir)
        write_query_results_to_csv(
            args.results_dir, args.csv_results_file_prefix, resultsdict)

    except RuntimeError as e:
        _LOGGER.error(e)

    if args.verbose:
        _LOGGER.debug("Destroy session on lab server")
    stc.end_session()

    _LOGGER.info("Test complete!")

if __name__ == "__main__":
    main()
