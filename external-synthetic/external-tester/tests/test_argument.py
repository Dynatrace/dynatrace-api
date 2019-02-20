class TestArgument:
    """Representation of a single test parameter.

    This class holds the same data as passed to add_argument method in the
    argparse.ArgumentParser class.
    """

    def __init__(self, flag_names, flag_args):
        """Create a TestParser class instance.

        Each parameter passed to this method is the same as a corresponding
        parameter to the argparse.ArgumentParser.add_argument() method.
        """

        self.flag_names = flag_names
        self.flag_args = flag_args
