
## Overview

The tagging example demonstrates how to automatically tag monitored components that contain a specific substring pattern within
the display name. 

## Prerequisites

The full Dynatrace API documentation can be found here: 
https://help.dynatrace.com/api-documentation/v1/

1. Create a Dynatrace API key
4. Enter your Dynatrace environment id and your API key within the dt_auto_tag.py script
5. Configure a name string pattern and some tags
6. Run the script by typing `python dt_auto_tag.py`

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
