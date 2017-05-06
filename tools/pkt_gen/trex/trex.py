# Copyright 2017 Martin Goldammer, OPNFV, Red Hat Inc.
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
"""
Trex Traffic Generator Model
"""
# pylint: disable=F0401, E0602
import logging
import subprocess
import sys
import os
from conf import settings
from conf import merge_spec
from core.results.results_constants import ResultsConstants
from tools.pkt_gen.trafficgen.trafficgen import ITrafficGenerator
sys.path.append(os.environ['TREX_PATH'])
from trex_stl_lib.api import *


class Trex(ITrafficGenerator):
    """Trex Traffic generator wrapper."""
    _logger = logging.getLogger(__name__)

    def __init__(self):
        """Trex class constructor."""
        super().__init__()
        self._logger.info("In trex __init__ method")
        self._params = {}
        self._trex_host_ip_addr = (
            settings.getValue('TRAFFICGEN_TREX_HOST_IP_ADDR'))
        self._trex_base_dir = (
            settings.getValue('TRAFFICGEN_TREX_BASE_DIR'))
        self._trex_user = settings.getValue('TRAFFICGEN_TREX_USER')
        self._stlclient = STLClient()

    def connect(self):
        '''Connect to Trex traffic generator

        Verify that Trex is on the system indicated by
        the configuration file
        '''
        self._logger.info("TREX:  In Trex connect method...")

        if self._trex_host_ip_addr:
            cmd_ping = "ping -c1 " + self._trex_host_ip_addr
        else:
            raise RuntimeError('TREX: Trex host not defined')

        ping = subprocess.Popen(cmd_ping, shell=True, stderr=subprocess.PIPE)
        output, error = ping.communicate()

        if ping.returncode:
            self._logger.error(error)
            self._logger.error(output)
            raise RuntimeError('TREX: Cannot ping Trex host at ' + \
                               self._trex_host_ip_addr)

        connect_trex = "ssh " + self._trex_user + \
                          "@" + self._trex_host_ip_addr

        cmd_find_trex = connect_trex + " ls " + \
                           self._trex_base_dir + "t-rex-64"


        find_trex = subprocess.Popen(cmd_find_trex,
                                     shell=True,
                                     stderr=subprocess.PIPE)
        output, error = find_trex.communicate()

        if find_trex.returncode:
            self._logger.error(error)
            self._logger.error(output)
            raise RuntimeError(
                'TREX: Cannot locate Trex program at %s within %s' \
                % (self._trex_host_ip_addr, self._trex_base_dir))

        self._logger.info("TREX: Trex host successfully found...")

    def disconnect(self):
        """Disconnect from the traffic generator.

        As with :func:`connect`, this function is optional.

        Where implemented, this function should raise an exception on
        failure.

        :returns: None
        """
        self._logger.info("TREX: In trex disconnect method")

    @staticmethod
    def create_packets(traffic, ports_info):
        """Create base packet according to traffic specification.
           If traffic haven't specified srcmac and dstmac fields
           packet will be create with mac address of trex server.
        """
        mac_add = [li['hw_mac'] for li in ports_info]

        if traffic and traffic['l2']['framesize'] > 0:
            if traffic['l2']['dstmac'] == '00:00:00:00:00:00'and \
               traffic['l2']['srcmac'] == '00:00:00:00:00:00':
                base_pkt_a = Ether(src=mac_add[0], dst=mac_add[1], \
                             )/IP(proto=traffic['l3']['proto'], \
                             src=traffic['l3']['srcip'], dst=traffic['l3']['dstip'])
                base_pkt_b = Ether(src=mac_add[1], dst=mac_add[0], \
                             )/IP(proto=traffic['l3']['proto'], \
                             src=traffic['l3']['dstip'], dst=traffic['l3']['srcip'])
            else:
                base_pkt_a = Ether(src=traffic['l2']['srcmac'], dst=traffic['l2']['dstmac'], \
                             )/IP(proto=traffic['l3']['proto'], \
                             src=traffic['l3']['srcip'], dst=traffic['l3']['dstip'])
                base_pkt_b = Ether(src=traffic['l2']['dstmac'], dst=traffic['l2']['srcmac'], \
                             )/IP(proto=traffic['l3']['proto'], \
                             src=traffic['l3']['dstip'], dst=traffic['l3']['srcip'])

        return (base_pkt_a, base_pkt_b)

    @staticmethod
    def create_streams(base_pkt_a, base_pkt_b, traffic, tput_frame_rate=None):
        """Add the base packet to the streams. Erase FCS and add payload
           according to traffic specification
        """
        frame_size = int(traffic['l2']['framesize'])
        fsize_no_fcs = frame_size - 4
        payload_a = max(0, fsize_no_fcs - len(base_pkt_a)) * 'x'
        payload_b = max(0, fsize_no_fcs - len(base_pkt_b)) * 'x'
        pkt_a = STLPktBuilder(pkt=base_pkt_a/payload_a)
        pkt_b = STLPktBuilder(pkt=base_pkt_b/payload_b)
        if tput_frame_rate:
            stream_1 = STLStream(packet=pkt_a,
                                 flow_stats=STLFlowLatencyStats(pg_id=0),
                                 name='stream_1',
                                 mode=STLTXCont(pps=tput_frame_rate))
            stream_2 = STLStream(packet=pkt_b,
                                 flow_stats=STLFlowLatencyStats(pg_id=1),
                                 name='stream_2',
                                 mode=STLTXCont(pps=tput_frame_rate))
        else:
            stream_1 = STLStream(packet=pkt_a,
                                 flow_stats=STLFlowLatencyStats(pg_id=0),
                                 name='stream_1',
                                 mode=STLTXCont(pps=traffic['frame_rate']))
            stream_2 = STLStream(packet=pkt_b,
                                 flow_stats=STLFlowLatencyStats(pg_id=1),
                                 name='stream_2',
                                 mode=STLTXCont(pps=traffic['frame_rate']))

        return (stream_1, stream_2)

    def send_cont_traffic(self, traffic=None, duration=30):
        """See ITrafficGenerator for description
        """
        self._logger.info("In Trex send_cont_traffic method")
        self._params.clear()

        results = {}
        self._params['traffic'] = self.traffic_defaults.copy()
        if traffic:
            self._params['traffic'] = merge_spec(
                self._params['traffic'], traffic)
        self._stlclient = STLClient(username=self._trex_user, server=self._trex_host_ip_addr,
                                    verbose_level=LoggerApi.VERBOSE_REGULAR)
        self._stlclient.connect()
        my_ports = [0, 1]
        self._stlclient.reset(my_ports)
        ports_info = self._stlclient.get_port_info(my_ports)
        packet_1, packet_2 = self.create_packets(traffic, ports_info)
        stream_1, stream_2 = self.create_streams(packet_1, packet_2, traffic)

        self._stlclient.add_streams(stream_1, ports=[0])
        self._stlclient.add_streams(stream_2, ports=[1])
        self._stlclient.clear_stats()
        self._stlclient.start(ports=[0, 1], force=True, duration=duration)
        self._stlclient.wait_on_traffic(ports=[0, 1])
        stats = self._stlclient.get_stats(sync_now=True)
        logging.debug("Detailed statistics reported by Trex: " + \
                      str(stats))
        results[ResultsConstants.TX_RATE_MBPS] = (
            '{:.3f}'.format(
                float(stats["total"]["tx_bps"] / 1000000)))

        results[ResultsConstants.TX_RATE_FPS] = (
            '{:.3f}'.format(
                float(stats["total"]["tx_pps"])))

        results[ResultsConstants.FRAME_LOSS_PERCENT] = (
            '{:.3f}'.format(
                float((stats["total"]["opackets"] - stats["total"]["ipackets"]) * 100 /
                      stats["total"]["opackets"])))

        results[ResultsConstants.MAX_LATENCY_NS] = (
            '{:.3f}'.format(
                (float(max(stats["latency"][0]["latency"]["total_max"],
                           stats["latency"][1]["latency"]["total_max"])))))

        results[ResultsConstants.AVG_LATENCY_NS] = (
            '{:.3f}'.format(
                float((stats["latency"][0]["latency"]["average"]+
                       stats["latency"][1]["latency"]["average"])/2)))

        results[ResultsConstants.MIN_LATENCY_NS] = (
            '{:.3f}'.format(
                (float(min(stats["latency"][0]["latency"]["total_min"],
                           stats["latency"][1]["latency"]["total_min"])))))

        results[ResultsConstants.THROUGHPUT_RX_FPS] = (
            '{:.3f}'.format(
                float(stats["total"]["opackets"] / duration)))

        return results

    def start_cont_traffic(self, traffic=None, duration=5):
        raise NotImplementedError(
            'Trex start cont traffic not implemented')

    def stop_cont_traffic(self):
        """See ITrafficGenerator for description
        """
        raise NotImplementedError(
            'Trex stop_cont_traffic method not implemented')

    def send_rfc2544_throughput(self, traffic=None, duration=20,
                                lossrate=0.0, tests=1):
        """See ITrafficGenerator for description
        """
        raise NotImplementedError(
            'Trex send rfc2544 throughput not implemented')

    def start_rfc2544_throughput(self, traffic=None, tests=1, duration=20,
                                 lossrate=0.0):
        raise NotImplementedError(
            'Trex start rfc2544 throughput not implemented')

    def wait_rfc2544_throughput(self):
        raise NotImplementedError(
            'Trex wait rfc2544 throughput not implemented')

    def send_burst_traffic(self, traffic=None, numpkts=100, duration=20):
        raise NotImplementedError(
            'Trex send burst traffic not implemented')

    def send_rfc2544_back2back(self, traffic=None, tests=1, duration=20,
                               lossrate=0.0):
        raise NotImplementedError(
            'Trex send rfc2544 back2back not implemented')

    def start_rfc2544_back2back(self, traffic=None, tests=1, duration=20,
                                lossrate=0.0):
        raise NotImplementedError(
            'Trex start rfc2544 back2back not implemented')

    def wait_rfc2544_back2back(self):
        raise NotImplementedError(
            'Trex wait rfc2544 back2back not implemented')

if __name__ == "__main__":
    pass
