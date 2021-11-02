.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) Anuket, Spirent, AT&T, Ixia  and others.

.. Anuket ViNePerf Documentation master file.

============================================================
Anuket ViNePerf Kubernetes Container Networking Benchmarking
============================================================
ViNePerf supports testing and benchmarking of kubernetes container networking solution, referred as kubernetes Container Networking Benchmarking (CNB). The process can be broadly classified into following four operations.

1. Setting up of Kubernetes Cluster.
2. Deploying container networking solution.
3. Deploying pod(s).
4. Running tests.

First step is achieved through the tool present in *tools/k8s/cluster-deployment* folder. Please refer to the documentation present in that folder for automated kubernetes cluster setup.

User can choose to perform all the remaining steps (2, 3, and 4), by running the following command.

.. code-block:: console

    vsperf --k8s --conf-file k8s.conf pcp_tput

User can also chose to perform only steps 3 and 4, by choosing to run following test cases.

.. code-block:: console

    vsperf --k8s --conf-file k8s.conf pcp_evs_tput
    or
    vsperf --k8s --conf-file k8s.conf pccp_evs_tput


************************
Important Configurations
************************

VSPERF has introduced a new configuration parameters, as listed below, for kubernetes CNB. The file *12_k8s.conf*, present in conf folder provides sample values. User has to modify these parameters to suit their environment before running the above command.

1. K8S_CONFIG_FILEPATH - location of the kubernetes-cluster access file. This will be used to connect to the cluster.
2. PLUGIN - The plugin to use. Allowed values are OvsDPDK, VPP, and SRIOV.
3. NETWORK_ATTACHMENT_FILEPATH - location of the network attachment definition file.
4. CONFIGMAP_FILEPATH - location of the config-map file. This will be used only for SRIOV plugin.
5. POD_MANIFEST_FILEPATH - location of the POD definition file.
6. APP_NAME - Application to run in the pod. Options - l2fwd, testpmd, and l3fwd.


*********
Testcases
*********
Kubernetes CNB will be done through new testcases. For Jerma release, only pcp_tput will be supported. This testcase, will be similar to pvp_tput, where VNF is replaced with a pod/container. The pcp_tput testcase, will still use phy2phy as deployment.
In Kali release, two testscases were added:

1. pcp_evs_tput: Single-Pod throughput test, where virtual switch is externally deployed and managed.
2. pccp_evs_tput: Two-Pod throughput test, where virtual switch is externally deployed and managed.

In future releases, more testcases for kubernetes will be added.


.. toctree::
   :numbered:
   :maxdepth: 2

   helm.rst
   artifacts.rst

Build date: |today|
