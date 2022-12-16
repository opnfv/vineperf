<!---
This work is licensed under a Creative Commons Attribution 4.0 International License.
http://creativecommons.org/licenses/by/4.0
-->

# bpfswitch

This repository is self contained. Please install linux-headers for kernel
version.

## XDP L2 forwarding
xdp\_l2fwd handles Layer 2 forwarding between an ingress device (e.g., host
devices) and egress device (e.g., tap device for VMs or other host device). 
Userspace populates an FDB (hash map) with \<smac,dmac> pairs returning an
index into a device map which contains the device to receive the packet.
See scripts/l2fwd.sh for an example.

This program is used for the netdev 0x14 tutorial, XDP and the cloud: Using
XDP on hosts and VMs https://netdevconf.info/0x14/session.html?tutorial-XDP-and-the-cloud

## Using l2Fwd

1. Go to vineperf/src/bpfswitch/ folder.
2. First run configure script and then run make 
3. Go to scripts/ folder and open l2fwd.sh file
4. Update values of TGEN<EAST/WEST>MAC, <EAST/WEST> Interfaces and their indexes.
5. Use ifindex.py to know the indexes.
5. Ensure that path of bpftool is correc in the file.
6. Save changes and run the script.
7. If successfully run the setup is ready to test loopback

## Dummy XDP program

xdp\_dummy is a dummy XDP program that just returns XDP\_PASS.
