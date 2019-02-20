from tests import Test, TestArgument, TestStep

from datetime import datetime
import socket


class TcpTest(Test):
    """
    TCP socket connection test class.

    It measures time needed to establish a TCP socket connection to a remote
    host and close it without actually sending any data.
    """

    TEST_NAME = 'tcp'
    HOSTNAME_FLAG = 'hostname'
    TIMEOUT_FLAG = 'timeout'

    TEST_ARGUMENTS = [
        TestArgument(
            flag_names=['--' + HOSTNAME_FLAG],
            flag_args={
                'required': True,
                'nargs': 1,
                'metavar': 'HOSTNAME',
                'help': "Address of a host to test in format: 'hostname:port'"
            }
        ),

        TestArgument(
            flag_names=['--' + TIMEOUT_FLAG],
            flag_args={
                'nargs': 1,
                'type': float,
                'metavar': 'N',
                'help': "Set timeout in seconds (default: 1.0)"
            }
        ),
    ]

    def __init__(self, args):
        """Create a TcpTest class instance.

        Extends the base class __init__() method.
        Args:
            args: Command line arguments in dict form
        """
        super().__init__()

        self.hostname = args[self.HOSTNAME_FLAG][0]
        self.dynatrace_test_name = "TCP socket connectivity test for {}".format(self.hostname)
        self._configure(args)

    def _configure(self, args):
        """Configure the TcpTest class instance.

        For internal use only.
        """
        try:
            (raw_hostname, raw_port) = self.hostname.split(':')
            raw_port = int(raw_port)
            timeout = args[self.TIMEOUT_FLAG][0] if args[self.TIMEOUT_FLAG] is not None else 1
            self.steps.append(TcpTest.TcpTestStep(raw_hostname, raw_port, timeout))
        except ValueError:
            raise RuntimeError("Hostname should be given as [hostname]:[port]")

    class TcpTestStep(TestStep):
        """TCP test step class.

        This class is capable of setting up a connection over a TCP socket.
        """

        def __init__(self, raw_hostname, raw_port, timeout):
            """Create TcpTestStep class instance.

            Args:
                raw_hostname: IP address or hostname of the host to connect to
                raw_port: port number on which the connection should be made
            """
            test_step_name = "Check if TCP connection can be made for host {}, port {}".format(raw_hostname, raw_port)
            super().__init__(test_step_name)

            self.raw_hostname = raw_hostname
            self.raw_port = raw_port
            self.timeout = timeout

        def __call__(self):
            """Execute the test step.

            Overrides the base class implementation.
            """
            self.logger.info("Establishing TCP socket connection to {}:{} (timeout {}s)"
                             .format(self.raw_hostname, self.raw_port, self.timeout))

            self.set_started()

            sock = socket.socket()
            sock.settimeout(self.timeout)
            sock.connect((self.raw_hostname, self.raw_port))
            sock.close()

            self.duration = datetime.now() - self.start_timestamp

            self.set_passed()
            self.logger.info("TCP socket connection successful, closing")
