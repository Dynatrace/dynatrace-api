## Dynatrace external synthetic API examples

The Dynatrace external synthetic API allows you to push synthetic data from 3rd party or home-grown 
synthetic solutions to Dynatrace. Here are some example implementations to get you started.

### Python

See `externalSyntheticExample.py` for a generic example written in Python.

Just replace the placeholders with your Dynatrace environment id & token and run the script.
If everything works it should return HTTP status code 204 (no content) and the synthetic data will show up in the Dynatrace UI.

Keep in mind this example only generates one data point per execution.

### AWS CloudWatch

Check the `aws-cloudwatch` folder for examples of how to push canary results to the API.

## License
This module is provided under BSD-3-Clause license. Please check out the details in LICENSE.txt
