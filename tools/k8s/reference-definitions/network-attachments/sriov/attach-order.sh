kubectl create -f netAttach-sriov-dpdk-a.yaml
kubectl create -f netAttach-sriov-dpdk-b.yaml
kubectl create -f configMap.yaml
kubectl create -f sriovdp-daemonset.yaml
