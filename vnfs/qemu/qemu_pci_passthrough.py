# Copyright 2015-2017 Intel Corporation.
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

"""Automation of QEMU hypervisor with direct access to host NICs via
   PCI passthrough.
"""
import logging
import subprocess

from conf import settings as S
from vnfs.qemu.qemu import IVnfQemu
from tools import tasks
from tools.module_manager import ModuleManager

_MODULE_MANAGER = ModuleManager()

class QemuPciPassthrough(IVnfQemu):
    """
    Control an instance of QEMU with direct access to the host network devices
    """
    def __init__(self):
        """
        Initialization function.
        """
        super(QemuPciPassthrough, self).__init__()
        self._logger = logging.getLogger(__name__)
        self._host_nics = S.getValue('NICS')

        # in case of SRIOV and PCI passthrough we must ensure, that MAC addresses are swapped
        if S.getValue('SRIOV_ENABLED') and not self._testpmd_fwd_mode.startswith('mac'):
            self._logger.info("SRIOV detected, forwarding mode of testpmd was changed from '%s' to '%s'",
                              self._testpmd_fwd_mode, 'mac')
            self._testpmd_fwd_mode = 'mac'

        for nic in self._host_nics:
            self._cmd += ['-device', 'vfio-pci,host=' + nic['pci']]

    def start(self):
        """
        Start QEMU instance, bind host NICs to vfio-pci driver
        """
        # load vfio-pci
        _MODULE_MANAGER.insert_modules(['vfio-pci'])

        # bind every interface to vfio-pci driver
        try:
            nics_list = list(tmp_nic['pci'] for tmp_nic in self._host_nics)
            tasks.run_task(['sudo', S.getValue('TOOLS')['bind-tool'], '--bind=vfio-pci'] + nics_list,
                           self._logger, 'Binding NICs %s...' % nics_list, True)

        except subprocess.CalledProcessError:
            self._logger.error('Unable to bind NICs %s', self._host_nics)

        super(QemuPciPassthrough, self).start()

    def stop(self):
        """
        Stop QEMU instance, bind host NICs to the original driver
        """
        super(QemuPciPassthrough, self).stop()

        # bind original driver to every interface
        for nic in self._host_nics:
            if nic['driver']:
                try:
                    tasks.run_task(['sudo', S.getValue('TOOLS')['bind-tool'], '--bind=' + nic['driver'], nic['pci']],
                                   self._logger, 'Binding NIC %s...' % nic['pci'], True)

                except subprocess.CalledProcessError:
                    self._logger.error('Unable to bind NIC %s to driver %s', nic['pci'], nic['driver'])

        # unload vfio-pci driver
        _MODULE_MANAGER.remove_modules()
