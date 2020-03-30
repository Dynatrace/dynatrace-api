from tests import Test, TestStep, TestArgument

from datetime import datetime
import dns.resolver


class DnsTest(Test):
    """
    DNS test class.

    It measures the time needed for an authoritative name server to give an
    answer to a DNS query.
    """

    TEST_NAME = "dns"

    HOSTNAME_FLAG = "hostname"

    TEST_ARGUMENTS = [
        TestArgument(
            flag_names=['--' + HOSTNAME_FLAG],
            flag_args={
                'required': True,
                'nargs': 1,
                'metavar': 'HOSTNAME',
                'help': 'Address of a host to test'
            }
        )
    ]

    def __init__(self, args):
        """Create a DnsTest class instance.

        Extends the base class __init__() method.
        Args:
            args: Command line arguments in dict form
        """
        super().__init__()

        self.resolver = None  # Internal DNS resolver.
        self.hostname = args[self.HOSTNAME_FLAG][0]
        self._configure()

    def _configure(self):
        """Configure the DnsTest class instance."""

        self.steps.append(self.CheckDnsStep(self.hostname))
        self.dynatrace_test_name = 'DNS query test for {}'.format(self.hostname)

    class CheckDnsStep(TestStep):
        """DNS test step class."""

        def __init__(self, hostname):
            """Create CheckDnsStep class instance.

            Args:
                hostname: hostname for which dns lookup will be performed
            """
            test_step_name = 'Check authoritative name server response for {}'.format(hostname)
            super().__init__(test_step_name)

            self.hostname = hostname

        def __call__(self):
            """Execute the test step.

            Overrides the base class implementation.
            """
            self.set_started()

            self.resolver = dns.resolver.Resolver()
            self.resolver.nameserver = self._get_nameservers()
            self.logger.info('Querying name servers of {} started'.format(self.hostname))
            start_time = datetime.now()
            query_result = self.resolver.query(self.hostname, 'A')
            end_time = datetime.now()
            self.set_passed()
            self.logger.info('Querying name servers of {} finished successfully; found IPs: {}'
                             .format(self.hostname, ', '.join([str(rdata) for rdata in query_result])))
            self.duration = end_time - start_time

        def _get_nameservers(self):
            """Retrieve authoritative name servers for a domain.


            It sets up internal DNS resolver object so that it uses
            authoritative name servers only to query for DNS records
            pertaining the hostname of interest. For internal use
            only.
            """
            nameservers_found = False
            query_data = None
            domains = self.hostname.split('.')
            domain_name = str('.'.join(domains))

            while not nameservers_found and domain_name:
                try:
                    self.logger.info('Looking for name servers for {}'.format(domain_name))
                    query_data = dns.resolver.query(domain_name, 'NS')
                    nameservers_found = True
                except dns.resolver.NoAnswer as e:
                    self.logger.info('NS record not found for domain {domain} ({message}), trying parent domain'
                                     .format(domain=domain_name, message=str(e)))
                    domain_name = '.'.join(domain_name.split('.')[1:])
            if not nameservers_found:
                raise RuntimeError('Could not find name servers for {}'.format(self.hostname))

            nameservers = [query_data_element.to_text() for query_data_element in query_data]
            self.logger.info('Name servers for {} found: {}'.format(self.hostname, ', '.join(nameservers)))

            return nameservers
