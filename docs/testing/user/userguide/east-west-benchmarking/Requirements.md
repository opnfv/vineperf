# Requirements for the tests

Some requirements are needed to run the test in the five topologies and these involve CPU, Memory, shared folders, etc...

### CPU

The CPUs assigned to a Pod can't be assigned to other Pods: the allocation is exclusive.

### Shared Folders

For TRex and PROX pods it's necessary to include some volumes in their pod definition file (example of these file are under the [Kubernetes configuration](./Configurations/Kubernetes)) that provide:

- Annotations and metadata:  Pod's details (e.g. memif/vhost socket file name)

  ```yaml
  ...
  spec:
  	containers:
        ...
          volumeMounts:
          - mountPath: /etc/podnetinfo
            name: podinfo
            readOnly: false
          ...
  volumes:
    - name: podinfo
      downwardAPI:
        items:
          - path: "labels"
            fieldRef:
              fieldPath: metadata.labels
          - path: "annotations"
            fieldRef:
              fieldPath: metadata.annotations
  ...
  ```

- Socket files for memif and vhost interfaces: (directory with some socket files for memif/vhost interfaces). It's shared between pods.

  ```yaml
  ...
  spec:
  	containers:
        ...
          volumeMounts:
          ...
          - mountPath: /usrspcni/
            name: shared-dir
          ...
  	volumes:
    	...
      - name: shared-dir
      hostPath:
      	path: /var/lib/cni/usrspcni/data/
  ...
  ```

  

- Hugepages:

  ```yaml
  ...
  spec:
  	containers:
        ...
          volumeMounts:
          ...
          - mountPath: /dev/hugepages
            name: hugepage
            ...
  	volumes:
  	...
  	- name: hugepage
      emptyDir:
        medium: HugePages
  ...
  ```

  

And only for PROX:

- directory with the PROX configuration files: Directory that contains `parameters.lua` and `prox.cfg` files. It's shared between pods.

  ```yaml
  ...
  spec:
  	containers:
        ...
          volumeMounts:
          ...
          - mountPath: /opt/prox/
            name: prox-dir
          ...
      volumes:
  	...
      - name: prox-dir
      hostPath:
          path: /opt/prox/
  ...
  ```

  There are two variants of this directory: one for generator pod and the other for swap pods. The configuration files are more coherent with the role of the pod.

  - Genreator pod: `/opt/proxgen`
  - Swap pods: `/opt/proxswap`

### CNIs

The first CNI that is needed is Multus. This CNI allow to assign more than a single interface to the Pod.
The choice of the CNIs that can be used for these additional interfaces is limited by the fact that the networking is in user space, so Userspace CNI should be used.

### vSwitches

As the Userspace CNI is used, the only virtual swithces that are supported are: OvS-DPDK and VPP.