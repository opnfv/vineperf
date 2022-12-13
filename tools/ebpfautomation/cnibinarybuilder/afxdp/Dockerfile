# Build the container
# docker build -t afxdpbuilder .
# Copy the binary from container to local system (ex: replace ./ with /opt/cni/bin)
# docker run --name afxdp afxdpbuilder && docker cp afxdp:/usr/local/bin/afxdp ./ && docker stop afxdp && docker rm afxdp
FROM golang:1.19

WORKDIR /usr/src/

RUN git clone https://github.com/intel/afxdp-plugins-for-kubernetes afxdp
RUN apt-get update 
RUN apt-get install -y libbpf-dev

WORKDIR /usr/src/afxdp

RUN go build -o /usr/local/bin/afxdp ./cmd/cni
