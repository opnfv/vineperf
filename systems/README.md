<!---
This work is licensed under a Creative Commons Attribution 4.0 International License.
http://creativecommons.org/licenses/by/4.0
-->

This folder abstract out details among linux distros.

One time setup:
---------------

On a freshly built system, run the following with a super user privilege
or with password less sudo access.
```
    ./build_base_machine.sh
```

If you want to use vsperf in trafficgen-mode ONLY, then add a parameter.
```
    ./build_base_machine.sh trafficgen
```

Newer Kernel Versions:
----------------------

May need following changes:

1. In src/l2fwd/l2fwd.c, comment out the line with xmit_more (193).

2. In src/qemu/Makefile, In line 30, we MAY have to add the following:
```
    --disable-werror 
```
3. In src/qemu/Makefile, In line 31, we MAY have to change python flag to:
```
    --python='/usr/bin/python3'
```
4. If Fedora 32+ is used, then change the line 52 in src/ovs/Makefile to:
```   
    DPDK_LIB = $(DPDK_DIR)/build/lib64
```

   
