from reporting.api_constants import ApiConstants

from datetime import datetime
import requests
import logging
import hashlib


class ResultsReporter:
    """A class responsible for sending test results to Dynatrace."""

    def __init__(self, api_url, api_token, schedule_interval, location_id,
                 location_name, engine_name='Custom Python script'):
        """
        Initialize ResultsReporter class.

        Args:
            api_url: Dynatrace API endpoint FQDN for sending test results
            api_token: Dynatrace API token
            schedule_interval: Seconds between
            location_id: ID of location tests are run on
            location_name: Name of used location tests are run on

            engine_name: Name of the engine displayed in UI (default 'Custom Python script')
        """

        self.logger = logging.getLogger(__name__)
        self.api_url = api_url
        self.api_token = api_token
        self.schedule_interval = schedule_interval
        self.location_id = location_id
        self.location_name = location_name
        self.engine_name = engine_name

    def send_result_of(self, test):
        """
        Send test result to Dynatrace

        Args:
            test: Test object which result should be sent
        """

        result_report = self._prepare_report(test)
        test_result_consumer_endpoint = "{api_url}?Api-Token={api_token}".format(
            api_url=self.api_url, api_token=self.api_token
        )

        try:
            self.logger.info("Sending test results to {api_url} started".format(api_url=self.api_url))
            response = requests.post(test_result_consumer_endpoint, json=result_report)
            if not response.ok:
                raise RuntimeError(
                    "HTTP status code: {code}, message: {response_body}"
                    .format(code=response.status_code, response_body=response.text)
                )
            self.logger.info("Sending test results to {api_url} finished".format(api_url=self.api_url))

        except Exception as e:
            self.logger.error(
                "Error while sending results to {api_url}: {message}"
                .format(api_url=self.api_url, message=str(e))
            )

    def _prepare_report(self, test):
        """Prepare a valid Dynatrace API call.

        For internal use only.
        """
        result_report = dict()

        result_report[ApiConstants.MESSAGE_TIMESTAMP] = self._convert_datetime_to_milliseconds(datetime.now())
        result_report[ApiConstants.SYNTHETIC_ENGINE_NAME] = self.engine_name
        result_report[
            ApiConstants.SYNTHETIC_ENGINE_ICON_URL] = "http://assets.dynatrace.com/global/icons/cpu_processor.png"
        result_report[ApiConstants.LOCATIONS] = self._get_locations()
        result_report[ApiConstants.TESTS] = self._get_tests(test)
        result_report[ApiConstants.TEST_RESULTS] = self._get_test_results(test)

        return result_report

    def _get_locations(self):
        """Return a representation of a list of test locations.

        For internal use only.
        """
        locations = [{ApiConstants.Locations.ID: str(self.location_id),
                      ApiConstants.Locations.NAME: self.location_name}]

        return locations

    def _get_tests(self, test):
        """Return a representation of a list of tests.

        For internal use only.
        """
        tests = [{
            ApiConstants.Tests.ID: self._make_test_id(test),
            ApiConstants.Tests.TITLE: test.dynatrace_test_name,
            ApiConstants.Tests.TEST_SETUP: self.engine_name,
            ApiConstants.Tests.ENABLED: True,
            ApiConstants.Tests.LOCATIONS: self._get_test_locations(),
            ApiConstants.Tests.STEPS: self._get_test_steps(test),
            ApiConstants.Tests.SCHEDULE_INTERVAL_IN_SECONDS: self.schedule_interval
        }]

        return tests

    def _get_test_locations(self):
        """Return a representation of a list of test locations.

        For internal use only.
        """
        locations = [{
            ApiConstants.Tests.Locations.ID: self.location_id,
            ApiConstants.Tests.Locations.ENABLED: True
        }]

        return locations

    def _get_test_steps(self, test):
        """Return a representation of a list of test steps.

        For internal use only.
        """
        steps = [{
            ApiConstants.Tests.Steps.ID: step_number,
            ApiConstants.Tests.Steps.TITLE: step.name
        } for step_number, step in enumerate(test.steps, 1)]

        return steps

    def _get_test_results(self, test):
        """Return a representation of a list of test results.

        For internal use only.
        """
        test_results = [{
            ApiConstants.TestResults.ID: self._make_test_id(test),
            ApiConstants.TestResults.SCHEDULE_INTERVAL_IN_SECONDS: self.schedule_interval,
            ApiConstants.TestResults.TOTAL_STEP_COUNT: 1,
            ApiConstants.TestResults.LOCATION_RESULTS: self._get_location_results(test)
        }]

        return test_results

    def _get_location_results(self, test):
        """Return a representation of a list of test location results.

        For internal use only.
        """
        location_results = [{
            ApiConstants.TestResults.LocationResults.ID: self.location_id,
            ApiConstants.TestResults.LocationResults.START_TIMESTAMP:
                self._convert_datetime_to_milliseconds(test.start_timestamp),
            ApiConstants.TestResults.LocationResults.SUCCESS: all([step.successful for step in test.steps]),
            ApiConstants.TestResults.LocationResults.STEP_RESULTS: self._get_step_results(test)
        }]

        return location_results

    def _get_step_results(self, test):
        """Return a representation of a list of step results.

        For internal use only.
        """
        step_results = [{
            ApiConstants.TestResults.LocationResults.StepResults.ID: step_number,
            ApiConstants.TestResults.LocationResults.StepResults.START_TIMESTAMP:
                self._convert_datetime_to_milliseconds(step.start_timestamp) if step.start_timestamp is not None
                else self._convert_datetime_to_milliseconds(test.start_timestamp),
            ApiConstants.TestResults.LocationResults.StepResults.RESPONSE_TIME_MILLIS: int(
                step.duration.total_seconds() * 1000) if step.duration is not None else None
        } for step_number, step in enumerate(test.steps, 1)]

        return step_results

    def _convert_datetime_to_milliseconds(self, timestamp):
        """Convert a timestamp in seconds to an integer timestamp in milliseconds.

        For internal use only.
        """
        return int(timestamp.timestamp() * 1000)

    def _make_test_id(self, test):
        return hashlib.sha256(str.encode('{title}'.format(title=test.dynatrace_test_name))).hexdigest()
