from configargparse import ArgParser
from tests import Test
from reporting import ResultsReporter
import argcomplete

# Used in SyntheticThirdPartyTester._configure_test_types when iterating through all test definitions
from tests.testdefinitions import *

import time
import logging
import sys


class SyntheticThirdPartyTester:
    """
    Application main class.

    Responsible for parsing command line arguments, scheduling test execution
    and test result sending
    """

    TEST_NAMES_TO_TEST_CLASSES = {}
    """
    A mapping between test names and test classes.

    All tests from tests.testdefinitions module subclassed from tests/test:Test class
    which have TEST_NAME defined will be added to this mapping.
    """

    # Command line flags
    TEST_TYPE_DEST = '__test_type__'
    INTERVAL_FLAG = 'interval'
    DYNATRACE_URL_FLAG = 'dynatraceUrl'
    API_TOKEN_FLAG = 'apiToken'

    LOCATION_ID_FLAG = 'locationId'
    LOCATION_NAME_FLAG = 'locationName'
    ENGINE_NAME_FLAG = 'engineName'

    LOG_LEVEL_FLAG = 'logLevel'
    LOG_LEVEL_CHOICES = ['debug', 'info', 'warning', 'error', 'critical']

    def __init__(self):
        """
        Create a SyntheticThirdPartyTester object.
        """
        self.logger = logging.getLogger(__name__)

        self._result_reporter = None
        self._test = None
        self._schedule_interval = None

        self._configure_test_types()

        parser = self._create_argparser()
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(1)
        args = vars(parser.parse_args())
        self._configure(args)

    def run(self):
        """
        Run the test and send test result to the cluster.

        This method runs an infinite loop that can be exited by issuing SIGINT
        to the process.
        """
        try:
            while True:
                self._test.run()
                self._result_reporter.send_result_of(self._test)
                time.sleep(self._schedule_interval)
        except KeyboardInterrupt:
            self.logger.info("Interrupt received, stopping.")

    def _configure(self, args):
        """ Configure the SyntheticThirdPartyTester class.

        For internal use only.
        """
        self._schedule_interval = args[self.INTERVAL_FLAG][0]
        self._result_reporter = self._create_reporter(args)
        self._test = self._create_test_object(args)

        # Set log level
        if self.LOG_LEVEL_FLAG in args and args[self.LOG_LEVEL_FLAG] is not None:
            log_lvl = args[self.LOG_LEVEL_FLAG][0]
            if log_lvl == 'debug':
                logging.getLogger().setLevel(logging.DEBUG)
            elif log_lvl == 'info':
                logging.getLogger().setLevel(logging.INFO)
            elif log_lvl == 'warning':
                logging.getLogger().setLevel(logging.WARNING)
            elif log_lvl == 'error':
                logging.getLogger().setLevel(logging.ERROR)
            elif log_lvl == 'critical':
                logging.getLogger().setLevel(logging.CRITICAL)

        self.logger.info(
            "Starting with configuration: (test: {}, interval: {}s, API endpoint URL: {})"
            .format(args[self.TEST_TYPE_DEST], args[self.INTERVAL_FLAG][0], args[self.DYNATRACE_URL_FLAG][0])
        )

    def _configure_test_types(self):
        """ Configure available test types.

        For internal use only
        """
        for test_class in Test.__subclasses__():
            if test_class.TEST_NAME is None:
                # If name is not defined test will not be available
                logging.warning("Test type has no name specified. Will not be runnable: {}".format(test_class))
            else:
                # Check for conflicting test names
                if test_class.TEST_NAME in self.TEST_NAMES_TO_TEST_CLASSES:
                    logging.error("Multiple tests with the same name: {} -> {}, {}".format(
                        test_class.TEST_NAME,
                        self.TEST_NAMES_TO_TEST_CLASSES[test_class.TEST_NAME],
                        test_class
                    ))
                    exit(1)

                self.TEST_NAMES_TO_TEST_CLASSES[test_class.TEST_NAME] = test_class

    def _create_reporter(self, args):
        """ Create a test result reporter.

        For internal use only.
        """

        api_url = args[self.DYNATRACE_URL_FLAG][0] + "/api/v1/synthetic/ext/tests"
        api_token = args[self.API_TOKEN_FLAG][0]
        schedule_interval = args[self.INTERVAL_FLAG][0]

        location_id = args[self.LOCATION_ID_FLAG][0]
        location_name = args[self.LOCATION_NAME_FLAG][0]
        engine_name = 'Custom Python script'

        if self.ENGINE_NAME_FLAG in args and args[self.ENGINE_NAME_FLAG] is not None:
            engine_name = args[self.ENGINE_NAME_FLAG][0]

        return ResultsReporter(api_url, api_token, schedule_interval, location_id, location_name, engine_name)

    def _create_test_object(self, args):
        """ Create a test class object.

        For internal use only.
        """

        test_type = args[self.TEST_TYPE_DEST]
        test_class = self.TEST_NAMES_TO_TEST_CLASSES[test_type]
        return test_class(args)

    def _create_argparser(self):
        """ Create argument parser.

        For internal use only.
        """

        parser = ArgParser(
            description="Dynatrace third-party test utility.",
            default_config_files=['./config.ini'],
            add_config_file_help=False
        )

        self._create_subparsers(parser)
        argcomplete.autocomplete(parser)
        return parser

    def _create_subparsers(self, parser):
        """ Create subparsers for all available test types.

        For internal use only.
        """

        command_parsers = parser.add_subparsers(help="Type of test to execute", dest=self.TEST_TYPE_DEST)
        for test_name, test_class in self.TEST_NAMES_TO_TEST_CLASSES.items():
            test_type_parser = command_parsers.add_parser(
                test_name,
                description=test_class.TEST_HELP_DESCRIPTION,
                add_config_file_help=False,
                allow_abbrev=False
            )

            # Add common arguments
            required_args = test_type_parser.add_argument_group("required arguments")
            self._add_common_arguments(test_type_parser, required_args)

            # Add test specific arguments
            for test_argument in test_class.TEST_ARGUMENTS:
                if 'required' in test_argument.flag_args and test_argument.flag_args['required']:
                    required_args.add_argument(*test_argument.flag_names, **test_argument.flag_args)
                else:
                    test_type_parser.add_argument(*test_argument.flag_names, **test_argument.flag_args)

    def _add_common_arguments(self, sparser, required_args):
        """ Add common arguments to sub-parser.

        For internal use only.
        """

        # Add optional arguments
        sparser.add_argument("-c", "-config", is_config_file=True, help="Config file path")
        sparser.add_argument(
            "--{}".format(self.LOG_LEVEL_FLAG),
            nargs=1,
            type=str,
            choices=self.LOG_LEVEL_CHOICES,
            help="Log level for logger (default: info)."
        )
        sparser.add_argument(
            "--{}".format(self.ENGINE_NAME_FLAG),
            nargs=1,
            metavar='NAME',
            type=str,
            help="Engine name used in test report (default: 'Custom python script')."
        )

        # Add required arguments
        required_args.add_argument(
            "--{}".format(self.LOCATION_ID_FLAG),
            required=True,
            nargs=1,
            metavar='N',
            type=int,
            help="ID of the location from which the test is performed."
        )
        required_args.add_argument(
            "--{}".format(self.LOCATION_NAME_FLAG),
            required=True,
            nargs=1,
            metavar='NAME',
            type=str,
            help="Name of the location from which the test is performed."
        )
        required_args.add_argument(
            "--{}".format(self.INTERVAL_FLAG),
            required=True,
            nargs=1,
            metavar='N',
            type=float,
            help="Interval at which the test should run in seconds."
        )
        required_args.add_argument(
            "--{}".format(self.DYNATRACE_URL_FLAG),
            required=True,
            nargs=1,
            metavar='URL',
            type=str,
            help="Base communication url for tenant (SaaS eg. 'https://{TENANT_ID}.live.dynatrace.com')."
        )
        required_args.add_argument(
            "--{}".format(self.API_TOKEN_FLAG),
            required=True,
            nargs=1,
            metavar='TOKEN',
            type=str,
            help="Dynatrace API authentication token."
        )
