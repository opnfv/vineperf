# Copyright 2022 The Linux Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
