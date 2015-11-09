## Overview

This Ruxit timeseries data export API example demonstrate the export of CPU timeseries for a given host and how to
chart the resulting data points by using Google charts.
Mind that a Node.js service wrapper is used to cope with the Browsers security restriction to only load resources
from the same origin. The service wrapper also hides the secret API token for accessing the Ruxit tenant data instead
of exposing it within the JavaScript.

### Ruxit data export API documentation

The full API documentation can be found here: 
https://ruxit.com/help/api-documentation/v1/timeseries

####`API key`
The API key for your Ruxit tenant. You can generate a key by following these steps

1. go to your Ruxit environment: https://{tenant}.live.ruxit.com
2. Click the burger menu in the right upper corner and select **Integration**
3. You will see the "API" section; 
4. Enter a description label and click on **Generate**
5. copy it and use it in your data export API examples

##License
This module is provided under BSD-3-Clause license. Please check out the details in the LICENSE.txt
