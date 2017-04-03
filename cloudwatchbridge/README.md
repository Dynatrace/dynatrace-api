## Overview

The CloudWatch bridge example demonstrates how to automatically push Dynatrace full stack monitoring metrics
over to CloudWatch.

### Prerequisites

The full Dynatrace API documentation can be found here: 
https://help.dynatrace.com/api-documentation/v1/

1. Install the [Amazon CloudWatch Command Line Interface](http://docs.aws.amazon.com/AmazonCloudWatch/latest/cli/SetupCLI.html)
2. Setup and authenticate your Amazon CloudWatch Command Line Interface
3. Create a Dynatrace API key (see below)
4. Enter your Dynatrace environment id and your API key within the dt_cw_bridge.py script
5. Configure valid timeseries ids, aggregation types and entities within the dt_cw_bridge.py script
6. Run the script by typing `python dt_cw_bridge.py`

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
