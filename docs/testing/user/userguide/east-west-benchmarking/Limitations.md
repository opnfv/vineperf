# Limitations

There are some limitations due to the different tools used:
- TRex
  - Does not support virtio driver for vhost-user interfaces needed by OvS-DPDK.
  - Does not support single interface configuration (dummy interfaces) with memif.
- PROX
  - In this envirorment it does not support multiple core assignement for a single task.
- Memif
  - Configuration can be changed only by modifying the source code of Userspace CNI.