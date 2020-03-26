class ApiConstants:
    """
    A holder of all Dynatrace API constants.

    The structure of this class represents the structure of Dynatrace API.
    Each static field represents a single property in the root of the API JSON,
    while nested classes represent nested objects and their properties.
    Please refer to Dynatrace API documentation for more details.
    """

    MESSAGE_TIMESTAMP = 'messageTimestamp'
    SYNTHETIC_ENGINE = 'syntheticEngine'
    SYNTHETIC_ENGINE_NAME = 'syntheticEngineName'
    SYNTHETIC_ENGINE_ICON_URL = 'syntheticEngineIconUrl'
    LOCATIONS = 'locations'
    TESTS = 'tests'
    TEST_RESULTS = 'testResults'

    class Locations:
        """Constants for .locations"""
        ID = 'id'
        NAME = 'name'

    class Tests:
        """Constants for .tests"""
        ID = 'id'
        TITLE = 'title'
        TEST_SETUP = 'testSetup'
        ENABLED = 'enabled'
        LOCATIONS = 'locations'
        STEPS = 'steps'
        SCHEDULE_INTERVAL_IN_SECONDS = 'scheduleIntervalInSeconds'

        class Locations:
            """Constants for .tests.locations"""
            ID = 'id'
            ENABLED = 'enabled'

        class Steps:
            """Constants for .tests.steps"""
            ID = 'id'
            TITLE = 'title'

    class TestResults:
        """Constants for .testResults"""
        ID = 'id'
        SCHEDULE_INTERVAL_IN_SECONDS = 'scheduleIntervalInSeconds'
        TOTAL_STEP_COUNT = 'totalStepCount'
        LOCATION_RESULTS = 'locationResults'

        class LocationResults:
            """Constants for .testResults.locationResults"""
            ID = 'id'
            START_TIMESTAMP = 'startTimestamp'
            SUCCESS = 'success'
            STEP_RESULTS = 'stepResults'

            class StepResults:
                """Constants for .testResults.locationResults.StepResults"""
                ID = 'id'
                START_TIMESTAMP = 'startTimestamp'
                RESPONSE_TIME_MILLIS = 'responseTimeMillis'
