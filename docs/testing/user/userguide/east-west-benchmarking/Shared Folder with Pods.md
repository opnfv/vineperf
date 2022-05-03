# Shared Folder with Pods

For TRex and PROX pods it's necessary to include some volumes in their pod definition file (example of these file are under the [Kubernetes configuration](./Configurations/Kubernetes)) that provide:

- Annotations and metadata:  Pod's details (e.g. memif/vhost socket file name)

  ```
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

  ```
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

  ```
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

  ```
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



