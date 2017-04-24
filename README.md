## Overview

The Dynatrace API examples demonstrate how to access various parts of Dynatrace, such as
timeseries, problem feed and infrastructure topology as an API consumer.

## Dynatrace API documentation

The full Dynatrace API documentation can be found here: 
https://help.dynatrace.com/api-documentation/v1/

## API key
In order to use the Dynatrace API, you need an API key for your Dynatrace tenant. You can generate a key by following these steps

1. Go to your Dynatrace environment: https://{tenant}.live.dynatrace.com
2. Expand the side-bar menu on the left side of the screen and go to **Settings** and then **Integration**
3. Choose the **Dynatrace API** section
4. Click on **Generate token** to create a new API key
5. Enter a description label and submit the request
6. Expand the created key via clicking on the "Edit"-label, copy the token and use it in your Dynatrace API examples

## Using the API with Dynatrace Managed environments

For Dynatrace Managed environments you need to use an URL with the following structure:

    https://<hostname>/e/<tenant-id>/api/v1/

e.g.

    https://sample.dynatrace-managed.com/e/12345678-1234-1234-1234-abcdef12/api/v1/

## License
This module is provided under BSD-3-Clause license. Please check out the details in the LICENSE.txt
