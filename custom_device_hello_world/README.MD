# Custom Device Hello World

This Python script is intended as 'Hello World' custom device example that fulfills following demo use-cases:

1. Creation of a custom device
2. Reporting of custom properties and tags for the custom device
3. Registration of a custom metric that is bound to that type of custom device
4. Registration of a threshold that raises an event when custom metric is out of regular boundaries
5. Reporting of random values for the custom metrics
6. Daily problem pattern triggering between 11 and 12 

## Operation and deployment of the script

The script was designed to report random values in a stateless manner. The script should be called every minute. 
It is strongly suggested to run this script in a minute Cron-job, which gives you the full demo experience within Dynatrace.

## Necessary parameters

**YOUR_DT_API_URL** must be replaced with your own environments API URL
**YOUR_API_TOKEN** must be replaced with your own environments API token
