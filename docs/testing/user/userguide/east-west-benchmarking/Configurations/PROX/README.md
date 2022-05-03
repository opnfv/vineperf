# PROX Configuration files

In this folder there are all the files to configure a pod, with one or two interfaces running PROX, as a generator or a swap.

The `eal` parameter in all `parameters.lua` files are configured for VPP and memif interfaces. To use OvS-DPDK and virtio-user interfaces replace that line with something like this:

- One interface: `eal="--socket-mem=256,0 --vdev=virtio_user0,path=/usrspcni/563e4f024755-net1"`
- Two interface: `eal="--socket-mem=256,0 --vdev=virtio_user0,path=/usrspcni/563e4f024755-net1 --vdev=virtio_user1,path=/usrspcni/563e4f024755-net2"`

