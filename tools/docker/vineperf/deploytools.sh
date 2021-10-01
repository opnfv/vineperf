#!/usr/bin/env bash

# If already running from root, no need for sudo
SUDO=""
[ $(id -u) -ne 0 ] && SUDO="sudo"

function os_pkgs_install()
{
	${SUDO} apt-get -y update
	# Install required packages
	${SUDO} apt-get install -y git wget iputils-ping iproute2 unzip openssh-server openssh-client tk sudo
}

function os_cfg()
{
	[ ! -f /etc/ssh/ssh_host_rsa_key ] && ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''
	[ ! -f /etc/ssh/ssh_host_ecdsa_key ] && ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N ''
	[ ! -f /etc/ssh/ssh_host_ed25519_key ] && ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ''

	[ ! -d /var/run/sshd ] && mkdir -p /var/run/sshd

	USER_NAME="opnfv"
	USER_PWD="opnfv"
	ROOT_USER="root"

	useradd -m -d /home/${USER_NAME} -s /bin/bash -U ${USER_NAME}
	echo "${USER_NAME}:${USER_PWD}" | chpasswd
	echo "${ROOT_USER}:${USER_PWD}" | chpasswd
	usermod -aG sudo ${USER_NAME}

	echo "%sudo ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${USER_NAME}
}

function cleanup()
{
	${SUDO} apt-get autoremove -y
	${SUDO} apt-get clean all
	${SUDO} rm -rf /var/cache/apt
}

os_pkgs_install
os_cfg
cleanup
