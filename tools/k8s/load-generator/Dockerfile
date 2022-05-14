# Copyright 2022 The Linux Foundation.
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

FROM debian:bullseye
RUN mkdir -p /opt/spirent/inception
EXPOSE 3357
EXPOSE 13731
EXPOSE 13771
EXPOSE 17731
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y net-tools procps
COPY ./config.zpl /opt/spirent/inception/config.zpl
COPY ./cloudstress /opt/spirent/inception/cloudstress
WORKDIR /opt/spirent/inception
CMD ["cloudstress", "--conffile", "config.zpl"]
