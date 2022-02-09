# Metric Expressions for K8s
This document collects frequently asked metric expressions for typical K8s use-cases. Listed metric expressions can be used for [charting](https://www.dynatrace.com/support/help/how-to-use-dynatrace/dashboards-and-charts/explorer/explorer-advanced-query-editor/) or alerting using [custom metric events](https://www.dynatrace.com/support/help/how-to-use-dynatrace/problem-detection-and-analysis/problem-detection/metric-events-for-alerting/advanced-metric-queries/).

## Prerequisites
This document assumes basic familiarity with metric selectors. If you don't yet feel comfortable with simple metric selectors, consider reading
through [Query by Example](query-by-example.md) first.

You can try the examples listed here through the Web UI via _Data Explorer_,
or you can send selectors to the `/v2/metrics/query` API for evaluation.

## Important note
Depending on the size of your environment, the following examples might put extrem load on your Dynatrace environment. Please use with care and try using filters whenever possible to narrow the scope of these queries.

## K8s

### Nodes utilization
Measure relative nodes utilization in terms of usage, requests and limits over time.
#### CPU
*Usage*
```
(
  (builtin:cloud.kubernetes.node.cores:avg)
  - (builtin:cloud.kubernetes.node.cpuAvailable:avg)
)
/(builtin:cloud.kubernetes.node.cores:avg)
*(100)
```
*Requests*
```
(builtin:cloud.kubernetes.node.cpuRequested:avg)
/(builtin:cloud.kubernetes.node.cores:avg)
*(100)
```
*Limits*
```
(builtin:cloud.kubernetes.node.cpuRequested:avg)
/(builtin:cloud.kubernetes.node.cores:avg)
*(100)
```
Let us reduce the scope of this query to nodes of a given cluster. This is especially important if you want to set up an alert in the scope of a single cluster. The scope is narrowed down to a single cluster by attaching a *filter* for the cluster entity. E.g., for usage this would result in the following metric expresion. Note: Replace *KUBERNETES_CLUSTER-A943C5CF0A41A684* with the entitiy-id of your Kubernetes cluster.

*Usage*
```
(
    (
      (builtin:cloud.kubernetes.node.cores:avg)
      - (builtin:cloud.kubernetes.node.cpuAvailable:avg)
    )
    /(builtin:cloud.kubernetes.node.cores:avg)
    *(100)
)
:filter(in("dt.entity.kubernetes_node", entitySelector("type(KUBERNETES_NODE),toRelationships.IS_KUBERNETES_CLUSTER_OF_NODE(type(KUBERNETES_CLUSTER),entityId(KUBERNETES_CLUSTER-A943C5CF0A41A684))")))
```
We can further expand this query and only count nodes of a cluster with a CPU usage above a certain threshold. In other words: "How many of my cluster's nodes have CPU usage over 80%".
Note: Replace *KUBERNETES_CLUSTER-A943C5CF0A41A684* with the entitiy-id of your Kubernetes cluster and 80 with your desired CPU usage threshold.
```
(
    (
      (builtin:cloud.kubernetes.node.cores:avg)
      - (builtin:cloud.kubernetes.node.cpuAvailable:avg)
    )
    /(builtin:cloud.kubernetes.node.cores:avg)
    *(100)
)
:filter(in("dt.entity.kubernetes_node", entitySelector("type(KUBERNETES_NODE),toRelationships.IS_KUBERNETES_CLUSTER_OF_NODE(type(KUBERNETES_CLUSTER),entityId(KUBERNETES_CLUSTER-A943C5CF0A41A684))")))
:filter(series(avg,gt,80)):splitby():count
```
We can modify this query to also answer the reverse question: "How many of my cluster's nodes have CPU usage below 80%". Just replace *gt* with *lt*.
```
(
    (
      (builtin:cloud.kubernetes.node.cores:avg)
      - (builtin:cloud.kubernetes.node.cpuAvailable:avg)
    )
    /(builtin:cloud.kubernetes.node.cores:avg)
    *(100)
)
:filter(in("dt.entity.kubernetes_node", entitySelector("type(KUBERNETES_NODE),toRelationships.IS_KUBERNETES_CLUSTER_OF_NODE(type(KUBERNETES_CLUSTER),entityId(KUBERNETES_CLUSTER-A943C5CF0A41A684))")))
:filter(series(avg,lt,80)):splitby():count
```
By replacing the *usage* part of this query, we can solve the same use-cases in terms of *requests* and *limits*. E.g., for *requests* the last metric expression above would result in the following query:
```
(
  (builtin:cloud.kubernetes.node.cpuRequested:avg)
  /(builtin:cloud.kubernetes.node.cores:avg)
  *(100)
)
:filter(in("dt.entity.kubernetes_node", entitySelector("type(KUBERNETES_NODE),toRelationships.IS_KUBERNETES_CLUSTER_OF_NODE(type(KUBERNETES_CLUSTER),entityId(KUBERNETES_CLUSTER-A943C5CF0A41A684))")))
:filter(series(avg,lt,80)):splitby():count
```
#### Memory
The metric expresions used for *CPU* can easily be adapted to *Memory* by just replacing the CPU related metrics with the proper memory related metric metric:
* builtin:cloud.kubernetes.node.cores -> builtin:cloud.kubernetes.node.memory
* builtin:cloud.kubernetes.node.cpuAvailable -> builtin:cloud.kubernetes.node.memoryAvailable
* builtin:cloud.kubernetes.node.cpuRequested -> builtin:cloud.kubernetes.node.memoryRequested
* builtin:cloud.kubernetes.node.cpuLimit -> builtin:cloud.kubernetes.node.memoryLimit

### Node conditions
For node conditions, it's important to understand, that a single node can have multiple conditions at the same time. Consequently, the used metric offers a dimension for each condition (node_condition), that can either be true or false (condition_status) at any given point in time. Hence, we can chart which nodes have any not-ready condition. Of course, we can also use this metric expression for setting up an alert.
```
builtin:cloud.kubernetes.node.conditions:
filter(and(ne(node_condition,Ready),eq(condition_status,True))):splitBy("dt.entity.kubernetes_cluster","dt.entity.kubernetes_node","node_condition"):count
```

### Workloads
Let's use some metric expressions to understand if we have proper requests and limits in place for our workloads. We start by looking into the relation between usage and requests. Usually, one tries to have usage just below reqeuest. So which workloads are requesting far more CPU or Memory, than they actually use - this is usually refered to as *slack*.


## Further Reading
Please refer to the documentation on metric expressions on [dyntrace.com](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2/metric-expressions/)
for additional technical details such as:
* precedence of operators,
* semantics for combinations of point/series results and literals,
* null handling,
* time alignment,
* many others.
