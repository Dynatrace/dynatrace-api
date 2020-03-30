from tests import Test, TestStep, TestArgument
from datetime import datetime

import pymysql
import pymongo


class DbTest(Test):
    """
    Database connectivity test.

    Measures time needed to connect to a database and close connection.
    """

    TEST_NAME = 'db'

    TEST_HELP_DESCRIPTION = "Test connection to database (mysql or mongodb) with given credentials and " \
                            "measures time required to connect and disconnect."

    # Configuration flags
    HOSTNAME_FLAG = 'hostname'
    DATABASE_TYPE_FLAG = 'databaseType'
    ADDRESS_FLAG = 'address'
    USERNAME_FLAG = 'username'
    PASSWORD_FLAG = 'password'
    DATABASE_NAME_FLAG = 'databaseName'
    AUTH_SOURCE_FLAG = 'authSource'
    AUTH_MECHANISM_FLAG = 'authMechanism'

    # Constants
    MYSQL = 'mysql'
    MONGODB = 'mongodb'
    AUTH_MECHANISM_CHOICES = ('DEFAULT', 'MONGODB-CR', 'MONGODB-X509', 'GSSAPI', 'SCRAM-SHA-1', 'PLAIN')

    TEST_ARGUMENTS = [
        TestArgument(
            flag_names=['--' + HOSTNAME_FLAG],
            flag_args={
                'required': True,
                'nargs': 1,
                'metavar': 'HOSTNAME',
                'help': "Address of a host to test."
            }
        ),

        TestArgument(
            flag_names=['--' + DATABASE_TYPE_FLAG],
            flag_args={
                'required': True,
                'nargs': 1,
                'metavar': 'TYPE',
                'type': str,
                'choices': [MYSQL, MONGODB],
                'help': "Type of database to connect to: [ {} | {} ].".format(MYSQL, MONGODB)
            }
        ),

        TestArgument(
            flag_names=['--' + DATABASE_NAME_FLAG],
            flag_args={
                'nargs': 1,
                'metavar': 'NAME',
                'type': str,
                'help': "Database name."
            }
        ),

        TestArgument(
            flag_names=['--' + USERNAME_FLAG],
            flag_args={
                'nargs': 1,
                'metavar': 'USERNAME',
                'type': str,
                'help': "Database user."
            }
        ),

        TestArgument(
            flag_names=['--' + PASSWORD_FLAG],
            flag_args={
                'nargs': 1,
                'metavar': 'PASSWORD',
                'type': str,
                'help': "Database password."
            }
        ),

        TestArgument(
            flag_names=['--' + AUTH_SOURCE_FLAG],
            flag_args={
                'nargs': 1,
                'metavar': 'SOURCE',
                'type': str,
                'help': "MongoDB authentication source."
            }
        ),

        TestArgument(
            flag_names=['--' + AUTH_MECHANISM_FLAG],
            flag_args={
                'nargs': 1,
                'metavar': 'MECHANISM',
                'choices': AUTH_MECHANISM_CHOICES,
                'type': str,
                'help': "MongoDB authentication mechanism."
            }
        ),
    ]

    def __init__(self, args):
        """Create a DbTest class instance.

        Extends the base class __init__() method.
        Args:
            args: Command line arguments in dict form
        """
        super().__init__()

        self.database_type = None
        self.database_name = None
        self.username = None
        self.password = None
        self.auth_source = None
        self.auth_mechanism = None
        self.hostname = args[self.HOSTNAME_FLAG][0]

        self.configure(args)

    def configure(self, args):
        """Configure the DbTest class instance."""
        self.database_type = args[DbTest.DATABASE_TYPE_FLAG][0]
        self.database_name = args[DbTest.DATABASE_NAME_FLAG][0] if args[DbTest.DATABASE_NAME_FLAG] is not None else None
        self.username = args[DbTest.USERNAME_FLAG][0] if args[DbTest.USERNAME_FLAG] is not None else None
        self.password = args[DbTest.PASSWORD_FLAG][0] if args[DbTest.USERNAME_FLAG] is not None else None
        self.auth_source = args[DbTest.AUTH_SOURCE_FLAG][0] if args[DbTest.AUTH_SOURCE_FLAG] is not None else 'admin'
        self.auth_mechanism = args[DbTest.AUTH_MECHANISM_FLAG][0] if args[DbTest.AUTH_MECHANISM_FLAG] is not None\
            else None
        self.dynatrace_test_name = "Database (type: {}, name: {}) connectivity test for {}"\
                                   .format(self.database_type, self.database_name, self.hostname)
        test_step = DbTest.DatabaseConnectivityStep(
            self.hostname, self.database_type, self.username, self.password,
            self.database_name, self.auth_source, self.auth_mechanism
        )
        self.steps.append(test_step)

    class DatabaseConnectivityStep(TestStep):
        """Database test step class."""

        def __init__(self, hostname, database_type, username, password,
                     database_name, auth_source=None, auth_mechanism=None):
            """
            Create DatabaseConnectivityStep class instance.

            Args:
                hostname: database host name
                database_type: type of database to test
                username: database user username
                password: database user password
                database_name: database name

                auth_source: authentication source (for MongoDB only)
                auth_mechanism: authentication mechanism (for MongoDB only)
            """
            test_step_name = "Checking database connectivity for {hostname}, database type: {database_type}"\
                             .format(hostname=hostname, database_type=database_type)
            super().__init__(test_step_name)

            self.hostname = hostname
            self.username = username
            self.password = password
            self.database_name = database_name
            self.database_type = database_type
            self.auth_source = auth_source
            self.auth_mechanism = auth_mechanism

        def __call__(self):
            """Execute the test step.

            Overrides the base class implementation.
            """
            self.logger.info("Checking database connectivity for {}, database type: {}"
                             .format(self.hostname, self.database_type))
            self.logger.info("Establishing connection to database")

            self.set_started()

            if self.database_type == DbTest.MYSQL:
                self._do_run_mysql()
            elif self.database_type == DbTest.MONGODB:
                self._do_run_mongodb()
            else:
                raise RuntimeError("Unknown database type")

            self.duration = datetime.now() - self.start_timestamp

            self.logger.info("Connection to database closed")
            self.set_passed()

        def _do_run_mysql(self):
            """Run the step for MySQL.

            For internal use only.
            """

            connection = pymysql.connect(
                host=self.hostname,
                user=self.username,
                passwd=self.password,
                db=self.database_name
            )

            connection.close()

        def _do_run_mongodb(self):
            """Run the step for MongoDB.

            For internal use only.
            """

            auth = {} if self.auth_mechanism is None else {'authMechanism': self.auth_mechanism}
            client = pymongo.MongoClient(
                self.hostname,
                username=self.username,
                password=self.password,
                authSource=self.auth_source,
                **auth
            )
            client.server_info()
            client.close()
