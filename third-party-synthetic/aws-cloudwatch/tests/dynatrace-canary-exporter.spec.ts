import * as canaryLoader from './utils/canary-loader';
const { fn, mock } = jest;
const { any, anything, objectContaining, stringContaining } = expect;

/* Utils */
const canaryLoggingOn = true;
const log = (logger: Handler, ...params: any[]) => {
  if (canaryLoggingOn) {
    logger(...params);
  }
};

const addHandler = (handlerList: HandlerList, handlerName: string, handler: Handler) => {
  handlerList[handlerName] = handlerList[handlerName] || [];
  handlerList[handlerName].push(handler);
};

const callHandlers = (handlerList: HandlerList, handlerName: string, ...params: any[]) => {
  handlerList[handlerName].forEach((handler) => handler(...params));
}

/* Page mocks */
const pageTitle = 'Test page title';
const pageUrl = 'https://www.test-canary-url.com';
const mockPage: MockPage = {
  title: fn(() => Promise.resolve(pageTitle)),
  url: fn(() => pageUrl),
  waitFor: fn(() => { }),
  on: fn((name, func) => addHandler(mockPage._pageHandlers, name, func)),
  goto: fn(() => {
    callHandlers(mockPage._pageHandlers, 'response', {
      url: () => pageUrl,
      status: () => 200,
    });

    callHandlers(mockPage._pageHandlers, 'load');

    return {
      status: fn(() => 200),
    };
  }),
  evaluate: fn((expression) => expression()),
  _pageHandlers: {},
};

/* CloudWatch Mocks */
const mockLog = {
  info: fn((...params) => log(console.info, params)),
  warn: fn((...params) => log(console.warn, params)),
  error: fn((...params) => log(console.error, params)),
};

const awsRegionName = 'me-south-1';
const awsAccountId = '56473829';
const canaryName = 'Test canary name';
const canaryUserAgentString = `:::${awsRegionName}:${awsAccountId}::${canaryName}:`;
const mockSynthetics = {
  getPage: fn(() => mockPage),
  getCanaryUserAgentString: fn(() => canaryUserAgentString),
  takeScreenshot: fn(() => { }),
};

let mockAwsParameters: {[index: string]: string} = {};
const mockParameterStore = {
  getParameter: fn((options: {Name: string}, callback) =>
    callback(undefined, { Parameter: { Value: mockAwsParameters[options.Name] } })),
};
const mockAWS = {
  SSM: fn(() => mockParameterStore),
};

/* HTTP Mocks */
const buildMockResponse = () => {
  const mockResponse: MockHttpResponse = {
    statusCode: 200,
    on: fn((name, func) => addHandler(mockResponse._responseHandlers, name, func)),
    setEncoding: fn(() => { }),
    _responseHandlers: {},
  };
  return mockResponse;
};

const buildExecuteAndCacheMockRequest = (httpPackage: any) => {
  const end = fn(() => { });
  const mockRequest: MockHttpRequest = {
    on: fn((name, func) => addHandler(mockRequest._requestHandlers, name, func)),
    write: fn((body) => mockRequest._body = JSON.parse(body)),
    end,
    _originalEnd: end,
    _requestHandlers: {},
  };

  const mockResponse = buildMockResponse();
  httpPackage._mockRequests.push({
    request: mockRequest,
    response: mockResponse,
  });

  // Use timeouts to allow time to register handlers
  setTimeout(() => {
    callHandlers(mockRequest._requestHandlers, 'response', mockResponse);
    setTimeout(() => callHandlers(mockResponse._responseHandlers, 'end'));
  });

  return mockRequest;
};

const mockHttps: MockHttpModule = {
  request: fn(() => buildExecuteAndCacheMockRequest(mockHttps)),
  get: fn(() => buildExecuteAndCacheMockRequest(mockHttps)),
  _mockRequests: [],
};
const mockHttp: MockHttpModule = {
  request: fn(() => buildExecuteAndCacheMockRequest(mockHttp)),
  get: fn(() => buildExecuteAndCacheMockRequest(mockHttp)),
  _mockRequests: [],
};

/* Module Mocks */
mock('SyntheticsLogger', () => mockLog, { virtual: true });
mock('Synthetics', () => mockSynthetics, { virtual: true });
mock('aws-sdk', () => mockAWS, { virtual: true });
mock('http', () => ({ ...mockHttp }));
mock('https', () => ({ ...mockHttps }));

/* Global mocks */
const responseTimeMillis = 3333;
const startTimestamp = 777777777777;
global.performance = {
  getEntriesByType: () => [{ loadEventStart: responseTimeMillis }] as PerformanceNavigationTiming[],
  timeOrigin: startTimestamp,
} as any;

beforeEach(() => {
  mockPage._pageHandlers = {};
  mockHttp._mockRequests = [];
  mockHttps._mockRequests = [];
  global.beforeExporter = undefined;
  mockAwsParameters = {
    '/CloudWatchSynthetics/DynatraceUrl': 'https://tenant-id.live.dynatrace.com',
    '/CloudWatchSynthetics/DynatraceSyntheticsApiToken': 'TEST-TOKEN-111',
  };
});

describe('buildAndLoadCanary', () => {
  it('is a simple canary testing tool that merges the canary with the exporter script ' +
    'and exposes the original/non-overriden canary exports for testing purposes', async () => {
      // GIVEN - an instrumented mock canary
      // We can use an event to read/write to the canary exports before the exporter runs
      global.beforeExporter = (_exports) => {
        _exports.addedValue = 'intercepted';
      };

      // WHEN - the canary is loaded
      const canary = await canaryLoader.buildAndLoadCanary('./utils/42-demo-canary.js');

      // THEN - The canary is loaded as a module
      expect(canary).toBeTruthy();

      // With a (now-overriden) handler
      const overridenHandler = canary.handler;
      expect(overridenHandler).toBeTruthy();

      // we can access the original canary/exports/handler
      const originalCanary = canary._originalExports;
      const originalHandler = originalCanary.handler;
      expect(originalHandler).toBeTruthy();

      // Which is, indeed, a different handler
      expect(overridenHandler).not.toBe(originalHandler);

      // The exports used by the canary were successfully modified by the beforeExporter handler
      expect(canary.addedValue).toBe('intercepted');
      // These changes are not reflected in the cached original exports
      expect(originalCanary.addedValue).toBeUndefined();

      // WHEN - the instrumented canary is executed it executes the original handler
      expect(originalHandler).toHaveBeenCalledTimes(0);
      expect(await overridenHandler()).toBe(42);
      expect(originalHandler).toHaveBeenCalledTimes(1);

      // WHEN - the original handler is executed we find the same result
      expect(await overridenHandler()).toBe(await originalHandler());
      expect(await originalHandler()).toBe(42);

      // When all is said and done, we leave the handler in its overridden state,
      // because the canary might get executed again before the canary module is reloaded
      // and we can only override the handler when the script is first loaded.
      expect(canary.handler).toBe(overridenHandler);
    });
});

describe('dynatrace-canary-exporter', () => {

  it('overrides the first exported function it finds as the canary entry point', async () => {
    // GIVEN a canary with multiple exports
    const handler1 = fn(() => { });
    const handler2 = fn(() => { });
    global.beforeExporter = (_exports) => {
      _exports.handler1 = handler1;
      _exports.handler2 = handler2;
    };

    // WHEN the canary is loaded
    await canaryLoader.buildAndLoadCanary();

    // THEN a warning is logged, because it's not clear which function is the canary entry point
    expect(mockLog.warn).toHaveBeenCalledTimes(1);
  });

  describe('overrides [http|https].[request|get]', () => {

    it('to instrument api canaries', async () => {
      // GIVEN an api canary that makes a single request
      const canary = await canaryLoader.buildAndLoadCanary('../web-api-canary_API-canary.js');
      const canaryRequestCount = 1;

      // WHEN the canary is executed
      await canary.handler()

      // THEN 2 requests should be made: canary request + request for pushing results to Dynatrace
      const totalRequestCount = canaryRequestCount + 1;
      expect(mockHttps.request).toHaveBeenCalledTimes(totalRequestCount);
      expect(mockHttps._mockRequests.length).toBe(totalRequestCount);

      const canaryRequest = mockHttps._mockRequests[0].request;
      const canaryResponse = mockHttps._mockRequests[0].response;
      const resultsRequest = mockHttps._mockRequests[1].request;
      const resultsResponse = mockHttps._mockRequests[1].response;

      // The canary request/response should get intercepted/overriden
      expect(canaryRequest.on).toHaveBeenCalledWith('response', any(Function));
      expect(canaryRequest.on).toHaveBeenCalledWith('error', any(Function));
      expect(canaryRequest.on).toHaveBeenCalledTimes(2 * 2); // x2 = Assuming the original and interceptor listen to the same events
      expect(canaryResponse.on).toHaveBeenCalledWith('data', any(Function));
      expect(canaryResponse.on).toHaveBeenCalledWith('end', any(Function));
      expect(canaryResponse.on).toHaveBeenCalledTimes(2 * 2); // x2 = Assuming the original and interceptor listen to the same events

      expect(canaryRequest.end).not.toBe(canaryRequest._originalEnd);
      // But overriden functions should still get called
      expect(canaryRequest._originalEnd).toHaveBeenCalledTimes(1);

      // The results request/response should not get intercepted/overriden
      expect(resultsRequest.on).toHaveBeenCalledWith('response', any(Function));
      expect(resultsRequest.on).toHaveBeenCalledWith('error', any(Function));
      expect(resultsRequest.on).toHaveBeenCalledTimes(2);
      expect(resultsResponse.on).toHaveBeenCalledWith('data', any(Function));
      expect(resultsResponse.on).toHaveBeenCalledWith('end', any(Function));
      expect(resultsResponse.on).toHaveBeenCalledTimes(2);
      expect(resultsRequest.end).toBe(resultsRequest._originalEnd);
      expect(resultsRequest.end).toHaveBeenCalledTimes(1);

      // The original overriden http package functions should be restored
      expect(mockHttps.request).toBe(require('https').request);
      expect(mockHttps.get).toBe(require('https').get);
      expect(mockHttp.request).toBe(require('http').request);
      expect(mockHttp.get).toBe(require('http').get);
    });
  });

  describe('overrides synthetics.getPage', () => {

    it('to listen to page events', async () => {
      // GIVEN a web page canary
      const canary = await canaryLoader.buildAndLoadCanary('../web-page-canary_heartbeat-monitoring.js');;

      // WHEN the canary is executed
      await canary.handler();

      // THEN synthetics.getPage is overriden to intercept page events
      expect(mockPage.on).toHaveBeenCalledWith('response', any(Function));
      expect(mockPage.on).toHaveBeenCalledWith('load', any(Function));
      expect(mockPage.on).toHaveBeenCalledTimes(2);
    });

    it('and generate step results', async () => {
      // GIVEN a web page canary
      const canary = await canaryLoader.buildAndLoadCanary('../web-page-canary_heartbeat-monitoring.js');;

      // WHEN the canary is executed
      await canary.handler();

      // THEN a requested should be posted to Dynatrace
      expect(mockHttps.request).toHaveBeenCalledWith({
        host: anything(),
        path: anything(),
        port: anything(),
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': stringContaining('Api-Token'),
        },
      });

      // With the expected results
      const result = mockHttps._mockRequests[0].request._body;
      // Correct monitor definition
      expect(result.syntheticEngineName).toBe('AWS CloudWatch Synthetics');
      expect(result.tests).toEqual([objectContaining({
        title: canaryName,
        enabled: true,
        deleted: false,
        locations: [{
          id: awsRegionName,
          enabled: true,
        }],
        steps: [{
          id: 1,
          title: pageTitle,
        }],
        scheduleIntervalInSeconds: any(Number),
      })]);
      // Timestamp is realistic
      expect(result.messageTimestamp).toBeLessThan(Date.now());
      expect(result.messageTimestamp + 1000).toBeGreaterThan(Date.now());

      // Correct monitor results
      expect(result.testResults).toEqual([objectContaining({
        totalStepCount: 1,
        locationResults: [objectContaining({
          id: awsRegionName,
          success: true,
          stepResults: [{
            id: 1,
            startTimestamp,
            responseTimeMillis,
          }],
        })],
      })]);
      // Timestamp is realistic
      expect(result.testResults[0].locationResults[0].startTimestamp).toBeLessThan(Date.now());
      expect(result.testResults[0].locationResults[0].startTimestamp + 1000).toBeGreaterThan(Date.now());
    });
  });

  describe('sanitizes/standardizes provided tenant and host URLs', () => {

    const thirdPartyResultsApiPath = '/api/v1/synthetic/ext/tests';
    const protocol = 'https';

    it('SaaS tenant without slash', async () => {
      // GIVEN a dynatrace SaaS tenant url that is only a protocal and host
      const host = 'tenant-id.live.dynatrace.com';
      const tenantUrl = `${protocol}://${host}`; // That ends WITHOUT a slash
      mockAwsParameters = { '/CloudWatchSynthetics/DynatraceUrl': tenantUrl };

      // WHEN the canary is loaded and executed
      const canary = await canaryLoader.buildAndLoadCanary('../web-page-canary_heartbeat-monitoring.js')
      await canary.handler();

      // THEN in the configured request:
      expect(mockHttps.request).toHaveBeenCalledWith(objectContaining({
        // The tenant host name should match the request's host
        host: host,
        // The path is simply the api path
        path: thirdPartyResultsApiPath,
        // The port is left blank resulting in the default protocol port being used
        port: '',
      }));
    });

    it('SaaS tenant with slash', async () => {
      // GIVEN a dynatrace SaaS tenant url that is only a protocal and host
      const host = 'tenant-id.live.dynatrace.com';
      const tenantUrl = `${protocol}://${host}/`; // That ends WITH a slash
      mockAwsParameters = { '/CloudWatchSynthetics/DynatraceUrl': tenantUrl };

      // WHEN the canary is loaded and executed
      const canary = await canaryLoader.buildAndLoadCanary('../web-page-canary_heartbeat-monitoring.js')
      await canary.handler();

      // THEN the request configuration is the same as a tenant URL that doesn't end with a slash (see above):
      expect(mockHttps.request).toHaveBeenCalledWith(objectContaining({
        host: host,
        path: thirdPartyResultsApiPath,
        port: '',
      }));
    });

    it('SaaS tenant without protocol', async () => {
      // GIVEN a dynatrace SaaS tenant url that is only a host (WITHOUT a protocol)
      const host = 'tenant-id.live.dynatrace.com';
      mockAwsParameters = { '/CloudWatchSynthetics/DynatraceUrl': host };

      // WHEN the canary is loaded and executed
      const canary = await canaryLoader.buildAndLoadCanary('../web-page-canary_heartbeat-monitoring.js')
      await canary.handler();

      // THEN the request configuration is the same as a tenant URL that does have a protocol, (see above)
      // because the https protocol is redundant when using the https package:
      expect(mockHttps.request).toHaveBeenCalledWith(objectContaining({
        host: host,
        path: thirdPartyResultsApiPath,
        port: '',
      }));
    });

    it('Managed tenant with additional path', async () => {
      // GIVEN a dynatrace Managed tenant url with both a host and additional path
      const host = 'sample.dynatrace-managed.com';
      const tenantPath = '/e/00000000-0000-0000-0000-000000000000';
      const tenantUrl = `${protocol}://${host}${tenantPath}`;
      mockAwsParameters = { '/CloudWatchSynthetics/DynatraceUrl': tenantUrl };

      // WHEN the canary is loaded and executed
      const canary = await canaryLoader.buildAndLoadCanary('../web-page-canary_heartbeat-monitoring.js')
      await canary.handler();

      // THEN the additional tenant path is appended to the third-party api path
      expect(mockHttps.request).toHaveBeenCalledWith(objectContaining({
        host: host,
        path: tenantPath + thirdPartyResultsApiPath,
        port: '',
      }));
    });

    it('Managed tenant with additional path and slash', async () => {
      // GIVEN a dynatrace Managed tenant url with both a host and additional path
      const host = 'sample.dynatrace-managed.com';
      const tenantPath = '/e/00000000-0000-0000-0000-000000000000';
      const tenantUrl = `${protocol}://${host}${tenantPath}/`; // That ends WITH a slash
      mockAwsParameters = { '/CloudWatchSynthetics/DynatraceUrl': tenantUrl };

      // WHEN the canary is loaded and executed
      const canary = await canaryLoader.buildAndLoadCanary('../web-page-canary_heartbeat-monitoring.js')
      await canary.handler();

      // THEN the request configuration is the same as a tenant URL that doesn't end with a slash (see above):
      expect(mockHttps.request).toHaveBeenCalledWith(objectContaining({
        host: host,
        path: tenantPath + thirdPartyResultsApiPath,
        port: '',
      }));
    });

    it('Managed ActiveGate with custom port', async () => {
      // GIVEN a Managed ActiveGate url with a custom HTTPS port
      const host = 'sample.dynatrace-managed.com';
      const tenantPath = '/e/00000000-0000-0000-0000-000000000000';
      const port = '9999';
      const tenantUrl = `${protocol}://${host}:${port}${tenantPath}`;
      mockAwsParameters = { '/CloudWatchSynthetics/DynatraceUrl': tenantUrl };

      // WHEN the canary is loaded and executed
      const canary = await canaryLoader.buildAndLoadCanary('../web-page-canary_heartbeat-monitoring.js')
      await canary.handler();

      // THEN the additional tenant path is appended to the third-party api path
      expect(mockHttps.request).toHaveBeenCalledWith(objectContaining({
        host: host,
        path: tenantPath + thirdPartyResultsApiPath,
        port: port,
      }));
    });
  });
});
