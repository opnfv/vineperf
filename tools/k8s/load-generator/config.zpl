# Copyright 2022 Spirent Communications.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on a "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied

#rfc.zeromq.org/spec:4/ZPL

generator
    cpu
        utilization = 100.0
        running = "true"
    block
        writes_per_sec = 1048576
        write_size = 2M
        reads_per_sec = 1048576
        read_size = 2M
        queue_depth = 4
        vdev_path = "/tmp"
        vdev_size = 1048576000
        file_size = 1000
        running = "true"
        pattern = "random"
    memory
        writes_per_sec = 1048576
        write_size = 2000000
        reads_per_sec = 1048576
        read_size = 2000000
        buffer_size = 250000000
        running = "true"
        pattern = "random"
    network.client
        connections = 10
        threads = 5
        ops_per_connection = 10
        protocol = tcp
        writes_per_sec = 1043576
        write_size = 2000000
        reads_per_sec = 1043576
        read_size = 2000000
        running = "true"
    network.server
        running = "true"
