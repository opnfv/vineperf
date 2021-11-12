#!/bin/bash

# SPDX-License-Identifier: Apache-2.0
# Copyright(c) 2021 Red Hat, Inc.


# Add new app-netutil headerfile to the main code so app-netutil
# can be called to gather parameters.
#
# Search for line with: "#include <rte_mbuf.h>".
# Append line:          "#include "dpdk-args.h"".
sed -i -e '/#include <rte_mbuf.h>/a #include "dpdk-args.h"' main.c


# Replace the call to rte_eal_init() to call app-netutil code first
# if no input parametes were passed in. app-netutil code generates
# its own set of DPDK parameters that are used instead. If input
# parameters were passed in, call rte_eal_init() with input parameters
# and run as if app-netutil wasn't there.
#
# Search for the line with "ret = rte_eal_init(argc, argv);"
# Create a label 'a' and continue searching and copying until
#   line with "argv += ret;" is found.
# Replace that block of code with the contents of file 'l2fwd_eal_init.txt'.
sed -i '/ret = rte_eal_init(argc, argv);/{
:a;N;/argv += ret;/!ba;N;s/.*\n//g
r l2fwd_eal_init.txt
}' main.c


# If no input parametes were passed in, use the parameter list generated
# by app-netutil in the previous patch to call the local parameter
# parsing code, l2fwd_parse_args(). If input parameters were passed in,
# call l2fwd_parse_args() with input parameters and run as if app-netutil
# wasn't there.
#
# Search for the line with "ret = l2fwd_parse_args(argc, argv);"
# Replace that line of code with the contents of file
#   'l2fwd_parse_args.txt'.
sed -i '/ret = l2fwd_parse_args(argc, argv);/{
s/ret = l2fwd_parse_args(argc, argv);//g
r l2fwd_parse_args.txt
}' main.c


# Add new app-netutil source file to the Makefile.
#
# Search for line with: "SRCS-y :=".
# Append line:          "SRCS-y += c_util.c dpdk-args.c".
sed -i -e '/SRCS-y :=/a SRCS-y += c_util.c dpdk-args.c' Makefile


# Add new app-netutil shared library to the Makefile.
# Contains the C API and GO package which collects the
# interface data.
#
# Search for line with: "SRCS-y += c_util.c dpdk-args.c".
# Append line:          "LDLIBS += -lnetutil_api".
sed -i -e '/SRCS-y += c_util.c dpdk-args.c/a LDLIBS += -lnetutil_api' Makefile
