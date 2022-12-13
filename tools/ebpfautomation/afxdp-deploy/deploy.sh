#!/bin/bash

# This script should be run from a node that has access to K8S Cluster

ROOT_UID=0
SUDO=""

# check if root
if [ "$UID" -ne "$ROOT_UID" ]
then
    # installation must be run via sudo
    SUDO="sudo -E"
fi

# clone afxdp plugins repository
echo "Cloning afxdp-plugins-for-kubernetes repository..."
[ -d afxdp-plugins-for-kubernetes ] && rm -rf afxdp-plugins-for-kubernetes
git clone https://github.com/intel/afxdp-plugins-for-kubernetes &> /dev/null


# Copy daemonset.yml to the appropriate folder
cp daemonset.yml afxdp-plugins-for-kubernetes/deployments

# Build and deploy
cd afxdp-plugins-for-kubernetes && make deploy

# Deploy the network attachment definition
kubectl create -f afxdp-nad.yaml
