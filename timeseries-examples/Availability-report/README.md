## Overview

This Dynatrace API example generates either a host or a full processes availability report in HTML.

![Host availability report](/host_report.png?raw=true "Host availability report")

![Process availability report](/process_report.png?raw=true "Process availability report")

## Dynatrace API documentation

The full API documentation can be found here: 
https://help.dynatrace.com/api-documentation/v1/timeseries

## API token
In order to use the Dynatrace API, you need an API token for your Dynatrace tenant. You can generate a token by following these steps

1. Go to your Dynatrace environment: https://{tenant}.live.dynatrace.com
2. Expand the side-bar menu on the left side of the screen and go to **Settings** and then **Integration**
3. Choose the **Dynatrace API** section
4. Click on **Generate token** to create a new API token
5. Enter a description label and submit the request
6. Expand the created token via clicking on the "Edit"-label, copy the token and use it in your Dynatrace API examples

## License
This module is provided under BSD-3-Clause license. Please check out the details in the LICENSE.txt
