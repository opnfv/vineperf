# OPNFV - k8s cluster setup

This project aims to set up and programmatically deploy a Kubernetes cluster on CentOS 7 machines with the help of Kubeadm. It uses ansible and requires very little intervention.

## Getting Started
The following steps aim to describe the minimum required to successfully run this script.


### Prerequisites

Kubernetes and Ansible should be installed on the master node and docker and kubelet services should be running on the master and worker nodes.


### Setup
In order to configure the cluster an inventory file should be included. The inventory file (e.g.,`hosts`) has the following structure:

```
[master]
master ansible_host={enter-master-ip} ansible_connection=ssh ansible_ssh_user={insert-user}  ansible_ssh_pass={insert-password} ansible_ssh_common_args='-o StrictHostKeyChecking=no'

[workers]
worker ansible_host={enter-master-ip}  ansible_connection=ssh ansible_ssh_user={insert-user} ansible_ssh_pass={insert-password} ansible_ssh_common_args='-o StrictHostKeyChecking=no'

```
In this configuration file, connection details should be filled in. In case more nodes within the cluster are needed, add lines as necessary to the workers group within the `hosts` file.

Install the kubernetes.core module for ansible-playbook. This module is required as prerequisite to run the playbook.

```
ansible-galaxy collection install kubernetes.core
```


### Usage
In order to use the script, download or clone [this repository] (https://gerrit.opnfv.org/gerrit/vswitchperf) to the root of what will be the master node.

Navigate to its contents and execute the following command as regular user (this will prevent errors throughout configuration and deployment) on whichever machine you wish to use as the master node (this host will be the one running kubectl):

```
ansible-playbook k8sclustermanagement.yml -i hosts –tags “deploy”

```
You can verify the installation by running:
```
kubectl get nodes
```
And verifying the readiness of the nodes. More information may be obtained with `kubectl describe nodes` if needed.


To clear the cluster, execute the following command

```
ansible-playbook k8sclustermanagement.yml -i hosts_garr –tags “clear” 
```

To deploy only CNI plugins

```
ansible-playbook k8sclustermanagement.yml -i hosts_garr –tags “cni” 
```

To deploy Danm CNI

Build the Danm Binaries and onboard them to your cluster image repository

```
git clone github.com/nokia/danm
cd danm
./build_danm.sh
```

Deploy the Danm CNI with the `danm` tag.

```
ansible-playbook k8sclustermanagement.yml -i hosts_garr –tags “cni, danm” 
```

Specifying danm tag only deploys Danm and skips Multus.


### Debugging

In case a step goes wrong within the installation, ansible should display a message, however, there's also files to debug if the installation had something to do within k8s. In the case of the master node, we should be able to find a `log_init.txt` with necessary logs. On worker nodes, the relevant file is `node_joined.txt`.
