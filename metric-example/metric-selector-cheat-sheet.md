# Metric Selector Cheat Sheet
This example-oriented document will teach you techniques with metric selectors that will enable you to implement advanced use cases quickly.

## Add the pretty entity name to the result

If you query a metric, you'll get only the id of the entity dimensions in the result like `"HOST-0123456789ABCDEF"`. Using the [`names` transformation](https://www.dynatrace.com/support/help/shortlink/api-metrics-v2-selector#names), you can add the pretty name of the entity in your result:
```
builtin:host.cpu.user:names
```
The query result will then contain `dt.entity.host` and the `dt.entity.host.name` dimensions.

## Remove single values from the result
Let's say you want to keep only the timeslots with a value greater than zero. You can use the [`partition` transformation](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2/metric-selector#partition) for that:
```
my_metric
    :partition(
        "status",
            value("keep", gt(0))
    )
    :merge("status")
```
The partition operator discards all timeslots not matching its conditions. Afterward, we remove the dimension `status` added in the partitioning step using the [`merge` transformation](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2/metric-selector#merge).

## Filter series based on their time-aggregated value
Whereas you can use the `partition` transformation to filter single values, you can sift the whole series using the `series` condition of the `filter` transformation. For example, if you want to get only the series that were available over zero percent in the query timeframe, you can use the following query:
```
builtin:pgi.availability
    :filter(
        series(max,gt(0))
    )
```
To get more insights about the difference between the partition transformation and the series condition, see https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2/metric-selector#conditions.


## Filter dimension values
Consider you have the following values for the dimension `url` of your metric `web_requests`:
- app.dynatrace.co.jp
- app.dynatrace.com
- www.dynatrace.com 
- app.dynatrace.de

If you want to include only URLS starting with `app.` and filter out all URLs ending with `.co.jp`, you can use the following query:
```
web_requests
    :filter(
        and(
            prefix(url, "app."),
            not(
                suffix(url, ".co.jp")
            )
        )
    )
```
The `url` dimensions returned for this query are "app.dynatrace.com" and "app.dynatrace.de". To get all dimensions, you can leverage the `contains` condition:
```
web_requests
    :filter(
        contains(url, ".dynatrace.")
    )
```    

### Entity dimension name filtering

You can use the embedded [entity selector](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/entity-v2/entity-selector) to filter `dt.entity.*` dimensions. For example,
```
builtin:host.cpu.user
    :filter(
        in("dt.entity.host", 
            entitySelector("type(~"HOST~"),not(entityName.startsWith(~"dc1~"))")
        )
    )
```
returns only host entities with names that don't start with "dc1".

## Get the number of distinct dimension values
As no out-of-the-box metric gives you the number of hosts, you can use
```
builtin:host.cpu.user
    :splitBy("dt.entity.host")
    :auto
    :splitBy()
    :count
```
to figure out the number of hosts.
Similarly, you can get the number of distinct disks by the following query:
```
builtin:host.disk.avail
    :splitBy("dt.entity.disk")
    :auto
    :splitBy()
    :count
```

The approach is always:
1. Reduce the dimensions by `splitBy(<dimension>)`, so only the dimension for which you want to count the distinct values remains
1. Extract a single value for each series and timeslot using `auto`
1. Merge all dimensions using `splitBy()`
1. call the `count` aggregation

To get the total value of distinct values for the query timeframe, insert a `:fold` after the first step. For example:
```
builtin:host.cpu.user
    :splitBy("dt.entity.host")
    :fold
    :auto
    :splitBy()
    :count
```

## Calculating percentages 
The query 
```
builtin:service.response.time
    :avg
    :partition("latency",value("good",lt(10000)))
    :splitBy()
    :count
    :default(0) 
/
builtin:service.response.time
    :avg
    :splitBy()
    :count
* 100
```
returns the percentage of the series that had an average response time over 10,000 microseconds for a timeslot. This number is not equal to the percentage of requests with a response time of over 10k microseconds as the metric data is aggregated to 1-minute buckets. To get the exact percentage of requests running longer than 10k microseconds, you'd need to create a [Calculated service metric](https://www.dynatrace.com/support/help/platform-modules/applications-and-microservices/services/service-monitoring-settings/calculated-service-metric) that only captures requests matching this criterion and use it as the dividend in the metric expression.

## Enforce a default value
Consider you have the metric `number_errors` that is only incremented when an error occurs. To fill up the empty timeslots with zeros even if there were no booking in the whole query timeframe, use [`default(0,always)`](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2/metric-selector#default):
```
number_errors:
    :splitBy()
    :sum
    :default(0,always)
```

## Add the parent dimension to the result
For some entity dimensions like `PROCESS_GROUP_INSTANCE` and `SERVICE_METHOD`, you can enrich the result with the "parent" of these dimensions. For example, the metric `builtin:tech.generic.processCount` per default only provides the `dt.entity.process_group_instance` dimension. To get also the host dimension in the result, use the query:
```
builtin:tech.generic.processCount:parents
```
Moreover, you can combine the `names` and the `parents` transformations.
```
builtin:tech.generic.processCount:parents:names
```
will return both the `PROCESS_GROUP_INSTANCE` and `HOST` dimensions and the pretty names for both.

## Add further dimensions to the result
Besides enriching the metric dimensionality with the display name and the pre-configured parent of the entity dimensions, adding additional dimensions using the [`partition` transformation](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2/metric-selector#partition) is possible. For example:
```
builtin:service.response.time
    :avg
    :partition(
        "latency",
            value("slow", gt(10000)),
            value("good", otherwise)
    )
```
Adds the dimension "latency" to the series of the result. The dimension value depends on the response time. Data points greater than 10,000 microseconds are categorized as slow and the others as good.

### Map dimensions to another one
If you want to add a new dimension based on existing dimensions, you can also use the `partition` transformation. For example, consider a metric with the HTTP status code as its dimension, and you want to map all requests to "success" unless their status code begins with 4 or 5 (that is, they have 400 or 500 as their status code). 
You can achieve that by the following query:
```
http_request
    :partition("status",
        dimension("success", and(not(prefix("status_code", "4")), not(prefix("status_code", "5")))),
        otherwise("error"))
    :splitBy("status")
```

Using the metric selector query language, there is no further way to enrich the series dimensionality. You'd need to leverage the [DQL](https://www.dynatrace.com/support/help/platform/grail/dynatrace-query-language) for more advanced use cases.    
