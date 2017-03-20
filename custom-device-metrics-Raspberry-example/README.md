
## Overview

The custom metric and device example demonstrates how to use the Dynatrace API to define new metrics and
custom devices within your environment.
Within this tiny example a Raspberry PI measures and sends its CPU temperature as well as the free memory
into a Dynatrace environment.
First the timeseries metrics are registered, then the device metadata along with the metric values is sent
by using a scheduled job. 

## Prerequisites

The full Dynatrace API documentation can be found here: 
https://help.dynatrace.com/api-documentation/v1/

1. Create a Dynatrace API key (see below)
4. Enter your Dynatrace environment id and your API key within the dt_auto_tag.py script

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
