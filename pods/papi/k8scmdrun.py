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
Run commands inside the pod for post-deployment configuration
"""

import re
import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

def execute_command(api_instance, pod_info, exec_command):
    """
    Execute a command inside a specified pod
    exec_command = list of strings
    """
    name = pod_info['name']
    resp = None
    try:
        resp = api_instance.read_namespaced_pod(name=name,
                                                namespace='default')
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            exit(1)
    if not resp:
        print("Pod %s does not exist. Creating it..." % name)
        return -1

    # Calling exec and waiting for response
    resp = stream(api_instance.connect_get_namespaced_pod_exec,
                  name,
                  'default',
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False)
    print("Response: " + resp)
    return resp

def get_virtual_sockets(api_instance, podname, namespace):
    """
    Memif or VhostUser Sockets
    """
    socket_files = []
    pinfo = {'name': podname,
             'pod_ip':'',
             'namespace': namespace}
    cmd = ['cat', '/etc/podnetinfo/annotations']
    response = execute_command(api_instance, pinfo, cmd)
    # Remove unnecessary elements
    results = re.sub(r"(\\n|\"|\n|\\|\]|\{|\}|\[)", "", response).strip()
    # Remove unnecessary spaces
    results = re.sub(r"\s+","", results, flags=re.UNICODE)
    # Get the RHS values
    output = results.split('=')
    for out in output:
        if 'socketfile' in out:
            out2 = out.split(',')
            for rout in out2:
                if 'socketfile' in rout:
                    print(rout[11:])
                    socket_files.append(rout[11:])


def get_sriov_interfaces(api_instance, podname, namespace):
    """
    Get SRIOV PIDs.
    """
    pinfo = {'name': podname,
             'pod_ip':'',
             'namespace': namespace}
    cmd = ['cat', '/etc/podnetinfo/annotations']
    response = execute_command(api_instance, pinfo, cmd)
    # Remove unnecessary elements
    results = re.sub(r"(\\n|\"|\n|\\|\]|\{|\}|\[)", "", response).strip()
    # Remove unnecessary spaces
    results = re.sub(r"\s+","", results, flags=re.UNICODE)
    # Get the RHS values
    output = results.split('=')
    names = []
    ifs = []
    for out in output:
        if 'interface' in out:
            out2 = out.split(',')
            for rout in out2:
                if 'interface' in rout:
                    ifs.append(rout[10:])
                elif 'name' in rout:
                    names.append(rout[5:])
    res = {names[i]: ifs[i] for i in range(len(names))}

def start_fowarding_app(api_instance, podname, namespace, appname):
    """
    Start the Forwarding Application
    """
    pinfo = {'name': podname,
             'pod_ip':'',
             'namespace': namespace}
    cmd = [appname, '&']
    response = execute_command(api_instance, pinfo, cmd)
