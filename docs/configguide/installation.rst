.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

======================
Installing vswitchperf
======================

Supported Operating Systems
---------------------------

* CentOS 7
* Fedora 20
* Fedora 21
* Fedora 22
* RedHat 7.2
* Ubuntu 14.04

Supported vSwitches
-------------------
The vSwitch must support Open Flow 1.3 or greater.

* OVS (built from source).
* OVS with DPDK (built from source).

Supported Hypervisors
---------------------

* Qemu version 2.3.

Available VNFs
--------------
A simple VNF that forwards traffic through a VM, using:

* DPDK testpmd
* Linux Brigde
* custom l2fwd module

The official VM image is called vloop-vnf and it is available for free
download at OPNFV website.

vloop-vnf changelog:
====================

* `vloop-vnf-ubuntu-14.04_20160823`_

  * ethtool installed
  * only 1 NIC is configured by default to speed up boot with 1 NIC setup
  * security updates applied

* `vloop-vnf-ubuntu-14.04_20160804`_

  * Linux kernel 4.4.0 installed
  * libnuma-dev installed
  * security updates applied

* `vloop-vnf-ubuntu-14.04_20160303`_

  * snmpd service is disabled by default to avoid error messages during VM boot
  * security updates applied

* `vloop-vnf-ubuntu-14.04_20151216`_

  * version with development tools required for build of DPDK and l2fwd

Other Requirements
------------------
The test suite requires Python 3.3 and relies on a number of other
packages. These need to be installed for the test suite to function.

Installation of required packages, preparation of Python 3 virtual
environment and compilation of OVS, DPDK and QEMU is performed by
script **systems/build_base_machine.sh**. It should be executed under
user account, which will be used for vsperf execution.

**Please Note**: Password-less sudo access must be configured for given
user account before script is executed.

Execution of installation script:

.. code:: bash

    $ cd systems
    $ ./build_base_machine.sh

**Please Note**: you don't need to go into any of the systems subdirectories,
simply run the top level **build_base_machine.sh**, your OS will be detected
automatically.

Script **build_base_machine.sh** will install all the vsperf dependencies
in terms of system packages, Python 3.x and required Python modules.
In case of CentOS 7 it will install Python 3.3 from an additional repository
provided by Software Collections (`a link`_). In case of RedHat 7 it will
install Python 3.4 as an alternate installation in /usr/local/bin. Installation
script will also use `virtualenv`_ to create a vsperf virtual environment,
which is isolated from the default Python environment. This environment will
reside in a directory called **vsperfenv** in $HOME.

You will need to activate the virtual environment every time you start a
new shell session. Its activation is specific to your OS:

CentOS 7
========

.. code:: bash

    $ scl enable python33 bash
    $ cd $HOME/vsperfenv
    $ source bin/activate

Fedora, RedHat and Ubuntu
=========================

.. code:: bash

    $ cd $HOME/vsperfenv
    $ source bin/activate

Gotcha
^^^^^^
.. code:: bash

   $ source bin/activate
   Badly placed ()'s.

Check what type of shell you are using

.. code:: bash

   echo $shell
   /bin/tcsh

See what scripts are available in $HOME/vsperfenv/bin

.. code:: bash

   $ ls bin/
   activate          activate.csh      activate.fish     activate_this.py

source the appropriate script

.. code:: bash

   $ source bin/activate.csh

Working Behind a Proxy
======================

If you're behind a proxy, you'll likely want to configure this before
running any of the above. For example:

  .. code:: bash

    export http_proxy=proxy.mycompany.com:123
    export https_proxy=proxy.mycompany.com:123

.. _a link: http://www.softwarecollections.org/en/scls/rhscl/python33/
.. _virtualenv: https://virtualenv.readthedocs.org/en/latest/
.. _vloop-vnf-ubuntu-14.04_20160823: http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20160823.qcow2
.. _vloop-vnf-ubuntu-14.04_20160804: http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20160804.qcow2
.. _vloop-vnf-ubuntu-14.04_20160303: http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20160303.qcow2
.. _vloop-vnf-ubuntu-14.04_20151216: http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20151216.qcow2

Hugepage Configuration
----------------------

Systems running vsperf with either dpdk and/or tests with guests must configure
hugepage amounts to support running these configurations. It is recommended
to configure 1GB hugepages as the pagesize.

The amount of hugepages needed depends on your configuration files in vsperf.
Each guest image requires 4096 MB by default according to the default settings
in the ``04_vnf.conf`` file.

.. code:: bash

    GUEST_MEMORY = ['4096', '4096']

The dpdk startup parameters also require an amount of hugepages depending on
your configuration in the ``02_vswitch.conf`` file.

.. code:: bash

    VSWITCHD_DPDK_ARGS = ['-c', '0x4', '-n', '4', '--socket-mem 1024,1024']
    VSWITCHD_DPDK_CONFIG = {
        'dpdk-init' : 'true',
        'dpdk-lcore-mask' : '0x4',
        'dpdk-socket-mem' : '1024,1024',
    }

Note: Option VSWITCHD_DPDK_ARGS is used for vswitchd, which supports --dpdk
parameter. In recent vswitchd versions, option VSWITCHD_DPDK_CONFIG will be
used to configure vswitchd via ovs-vsctl calls.

With the --socket-mem argument set to use 1 hugepage on the specified sockets as
seen above, the configuration will need 10 hugepages total to run all tests
within vsperf if the pagesize is set correctly to 1GB.

VSPerf will verify hugepage amounts are free before executing test
environments. In case of hugepage amounts not being free, test initialization
will fail and testing will stop.

**Please Note**: In some instances on a test failure dpdk resources may not
release hugepages used in dpdk configuration. It is recommended to configure a
few extra hugepages to prevent a false detection by VSPerf that not enough free
hugepages are available to execute the test environment. Normally dpdk would use
previously allocated hugepages upon initialization.

Depending on your OS selection configuration of hugepages may vary. Please refer
to your OS documentation to set hugepages correctly. It is recommended to set
the required amount of hugepages to be allocated by default on reboots.

Information on hugepage requirements for dpdk can be found at
http://dpdk.org/doc/guides/linux_gsg/sys_reqs.html

You can review your hugepage amounts by executing the following command

.. code:: bash

    cat /proc/meminfo | grep Huge

If no hugepages are available vsperf will try to automatically allocate some.
Allocation is controlled by HUGEPAGE_RAM_ALLOCATION configuration parameter in
``02_vswitch.conf`` file. Default is 2GB, resulting in either 2 1GB hugepages
or 1024 2MB hugepages.
