"""
Tool to configure flows for Kubernetes Usecases.
"""

from tools import tasks
from conf import settings as S

class ExtVswitchFlowCtl(tasks.Process):
    """
    Virtual Switch Flow Control
    """
    def __init__(self, sw_type):
        super().__init__()
        self.swtype = sw_type
        self._vpp_ctl = ['sudo', S.getValue('EXT_VSWITCH_VPP_FLOWCTL')]
        self._ovs_ctl = ['sudo', S.getValue('EXT_VSWITCH_OVS_FLOWCTL')]

    def get_vppinterfaces(self):
        ifargs = ['show', 'interface']
        output = run_vppctl(ifargs)
        ifaces = output.split('\n')
        pifaces = []
        vifaces = []
        for iface in ifaces:
            name = iface.split()[0]
            index = iface.split()[0]
            if 'Name' in name or 'local' in name:
                continue
            if 'Ethernet' in name:
                pifaces.append(name)
            if 'memif' in name:
                vifaces.append(name)
        assert len(vifaces) == 2 or len(vifaces) == 4
        assert len(pifaces) == 2
        assert vifaces[0][:-1] in vifaces[1][:-1] 
        assert pifaces[0][:-1] in pifaces[1][:-1] 
        if len(vifaces) == 4:
            assert vifaces(2)[:-1] in vifaces(3)[:1]
        return pifaces,vifaces
        

    def add_connections(self):
        if 'VPP' in S.getValue('EXT_VSWITCH'):
            add_vpp_xconnect()
        else
            add_ovs_xconnect()


    def add_ovs_xconnect(self):
        entries = [['--timeout', '10', '-o', 'OpenFlow13', 'add-flow',
                    S.getValue('EXT_VSWITCH_OVS_BRIDGE'),
                    'in_port=1,idle_timeout=0,action=output:3'],
                   ['--timeout', '10', '-o', 'OpenFlow13', 'add-flow',
                    S.getValue('EXT_VSWITCH_OVS_BRIDGE'),
                    'in_port=3,idle_timeout=0,action=output:1'],
                   ['--timeout', '10', '-o', 'OpenFlow13', 'add-flow',
                    S.getValue('EXT_VSWITCH_OVS_BRIDGE'),
                    'in_port=2,idle_timeout=0,action=output:4'],
                   ['--timeout', '10', '-o', 'OpenFlow13', 'add-flow',
                    S.getValue('EXT_VSWITCH_OVS_BRIDGE'),
                    'in_port=4,idle_timeout=0,action=output:2']]
        for entry in entries:
            run_ovsfctl(entry)
        

    def add_vpp_xconnect(self):
        pifaces, vifaces = get_vpp_interfaces()
        if len(vifaces) == 2:
            entries = [['test', 'l2patch', 'rx',
                        pifaces[0], 'tx', vifaces[0]],
                       ['test', 'l2patch', 'rx',
                        vifaces[0], 'tx', pifaces[0]],
                       ['test', 'l2patch', 'rx',
                        pifaces[1], 'tx', vifaces[1]],
                       ['test', 'l2patch', 'rx',
                        vifaces[1], 'tx', pifaces[1]]]
        elif len(vifaces) == 4:
            entries = [['test', 'l2patch', 'rx',
                        pifaces[0], 'tx', vifaces[0]],
                       ['test', 'l2patch', 'rx',
                        vifaces[0], 'tx', pifaces[0]],
                       ['test', 'l2patch', 'rx',
                        vifaces[1], 'tx', vifaces[2]],
                       ['test', 'l2patch', 'rx',
                        vifaces[2], 'tx', vifaces[2]],
                       ['test', 'l2patch', 'rx',
                        pifaces[1], 'tx', vifaces[3]],
                       ['test', 'l2patch', 'rx',
                        vifaces[3], 'tx', pifaces[1]]]

        for entry in entries:
            run_vppctl(entry)
                    

    def run_ovsfctl(self, args, check_error=False):
        """Run ``ovs-ofctl`` with supplied arguments.

        :param args: Arguments to pass to ``vppctl``
        :param check_error: Throw exception on error

        :return: None
        """
        cmd = self._ovs_ctl + args
        return tasks.run_task(cmd, self._logger,
                              'Running ovs-ofctl...',
                              check_error)


    def run_vppctl(self, args, check_error=False):
        """Run ``vppctl`` with supplied arguments.

        :param args: Arguments to pass to ``vppctl``
        :param check_error: Throw exception on error

        :return: None
        """
        cmd = self._vpp_ctl + args
        return tasks.run_task(cmd, self._logger,
                              'Running vppctl...',
                              check_error)

