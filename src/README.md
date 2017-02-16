<!---
This work is licensed under a Creative Commons Attribution 4.0 International License.
http://creativecommons.org/licenses/by/4.0
-->

### Purpose of this folder - Quickview

1. contains place holders for upstream source code package.
2. manages the package dependency
3. provides simple one-button build for test developers

### Motivation Explained

There are multiple goals for the project vswitch performance characterization.
First,  it is a generic test framework that can be used to characterize any vswitch solution.
Second, it is to be as CI tool to validate any change during development.

For the first goal, it would be nice to get all the relevant upstream source package and
to provide a easy build environment for a given test developer. Obviously we don't want to
rewrite the makefile system from upstream project. However we need to add a wrapper to the
individual packages to manage package dependecy. For example, to test ovs-dpdk vswitch solution,
the build of ovs would depend on the build result of dpdk.
This dependency is never explicitly specified in the individual package.

For the second goal as a CI tool, it may not be needed to pull the upstream package.
So this whole folder can be ignored.

### Files and subfolders

* package-list: contains list of packages and their associated tags
* mk:           contains top level makefiles
* dpdk:         place holder for dpdk package
* ovs:          place holder for ovs package.
* l2fwd:        simple l2 forwarding kernel module
