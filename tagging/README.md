
## Overview

The tagging example demonstrates how to automatically tag monitored components that contain a specific substring pattern within
the display name. 

### Prerequisites

The full Dynatrace API documentation can be found here: 
https://help.dynatrace.com/api-documentation/v1/

1. Create a Dynatrace API key
4. Enter your Dynatrace environment id and your API key within the dt_auto_tag.py script
5. Configure a name string pattern and some tags
6. Run the script by typing **python dt_auto_tag.py**

####`API key`
The API key for your Dynatrace tenant. You can generate a key by following these steps

1. go to your Dynatrace environment: https://{tenant}.live.dynatrace.com
2. Click the burger menu in the right upper corner and select **Integration**
3. You will see the "Dynatrace API" section; 
4. Enter a description label and click on **Generate**
5. copy it and use it in your Dynatrace API examples

##License
This module is provided under BSD-3-Clause license. Please check out the details in the LICENSE.txt

