## AWS CloudWatch

AWS CloudWatch canaries are executed in a Node.js lambda. The dynatrace exporter script (`dynatrace-canary-exporter.js`) can be appended to the end of the lambda script to push the canary results to a Dynatrace synthetic third-party monitor. In order to push results to Dynatrace simply:
1) Append the script to the end of the canary
2) Set the Dynatrace `host` and `apiToken` for accessing the API (optionally loading the token from the parameter store)
3) Set the `canaryInterval` (in seconds), so that Dynatrace knows how often to expect results
4) Optionally customize the monitor display name used in the Dynatrace UI (defaults to the canary name)

At the time of writing, AWS CloudWatch provides four different canary blueprints that can be grouped into two types. The provided script handles both of these types:
- **Web page**: *Heartbeat monitoring*, *GUI workflow builder* and *Broken link checker*
- **Web API**: *API canary*

> At the time of writing, the only **performance metric** provided by canaries is the lambda execution time. This metric obviously isn't available *inside* the lambda execution, so these examples use different metrics. As a result, the metrics in the Dynatrace UI won't match the canary metrics in the CloudWatch UI.

### Examples

The following canaries were generated in the AWS CloudWatch UI and have been verified to work with the exporter script. To test a canary simply append the exporter script to the end of it:

- `web-page-canary_heartbeat-monitoring.js`
- `web-page-canary_broken-link-checker.js`
- `web-page-canary_GUI-workflow-builder.js`
- `web-api-canary_API-canary.js`

> The broken link checker canary recursively checks whatever links it finds on a page. Each link gets recorded as a step in Dynatrace, but different runs may find different links/steps. The previous step names will simply be overwritten by the new names. Thus, the historic data of a step may not necessarily correspond to its current name.

### Metrics

#### Web page canaries

For web page canaries a monitor step result is generated for each page load event. The step performance is measured using the `DomContentLoaded` metric from puppeteer.

#### Web API Canaries

For web API canaries a monitor step result is generated for each web request sent with the `http` or `https` packages. The step performance is measured using the `request.end` and `response.end` events.

## License

This module is provided under BSD-3-Clause license. Please check out the details in LICENSE.txt
