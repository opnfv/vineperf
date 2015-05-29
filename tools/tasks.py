# Copyright 2015 Intel Corporation.
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

"""Task management helper functions and classes.
"""

import select
import subprocess
import logging
import pexpect
import threading
import sys
import os
import locale

from conf import settings


CMD_PREFIX = 'cmd : '
_MY_ENCODING = locale.getdefaultlocale()[1]

def _get_stdout():
    """Get stdout value for ``subprocess`` calls.
    """
    stdout = None

    if settings.getValue('VERBOSITY') != 'debug':
        stdout = open(os.devnull, 'wb')

    return stdout


def run_task(cmd, logger, msg=None, check_error=False):
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

    stdout = []
    stderr = []

    if msg:
        logger.info(msg)

    logger.debug('%s%s', CMD_PREFIX, ' '.join(cmd))

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

        while True:
            reads = [proc.stdout.fileno(), proc.stderr.fileno()]
            ret = select.select(reads, [], [])

            for file_d in ret[0]:
                if file_d == proc.stdout.fileno():
                    line = proc.stdout.readline()
                    if settings.getValue('VERBOSITY') == 'debug':
                        sys.stdout.write(line.decode(_MY_ENCODING))
                    stdout.append(line)
                if file_d == proc.stderr.fileno():
                    line = proc.stderr.readline()
                    sys.stderr.write(line.decode(_MY_ENCODING))
                    stderr.append(line)

            if proc.poll() is not None:
                break
    except OSError as ex:
        handle_error(ex)
    else:
        if proc.returncode:
            ex = subprocess.CalledProcessError(proc.returncode, cmd, stderr)
            handle_error(ex)

    return ('\n'.join(sout.decode(_MY_ENCODING).strip() for sout in stdout),
            ('\n'.join(sout.decode(_MY_ENCODING).strip() for sout in stderr)))

def run_background_task(cmd, logger, msg):
    """Run task in background and log when started.

    Run given task using ``subprocess.Popen``. Log the command
    used. Print stdout to screen if in verbose mode. Prints stderr
    to screen always.

    :param cmd: Exact command to be executed
    :param logger: Logger to write details to
    :param msg: Message to be shown to user

    :returns: Process PID
    """
    logger.info(msg)
    logger.debug('%s%s', CMD_PREFIX, ' '.join(cmd))

    proc = subprocess.Popen(cmd, stdout=_get_stdout(), bufsize=0)

    return proc.pid


def run_interactive_task(cmd, logger, msg):
    """Run a task interactively and log when started.

    Run given task using ``pexpect.spawn``. Log the command used.
    Performs neither validation of the process - if the process
    successfully started or is still running - nor killing of the
    process. The user must do both.

    :param cmd: Exact command to be executed
    :param logger: Logger to write details to
    :param msg: Message to be shown to user

    :returns: ``pexpect.child`` object
    """
    logger.info(msg)
    logger.debug('%s%s', CMD_PREFIX, cmd)
    child = pexpect.spawnu(cmd)

    if settings.getValue('VERBOSITY') == 'debug':
        child.logfile_read = sys.stdout

    return child


class Process(object):
    """Control an instance of a long-running process.

    This is basically a context-manager wrapper around the
    ``run_interactive_task`` function above (with some extra helper
    functions).
    """
    _cmd = None
    _child = None
    _logfile = None
    _logger = logging.getLogger(__name__)
    _expect = None
    _timeout = -1
    _proc_name = 'unnamed process'
    _relinquish_thread = None

    # context manager

    def __enter__(self):
        """Start process instance using context manager.
        """
        self.start()
        return self

    def __exit__(self, type_, value, traceback):
        """Shutdown process instance.
        """
        self.kill()

    # startup/shutdown

    def start(self):
        """Start process instance.
        """
        self._start_process()
        if self._timeout > 0:
            self._expect_process()

    def _start_process(self):
        """Start process instance.
        """
        cmd = ' '.join(settings.getValue('SHELL_CMD') +
                       ['"%s"' % ' '.join(self._cmd)])

        self._child = run_interactive_task(cmd, self._logger,
                                           'Starting %s...' % self._proc_name)
        self._child.logfile = open(self._logfile, 'w')

    def expect(self, msg, timeout=None):
        """Expect string from process.

        Expect string and die if not received.

        :param msg: String to expect.
        :param timeout: Time to wait for string.

        :returns: None
        """
        self._expect_process(msg, timeout)

    def _expect_process(self, msg=None, timeout=None):
        """Expect string from process.
        """
        if not msg:
            msg = self._expect
        if not timeout:
            timeout = self._timeout

        # we use exceptions rather than catching conditions in ``expect`` list
        # as we want to fail catastrophically after handling; there is likely
        # little we can do from within the scripts to fix issues such as
        # hugepages not being mounted
        try:
            self._child.expect([msg], timeout=timeout)
        except pexpect.EOF as exc:
            self._logger.critical(
                'An error occurred. Please check the logs (%s) for more'
                ' information. Exiting...', self._logfile)
            raise exc
        except pexpect.TIMEOUT as exc:
            self._logger.critical(
                'Failed to execute in \'%d\' seconds. Please check the logs'
                ' (%s) for more information. Exiting...',
                timeout, self._logfile)
            self.kill()
            raise exc
        except (Exception, KeyboardInterrupt) as exc:
            self._logger.critical('General exception raised. Exiting...')
            self.kill()
            raise exc

    def kill(self):
        """Kill process instance if it is alive.
        """
        if self._child and self._child.isalive():
            run_task(['sudo', 'kill', '-2', str(self._child.pid)],
                     self._logger)

            if self.is_relinquished():
                self._relinquish_thread.join()

        self._logger.info(
            'Log available at %s', self._logfile)

    def is_relinquished(self):
        """Returns True if process is relinquished.

        If relinquished the process is no longer controllable and can
        only be killed.

        :returns: True if process is relinquished, else False.
        """
        return self._relinquish_thread

    def is_running(self):
        """Returns True if process is running.

        :returns: True if process is running, else False
        """
        return self._child is not None

    def _affinitize_pid(self, core, pid):
        """Affinitize a process with ``pid`` to ``core``.

        :param core: Core to affinitize process to.
        :param pid: Process ID to affinitize.

        :returns: None
        """
        run_task(['sudo', 'taskset', '-c', '-p', str(core),
                  str(pid)],
                 self._logger)

    def affinitize(self, core):
        """Affinitize process to a specific ``core``.

        :param core: Core to affinitize process to.

        :returns: None
        """
        self._logger.info('Affinitizing process')

        if self._child and self._child.isalive():
            self._affinitize_pid(core, self._child.pid)

    class ContinueReadPrintLoop(threading.Thread):
        """Thread to read output from child and log.

        Taken from: https://github.com/pexpect/pexpect/issues/90
        """
        def __init__(self, child):
            self.child = child
            threading.Thread.__init__(self)

        def run(self):
            while True:
                try:
                    self.child.read_nonblocking()
                except (pexpect.EOF, pexpect.TIMEOUT):
                    break

    def relinquish(self):
        """Relinquish control of process.

        Give up control of application in order to ensure logging
        continues for the application. After relinquishing control it
        will no longer be possible to :func:`expect` anything.

        This works around an issue described here:

            https://github.com/pexpect/pexpect/issues/90

        It is hoped that future versions of pexpect will avoid this
        issue.
        """
        self._relinquish_thread = self.ContinueReadPrintLoop(self._child)
        self._relinquish_thread.start()


class CustomProcess(Process):
    """An sample implementation of ``Process``.

    This is essentially a more detailed version of the
    ``run_interactive_task`` function that checks for process execution
    and kills the process (assuming use of the context manager).
    """
    def __init__(self, cmd, timeout, logfile, expect, name):
        """Initialise process state.

        :param cmd: Command to execute.
        :param timeout: Time to wait for ``expect``.
        :param logfile: Path to logfile.
        :param expect: String to expect indicating startup. This is a
            regex and should be escaped as such.
        :param name: Name of process to use in logs.

        :returns: None
        """
        self._cmd = cmd
        self._logfile = logfile
        self._expect = expect
        self._proc_name = name
        self._timeout = timeout
