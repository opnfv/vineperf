.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T, Red Hat, Spirent, Ixia  and others.

.. OPNFV ViNePerf Documentation master file.

*************************************
ViNePerf Configuration and User Guide
*************************************

============
Introduction
============

ViNePerf is an OPNFV testing project.

ViNePerf provides an automated test-framework and comprehensive test suite based on Industry
Test Specifications for measuring NFVI data-plane performance. The data-path includes switching technologies with
physical and virtual network interfaces. The ViNePerf architecture is switch and traffic generator agnostic and test
cases can be easily customized. ViNePerf was designed to be independent of OpenStack therefore OPNFV installer scenarios
are not required. ViNePerf can source, configure and deploy the device-under-test using specified software versions and
network topology. ViNePerf is used as a development tool for optimizing switching technologies, qualification of packet
processing functions and for evaluation of data-path performance.

The Euphrates release adds new features and improvements that will help advance high performance packet processing
on Telco NFV platforms. This includes new test cases, flexibility in customizing test-cases, new results display
options, improved tool resiliency, additional traffic generator support and VPP support.

ViNePerf provides a framework where the entire NFV Industry can learn about NFVI data-plane performance and try-out
new techniques together. A new IETF benchmarking specification (RFC8204) is based on ViNePerf work contributed since
2015. ViNePerf is also contributing to development of ETSI NFV test specifications through the Test and Open Source
Working Group.

* Wiki: https://wiki.anuket.io/display/HOME/ViNePERF
* Repository: https://git.opnfv.org/vineperf
* Artifacts: https://artifacts.opnfv.org/vswitchperf.html
* Continuous Integration: https://build.opnfv.org/ci/view/vineperf/

==================================
ViNePerf Install and Configuration
==================================

.. toctree::
   :caption: ViNePerf Install, Upgrade, Traffic Generator Guide
   :maxdepth: 2
   :numbered:

   ./installation.rst
   ./upgrade.rst
   ./trafficgen.rst
   ./tools.rst

===================
ViNePerf Test Guide
===================

.. toctree::
   :caption: ViNePerf Test Execution
   :maxdepth: 2

   ../userguide/testusage.rst
   ../userguide/teststeps.rst
   ../userguide/integration.rst
   ../userguide/trafficcapture.rst
   ../userguide/yardstick.rst
   ../userguide/testlist.rst
