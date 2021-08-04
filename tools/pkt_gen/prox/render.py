import os

from conf import merge_spec
from conf import settings
from jinja2 import Environment, FileSystemLoader

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def render_content_jinja():
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

    file_loader = FileSystemLoader(templates_dir_path)
    env = Environment(loader = file_loader)
    destination_dir = settings.getValue("TRAFFICGEN_PROX_CONF_DIR")

    for filename in listdir_nohidden(templates_dir_path):
        file = env.get_template(filename)
        rendered_content = file.render(data = values_from_vineperf)
        filename = os.path.splitext(filename)[0]
        with open(os.path.join(destination_dir, filename), "w+") as fh:
           fh.write(rendered_content)
