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

The framesize paramter can be overridden from the configuration
files by adding the following to your custom configuration file
``10_custom.conf``:

.. code-block:: console

    TRAFFICGEN_PKT_SIZES = (64, 128,)

OR from the commandline:

.. code-block:: console

    $ ./vsperf --test-params "pkt_sizes=x,y" $TESTNAME

You can also modify the traffic transmission duration and the number
of trials run by the traffic generator by extending the example
commandline above to:

.. code-block:: console

    $ ./vsperf --test-params "pkt_sizes=x,y;duration=10;rfc2455_trials=3" $TESTNAME

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
where xxxx is your port number (take note of this port number you will
need it for the 10\_custom.conf file).

.. image:: TCLServerProperties.png

Hit Ok and start the TCL server application

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

Xena Networks
-------------

Installation
~~~~~~~~~~~~

Xena Networks traffic generator requires certain files and packages to be
installed. It is assumed the user has access to the Xena2544.exe file which
must be placed in VSPerf installation location under the tools/pkt_gen/xena
folder. Contact Xena Networks for the latest version of this file. The user
can also visit www.xenanetworks/downloads to obtain the file with a valid
support contract.

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
