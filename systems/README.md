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

eBPF 
----

Adding eBPF support may require additional installations. The installation
script already includes tools like llvm, clang, libbpf-dev, etc.
For some programs, you may have to build kernel by downloading the source.
In the folder where you have kernel source, run:
```
make oldconfig && make prepare && make headers_install && make
```
While building any program, if you encounter an error with bpf.h in
include/linux/ folder, get the latest of bcc from iovisor project,
using following commands

```
apt purge bpfcc-tools libbpfcc python3-bpfcc
wget https://github.com/iovisor/bcc/releases/download/v0.25.0/bcc-src-with-submodule.tar.gz
tar xf bcc-src-with-submodule.tar.gz
cd bcc/
apt install -y python-is-python3
apt install -y bison build-essential cmake flex git libedit-dev   libllvm11 llvm-11-dev libclang-11-dev zlib1g-dev libelf-dev libfl-dev python3-distutils
apt install -y checkinstall
mkdir build
cd build/
cmake -DCMAKE_INSTALL_PREFIX=/usr -DPYTHON_CMD=python3 ..
make
checkinstall
```   
