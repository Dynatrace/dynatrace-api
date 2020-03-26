// DYNATRACE EDIT START

(function () {

    // -- Hard-coded aws/canary values --
    // The monitor display name in Dynatrace
    const canaryName = 'Test Canary name';
    // The location display name in Dynatrace
    const awsLocationName = 'US East (N. Virginia)';
    // To uniquely identify the location and generate links in Dynatrace back to the Canary
    const awsLocationId = 'us-east-1';
    // How often the canary is scheduled to run (so that Dynatrace can correctly detect and display availability)
    const canaryInterval = 3600;

    // -- DT API --
    // Dynatrace host name the results should be sent to
    const host = 'demo.dev.dynatracelabs.com';
    // Dynatrace api token with permissions to post monitor results
    const apiToken = '';
    // The dynatrace external-monitor endpoint
    const apiPath = '/api/v1/synthetic/ext/tests';

    // External monitor config
    const awsSyntheticEngineName = 'AWS CloudWatch';
    const awsSyntheticEngineIcon = 'https://raw.githubusercontent.com/Dynatrace/dynatrace-api/master/external-synthetic/aws-cloudwatch/cloud-watch-icon.png';

    // necessary imports
    const log = require('SyntheticsLogger');
    const synthetics = require('Synthetics');
    const https = require('https');

    // global (to us) variables that are accessed in various asynchronous handlers
    let page = undefined;
    let stepResults = [];
    let testResult = undefined;
    let responses = [];

    // Extend synthetics.getPage so we can get a reference to the page object
    const originalGetPage = synthetics.getPage;
    synthetics.getPage = async () => {
        page = await originalGetPage.call(synthetics);
        // Handle DomContentLoaded and Response events so we can get metrics and HTTP response codes
        initDtTestResultHandlers(page, stepResults, responses);
        return page;
    };

    // Extend the canary's main entry point, so that we can upload the test results when it's done
    const originalHandler = exports.handler;
    exports.handler = async () => {
        let originalHandlerError = undefined;
        let originalHandlerReturnValue = undefined;

        try {
            originalHandlerReturnValue = await originalHandler.call(exports);
        } catch (error) {
            log.info(`DT: Original handler threw an error (${error})`);
            originalHandlerError = error;
        } finally {
            // Prevent unexpected DT-specific errors from breaking the canary
            try {
                await sendResultsToDynatrace(!originalHandlerError);
            } catch (error) {
                log.error('DT: An unexpected error occured while building and posting exernal-monitor result to Dynatrace', error);
            }
        }

        if (originalHandlerError) {
            throw originalHandlerError;
        } else {
            return originalHandlerReturnValue;
        }
    }

    async function sendResultsToDynatrace(canaryWasSuccessful) {
        if (stepResults.length) {
            testResult = await buildDtTestResult(stepResults, canaryWasSuccessful);
            await postDtTestResult(testResult);
        } else {
            log.info('DT: No step results.')
        }
    }

    async function buildDtTestResult(stepResults, canaryWasSuccessful) {
        log.info('DT: Building external-monitor result');

        // Grab the current timestamp before we waste time on anything else
        const doneAt = new Date().getTime();

        const success = canaryWasSuccessful && stepResults.every((stepResult) => isSuccessfulStatusCode(stepResult.status));

        const lastStepResult = stepResults[stepResults.length - 1];
        const runtime = lastStepResult.timestamp;
        const startTimestamp = doneAt - runtime;
        const responseTime = lastStepResult.responseTime;

        const testId = canaryName;
        const canariesUrl = `https://${awsLocationId}.console.aws.amazon.com/cloudwatch/home?region=${awsLocationId}#synthetics:canary`;

        const testResult = {
            syntheticEngineName: awsSyntheticEngineName,
            syntheticEngineIconUrl: awsSyntheticEngineIcon,
            messageTimestamp: doneAt,
            locations: [
                {
                    id: awsLocationId,
                    name: awsLocationName,
                }
            ],
            tests: [
                {
                    id: testId,
                    title: canaryName,
                    drilldownLink: `${canariesUrl}/detail/${canaryName}`,
                    editLink: `${canariesUrl}/edit/${canaryName}`,
                    enabled: true,
                    deleted: false,
                    locations: [
                        {
                            id: awsLocationId,
                            enabled: true,
                        }
                    ],
                    steps: stepResults.map((result, i) => ({
                        id: i + 1,
                        title: result.title,
                    })),
                    scheduleIntervalInSeconds: canaryInterval,
                }
            ],
            testResults: [
                {
                    id: testId,
                    totalStepCount: stepResults.length,
                    locationResults: [
                        {
                            id: awsLocationId,
                            startTimestamp: startTimestamp,
                            success: success,
                            responseTimeMillis: responseTime,
                            stepResults: stepResults.map((result, i) => ({
                                id: i + 1,
                                startTimestamp: doneAt - result.timestamp,
                                responseTimeMillis: result.responseTime,
                                title: result.title,
                                ...result.error,
                            })),
                        }
                    ]
                }
            ]
        };

        log.info('DT: Built external-monitor result successfully');
        return testResult;
    }

    async function postDtTestResult(testResult) {
        log.info(`DT: Posting external-monitor result to: ${host}${apiPath}.`);

        return new Promise((resolve) => {
            // Configure the request
            const request = https.request({
                host: host,
                path: apiPath,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Api-Token ${apiToken}`,
                },
            });

            // Prepare handlers
            request.on('response', (response) => {
                const code = response.statusCode;
                response.setEncoding('utf8');

                if (isSuccessfulStatusCode(code)) {
                    log.info('DT: Posted external-monitor result successfully');
                }

                response.on('data', (data) => {
                    if (!isSuccessfulStatusCode(code)) {
                        log.error(`DT: Posting external-monitor result failed: ${code}. ${JSON.stringify(data)}.`);
                    }
                });

                response.on('end', () => resolve());
            });

            request.on('error', (error) => {
                log.error(`DT: Posting external-monitor result failed wtih error: ${JSON.stringify(error)}.`);
                resolve();
            });

            // Add the test results and complete the request
            request.write(JSON.stringify(testResult));
            request.end();
        });
    }

    function initDtTestResultHandlers(page, stepResults, responses) {
        // Each time a page/dom loads we save the result as a step
        page.on('domcontentloaded', async () => {
            const metrics = (await page._client.send('Performance.getMetrics')).metrics;

            const metric = metrics.find(m => m.name === 'DomContentLoaded').value;
            const timestamp = metrics.find(m => m.name === 'Timestamp').value;
            const response = responses.find((response) => page.url() === response.url);
            
            if (!response) {
                if (page.url() !== 'about:blank') {
                    log.error('DT: A response was unexpectedly missing for the URL: ' + page.url());
                }
            } else {
                const status = response.status;
                const success = isSuccessfulStatusCode(status);
                const title = (await page.title()) || page.url();
    
                const stepResult = {
                    title: title,
                    responseTime: metric,
                    timestamp,
                    status,
                    error: success ? {} : {
                        error: {
                            message: `Failed to load: '${title}' (${page.url()}).`,
                            code: status,
                        }
                    }
                };
    
                stepResults.push(stepResult);
                log.info(`DT: Step result:  ${JSON.stringify(stepResult)}.`);
            }
        });

        page.on('response', async (response) => {
            // Save every response so that we can look up status codes later
            responses.push({
                url: response.url(),
                status: response.status(),
            });
        });
    }

    function isSuccessfulStatusCode(statusCode) {
        return 200 <= statusCode && statusCode < 300;
    }
})();