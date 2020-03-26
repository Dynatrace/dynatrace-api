from datetime import datetime

import logging


class TestStep:
    """Representation of a single test step.

    This class provides the basic block for a test. Each test can consist of
    multiple steps with each step being represented by instances of this class.
    The test step logic should be contained in the __call__ method (without
    parameters) - see method documentation for more details.
    """

    def __init__(self, name):
        self.name = name
        """Test step name."""
        self.start_timestamp = None
        """Test step start timestamp as datetime.datetime object."""
        self.duration = None
        """Test step duration as datetime.timedelta object."""
        self.successful = False
        """Boolean flag representing test step execution status."""
        self.logger = logging.getLogger(__name__)
        """Test step logger."""

    def __call__(self):
        """Execute the test step.

        Derived classes should override this method and all test step logic
        should be placed inside it. A client programmer must manually set the
        test step duration time and mark it is successful.
        """
        raise NotImplementedError('Class {class_name} does not implement __call__() method'
                                  .format(class_name=type(self).__name__))

    def set_passed(self):
        """Mark the step as passed.

        Convenience method.
        """
        self.successful = True

    def set_failed(self):
        """Mark the step as failed.

        Convenience method.
        """
        self.successful = False

    def set_started(self):
        """Mark the start of the test.

        Convenience method.
        """
        self.start_timestamp = datetime.now()
