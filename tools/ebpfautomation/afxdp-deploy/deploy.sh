#!/bin/bash

# Copyright 2022 The Linux Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
