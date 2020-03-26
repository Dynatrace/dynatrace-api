from tests import Test, TestArgument, TestStep

from datetime import datetime
from pathlib import Path


class FileExistsTest(Test):
    """
    Simple example test class

    This example test (if added to tests/testdefinitions/ package)
    will check if file exists at given path.
    """

    # TEST_NAME must be unique and defined for test to be available
    TEST_NAME = 'example-test'

    # Description added to command line help message for this test
    TEST_HELP_DESCRIPTION = "This is example test. "

    # Flag used to set additional argument
    FILE_PATH_FLAG = 'filepath'

    # Definitions of additional arguments required by test
    # To add test specific arguments append TestArgument instances to this list
    TEST_ARGUMENTS = [
        TestArgument(
            flag_names=['--' + FILE_PATH_FLAG],
            flag_args={
                'required': True,
                'nargs': 1,
                'metavar': 'PATH',
                'help': "Path to the file whose existence will be tested."
            }
        ),
    ]

    def __init__(self, args):
        """Create an FileExistsTest class instance.

        Args:
            args: Command line arguments in dict form
        """

        super().__init__()

        # Parse test specific flags from supplied arguments
        file_path = args[self.FILE_PATH_FLAG][0]

        # Dynatrace test name shows up in UI as synthetic monitor name so make sure it is meaningful
        self.dynatrace_test_name = 'Example test. Checks if file exists at: {}'.format(file_path)

        # Append steps the test consists of
        self.steps.append(self.FileExistsTestStep(file_path))

    class FileExistsTestStep(TestStep):
        """
        FileExistsTest test step class.

        TestStep defines one step preformed in test.
        Tests can contain many steps.
        """

        def __init__(self, file_path):
            """
            Create FileExistsTest class instance.

            Args:
                file_path: Path to file which test check if exists
            """

            # Set up step name, it will show up in monitor UI
            test_step_name = 'Checking if file exists at: {}'.format(file_path)
            super().__init__(test_step_name)

            self.file_path = file_path

        def __call__(self):
            """
            Execute the test step.

            Overrides the base class implementation.
            """

            # Mark that step execution has started
            self.set_started()
            self.logger.info('Checking if file exists at: {}'.format(self.file_path))

            # If step raises Exception it will be caught and logged in Test.run method

            start_time = datetime.now()

            # Check if file exists
            file = Path(self.file_path)
            is_file = file.is_file()
            end_time = datetime.now()

            if is_file:
                # If file exists set step as successful
                self.set_passed()
            else:
                self.set_failed()

            # Set up measured duration of the test step
            self.duration = end_time - start_time
