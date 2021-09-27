import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import json
import yaml
from rich.console import Console
from rich.table import Table
import time
import re


console = Console()

def check_system_installations():
    try:
        subprocess.Popen(f"helm version",shell=True,stdout=subprocess.PIPE,).stdout.read()
        subprocess.Popen(f"kubectl version --client",shell=True,stdout=subprocess.PIPE,).stdout.read()
        subprocess.Popen(f"minikube version",shell=True,stdout=subprocess.PIPE,).stdout.read()

    except subprocess.CalledProcessError as e:
        print (e.output)


def parse_helm_chart(helm_path):
    values_file = os.path.join(helm_path,"Chart.yaml")
    with open(values_file, 'r') as f:
        doc = yaml.load(f)
    name_of_chart = doc['name']

    values_file = os.path.join(helm_path,"values.yaml")
    with open(values_file, 'r') as f:
        doc = yaml.load(f)
    n_pods = doc['replicas']
    return (name_of_chart, n_pods)


def service_details(name):
    print("\nDEPLOYEMENT DETAILS\n")

    pp = subprocess.Popen(f"kubectl get service -o json {name}", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = pp.stdout.read()
    string = output.decode().replace("'", '"')
    _json = eval(string)

    table = Table(show_header=True)

    table.add_column("NAME")
    table.add_column("Type")
    table.add_column("CLUSTER-IP")
    table.add_column("EXTERNAL-IP")
    table.add_column("PORT(S)")

    tt = f'{_json["spec"]["ports"][0]["port"]}:{_json["spec"]["ports"][0]["nodePort"]}/{_json["spec"]["ports"][0]["protocol"]}'

    table.add_row(
        f'{_json["metadata"]["name"]}',
        f'{_json["spec"]["type"]}',
        f'{_json["spec"]["clusterIP"]}',
        f'{_json["status"]["loadBalancer"]}',
        tt,
    )
    console.print(table)

def pod_details(replicas):
    
    print("\nPOD DETAILS\n")

    pp = subprocess.Popen(f"kubectl get pods -o json", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = pp.stdout.read()
    pod_string = output.decode().replace("'", '"')
    true = True
    null = None
    false = False
    pod_json = eval(pod_string)

    table = Table(show_header=True)

    table.add_column("POD NAME")
    table.add_column("NAMESPACE")
    table.add_column("HOST-IP")
    table.add_column("PHASE")
    table.add_column("POD-IP")
    table.add_column("POD-IPs")
    
    podname = pod_json["items"][0]["metadata"]["name"]

    #print(replicas) 
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

    pp = subprocess.Popen(f"kubectl exec -i {podname} -c nginx -- ip -o a", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = pp.stdout.read()
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

    check_system_installations()
    helm_location = input("Enter the location of helm chart:  ")
    name,replicas = parse_helm_chart(helm_location)
    
    subprocess.Popen(f"helm install {name} {helm_location}",shell=True,stdout=subprocess.PIPE,).communicate()

    time.sleep(10)

    # status of helm charts

    print("\nStatus of helm charts\n")
    subprocess.run("helm list", shell =True)
    print("--" * 50)
    
    #pod details
    pod_details(replicas)
    
    #deployment details
    service_details(name)


if __name__ == "__main__":
    main()