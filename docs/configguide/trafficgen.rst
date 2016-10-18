.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

===========================
'vsperf' Traffic Gen Guide
===========================

Overview
---------------------
VSPERF supports the following traffic generators:

  * Dummy (DEFAULT): Allows you to use your own external
    traffic generator.
  * IXIA (IxNet and IxOS)
  * Spirent TestCenter
  * Xena Networks
  * MoonGen

To see the list of traffic gens from the cli:

.. code-block:: console

    $ ./vsperf --list-trafficgens

This guide provides the details of how to install
and configure the various traffic generators.

Background Information
----------------------
The traffic default configuration can be found in
tools/pkt_gen/trafficgen/trafficgenhelper.py, and is configured as
follows:

.. code-block:: console

    TRAFFIC_DEFAULTS = {
        'l2': {
            'framesize': 64,
            'srcmac': '00:00:00:00:00:00',
            'dstmac': '00:00:00:00:00:00',
        },
        'l3': {
            'proto': 'tcp',
            'srcip': '1.1.1.1',
            'dstip': '90.90.90.90',
        },
        'l4': {
            'srcport': 3000,
            'dstport': 3001,
        },
        'vlan': {
            'enabled': False,
            'id': 0,
            'priority': 0,
            'cfi': 0,
        },
    }

The framesize parameter can be overridden from the configuration
files by adding the following to your custom configuration file
``10_custom.conf``:

.. code-block:: console

    TRAFFICGEN_PKT_SIZES = (64, 128,)

OR from the commandline:

.. code-block:: console

    $ ./vsperf --test-params "pkt_sizes=x,y" $TESTNAME

You can also modify the traffic transmission duration and the number
of tests run by the traffic generator by extending the example
commandline above to:

.. code-block:: console

    $ ./vsperf --test-params "pkt_sizes=x,y;duration=10;rfc2544_tests=1" $TESTNAME

Dummy Setup
------------
To select the Dummy generator please add the following to your
custom configuration file ``10_custom.conf``.


.. code-block:: console

     TRAFFICGEN = 'Dummy'

OR run ``vsperf`` with the ``--trafficgen`` argument

.. code-block:: console

    $ ./vsperf --trafficgen Dummy $TESTNAME

Where $TESTNAME is the name of the vsperf test you would like to run.
This will setup the vSwitch and the VNF (if one is part of your test)
print the traffic configuration and prompt you to transmit traffic
when the setup is complete.

.. code-block:: console

    Please send 'continuous' traffic with the following stream config:
    30mS, 90mpps, multistream False
    and the following flow config:
    {
        "flow_type": "port",
        "l3": {
            "srcip": "1.1.1.1",
            "proto": "tcp",
            "dstip": "90.90.90.90"
        },
        "traffic_type": "continuous",
        "multistream": 0,
        "bidir": "True",
        "vlan": {
            "cfi": 0,
            "priority": 0,
            "id": 0,
            "enabled": false
        },
        "frame_rate": 90,
        "l2": {
            "dstport": 3001,
            "srcport": 3000,
            "dstmac": "00:00:00:00:00:00",
            "srcmac": "00:00:00:00:00:00",
            "framesize": 64
        }
    }
    What was the result for 'frames tx'?

When your traffic gen has completed traffic transmission and provided
the results please input these at the vsperf prompt. vsperf will try
to verify the input:

.. code-block:: console

    Is '$input_value' correct?

Please answer with y OR n.

VPSERF will ask you for:
  * Result for 'frames tx'
  * Result for 'frames rx'
  * Result for 'min latency'
  * Result for 'max latency'
  * Result for 'avg latency'

Finally vsperf will print out the results for your test and generate the
appropriate logs and csv files.


IXIA Setup
----------

On the CentOS 7 system
~~~~~~~~~~~~~~~~~~~~~~

You need to install IxNetworkTclClient$(VER\_NUM)Linux.bin.tgz.

On the IXIA client software system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find the IxNetwork TCL server app (start -> All Programs -> IXIA ->
IxNetwork -> IxNetwork\_$(VER\_NUM) -> IxNetwork TCL Server)

Right click on IxNetwork TCL Server, select properties - Under shortcut tab in
the Target dialogue box make sure there is the argument "-tclport xxxx"
where xxxx is your port number (take note of this port number as you will
need it for the 10\_custom.conf file).

.. image:: TCLServerProperties.png

Hit Ok and start the TCL server application

VSPERF configuration
~~~~~~~~~~~~~~~~~~~~

There are several configuration options specific to the IxNetworks traffic generator
from IXIA. It is essential to set them correctly, before the VSPERF is executed
for the first time.

Detailed description of options follows:

 * TRAFFICGEN_IXNET_MACHINE - IP address of server, where IxNetwork TCL Server is running
 * TRAFFICGEN_IXNET_PORT - PORT, where IxNetwork TCL Server is accepting connections from
   TCL clients
 * TRAFFICGEN_IXNET_USER - username, which will be used during communication with IxNetwork
   TCL Server and IXIA chassis
 * TRAFFICGEN_IXIA_HOST - IP address of IXIA traffic generator chassis
 * TRAFFICGEN_IXIA_CARD - identification of card with dedicated ports at IXIA chassis
 * TRAFFICGEN_IXIA_PORT1 - identification of the first dedicated port at TRAFFICGEN_IXIA_CARD
   at IXIA chassis; VSPERF uses two separated ports for traffic generation. In case of
   unidirectional traffic, it is essential to correctly connect 1st IXIA port to the 1st NIC
   at DUT, i.e. to the first PCI handle from WHITELIST_NICS list. Otherwise traffic may not
   be able to pass through the vSwitch.
 * TRAFFICGEN_IXIA_PORT2 - identification of the second dedicated port at TRAFFICGEN_IXIA_CARD
   at IXIA chassis; VSPERF uses two separated ports for traffic generation. In case of
   unidirectional traffic, it is essential to correctly connect 2nd IXIA port to the 2nd NIC
   at DUT, i.e. to the second PCI handle from WHITELIST_NICS list. Otherwise traffic may not
   be able to pass through the vSwitch.
 * TRAFFICGEN_IXNET_LIB_PATH - path to the DUT specific installation of IxNetwork TCL API
 * TRAFFICGEN_IXNET_TCL_SCRIPT - name of the TCL script, which VSPERF will use for
   communication with IXIA TCL server
 * TRAFFICGEN_IXNET_TESTER_RESULT_DIR - folder accessible from IxNetwork TCL server,
   where test results are stored, e.g. ``c:/ixia_results``; see test-results-share_
 * TRAFFICGEN_IXNET_DUT_RESULT_DIR - directory accessible from the DUT, where test
   results from IxNetwork TCL server are stored, e.g. ``/mnt/ixia_results``; see
   test-results-share_

.. _test-results-share:

Test results share
~~~~~~~~~~~~~~~~~~

VSPERF is not able to retrieve test results via TCL API directly. Instead, all test
results are stored at IxNetwork TCL server. Results are stored at folder defined by
``TRAFFICGEN_IXNET_TESTER_RESULT_DIR`` configuration parameter. Content of this
folder must be shared (e.g. via samba protocol) between TCL Server and DUT, where
VSPERF is executed. VSPERF expects, that test results will be available at directory
configured by ``TRAFFICGEN_IXNET_DUT_RESULT_DIR`` configuration parameter.

Example of sharing configuration:

 * Create a new folder at IxNetwork TCL server machine, e.g. ``c:\ixia_results``
 * Modify sharing options of ``ixia_results`` folder to share it with everybody
 * Create a new directory at DUT, where shared directory with results
   will be mounted, e.g. ``/mnt/ixia_results``
 * Update your custom VSPERF configuration file as follows:

   .. code-block:: python

       TRAFFICGEN_IXNET_TESTER_RESULT_DIR = 'c:/ixia_results'
       TRAFFICGEN_IXNET_DUT_RESULT_DIR = '/mnt/ixia_results'

   Note: It is essential to use slashes '/' also in path
   configured by ``TRAFFICGEN_IXNET_TESTER_RESULT_DIR`` parameter.
 * Install cifs-utils package.

   e.g. at rpm based Linux distribution:

   .. code-block:: console

       yum install cifs-utils

 * Mount shared directory, so VSPERF can access test results.

   e.g. by adding new record into ``/etc/fstab``

   .. code-block:: console

       mount -t cifs //_TCL_SERVER_IP_OR_FQDN_/ixia_results /mnt/ixia_results
             -o file_mode=0777,dir_mode=0777,nounix

It is recommended to verify, that any new file inserted into ``c:/ixia_results`` folder
is visible at DUT inside ``/mnt/ixia_results`` directory.

Spirent Setup
-------------

Spirent installation files and instructions are available on the
Spirent support website at:

http://support.spirent.com

Select a version of Spirent TestCenter software to utilize. This example
will use Spirent TestCenter v4.57 as an example. Substitute the appropriate
version in place of 'v4.57' in the examples, below.

On the CentOS 7 System
~~~~~~~~~~~~~~~~~~~~~~

Download and install the following:

Spirent TestCenter Application, v4.57 for 64-bit Linux Client

Spirent Virtual Deployment Service (VDS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Spirent VDS is required for both TestCenter hardware and virtual
chassis in the vsperf environment. For installation, select the version
that matches the Spirent TestCenter Application version. For v4.57,
the matching VDS version is 1.0.55. Download either the ova (VMware)
or qcow2 (QEMU) image and create a VM with it. Initialize the VM
according to Spirent installation instructions.

Using Spirent TestCenter Virtual (STCv)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

STCv is available in both ova (VMware) and qcow2 (QEMU) formats. For
VMware, download:

Spirent TestCenter Virtual Machine for VMware, v4.57 for Hypervisor - VMware ESX.ESXi

Virtual test port performance is affected by the hypervisor configuration. For
best practice results in deploying STCv, the following is suggested:

- Create a single VM with two test ports rather than two VMs with one port each
- Set STCv in DPDK mode
- Give STCv 2*n + 1 cores, where n = the number of ports. For vsperf, cores = 5.
- Turning off hyperthreading and pinning these cores will improve performance
- Give STCv 2 GB of RAM

To get the highest performance and accuracy, Spirent TestCenter hardware is
recommended. vsperf can run with either stype test ports.

Using STC REST Client
~~~~~~~~~~~~~~~~~~~~~
The stcrestclient package provides the stchttp.py ReST API wrapper module.
This allows simple function calls, nearly identical to those provided by
StcPython.py, to be used to access TestCenter server sessions via the
STC ReST API. Basic ReST functionality is provided by the resthttp module,
and may be used for writing ReST clients independent of STC.

- Project page: <https://github.com/Spirent/py-stcrestclient>
- Package download: <http://pypi.python.org/pypi/stcrestclient>

To use REST interface, follow the instructions in the Project page to
install the package. Once installed, the scripts named with 'rest' keyword
can be used. For example: testcenter-rfc2544-rest.py can be used to run
RFC 2544 tests using the REST interface.

Configuration:
~~~~~~~~~~~~~~
The mandatory configurations are enlisted below.

1. The Labserver and license server addresses. These parameters applies to
   all the tests and are mandatory.

.. code-block:: console

    TRAFFICGEN_STC_LAB_SERVER_ADDR = " "
    TRAFFICGEN_STC_LICENSE_SERVER_ADDR = " "

2. For RFC2544 tests, the following parameters are mandatory


.. code-block:: console

    TRAFFICGEN_STC_RFC2544_TPUT_TEST_FILE_NAME = " "
    TRAFFICGEN_STC_EAST_CHASSIS_ADDR = " "
    TRAFFICGEN_STC_EAST_SLOT_NUM = " "
    TRAFFICGEN_STC_EAST_PORT_NUM = " "
    TRAFFICGEN_STC_EAST_INTF_ADDR = " "
    TRAFFICGEN_STC_EAST_INTF_GATEWAY_ADDR = " "
    TRAFFICGEN_STC_WEST_CHASSIS_ADDR = ""
    TRAFFICGEN_STC_WEST_SLOT_NUM = " "
    TRAFFICGEN_STC_WEST_PORT_NUM = " "
    TRAFFICGEN_STC_WEST_INTF_ADDR = " "
    TRAFFICGEN_STC_WEST_INTF_GATEWAY_ADDR = " "

3. For RFC2889 tests, specifying the locations of the ports is mandatory.

.. code-block:: console

    TRAFFICGEN_STC_RFC2889_TEST_FILE_NAME = " "
    TRAFFICGEN_STC_RFC2889_LOCATIONS= " "

Xena Networks
-------------

Installation
~~~~~~~~~~~~

Xena Networks traffic generator requires specific files and packages to be
installed. It is assumed the user has access to the Xena2544.exe file which
must be placed in VSPerf installation location under the tools/pkt_gen/xena
folder. Contact Xena Networks for the latest version of this file. The user
can also visit www.xenanetworks/downloads to obtain the file with a valid
support contract.

**Note** VSPerf has been fully tested with version v2.43 of Xena2544.exe

To execute the Xena2544.exe file under Linux distributions the mono-complete
package must be installed. To install this package follow the instructions
below. Further information can be obtained from
http://www.mono-project.com/docs/getting-started/install/linux/

.. code-block:: console

    rpm --import "http://keyserver.ubuntu.com/pks/lookup?op=get&search=0x3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF"
    yum-config-manager --add-repo http://download.mono-project.com/repo/centos/
    yum -y install mono-complete

To prevent gpg errors on future yum installation of packages the mono-project
repo should be disabled once installed.

.. code-block:: console

    yum-config-manager --disable download.mono-project.com_repo_centos_

Configuration
~~~~~~~~~~~~~

Connection information for your Xena Chassis must be supplied inside the
``10_custom.conf`` or ``03_custom.conf`` file. The following parameters must be
set to allow for proper connections to the chassis.

.. code-block:: console

    TRAFFICGEN_XENA_IP = ''
    TRAFFICGEN_XENA_PORT1 = ''
    TRAFFICGEN_XENA_PORT2 = ''
    TRAFFICGEN_XENA_USER = ''
    TRAFFICGEN_XENA_PASSWORD = ''
    TRAFFICGEN_XENA_MODULE1 = ''
    TRAFFICGEN_XENA_MODULE2 = ''

RFC2544 Throughput Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Xena traffic generator testing for rfc2544 throughput can be modified for
different behaviors if needed. The default options for the following are
optimized for best results.

.. code-block:: console

    TRAFFICGEN_XENA_2544_TPUT_INIT_VALUE = '10.0'
    TRAFFICGEN_XENA_2544_TPUT_MIN_VALUE = '0.1'
    TRAFFICGEN_XENA_2544_TPUT_MAX_VALUE = '100.0'
    TRAFFICGEN_XENA_2544_TPUT_VALUE_RESOLUTION = '0.5'
    TRAFFICGEN_XENA_2544_TPUT_USEPASS_THRESHHOLD = 'false'
    TRAFFICGEN_XENA_2544_TPUT_PASS_THRESHHOLD = '0.0'

Each value modifies the behavior of rfc 2544 throughput testing. Refer to your
Xena documentation to understand the behavior changes in modifying these
values.

MoonGen
-------

Installation
~~~~~~~~~~~~

MoonGen architecture overview and general installation instructions
can be found here:

https://github.com/emmericp/MoonGen

* Note:  Today, MoonGen with VSPERF only supports 10Gbps line speeds.

For VSPerf use, MoonGen should be cloned from here (as opposed to the previously
mentioned GitHub):

git clone https://github.com/atheurer/MoonGen

and use the opnfv-stable branch:

git checkout opnfv-stable

VSPerf uses a particular example script under the examples directory within
the MoonGen project:

MoonGen/examples/opnfv-vsperf.lua

Follow MoonGen set up instructions here:

https://github.com/atheurer/MoonGen/blob/opnfv-stable/MoonGenSetUp.html

Note one will need to set up ssh login to not use passwords between the server
running MoonGen and the device under test (running the VSPERF test
infrastructure).  This is because VSPERF on one server uses 'ssh' to
configure and run MoonGen upon the other server.

One can set up this ssh access by doing the following on both servers:

.. code-block:: console

    ssh-keygen -b 2048 -t rsa
    ssh-copy-id <other server>

Configuration
~~~~~~~~~~~~~

Connection information for MoonGen must be supplied inside the
``10_custom.conf`` or ``03_custom.conf`` file. The following parameters must be
set to allow for proper connections to the host with MoonGen.

.. code-block:: console

    TRAFFICGEN_MOONGEN_HOST_IP_ADDR = ""
    TRAFFICGEN_MOONGEN_USER = ""
    TRAFFICGEN_MOONGEN_BASE_DIR = ""
    TRAFFICGEN_MOONGEN_PORTS = ""
    TRAFFICGEN_MOONGEN_LINE_SPEED_GBPS = ""
