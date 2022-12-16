#!/bin/bash

# Copyright David Ashern and Sridhar K. N. Rao

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

# L2FWD configuration 


BPFFS=/sys/fs/bpf
BPFTOOL=/usr/sbin/bpftool

# MAC ADDRESSES - Ex: Of Traffic-Generator Ports
TGENEASTMAC=12:41:da:80:1f:71
TGENWESTMAC=12:30:6d:9f:6f:42

# Interfaces
EAST=ens0f0
WEST=ens0f1

# Index of Interfaces
EASTINDEX=1
EASTINDEX=2


################################################################################
#
pr_msg()
{
	echo -e "\e[34m$*\e[00m"
}

run_cmd()
{
	local cmd="$*"

	echo
	echo -e "\e[31m${cmd}\e[00m"
	sudo $cmd
}

show_maps()
{
	echo
        echo -e "\e[31m${BPFTOOL} map sh\e[00m"
	sudo ${BPFTOOL} map sh | \
	awk 'BEGIN { skip = 0 } {
		if (skip) {
			skip--
		} else if ($2 == "lpm_trie") {
			skip = 1
		} else {
			print
		}
	}'
}

show_progs()
{
	echo
        echo -e "\e[31m${BPFTOOL} prog sh\e[00m"
	sudo ${BPFTOOL} prog sh | \
	awk 'BEGIN { skip = 0 } {
		if (skip) {
			skip--
		} else if ($2 == "cgroup_skb") {
			skip = 2
		} else {
			print
		}
	}'
}

show_status()
{
	show_maps
	show_progs
	run_cmd ${BPFTOOL} net sh
}

do_reset()
{
	sudo rm -rf ${BPFFS}/map
	sudo rm -rf ${BPFFS}/prog
	sudo mkdir ${BPFFS}/map
	sudo mkdir ${BPFFS}/prog

	for d in eth0 eth1
	do
		sudo ${BPFTOOL} net detach xdp dev ${d}
		sudo ethtool -K ${d} hw-tc-offload on
		sudo ethtool -K ${d} rxvlan off
	done
}

################################################################################
# start

do_reset >/dev/null 2>&1

echo
pr_msg "Create ports map"
pr_msg "- global map used for bulking redirected packets"

run_cmd ${BPFTOOL} map create ${BPFFS}/map/xdp_fwd_ports \
       type devmap_hash key 4 value 8 entries 512 name xdp_fwd_ports

echo
pr_msg "Add entries to the egress port map for EAST and WEST Interfaces"
run_cmd ${BPFTOOL} map update pinned ${BPFFS}/map/xdp_fwd_ports \
	key hex ${EASTINDEX} 0 0 0 value hex ${EASTINDEX} 0 0 0 0 0 0 0
run_cmd ${BPFTOOL} map update pinned ${BPFFS}/map/xdp_fwd_ports \
	key hex ${WESTINDEX} 0 0 0 value hex ${WESTINDEX} 0 0 0 0 0 0 0

echo
pr_msg "load l2fwd program and attach to eth0 and eth1"

run_cmd ${BPFTOOL} prog load ../ksrc/obj/xdp_l2fwd.o ${BPFFS}/prog/xdp_l2fwd \
    map name xdp_fwd_ports name xdp_fwd_ports
run_cmd ${BPFTOOL} net attach xdp pinned ${BPFFS}/prog/xdp_l2fwd dev ${EAST}
run_cmd ${BPFTOOL} net attach xdp pinned ${BPFFS}/prog/xdp_l2fwd dev ${WEST}

echo
pr_msg "Add FDB and port map entries for this"
run_cmd ../usrc/bin/xdp_l2fwd -s ${TGENEASTMAC} -m ${TGENWESTMAC} -d eth1
run_cmd ../usrc/bin/xdp_l2fwd -s ${TGENWESTMAC} -m ${TGENEASTMAC} -d eth1
run_cmd ../usrc/bin/xdp_l2fwd -P
