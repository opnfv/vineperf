import select
import subprocess
import logging
import threading
import sys
import os
import locale
import time
from jinja2 import Environment, FileSystemLoader

CMD_PREFIX = 'cmd : '
VERBOSITY = 'info'
_logger = logging.getLogger(__name__)

def run_task(cmd, logger=_logger, msg=None, check_error=False):
    """Run task, report errors and log overall status.

    Run given task using ``subprocess.Popen``. Log the commands
    used and any errors generated. Prints stdout to screen if
    in verbose mode and returns it regardless. Prints stderr to
    screen always.

    :param cmd: Exact command to be executed
    :param logger: Logger to write details to
    :param msg: Message to be shown to user
    :param check_error: Throw exception on error

    :returns: (stdout, stderr)
    """
    def handle_error(exception):
        """Handle errors by logging and optionally raising an exception.
        """
        logger.error(
            'Unable to execute %(cmd)s. Exception: %(exception)s',
            {'cmd': ' '.join(cmd), 'exception': exception})
        if check_error:
            raise exception

    try:
        proc = subprocess.Popen(map(os.path.expanduser, cmd),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output = proc.communicate()[0].decode("utf-8")
    except OSError as ex:
        handle_error(ex)
    else:
       if proc.returncode:
            ex = subprocess.CalledProcessError(proc.returncode, cmd, stderr)
            handle_error(ex)
    return output

ifaces = []
sout = run_task(['/usr/bin/c_sample'])
if sout:
    for line in sout.split('\n'):
        if 'Path=' in line:
            print(line)
            field = line.split(' ')[-1].split('=')[-1]
            ifaces.append(field)
ifacesdir = {
    'if1' : ifaces[0],
    'if2' : ifaces[1]}

if len(ifaces) == 2:
    file_loader = FileSystemLoader('./')
    env = Environment(loader = file_loader)
    fileref = env.get_template('./trex_cfg.yaml.j2')
    renderedcon = fileref.render(data=ifacesdir)
    with open('/etc/trex_cfg.yaml', "w+") as fh:
        fh.write(renderedcon)
