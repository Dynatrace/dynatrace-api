## Overview

The CloudWatch bridge example demonstrates how to automatically push Dynatrace full stack monitoring metrics
over to CloudWatch.

### Prerequisites

The full Dynatrace API documentation can be found here: 
https://help.dynatrace.com/api-documentation/v1/

1. Install the [Amazon CloudWatch Command Line Interface](http://docs.aws.amazon.com/AmazonCloudWatch/latest/cli/SetupCLI.html)
2. Setup and authenticate your Amazon CloudWatch Command Line Interface
3. Create a Dynatrace API key
4. Enter your Dynatrace environment id and your API key within the dt_cw_bridge.py script
5. Configure valid timeseries ids, aggregation types and entities within the dt_cw_bridge.py script
6. Run the script by typing **python dt_cw_bridge.py**

####`API key`
The API key for your Dynatrace tenant. You can generate a key by following these steps

1. go to your Dynatrace environment: https://{tenant}.live.dynatrace.com
2. Click the burger menu in the right upper corner and select **Integration**
3. You will see the "Dynatrace API" section; 
4. Enter a description label and click on **Generate**
5. copy it and use it in your Dynatrace API examples

##License
This module is provided under BSD-3-Clause license. Please check out the details in the LICENSE.txt

