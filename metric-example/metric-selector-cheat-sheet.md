# Metric Selector Cheat Sheet
This example-oriented document will teach you techniques with metric selectors that will enable you to implement advanced use cases quickly.

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
1. Get the dimension for which you want to count the distinct values using `splitBy(<dimension>)`
1. Extract a single value for each series and timeslot using `auto`
1. Merge all dimensions using `splitBy()`
1. call the `count` aggregation

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

## Calculating percentages 
The query 
```
builtin:service.response.time
    :avg
    :partition(latency,value(good,lt(10000)))
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
    