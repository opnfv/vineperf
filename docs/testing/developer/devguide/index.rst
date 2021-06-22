.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T, Red Hat, Spirent, Ixia  and others.

.. OPNFV ViNePerf Documentation master file.

******************************
OPNFV ViNePerf Developer Guide
******************************

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

=============
Design Guides
=============

.. toctree::
   :caption: Traffic Gen Integration, ViNePerf Design, Test Design, Test Plan
   :maxdepth: 2

   ./design/trafficgen_integration_guide.rst
   ./design/vswitchperf_design.rst

   ./requirements/vswitchperf_ltd.rst
   ./requirements/vswitchperf_ltp.rst

=============
IETF RFC 8204
=============

.. toctree::
   :caption: ViNePerf contributions to Industry Specifications
   :maxdepth: 2
   :numbered:

The IETF Benchmarking Methodology Working Group (BMWG) was re-chartered in 2014 to include benchmarking for
Virtualized Network Functions (VNFs) and their infrastructure. A version of the ViNePerf test specification was
summarized in an Internet Draft ... `Benchmarking Virtual Switches in OPNFV <https://tools.ietf.org/html/draft-ietf-bmwg-vswitch-opnfv-01>`_ and contributed to the BMWG. In June 2017 the Internet Engineering Steering Group of the IETF
approved the most recent version of the draft for publication as a new test specification (RFC 8204).

======================
ViNePerf CI Test Cases
======================

.. toctree::
   :caption: ViNePerf Scenarios & Results
   :maxdepth: 2
   :numbered:

CI Test cases run daily on the ViNePerf Pharos POD for master and stable branches.
