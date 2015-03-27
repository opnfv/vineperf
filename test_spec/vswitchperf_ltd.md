#CHARACTERIZE VSWITCH PERFORMANCE FOR TELCO NFV USE CASES LEVEL TEST DESIGN

##Table of Contents

- [1. Introduction](#Introduction)
  - [1.1. Document identifier](#DocId)
  - [1.2. Scope](#Scope)
  - [1.3. References](#References)


- [2. Details of the Level Test Design](#DetailsOfTheLevelTestDesign)
  - [2.1. Features to be tested](#FeaturesToBeTested)
  - [2.2. Approach](#Approach)
  - [2.3. Test identification](#TestIdentification)
    - [2.3.1 Throughput tests](#ThroughputTests)
    - [2.3.2 Packet Delay Tests](#PacketDelayTests)
    - [2.3.3 Scalability Tests](#ScalabilityTests)
    - [2.3.4 CPU and Memory Consumption Tests](#CPUTests)
    - [2.3.5 Coupling Between the Control Path and The Datapath Tests](#CPDPTests)
    - [2.3.6 Time to Establish Flows Tests](#FlowLatencyTests)
    - [2.3.7 Noisy Neighbour Tests](#NoisyNeighbourTests)
    - [2.3.8 Overlay Tests](#OverlayTests)
    - [2.3.9 Summary Test List](#SummaryList)
  - [2.4. Feature pass/fail criteria](#PassFail)
  - [2.5. Test deliverables](#TestDeliverables)


- [3. General](#General)
  - [3.1. Glossary](#Glossary)
  - [3.2. Document change procedures and history](#History)
  - [3.3. Contributors](#Contributors)

<br/>

---
<a name="Introduction"></a>
##1. Introduction
  The objective of the OPNFV project titled **“Characterize vSwitch Performance for Telco NFV Use Cases”**, is to evaluate a virtual switch to identify its suitability for a Telco Network Function Virtualization (NFV) environment. The intention of this Level Test Design (LTD) document is to specify the set of tests to carry out in order to objectively measure the current characteristics of a virtual switch in the Network Function Virtualization Infrastructure (NFVI) as well as the test pass criteria. The detailed test cases will be defined in [Section 2](#DetailsOfTheLevelTestDesign), preceded by the [Document identifier](#DocId) and the [Scope](#Scope).

 This document is currently in draft form.

  <a name="DocId"></a>
  ###1.1. Document identifier
  The document id will be used to uniquely identify versions of the LTD. The format for the document id will be: OPNFV\_vswitchperf\_LTD\_ver\_NUM\_MONTH\_YEAR\_STATUS, where by the status is one of: draft, reviewed, corrected or final. The document id for this version of the LTD is: OPNFV\_vswitchperf\_LTD\_ver\_1.6\_Jan\_15\_DRAFT.

  <a name="Scope"></a>
  ###1.2. Scope
  The main purpose of this project is to specify a suite of performance tests in order to objectively measure the current packet transfer characteristics of a virtual switch in the NFVI. The intent of the project is to facilitate testing of any virtual switch. Thus, a generic suite of tests shall be developed, with no hard dependencies to a single implementation. In addition, the test case suite shall be architecture independent.

  The test cases developed in this project shall not form part of a separate test framework, all of these tests may be inserted into the Continuous Integration Test Framework and/or the Platform Functionality Test Framework - if a vSwitch becomes a standard component of an OPNFV release.

  <a name="References"></a>
  ###1.3. References

  - [RFC 1242 Benchmarking Terminology for Network Interconnection Devices](http://www.ietf.org/rfc/rfc1242.txt)
  - [RFC 2544 Benchmarking Methodology for Network Interconnect Devices](http://www.ietf.org/rfc/rfc2544.txt)
  - [RFC 2285 Benchmarking Terminology for LAN Switching Devices](http://www.ietf.org/rfc/rfc2285.txt)
  - [RFC 2889 Benchmarking Methodology for LAN Switching Devices](http://www.ietf.org/rfc/rfc2889.txt)
  - [RFC 3918 Methodology for IP Multicast Benchmarking](http://www.ietf.org/rfc/rfc3918.txt)
  - [RFC 4737 Packet Reordering Metrics](http://www.ietf.org/rfc/rfc4737.txt)
  - [RFC 5481 Packet Delay Variation Applicability Statement](http://www.ietf.org/rfc/rfc5481.txt)
  - [RFC 6201 Device Reset Characterization](http://tools.ietf.org/html/rfc6201)

<br/>

<a name=" DetailsOfTheLevelTestDesign"></a>
##2. Details of the Level Test Design
This section describes the features to be tested ([cf. 2.1](#FeaturesToBeTested)), the test approach ([cf. 2.2](#Approach)); it also identifies the sets of test cases or scenarios ([cf. 2.3](#TestIdentification)) along with the pass/fail criteria ([cf. 2.4](#PassFail)) and the test deliverables ([cf. 2.5](#TestDeliverables)).

<a name="FeaturesToBeTested"></a>
  ###2.1. Features to be tested
  Characterizing virtual switches (i.e. Device Under Test (DUT) in this document) includes measuring the following performance metrics:
   - Throughput as defined by [RFC1242]: The maximum rate at which none of the offered frames are dropped by the DUT. The maximum frame rate and bit rate that can be transmitted by the DUT without any error should be recorded. Note there is an equivalent bit rate and a specific layer at which the payloads contribute to the bits. Errors and improperly formed frames or packets are dropped.
   - Packet delay introduced by the DUT and its cumulative effect on E2E networks. Frame delay can be measured equivalently.
   - Packet delay variation: measured from the perspective of the VNF/application. Packet delay variation is sometimes called "jitter". However, we will avoid the term "jitter" as the term holds different meaning to different groups of people. In this document we will simply use the term packet delay variation. The preferred form for this metric is the PDV form of delay variation defined in [RFC5481].
   - Packet loss (within a configured waiting time at the receiver): All packets sent to the DUT should be accounted for.
   - Burst behaviour: measures the ability of the DUT to buffer packets.
   - Packet re-ordering: measures the ability of the device under test to maintain sending order throughout transfer to the destination.
   - Packet correctness Packets or Frames must be well-formed, in that they include all required fields, conform to length requirements, pass integrity checks, etc.
   - Availability and capacity of the DUT i.e. when the DUT is fully “up” and connected:
     - Includes power consumption of the CPU (in various power states) and system.
     - Includes CPU utilization.
     - Includes # NIC interfaces supported.
     - Includes headroom of VM workload processing cores (i.e. available for applications).

<a name="Approach"></a>
 ###2.2. Approach
 In order to determine the packet transfer characteristics of a virtual switch, the tests will be broken down into the following categories:

  - Throughput Tests to measure the maximum forwarding rate (in frames per second or fps) and bit rate (in Mbps) for a constant load (as defined by [RFC1242]) without traffic loss.
  - Packet and Frame Delay Tests to measure average, min and max packet and frame delay for constant loads.
  - Stream Performance Tests (TCP, UDP) to measure bulk data transfer performance, i.e. how fast systems can send and receive data through the switch.
  - Request/Response Performance Tests (TCP, UDP) the measure the transaction rate through the switch.
 - Packet delay tests to understand latency distribution for different packet sizes and over an extended test run to uncover outliers.
  - Scalability Tests to understand how the virtual switch performs as the number of flows, active ports, complexity of the forwarding logic's configuration... it has to deal with increases.
  - Control Path and Datapath Coupling Tests, to understand how closely coupled the datapath and the control path are as well as the effect of this coupling on the performance of the DUT.
  - CPU and Memory Consumption Tests to understand the virtual switch’s footprint on the system, this includes:
   - CPU utilization
   - Cache utilization
   - Memory footprint
  - Time To Establish Flows Tests.
  - Noisy Neighbour Tests, to understand the effects of resource sharing on the performance of a virtual switch.

**Note:** some of the tests above can be conducted simultaneously where the combined results would be insightful, for example Packet/Frame Delay and Scalability.

The following represents possible deployments which can help to determine the performance of both the virtual switch and the datapath into the VNF:

  - Physical port  → virtual switch → physical port.

<pre><code>
                                                         __
    +--------------------------------------------------+   |
    |              +--------------------+              |   |
    |              |                    |              |   |
    |              |                    v              |   |  Host
    |   +--------------+            +--------------+   |   |
    |   |   phy port   |  vSwitch   |   phy port   |   |   |
    +---+--------------+------------+--------------+---+ __|
               ^                           :
               |                           |
               :                           v
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+
</code></pre>

  - Physical port → virtual switch → VNF → virtual switch → physical port.

<pre><code>
                                                          __
    +---------------------------------------------------+   |
    |                                                   |   |
    |   +-------------------------------------------+   |   |
    |   |                 Application               |   |   |
    |   +-------------------------------------------+   |   |
    |       ^                                  :        |   |
    |       |                                  |        |   |  Guest
    |       :                                  v        |   |
    |   +---------------+           +---------------+   |   |
    |   | logical port 0|           | logical port 1|   |   |
    +---+---------------+-----------+---------------+---+ __|
            ^                                  :
            |                                  |
            :                                  v         __
    +---+---------------+----------+---------------+---+   |
    |   | logical port 0|          | logical port 1|   |   |
    |   +---------------+          +---------------+   |   |
    |       ^                                  :       |   |
    |       |                                  |       |   |  Host
    |       :                                  v       |   |
    |   +--------------+            +--------------+   |   |
    |   |   phy port   |  vSwitch   |   phy port   |   |   |
    +---+--------------+------------+--------------+---+ __|
               ^                           :
               |                           |
               :                           v
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+
</code></pre>

  - Physical port → virtual switch → VNF → virtual switch → VNF → virtual switch → physical port.

<pre><code>
                                                                                                                 __
    +---------------------------------------------------+   +---------------------------------------------------+  |
    |   Guest 1                                         |   |   Guest 2                                         |  |
    |   +-------------------------------------------+   |   |   +-------------------------------------------+   |  |
    |   |                 Application               |   |   |   |                 Application               |   |  |
    |   +-------------------------------------------+   |   |   +-------------------------------------------+   |  |
    |       ^                                  :        |   |       ^                                  :        |  |
    |       |                                  |        |   |       |                                  |        |  |  Guest
    |       :                                  v        |   |       :                                  v        |  |
    |   +---------------+           +---------------+   |   |   +---------------+           +---------------+   |  |
    |   | logical port 0|           | logical port 1|   |   |   | logical port 0|           | logical port 1|   |  |
    +---+---------------+-----------+---------------+---+   +---+---------------+-----------+---------------+---+__|
            ^                                  :                    ^                                  :
            |                                  |                    |                                  |
            :                                  v                    :                                  v         __
    +---+---------------+----------+---------------+------------+---------------+-----------+---------------+---+  |
    |   |     port 0    |          |     port 1    |            |     port 2    |           |     port 3    |   |  |
    |   +---------------+          +---------------+            +---------------+           +---------------+   |  |
    |       ^                                  :                    ^                                  :        |  |
    |       |                                  |                    |                                  |        |  |  Host
    |       :                                  +--------------------+                                  v        |  |
    |   +--------------+                                                                    +--------------+    |  |
    |   |   phy port   |                               vswitch                              |   phy port   |    |  |
    +---+--------------+--------------------------------------------------------------------+--------------+----+__|
               ^                                                                                    :
               |                                                                                    |
               :                                                                                    v
    +-----------------------------------------------------------------------------------------------------------+
    |                                                                                                           |
    |                                              traffic generator                                            |
    |                                                                                                           |
    +-----------------------------------------------------------------------------------------------------------+
</code></pre>

  - Physical port → virtual switch → VNF.

<pre><code>
                                                          __
    +---------------------------------------------------+   |
    |                                                   |   |
    |   +-------------------------------------------+   |   |
    |   |                 Application               |   |   |
    |   +-------------------------------------------+   |   |
    |       ^                                           |   |
    |       |                                           |   |  Guest
    |       :                                           |   |
    |   +---------------+                               |   |
    |   | logical port 0|                               |   |
    +---+---------------+-------------------------------+ __|
            ^
            |
            :                                            __
    +---+---------------+------------------------------+   |
    |   | logical port 0|                              |   |
    |   +---------------+                              |   |
    |       ^                                          |   |
    |       |                                          |   |  Host
    |       :                                          |   |
    |   +--------------+                               |   |
    |   |   phy port   |  vSwitch                      |   |
    +---+--------------+------------ -------------- ---+ __|
               ^
               |
               :
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+
</code></pre>

  - VNF → virtual switch → physical port.

<pre><code>
                                                          __
    +---------------------------------------------------+   |
    |                                                   |   |
    |   +-------------------------------------------+   |   |
    |   |                 Application               |   |   |
    |   +-------------------------------------------+   |   |
    |                                          :        |   |
    |                                          |        |   |  Guest
    |                                          v        |   |
    |                               +---------------+   |   |
    |                               | logical port  |   |   |
    +-------------------------------+---------------+---+ __|
                                               :
                                               |
                                               v         __
    +------------------------------+---------------+---+   |
    |                              | logical port  |   |   |
    |                              +---------------+   |   |
    |                                          :       |   |
    |                                          |       |   |  Host
    |                                          v       |   |
    |                               +--------------+   |   |
    |                     vSwitch   |   phy port   |   |   |
    +-------------------------------+--------------+---+ __|
                                           :
                                           |
                                           v
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+
</code></pre>

  - virtual switch → VNF → virtual switch.

<pre><code>
                                                                                                                 __
    +---------------------------------------------------+   +---------------------------------------------------+  |
    |   Guest 1                                         |   |   Guest 2                                         |  |
    |   +-------------------------------------------+   |   |   +-------------------------------------------+   |  |
    |   |                 Application               |   |   |   |                 Application               |   |  |
    |   +-------------------------------------------+   |   |   +-------------------------------------------+   |  |
    |                                          :        |   |       ^                                           |  |
    |                                          |        |   |       |                                           |  |  Guest
    |                                          v        |   |       :                                           |  |
    |                               +---------------+   |   |   +---------------+                               |  |
    |                               | logical port 0|   |   |   | logical port 0|                               |  |
    +-------------------------------+---------------+---+   +---+---------------+-------------------------------+__|
                                               :                    ^
                                               |                    |
                                               v                    :                                            __
    +------------------------------+---------------+------------+---------------+-------------------------------+  |
    |                              |     port 0    |            |     port 1    |                               |  |
    |                              +---------------+            +---------------+                               |  |
    |                                          :                    ^                                           |  |
    |                                          |                    |                                           |  |  Host
    |                                          +--------------------+                                           |  |
    |                                                                                                           |  |
    |                                                  vswitch                                                  |  |
    +-----------------------------------------------------------------------------------------------------------+__|
</code></pre>

**Note:** For tests where the traffic generator and/or measurement receiver are implemented on VM and connected to the virtual switch through vNIC, the issues of shared resources and interactions between the measurement devices and the device under test must be considered.

 ####General Methodology:

  To establish the baseline performance of the virtual switch, tests would initially be run with a simple workload in the VNF (the recommended simple workload VNF would be [DPDK]'s testpmd application forwarding packets in a VM). Subsequently, the tests would also be executed with a real Telco workload running in the VNF, which would exercise the virtual switch in the context of higher level Telco NFV use cases, and prove that its underlying characteristics and behaviour can be measured and validated. Suitable real Telco workload VNFs are yet to be identified.

 <a name="DefaultParams"></a>
 #####Default Test Parameters:
 The following list identifies the default parameters for suite of tests:

 - Reference application: Simple forwarding or Open Source VNF.
 - Frame size (bytes): 64, 128, 256, 512, 1024, 1280, 1518, 2K, 4k OR Packet size based on use-case (e.g. RTP 64B, 256B).
 - Reordering check: Tests should confirm that packets within a flow are not reordered.
 - Duplex: Unidirectional / Bidirectional. Default: Full duplex with traffic transmitting in both directions, as network traffic generally does not flow in a single direction. By default the data rate of transmitted traffic should be the same in both directions, please note that asymmetric traffic (e.g. downlink-heavy) tests will be mentioned explicitly for the relevant test cases.
 - Number of Flows: Default for non scalability tests is a single flow. For scalability tests the goal is to test with maximum supported flows but where possible will test up to 10 Million flows. Start with a single flow and scale up. By default flows should be added sequentially, tests that add flows simultaneously will explicitly call out their flow addition behaviour. Packets are generated across the flows uniformly with no burstiness.
 - Traffic Types: UDP, SCTP, RTP, GTP and UDP traffic.
 - Deployment scenarios are:
   - Physical → virtual switch → physical.
   - Physical → virtual switch → VNF → virtual switch → physical.
   - Physical → virtual switch → VNF → virtual switch → VNF → virtual switch → physical.
   - Physical → virtual switch → VNF.
   - VNF → virtual switch → Physical.
   - VNF → virtual switch → VNF.

 Tests MUST have these parameters unless otherwise stated. **Test cases with non default parameters will be stated explicitly**.

 **Note**: For throughput tests unless stated otherwise, test configurations should ensure that traffic traverses the installed flows through the switch, i.e. flows are installed and have an appropriate time out that doesn't expire before packet transmission starts.

 #####Test Priority
  Tests will be assigned a priority in order to determine which tests should be implemented immediately and which tests implementations can be deferred.

 Priority can be of following types:
  - Urgent: Must be implemented immediately.
  - High: Must be implemented in the next release.
  - Medium: May be implemented after the release.
  - Low: May or may not be implemented at all.

 #####DUT Setup
 The DUT should be configured to its "default" state. The DUT's configuration or set-up must not change between tests in any way other than what is required to do the test. All supported protocols must be configured and enabled for each test set up.

 #####Port Configuration
 The DUT should be configured with n ports where n is a multiple of 2. Half of the ports on the DUT should be used as ingress ports and the other half of the ports on the DUT should be used as egress ports. Where a DUT has more than 2 ports, the ingress data streams should be set-up so that they transmit packets to the egress ports in sequence so that there is an even distribution of traffic across ports. For example, if a DUT has 4 ports 0(ingress), 1(ingress), 2(egress) and 3(egress), the traffic stream directed at port 0 should output a packet to port 2 followed by a packet to port 3. The traffic stream directed at port 1 should also output a packet to port 2 followed by a packet to port 3.

 #####Frame formats
  Layer 2 (data link layer) protocols:

  -  Ethernet II

  <pre><code>

  +-----------------------------+-----------------------------------------------------------------------+---------+
  |       Ethernet Header       |                                Payload                                |Check Sum|
  +-----------------------------+-----------------------------------------------------------------------+---------+
   |___________________________| |_____________________________________________________________________| |_______|
              14 Bytes                                       46 - 1500 Bytes                              4 Bytes

  </code></pre>

  Layer 3 (network layer) protocols:

  - IPv4

  <pre><code>

  +-----------------------------+-------------------------------------+---------------------------------+---------+
  |       Ethernet Header       |              IP Header              |             Payload             |Check Sum|
  +-----------------------------+-------------------------------------+---------------------------------+---------+
   |___________________________| |___________________________________| |_______________________________| |_______|
              14 Bytes                         20 Bytes                         26 - 1480 Bytes           4 Bytes

  </code></pre>

  - IPv6

  <pre><code>

  +-----------------------------+-------------------------------------+---------------------------------+---------+
  |       Ethernet Header       |              IP Header              |             Payload             |Check Sum|
  +-----------------------------+-------------------------------------+---------------------------------+---------+
   |___________________________| |___________________________________| |_______________________________| |_______|
              14 Bytes                         40 Bytes                         26 - 1460 Bytes           4 Bytes

  </code></pre>

  Layer 4 (transport layer) protocols:
  - TCP
  - UDP
  - SCTP

  <pre><code>

  +-----------------------------+-------------------------------------+-----------------+---------------+---------+
  |       Ethernet Header       |              IP Header              | Layer 4 Header  |    Payload    |Check Sum|
  +-----------------------------+-------------------------------------+-----------------+---------------+---------+
   |___________________________| |___________________________________| |_______________| |_____________| |_______|
              14 Bytes                         20 Bytes                    20 Bytes       6 - 1460 Bytes  4 Bytes

  </code></pre>

  Layer 5 (application layer) protocols:

  - RTP
  - GTP

  <pre><code>

  +-----------------------------+-------------------------------------+-----------------+---------------+---------+
  |       Ethernet Header       |              IP Header              | Layer 4 Header  |    Payload    |Check Sum|
  +-----------------------------+-------------------------------------+-----------------+---------------+---------+
   |___________________________| |___________________________________| |_______________| |_____________| |_______|
              14 Bytes                         20 Bytes                    20 Bytes        Min 6 Bytes    4 Bytes

  </code></pre>

  #####Packet Throughput
  There is a difference between an Ethernet frame, an IP packet, and a UDP datagram. In the seven-layer OSI model of computer networking, packet refers to a data unit at layer 3 (network layer). The correct term for a data unit at layer 2 (data link layer) is a frame, and at layer 4 (transport layer) is a segment or datagram.

  Important concepts related to 10GbE performance are frame rate and throughput. The MAC bit rate of 10GbE, defined in the IEEE standard 802 .3ae, is 10 billion bits per second. Frame rate is based on the bit rate and frame format definitions. Throughput, defined in IETF RFC 1242, is the highest rate at which the system under test can forward the offered load, without loss.

  The frame rate for 10GbE is determined by a formula that divides the 10 billion bits per second by the preamble + frame length + inter-frame gap.

  The maximum frame rate is calculated using the minimum values of the following parameters, as described in the IEEE 802 .3ae standard:

  - Preamble: 8 bytes * 8 = 64 bits
  -  Frame Length: 64 bytes (minimum) * 8 = 512 bits
  -  Inter-frame Gap: 12 bytes (minimum) * 8 = 96 bits

  Therefore, Maximum Frame Rate (64B Frames)

  = MAC Transmit Bit Rate / (Preamble + Frame Length + Inter-frame Gap)

  = 10,000,000,000 / (64 + 512 + 96)

  = 10,000,000,000 / 672

  = 14,880,952.38 frame per second (fps)

  #####RFC 1242 Benchmarking Terminology for Network Interconnection Devices
  RFC 1242 defines the terminology that is used in describing performance benchmarking tests and their results. Definitions and discussions covered include: Back-to-back, bridge, bridge/router, constant load, data link frame size, frame loss rate, inter frame gap, latency, and many more.

  #####RFC 2544 Benchmarking Methodology for Network Interconnect Devices
  RFC 2544 outlines a benchmarking methodology for network Interconnect Devices. The methodology results in performance metrics such as latency, frame loss percentage, and maximum data throughput.

  In this document network “throughput” (measured in millions of frames per second) is based on RFC 2544, unless otherwise noted. Frame size refers to Ethernet frames ranging from smallest frames of 64 bytes to largest frames of 4K bytes.

  Types of tests are:
  1.	Throughput test defines the maximum number of frames per second that can be transmitted without any error.
  2.	Latency test measures the time required for a frame to travel from the originating device through the network to the destination device. Please note that note RFC2544 Latency measurement will be superseded with a measurement of average latency over all successfully transferred packets or frames.
  3.	Frame loss test measures the network’s response in overload conditions - a critical indicator of the network’s ability to support real-time applications in which a large amount of frame loss will rapidly degrade service quality.
  4.	Burst test assesses the buffering capability of a switch. It measures the maximum number of frames received at full line rate before a frame is lost. In carrier Ethernet networks, this measurement validates the excess information rate (EIR) as defined in many SLAs.
  5.	System recovery to characterize speed of recovery from an overload condition
  6.	Reset to characterize speed of recovery from device or software reset. This type of test has been updated by [RFC6201] as such, the methodology defined by this specification will be that of RFC 6201.

  Although not included in the defined RFC 2544 standard, another crucial measurement in Ethernet networking is packet delay variation. The definition set out by this specification comes from [RFC5481].

  #####RFC 2285 Benchmarking Terminology for LAN Switching Devices
  RFC 2285 defines the terminology that is used to describe the terminology for benchmarking a LAN switching device. It extends RFC 1242 and defines: DUTs, SUTs, Traffic orientation and distribution, bursts, loads, forwarding rates, etc.

  #####RFC 2889 Benchmarking Methodology for LAN Switching
  RFC 2889 outlines a benchmarking methodology for LAN switching, it extends RFC 2544. The outlined methodology gathers performance metrics for forwarding, congestion control, latency, address handling and finally filtering.

  #####RFC 3918 Methodology for IP Multicast Benchmarking
  RFC 3918 outlines a methodology for IP Multicast benchmarking.

  #####RFC 4737 Packet Reordering Metrics
  RFC 4737 describes metrics for identifying and counting re-ordered packets within a stream, and metrics to measure the extent each packet has been re-ordered.

  #####RFC 5481 Packet Delay Variation Applicability Statement
  RFC 5481 defined two common, but different forms of delay variation metrics, and compares the metrics over a range of networking circumstances and tasks. The most suitable form for vSwitch benchmarking is the "PDV" form.

  #####RFC 6201 Device Reset Characterization
  RFC 6201 extends the methodology for characterizing the speed of recovery of the DUT from device or software reset described in RFC 2544.


<a name="TestIdentification"></a>
###2.3. Test identification
  <a name="ThroughputTests"></a>
  ####2.3.1 Throughput tests
  The following tests aim to determine the maximum forwarding rate that can be achieved with a virtual switch.

  The following list is not exhaustive but should indicate the type of tests that should be required. It is expected that more will be added.

  - #####Test ID: LTD.Throughput.RFC2544.PacketLossRatio

  **Title**: RFC 2544 X% packet loss ratio Throughput and Latency Test

  **Prerequisite Test**: N/A

  **Priority**:

  **Description**:

  This test determines the DUT's maximum forwarding rate with X% traffic loss for a constant load (fixed length frames at a fixed interval time). The default loss percentages to be tested are:
    - X = 0%
    - X = 10^-7%

  Note: Other values can be tested if required by the user.

  The selected frame sizes are those previously defined under [Default Test Parameters](#DefaultParams). The test can also be used to determine the average latency of the traffic.

  Under the [RFC2544] test methodology, the test duration will include a number of trials; each trial should run for a minimum period of 60 seconds. A binary search methodology must be applied for each trial to obtain the final result.

  **Expected Result**:
  At the end of each trial, the presence or absence of loss determines the modification of offered load for the next trial, converging on a maximum rate, or [RFC2544] Throughput with X% loss. The Throughput load is re-used in related [RFC2544] tests and other tests.

  **Metrics Collected**:

  The following are the metrics collected for this test:

   - The maximum forwarding rate in Frames Per Second (FPS) and Mbps of the DUT for each frame size with X% packet loss.
   - The average latency of the traffic flow when passing through the DUT (if testing for latency, note that this average is different from the test specified in Section 26.3 of [RFC2544]).

<br/>
 - #####Test ID: LTD.Throughput.RFC2544.PacketLossRatioFrameModification
  **Title**: RFC 2544 X% packet loss Throughput and Latency Test with packet modification

  **Prerequisite Test**: N\A

  **Priority**:

  **Description**:

  This test determines the DUT's maximum forwarding rate with X% traffic loss for a constant load (fixed length frames at a fixed interval time). The default loss percentages to be tested are:
    - X = 0%
    - X = 10^-7%

  Note: Other values can be tested if required by the user.

  The selected frame sizes are those previously defined under [Default Test Parameters](#DefaultParams). The test can also be used to determine the average latency of the traffic.

  Under the [RFC2544] test methodology, the test duration will include a number of trials; each trial should run for a minimum period of 60 seconds. A binary search methodology must be applied for each trial to obtain the final result.

  During this test, the DUT must perform the following operations on the traffic flow:

   - Perform packet parsing on the DUT's ingress port.
   - Perform any relevant address look-ups on the DUT's ingress ports.
   - Modify the packet header before forwarding the packet to the DUT's egress port. Packet modifications include:
     - Modifying the Ethernet source or destination MAC address.
     - Modifying/adding a VLAN tag.
     - Modifying/adding a MPLS tag.
     - Modifying the source or destination ip address.
     - Modifying the TOS/DSCP field.
     - Modifying the source or destination ports for UDP/TCP/SCTP  (Recommended).
     - Modifying the TTL.

  **Expected Result**:
  The Packet parsing/modifications require some additional degree of processing resource, therefore the [RFC2544] Throughput is expected to be somewhat lower than the Throughput level measured without additional steps. The reduction is expected to be greatest on tests with the smallest packet sizes (greatest header processing rates).

  **Metrics Collected**:

  The following are the metrics collected for this test:

   - The maximum forwarding rate in Frames Per Second (FPS) and Mbps of the DUT for each frame size with X% packet loss and packet modification operations being performed by the DUT.
   - The average latency of the traffic flow when passing through the DUT (if testing for latency, note that this average is different from the test specified in Section 26.3 of [RFC2544]).
   - The [RFC5481] PDV form of delay variation on the traffic flow, using the 99th percentile.

<br/>
 - #####Test ID: LTD.Throughput.RFC2544.SystemRecoveryTime
  **Title**: RFC 2544 System Recovery Time Test

  **Prerequisite Test**: N\A

  **Priority**:

  **Description**:

  The aim of this test is to determine the length of time it takes the DUT to recover from an overload condition for a constant load (fixed length frames at a fixed interval time). The selected frame sizes are those previously defined under [Default Test Parameters](#DefaultParams), traffic should be sent to the DUT under normal conditions. During the duration of the test and while the traffic flows are passing though the DUT, at least one situation leading to an overload condition for the DUT should occur. The time from the start of the overload condition to when the DUT returns to normal operations should be measured to determine recovery time. Prior to overloading the DUT, one should record the average latency for 100 packets forwarded through the DUT.

  The suggested overload condition would be to transmit traffic at a very high frame rate to the DUT, for at least 60 seconds, then reduce the frame rate to the DUT by half; A number of time-stamps should be recorded: 
    - Record the time-stamp at which the frame rate was halved and record a second time-stamp at the time of the last frame lost. The recovery time is the difference between the two timestamps.
    - Record the average Latency for 100 frames after the last frame loss and continue to record average latency measurements for every 100 frames, when latency returns to pre-overload levels record the time-stamp.

  **Expected Result**:

  **Metrics collected**

  The following are the metrics collected for this test:

   - The length of time it takes the DUT to recover from an overload condition.
   - The length of time it takes the DUT to recover the average latency to pre-overload conditions.

  **Deployment scenario**:

   - Physical → virtual switch → physical.

<br/>
 - #####Test ID: LTD.Throughput.RFC2544.BackToBackFrames
  **Title**: RFC 2544 Back To Back Frames Test

  **Prerequisite Test**: N\A

  **Priority**:

  **Description**:

  The aim of this test is to characterize the ability of the DUT to process back-to-back frames. For each frame size previously defined under [Default Test Parameters](#DefaultParams), a burst of traffic is sent to the DUT with the minimum inter-frame gap between each frame. If the number of received frames equals the number of frames that were transmitted, the burst size should be increased and traffic is sent to the DUT again. The value measured is the back-to-back value, that is the maximum burst size the DUT can handle without any frame loss. 

  **Expected Result**:

  Tests of back-to-back frames with physical devices have produced unstable results in some cases. All tests should be repeated in multiple test sessions and results stability should be examined.

  **Metrics collected**

  The following are the metrics collected for this test:

   - The back-to-back value, which is the the number of frames in the longest burst that the DUT will handle without the loss of any frames.

  **Deployment scenario**:

   - Physical → virtual switch → physical.

<br/>
  - #####Test ID: LTD.Throughput.RFC2544.Soak
  **Title**: RFC 2544 X% packet loss Throughput Soak Test

  **Prerequisite Test** LTD.Throughput.RFC2544.PacketLossRatio

  **Priority**:

  **Description**:

  The aim of this test is to understand the Throughput stability over an extended test duration in order to uncover any outliers. To allow for an extended test duration, the test should ideally run for 24 hours or, if this is not possible, for at least 6 hour. For this test, each frame size must be sent at the highest Throughput with X% packet loss, as determined in the prerequisite test. The default loss percentages to be tested are:
    - X = 0%
    - X = 10^-7%

  Note: Other values can be tested if required by the user.

  **Expected Result**:

  **Metrics Collected**:

  The following are the metrics collected for this test:

   - Throughput stability of the DUT.
   - Any outliers in the Throughput stability.
   - Any unexpected variation in Throughput stability.

<br/>

  - #####Test ID: LTD.Throughput.RFC2544.SoakFrameModification
  **Title**: RFC 2544 X% packet loss Throughput Soak Test with Frame Modification

  **Prerequisite Test** LTD.Throughput.RFC2544.PacketLossRatioFrameModification

  **Priority**:

  **Description**:

  The aim of this test is to understand the Throughput stability over an extended test duration in order to uncover any outliers. To allow for an extended test duration, the test should ideally run for 24 hours or, if this is not possible, for at least 6 hour. For this test, each frame size must be sent at the highest Throughput with X% packet loss, as determined in the prerequisite test. The default loss percentages to be tested are:
    - X = 0%
    - X = 10^-7%

  Note: Other values can be tested if required by the user.

  During this test, the DUT must perform the following operations on the traffic flow:

   - Perform packet parsing on the DUT's ingress port.
   - Perform any relevant address look-ups on the DUT's ingress ports.
   - Modify the packet header before forwarding the packet to the DUT's egress port. Packet modifications include:
     - Modifying the Ethernet source or destination MAC address.
     - Modifying/adding a VLAN tag.
     - Modifying/adding a MPLS tag.
     - Modifying the source or destination ip address.
     - Modifying the TOS/DSCP field.
     - Modifying the source or destination ports for UDP/TCP/SCTP  (Recommended).
     - Modifying the TTL.

  **Expected Result**:

  **Metrics Collected**:

  The following are the metrics collected for this test:

   - Throughput stability of the DUT.
   - Any outliers in the Throughput stability.
   - Any unexpected variation in Throughput stability.

<br/>
[RFC1242]:(http://www.ietf.org/rfc/rfc1242.txt)
[RFC2544]:(http://www.ietf.org/rfc/rfc2544.txt)
[RFC5481]:(http://www.ietf.org/rfc/rfc5481.txt)
[RFC6201]:(http://www.ietf.org/rfc/rfc6201.txt)
[DPDK]:http://www.dpdk.org/
