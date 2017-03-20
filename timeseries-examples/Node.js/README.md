## Overview

This Dynatrace timeseries data export API example demonstrate the export of CPU timeseries for a given host and how to
chart the resulting data points by using Google charts.
Mind that a Node.js service wrapper is used to cope with the Browsers security restriction to only load resources
from the same origin. The service wrapper also hides the secret API token for accessing the Dynatrace tenant data instead
of exposing it within the JavaScript.

## Dynatrace data export API documentation

The full API documentation can be found here: 
https://help.dynatrace.com/api-documentation/v1/timeseries

## API key
In order to use the Dynatrace API, you need an API key for your Dynatrace tenant. You can generate a key by following these steps

1. Go to your Dynatrace environment: https://{tenant}.live.dynatrace.com
2. Expand the side-bar menu on the left side of the screen and go to **Settings** and then **Integration**
3. Choose the **Dynatrace API** section
4. Click on **Generate token** to create a new API key
5. Enter a description label and submit the request
6. Expand the created key via clicking on the "Edit"-label, copy the token and use it in your Dynatrace API examples

## License
This module is provided under BSD-3-Clause license. Please check out the details in the LICENSE.txt
