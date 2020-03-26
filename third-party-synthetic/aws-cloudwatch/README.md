## AWS CloudWatch examples

AWS CloudWatch canaries are executed in a Node.js lambda. Here are some examples of how to edit the lambda script to push the canary results to Dynatrace.

> At the time of writing, the only **performance metric** provided by canaries is the lambda execution time. This metric obviously isn't available inside the lambda execution. These example access other metrics that **are** available. As a result, the metrics in the Dynatrace UI won't match the canary metrics in the CloudWatch UI.

At the time of writing, AWS CloudWatch provides four canary blueprints. Three are designed to monitor **web pages** (*Heartbeat monitoring*, *GUI workflow builder* and *Broken link checker*) and the fourth to monitor **web APIs** (*API canary*). There are currently only examples for web page canaries.

All the examples work by simply appending a script to the end of the canary and setting some hard-coded values necessary for building a valid result for Dynatrace.

### Web page Canaries

#### Scripts

Web page canaries can use `web-page-canary_dt-exporter.js` to push results to Dynatrace. The content of the script can be appended to each of the following canaries to create a working example:

- `web-page-canary_heartbeat-monitoring.js`
- `web-page-canary_broken-link-checker.js`
- `web-page-canary_GUI-workflow-builder.js`

#### Configuration

The exporter script requires several variables to be configured:

```javascript
// -- Hard-coded aws/canary values --
// The monitor display name in Dynatrace
const canaryName = 'Test Canary name';
// The location display name in Dynatrace
const awsLocationName = 'US East (N. Virginia)';
// To uniquely identify the location and generate links in Dynatrace back to the canary
const awsLocationId = 'us-east-1';
// How often the canary is scheduled to run (so that Dynatrace can correctly detect and display availability)
const canaryInterval = 3600;

// -- DT API --
// Dynatrace host name the results should be sent to
const host = 'demo.dev.dynatracelabs.com';
// Dynatrace api token with permissions to post monitor results
const apiToken = '';
```

#### Results

A monitor step result is generated for each page load event. The `DomContentLoaded` metric from puppeteer is used to measure step performance.

## License

This module is provided under BSD-3-Clause license. Please check out the details in LICENSE.txt