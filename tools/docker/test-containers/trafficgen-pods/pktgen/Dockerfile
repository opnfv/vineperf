FROM centos:7 as builder

#
## Install required packages
##
RUN rpm --import https://mirror.go-repo.io/centos/RPM-GPG-KEY-GO-REPO && curl -s https://mirror.go-repo.io/centos/go-repo.repo | tee /etc/yum.repos.d/go-repo.repo
RUN yum groupinstall -y "Development Tools"
RUN yum install -y wget numactl-devel git golang make; yum clean all
## Debug Tools (if needed):
RUN yum install -y pciutils iproute; yum clean all

##
## Download and Build APP-NetUtil
##
WORKDIR /root/go/src/
RUN mkdir github.com && cd github.com && mkdir openshift && cd openshift && git clone https://github.com/openshift/app-netutil
WORKDIR /root/go/src/github.com/openshift/app-netutil
RUN make c_sample
RUN cp bin/libnetutil_api.so /lib64/libnetutil_api.so; cp bin/libnetutil_api.h /usr/include/libnetutil_api.h

## Download and Build DPDK
##


ENV DPDK_VER 21.02
ENV DPDK_DIR /usr/src/dpdk-${DPDK_VER}
WORKDIR /usr/src/
RUN wget http://fast.dpdk.org/rel/dpdk-${DPDK_VER}.tar.xz
RUN tar -xpvf dpdk-${DPDK_VER}.tar.xz
ENV RTE_TARGET=x86_64-native-linuxapp-gcc
ENV RTE_SDK=${DPDK_DIR}
WORKDIR ${DPDK_DIR}

COPY ./vhost_substitute.sh ./vhost_substitute.sh
RUN ./vhost_substitute.sh

EXPOSE 22 8474

RUN yum install -y epel-release && yum install -y dnf
RUN dnf install -y meson ninja-build
RUN pip3 install pyelftools

RUN meson build && ninja -C build && ninja -C build install && ldconfig

WORKDIR /usr/src/
ENV PKG_CONFIG_PATH /usr/local/lib64/pkgconfig
RUN git clone http://dpdk.org/git/apps/pktgen-dpdk
RUN yum install -y libpcap libpcap-devel
RUN yum install -y kernel-devel kernel-headers
RUN cd pktgen-dpdk && git checkout tags/pktgen-21.02.0 && make -j
