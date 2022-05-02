# Stressor for Cloud-Native Usecases using Spirent Cloudstress

## Updating the configuration

Modify the config.zpl file according to your requirements - configure the required amount of CPU and Memory stresses.

##  Building container (if required)

Download the cloudstress binary from the artifacts.

Build using the following command

```sh
$ docker build --rm -t autocloudstress .
```

## Using existing container.

Pre-built container exists in dockerhub as: vsperf/autocloudstress:thoth

## Running workloads.

Run the built or existing container as pods.
Example deployment file: csdeployment.yaml present in this folder.
