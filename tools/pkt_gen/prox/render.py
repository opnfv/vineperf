# Copyright 2021 Spirent Communications.
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

"""
Render Jinja templates to corresponding files
"""

import os

#from conf import merge_spec
from conf import settings
from jinja2 import Environment, FileSystemLoader

def listdir_nohidden(path):
    """
    Exclude hidden directories
    """
    for fname in os.listdir(path):
        if not fname.startswith('.'):
            yield fname

def render_content_jinja_baremetal(pkt_size):
    """
    Render Templates
    """
    templates_dir_path = settings.getValue('TRAFFICGEN_PROX_TEMPLATES_DIR')
    values_from_vineperf = {
        'm1_admin_ip' : settings.getValue('TRAFFICGEN_PROX_EAST_MGMT_IP'),
        'm2_admin_ip' : settings.getValue('TRAFFICGEN_PROX_WEST_MGMT_IP'),
        'local_ip1' : settings.getValue('TRAFFICGEN_PROX_EAST_IP'),
        'local_ip2' : settings.getValue('TRAFFICGEN_PROX_WEST_IP'),
        'local_eip1' : settings.getValue('TRAFFICGEN_PROX_EAST_ENV_IP'),
        'local_eip2' : settings.getValue('TRAFFICGEN_PROX_WEST_ENV_IP'),
        'mac1' : settings.getValue('TRAFFICGEN_PROX_EAST_MAC'),
        'mac2' : settings.getValue('TRAFFICGEN_PROX_WEST_MAC'),
        'emac1' : settings.getValue('TRAFFICGEN_PROX_EAST_ENV_MAC'),
        'emac2' : settings.getValue('TRAFFICGEN_PROX_WEST_ENV_MAC'),
        'pci1': settings.getValue('TRAFFICGEN_PROX_EAST_PCI_ID'),
        'pci2': settings.getValue('TRAFFICGEN_PROX_WEST_PCI_ID'),
        'mcore' : settings.getValue('TRAFFICGEN_PROX_MASTER_CORES'),
        'gencores' : settings.getValue('TRAFFICGEN_PROX_GENERATOR_CORES'),
        'latcores' : settings.getValue('TRAFFICGEN_PROX_LATENCY_CORES'),
        'config_file' : os.path.join(settings.getValue('TRAFFICGEN_PROX_CONF_DIR'),
            settings.getValue('TRAFFICGEN_PROX_GENERATOR_CONFIG_FILENAME')),
        'user' : settings.getValue('TRAFFICGEN_PROX_GENERATOR_USER'),
        'key' : os.path.join(settings.getValue('TRAFFICGEN_PROX_CONF_DIR'),
            settings.getValue('TRAFFICGEN_PROX_GENERATOR_KEYFILE')),
        'latency_buckets': settings.getValue('TRAFFICGEN_PROX_LATENCY_BUCKETS'),
    }
    if pkt_size:
        values_from_vineperf['pktsizes'] = pkt_size
    else:
        values_from_vineperf['pktsizes'] = settings.getValue('TRAFFICGEN_PROX_PKTSIZES')

    file_loader = FileSystemLoader(templates_dir_path)
    env = Environment(loader = file_loader)
    destination_dir = settings.getValue("TRAFFICGEN_PROX_CONF_DIR")

    for filename in listdir_nohidden(templates_dir_path):
        file = env.get_template(filename)
        rendered_content = file.render(data = values_from_vineperf)
        filename = os.path.splitext(filename)[0]
        with open(os.path.join(destination_dir, filename), "w+") as fileh:
            fileh.write(rendered_content)
