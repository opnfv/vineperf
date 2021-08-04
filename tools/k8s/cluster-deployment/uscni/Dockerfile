# docker build --rm -t uscni
FROM centos:7
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN yum install -y epel-release wget; yum clean all
RUN wget --no-check-certificate https://golang.org/dl/go1.16.6.linux-amd64.tar.gz 
RUN tar -C /usr/local -xzf go1.16.6.linux-amd64.tar.gz
ENV PATH /usr/local/go/bin:$PATH
RUN yum install -y git make sudo; yum clean all
ENV GOPATH /root/go
RUN mkdir -p "/root/go" "$GOPATH/bin" "$GOPATH/src" "$GOPATH/src" && chmod -R 777 "$GOPATH"
WORKDIR /root/go/src/
ENV GO111MODULE off
RUN go get github.com/intel/userspace-cni-network-plugin > /tmp/UserspaceDockerBuild.log 2>&1 || echo "Can ignore no GO files."
WORKDIR /root/go/src/github.com/intel/userspace-cni-network-plugin
ENV GO111MODULE on
ENV GOROOT /usr/local/go
ENV GOPATH /root/go
RUN make clean && make install-dep && make install && make
RUN cp userspace/userspace /usr/bin/userspace

FROM alpine:latest
COPY --from=0 /usr/bin/userspace /userspace

ADD entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
