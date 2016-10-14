.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

Integration tests
=================

VSPERF includes a set of integration tests defined in conf/integration.
These tests can be run by specifying --integration as a parameter to vsperf.
Current tests in conf/integration include switch functionality and Overlay
tests.

Tests in the conf/integration can be used to test scaling of different switch
configurations by adding steps into the test case.

For the overlay tests VSPERF supports VXLAN, GRE and GENEVE tunneling protocols.
Testing of these protocols is limited to unidirectional traffic and
P2P (Physical to Physical scenarios).

NOTE: The configuration for overlay tests provided in this guide is for
unidirectional traffic only.

Executing Integration Tests
---------------------------

To execute integration tests VSPERF is run with the integration parameter. To
view the current test list simply execute the following command:

.. code-block:: console

    ./vsperf --integration --list

The standard tests included are defined inside the
``conf/integration/01_testcases.conf`` file.

Test Steps
----------

Execution of integration tests are done on a step by step work flow starting
with step 0 as defined inside the test case. Each step of the test increments
the step number by one which is indicated in the log.

.. code-block:: console

    (testcases.integration) - Step 1 - 'vswitch add_switch ['int_br1']' ... OK

Each step in the test case is validated. If a step does not pass validation the
test will fail and terminate. The test will continue until a failure is detected
or all steps pass. A csv report file is generated after a test completes with an
OK or FAIL result.

Test objects and their functions
--------------------------------

Every test step can call a function of one of the supported test objects. The list
of supported objects and their most common functions follows:

    * ``vswitch`` - provides functions for vSwitch configuration

      List of supported functions:

        * ``add_switch br_name`` - creates a new switch (bridge) with given ``br_name``
        * ``del_switch br_name`` - deletes switch (bridge) with given ``br_name``
        * ``add_phy_port br_name`` - adds a physical port into bridge specified by ``br_name``
        * ``add_vport br_name`` - adds a virtual port into bridge specified by ``br_name``
        * ``del_port br_name port_name`` - removes physical or virtual port specified by
          ``port_name`` from bridge ``br_name``
        * ``add_flow br_name flow`` - adds flow specified by ``flow`` dictionary into
          the bridge ``br_name``; Content of flow dictionary will be passed to the vSwitch.
          In case of Open vSwitch it will be passed to the ``ovs-ofctl add-flow`` command.
          Please see Open vSwitch documentation for the list of supported flow parameters.
        * ``del_flow br_name [flow]`` - deletes flow specified by ``flow`` dictionary from
          bridge ``br_name``; In case that optional parameter ``flow`` is not specified
          or set to an empty dictionary ``{}``, then all flows from bridge ``br_name``
          will be deleted.
        * ``dump_flows br_name`` - dumps all flows from bridge specified by ``br_name``
        * ``enable_stp br_name`` - enables Spanning Tree Protocol for bridge ``br_name``
        * ``disable_stp br_name`` - disables Spanning Tree Protocol for bridge ``br_name``
        * ``enable_rstp br_name`` - enables Rapid Spanning Tree Protocol for bridge ``br_name``
        * ``disable_rstp br_name`` - disables Rapid Spanning Tree Protocol for bridge ``br_name``

        Examples:

        .. code-block:: python

            ['vswitch', 'add_switch', 'int_br0']

            ['vswitch', 'del_switch', 'int_br0']

            ['vswitch', 'add_phy_port', 'int_br0']

            ['vswitch', 'del_port', 'int_br0', '#STEP[2][0]']

            ['vswitch', 'add_flow', 'int_br0', {'in_port': '1', 'actions': ['output:2'],
             'idle_timeout': '0'}],

            ['vswitch', 'enable_rstp', 'int_br0']

    * ``vnf[ID]`` - provides functions for deployment and termination of VNFs; Optional
      alfanumerical ``ID`` is used for VNF identification in case that testcase
      deploys multiple VNFs.

      List of supported functions:

        * ``start`` - starts a VNF based on VSPERF configuration
        * ``stop`` - gracefully terminates given VNF

        Examples:

        .. code-block:: python

            ['vnf1', 'start']
            ['vnf2', 'start']
            ['vnf2', 'stop']
            ['vnf1', 'stop']

    * ``trafficgen`` - triggers traffic generation

      List of supported functions:

        * ``send_traffic traffic`` - starts a traffic based on the vsperf configuration
          and given ``traffic`` dictionary. More details about ``traffic`` dictionary
          and its possible values are available at `Traffic Generator Integration Guide
          <http://artifacts.opnfv.org/vswitchperf/docs/design/trafficgen_integration_guide.html#step-5-supported-traffic-types>`__

        Examples:

        .. code-block:: python

            ['trafficgen', 'send_traffic', {'traffic_type' : 'throughput'}]

            ['trafficgen', 'send_traffic', {'traffic_type' : 'back2back', 'bidir' : 'True'}]

    * ``settings`` - reads or modifies VSPERF configuration

      List of supported functions:

        * ``getValue param`` - returns value of given ``param``
        * ``setValue param value`` - sets value of ``param`` to given ``value``

        Examples:

        .. code-block:: python

            ['settings', 'getValue', 'TOOLS']

            ['settings', 'setValue', 'GUEST_USERNAME', ['root']]

    * ``namespace`` - creates or modifies network namespaces

      List of supported functions:

        * ``create_namespace name`` - creates new namespace with given ``name``
        * ``delete_namespace name`` - deletes namespace specified by its ``name``
        * ``assign_port_to_namespace port name [port_up]`` - assigns NIC specified by ``port``
          into given namespace ``name``; If optional parameter ``port_up`` is set to ``True``,
          then port will be brought up.
        * ``add_ip_to_namespace_eth port name addr cidr`` - assigns an IP address ``addr``/``cidr``
          to the NIC specified by ``port`` within namespace ``name``
        * ``reset_port_to_root port name`` - returns given ``port`` from namespace ``name`` back
          to the root namespace

        Examples:

        .. code-block:: python

            ['namespace', 'create_namespace', 'testns']

            ['namespace', 'assign_port_to_namespace', 'eth0', 'testns']

    * ``veth`` - manipulates with eth and veth devices

      List of supported functions:

        * ``add_veth_port port peer_port`` - adds a pair of veth ports named ``port`` and
          ``peer_port``
        * ``del_veth_port port peer_port`` - deletes a veth port pair specified by ``port``
          and ``peer_port``
        * ``bring_up_eth_port eth_port [namespace]`` - brings up ``eth_port`` in (optional)
          ``namespace``

        Examples:

        .. code-block:: python

            ['veth', 'add_veth_port', 'veth', 'veth1']

            ['veth', 'bring_up_eth_port', 'eth1']

    * ``tools`` - provides a set of helper functions

      List of supported functions:

        * ``Assert condition`` - evaluates given ``condition`` and raises ``AssertionError``
          in case that condition is not ``True``
        * ``Eval expression`` - evaluates given expression as a python code and returns
          its result
        * ``Exec command [regex]`` - executes a shell command and filters its output by
          (optional) regular expression

        Examples:

        .. code-block:: python

            ['tools', 'exec', 'numactl -H', 'available: ([0-9]+)']
            ['tools', 'assert', '#STEP[-1][0]>1']

    * ``wait`` - is used for test case interruption. This object doesn't have
      any functions. Once reached, vsperf will pause test execution and waits
      for press of ``Enter key``. It can be used during testcase design
      for debugging purposes.

      Examples:

      .. code-block:: python

        ['wait']

Test Macros
-----------

Test profiles can include macros as part of the test step. Each step in the
profile may return a value such as a port name. Recall macros use #STEP to
indicate the recalled value inside the return structure. If the method the
test step calls returns a value it can be later recalled, for example:

.. code-block:: python

    {
        "Name": "vswitch_add_del_vport",
        "Deployment": "clean",
        "Description": "vSwitch - add and delete virtual port",
        "TestSteps": [
                ['vswitch', 'add_switch', 'int_br0'],               # STEP 0
                ['vswitch', 'add_vport', 'int_br0'],                # STEP 1
                ['vswitch', 'del_port', 'int_br0', '#STEP[1][0]'],  # STEP 2
                ['vswitch', 'del_switch', 'int_br0'],               # STEP 3
             ]
    }

This test profile uses the vswitch add_vport method which returns a string
value of the port added. This is later called by the del_port method using the
name from step 1.

It is also possible to use negative indexes in step macros. In that case
``#STEP[-1]`` will refer to the result from previous step, ``#STEP[-2]``
will refer to result of step called before previous step, etc. It means,
that you could change ``STEP 2`` from previous example to achieve the same
functionality:

.. code-block:: python

                ['vswitch', 'del_port', 'int_br0', '#STEP[-1][0]'],  # STEP 2

Also commonly used steps can be created as a separate profile.

.. code-block:: python

    STEP_VSWITCH_PVP_INIT = [
        ['vswitch', 'add_switch', 'int_br0'],           # STEP 0
        ['vswitch', 'add_phy_port', 'int_br0'],         # STEP 1
        ['vswitch', 'add_phy_port', 'int_br0'],         # STEP 2
        ['vswitch', 'add_vport', 'int_br0'],            # STEP 3
        ['vswitch', 'add_vport', 'int_br0'],            # STEP 4
    ]

This profile can then be used inside other testcases

.. code-block:: python

    {
        "Name": "vswitch_pvp",
        "Deployment": "clean",
        "Description": "vSwitch - configure switch and one vnf",
        "TestSteps": STEP_VSWITCH_PVP_INIT +
                     [
                        ['vnf', 'start'],
                        ['vnf', 'stop'],
                     ] +
                     STEP_VSWITCH_PVP_FINIT
    }

HelloWorld and other basic Testcases
------------------------------------

The following examples are for demonstration purposes.
You can run them by copying and pasting into the
conf/integration/01_testcases.conf file.
A command-line instruction is shown at the end of each
example.

HelloWorld
^^^^^^^^^^

The first example is a HelloWorld testcase.
It simply creates a bridge with 2 physical ports, then sets up a flow to drop
incoming packets from the port that was instantiated at the STEP #1.
There's no interaction with the traffic generator.
Then the flow, the 2 ports and the bridge are deleted.
'add_phy_port' method creates a 'dpdk' type interface that will manage the
physical port. The string value returned is the port name that will be referred
by 'del_port' later on.

.. code-block:: python

    {
        "Name": "HelloWorld",
        "Description": "My first testcase",
        "Deployment": "clean",
        "TestSteps": [
            ['vswitch', 'add_switch', 'int_br0'],   # STEP 0
            ['vswitch', 'add_phy_port', 'int_br0'], # STEP 1
            ['vswitch', 'add_phy_port', 'int_br0'], # STEP 2
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'actions': ['drop'], 'idle_timeout': '0'}],
            ['vswitch', 'del_flow', 'int_br0'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[1][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[2][0]'],
            ['vswitch', 'del_switch', 'int_br0'],
        ]

    }

To run HelloWorld test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration HelloWorld

Specify a Flow by the IP address
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The next example shows how to explicitly set up a flow by specifying a
destination IP address.
All packets received from the port created at STEP #1 that have a destination
IP address = 90.90.90.90 will be forwarded to the port created at the STEP #2.

.. code-block:: python

    {
        "Name": "p2p_rule_l3da",
        "Description": "Phy2Phy with rule on L3 Dest Addr",
        "Deployment": "clean",
        "biDirectional": "False",
        "TestSteps": [
            ['vswitch', 'add_switch', 'int_br0'],   # STEP 0
            ['vswitch', 'add_phy_port', 'int_br0'], # STEP 1
            ['vswitch', 'add_phy_port', 'int_br0'], # STEP 2
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'dl_type': '0x0800', 'nw_dst': '90.90.90.90', \
                'actions': ['output:#STEP[2][1]'], 'idle_timeout': '0'}],
            ['trafficgen', 'send_traffic', {'traffic_type' : 'continuous'}],
            ['vswitch', 'dump_flows', 'int_br0'],   # STEP 5
            ['vswitch', 'del_flow', 'int_br0'],     # STEP 7 == del-flows
            ['vswitch', 'del_port', 'int_br0', '#STEP[1][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[2][0]'],
            ['vswitch', 'del_switch', 'int_br0'],
        ]
    },

To run the test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration p2p_rule_l3da

Multistream feature
^^^^^^^^^^^^^^^^^^^

The next testcase uses the multistream feature.
The traffic generator will send packets with different UDP ports.
That is accomplished by using "Stream Type" and "MultiStream" keywords.
4 different flows are set to forward all incoming packets.

.. code-block:: python

    {
        "Name": "multistream_l4",
        "Description": "Multistream on UDP ports",
        "Deployment": "clean",
        "Stream Type": "L4",
        "MultiStream": 4,
        "TestSteps": [
            ['vswitch', 'add_switch', 'int_br0'],   # STEP 0
            ['vswitch', 'add_phy_port', 'int_br0'], # STEP 1
            ['vswitch', 'add_phy_port', 'int_br0'], # STEP 2
            # Setup Flows
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'dl_type': '0x0800', 'nw_proto': '17', 'udp_dst': '0', \
                'actions': ['output:#STEP[2][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'dl_type': '0x0800', 'nw_proto': '17', 'udp_dst': '1', \
                'actions': ['output:#STEP[2][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'dl_type': '0x0800', 'nw_proto': '17', 'udp_dst': '2', \
                'actions': ['output:#STEP[2][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'dl_type': '0x0800', 'nw_proto': '17', 'udp_dst': '3', \
                'actions': ['output:#STEP[2][1]'], 'idle_timeout': '0'}],
            # Send mono-dir traffic
            ['trafficgen', 'send_traffic', {'traffic_type' : 'continuous', \
                'bidir' : 'False'}],
            # Clean up
            ['vswitch', 'del_flow', 'int_br0'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[1][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[2][0]'],
            ['vswitch', 'del_switch', 'int_br0'],
         ]
    },

To run the test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration multistream_l4

PVP with a VM Replacement
^^^^^^^^^^^^^^^^^^^^^^^^^

This example launches a 1st VM in a PVP topology, then the VM is replaced
by another VM.
When VNF setup parameter in ./conf/04_vnf.conf is "QemuDpdkVhostUser"
'add_vport' method creates a 'dpdkvhostuser' type port to connect a VM.

.. code-block:: python

    {
        "Name": "ex_replace_vm",
        "Description": "PVP with VM replacement",
        "Deployment": "clean",
        "TestSteps": [
            ['vswitch', 'add_switch', 'int_br0'],       # STEP 0
            ['vswitch', 'add_phy_port', 'int_br0'],     # STEP 1
            ['vswitch', 'add_phy_port', 'int_br0'],     # STEP 2
            ['vswitch', 'add_vport', 'int_br0'],        # STEP 3    vm1
            ['vswitch', 'add_vport', 'int_br0'],        # STEP 4

            # Setup Flows
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'actions': ['output:#STEP[3][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[4][1]', \
                'actions': ['output:#STEP[2][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[2][1]', \
                'actions': ['output:#STEP[4][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[3][1]', \
                'actions': ['output:#STEP[1][1]'], 'idle_timeout': '0'}],

            # Start VM 1
            ['vnf1', 'start'],
            # Now we want to replace VM 1 with another VM
            ['vnf1', 'stop'],

            ['vswitch', 'add_vport', 'int_br0'],        # STEP 11    vm2
            ['vswitch', 'add_vport', 'int_br0'],        # STEP 12
            ['vswitch', 'del_flow', 'int_br0'],
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'actions': ['output:#STEP[11][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[12][1]', \
                'actions': ['output:#STEP[2][1]'], 'idle_timeout': '0'}],

            # Start VM 2
            ['vnf2', 'start'],
            ['vnf2', 'stop'],
            ['vswitch', 'dump_flows', 'int_br0'],

            # Clean up
            ['vswitch', 'del_flow', 'int_br0'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[1][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[2][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[3][0]'],    # vm1
            ['vswitch', 'del_port', 'int_br0', '#STEP[4][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[11][0]'],   # vm2
            ['vswitch', 'del_port', 'int_br0', '#STEP[12][0]'],
            ['vswitch', 'del_switch', 'int_br0'],
        ]
    },

To run the test:

  .. code-block:: console

     ./vsperf --conf-file user_settings.py --integration ex_replace_vm

VM with a Linux bridge
^^^^^^^^^^^^^^^^^^^^^^

In this example a command-line parameter allows to set up a Linux bridge into
the guest VM.
That's one of the available ways to specify the guest application.
Packets matching the flow will be forwarded to the VM.

.. code-block:: python

    {
        "Name": "ex_pvp_rule_l3da",
        "Description": "PVP with flow on L3 Dest Addr",
        "Deployment": "clean",
        "TestSteps": [
            ['vswitch', 'add_switch', 'int_br0'],       # STEP 0
            ['vswitch', 'add_phy_port', 'int_br0'],     # STEP 1
            ['vswitch', 'add_phy_port', 'int_br0'],     # STEP 2
            ['vswitch', 'add_vport', 'int_br0'],        # STEP 3    vm1
            ['vswitch', 'add_vport', 'int_br0'],        # STEP 4
            # Setup Flows
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'dl_type': '0x0800', 'nw_dst': '90.90.90.90', \
                'actions': ['output:#STEP[3][1]'], 'idle_timeout': '0'}],
            # Each pkt from the VM is forwarded to the 2nd dpdk port
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[4][1]', \
                'actions': ['output:#STEP[2][1]'], 'idle_timeout': '0'}],
            # Start VMs
            ['vnf1', 'start'],
            ['trafficgen', 'send_traffic', {'traffic_type' : 'continuous', \
                'bidir' : 'False'}],
            ['vnf1', 'stop'],
            # Clean up
            ['vswitch', 'dump_flows', 'int_br0'],       # STEP 10
            ['vswitch', 'del_flow', 'int_br0'],         # STEP 11
            ['vswitch', 'del_port', 'int_br0', '#STEP[1][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[2][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[3][0]'],  # vm1 ports
            ['vswitch', 'del_port', 'int_br0', '#STEP[4][0]'],
            ['vswitch', 'del_switch', 'int_br0'],
        ]
    },

To run the test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --test-params
            "guest_loopback=linux_bridge" --integration ex_pvp_rule_l3da

Forward packets based on UDP port
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This examples launches 2 VMs connected in parallel.
Incoming packets will be forwarded to one specific VM depending on the
destination UDP port.

.. code-block:: python

    {
        "Name": "ex_2pvp_rule_l4dp",
        "Description": "2 PVP with flows on L4 Dest Port",
        "Deployment": "clean",
        "Stream Type": "L4",    # loop UDP ports
        "MultiStream": 2,
        "TestSteps": [
            ['vswitch', 'add_switch', 'int_br0'],       # STEP 0
            ['vswitch', 'add_phy_port', 'int_br0'],     # STEP 1
            ['vswitch', 'add_phy_port', 'int_br0'],     # STEP 2
            ['vswitch', 'add_vport', 'int_br0'],        # STEP 3    vm1
            ['vswitch', 'add_vport', 'int_br0'],        # STEP 4
            ['vswitch', 'add_vport', 'int_br0'],        # STEP 5    vm2
            ['vswitch', 'add_vport', 'int_br0'],        # STEP 6
            # Setup Flows to reply ICMPv6 and similar packets, so to
            # avoid flooding internal port with their re-transmissions
            ['vswitch', 'add_flow', 'int_br0', \
                {'priority': '1', 'dl_src': '00:00:00:00:00:01', \
                'actions': ['output:#STEP[3][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', \
                {'priority': '1', 'dl_src': '00:00:00:00:00:02', \
                'actions': ['output:#STEP[4][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', \
                {'priority': '1', 'dl_src': '00:00:00:00:00:03', \
                'actions': ['output:#STEP[5][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', \
                {'priority': '1', 'dl_src': '00:00:00:00:00:04', \
                'actions': ['output:#STEP[6][1]'], 'idle_timeout': '0'}],
            # Forward UDP packets depending on dest port
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'dl_type': '0x0800', 'nw_proto': '17', 'udp_dst': '0', \
                'actions': ['output:#STEP[3][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[1][1]', \
                'dl_type': '0x0800', 'nw_proto': '17', 'udp_dst': '1', \
                'actions': ['output:#STEP[5][1]'], 'idle_timeout': '0'}],
            # Send VM output to phy port #2
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[4][1]', \
                'actions': ['output:#STEP[2][1]'], 'idle_timeout': '0'}],
            ['vswitch', 'add_flow', 'int_br0', {'in_port': '#STEP[6][1]', \
                'actions': ['output:#STEP[2][1]'], 'idle_timeout': '0'}],
            # Start VMs
            ['vnf1', 'start'],                          # STEP 16
            ['vnf2', 'start'],                          # STEP 17
            ['trafficgen', 'send_traffic', {'traffic_type' : 'continuous', \
                'bidir' : 'False'}],
            ['vnf1', 'stop'],
            ['vnf2', 'stop'],
            ['vswitch', 'dump_flows', 'int_br0'],
            # Clean up
            ['vswitch', 'del_flow', 'int_br0'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[1][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[2][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[3][0]'],  # vm1 ports
            ['vswitch', 'del_port', 'int_br0', '#STEP[4][0]'],
            ['vswitch', 'del_port', 'int_br0', '#STEP[5][0]'],  # vm2 ports
            ['vswitch', 'del_port', 'int_br0', '#STEP[6][0]'],
            ['vswitch', 'del_switch', 'int_br0'],
        ]
    },

To run the test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration ex_2pvp_rule_l4dp

Executing Tunnel encapsulation tests
------------------------------------

The VXLAN OVS DPDK encapsulation tests requires IPs, MAC addresses,
bridge names and WHITELIST_NICS for DPDK.

NOTE: Only Ixia traffic generators currently support the execution of the tunnel
encapsulation tests. Support for other traffic generators may come in a future
release.

Default values are already provided. To customize for your environment, override
the following variables in you user_settings.py file:

  .. code-block:: python

    # Variables defined in conf/integration/02_vswitch.conf
    # Tunnel endpoint for Overlay P2P deployment scenario
    # used for br0
    VTEP_IP1 = '192.168.0.1/24'

    # Used as remote_ip in adding OVS tunnel port and
    # to set ARP entry in OVS (e.g. tnl/arp/set br-ext 192.168.240.10 02:00:00:00:00:02
    VTEP_IP2 = '192.168.240.10'

    # Network to use when adding a route for inner frame data
    VTEP_IP2_SUBNET = '192.168.240.0/24'

    # Bridge names
    TUNNEL_INTEGRATION_BRIDGE = 'br0'
    TUNNEL_EXTERNAL_BRIDGE = 'br-ext'

    # IP of br-ext
    TUNNEL_EXTERNAL_BRIDGE_IP = '192.168.240.1/24'

    # vxlan|gre|geneve
    TUNNEL_TYPE = 'vxlan'

    # Variables defined conf/integration/03_traffic.conf
    # For OP2P deployment scenario
    TRAFFICGEN_PORT1_MAC = '02:00:00:00:00:01'
    TRAFFICGEN_PORT2_MAC = '02:00:00:00:00:02'
    TRAFFICGEN_PORT1_IP = '1.1.1.1'
    TRAFFICGEN_PORT2_IP = '192.168.240.10'

To run VXLAN encapsulation tests:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=vxlan' overlay_p2p_tput

To run GRE encapsulation tests:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=gre' overlay_p2p_tput

To run GENEVE encapsulation tests:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=geneve' overlay_p2p_tput

To run OVS NATIVE tunnel tests (VXLAN/GRE/GENEVE):

1. Install the OVS kernel modules

  .. code:: console

    cd src/ovs/ovs
    sudo -E make modules_install

2. Set the following variables:

  .. code-block:: python

    VSWITCH = 'OvsVanilla'
    # Specify vport_* kernel module to test.
    PATHS['vswitch']['OvsVanilla']['src']['modules'] = [
        'vport_vxlan',
        'vport_gre',
        'vport_geneve',
        'datapath/linux/openvswitch.ko',
    ]

  **NOTE:** In case, that Vanilla OVS is installed from binary package, then
  please set ``PATHS['vswitch']['OvsVanilla']['bin']['modules']`` instead.

3. Run tests:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=vxlan' overlay_p2p_tput


Executing VXLAN decapsulation tests
------------------------------------

To run VXLAN decapsulation tests:

1. Set the variables used in "Executing Tunnel encapsulation tests"

2. Set dstmac of DUT_NIC2_MAC to the MAC adddress of the 2nd NIC of your DUT

  .. code-block:: python

    DUT_NIC2_MAC = '<DUT NIC2 MAC>'

3. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration overlay_p2p_decap_cont

If you want to use different values for your VXLAN frame, you may set:

  .. code-block:: python

    VXLAN_FRAME_L3 = {'proto': 'udp',
                      'packetsize': 64,
                      'srcip': TRAFFICGEN_PORT1_IP,
                      'dstip': '192.168.240.1',
                     }
    VXLAN_FRAME_L4 = {'srcport': 4789,
                      'dstport': 4789,
                      'vni': VXLAN_VNI,
                      'inner_srcmac': '01:02:03:04:05:06',
                      'inner_dstmac': '06:05:04:03:02:01',
                      'inner_srcip': '192.168.0.10',
                      'inner_dstip': '192.168.240.9',
                      'inner_proto': 'udp',
                      'inner_srcport': 3000,
                      'inner_dstport': 3001,
                     }


Executing GRE decapsulation tests
---------------------------------

To run GRE decapsulation tests:

1. Set the variables used in "Executing Tunnel encapsulation tests"

2. Set dstmac of DUT_NIC2_MAC to the MAC adddress of the 2nd NIC of your DUT

  .. code-block:: python

    DUT_NIC2_MAC = '<DUT NIC2 MAC>'

3. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --test-params 'tunnel_type=gre'
             --integration overlay_p2p_decap_cont


If you want to use different values for your GRE frame, you may set:

  .. code-block:: python

    GRE_FRAME_L3 = {'proto': 'gre',
                    'packetsize': 64,
                    'srcip': TRAFFICGEN_PORT1_IP,
                    'dstip': '192.168.240.1',
                   }

    GRE_FRAME_L4 = {'srcport': 0,
                    'dstport': 0
                    'inner_srcmac': '01:02:03:04:05:06',
                    'inner_dstmac': '06:05:04:03:02:01',
                    'inner_srcip': '192.168.0.10',
                    'inner_dstip': '192.168.240.9',
                    'inner_proto': 'udp',
                    'inner_srcport': 3000,
                    'inner_dstport': 3001,
                   }


Executing GENEVE decapsulation tests
------------------------------------

IxNet 7.3X does not have native support of GENEVE protocol. The
template, GeneveIxNetTemplate.xml_ClearText.xml, should be imported
into IxNET for this testcase to work.

To import the template do:

1. Run the IxNetwork TCL Server
2. Click on the Traffic menu
3. Click on the Traffic actions and click Edit Packet Templates
4. On the Template editor window, click Import. Select the template
   located at ``3rd_party/ixia/GeneveIxNetTemplate.xml_ClearText.xml``
   and click import.
5. Restart the TCL Server.

To run GENEVE decapsulation tests:

1. Set the variables used in "Executing Tunnel encapsulation tests"

2. Set dstmac of DUT_NIC2_MAC to the MAC adddress of the 2nd NIC of your DUT

  .. code-block:: python

    DUT_NIC2_MAC = '<DUT NIC2 MAC>'

3. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --test-params 'tunnel_type=geneve'
             --integration overlay_p2p_decap_cont


If you want to use different values for your GENEVE frame, you may set:

  .. code-block:: python

    GENEVE_FRAME_L3 = {'proto': 'udp',
                       'packetsize': 64,
                       'srcip': TRAFFICGEN_PORT1_IP,
                       'dstip': '192.168.240.1',
                      }

    GENEVE_FRAME_L4 = {'srcport': 6081,
                       'dstport': 6081,
                       'geneve_vni': 0,
                       'inner_srcmac': '01:02:03:04:05:06',
                       'inner_dstmac': '06:05:04:03:02:01',
                       'inner_srcip': '192.168.0.10',
                       'inner_dstip': '192.168.240.9',
                       'inner_proto': 'udp',
                       'inner_srcport': 3000,
                       'inner_dstport': 3001,
                      }


Executing Native/Vanilla OVS VXLAN decapsulation tests
------------------------------------------------------

To run VXLAN decapsulation tests:

1. Set the following variables in your user_settings.py file:

  .. code-block:: python

    PATHS['vswitch']['OvsVanilla']['src']['modules'] = [
        'vport_vxlan',
        'datapath/linux/openvswitch.ko',
    ]

    DUT_NIC1_MAC = '<DUT NIC1 MAC ADDRESS>'

    TRAFFICGEN_PORT1_IP = '172.16.1.2'
    TRAFFICGEN_PORT2_IP = '192.168.1.11'

    VTEP_IP1 = '172.16.1.2/24'
    VTEP_IP2 = '192.168.1.1'
    VTEP_IP2_SUBNET = '192.168.1.0/24'
    TUNNEL_EXTERNAL_BRIDGE_IP = '172.16.1.1/24'
    TUNNEL_INT_BRIDGE_IP = '192.168.1.1'

    VXLAN_FRAME_L2 = {'srcmac':
                      '01:02:03:04:05:06',
                      'dstmac': DUT_NIC1_MAC
                     }

    VXLAN_FRAME_L3 = {'proto': 'udp',
                      'packetsize': 64,
                      'srcip': TRAFFICGEN_PORT1_IP,
                      'dstip': '172.16.1.1',
                     }

    VXLAN_FRAME_L4 = {
                      'srcport': 4789,
                      'dstport': 4789,
                      'protocolpad': 'true',
                      'vni': 99,
                      'inner_srcmac': '01:02:03:04:05:06',
                      'inner_dstmac': '06:05:04:03:02:01',
                      'inner_srcip': '192.168.1.2',
                      'inner_dstip': TRAFFICGEN_PORT2_IP,
                      'inner_proto': 'udp',
                      'inner_srcport': 3000,
                      'inner_dstport': 3001,
                     }

  **NOTE:** In case, that Vanilla OVS is installed from binary package, then
  please set ``PATHS['vswitch']['OvsVanilla']['bin']['modules']`` instead.

2. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=vxlan' overlay_p2p_decap_cont

Executing Native/Vanilla OVS GRE decapsulation tests
----------------------------------------------------

To run GRE decapsulation tests:

1. Set the following variables in your user_settings.py file:

  .. code-block:: python

    PATHS['vswitch']['OvsVanilla']['src']['modules'] = [
        'vport_gre',
        'datapath/linux/openvswitch.ko',
    ]

    DUT_NIC1_MAC = '<DUT NIC1 MAC ADDRESS>'

    TRAFFICGEN_PORT1_IP = '172.16.1.2'
    TRAFFICGEN_PORT2_IP = '192.168.1.11'

    VTEP_IP1 = '172.16.1.2/24'
    VTEP_IP2 = '192.168.1.1'
    VTEP_IP2_SUBNET = '192.168.1.0/24'
    TUNNEL_EXTERNAL_BRIDGE_IP = '172.16.1.1/24'
    TUNNEL_INT_BRIDGE_IP = '192.168.1.1'

    GRE_FRAME_L2 = {'srcmac':
                    '01:02:03:04:05:06',
                    'dstmac': DUT_NIC1_MAC
                   }

    GRE_FRAME_L3 = {'proto': 'udp',
                    'packetsize': 64,
                    'srcip': TRAFFICGEN_PORT1_IP,
                    'dstip': '172.16.1.1',
                   }

    GRE_FRAME_L4 = {
                    'srcport': 4789,
                    'dstport': 4789,
                    'protocolpad': 'true',
                    'inner_srcmac': '01:02:03:04:05:06',
                    'inner_dstmac': '06:05:04:03:02:01',
                    'inner_srcip': '192.168.1.2',
                    'inner_dstip': TRAFFICGEN_PORT2_IP,
                    'inner_proto': 'udp',
                    'inner_srcport': 3000,
                    'inner_dstport': 3001,
                   }

  **NOTE:** In case, that Vanilla OVS is installed from binary package, then
  please set ``PATHS['vswitch']['OvsVanilla']['bin']['modules']`` instead.

2. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=gre' overlay_p2p_decap_cont

Executing Native/Vanilla OVS GENEVE decapsulation tests
-------------------------------------------------------

To run GENEVE decapsulation tests:

1. Set the following variables in your user_settings.py file:

  .. code-block:: python

    PATHS['vswitch']['OvsVanilla']['src']['modules'] = [
        'vport_geneve',
        'datapath/linux/openvswitch.ko',
    ]

    DUT_NIC1_MAC = '<DUT NIC1 MAC ADDRESS>'

    TRAFFICGEN_PORT1_IP = '172.16.1.2'
    TRAFFICGEN_PORT2_IP = '192.168.1.11'

    VTEP_IP1 = '172.16.1.2/24'
    VTEP_IP2 = '192.168.1.1'
    VTEP_IP2_SUBNET = '192.168.1.0/24'
    TUNNEL_EXTERNAL_BRIDGE_IP = '172.16.1.1/24'
    TUNNEL_INT_BRIDGE_IP = '192.168.1.1'

    GENEVE_FRAME_L2 = {'srcmac':
                       '01:02:03:04:05:06',
                       'dstmac': DUT_NIC1_MAC
                      }

    GENEVE_FRAME_L3 = {'proto': 'udp',
                       'packetsize': 64,
                       'srcip': TRAFFICGEN_PORT1_IP,
                       'dstip': '172.16.1.1',
                      }

    GENEVE_FRAME_L4 = {'srcport': 6081,
                       'dstport': 6081,
                       'protocolpad': 'true',
                       'geneve_vni': 0,
                       'inner_srcmac': '01:02:03:04:05:06',
                       'inner_dstmac': '06:05:04:03:02:01',
                       'inner_srcip': '192.168.1.2',
                       'inner_dstip': TRAFFICGEN_PORT2_IP,
                       'inner_proto': 'udp',
                       'inner_srcport': 3000,
                       'inner_dstport': 3001,
                      }

  **NOTE:** In case, that Vanilla OVS is installed from binary package, then
  please set ``PATHS['vswitch']['OvsVanilla']['bin']['modules']`` instead.

2. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=geneve' overlay_p2p_decap_cont


Executing Tunnel encapsulation+decapsulation tests
--------------------------------------------------

The OVS DPDK encapsulation_decapsulation tests requires IPs, MAC addresses,
bridge names and WHITELIST_NICS for DPDK.

The test cases can test the tunneling encap and decap without using any ingress
overlay traffic as compared to above test cases. To achieve this the OVS is
configured to perform encap and decap in a series on the same traffic stream as
given below.

TRAFFIC-IN --> [ENCAP] --> [MOD-PKT] --> [DECAP] --> TRAFFIC-OUT


Default values are already provided. To customize for your environment, override
the following variables in you user_settings.py file:

  .. code-block:: python

    # Variables defined in conf/integration/02_vswitch.conf

    # Bridge names
    TUNNEL_EXTERNAL_BRIDGE1 = 'br-phy1'
    TUNNEL_EXTERNAL_BRIDGE2 = 'br-phy2'
    TUNNEL_MODIFY_BRIDGE1 = 'br-mod1'
    TUNNEL_MODIFY_BRIDGE2 = 'br-mod2'

    # IP of br-mod1
    TUNNEL_MODIFY_BRIDGE_IP1 = '10.0.0.1/24'

    # Mac of br-mod1
    TUNNEL_MODIFY_BRIDGE_MAC1 = '00:00:10:00:00:01'

    # IP of br-mod2
    TUNNEL_MODIFY_BRIDGE_IP2 = '20.0.0.1/24'

    #Mac of br-mod2
    TUNNEL_MODIFY_BRIDGE_MAC2 = '00:00:20:00:00:01'

    # vxlan|gre|geneve, Only VXLAN is supported for now.
    TUNNEL_TYPE = 'vxlan'

To run VXLAN encapsulation+decapsulation tests:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             overlay_p2p_mod_tput
