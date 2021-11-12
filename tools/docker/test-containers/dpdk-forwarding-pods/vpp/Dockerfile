# Build with latest VPP release
# docker build -t vpp .
# Build with stable VPP 20.05
# docker build --build-arg REPO='2005' -t vpp .
# Build with exact VPP version
# docker build --build-arg REPO='master' --build-arg VPP_VERSION='20.09-rc0~174-gbfeae8c57' -t vpp .
# Build with specific VPP commit
# docker build --build-arg REPO='master' --build-arg VPP_VERSION='20.09-rc0~[^ ]*-g<commit>' -t vpp .

# Post-Build
#vpp_version=$(docker run --rm $IMAGE_NAME cat /vpp/version)
#vpp_release=$(echo $vpp_version | cut -d~ -f1)
#vpp_commit=$(echo $vpp_version | sed -r 's/.*-g([0-9a-f]+).*/\1/')
#VPP_VERSION=$(docker run --rm $IMAGE_NAME cat /vpp/version | cut -d~ -f1,2 | sed -e 's/~/./g')

FROM ubuntu:18.04

RUN apt-get update && apt-get install -y --no-install-recommends \
		apt-transport-https \
		ca-certificates \
		curl \
		gnupg \
		iproute2 \
		iputils-ping \
 	&& rm -rf /var/lib/apt/lists/*

ARG REPO
ARG VPP_VERSION

WORKDIR /vpp

COPY get-vpp.sh /get-vpp.sh

RUN set -eux; \
	/get-vpp.sh; \
	apt-get update && apt-get install -y -V ./*.deb; \
	dpkg-query -f '${Version}\n' -W vpp > /vpp/version; \
	rm -rf vom*.deb vpp-dbg*.deb; \
	rm -rf /var/lib/apt/lists/*;

RUN mkdir -p /var/log/vpp

CMD ["/usr/bin/vpp", "-c", "/etc/vpp/startup.conf"]
