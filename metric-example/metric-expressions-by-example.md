# Metric Expressions by Example
This is an example-oriented document that will teach you advanced 
techniques with metric selectors that will enable you to:
* convert °F to Kelvin,
* calculate an error rate metric from a service call count metric and an error count metric,
* show the available memory of the hosts that run the most memory-intensive process group instances.

## Prerequisites
This document assumes basic familiarity with metric selectors. If you don't yet feel comfortable with simple metric selectors, consider reading
through [Query by Example](query-by-example.md) first.

You can try the examples listed here through the Web UI via _Data Explorer_,
or you can send selectors to the `/v2/metrics/query` API for evaluation.

## Scenario 1: Convert Fahrenheit to Kelvin
> **Task** The LHCs magnets cables are kept in a superconducting state by ensuring that
> their temperature remains under 1.9K. In an effort to improve LHCs uptime,
> we recently installed temperature sensors that report directly to Dynatrace.
> Unfortunately, we bought the wrong model and all the measurements are in
> degrees Fahrenheit. How can we still check for magnets outside the nominal
> temperature range?

_Note: This scenario uses a notation for the series operator that is only available with Dynatrace versions 228 and later._

Let's convert to Kelvin first and then filter for magnets that are above the
nominal temperature range:
```
(
  (
    (temperature) + (459.67)
  )
  /
  (
    (5) / (9)
  )
)
: filter(
    series(max, gt(1.9))
  )
```

We can see that:
* `+`, `/` are arithmetic operators in infix notation, with `*` and `-` also available,
* operands of arithmetic are written in parentheses,
* `/` and `*` bind more closely than `-` and `+`, but just like in math, we can define a different order of operations by enclosing sub-expressions in parentheses,
* operators like `:filter` can be applied to a bracketed sub-expression with a calculation in it.

Keep in mind that many metric keys have dashes in them. Those dashes are interpreted literally (as part of the metric key)
and only become a calculation once the operands are enclosed in parentheses. For example, `request-duration` is a single
metric key, while `(request)-(duration)` subtracts `duration` from `request`.

## Scenario 2: Percentage of Client Errors
> **Task** We recently made a breaking change to our API and want to see which percentage
> of calls to the REST service trigger 4xx errors before and after the introduction of the
> breaking change.

`builtin:service.errors.fourxx.count` gives us just the amount of service calls with a 4xx exit
status, while `builtin:service.errors.total.count` additionally includes 5xx errors. If our
REST service has the entity ID `SERVICE-1234567890`, then we can get the percentage of errors
in the 4xx range with:
```
(
  (100)
  *
  (builtin:service.errors.fourxx.count)
  /
  (builtin:service.errors.total.count)
):filter(eq("dt.entity.service","SERVICE-1234567890"))
```

How does such a calculation with two separate metrics work? Dynatrace will first find all the series
with equal dimensions. For each match, we combine the associated data at the same time slot by applying
the numbers to the arithmetic operator in use. With the result, we assemble a new output series for each
match.

In the case of our example, we use this functionality to divide error counts that were measured in the
same time slot.

## Scenario 3: Revenue in Percent over the Query Timeframe
> **Task** Which percentage of our revenue was made in any given month of the last year?

We store revenue data in a metric called `revenue` that is split by a single dimension
`region`. Instead of revenue in absolute terms, we want to see for each timeslot what
percentage of the revenue over the whole query timeframe fall into that timeslot. In other
words, we want to divide by the combined revenue over the whole query timeframe and multiply
by 100.

For the multiplication by `100`, we can just use a numeric literal, but for the combined
revenue we would need a calculated value instead of a fixed one.

To achieve that with metric expressions, we need to reduce the revenue result to a
single value. This is done by first merging all dimensions into one using `splitBy()`,
yielding a single dimension-less series. Next, we want to apply `fold` to sum up all of
the individual data points of this one series, so that we end up with a single number
for the full revenue.

Putting it all together, we set our resolution to months, set `from` to `now-1y to now`
and finally our metric selector:
```
(100) * (revenue) / (revenue:splitBy():fold)
```

What would happen if we omitted the `fold`? In that case the percentage in any given timeslot
will be relative to the full revenue over all regions just in that timeslot, instead of
being relative to the revenue of the whole timeframe:
```
(100) * (revenue) / (revenue:splitBy())
```

If we omit the `splitBy()`, but keep the `fold`, then the percentages will
only apply to the current series and each series will sum up to 100 percent:
```
(100) * (revenue) / (revenue:fold)
```

In general, any dimension-less series result or dimension-less point result can be used in
the same way as a numeric literal. When doing arithmetic, think about which of your operands
should be series and which should be points (`:fold`). Also think about whether you want
to pair equal tuples for the calculation, or if you instead want all tuples of one side
to be paired with a single, empty tuple on the other side (`:splitBy()`). Each combination
has its own use cases.

## Scenario 4: Response Time Categories
> **Task** Given a maximum acceptable response time of t = 1.5s in the 99th percentile, we want to
> classify response times of our services as "satisfactory" (&le; t), "tolerable" (&le; 4t)
> or "frustrating" (&gt; 4t). We want to see how the service count in each category changes
> over time.

_Note: This scenario uses the partition operator, which is available in Dynatrace versions 227 and later._

First, we obtain a response time in the 99th percentile for each timeslot and every service,
and we scale from microseconds to full seconds:
```
(builtin:service.response.time:percentile(99)) / (1000) / (1000)
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
((builtin:service.response.time:percentile(99)) / (1000) / (1000))
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

## Scenario 5: Available Memory of Hosts with Top 10 PGIs
> **Task** We recently increased the maximum heap space for all our Java processes to achieve
> better utilization of available RAM. We want to verify that there's enough free memory on the hosts where
> the Top 10 most memory consuming processes run.

Sometimes we want to use one metric for topping and another metric for the actual data.
`:sort` has no built-in functionality to sort by the values of a metric other than the one
being sorted, but that is not going to stop us because we have metric expressions at our disposal.

We want to get the top PGIs of `builtin:tech.generic.mem.usage`, transform the dimensions from
PGIs to only hosts, then replace the values for the top hosts with data from
`builtin:tech.generic.mem.usage`.

We start with the top hosts part: Get PGI memory usage with `builtin:tech.generic.mem.usage`
and reduce to the Top 10 by appending `:sort(value(max,descending)):limit(10)`. To view data
on host level instead of PGI we add host dimensions with `:parents` and then group by them with
`splitBy("dt.entity.host")`, which also removes the PGIs from the dimension tuples.

Now we have host-based dimension tuples for the top PGIs and want to fill in the values of
another metric `builtin:host.mem.avail.bytes`. A general pattern to apply topping with `metricA`
but show the values from `metricB` for the topped dimensions is:
```
(<metricA>:sort(...):limit(...))*(0)+(<metricB>)
```

Let's put it all together:
```
(
  builtin:tech.generic.mem.usage
  : sort(value(max,descending))
  : limit(10)
  : parents
  : splitBy("dt.entity.host")
)
*
(0)
+
(builtin:host.mem.avail.bytes)
```

It worked, we successfully used the PGIs from `builtin:tech.generic.mem.usage` for sorting,
but the associated hosts and values from `builtin:host.mem.avail.bytes`!

What would have happened if we forgot `:parents:splitBy("dt.entity.host")`, though? Then we
would have attempted to add PGI data together with Host data, giving us an empty response
with a warning like the following:
```
"Metric expression contains non-matching dimension-keys. Please consider applying `:splitBy()` to all involved operands."
```

If you encounter such a warning, check the `dimensionDefinitions` of the operands on the schema
endpoint, and consider adding `splitBy` as needed.

## Further Reading
Please refer to the documentation on metric expressions on [dyntrace.com](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2/metric-expressions/)
for additional technical details such as:
* precedence of operators,
* semantics for combinations of point/series results and literals,
* null handling,
* time alignment,
* many others.
