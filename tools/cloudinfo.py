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


"""
Get Cloud information and save it a file
"""

import os
import json
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from conf import settings

def save_kubernetes_info():
    """
    Save Kubernetes Cluster Info
    """
    config.load_kube_config(settings.getValue('K8S_CONFIG_FILEPATH'))
    with open(os.path.join(settings.getValue('RESULTS_PATH'),
                           'cloud_info.txt'), 'a+') as outf:
        api = client.CoreV1Api()
        try:
            node_info = api.list_node()
        except ApiException as err:
            raise Exception from err
        for ni_item in node_info.items:
            outf.write("\n ******************************************** \n")
            outf.write("\n System Information \n")
            sinfo = {'Architecture': ni_item.status.node_info.architecture,
                     'Container Runtime Version':ni_item.status.node_info.container_runtime_version,
                     'kernel version':ni_item.status.node_info.kernel_version,
                     'Kube Proxy Version':ni_item.status.node_info.kube_proxy_version,
                     'Kubelet Version':ni_item.status.node_info.kubelet_version,
                     'Operating System':ni_item.status.node_info.operating_system,
                     'OS Image':ni_item.status.node_info.os_image}
            json.dump(sinfo, outf, indent=4)
            outf.write("\n List of Addresses \n")
            addresses = []
            for addrs in ni_item.status.addresses:
                entry = {'address': addrs.address, 'type': addrs.type}
                addresses.append(entry)
                json.dump(entry, outf, indent=4)
            sinfo['List of Addresses'] = entry
            outf.write("\n Allocatable Resources \n")
            sinfo['Allocatable Resources'] = ni_item.status.allocatable
            json.dump(ni_item.status.allocatable, outf, indent=4)
            outf.write("\n Available Resources \n")
            sinfo['Available Resources'] = ni_item.status.capacity
            json.dump(ni_item.status.capacity, outf, indent=4)
        api = client.VersionApi()
        try:
            version_info = api.get_code()
        except ApiException as err:
            raise Exception from err
        outf.write("\n Version Information \n")
        vinfo = {'git_commit': version_info.git_commit, 'git_version': version_info.git_version,
                 'platform': version_info.platform, 'go_version': version_info.go_version}
        #json.dump(vinfo, outf, indent=4)
        result = {**sinfo, **vinfo}
        return result

def save_openstack_info():
    """
    Save Openstack Info
    """
    return None

def save_cloud_info():
    """
    Save Cloud Information
    """
    if settings.getValue('K8S'):
        return save_kubernetes_info()
    elif settings.getValue('OPENSTACK'):
        return save_openstack_info()
    else:
        print("Unsupported Cloud")
        return None
    return 0

if __name__ == "__main__":
    save_cloud_info()
