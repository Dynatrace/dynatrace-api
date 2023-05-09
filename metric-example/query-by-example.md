# Query by Example
The REST API for metrics gives you access to timeseries data, such as CPU utilization of a host or service or the bounce rate of a web application. For instance, free disk space, per host, per disk is uniquely identified with `builtin:host.disk.avail`. This hierarchical identifier is referred to as a metric key.

A plain metric key is also the simplest form of a metric selector, which is used to specify one or more metrics to the Metric REST API for query, with the option to have the API perform additional transformations on the metric data, such as taking the average, sorting the result, or keeping only data points for satisfied users.

## Prerequisites

Before jumping into the usage scenarios, make sure that you have the following information at hand:

*   the host and path of the Dynatrace instance you want to run metric queries against, below referred to as `{base}` 

	- for Managed clusters: `{base}` is `https://{your-domain}/e/{your-environment-id}/api/v2`
	- for SaaS: `{base}` is `https://{your-environment-id}.live.dynatrace.com/api/v2`
*   a valid API-token with the `MetricsRead` permission ("Read metrics" in the UI) for the host.

Some of the examples use `curl` to make the actual requests. If you are comfortable with testing an API using the terminal, make sure you have it installed.

Alternatively, use a REST client like [Insomnia](https://insomnia.rest/) or [Postman](https://www.postman.com/), both of which support importing curl commands.

## Scenario 1: Explore Metrics, Dimensions, Aggregation Techniques

> **Task**
> We want to get a list of available metrics.

The endpoint `{base}/metrics` provides access to all metrics that can be queried. Essential metadata is bundled together as a _descriptor_.

We will list metric keys with only essential metadata, formatted as a CSV table, by querying:

```
GET {base}/metrics
Authorization: Api-Token <do not forget your token>
Accept: text/csv
```

As a curl command:
```
curl -XGET -H "Authorization: Api-Token `<do not forget your token>`" -H 'Accept: text/csv' "{base}/metrics"
```

The result is newline-separated and suitable for viewing in Spreadsheet applications like _Microsoft Excel_ or other machine-supported processing:

```
metricId
builtin:cloud.vmware.hypervisor.nic.packetsTxDropped
builtin:cloud.vmware.hypervisor.nic.dataRx
builtin:cloud.vmware.hypervisor.nic.dataTx
...
```

The metric key alone only gives us a vague idea about what data the metric provides. To learn more about the metrics we can select optional fields using the fields parameter.

When omitting `fields`, then `metricId`, `displayName`, `description` and `unit` will be included in the descriptor. If we are only interested in keys, but not in the metadata, the `fields` parameter can be set to only the fields of interest, e.g. just `metricId`:

```
GET {base}/metrics?fields=metricId
```

Conversely, metadata can be added to the basic four properties by setting fields to a comma-separated list of property names, starting with +:

```
GET {base}/metrics?fields=+dduBillable,+created,+lastWritten,+entityType,+aggregationTypes,+transformations,+defaultAggregation,+dimensionDefinitions,+tags,+metricValueType
```

The display names and descriptions give us an idea about the contained data. Another critical piece of information is the list of available aggregation techniques. For instance, it is valid to request the average CPU utilization, but the API will reject any request for the median, since it does not make sense for that specific metric.

## Scenario 2: Select One Metric With Full Metadata

> **Task**
> We found an interesting metric and we would like to get more information about what data it provides and which queries we can actually do.

Depending on how Dynatrace is used, there may be hundreds or even thousands of metrics available. When learning more about metrics, we are often only interested in a handful of metrics. Requesting a single metric can be done by using a metric key from before as a _metricId_ path component:

```
GET {base}/metrics/builtin:host.cpu.usage
Accept: text/csv
```

Note that a full descriptor with all optional fields included is returned when requesting a single metric as a path parameter. Any field name returned here can also be used for the `fields` parameter on `/metrics`.

## Scenario 3: Select Multiple Metrics with Tuples

>**Task**
>We want metadata of two related metrics to compare them.

What is the difference between CPU `builtin:host.cpu.system` and `builtin:host.cpu.user`? We can find out by forming a selector that matches the metric key for both and access both descriptors in a single call. This can be done by gluing multiple metric keys together with a comma character:

```
builtin:host.cpu.system,builtin:host.cpu.user
```

Since this usage pattern is often used, there is a shorthand for it. Instead of a plain word, a dot-separated selector component can also be a _tuple_, which defines multiple alternatives in parentheses. The following is semantically identical to the above selector:

```
builtin:host.cpu.(system,user)
```

To filter the descriptor collection down to these two metrics, provide them as a `metricSelector` query parameter (not path parameter):
```
GET {base}/metrics?metricSelector=builtin:host.cpu.(system,user)
Accept: text/csv
```

## Scenario 4: List Metric Sub-Trees with Wildcards

>**Task**
>We would like to search for all metrics for a certain topic.

Sometimes, we are not only interested in similar keys with a common parent, but we want all metrics in a specific sub-tree. For instance, how do we find out about all CPU-related Host metrics? We can easily use a wildcard selector for this purpose:

```
builtin:host.cpu.*
```

Note that wildcard selectors are allowed for descriptor queries, but not for bulk metric data queries. Such bulk queries have an upper bound of twelve metrics at a time, and allowing wildcards in a query would make adding new metric keys a breaking change.

## Scenario 5: Full-text Metric Search

>**Task**
>We would like to search for all metrics that mention a specific concept in their ID, display name, or description.

Not all CPU metrics are captured on host level, like `builtin:host.cpu.system`. How do we find out about CPU metrics on PGI or container level?

Let's use the `text` parameter with `/metrics` and set it to "cpu" to search for other CPU-related metrics:

```
GET {base}/metrics?text=cpu
```

Turns out there are a whole lot of other metrics related to CPU! Most of them include `cpu` in the metric key, but e.g. `builtin:cloud.kubernetes.cluster.cores` does not. Why does it show up in the result, then? It does because `text` also uses the display name and the description for this search. This is also what the Data Explorer uses to present available metrics when you start typing into the metric field.

## Scenario 6: Querying Time Series Data

>**Task**
>We would like to query CPU usage on some hosts during the last 2 weeks.

Querying works by supplying a metric selector to the `{base}/metrics/query?metricSelector={selector}` end point. Assuming we are interested in the average utilized CPU time of all hosts in our cluster individually we might issue the following request:

```
GET {base}/metrics/query?metricSelector=builtin:host.cpu.usage
```

Note that while not strictly part of the metric selector, there are some closely related GET parameters. If they are left out, default parameters are assumed:

| Query parameter | Example | Default value | Description |
|:---|---|---|---|
| `from` | `1554798800839` | `now-2w` | Lower bound of query timeframe |
| `to` | `2019-06-03` | `now` | Upper bound of query timeframe |
| `resolution` | `1m`, `12h`, `60` | `120` | Desired data point count (unit-less) or step between data points (with unit of time) |

The above query yields a result in the following format when the output format is chosen to be CSV:

```
metricId,dt.entity.host,time,value
builtin:host.cpu.usage,HOST-F1266E1D0AAC2C3C,2019-03-26 12:00:00,7.547508145734597
builtin:host.cpu.usage,HOST-F1266E1D0AAC2C3C,2019-03-26 15:00:00,10.327820480510752
builtin:host.cpu.usage,HOST-F1266E1D0AAC2C3C,2019-03-26 18:00:00,9.816637022694524
```

## Scenario 7: Aggregation with Basic Transformer Chains

>**Task**
>We want to look at the peak CPU usage

Metric result data for each time slot is processed by a value extraction function. Such a function is also referred to as sample statistic or (time) aggregation function. Consider the CPU utilization metric. Assuming that utilization is recorded every second, how can sixty second recordings be combined into a value for the containing minute? If revenue is recorded per month, how are the month samples combined into the revenue of the whole year?

If the selector is a plain metric key, the API uses the default aggregation method to solve this problem, which can be queried with the metric descriptor. This behavior can easily be overridden with a transformer, e.g. if we are interested in the maximum CPU utilization (instead of the default of the arithmetic mean) in a given time slot we can use this request:
```
GET {base}/metrics/query?metricSelector=builtin:host.cpu.usage:max
```
Note that each metric allows at least one value extraction function, but some may not be available or not make sense for a metric. Any attempt to use an incompatible technique results in an error.

To check for available aggregation techniques, obtain the array in `/metrics/<metric ID>` under the `"aggregationTypes"` field. Depending on the metric, any of the following might be supported and hence contained in the array:

| Aggregation | Meaning | Uses |
| --- | --- | --- |
| `min` | Aggregate time slot values into one by selecting the lowest value, ignoring `null` | CPU, Traffic, Load time, etc. |
| `max` | Aggregate time slot values into one by selecting the highest value, ignoring `null` | CPU, Traffic, Load time, etc. |
| `avg` | Aggregate time slot values into one by taking the arithmetic mean, ignoring `null` | CPU, Traffic, Disk space, etc. |
| `sum` | Sums up values in the time slot, ignoring `null` | Network Throughput, Disk Throughput |
| `value` | Take a single value as-is. | Counters, previously aggregated values |
| `count` | Determines the value count in the time slot, not counting `null` | Response time, Action duration |
| `percentile(N)` | Estimates the n-th percentile, where N in range [0,100) is mapped to p in range [0,1) | Response time, Action duration |

Percentile aggregations are available for many response-time-based metrics. The count is often useful to determine the reliability of quantile estimations. Generally, more samples allow for a more exact estimation or more exact averages.

Time aggregation methods are actually the simplest form of a more general concept, namely result transformers. All transformers modify the underlying metric to create a new one with possibly different dimensions, available aggregation types and data point values. Either dimension tuples are extended, trimmed or modified, result rows are removed, or, as before, the techniques used to derive numbers from associated data are changed.

If we want to observe the changed properties of a metric after transformation, we can access its _descriptor_, just like with a plain metric. See how the available aggregation types in the descriptor change, when the aggregation is already specified (line wrapping for better brevity, the actual response contains newlines only to break apart lines of the result CSV):
```
GET {base}/metrics/builtin:apps.web.sessionDuration:avg
Accept: text/csv
    
metricId,displayName,description,unit,dduBillable,entityType,  
aggregationTypes,transformations,defaultAggregation,dimensionDefinitions,  
lastWritten,created,tags,metricValueType,rootCauseRelevant,impactRelevant,  
minimumValue,maximumValue  
builtin:apps.web.sessionDuration:avg,Session duration,,MicroSecond,false,  
[APPLICATION],"[auto, value]","[filter, fold, limit, merge, names, parents, splitBy]",  
value,"[dt.entity.application:ENTITY, Users:STRING, User type:STRING]",1611848280066,  
,[],unknown,,,,
```
Observing the transformed descriptor is especially useful with more complex transformer chains.

## Scenario 8: Find CPU hogs

>**Task**
>We just queried CPU data and found a host with abnormally high CPU utilization, but it might not be the only one. How do we query for the 3 hosts with the highest average CPU utilization right now?

We just queried
```
{base}/metrics/query?metricSelector=builtin:host.cpu.usage&from=now/d
```
and get back results for some thousands of hosts. Looking at the data, most hosts in `builtin:host.cpu.usage` seem to behave normally, but some have extremely high CPU utilization. Hopefully, none of the high-CPU hosts were overlooked. We decide to query for the 3 hosts where the CPU utilization percentage was highest today (on average).

Using `:sort(avg, descending)` would put the hosts on top that have the highest average over the whole series.

What does this mean exactly? To compare one series to the other, it is necessary to reduce each series to a single number that can easily be compared to other series. `avg` does just that by extracting an average from the series for use by the sort operator. Note that the output of the `sort` operator will not be this average (which is only used for comparison), but the full series that the average was derived from.

More generally, `avg` is called a _rollup_. Other examples of rollups are `max` for the peak value of each series or `sum` for the sum of all values in the series. Apart from sorting, rollups can also be used to filter a series based on whether or not they exceed a certain threshold, replace a series with the rolled-up value, or to calculate a seven day incidence.

Back to our example with CPU utilizations: With just `:sort(avg, descending)`, we would still have a lot of low-utilization hosts further down that we are not interested in right now.

The solution is to combine `:sort` with `:limit(N)`, which keeps the first N results and drops the rest:
```
builtin:host.cpu.usage  
: sort(  
	value(avg, descending)  
)
: limit(3)
```
The order of transformations is important for the overall meaning of the query. Transformations are evaluated left to right and line-wise top to bottom. Since limit is evaluated after sort, it will only cut off the low-CPU hosts. Writing multi-line selectors like the one in the example can make complex metric selectors more readable than the single-line version.

The result looks promising, but `HOST-10000000000000` is not exactly human-readable:
```
metricId,dt.entity.host,time,value  
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3)",HOST-30000000000000,1610992260000,71.592474088881172
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3)",HOST-30000000000000,1610995860000,71.97523692696515
[...]
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3)",HOST-10000000000000,1610992260000,68.546555923312308
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3)",HOST-10000000000000,1610995860000,64.51643715911996
[...]
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3)",HOST-20000000000000,1610992260000,60.54574979701455
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3)",HOST-20000000000000,1610995860000,64.8794602031501
[...]
```

Note: `[...]` indicates that data points have been left out for brevity.

Add an additional transformation `:names` to also find out about the hostname:
```
metricId,dt.entity.host.name,dt.entity.host,time,value  
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3):names",eu.example.com,HOST-5928C8E47F4BFE45,1610992380000,71.592501233253316
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3):names",eu.example.com,HOST-5928C8E47F4BFE45,1610995860000,71.97523692696515
[...]
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3):names",us.example.com,HOST-E35417DEC6EDCF40,1610992380000,68.54627779165626
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3):names",us.example.com,HOST-E35417DEC6EDCF40,1610995860000,64.51643715911996
[...]
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3):names",staging.example.com,HOST-E398C6694A573CC2,1610992380000,60.545800811738996
"builtin:host.cpu.usage:sort(value(avg,descending)):limit(3):names",staging.example.com,HOST-E398C6694A573CC2,1610995860000,64.8794602031501
[...]
```
That's better. You can see that by combining transformations, we can design powerful queries and slice and dice the data as we need it.

## Scenario 9: Peak CPU Usage
>**Task**
>Given measurements of CPU utilization percentages, how can we find the peak values of the top series?

In the previous example we sorted a series based on a _rollup_ called `avg`. Now we want to check for outliers, so we use the `max` _rollup_, resulting in the series with the highest peaks appearing first:
```
builtin:host.cpu.usage
: sort(  
	value(max, descending)  
)
: limit(3)
```

This works, but how high was the peak, exactly, for the series shown? Just scanning through the three series in the result and getting the top value will give us a subtly wrong result for this example: since no time aggregation was specified, we rely on the default aggregation to aggregate the samples in the time slots to one value. For `builtin:host.cpu.usage`, the default aggregation is average, not maximum. Hence, we do not even see the exact value we used for sorting in the result.

Adding `:max` at the end of our selector would change the time aggregation so that we see the maximum sample in each time slot, but we would still have to go through all of the values to find the peak, which seems tedious.

Instead, let's add `:fold(max)` and let the metric API figure out the peak for us. The purpose of `fold` is to reduce series to a single value. A rollup function (`max`) may be provided as an argument. For example:
```
builtin:host.cpu.usage
: sort(  
	value(max, descending)  
)
: limit(3)
: fold(max)
```

Now, each result holds exactly one value, and that value is the peak.

## Scenario 10: Combine Series and Point Queries with Folding

>**Task**
>For a report, we want to query both per-month CPU usage, but also get an overall average.

We have already seen `fold` in action to extract a peak value.
In some situations, it is useful to have such a summary value together with the full series, that is, a mixed result with some series results and some related point results.

Say we want to access `builtin:host.cpu.usage` over the complete last year from January to just before January this year (`now-y/y` to `now/y`). We want a resolution of `1M`, but we are also interested in the average value over the whole year. This can be done in a single bulk query, once using `:fold(avg)` and once omitting it:
```
GET {base}/metrics/query?metricId=builtin:host.cpu.usage:fold(avg),builtin:host.cpu.usage&from=now-y/y&to=now/y&resolution=1M
```

Any of `min`, `max`, `avg`, `median`, `percentile(N)`, `sum`, `count` or `auto` can be used here as an argument for the fold, regardless of which aggregation types are supported by the metric, e.g. `builtin:host.cpu.usage:fold(median)` is perfectly legal and will calculate an estimation for a median sample over time for each host.

It is also legal to not specify any arguments for `:fold`. In this case measurements over time are merged, but no value is extracted yet. How exactly this merging works depends on the metric. Any time aggregation that was supported before the fold can be applied later, e.g. `builtin:host.cpu.usage:fold:min`. Leaving out the time aggregation will lead to the default aggregation being applied as the last step.

## Scenario 11: Average Session Duration of Non-robot First-time Users with Advanced Transformer Chains

>**Task**
>We need to provide data on average session duration, but filter out some unwanted types of visits which do not represent a real user.

With what we have learned up until now, no metric seems to be a perfect match for the following use case: We want to calculate the average session duration of first-time users, regardless of whether the user is synthetic or a real user. Some metrics come close, but are not perfect. Luckily, transformer chains allow us to derive new metrics from existing ones that exactly meet our needs.

Consider for example `builtin:apps.web.sessionDuration`. Looking at response data we see that it does give us the session duration, and whether the visitor was new, but also reports recurring users and robots, cluttering our result with data that we don't need:
```
metricId,dt.entity.application,VisitorType,VisitType,time,value
builtin:apps.web.sessionDuration,APPLICATION-DFD07AE5A6077853,RECURRING_VISITOR,REAL_USER,2019-04-09 13:31:00,7.0866E7
builtin:apps.web.sessionDuration,APPLICATION-923D6049CBA84FBD,NEW_VISITOR,ROBOT,2019-04-09 13:31:00,4.61475E7
...
```
Chaining multiple transformers together, we can derive a new metric from `builtin:apps.web.sessionDuration` that does exactly what we need. For this, we need `:filter` and `:splitBy` in our tool box.

Examining the result data we see that additional dimensions tell us whether the numbers were recorded for new visitors or recurring ones and whether the visit was from a robot, a synthetic user or a real user. We are only interested in new visitors that are not robots. Whether they are synthetic or real is irrelevant for our use case.

Dropping robots is easy with :`filter`, which drops results based on a condition. The condition may contain logical connectives and can perform checks on the values of dimension. Our expectations can be formalized as follows: `VisitorType` should be equal to `NEW_VISITOR`, while `VisitType` needs to be not equal to `ROBOT`. This can be expressed in terms of a filter, which we can append to our metric selector:
```
:filter(and(eq(VisitorType,NEW_VISITOR),ne(VisitType,ROBOT)))
```
We observe that the payload has changed to only contain the result data we are interested in. For each application, two data points remain per timeslot, one for `SYNTHETIC`, and one for `REAL_USER`, while the visitor type is constant at `NEW_VISITOR`. We actually want the average of synthetic and real, so that we have one data point per application. We can easily view them as a combined data point by using a `splitBy` transformer. The transformer merges all dimensions that are not passed as arguments to it:
```
:splitBy(dt.entity.application)
```
Combining our `:filter` and `:splitBy` transformations, we see that we have solved our problem and get the data in the exact format that we need it in:
```
metricId,dt.entity.application,time,value
"builtin:apps.web.sessionDuration:filter(and(eq(VisitorType,NEW_VISITOR),ne(VisitType,ROBOT))):splitBy(dt.entity.application)",APPLICATION-1AF167A3A7B45A8A,2019-04-09 00:00:00,20.51584226122635
...
```
Note how the semantics of the transformer chain change with the ordering of the transformers. The filter does not make sense after the splitBy.

We get an error since we just merged the visitor type and then tried to filter on the dimension we just removed.

## Scenario 12: Service Response Time in the 99th Percentile
>**Task**
>For our payment service, we query the maximum response time of the last day to visualize it as a KPI on a dashboard. Unfortunately the maximum is very sensitive to outliers. Can we make our KPI more robust?

We regularly query `builtin:service.response.time` for the peak response time of our payment service during the last day. We use `:filter` to get just the payment service, `:max` to get the maximum per time slot, and we use `:fold(max)` to get just the peak value:
```
builtin:service.response.time
: filter(eq(dt.entity.service, "SERVICE-1234567890"))
: max
: fold(max)
```

This query worked well at first, but since a couple of days the pen testing crew of our company is running tests against our live payment service every 10 hours to verify that it is robust when hit by a nasty kind of DoS attack called [Slowloris](https://en.wikipedia.org/wiki/Slowloris_(computer_security)). The idea of this attack is to perform many parallel requests that only send headers but never finish the HTTP request. These requests are sent with the lowest possible bandwidth that does not time out the request. For a vulnerable system, this could block all threads that handle incoming requests since they are all waiting for a request to complete that will never be done.

Luckily, we are not experiencing any operational issues from the tests, but we notice that the response times of the tests now completely dominate our KPI, rendering it unusable to check whether or not the response time for our customers is acceptable. The KPI shows response times of several hours, but when we query the series without fold, we see the maximum response time is well under 100ms for hours where no pen tests were run. Somehow, we still want to use one of thse maxima as an indicator of how fast our slowest requests complete, but instead of the real maximum, we decide that we want to query the time slot that has a reponse time that is higher than 90% of the response times but smaller than the remaining 10%. This way, our pen tests will not influence our KPI.

Put differently, we want to extract an estimation for the 90th percentile of the response times in the query time frame:
```
builtin:service.response.time
: filter(eq(dt.entity.service, "SERVICE-1234567890"))
: max
: fold(percentile(90))
```

Works like a charm, now our KPI is less sensitive to outliers.

Note that any rollup can be used in `fold` - It is not necessary for the metric to support it as a time aggregation. For example, it is perfectly legal to get the median CPU utilization over time with `builtin:host.cpu.usage:fold(median)`, but getting the median per time slot with `:median` for that metric would be an error.

Also note that applying a time aggregation right before a fold with the same aggregation kind used as a rollup is optional. If `metric` supports `min`, then `metric:fold(min)` behaves the same as `metric:min:fold(min)`. If the metric in the first example does not support `min` but has not been in another way before folding, then `auto` will be used.

## Scenario 13: Weighted and Unweighted Averages of Sales
>**Task**
> Given a gauge metric that tracks every sale, split by a product ID, what's the average daily price for product 42 in the last two weeks? What is the average daily revenue of product 42 in the last two weeks?

The prime use case for gauge metrics is regular sampling, e.g. of a temperature, but in Dynatrace you can also use it to track statistical summaries of events that occur in irregular intervals. For instance, `builtin:tech.php.phpGc.durationMs` receives a duration in milliseconds after each run of the PHP garbage collector. If the garbage collector does not run, no value is reported.

Such event-style gauge metrics can be used for other kinds of measurements too.
Our own metric `sales` reports one data point for each sale of a product, namely the price we sold it for, with the product ID stored in the dimension `id`. The price varies over time due to a number of factors: some customers get a premium discount and we also offer a best-price guarantee so we are obligated to give an equivalent or better offer if a customer shows us that a competitor offers a cheaper price.

First we want to get data for the last two weeks with days resolution so we set `from` to `now-2w` and we set `resolution` to `d`.

Now we want to write the selector. All of the aggregation types kind of make sense for our event-based sales metric: the number of sales for a product/timeslot is `sales:count`, the total revenue for it is `sales:sum`, the average selling price in the time slot is `sales:avg` and the best/worst price are either `sales:min` or `sales:max`, depending on your perspective. Note that if no price is reported in a time slot of a query response, then the value will be `null`, regardless of the sample statistic in use. We will learn later on in this scenario how to deal with such data gaps.

Since we are interested in the average daily price for product 42, a first attempt might be to roll up the result for the last two weeks using `avg`:
```
sales
: filter(eq("id", "42"))
: fold(avg)
```

At first sight, this seems fine, but we have made a subtle mistake: `fold(avg)` on a gauge metric will give us an average that is weighted by the sample count, so if we sold 100 items of product 42 on Monday, just one on Tuesday, and nothing on Wednesday, then the impact of the sales on Monday will be 100 times higher than that of Tuesday, and Wednesday has no impact at all. Data gaps like Wednesday should not influence the total average sales price, so we can keep the `null` values as-is, but using cardinality as weight clearly skews our average towards Monday's value.

What we really want is the average of the per-timeslot averages, excluding time slots with no data, so that every time slot with non-null data has the same weight. We do that by first applying the time aggregation `avg` to get per-timeslot averages, and then we average those into a single value with `fold(avg)`:
```
sales
: filter(eq("id", "42"))
: avg
: fold(avg)
```

Voilà.

Next, we need the average daily revenue for product 42 in the query timeframe. To get the total revenue for the product on each day, we use `:sum` and we average the per-timeslot values using `:fold(avg)`, but this time we do not want to ignore data gaps. Instead, we want to include days where no sale was reported as 0 in the average calculation. `:default(0)` will do just that and replace data gaps (`null`) with the specified value. Putting it all together, we get the average revenue per time slot for product 42 in the query timeframe with:
```
sales
: filter(eq("id", "42"))
: sum
: default(0)
: fold(avg)
```

## Scenario 14: All Service Methods of a Service

>**Task**
>We want to get information for our web service, but by default the data is reported on service method level.

Transformers allow us to shape a metric to our needs. Until now, we have done that by removing dimensions, or by removing result rows. Some transformers also add dimensions, and `:parents` is one of them.

Consider the following problem: The metric `builtin:service.keyRequest.errors.fourxx` is recorded per service method. We are interested in the service methods, but we want to filter the result payload by the ID of the service, namely `SERVICE-0123456789ABCDEF`. We cannot use a scope, since the primary entity is `SERVICE_METHOD` and not `SERVICE`. A `:filter` transformation would work, if the metric contained a secondary service dimension, which it does not. It can easily be added, though, by prepending the transformer `:parents`.

`:parents` is not only suitable for adding application entities. The general contract of `:parents` is that for each monitored entity dimension, a new dimension will be added before the existing one, if the entity is naturally embedded inside a larger entity of which there can only be one. Disks are a good example. A disk needs a host, otherwise monitoring is not possible. The following have similar disk-host-like relations that `:parents` is suitable for:

| Child Dimension Type | Child Synonyms | :parent Dimension Type | :parent Synonyms |
|---|---|---|---|
| `SERVICE_METHOD` | Key request | `SERVICE` | — |
| `APPLICATION_METHOD` | Key user action  | `APPLICATION` | — |
| `PROCESS_GROUP_INSTANCE` | Process Instance, Process, Instance | `HOST` | — |
| `DISK` | — | `HOST` | — |
| `SYNTHETIC_TEST_STEP` | — | `SYNTHETIC_TEST` | — |

We try accessing the descriptor for `builtin:service.keyRequest.errors.fourxx.rate:parents` and observe that we have gained a new dimension `dt.entity.service`. We know the ID of the service we are interested in and reference it via the relevant dimension in a `:filter` transformer and see that the result data meets our expectations:
```
GET {{base}}/metrics/query?metricSelector=builtin:service.keyRequest.errors.fourxx.rate:parents:filter(eq(dt.entity.service,SERVICE-0123456789ABCDEF))
Accept: text/csv

metricId,dt.entity.service,dt.entity.service_method,time,value
"builtin:service.keyRequest.errors.fourxx.rate:parents:filter(eq(dt.entity.service,SERVICE-0123456789ABCDEF))",SERVICE-0123456789ABCDEF,SERVICE_METHOD-0730DE996E8AA425,2019-04-08 00:00:00,0.0
"builtin:service.keyRequest.errors.fourxx.rate:parents:filter(eq(dt.entity.service,SERVICE-0123456789ABCDEF))",SERVICE-0123456789ABCDEF,SERVICE_METHOD-0730DE996E8AA425,2019-04-15 00:00:00,0.0
"builtin:service.keyRequest.errors.fourxx.rate:parents:filter(eq(dt.entity.service,SERVICE-0123456789ABCDEF))",SERVICE-0123456789ABCDEF,SERVICE_METHOD-13A5BE527CDA803D,2019-04-08 00:00:00,0.0
"builtin:service.keyRequest.errors.fourxx.rate:parents:filter(eq(dt.entity.service,SERVICE-0123456789ABCDEF))",SERVICE-0123456789ABCDEF,SERVICE_METHOD-13A5BE527CDA803D,2019-04-15 00:00:00,0.0
```
If we want to lose the service dimension again after filtering, we can use a `:splitBy(dt.entity.service_method)`. The order of transformations is again important. The filter cannot precede the `:parents`, since the dimension does not exist at that point.

## Scenario 15: Apdex for Users of iOS 6.x

>**Task**
>We want to filter a secondary dimension (Operating System) by name, rather than by ID.

Most metrics use entities in at least one dimension. The metric for Apdex split by operating system and version has two entity dimensions and one string dimension, namely the application (primary entity) being measured and the operating system (secondary entity) and version (string) for which the data is valid.

When we wish to only obtain data for a specific application, of which we know the name, we may use a scope expression with the `entity` predicate. We cannot use the same technique to instead filter operating systems by name, since scopes do not apply to secondary entities, but we may filter secondary entities by name using a transformer chain. For this, we use a combination of `:names` and `:filter`.

Accessing the descriptor of `builtin:apps.other.apdex.osAndVersion`, we find out the names of the individual dimensions. The dimension `dt.entity.os` contains unique IDs for operating systems, but we do not know what the formal ID of iOS is, we only know that its name is `"iOS"`. To `:filter` against the display name version of `dt.entity.os`, we first append the transformer `:names` to the metric key, giving us the new dimensions `dt.entity.os.name` and `dt.entity.device_application.name`. As a next step, we can filter out the applications with name iOS. We end up with the following transformer chain:
```
:names:filter(eq(dt.entity.os.name,"iOS"))
```
The result now contains Apdex metrics only for iOS users. To limit the results to a specific major version, we can use a prefix matcher and form a logical conjunction:
```
:names:filter(and(eq(dt.entity.os.name,iOS),prefix("App Version","6.")))
```
We have successfully matched against the names of secondary entities and against string dimensions, leaving us with iOS 6.x results:
```
metricId,dt.entity.device_application.name,dt.entity.device_application,dt.entity.os.name,dt.entity.os,App Version,time,value  
"builtin:apps.other.apdex.osAndVersion:names:filter(and(eq(dt.entity.os.name,iOS),prefix(App Version,6.)))",easyTravel Demo,MOBILE_APPLICATION-752C288D59734C79,iOS,OS-62028BEE737F03D4,6.8.7,1610993640000,0.87
...
```

## Scenario 16: Using Space and Time Aggregation with Disk Usages

>**Task**
>For a dashboard, we want a single number for the used disk capacity over all hosts.

`builtin:host.disk.used` captures used disk space and will give us the average per timeslot if no aggregation is specified. We can append `:max:splitBy():sum` to first extract the maximum for each time slot on every host and disk (`:max`, the time aggregation), then aggregate the maximum into a single data structure (`:splitBy()` removes all dimensions and merges all series), and extract the sum part from the merged data structure (`:sum`, the space aggregation). The result will be a sum of used bytes, considering the maximum for each time slot, over all hosts and all disks.

This common transformation pattern looks like a mistake at first, because the output of `:max` is a plain number, which can not be aggregated with `:sum` (only `:value` is supported for plain numbers, which is a no-op) and `:splitBy` as we used it until now does not change the data type being passed through it. In our use case, `:splitBy` _does_ change the output data type, in order for `:sum` to become a supported aggregation type. This feature is often referred to as _bucket inference_, because `:splitBy` and `merge` intelligently decide which data structure (bucket) will be used to collect the merged values, by looking to the right for the next aggregation being applied to the merged values, changing the output data type of the merging.

Conceptually, you can think of the next aggregation after a `:splitBy` to operate on a list of merged values, supporting any of min, max, avg, sum, median or percentile on that list. Depending on the space aggregation in use, the API will use a suitable data structure to model this conceptual list of merged values (typically a statistical summary or percentile estimator).

## Scenario 17: Maximum of Average CPU Usage Values Over Time

>**Task**
>For a chart, we want to draw a line that exactly intersects the peak of the graph.

When can apply what we learned above and query for a series of the average over time and simultaneously query for the maximum over time:
```
builtin:host.cpu.usage:avg  
builtin:host.cpu.usage:fold:max
```
The second line merges the statistical data over all time slots, and then extracts the maximum value from the statistical data. This works, but the folded value will be the actual maximum sample. If we draw the series and the maximum together into a chart, the folded value may exceed the highest average value, since each value in the chart is actually an aggregate of multiple samples (the average of samples in our case). What if we want to query for the maximum of average values in the chart, not the actual maximum sample?

For that use case, we want to build a list of averages rather than a list of original samples, and extract the maximum from these averages.

We can take advantage of the fact that `:splitBy` collects pre-aggregated input values (e.g. averages) into a list if the next aggregation after the merge requires it. If we pass all dimensions of the metric to `:splitBy,` no dimensions will be removed and hence no actual merging will happen. Instead we have a list with a single average for each time slot. Before the final aggregation, we need to insert `:fold` so that the lists are merged into one over time. From this merged list, we finally extract the maximum with `:max`. Taking all of this together we end up with this selector:
```
builtin:host.cpu.usage:avg:splitBy(dt.entity.host):fold:max
```
The result is exactly what we wanted: the maximum average values over time. We can chart the maximum and see that it will exactly touch the peak of the graph.

If you query this selector together with `builtin:host.cpu.usage:avg` you see that the single value is always exactly equal to the maximum entry of the corresponding series.

## Scenario 18: Filtering for Special Characters with Quoting

>**Task**
>We have a filter text field, but the resulting metric selector is invalid if we type in special characters.

Some characters have a special meaning in metric selectors: ( ) : , ~ "

Additionally, white space is used to tell where an identifier such as "dt.entity.host" ends. Replacing the periods (full stops) with spaces would result in three identifiers next to each other, rather than a single one that contains white space.

If white space or any of the characters mentioned above are to be used within a dimension name, a filter matcher reference, or otherwise in their "literal" sense, rather than as syntax, we need to escape or quote them. Knowing about proper escaping is especially important when we build our selectors in code that handles user input (e.g. when a user can provide a filter reference in a text field). In such scenarios, we want to prevent them from making the resulting selector syntactically invalid or, even worse, allow them to change its meaning and insert a malicious piece of code into our selector.

Say, our user legitimately wants to filter for a host with name `Host 14.A "Alice" ~80° (Europe, North Africa)`. This filter reference can not be inserted into the selector as it is, since it contains a period, double quotes, a tilde, brackets, spaces and a comma. In order not to understand these characters as syntax, we surround the string with double quotes and escape the contained double quotes with a tilde to indicate that the quoted part is not over yet, but that we have an instance of a literal quote:
```
"Host 14.A ~"Alice~" ~~80° (Europe, North Africa)"
```
Alternatively, we can rely entirely on escaping instead of quoting, but this gets messy real quick:
```
Host~ 14~.A~ "Alice"~ ~~80° ~(Europe~,~ North~ Africa~)
```
To filter for this name, we can use a combination of `:names` and `:filter` and use our quoted version for the filter matcher to create a valid selector that uses special characters:
```
builtin:host.disk.avail  
: names  
: filter(  
	eq(  
		dt.entity.host.name,  
		"Host 14.A ~"Alice~" ~~80° (Europe, North Africa)"   
	)  
 )
```

## Scenario 19: Two Metrics with Two Different Entity Selectors

>**Task**
>We want to query multiple metrics at once, and each metric should use a different entity selector.

There is only one `entitySelector` GET parameter, and an entity selector queries for exactly one entity type, but the metric selector can query more than one metric and those metrics could use different entity types.

How can we query the PGI-based metric `builtin:tech.generic.cpu.usage` together with `builtin:host.cpu.usage` with the hosts and process group instances both filtered using a tag "business-critical"?

This is easily possible by embedding entity selectors into filters using the `in` matcher. The right-hand side of `in` can be supplied with an `entitySelector` function that runs an entity query from within a metric selector. Since entity selectors use a lot of special characters, the argument of the `entitySelector` function should always be quoted:
```
builtin:tech.generic.cpu.usage
: filter(  
    in(
      dt.entity.process_group_instance,  
      entitySelector("type(PROCESS_GROUP_INSTANCE),tag(business-critical)") 
    )  
),

builtin:host.cpu.usage  
: filter(  
     in(  
       dt.entity.host,  
       entitySelector("type(HOST),tag(business-critical")  
     )  
)
```

## Scenario 20: Does our Service use Less Memory after the Update

>**Task**
>We want to see the CPU utilization graph of yesterday and the day before yesterday, displayed on top of each other in a chart, so that we can look out for differences.

A specific process group instance ran on a new version yesterday. We want to display a graph of yesterday's CPU usage and for comparison, we want the day before layered on top of yesterday. We get yesterday with `from=now/d-d&to=now/d`. This time window can then be moved per each queried metric by using the `timeshift` operator, which takes a time interval to move the data by, but keeping the original timestamps, so that it can be layered on top of the other graph. In our case, with the timeframe from before we need `timeshift(-1d)`:
```
builtin:tech.generic.cpu.usage,  
builtin:tech.generic.cpu.usage:timeshift(-1d),
```
The second time series is shifted one day into the past, showing data from the day before yesterday, but with the same timestamps as the first, un-shifted series. When charting these, they will be displayed on top of each other.

## Scenario 21: Last Stock Price Yesterday

>**Task**
>We want the last reported value just before midnight yesterday, but if the last time slot contains a gap in the data, we want to go back and instead see the last non-null data.

To get the latest non-null value, use the `:last` operator. E.g. when the timeframe is set to yesterday, but there might be holes in the data (maybe the stock exchange computers have a maintenance window) we use, e.g.:
```
stock_price:last
```
If there is at least one non-null data point, the result will use the latest value or otherwise be empty.

## Scenario 22: Response Time Categories
> **Task** Given a maximum acceptable response time of t = 1.5s in the 99th percentile, we want to
> classify response times of our services as "satisfactory" (&le; t), "tolerable" (&le; 4t)
> or "frustrating" (&gt; 4t). We want to see how the service count in each category changes
> over time.

First, we obtain a response time in the 99th percentile for each timeslot and every service,
and we scale from microseconds to full seconds:
```
builtin:service.response.time:percentile(99):toUnit(MicroSecond,Second)
```

Next up, we want to categorize each data point into one of the three categories. This is done
by splitting up each series into three new ones, and then assigning each data point to at
most one of the three new series, depending on their value. When a data point has been assigned
to one category, the same timeslot will be `null` for the other categories. Let's use the
`partition` operator to achieve just that:
```
: partition(
    apdexCategory,
    value("satisfactory", range(0, 1.5)),
    value("tolerable",    range(1.5, 6)),
    value("frustrating",  otherwise) 
  )
```

Now, the response time series for each series belongs to a new series with "dt.entity.service"
and "apdexCategory" as their dimensions. Now we want to merge all data with the same category. By specifying
`:count` after the merge operation, instead of the values, we query just the data point count that
made it into the merge of each timeslot:
```
: splitBy("apdexCategory")
: count
```

That's almost what we want, but if no data point was available for a timeslot of a
category, the value will be a data gap, which is represented with `null`. `0` would be more
correct for our use case, so let's replace nulls with zero:
```
: default(0)
```

Putting it all together we get:
```
builtin:service.response.time:percentile(99):toUnit(MicroSecond,Second)
: partition(
    apdexCategory,
    value("satisfactory", range(0, 1.5)),
    value("tolerable",    range(1.5, 6)),
    value("frustrating",  otherwise) 
  )
: splitBy("apdexCategory")
: count
: default(0)
```

With the tools from this scenario at our disposal we can:
* split up data points of series into categories,
* count merged data points,
* assign a default value for gaps in the data.

## Other Functionality Related to Metric Selectors

The parameters `from`, `to` and `resolution` are not part of the metric selector but apply to the whole query. Nonetheless, this section provides a high-level overview that will help you use them effectively.

### Choosing Resolution and Time Frame

`from` and `to` accept multiple date formats, including milliseconds since 1970 and human-readable dates in year-month-day order that may include time-of-day, as well as GMT offset. Additionally, a simple format for relative dates is accepted.

The recommended way to format an absolute date known in advance is to fully specify it. For instance, the time of Nepali New Year in 2019 is identified with `2019-04-14T00:00:00+05:45` in the local time zone. If the bounds are calculated from within a script or in code, it is recommended to use a millisecond timestamp instead, e.g. `1554798800839`. Note that regardless of the format of the requested time frame, datetimes in responses will always be in UTC.

Sometimes, especially when using the API interactively, it is desirable to use a time relative to the current instant in time when making the request. The API facilitates this by accepting the time anchor `now` with simple arithmetic on top. For instance, minutes (`m`), hours (`h`), weeks (`w`), months (`M`) or years (`y`) can be added or subtracted from `now` using `+` and `-` operators. Furthermore, we support an alignment operator `/` that zeroes parts of the date smaller than the specified unit. Some examples:

| Expression | Meaning |
|---|---|
| `now-1w` | One week before now, same time-of-day as now |
| `now/w` | The beginning of the current week (Monday, 00:00:00.00) |
| `now/w-d` | Also beginning of the week, depending on who you ask (Sunday, 00:00:00.00) |
| `now/M+5m` | Five minutes into the current month |

Resolution accepts identical units, e.g. `M` or `1M` signifies one month of time between data points. Instead of directly specifying the resolution, a unit-less quantity can be specified that identifies a number of data points that should be equally distributed in the desired query timeframe. The API will then choose the most coarse resolution available that will result in at least the desired amount of data points.

It is important to note that the resolution is intended as a hint to the server about a preferred count or resolution. When the wish for a resolution cannot be fulfilled exactly, e.g. when requesting eleven minutes between data points, the API will try to find the most satisfying available resolution. Further, the query timeframe may not be aligned with how data points are stored internally, causing the API to extend the timeframe outwards. For these reasons, the API sometimes returns more data points than requested.

### Entity Selector

Per default, metrics are requested for the universal scope, encompassing the complete Dynatrace environment that the authenticated user has access to. More often than not, only a subset of this data is required. A restricted query is facilitated by the specification of an entity selector expression, sometimes referred to as an entity scope.

To limit a query to a host-based metric to a single host with name `important.example.com`, we may use this scope as a separate query parameter:
```
entitySelector=type(HOST),entityName(important.example.com)
```
This parameter uses the same syntax as the `entitySelector` function within a `:filter`, but instead applies to all queried metrics, not just the one filter. The query parameter always applies to the first entity dimension, never to a secondary dimension, which is only possible with `:filter`.

If you are unsure which `type` to use, consider querying the metric selector of the metric in question and examining its `entityType` field. It holds all possible parameters for `type` that this metric will accept during query.

Dynatrace has a powerful tagging system. It can automatically apply tags to hosts, services, applications or other entities based on many data sources, such as AWS availability zones, CPU architecture, domain names, or similar characteristics. Assuming we want Linux hosts in Europe, and assuming we have configured the tags `Europe` and `Linux`, we may use this scope:
```
entitySelector=type(HOST),tag(Europe),tag(Linux)
```
You can see that compound scope expressions are built by AND-connecting predicate expressions with the comma character.

## Further Reading

**To learn more about entity selectors, see the [Official EntitySelector Documentation](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/entity-v2/entity-selector/).**
