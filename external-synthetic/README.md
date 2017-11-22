## Overview
The Dynatrace external synthetic API (currently early access) allows you to send synthetic data from 3rd party or home-grown 
synthetic solutions into Dynatrace. Here you will find the current Swagger specification of the API as well as a simple
Python example to get you started.

## Example
Just replace the placeholders with your Dynatrace environment id & token and run the script.
If everything works it should return HTTP status code 204 (no content) and the synthetic data will show up in the Dynatrace UI.
Keep in mind this example only generates one data point per execution.

## License
This module is provided under BSD-3-Clause license. Please check out the details in the LICENSE.txt
