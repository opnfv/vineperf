# Configure PROX for bidirectional traffic

To configure PROX for bidirectional traffic starting from a unidirectional setup just modify the `parameters.lua`  and the `prox.cfg` and then modify the vSwitch configuration to connect the interfaces also in the opposite direction.

### Modify the `parameters.lua` file

Duplicate these parameters:

- `local_ip`
- `local_hex_ip`
- `local_hex_mac`
- `gencores`
- `latcores`

Adjust the names to make them unique. The file now should look like this:

```
...
local_ip1="192.168.30.11/24"
local_hex_ip1=convertIPToHex(local_ip1)
local_ip2="192.168.30.12/24"
local_hex_ip2=convertIPToHex(local_ip2)
...
local_hex_mac1="de ad c3 52 79 9b"
local_hex_mac2="02 09 c0 fd ba 1f"
gencores1="15"
gencores2="16"
latcores1="17"
latcores2="18"
...
```

### Modify the `prox.cfg` file

In this file duplicate the gencore and the latcore tasks adjust the tasks names and the variables names according to the ones in `parameters.lua` and then invert the ports number in the new tasks.

After these changes, the result is below:

```
[core $gencores1]
name=p0
task=0
mode=gen
tx port=p0
bps=1250000000
pkt inline=${local_hex_mac2} 00 00 00 00 00 00 08 00 45 00 00 2e 00 01 00 00 40 11 f7 7d ${local_hex_ip1} ${local_hex_ip2} 0b b8 0b b9 00 1a 55 7b
pkt size=60
min bulk size=$mbs
max bulk size=16
drop=yes
lat pos=42
accuracy pos=46
packet id pos=50
signature=0x98765432
signature pos=56
;arp update time=1

[core $gencores2]
name=p1
task=0
mode=gen
tx port=p1
bps=1250000000
pkt inline=${local_hex_mac1} 00 00 00 00 00 00 08 00 45 00 00 2e 00 01 00 00 40 11 f7 7d ${local_hex_ip2} ${local_hex_ip1} 0b b8 0b b9 00 1a 55 7b
pkt size=60
min bulk size=$mbs
max bulk size=16
drop=yes
lat pos=42
accuracy pos=46
packet id pos=50
signature=0x98765432
signature pos=56
;arp update time=1

[core $latcores1]
name=lat1
task=0
mode=lat
;sub mode=l3
rx port=p1
lat pos=42
accuracy pos=46
packet id pos=50
signature=0x98765432
signature pos=56
accuracy limit nsec=1000000
latency bucket size=${bucket_size_exp}
;arp update time=1

[core $latcores2]
name=lat2
task=0
mode=lat
;sub mode=l3
rx port=p0
lat pos=42
accuracy pos=46
packet id pos=50
signature=0x98765432
signature pos=56
accuracy limit nsec=1000000
latency bucket size=${bucket_size_exp}
;arp update time=1
```

### Modify VPP

To configure the opposite direction just copy the l2patches for the unidirectional traffic and invert the ports number:

```
vpp# show l2patch
                  memif1/0 -> memif3/0
                  memif4/0 -> memif2/0
vpp# test l2patch rx memif2/0 tx memif4/0
vpp# test l2patch rx memif3/0 tx memif1/0
vpp# show l2patch
                  memif1/0 -> memif3/0
                  memif2/0 -> memif4/0
                  memif3/0 -> memif1/0
                  memif4/0 -> memif2/0
```

###  Modify OvS-DPDK

To configure the opposite direction just edit the `setup-flows.sh`  copying the existing flows for the unidirectional traffic and invert the ports actions:

``` bash
udo ovs-ofctl --timeout 10 -O OpenFlow13 del-flows vsperf-br0
sudo ovs-ofctl --timeout 10 -O Openflow13 add-flow vsperf-br0 in_port=1,idle_timeout=0,action=output:3
sudo ovs-ofctl --timeout 10 -O Openflow13 add-flow vsperf-br0 in_port=4,idle_timeout=0,action=output:2
sudo ovs-ofctl --timeout 10 -O Openflow13 add-flow vsperf-br0 in_port=3,idle_timeout=0,action=output:1
sudo ovs-ofctl --timeout 10 -O Openflow13 add-flow vsperf-br0 in_port=2,idle_timeout=0,action=output:4
```

Run `sudo ./setup_flows.sh` and verify that the flows are correct by running `sudo ovs-ofctl dump-flows vsperf-br0`:

``` bash
[opnfv@worker utilities]$ sudo ovs-ofctl dump-flows vsperf-br0
 cookie=0x0, duration=10.400s, table=0, n_packets=0, n_bytes=0, in_port=1 actions=output:3
 cookie=0x0, duration=10.348s, table=0, n_packets=0, n_bytes=0, in_port=4 actions=output:2
 cookie=0x0, duration=10.410s, table=0, n_packets=0, n_bytes=0, in_port=3 actions=output:1
 cookie=0x0, duration=10.358s, table=0, n_packets=0, n_bytes=0, in_port=2 actions=output:4
```

### Configure rapid environment and files

On Node 1 source the rapidenv and enter the rapid folder:

```bash
[opnfv@worker ~]$ source rapidenv/bin/activate
(rapidenv) [opnfv@worker ~]$  cd rapid
(rapidenv) [opnfv@worker rapid]$
```

Now we need to modify the `.env` ,  `.tst` files to run the `runrapid.py` script that do the tests.

For the `topology-3.env`:

```
[rapid]
loglevel = DEBUG
version = 19.6.30
total_number_of_machines = 1

[M1]
name = rapid-pod-1
admin_ip = 10.244.1.157
dp_ip1 = 192.168.30.11
dp_mac1 = de:ad:c3:52:79:9b
dp_ip2 = 192.168.30.12
dp_mac2 = 02:09:c0:fd:ba:1f


[ssh]
key=rapid_rsa_key
user = root

[Varia]
vim = Openstack
stack = rapid
```

Before editing the `.tst` file, the new `prox.cfg` file should be copied under a folder in the same Node, in this case under `~/configs` and renamed as `prox-bi.cfg`.

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
config_file = configs/prox-bi.cfg
dest_vm = 1
mcore = [14]
gencores = [15,16]
latcores = [17,18]

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

### Running the tests

Now that it's all configured, the test can be started form the rapid folder with the `runrapid.py` script, passing the two files as arguments:

``` bash
(rapidenv) [opnfv@worker rapid]$ python runrapid.py --env topology-3.env --test topology-3.tst  --map machine.map --runtime 10 --screenlog DEBUG
```

