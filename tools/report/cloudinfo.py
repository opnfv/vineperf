# Copyright 2021 Spirent Communications.
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
from tools.os_deploy_tgen.utilities import utils
from tools.os_deploy_tgen.osclients import openstack

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
            for addrs in ni_item.status.addresses:
                entry = {'address': addrs.address, 'type': addrs.type}
                json.dump(entry, outf, indent=4)
            outf.write("\n Allocatable Resources \n")
            json.dump(ni_item.status.allocatable, outf, indent=4)
            outf.write("\n Available Resources \n")
            json.dump(ni_item.status.capacity, outf, indent=4)
        api = client.VersionApi()
        try:
            version_info = api.get_code()
        except ApiException as err:
            raise Exception from err
        outf.write("\n Version Information \n")
        vinfo = {'git_commit': version_info.git_commit, 'git_version': version_info.git_version,
                 'platform': version_info.platform, 'go_version': version_info.go_version}
        json.dump(vinfo, outf, indent=4)

def save_openstack_info():
    """
    Save Openstack Info
    """
    osclient = openstack.OpenStackClient(utils.pack_openstack_params())
    hypervisors = osclient.conn.list_hypervisors()
    with open(os.path.join(settings.getValue('RESULTS_PATH'),
                           'cloud_info.txt'), 'a+') as outf:
        for hypervisor in hypervisors:
            outf.write("\n ***************************************** \n")
            outf.write(f"Hypervisor status:      {hypervisor.status} \n")
            outf.write(f"Hypervisor type:        {hypervisor.hypervisor_type} \n")
            outf.write(f"Hypervisor CPU-Arch:    {hypervisor.cpu_info['arch']} \n")
            outf.write(f"Hypervisor CPU-model:    {hypervisor.cpu_info['model']} \n")
            outf.write(f"Hypervisor CPU-vendor:    {hypervisor.cpu_info['vendor']} \n")
            outf.write(f"Hypervisor CPU-topology:    {hypervisor.cpu_info['topology']} \n")
            outf.write(f"Hypervisor id:          {hypervisor.id} \n")
            outf.write(f"Hypervisor state:       {hypervisor.state} \n")
            outf.write(f"Hypervisor host IP:     {hypervisor.host_ip} \n")
            outf.write(f"Hypervisor running VMs: {hypervisor.running_vms} \n")
            outf.write(f"Hyperviror hostname: {hypervisor.name} \n")
        outf.write("\n ***************************************** \n")
        version_data = osclient.keystone_session.get_all_version_data()
        json.dump(version_data, outf, indent=2)

def save_cloud_info():
    """
    Save Cloud Information
    """
    if settings.getValue('K8S'):
        save_kubernetes_info()
    elif settings.getValue('OPENSTACK'):
        save_openstack_info()
    else:
        print("Unsupported Cloud")
        return -1
    return 0
