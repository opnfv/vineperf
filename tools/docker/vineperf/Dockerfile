# To Build
# docker build --rm -t vsperf .

# -------- Builder stage.
FROM python:3.9.7-slim-buster
MAINTAINER Sridhar Rao <sridhar.rao@spirent.com>

#
# Update and Install required packages
#
ARG BUILD_DIR=/opt/vineperf
COPY ./deploytools.sh ${BUILD_DIR}/
RUN chmod +x ${BUILD_DIR}/deploytools.sh \
  && ${BUILD_DIR}/deploytools.sh

WORKDIR /root
#
# Get vineperf
#
RUN git clone https://gerrit.opnfv.org/gerrit/vineperf

#
# Remove unnecessary python packages.
#
RUN cd vineperf && \
  sed -e '/numpy/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/matplotlib/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/pycrypto/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/pypsi/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/pyzmq/ s/^#*/#\ /' -i requirements.txt && \
  sed -e "\$apyzmq" -i requirements.txt

#
# Build VINEPERF
#
RUN cd vineperf/systems && ./build_base_machine.sh --trafficgen
RUN cd vineperf/systems/pythonlibs && /bin/bash -c ./add_prox.sh --trafficgen

# Expose SSH and PROX ports
EXPOSE 22 8474

# Copy SSH keys
#COPY ./vineperf.pub /home/opnfv/.ssh/authorized_keys
COPY ./vineperf.pub /root/.ssh/authorized_keys

# Copy startup script
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]
