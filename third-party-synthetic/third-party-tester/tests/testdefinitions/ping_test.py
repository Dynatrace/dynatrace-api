import os
from tests import Test, TestStep, TestArgument
from datetime import timedelta

import pings


class PingTest(Test):
    """Ping test class.

    It measures the time needed for a single ICMP probe to check server
    availability.
    """

    TEST_NAME = 'ping'

    TEST_HELP_DESCRIPTION = "Test if given host responds to ping message and measures response time"

    HOSTNAME_FLAG = 'hostname'
    TEST_ARGUMENTS = [
        TestArgument(
            flag_names=['--' + HOSTNAME_FLAG],
            flag_args={
                'required': True,
                'nargs': 1,
                'metavar': HOSTNAME_FLAG,
                'help': 'Address of a host to test'
            }
        ),
    ]

    def __init__(self, args):
        """Create a PingTest class instance.

        Extends the base class __init__() method.
        Args:
            args: Command line arguments in dict form
        """

        super().__init__()

        self.hostname = args[self.HOSTNAME_FLAG][0]
        self.dynatrace_test_name = 'ICMP ping test for {hostname}'.format(hostname=self.hostname)
        self.steps.append(PingTest.PingStep(self.hostname))

    class PingStep(TestStep):
        """ICMP ping test class."""

        def __init__(self, hostname):
            """Create PingStep class instance.

            Args:
                hostname: IP or hostname of the host to ping
            """

            test_step_name = 'ICMP ping test for {hostname}'.format(hostname=hostname)
            super().__init__(test_step_name)

            # Check if running as root at posix systems
            if os.name != "nt" and os.geteuid() != 0:
                self.logger.error(
                    'Operation not permitted - Note that ICMP messages '
                    'can only be sent from processes running as root.'
                )
                exit(1)

            self.pinger = pings.Ping()
            self.hostname = hostname

        def __call__(self):
            """Execute the test step.

            Overrides the base class implementation.
            """
            self.logger.info("Sending ICMP probe to {}".format(self.hostname))

            self.set_started()

            ping_response = self.pinger.ping(self.hostname)

            # Check if ICMP message was successfully received
            if ping_response.ret_code != pings.consts.SUCCESS:
                self.logger.error("ICMP probing failed")
                # Fail test by returning without calling self.set_passed()
                return

            # Only one ICMP probe is sent, so min time is the same as max and avg times
            self.duration = timedelta(milliseconds=ping_response.min_rtt)
            self.set_passed()
            self.logger.info("{} responded successfully".format(self.hostname))
