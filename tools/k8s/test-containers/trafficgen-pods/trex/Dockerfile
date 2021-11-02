##########################################################
# Build app-netutil components in separate builder image #
##########################################################
FROM centos:7 as builder

RUN rpm --import https://mirror.go-repo.io/centos/RPM-GPG-KEY-GO-REPO && curl -s https://mirror.go-repo.io/centos/go-repo.repo | tee /etc/yum.repos.d/go-repo.repo
RUN yum groupinstall -y "Development Tools"
RUN yum install -y wget numactl-devel git golang make; yum clean all

##
## Download and Build APP-NetUtil
##
WORKDIR /root/go/src/
RUN mkdir github.com && cd github.com && mkdir openshift && cd openshift && git clone https://github.com/openshift/app-netutil
WORKDIR /root/go/src/github.com/openshift/app-netutil
RUN make c_sample

#############################
# Create slim runtime image #
#############################
FROM centos:7

ARG BUILD_DIR=/root

COPY ./deploycentostools.sh ${BUILD_DIR}/
COPY --from=builder /root/go/src/github.com/openshift/app-netutil/bin/c_sample /usr/bin/c_sample
COPY --from=builder /root/go/src/github.com/openshift/app-netutil/bin/libnetutil_api.so /lib64/libnetutil_api.so
COPY --from=builder /root/go/src/github.com/openshift/app-netutil/bin/libnetutil_api.h /usr/include/libnetutil_api.h

RUN chmod a+rwx ${BUILD_DIR} && chmod +x ${BUILD_DIR}/deploycentostools.sh \
 && ${BUILD_DIR}/deploycentostools.sh

WORKDIR /root
COPY trex_cfg.yaml.j2 /root/trex_cfg.yaml.j2
COPY vppconf.py /root/vppconf.py
RUN wget --no-check-certificate https://trex-tgn.cisco.com/trex/release/latest; tar -xzvf latest; rm latest

# Expose SSH
EXPOSE 22

# Copy SSH keys
COPY ./rapid_rsa_key.pub /home/centos/.ssh/authorized_keys
COPY ./rapid_rsa_key.pub /root/.ssh/authorized_keys

RUN yum -y install python3 python3-pip; yum clean all
RUN pip3 install jinja2
