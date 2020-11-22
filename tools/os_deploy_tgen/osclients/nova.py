# Copyright (c) 2020 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Nova Client
"""

import itertools
import re
import time

from novaclient import client as nova_client_pkg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class ForbiddenException(nova_client_pkg.exceptions.Forbidden):
    """
    Custome Exception
    """



def get_available_compute_nodes(nova_client, flavor_name):
    """
    Return available compute nodes
    """
    try:
        host_list = [dict(host=svc.host, zone=svc.zone)
                     for svc in
                     nova_client.services.list(binary='nova-compute')
                     if svc.state == 'up' and svc.status == 'enabled']

        # If the flavor has aggregate_instance_extra_specs set then filter
        # host_list to pick only the hosts matching the chosen flavor.
        flavor = get_flavor(nova_client, flavor_name)

        if flavor is not None:
            extra_specs = flavor.get_keys()

            for item in extra_specs:
                if "aggregate_instance_extra_specs" in item:
                    LOG.debug('Flavor contains %s, using compute node '
                              'filtering', extra_specs)

                    # getting the extra spec seting for flavor in the
                    # standard format of extra_spec:value
                    extra_spec = item.split(":")[1]
                    extra_spec_value = extra_specs.get(item)

                    # create a set of aggregate host which match
                    agg_hosts = set(itertools.chain(
                        *[agg.hosts for agg in
                          nova_client.aggregates.list() if
                          agg.metadata.get(extra_spec) == extra_spec_value]))

                    # update list of available hosts with
                    # host_aggregate cross-check
                    host_list = [elem for elem in host_list if
                                 elem['host'] in agg_hosts]

        LOG.debug('Available compute nodes: %s ', host_list)

        return host_list

    except nova_client_pkg.exceptions.Forbidden as error:
        msg = 'Forbidden to get list of compute nodes'
        raise ForbiddenException(msg) from error


def does_flavor_exist(nova_client, flavor_name):
    """
    Check if flavor exists
    """
    for flavor in nova_client.flavors.list():
        if flavor.name == flavor_name:
            return True
    return False


def create_flavor(nova_client, **kwargs):
    """
    Create a flavor
    """
    try:
        nova_client.flavors.create(**kwargs)
    except nova_client_pkg.exceptions.Forbidden as error:
        msg = 'Forbidden to create flavor'
        raise ForbiddenException(msg) from error


def get_server_ip(nova_client, server_name, ip_type):
    """
    Get IP of the compute
    """
    server = nova_client.servers.find(name=server_name)
    addresses = server.addresses
    ips = [v['addr'] for v in itertools.chain(*addresses.values())
           if v['OS-EXT-IPS:type'] == ip_type]
    if not ips:
        raise Exception('Could not get IP address of server: %s' % server_name)
    if len(ips) > 1:
        raise Exception('Server %s has more than one IP addresses: %s' %
                        (server_name, ips))
    return ips[0]


def get_server_host_id(nova_client, server_name):
    """
    Get the host id
    """
    server = nova_client.servers.find(name=server_name)
    return server.hostId


def check_server_console(nova_client, server_id, len_limit=100):
    """
    Check Server console
    """
    try:
        console = (nova_client.servers.get(server_id)
                   .get_console_output(len_limit))
    except nova_client_pkg.exceptions.ClientException as exc:
        LOG.warning('Error retrieving console output: %s. Ignoring', exc)
        return None

    for line in console.splitlines():
        if (re.search(r'\[critical\]', line, flags=re.IGNORECASE) or
                re.search(r'Cloud-init.*Datasource DataSourceNone\.', line)):
            message = ('Instance %(id)s has critical cloud-init error: '
                       '%(msg)s. Check metadata service availability' %
                       dict(id=server_id, msg=line))
            LOG.error(message)
            return message
        if re.search(r'\[error', line, flags=re.IGNORECASE):
            LOG.error('Error message in instance %(id)s console: %(msg)s',
                      dict(id=server_id, msg=line))
        elif re.search(r'warn', line, flags=re.IGNORECASE):
            LOG.info('Warning message in instance %(id)s console: %(msg)s',
                     dict(id=server_id, msg=line))

    return None


def _poll_for_status(nova_client, server_id, final_ok_states, poll_period=20,
                     status_field="status"):
    """
    Poll for status
    """
    LOG.debug('Poll instance %(id)s, waiting for any of statuses %(statuses)s',
              dict(id=server_id, statuses=final_ok_states))
    while True:
        obj = nova_client.servers.get(server_id)

        err_msg = check_server_console(nova_client, server_id)
        if err_msg:
            raise Exception('Critical error in instance %s console: %s' %
                            (server_id, err_msg))

        status = getattr(obj, status_field)
        if status:
            status = status.lower()

        LOG.debug('Instance %(id)s has status %(status)s',
                  dict(id=server_id, status=status))

        if status in final_ok_states:
            break
        if status in ('error', 'paused'):
            raise Exception(obj.fault['message'])

        time.sleep(poll_period)


def wait_server_shutdown(nova_client, server_id):
    """
    Wait server shutdown
    """
    _poll_for_status(nova_client, server_id, ['shutoff'])


def wait_server_snapshot(nova_client, server_id):
    """
    Wait server snapshot
    """
    task_state_field = "OS-EXT-STS:task_state"
    server = nova_client.servers.get(server_id)
    if hasattr(server, task_state_field):
        _poll_for_status(nova_client, server.id, [None, '-', ''],
                         status_field=task_state_field)


def get_flavor(nova_client, flavor_name):
    """
    Get the flavor
    """
    for flavor in nova_client.flavors.list():
        if flavor.name == flavor_name:
            return flavor
    return None
