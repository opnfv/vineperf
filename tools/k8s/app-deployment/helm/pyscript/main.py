# Copyright 2015-2017 Intel Corporation.
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

'''
This script automatically develop helm charts and returns
useful informations
'''

import os
import subprocess
from subprocess import PIPE, STDOUT
import time
import re
from ast import literal_eval
import yaml
from rich.console import Console
from rich.table import Table

console = Console()

def check_system_installations():
    ''' Check system installations necessary for successful run of this script '''
    try:
        subprocess.run("helm version",shell=True,check=True)
        subprocess.run("kubectl version --client",shell=True,
        check= True)
        subprocess.run("minikube version",shell=True,check=True)

    except subprocess.CalledProcessError as error:
        print (error.output)


def parse_helm_chart(helm_path):
    ''' Extract name of the chart '''
    values_file = os.path.join(helm_path,"Chart.yaml")
    with open(values_file, 'r', encoding='utf-8') as file:
        doc = yaml.load(file)
    name_of_chart = doc['name']

    values_file = os.path.join(helm_path,"values.yaml")
    with open(values_file, 'r',encoding='utf-8') as file:
        doc = yaml.load(file)
    n_pods = doc['replicas']
    return (name_of_chart, n_pods)


def service_details(name):
    ''' Extract Service Details'''
    print("\nDEPLOYEMENT DETAILS\n")

    with subprocess.Popen(f"kubectl get service -o json {name}",shell=True,
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT) as process:
        output = process.stdout.read()
        string = output.decode().replace("'", '"')
        _j = literal_eval(string)

    table = Table(show_header=True)

    table.add_column("NAME")
    table.add_column("Type")
    table.add_column("CLUSTER-IP")
    table.add_column("EXTERNAL-IP")
    table.add_column("PORT(S)")

    col=f'{_j["spec"]["ports"][0]["port"]}:{_j["spec"]["ports"][0]["nodePort"]}/{_j["spec"]["ports"][0]["protocol"]}'

    table.add_row(
        f'{_j["metadata"]["name"]}',
        f'{_j["spec"]["type"]}',
        f'{_j["spec"]["clusterIP"]}',
        f'{_j["status"]["loadBalancer"]}',
        col,
    )
    console.print(table)


def pod_details(replicas):
    ''' Extract Pod Details'''
    print("\nPOD DETAILS\n")
    with subprocess.Popen("kubectl get pods -o json", shell=True,
                                stdin=PIPE, stdout=PIPE, stderr=STDOUT) as process:
        output = process.stdout.read()
        pod_string = output.decode().replace("'", '"')
        # true = True
        # null = None
        # false = False
        pod_json = literal_eval(pod_string)

    table = Table(show_header=True)

    table.add_column("POD NAME")
    table.add_column("NAMESPACE")
    table.add_column("HOST-IP")
    table.add_column("PHASE")
    table.add_column("POD-IP")
    table.add_column("POD-IPs")
    podname = pod_json["items"][0]["metadata"]["name"]

    for i in range(replicas):
        table.add_row(
            f'{pod_json["items"][i]["metadata"]["name"]}',
            f'{pod_json["items"][i]["metadata"]["namespace"]}',
            f'{pod_json["items"][i]["status"]["hostIP"]}',
            f'{pod_json["items"][i]["status"]["phase"]}',
            f'{pod_json["items"][i]["status"]["podIP"]}',
            f'{pod_json["items"][i]["status"]["podIPs"]}',
        )
    console.print(table)

    ip_interface(podname)


def ip_interface(podname):
    ''' Extract Network IP'''
    with subprocess.Popen(f"kubectl exec -i {podname} -c nginx -- ip -o a", shell=True,
                                stdin=PIPE, stdout=PIPE, stderr=STDOUT) as process:
        output = process.stdout.read()
        _string = output.decode().replace("'", '"')
        ipregex = r"((?:[0-9]{1,3}[.]){3}[0-9]{1,3}/[0-9]{1,2})"
        ipregex2 = r"((?:[0-9]{1,3}[.]){3}[0-9]{1,3})"
        list1=re.findall(ipregex, _string)
        list2=re.findall(ipregex2 ,_string)
        ip_list = list1 + list2
        ip_string = ', '.join(ip_list)

    table = Table(show_header=True)

    table.add_column("POD NAME")
    table.add_column("INTERFACE IPs")

    table.add_row(
        podname,
        ip_string,
    )
    console.print(table)


def main():
    ''' Main Function '''
    check_system_installations()

    helm_location = input("Enter the location of helm chart:  ")
    name,replicas = parse_helm_chart(helm_location)

    subprocess.run(f"helm install {name} {helm_location}",shell=True,
                        check = True).stdout.read()
    time.sleep(10)

    # status of helm charts
    print("\nStatus of helm charts\n")
    subprocess.Popen("helm list", shell =True,stdout=subprocess.PIPE,).communicate()
    print("--" * 50)

    #pod details
    pod_details(replicas)

    #deployment details
    service_details(name)

if __name__ == "__main__":
    main()
