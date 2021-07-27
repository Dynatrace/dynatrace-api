/**
 * Dynatrace AWS CloudWatch Synthetics Canary exporter
 * v1.0.3
 */

(function () {
    // -- Imports --
    const log = require('SyntheticsLogger');
    try {
        const synthetics = require('Synthetics');
        const https = require('https');
        const http = require('http');
        const AWS = require('aws-sdk')

        // -- Dynatrace configuration --
        // Dynatrace Tenant or ActiveGate URL e.g.
        //               SaaS: https://tenant-id.live.dynatrace.com
        //            Managed: https://sample.dynatrace-managed.com/e/00000000-0000-0000-0000-000000000000
        // Managed ActiveGate: https://sample.dynatrace-managed.com:9999/e/00000000-0000-0000-0000-000000000000
        // Either the URL itself OR load the URL from the parameter store
        const dynatraceUrl = '' || getParameter('/CloudWatchSynthetics/DynatraceUrl'/*, 'us-east-1'*/);
        // Dynatrace API Token with permission to create synthetic monitors
        // Either the token itself OR load the token from the parameter store
        const dynatraceApiToken = '' || getParameter('/CloudWatchSynthetics/DynatraceSyntheticsApiToken'/*, 'us-east-1'*/);

        // -- Display values --
        // How often the canary is scheduled to run (so that Dynatrace can correctly detect availability and display metrics)
        // Note: the configured canary schedule must be manually synchronized with this value
        const canaryInterval = 300; // In seconds
        // The monitor display name in Dynatrace (by default the canary name)
        const dynatraceMonitorName = '' || canaryConfig().canaryName;

        // -- Dynatrace third-party monitor constants --
        // The dynatrace synthetic third-party endpoint
        const apiPath = 'api/v1/synthetic/ext/tests';
        // Dynatrace monitor type/engine
        const dynatraceMonitorType = 'AWS CloudWatch Synthetics';
        const dynatraceMonitorTypeIcon = 'https://raw.githubusercontent.com/Dynatrace/dynatrace-api/master/third-party-synthetic/aws-cloudwatch/cloud-watch-icon.png';

        // The request Promises that return steps definitions/results
        const _stepResults$ = [];

        // Save references to the overridden functions, so they can be restored
        // and prevent intercepting requests after the canary
        const originalFuncs = [];
        const saveFunc = (funcModule, funcName) => originalFuncs.push({ funcModule, funcName, func: funcModule[funcName] });
        const restoreSavedFuncs = () => originalFuncs.forEach(({ funcModule, funcName, func }) => funcModule[funcName] = func);

        function beforeCanary() {
            // Reset the state manually, because the lambda script isn't always reloaded before each canary execution
            _stepResults$.length = originalFuncs.length = 0;

            // ----- Web page Canary instrumentation: START -----

            saveFunc(synthetics, 'getPage');
            // The original synthetics.getPage function that we override
            const originalGetPage = synthetics.getPage;
            // Extend synthetics.getPage so we can get a reference to the page object
            synthetics.getPage = async () => {
                const page = await originalGetPage.call(synthetics);
                // Handle DomContentLoaded and Response events so we can get metrics and HTTP response codes
                initDtTestResultHandlers(page, (stepResult) => _stepResults$.push(stepResult));
                return page;
            };
            // ----- Web page Canary instrumentation: END -----

            // ----- Web api Canary instrumentation: START -----
            // Override methods that make requests, so we can intercept them
            [http, https].forEach((funcModule) => ['get', 'request'].forEach((funcName) => {
                saveFunc(funcModule, funcName);
                const originalFunc = funcModule[funcName];
                funcModule[funcName] = function (urlOrOptions) {
                    const request = originalFunc.apply(funcModule, arguments);
                    handleCanaryRequest(request, urlOrOptions, (stepResult) => _stepResults$.push(stepResult));
                    return request;
                }
            }));
            // ----- Web api Canary instrumentation: END -----
        }

        function afterCanary() {
            // Restore the overriden methods
            restoreSavedFuncs();
        }

        // ----- Web page Canary step builder: START -----
        function initDtTestResultHandlers(page, onStepResult) {
            const responses = [];

            // Save every response so that we can look up status codes
            page.on('response', async (response) => {
                responses.push({
                    url: response.url(),
                    status: response.status(),
                });
            });

            // Each time a page loads we save the result as a step
            page.on('load', async () => {
                const response = responses.find((response) => page.url() === response.url);

                if (!response) {
                    if (page.url() !== 'about:blank') {
                        log.error('DT: A response was unexpectedly missing for the URL: ' + page.url());
                    }
                } else {
		    onStepResult(new Promise(async (resolve) => {  
			    const metric = await page.evaluate(() => performance.getEntriesByType('navigation')[0].loadEventStart);
			    const startTime = await page.evaluate(() => performance.timeOrigin);
			    const status = response.status;
			    const success = isSuccessfulStatusCode(status);
			    const title = (await page.title()) || page.url();

			    const stepResult = {
				title: title,
				startTimestamp: startTime,
				responseTimeMillis: metric,
				errorWrapper: success ? {} : {
				    error: {
					message: `Failed to load: '${title}' (${page.url()}).`,
					code: status,
				    }
				}
			    };

			    log.info(`DT: Step result (web page): ${JSON.stringify(stepResult)}.`);
			    resolve(stepResult);
		    }));
                }
            });
        }
        // ----- Web page Canary step builder: END -----

        // ----- Web api Canary step builder: START -----
        const ignoredApiUrlPatterns = [
            /^monitoring\..*\.amazonaws.com(\/.*)?$/, // Where synthetics posts canary results
	    /^cw-syn-results(.*)\.amazonaws\.com(.*)?$/, // where synthetics posts canary screenshots
            /^s3\.amazonaws\.com\/$/, // 
        ];

        function handleCanaryRequest(request, urlOrOptions, onStepResult) {
            const method = request.method;
            const url = getRequestUrl(urlOrOptions);

            if (ignoredApiUrlPatterns.some((pattern) => pattern.test(url))) {
                return;
            }

            const step = {
                title: `${method}: ${url}`,
                startTimestamp: Date.now()
            };

            // If the request was created with 'get', then 'end' is called automatically and the request is already getting sent
            // If the request was created with 'request', then 'end' will get called manually later and that provides a more precise start timestamp
            const originalEnd = request.end;
            request.end = function () {
                originalEnd.apply(request, arguments);
                step.startTimestamp = Date.now();
            };

            onStepResult(new Promise((resolve) => {

                request.on('response', async (response) => {
                    const responseResult = await handleCanaryResponse(response, step.startTimestamp);
                    const stepResult = {
                        ...step,
                        ...responseResult,
                    };
                    log.info(`DT: Step result (web api): ${JSON.stringify(stepResult)}.`);
                    resolve(stepResult);
                });

                request.on('error', function (error) {
                    const stepResult = {
                        ...step,
                        errorWrapper: {
                            error: {
                                code: 0,
                                message: error.toString(),
                            }
                        },
                    };
                    log.info(`DT: Step result with unexpected error (web api): ${JSON.stringify(stepResult)}.`);
                    resolve(stepResult);
                });
            }));
        }

        async function handleCanaryResponse(response, requestTime) {
            return new Promise((resolve) => {
                response.on('end', () => {
                    const step = {
                        responseTimeMillis: Date.now() - requestTime,
                        errorWrapper: {},
                    };

                    if (!isSuccessfulStatusCode(response.statusCode)) {
                        step.errorWrapper = {
                            error: {
                                code: response.statusCode,
                                message: response.statusMessage || 'An unknown error occured',
                            }
                        };
                    }

                    resolve(step);
                });

                // Without a 'data' handler, 'end' doesn't get triggered
                response.on('data', () => { });
            });
        }

        function getRequestUrl(urlOrOptions) {
            if (typeof urlOrOptions === 'string') {
                return urlOrOptions;
            } else {
                const host = urlOrOptions.host || urlOrOptions.hostname;
                let path = urlOrOptions.path;

                if (path && !path.startsWith('/')) {
                    path = '/' + path;
                }

                return path ? host + path : host;
            }
        }
        // ----- Web api Canary step builder: END -----


        // -------------------------------------------------------------------------
        // All code after this point is shared by both web page and web api canaries
        // -------------------------------------------------------------------------

        // Extend the canary's main entry point, so that we can upload the test results when it's done
        const handlerName = getCanaryHandlerName();
        const originalHandler = exports[handlerName];
        exports[handlerName] = async () => {
            const startTime = Date.now();

            let originalHandlerError = undefined;
            let originalHandlerReturnValue = undefined;

            try {
                beforeCanary();
            } catch (error) {
                log.error('DT: An unexpected error occured in the before canary handler', error);
            }

            try {
                originalHandlerReturnValue = await originalHandler.call(exports);
            } catch (error) {
                log.info(`DT: Original handler threw an error (${error})`);
                originalHandlerError = error;
            } finally {
                // Prevent unexpected DT-specific errors from breaking the canary
                try {
                    try {
                        afterCanary();
                    } catch (error) {
                        log.error('DT: An unexpected error occured in the after canary handler', error);
                    }
                    await sendResultsToDynatrace(_stepResults$, startTime, !originalHandlerError);
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

        async function sendResultsToDynatrace(stepResults$, startTime, canaryWasSuccessful) {
            if (stepResults$.length) {
                const stepResults = await Promise.all(stepResults$);
                const testResult = buildDtTestResult(stepResults, startTime, canaryWasSuccessful);
                await postDtTestResult(testResult);
            } else {
                log.info('DT: No step results.')
            }
        }

        function buildDtTestResult(stepResults, startTime, canaryWasSuccessful) {
            log.info('DT: Building third-party monitor result');

            const endTime = new Date().getTime();
            const success = canaryWasSuccessful && stepResults.every((stepResult) => !stepResult.errorWrapper.error);
            stepResults.forEach((stepResult, i) => stepResult.id = i + 1);

            const { canaryName, accountId, awsRegionName, awsRegionDescription } = canaryConfig();
            const testId = `${accountId}:${canaryName}`;
            const canariesUrl = `https://${awsRegionName}.console.aws.amazon.com/cloudwatch/home?region=${awsRegionName}#synthetics:canary`;

            const testResult = {
                syntheticEngineName: dynatraceMonitorType,
                syntheticEngineIconUrl: dynatraceMonitorTypeIcon,
                messageTimestamp: endTime,
                locations: [
                    {
                        id: awsRegionName,
                        name: awsRegionDescription,
                    }
                ],
                tests: [
                    {
                        id: testId,
                        title: dynatraceMonitorName,
                        drilldownLink: `${canariesUrl}/detail/${canaryName}`,
                        editLink: `${canariesUrl}/edit/${canaryName}`,
                        enabled: true,
                        deleted: false,
                        locations: [
                            {
                                id: awsRegionName,
                                enabled: true,
                            }
                        ],
                        steps: stepResults.map(({ id, title }) => ({ id, title })),
                        scheduleIntervalInSeconds: canaryInterval,
                    }
                ],
                testResults: [
                    {
                        id: testId,
                        totalStepCount: stepResults.length,
                        locationResults: [
                            {
                                id: awsRegionName,
                                startTimestamp: startTime,
                                success: success,
                                stepResults: stepResults.map(({ id, startTimestamp, responseTimeMillis, errorWrapper }) =>
                                    ({ id, startTimestamp, responseTimeMillis, ...errorWrapper })
                                ),
                            }
                        ]
                    }
                ]
            };

            log.info('DT: Built third-party monitor result successfully');
            log.info(JSON.stringify(testResult));
            return testResult;
        }

        async function postDtTestResult(testResult) {
            const apiUrl = new URL(apiPath, await getDynatraceUrl());
            const apiToken = await dynatraceApiToken;

            log.info(`DT: Posting third-party monitor result to: ${apiUrl.toString()}.`);

            return new Promise((resolve) => {
                // Configure the request
                const request = https.request({
                    host: apiUrl.hostname,
                    path: apiUrl.pathname,
                    port: apiUrl.port,
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
                        log.info('DT: Posted third-party monitor result successfully');
                    }

                    response.on('data', (data) => {
                        if (!isSuccessfulStatusCode(code)) {
                            log.error(`DT: Posting third-party monitor result failed: ${code}. ${JSON.stringify(data)}.`);
                        }
                    });

                    response.on('end', () => resolve());
                });

                request.on('error', (error) => {
                    log.error(`DT: Posting third-party monitor result failed wtih error: ${JSON.stringify(error)}.`);
                    resolve();
                });

                // Add the test results and complete the request
                request.write(JSON.stringify(testResult));
                request.end();
            });
        }

        const isSuccessfulStatusCode = (statusCode) => 200 <= statusCode && statusCode < 300;

        function canaryConfig() {
            const awsRegions = {
                'us-east-1': 'US East (N. Virginia)', 'us-east-2': 'US East (Ohio)', 'us-west-1': 'US West (N. California)', 'us-west-2': 'US West (Oregon)', 'ap-east-1': 'Asia Pacific (Hong Kong)',
                'ap-south-1': 'Asia Pacific (Mumbai)', 'ap-northeast-2': 'Asia Pacific (Seoul)', 'ap-southeast-1': 'Asia Pacific (Singapore)', 'ap-southeast-2': 'Asia Pacific (Sydney)',
                'ap-northeast-1': 'Asia Pacific (Tokyo)', 'ca-central-1': 'Canada (Central)', 'eu-central-1': 'Europe (Frankfurt)', 'eu-west-1': 'Europe (Ireland)',
                'eu-west-2': 'Europe (London)', 'eu-west-3': 'Europe (Paris)', 'eu-north-1': 'Europe (Stockholm)', 'me-south-1': 'Middle East (Bahrain)', 'sa-east-1': 'South America (São Paulo)',
            };
            const canaryUserAgentStringParts = synthetics.getCanaryUserAgentString().split(':');
            const awsRegionName = canaryUserAgentStringParts[3];
            canaryConfig = () => ({
                accountId: canaryUserAgentStringParts[4],
                canaryName: canaryUserAgentStringParts[6],
                awsRegionName,
                awsRegionDescription: awsRegions[awsRegionName] || awsRegionName,
            });
            return canaryConfig();
        };

        function getCanaryHandlerName() {
            const exportNames = Object.keys(exports).filter((key) => typeof exports[key] === 'function');
            if (exportNames.length > 1) {
                log.warn(`DT: Multiple functions are being exported. Assuming the first one is the canary entry point. (${exportNames.join(', ')})`);
            }
            return exportNames[0];
        }

        async function getParameter(name, region) {
            const config = typeof region === 'string' ? { region } : undefined;
            const parameterStore = new AWS.SSM(config);
            return new Promise((resolve, reject) => parameterStore.getParameter(
                { Name: name, WithDecryption: true },
                (error, data) => error ? reject(error) : resolve(data.Parameter.Value),
            ));
        }

        async function getDynatraceUrl() {
            let cleanUrl = await dynatraceUrl;
            cleanUrl = cleanUrl.startsWith('https://') ? cleanUrl : `https://${cleanUrl}`;
            cleanUrl = cleanUrl.endsWith('/') ? cleanUrl : `${cleanUrl}/`;
            return cleanUrl;
        }

    } catch (error) {
        log.error('DT: An unexpected error occured in the Dynatrace export script', error);
    }
})();
