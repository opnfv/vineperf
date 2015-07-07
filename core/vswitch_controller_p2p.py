# Copyright 2015 Intel Corporation.
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

"""VSwitch controller for Physical to Physical deployment
"""

import logging

from core.vswitch_controller import IVswitchController
from vswitches.utils import add_ports_to_flow

_FLOW_TEMPLATE = {
    'idle_timeout': '0'
}
BRIDGE_NAME = 'br0'

class VswitchControllerP2P(IVswitchController):
    """VSwitch controller for P2P deployment scenario.

    Attributes:
        _vswitch_class: The vSwitch class to be used.
        _vswitch: The vSwitch object controlled by this controller
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
    """
    def __init__(self, vswitch_class):
        """Initializes up the prerequisites for the P2P deployment scenario.

        :vswitch_class: the vSwitch class to be used.
        """
        self._logger = logging.getLogger(__name__)
        self._vswitch_class = vswitch_class
        self._vswitch = vswitch_class()
        self._deployment_scenario = "P2P"
        self._logger.debug('Creation using ' + str(self._vswitch_class))

    def setup(self):
        """Sets up the switch for p2p.
        """
        self._logger.debug('Setup using ' + str(self._vswitch_class))

        try:
            self._vswitch.start()

            self._vswitch.add_switch(BRIDGE_NAME)

            (_, phy1_number) = self._vswitch.add_phy_port(BRIDGE_NAME)
            (_, phy2_number) = self._vswitch.add_phy_port(BRIDGE_NAME)

            self._vswitch.del_flow(BRIDGE_NAME)

            # table#0 - flows designed to force 5 & 13 tuple matches go here
            flow = {'table':'0', 'priority':'1', 'actions': ['goto_table:1']}
            self._vswitch.add_flow(BRIDGE_NAME, flow)

            # table#1 - flows to route packets between ports goes here. The
            # chosen port is communicated to subsequent tables by setting the
            # metadata value to the egress port number
            flow = {'table':'1', 'priority':'1', 'in_port':'1',
                    'actions': ['write_actions(output:2)', 'write_metadata:2',
                        'goto_table:2']}
            self._vswitch.add_flow(BRIDGE_NAME, flow)
            flow = {'table':'1', 'priority':'1', 'in_port':'2',
                    'actions': ['write_actions(output:1)', 'write_metadata:1',
                        'goto_table:2']}
            self._vswitch.add_flow(BRIDGE_NAME, flow)

            # Frame modification table. Frame modification flow rules are
            # isolated in this table so that they can be turned on or off
            # without affecting the routing or tuple-matching flow rules.
            flow = {'table':'2', 'priority':'1', 'actions': ['goto_table:3']}
            self._vswitch.add_flow(BRIDGE_NAME, flow)

            # Egress table
            # (TODO) Billy O'Mahony - the drop action here actually required in
            # order to egress the packet. This is the subject of a thread on
            # ovs-discuss 2015-06-30.
            flow = {'table':'3', 'priority':'1', 'actions': ['drop']}
            self._vswitch.add_flow(BRIDGE_NAME, flow)

        except:
            self._vswitch.stop()
            raise

    def stop(self):
        """Tears down the switch created in setup().
        """
        self._logger.debug('Stop using ' + str(self._vswitch_class))
        self._vswitch.stop()

    def __enter__(self):
        self.setup()

    def __exit__(self, type_, value, traceback):
        self.stop()

    def get_vswitch(self):
        """See IVswitchController for description
        """
        return self._vswitch

    def get_ports_info(self):
        """See IVswitchController for description
        """
        self._logger.debug('get_ports_info  using ' + str(self._vswitch_class))
        return self._vswitch.get_ports(BRIDGE_NAME)
