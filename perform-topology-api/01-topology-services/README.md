Perform 2018 - Sample 1

This example is a slightly modified version of the [topology-smartscape](https://github.com/Dynatrace/dynatrace-api/tree/master/topology-smartscape) example.

It represents a base solution that is able to visualize a service map. The required data is getting queried from via Dynatrace Topology and Smartscape API via REST Calls.
Visualization is taken care of by Sigma.js.

Clicking on one of the nodes creates an alert box.

To use this example with your own Dynatrace environment, just replace the placeholder with your own environment id and API key. 