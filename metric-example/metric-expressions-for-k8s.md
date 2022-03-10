# Metric Expressions for K8s
This document collects frequently asked metric expressions for typical K8s use-cases. Listed metric expressions can be used for [charting](https://www.dynatrace.com/support/help/how-to-use-dynatrace/dashboards-and-charts/explorer/explorer-advanced-query-editor/) or alerting using [custom metric events](https://www.dynatrace.com/support/help/how-to-use-dynatrace/problem-detection-and-analysis/problem-detection/metric-events-for-alerting/advanced-metric-queries/).

**Table of contents**

<!-- TOC depthfrom:2 -->

- [Prerequisites](#prerequisites)
- [Important note](#important-note)
- [Node utilization](#node-utilization)
    - [CPU](#cpu)
    - [Memory](#memory)
- [Node conditions](#node-conditions)
- [Workload health](#workload-health)
    - [Not all pods running](#not-all-pods-running)
    - [Not all containers running](#not-all-containers-running)
- [Workloads resource utilization and optimization](#workloads-resource-utilization-and-optimization)
    - [Slack](#slack)
    - [Usage above requests](#usage-above-requests)
    - [Usage in terms of limits](#usage-in-terms-of-limits)
    - [High throttling](#high-throttling)
    - [Memory](#memory)
    - [High container restart rate](#high-container-restart-rate)
- [Further Reading](#further-reading)

<!-- /TOC -->

## Prerequisites
This document assumes basic familiarity with metric selectors. If you don't yet feel comfortable with simple metric selectors, consider reading
through [Query by Example](query-by-example.md) first.

You can try the examples listed here through the Web UI via _Data Explorer_,
or you can send selectors to the `/v2/metrics/query` API for evaluation.

## Important note
**Depending on the size of your environment, the following examples might put extreme load on your Dynatrace environment. Please use with care and try using filters whenever possible to narrow the scope of these queries.**

## Node utilization
Let's start of with some simple metric expressions to measure relative nodes utilization in terms of usage, requests and limits over time.

### CPU
For CPU **usage**, we can use the builtin:host.cpu.usage metric in combination with an entity-selector filtering for only hosts that are part of any Kubernetes cluster.
```
builtin:host.cpu.usage:avg
:filter(in("dt.entity.host", entitySelector("type(HOST),toRelationships.IS_KUBERNETES_CLUSTER_OF_HOST(type(KUBERNETES_CLUSTER),entityName())")))
```
For **requests** we can divide the requested CPU by the total number of cores available on each node.
```
(builtin:cloud.kubernetes.node.cpuRequested:avg)
/(builtin:cloud.kubernetes.node.cores:avg)
*(100)
```
The same can be done for **limits** as follows:
```
(builtin:cloud.kubernetes.node.cpuLimit:avg)
/(builtin:cloud.kubernetes.node.cores:avg)
*(100)
```
Let's reduce the scope of these queries to only nodes of a given cluster. This is especially important if you want to set up an alert in the scope of a single cluster. The scope is narrowed down to a single cluster by attaching a **filter** for the cluster entity. For **usage** this results in the following metric expression. Note: Replace *KUBERNETES_CLUSTER-44D2F1E49BE901AF* with the entity-ID of your Kubernetes cluster. The easiest way to get the entity-ID of your cluster, is to navigate to the cluster within the Dynatrace Web UI - you'll see the ID in the URL in your browser's address bar.

**Usage**
```
builtin:host.cpu.usage:avg
:filter(in("dt.entity.host", entitySelector("type(HOST),toRelationships.IS_KUBERNETES_CLUSTER_OF_HOST(type(KUBERNETES_CLUSTER),entityId(KUBERNETES_CLUSTER-44D2F1E49BE901AF))")))
```
We can further expand this query and only count nodes of a cluster with a CPU usage above a certain threshold. In other words: "How many of my cluster's nodes have CPU usage over 80%".
*Note: Replace "KUBERNETES_CLUSTER-44D2F1E49BE901AF" with the entity-ID of your Kubernetes cluster and 80 with your desired CPU usage threshold.*
```
builtin:host.cpu.usage:avg
:filter(in("dt.entity.host", entitySelector("type(HOST),toRelationships.IS_KUBERNETES_CLUSTER_OF_HOST(type(KUBERNETES_CLUSTER),entityId(KUBERNETES_CLUSTER-44D2F1E49BE901AF))")))
:filter(series(avg,gt,80)):splitby():count
```
We can modify this query to also answer the reverse question: "How many of my cluster's nodes have CPU usage below 80%". Just replace *gt* with *lt*.
```
builtin:host.cpu.usage:avg
:filter(in("dt.entity.host", entitySelector("type(HOST),toRelationships.IS_KUBERNETES_CLUSTER_OF_HOST(type(KUBERNETES_CLUSTER),entityId(KUBERNETES_CLUSTER-44D2F1E49BE901AF))")))
:filter(series(avg,lt,80)):splitby():count
```
By replacing the *usage* part of this query, we can solve the same use cases for **requests** and **limits**. For example, for **requests** the last metric expression above would result in the following query:
```
(
  (builtin:cloud.kubernetes.node.cpuRequested:avg)
  /(builtin:cloud.kubernetes.node.cores:avg)
  *(100)
)
:filter(in("dt.entity.kubernetes_node", entitySelector("type(KUBERNETES_NODE),toRelationships.IS_KUBERNETES_CLUSTER_OF_NODE(type(KUBERNETES_CLUSTER),entityId(KUBERNETES_CLUSTER-44D2F1E49BE901AF))")))
:filter(series(avg,lt,80)):splitby():count
```

### Memory
The metric expressions used for *CPU* can easily be adapted to *Memory* by just replacing the CPU related metrics with the proper memory related metric:
* builtin:cloud.kubernetes.node.cores -> builtin:cloud.kubernetes.node.memory
* builtin:cloud.kubernetes.node.cpuAvailable -> builtin:cloud.kubernetes.node.memoryAvailable
* builtin:cloud.kubernetes.node.cpuRequested -> builtin:cloud.kubernetes.node.memoryRequested
* builtin:cloud.kubernetes.node.cpuLimit -> builtin:cloud.kubernetes.node.memoryLimit

## Node conditions
For node conditions, it's important to understand, that a single node can have multiple conditions at the same time, such as, *DiskPressure* and *MemoryPressure*. Consequently, the used metric offers a dimension for each condition (node_condition), that can either be true or false (condition_status) at any given point in time. Hence, we can chart which nodes have any not-ready conditions. Of course, we can also use this metric expression for setting up a [custom event for alerting](https://www.dynatrace.com/support/help/how-to-use-dynatrace/problem-detection-and-analysis/problem-detection/metric-events-for-alerting#create-a-metric-event). Again, you could reduce the scope of this query to a single cluster by adding a proper filter.
```
builtin:cloud.kubernetes.node.conditions:
filter(and(ne(node_condition,Ready),eq(condition_status,True))):splitBy("dt.entity.kubernetes_cluster","dt.entity.kubernetes_node","node_condition"):count
```

## Workload health
Let's use metric expressions to monitor the health of our workloads. We **strongly recommend**, to scope such expressions to a single workload, by adding a **filter**. In the following examples, all expressions will be filtered to a sample workload by appending the following filter: 
```:filter(and(in("dt.entity.cloud_application",entitySelector("type(cloud_application),entityId(~"CLOUD_APPLICATION-A26E32FC302257AB~")"))))```

To adapt this to your scenario, simply replace "CLOUD_APPLICATION-A26E32FC302257AB" with the workload ID of your workload. Again, you can find the ID in the URL in your browser while viewing the workload in the Dynatrace Web UI.

### Not all pods running
Using the following query, you can find how many pods are not running compared to the number of desired pods of this workload.
```
( 
  (builtin:cloud.kubernetes.workload.desiredPods):splitBy("dt.entity.cloud_application")
  -(builtin:cloud.kubernetes.workload.pods):splitBy("dt.entity.cloud_application")
)
:filter(and(in("dt.entity.cloud_application",entitySelector("type(cloud_application),entityId(~"CLOUD_APPLICATION-A26E32FC302257AB~")"))))
```

### Not all containers running
Using the following query, you can find how many containers are not running compared to the number of desired containers of this workload.
```
( 
  (builtin:cloud.kubernetes.pod.desiredContainers):parents:splitBy("dt.entity.cloud_application")
  -(builtin:cloud.kubernetes.pod.containers):parents:splitBy("dt.entity.cloud_application")
)
:filter(and(in("dt.entity.cloud_application",entitySelector("type(cloud_application),entityId(~"CLOUD_APPLICATION-A26E32FC302257AB~")"))))
```

## Workloads resource utilization and optimization
Let's use some metric expressions to understand if we have **proper requests and limits** in place for our workloads. 
We start by looking into the relation between usage and requests. Usually, one tries to have usage just below requests. So which workloads are requesting far more CPU or Memory, than they actually use - this is usually referred to as *slack*. The following examples will only walk you through CPU related topics. They can easily by adapted to memory, by replacing the CPU metrics with their memory counterpart metrics. 

### Slack
```
(
    (builtin:cloud.kubernetes.pod.cpuRequests:parents:splitBy("dt.entity.cloud_application_instance","dt.entity.cloud_application"):avg)
    -(builtin:containers.cpu.usageMilliCores:parents:parents:splitBy("dt.entity.cloud_application_instance","dt.entity.cloud_application"):avg)
)
:splitBy("dt.entity.cloud_application"):avg
:filter(and(in("dt.entity.cloud_application",entitySelector("type(cloud_application),entityId(~"CLOUD_APPLICATION-A26E32FC302257AB~")"))))
```
*Note: We are using **:parents**, to split and filter by entities that are higher in the Kubernetes entity hierarchy (container -> pod -> workload -> namespace -> cluster).
You can also increase the scope of this query to multiple workloads by expanding the scope of the filter or just removing it. Just be aware, that in very large environments this can put a lot of stress on your Dynatrace environment.

### Usage above requests
Using the following query, we can see which workloads have a higher CPU usage than requested. Meaning, for such workloads one should consider increasing the set requests to increase the stability of the workload as well as the stability of the Kubernetes cluster it is running on.
```
(
    (builtin:containers.cpu.usageMilliCores:parents:parents:splitBy("dt.entity.cloud_application_instance","dt.entity.cloud_application"):avg)
    -(builtin:cloud.kubernetes.pod.cpuRequests:parents:splitBy("dt.entity.cloud_application_instance","dt.entity.cloud_application"):avg)
)
:splitBy("dt.entity.cloud_application"):avg
:filter(and(in("dt.entity.cloud_application",entitySelector("type(cloud_application),entityId(~"CLOUD_APPLICATION-A26E32FC302257AB~")"))))
```

### Usage in terms of limits
Users afraid of throttling, often want to alert on the percentage of limits being used. However, we suggest to alert on throttling relative to usage. The reason for this is, that the relative usage in terms of limits is not the only deciding factor for when Kubernetes starts to throttle containers - we'll cover that in the next example.
```
(
    (builtin:containers.cpu.usageMilliCores:avg:parents:parents:splitBy("dt.entity.cloud_application_instance","dt.entity.cloud_application"):sum)
    /(builtin:cloud.kubernetes.pod.cpuLimits:avg:parents:splitBy("dt.entity.cloud_application_instance","dt.entity.cloud_application"):sum)
    *(100)
)
:splitBy("dt.entity.cloud_application"):avg
:filter(and(in("dt.entity.cloud_application",entitySelector("type(cloud_application),entityId(~"CLOUD_APPLICATION-A26E32FC302257AB~")"))))
```

### High throttling
As mentioned, it makes more sense to alert on the outcome rather than only on one of multiple potential triggers for throttling. In other words, track throttling relative to usage instead of usage in terms of limits.
```
(
    (builtin:containers.cpu.throttledMilliCores:avg:parents:parents:splitBy("dt.entity.cloud_application_instance","dt.entity.cloud_application"):sum)
    /(builtin:containers.cpu.usageMilliCores:avg:parents:splitBy("dt.entity.cloud_application_instance","dt.entity.cloud_application"):sum)
    *(100)
)
:splitBy("dt.entity.cloud_application"):avg
:filter(and(in("dt.entity.cloud_application",entitySelector("type(cloud_application),entityId(~"CLOUD_APPLICATION-A26E32FC302257AB~")"))))
```

### Memory
Most of the metric expressions shown above can be adapted for memory related use cases by simply replacing the CPU metrics with the proper memory metrics. However, there is one important difference: While high CPU usage leads to throttling, high memory usage leads to out-of-memory kills, and thus container restarts. Consequently, it makes sense to keep track of container restarts. 

### High container restart rate
```
(
  (builtin:cloud.kubernetes.pod.containerRestarts:max:default(0):delta:parents)
  :splitBy("dt.entity.cloud_application")
  :sum
)
:splitBy("dt.entity.cloud_application"):sum
:filter(and(in("dt.entity.cloud_application",entitySelector("type(cloud_application),entityId(~"CLOUD_APPLICATION-A26E32FC302257AB~")"))))
```
*Note: Be aware, that the restart metric for containers is only available if we observed at least one restart. Consequently, for pods with no container restarts, there won't be any data.*

## Further Reading
Please refer to the documentation on metric expressions on [dyntrace.com](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2/metric-expressions/)
for additional technical details such as: precedence of operators, semantics for combinations of point/series results and literals, null handling, time alignment, many others.
