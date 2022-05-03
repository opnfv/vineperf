# ETSI GS NFV-TST 009 Testing with PROX and VPP in a Kubernetes Cluster

This document show an example of testing the dataplane in the third topology represented in the [topologies description](Topologies.md) with two pods equipped with two interfaces each that are bounded to VPP, using PROX as traffic generator. The `userspace-rapid-pod-t3-p1.yaml` and the `userspace-rapid-pod-t3-p2.yaml` files can be created by modifying the [Rapid pod definition file](./Configuration/Kubernetes/Rapid-pod/userspace-rapid-pod-2-interfaces-VPP.yaml).

### Prepare VPP and deploy the kubernetes components

- On Node 1:
  - Start `vpp.service` with `startup.conf` file under `/etc/vpp`
- On Node 2:
  - Deploy network attachment `userspace-vpp-netAttach-memif.yaml`
  - Deploy pods applying `userspace-rapid-pod-t3-p1.yaml` and `userspace-rapid-pod-t3-p2.yaml`

### Configure PROX inside the pods

- Generator Pod:

  - Enter the generator pod with `kubectl exec -it userspace-rapid-pod-t3-p1 -- /bin/bash`

  - copy the prox folder (it is shared between pods) to make changes on configuration files: `cp -r /opt/prox /opt/proxgen`

  - search for the two memif socketfile names running :  

    ```
    [root@userspace-rapid-pod-t3-p1 /]# cat /etc/podnetinfo/annotations | grep socketfile
    userspace/configuration-data="[{\n    \"containerId\": \"d3810ce7d4dee8f4cbcbfb7f3a53b86fd33481db282446b07dcb1bf4f1d7fa49\",\n    \
    
    "ifName\": \"net1\",\n    \"name\": \"userspace-vpp-net\",\n    \"config\": {\n        \"engine\": \"vpp\",\n        \"iftype\": \"
    
    memif\",\n        \"netType\": \"interface\",\n        \"memif\": {\n            \"role\": \"slave\",\n            \"mode\": \"ethe
    
    rnet\",\n            \"**socketfile**\": \"memif-d3810ce7d4de-net1.sock\"\n        },\n        \"vhost\": {},\n        \"bridge\": {}\n
    
    ​    },\n    \"ipResult\": {\n        \"interfaces\": [\n            {\n                \"name\": \"net1\",\n                \"sandb
    
    ox\": \"/proc/17603/ns/net\"\n            }\n        ],\n        \"dns\": {}\n    }\n},{\n    \"containerId\": \"d3810ce7d4dee8f4cb
    
    cbfb7f3a53b86fd33481db282446b07dcb1bf4f1d7fa49\",\n    \"ifName\": \"net2\",\n    \"name\": \"userspace-vpp-net\",\n    \"config\":
    
     {\n        \"engine\": \"vpp\",\n        \"iftype\": \"memif\",\n        \"netType\": \"interface\",\n        \"memif\": {\n      
    
    ​      \"role\": \"slave\",\n            \"mode\": \"ethernet\",\n            \"**socketfile**\": \"memif-d3810ce7d4de-net2.sock\"\n    
    
    ​    },\n        \"vhost\": {},\n        \"bridge\": {}\n    },\n    \"ipResult\": {\n        \"interfaces\": [\n            {\n    
    
    ​            \"name\": \"net2\",\n                \"sandbox\": \"/proc/17603/ns/net\"\n            }\n        ],\n        \"dns\": {
    
    }\n    }\n}]"
    ```

    

  - copy the names `memif-*-net1.sock` and `memif-*-net2.sock`

  - edit the `parameters.lua` changing the socketfile name and set the CPUs number for the main core, generator cores and latency cores: 

    ```lua
    ...
    eal="--socket-mem=256,0 --vdev=net_memif0,socket=/usrspcni/memif-d3810ce7d4de-net1.sock --vdev=net_memif1,socket=/usrspcni/memif-d3810ce7d4de-net2.sock"
    mcore="14"
    ...
    gencores="15"
    latcores="16"
    ...
    
    ```

  - edit `prox.cfg` to configure the tasks properly for generating and receiving packets:

    ```
    [lua]
    dofile("parameters.lua")
    
    [eal options] 
    -n=4 ; force number of memory channels
    no-output=no ; disable DPDK debug output 
    eal=--proc-type auto ${eal}
    
    [port 0]
    name=p0
    rx desc=2048
    tx desc=2048
    vlan=yes
    lsc=no                                                                         
    
    [port 1]
    name=p1
    rx desc=2048
    tx desc=2048
    vlan=yes
    lsc=no 
    
    [variables]
    $mbs=8                                                                         
    
    [defaults]
    mempool size=8K
                                            
    [global]
    name=${name}
    heartbeat timeout=${heartbeat}
    
    [core $mcore]
    mode=master
    
    [core $gencores]
    name=p0
    task=0
    mode=gen
    tx port=p0
    bps=1250000000
    pkt inline=${dest_hex_mac1} 00 00 00 00 00 00 08 00 45 00 00 2e 00 01 00 00 40 11 f7 7d ${local_hex_ip1} ${local_hex_ip2} 0b b8 0b b9 00 1a 55 7b
    pkt size=60
    min bulk size=$mbs
    max bulk size=16
    drop=yes
    lat pos=42
    accuracy pos=46
    packet id pos=50
    signature=0x98765432
    signature pos=56
    
    [core $latcores]
    name=lat
    task=0
    mode=lat
    rx port=p1
    lat pos=42
    accuracy pos=46
    packet id pos=50
    signature=0x98765432
    signature pos=56
    accuracy limit nsec=1000000
    latency bucket size=${bucket_size_exp}
    ```

  - Enter rapid folder and start PROX:

    ```
    [root@userspace-rapid-pod-t3-p1 /]# cd /opt/rapid/
    [root@userspace-rapid-pod-t3-p1 rapid]# ./prox -f ../proxgen/prox.cfg -et
    ```

    ```
    Usage: ./prox [-f CONFIG_FILE] [-a|-e] [-m|-s|-i] [-w DEF] [-u] [-t]
            -f CONFIG_FILE : configuration file to load, ./prox.cfg by default
            -e : don't autostart
            -t : Listen on TCP port 8474
    ```

    ![prox-vpp-screen](./images/prox-vpp-screen.png)

- Swap Pod:

  - Enter the generator pod with `kubectl exec -it userspace-rapid-pod-t3-p2 -- /bin/bash`
  - copy the prox folder (it is shared between pods) to make changes on configuration files: `cp -r /opt/prox /opt/proxswap`
  - search for the two memif socketfile names like for the Generator Pod and copy the names `memif-*-net1.sock` and `memif-*-net2.sock`

  - edit the `parameters.lua` changing the socketfile name and set the CPUs number for the main core (same as Generator Pod) and the swap cores: 

    ```lua
    ...
    swapone="17"
    ...
    
    ```

  - edit `prox.cfg` to configure the tasks properly for swapping:

    ```
    [lua]
    dofile("parameters.lua")                                                       
    
    [eal options] 
    -n=4 ; force number of memory channels
    no-output=no ; disable DPDK debug output 
    eal=--proc-type auto ${eal}
    
    [port 0]
    name=p0
    rx desc=2048
    tx desc=2048
    vlan=yes
    lsc=no                                                                         
    
    [port 1]
    name=p1
    rx desc=2048
    tx desc=2048
    vlan=yes
    lsc=no
    
    [variables]
    $mbs=8                                                                         
    
    [defaults]
    mempool size=8K
    
    [global]
    name=${name}
    heartbeat timeout=${heartbeat}
    
    [core $mcore]
    mode=master
    
    [core $swapone]
    name=swap1
    task=0
    mode=swap
    rx port=p0
    tx port=p1
    drop=no
    ```

    - Enter rapid folder and start PROX:

      ```
      [root@userspace-rapid-pod-t3-p2 /]# cd /opt/rapid/
      [root@userspace-rapid-pod-t3-p2 rapid]# ./prox -f ../proxgen/prox.cfg
      ```

      ![prox-vpp-screen-swap](./images/prox-vpp-screen-swap.png)

### Configure VPP

On Node 1 VPP should be configured to send the traffic between memif interfaces with `l2patch`:

```
[opnfv@worker ~]$ sudo vppctl
    _______    _        _   _____  ___ 
 __/ __/ _ \  (_)__    | | / / _ \/ _ \
 _/ _// // / / / _ \   | |/ / ___/ ___/
 /_/ /____(_)_/\___/   |___/_/  /_/    

vpp# show interface 
              Name               Idx    State  MTU (L3/IP4/IP6/MPLS)     Counter          Count     
local0                            0     down          0/0/0/0       
memif1/0                          1      up          9000/0/0/0     
memif2/0                          2      up          9000/0/0/0     
memif3/0                          3      up          9000/0/0/0     
memif4/0                          4      up          9000/0/0/0     
vpp# show l2patch 
no l2patch entries
vpp# test l2patch rx memif1/0 tx memif3/0
vpp# test l2patch rx memif4/0 tx memif2/0
vpp# show l2patch                        
                  memif1/0 -> memif3/0
                  memif4/0 -> memif2/0
```

To check the socketfiles of the showed memif for the patch configuration run:

```
vpp# show memif 
sockets
  id  listener    filename
  2   yes (1)     /var/lib/cni/usrspcni/data/memif-d3810ce7d4de-net2.sock
  4   yes (1)     /var/lib/cni/usrspcni/data/memif-ab82066a8020-net2.sock
  3   yes (1)     /var/lib/cni/usrspcni/data/memif-ab82066a8020-net1.sock
  0   no          /run/vpp/memif.sock
  1   yes (1)     /var/lib/cni/usrspcni/data/memif-d3810ce7d4de-net1.sock

...
```

### Configure rapid environment and files

On Node 1 the environment and the file for running rapid should be setted up.

Source the rapidenv and enter the rapid folder: 

```bash
[opnfv@worker ~]$ source rapidenv/bin/activate
(rapidenv) [opnfv@worker ~]$  cd rapid
(rapidenv) [opnfv@worker rapid]$
```

Now we need `.env` ,  `.tst` and `machine.map` files to run the `runrapid.py` script that do the tests.

Before creating theese files the IP of the generator pod is needed. On Node 1 run this command:

```bash
[opnfv@master ~]$ kubectl get pods -o wide
NAME                        READY   STATUS    RESTARTS   AGE   IP             NODE     NOMINATED NODE   READINESS GATES
userspace-rapid-pod-t3-p1   1/1     Running   0          69m   10.244.1.157   worker   <none>           <none>
userspace-rapid-pod-t3-p2   1/1     Running   0          69m   10.244.1.158   worker   <none>           <none>
```

For the `topology-3.env`:

```
[rapid]
loglevel = DEBUG
version = 19.6.30
total_number_of_machines = 1

[M1]
name = rapid-pod-1
admin_ip = 10.244.1.157
dp_ip = 192.168.1.4
dp_mac = de:ad:c3:52:79:9b


[ssh]
key=rapid_rsa_key
user = root

[Varia]
vim = Openstack
stack = rapid
```

Before the `.tst` file, the `prox.cfg` file should be copied under a folder in the same Node, in this case under `~/configs`. 

The `topology-3.tst`:

```
[TestParameters]
name = Rapid_ETSINFV_TST009
number_of_tests = 1
total_number_of_test_machines = 1 
lat_percentile = 99

[TestM1]
name = Generator
prox_launch_exit = false
config_file = configs/prox.cfg
dest_vm = 1
mcore = [14]
gencores = [15]
latcores = [16]

[test1]
test=TST009test
warmupflowsize=128
warmupimix=[64]
warmupspeed=1
warmuptime=2
imixs=[[64],[128],[256],[512],[1024],[1280],[1512]]
flows=[1]
drop_rate_threshold = 0
MAXr = 3
MAXz = 5000
MAXFramesPerSecondAllIngress = 12000000
StepSize = 10000
```

For `machine.map`:

```
[DEFAULT]
machine_index=0

[TestM1]
machine_index=1

[TestM2]
machine_index=2

[TestM3]
machine_index=3

[TestM4]
machine_index=4
```



### Running the tests

Now that it's all configured, the test can be started form the rapid folder with the `runrapid.py` script, passing the two files as arguments:

``` bash
(rapidenv) [opnfv@worker rapid]$ python runrapid.py --env topology-3.env --test topology-3.tst  --map machine.map --runtime 10 --screenlog DEBUG 
```

