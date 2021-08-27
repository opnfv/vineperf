# Copyright 2021 University Of Delhi, Spirent Communications
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
Automation of Pod Deployment with Kubernetes Python API
"""

# import os
import logging
import json
import time
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from conf import settings as S
from pods.pod.pod import IPod

class Papi(IPod):
    """
    Class for controlling the pod through PAPI
    """

    def __init__(self):
        """
        Initialisation function.
        """
        #super(Papi, self).__init__()
        super().__init__()

        self._logger = logging.getLogger(__name__)
        self._sriov_config = None
        self._sriov_config_ns = None

    def create(self):
        """
        Creation Process
        """
        print("Entering Create Function")
        config.load_kube_config(S.getValue('K8S_CONFIG_FILEPATH'))
        # create vswitchperf namespace
        api = client.CoreV1Api()
        namespace = 'default'
        pod_manifests = S.getValue('POD_MANIFEST_FILEPATH')
        pod_count = int(S.getValue('POD_COUNT'))
        if S.hasValue('POD_NAMESPACE'):
            namespace = S.getValue('POD_NAMESPACE')
        else:
            namespace = 'default'
        dep_pod_list = []

        # sriov configmap
        if S.getValue('PLUGIN') == 'sriov':
            configmap = load_manifest(S.getValue('CONFIGMAP_FILEPATH'))
            self._sriov_config = configmap['metadata']['name']
            self._sriov_config_ns = configmap['metadata']['namespace']
            api.create_namespaced_config_map(self._sriov_config_ns, configmap)


        # create nad(network attachent definitions)
        group = 'k8s.cni.cncf.io'
        version = 'v1'
        kind_plural = 'network-attachment-definitions'
        api = client.CustomObjectsApi() 
        assert pod_count <= len(pod_manifests)

        for nad_filepath in S.getValue('NETWORK_ATTACHMENT_FILEPATH'):
            nad_manifest = load_manifest(nad_filepath)

            try:
                response = api.create_namespaced_custom_object(group, version, namespace,
                                                               kind_plural, nad_manifest)
                self._logger.info(str(response))
                self._logger.info("Created Network Attachment Definition: %s", nad_filepath)
            except ApiException as err:
                raise Exception from err

        #create pod workloads
        api = client.CoreV1Api()
        for count in range(pod_count):
            dep_pod_info = {}
            pod_manifest = load_manifest(pod_manifests[count])
            dep_pod_info['name'] = pod_manifest["metadata"]["name"]
            try:
                response = api.create_namespaced_pod(namespace, pod_manifest)
                self._logger.info(str(response))
                self._logger.info("Created POD %d ...", self._number)
            except ApiException as err:
                raise Exception from err

            # Wait for the pod to start
            time.sleep(5)
            status = "Unknown"
            count = 0
            while True:
                if count == 10:
                    break
                try:
                    response = api.read_namespaced_pod_status(dep_pod_info['name'],
                            namespace)
                    status = response.status.phase
                except ApiException as err:
                    raise Exception from err
                if (status == "Running"
                        or status == "Failed"
                        or status == "Unknown"):
                    break
                else:
                    time.sleep(5)
                    count = count + 1
            # Now Get the Pod-IP
            try:
                response = api.read_namespaced_pod_status(dep_pod_info['name'],
                        namespace)
                dep_pod_info['pod_ip'] = response.status.pod_ip
            except ApiException as err:
                raise Exception from err
            dep_pod_info['namespace'] = namespace
            dep_pod_list.append(dep_pod_info)
            cmd = ['cat', '/etc/podnetinfo/annotations']
            execute_command(api, dep_pod_info, cmd)
        
        S.setValue('POD_LIST',dep_pod_list)
        return dep_pod_list

    def terminate(self):
        """
        Cleanup Process
        """
        #self._logger.info(self._log_prefix + "Cleaning vswitchperf namespace")
        self._logger.info("Terminating Pod")
        api = client.CoreV1Api()
        # api.delete_namespace(name="vswitchperf", body=client.V1DeleteOptions())

        if S.getValue('PLUGIN') == 'sriov':
            api.delete_namespaced_config_map(self._sriov_config, self._sriov_config_ns)


def load_manifest(filepath):
    """
    Reads k8s manifest files and returns as string

    :param str filepath: filename of k8s manifest file to read

    :return: k8s resource definition as string
    """
    with open(filepath) as handle:
        data = handle.read()

    try:
        manifest = json.loads(data)
    except ValueError:
        try:
            manifest = yaml.safe_load(data)
        except yaml.parser.ParserError as err:
            raise Exception from err

    return manifest

def replace_namespace(api, namespace):
    """
    Creates namespace if does not exists
    """
    namespaces = api.list_namespace()
    for nsi in namespaces.items:
        if namespace == nsi.metadata.name:
            api.delete_namespace(name=namespace,
                                 body=client.V1DeleteOptions())
            break

        time.sleep(0.5)
        api.create_namespace(client.V1Namespace(
            metadata=client.V1ObjectMeta(name=namespace)))
