# Third-Party synthetic example tester

This is a simple python application that periodically executes user defined tests
and sends results to Dynatrace cluster with few examples included.
This script should be used as an example.
If you're not familiar with Dynatrace API check out the
[documentation](https://www.dynatrace.com/support/help/dynatrace-api/ "Dynatrace API"),
especially the
[third-party synthetic call](https://www.dynatrace.com/support/help/dynatrace-api/environment/synthetic-api/external-synthetic-api/)
so you can build your own tests the way you need it.

## Getting started
These instructions will get you a copy of the project up and running on a windows or linux machine.

### Prerequisites
* Python3 runtime (with pip): [Download](https://www.python.org/downloads/)
* Dynatrace Tenant: [Get your Saas Trial Tenant](https://www.dynatrace.com/trial/)

### Installing
To install the tester in your machine you only need to clone the repository
and then download the python dependencies with pip.

#### Clone the Dynatrace api repository

    git clone https://github.com/Dynatrace/dynatrace-api.git

#### Navigate to tool location

    cd dynatrace-api/third-party-synthetic/third-party-tester

#### Download and install the requirements with pip
To install python project dependencies simply run the following command:

    pip install -r requirements.txt

##### Or run installer
Alternatively tester can be installed/build by running following command in the terminal:

    ./setup.py install/build

Bash completion can be enabled by running:

    eval "$(register-python-argcomplete synthetic-third-party-tester)"

or by globally activating `argcomplete` for python scripts.

    activate-global-python-argcomplete


### Running tests
Tester checks which tests are available by looking for all subclasses of
[Test](tests/test.py) class. Each such subclass is identified by its `TEST_NAME` field.
To list all available tests simply run:

    ./synthetic-third-party-tester --help

Running specific test:

    ./synthetic-third-party-tester test-name --test-args...

To get more information about specific test use `--help` flag.

    ./synthetic-third-party-tester test-name --help

Every test will require those basic parameters:

* _interval_ - time in seconds between test executions

* _locationId_ - Id of the location tests will be executed from

* _locationName_ - Name of the location tests will be executed from

* _dynatraceUrl_ - Base Dynatrace communication url for tenant
(SaaS example: https://{TENANT_ID}.live.dynatrace.com).

* _apiToken_ - Token used to authenticate request. Make sure ***Create and configure
synthetic monitors*** flag is enabled for the token.

Depending on type of test, setting more parameters may be required.


### Config file
Instead of supplying arguments by command line they can be set in config file.
Config file can be writen in _ini_ or _yaml_ style.
Each argument starting with double dash '--' can be set in config file.
Command line values supersede those from config file. Example config.ini file:

```
; Interval in seconds between test executions
interval = 10

; Dynatrace tenant URL
dynatraceUrl = https://********.live.dynatrace.com

; Api token for authentication.
apiToken = ********

; Location ID and name from which tests will run
locationId = 1
locationName = Custom location

; Example list argument (arg which has action='append' or nargs='+')
listArg = [val_1, val_2, val_3]
```

Check out [ConfigArgParse](https://pypi.org/project/ConfigArgParse/) documentation for
full config syntax.

### Create your own test
The easiest way to make your own test is to copy [example_test](examples/file_exists_test.py)
into [testdefinitions](tests/testdefinitions) folder and edit it as described in the comments.

In more detail, to create your own test you'll need to:

 * Create a subclass of [Test](tests/test.py) base class and save it in
 [testdefinitions](tests/testdefinitions) folder.

 * Set `TEST_NAME` and make sure its value is unique.

 * Set other values (`TEST_HELP_DESCRIPTION`, `dynatrace_test_name`).

 * Add additional argument to your test append [TestArgument](tests/test_argument.py)
 instance to `TEST_ARGUMENTS` list. This class just holds parameters for `argparse.add_argument`
 method so check its [documentation](https://docs.python.org/3/library/argparse.html#the-add-argument-method)
 for more information about them.

 * Configure steps for your test. To do so create subclass of [TestStep](tests/test_step.py)
 base class for each step. Set `test_step_name` values and `__call__` method
 and populate `steps` list in test class.

New test should be accessible by running `./synthetic-third-party-tester {TEST_NAME}`.
Test specific help message will be automatically generated.

### Exit codes
Tester will return exit code `1` when two different test definitions have the same `TEST_NAME`
defined or when `ping_test` on unix system is not executed by `root`.

When configured correctly `synthetic-third-party-tester` will lunch defined test in infinite loop
at specified intervals. Exceptions raised by executed test will be caught and logged.
Main loop will only stop on user request (eg. by `SIGTERM`).

### Project structure & description

```
third-party-tester
├── examples                        Folder with example test.
│   └── file_exists_test.py         Example test.
│
├── reporting                       Folder with classes dedicated to sending results.
│   ├── api_constants.py            Python representation of third-party test api.
│   └── resultsreporter.py          Class responsible for sending test reports.
│
├── syntester                       Folder with main application class.
│   └── syntester.py                Main application class.
│
├── tests                           Folder with classes dedicated to running tests.
│   ├── test_argument.py            Class representing additional test arguments.
│   ├── test.py                     Base Test class. All tests must be a subclass of it.
│   └── test_step.py                Base step class. Represents one step in test.
│   └── testdefinitions             Folder containing specific test definitions.
│       ├── db_test.py              Test class for checking database connection.
│       ├── dns_test.py             Test class for checking dns lookup.
│       ├── ping_test.py            Test class for checking ping response from host.
│       └── tcp_test.py             Test class for checking tcp connection to host.
│
├── config.ini                      Default configuration file.
├── LICENSE.md                      License.
├── README.md                       This readme file.
├── requirements.txt                Python project dependencies.
├── setup.py                        Setup script.
└── synthetic-third-party-tester       Main application
```

## License
This project is licensed under the Apache License - see the [LICENSE](LICENSE.md) file for details
