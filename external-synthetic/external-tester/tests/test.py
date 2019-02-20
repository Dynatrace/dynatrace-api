from datetime import datetime

import logging


class Test:
    """
    A base class for test definitions.

    To create a concrete test one should derive this class and fill its 'steps'
    field, which contains TestStep objects that encapsulate test step logic.
    """

    TEST_ARGUMENTS = []
    """
    Additional arguments that can be utilized by subclasses.

    If a subclass of the Test class needs to introduce additional parameters
    (e.g. testing a database may need a username and password), they should be
    added to this list as instances of TestArgument class.
    """

    TEST_NAME = None
    """
    Test name is used to identify tests. Test names MUST be unique.

    This tool tries to select all subclasses of this class located in tests/testdefinitions module
    as available tests. Without TEST_NAME defined test will not be selected as available test.
    When --help flag is set, program will list all available tests and their test names.
    """

    TEST_HELP_DESCRIPTION = None
    """Description added to help message (optional)."""

    def __init__(self):
        """
        Create a Test class instance.
        """
        self.logger = logging.getLogger(__name__)
        """Test execution logger object."""
        self.dynatrace_test_name = None
        """Test name that will appear in Dynatrace."""
        self.steps = []
        """List of test step objects of type TestStep."""
        self.successful = False
        """Test execution pass/fail status."""
        self.start_timestamp = None
        """Test execution start timestamp."""

    def run(self):
        """Run the test."""
        self.start_timestamp = datetime.now()
        try:
            for step in self.steps:
                step()
                if not step.successful:
                    self.logger.error("Test failed, error in step: '{}' ".format(step.name))
                    break
            self.successful = True
        except Exception as e:
            self.logger.error('Test execution error: {message}'.format(message=str(e)))
