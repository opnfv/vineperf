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
