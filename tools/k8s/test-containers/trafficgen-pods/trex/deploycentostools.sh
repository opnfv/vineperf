#!/usr/bin/env bash
##
## Copyright (c) 2010-2020 Intel Corporation
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##

# Directory for package build
BUILD_DIR="/root"
DPDK_VERSION="20.05"
MULTI_BUFFER_LIB_VER="0.52"
export RTE_SDK="${BUILD_DIR}/dpdk-${DPDK_VERSION}"
export RTE_TARGET="x86_64-native-linuxapp-gcc"

# By default, do not update OS
OS_UPDATE="n"
# By default, asumming that we are in the VM
K8S_ENV="y"

# If already running from root, no need for sudo
SUDO=""
[ $(id -u) -ne 0 ] && SUDO="sudo"

function os_pkgs_install()
{
	${SUDO} yum install -y deltarpm yum-utils

	# NASM repository for AESNI MB library
	#${SUDO} yum-config-manager --add-repo http://www.nasm.us/nasm.repo

	[ "${OS_UPDATE}" == "y" ] && ${SUDO} yum update -y
	${SUDO} yum install -y git wget gcc unzip libpcap-devel ncurses-devel \
			 libedit-devel lua-devel kernel-devel iperf3 pciutils \
			 numactl-devel vim tuna openssl-devel wireshark \
			 make driverctl

	${SUDO} wget https://www.nasm.us/pub/nasm/releasebuilds/2.14.02/linux/nasm-2.14.02-0.fc27.x86_64.rpm
	${SUDO} rpm -ivh nasm-2.14.02-0.fc27.x86_64.rpm
}


function os_pkgs_runtime_install()
{
	[ "${OS_UPDATE}" == "y" ] && ${SUDO} yum update -y

	# Install required dynamically linked libraries + required packages
	${SUDO} yum install -y numactl-libs libpcap openssh openssh-server \
		  openssh-clients sudo iproute
}


function os_cfg()
{
	[ ! -f /etc/ssh/ssh_host_rsa_key ] && ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''
	[ ! -f /etc/ssh/ssh_host_ecdsa_key ] && ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N ''
	[ ! -f /etc/ssh/ssh_host_ed25519_key ] && ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ''

	[ ! -d /var/run/sshd ] && mkdir -p /var/run/sshd

	USER_NAME="centos"
	USER_PWD="centos"

	useradd -m -d /home/${USER_NAME} -s /bin/bash -U ${USER_NAME}
	echo "${USER_NAME}:${USER_PWD}" | chpasswd
	usermod -aG wheel ${USER_NAME}

	echo "%wheel ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/wheelnopass
}

function dpdk_install()
{
	# Build DPDK for the latest kernel installed
	LATEST_KERNEL_INSTALLED=`ls -v1 /lib/modules/ | tail -1`
	export RTE_KERNELDIR="/lib/modules/${LATEST_KERNEL_INSTALLED}/build"

	# Get and compile DPDK
	pushd ${BUILD_DIR} > /dev/null 2>&1
	wget http://fast.dpdk.org/rel/dpdk-${DPDK_VERSION}.tar.xz
	tar -xf ./dpdk-${DPDK_VERSION}.tar.xz
	popd > /dev/null 2>&1

	${SUDO} ln -s ${RTE_SDK} ${BUILD_DIR}/dpdk

	pushd ${RTE_SDK} > /dev/null 2>&1
	make config T=${RTE_TARGET}
	# Starting from DPDK 20.05, the IGB_UIO driver is not compiled by default.
	# Uncomment the sed command to enable the driver compilation
	#${SUDO} sed -i 's/CONFIG_RTE_EAL_IGB_UIO=n/c\/CONFIG_RTE_EAL_IGB_UIO=y' ${RTE_SDK}/build/.config

	# For Kubernetes environment we use host vfio module
	if [ "${K8S_ENV}" == "y" ]; then
		sed -i 's/CONFIG_RTE_EAL_IGB_UIO=y/CONFIG_RTE_EAL_IGB_UIO=n/g' ${RTE_SDK}/build/.config
		sed -i 's/CONFIG_RTE_LIBRTE_KNI=y/CONFIG_RTE_LIBRTE_KNI=n/g' ${RTE_SDK}/build/.config
		sed -i 's/CONFIG_RTE_KNI_KMOD=y/CONFIG_RTE_KNI_KMOD=n/g' ${RTE_SDK}/build/.config
	fi

	# Compile with MB library if reqd.
	# sed -i '/CONFIG_RTE_LIBRTE_PMD_AESNI_MB=n/c\CONFIG_RTE_LIBRTE_PMD_AESNI_MB=y' ${RTE_SDK}/build/.config
	make -j`getconf _NPROCESSORS_ONLN`
	ln -s ${RTE_SDK}/build ${RTE_SDK}/${RTE_TARGET}
	popd > /dev/null 2>&1
}

function cleanup()
{
	${SUDO} yum autoremove -y
	${SUDO} yum clean all
	${SUDO} rm -rf /var/cache/yum
	${SUDO} rm ${BUILD_DIR}/*.xz
}

os_pkgs_install
os_cfg
dpdk_install
os_pkgs_runtime_install
cleanup
