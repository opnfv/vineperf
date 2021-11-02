.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) Anuket, Spirent, AT&T and others.

================================
Kubernetes Artifacts in ViNePerf
================================

Container Artifacts
-------------------

.. list-table:: Container Artifacts in ViNeperf
   :widths: 50 100
   :header-rows: 1

   * - Container
     - Dockerfile Path
   * - ViNePerf
     - tools/docker/vineperf
   * - CNI: Userspace CNI
     - tools/k8s/cluster-deployment/uscni
   * - Traffic Generator - Prox
     - tools/k8s/test-containers/trafficgen-pods/prox
   * - Traffic Generator - TRex
     - tools/k8s/test-containers/trafficgen-pods/trex
   * - Traffic Generator - pktgen
     - tools/k8s/test-containers/trafficgen-pods/pktgen
   * - DPDK-Forwarding
     - tools/k8s/test-containers/dpdk-forwarding-pods

Pod and Network Reference Definitions
-------------------------------------

.. list-table:: Pod and Network Definitions
   :widths: 50 100
   :header-rows: 1

   * - Pod-Definition: ViNePerf
     - tools/k8s/reference-definitions/pod-defs/vineperf
   * - Pod-Definition: OVSDPDK
     - tools/k8s/reference-definitions/pod-defs/ovsdpdk
   * - Pod-Definition: VPP
     - tools/k8s/reference-definitions/pod-defs/vpp
   * - Pod-Definition: SRIOV
     - tools/k8s/reference-definitions/pod-defs/sriov
   * - Traffic Generator - TRex
     - tools/k8s/reference-definitions/pod-defs/trex
   * - Traffic Generator - Prox
     - tools/k8s/reference-definitions/pod-defs/prox
   * - Network Attachment - OVSPDDK
     - tools/k8s/reference-definitions/network-attachments/ovsdpdk
   * - Network Attachment - VPP
     - tools/k8s/reference-definitions/network-attachments/vpp
   * - Network Attachment - SRIOV
     - tools/k8s/reference-definitions/network-attachments/sriov
