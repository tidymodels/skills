# Groupwise Metrics

Groupwise metrics quantify the disparity in metric values across groups. They are especially useful for fairness analysis but can be applied to any situation where you want to measure how much a metric varies across subgroups.

> **Note for Source Development:** If you're contributing directly to the yardstick package, see internal groupwise infrastructure. See the [Source Development Guide](source-guide.md) for details.

## Overview

**Use when:**

- You want to measure disparity in performance across groups (e.g., demographic groups)

- You need fairness metrics for ML models

- You want to quantify how much a metric differs between subsets of your data

**Key characteristics:**

- Built on top of existing yardstick metrics

- Automatically groups by a specified column

- Aggregates group-specific metrics into a single disparity measure

- Returns zero when metric is equal across all groups

**Examples:** Demographic parity, equal opportunity, accuracy difference

**Implementation:**

- Groupwise constructor: `R/groupwise.R` (implements `new_groupwise_metric()`)

- Built-in groupwise metrics: `R/groupwise-accuracy_diff.R`, `R/groupwise-accuracy_ratio.R`

- Aggregation functions: Range, difference, ratio calculations

**Common patterns:**

- Fairness metrics: Measure performance disparities across demographic groups

- Batch effects: Quantify variation across experimental batches

- Temporal stability: Track metric consistency over time periods

**Test patterns:**

- Groupwise creation: `tests/testthat/test-groupwise.R`

- Aggregation tests: Validates difference, ratio, range calculations

- Integration tests: Tests with grouped data and resampling

## Important Distinction: Group-Aware vs Groupwise

### All Metrics Are Group-Aware

**Every yardstick metric** respects `dplyr::group_by()`. When you pass grouped data to a metric, it computes the metric for each group separately.

```r
# Group-aware behavior (built into all metrics)
hpc_cv |>
  group_by(Resample) |>
  accuracy(obs, pred)

# Returns one row per Resample
# .metric .estimator .estimate Resample
# accuracy multiclass 0.709    Fold01
# accuracy multiclass 0.713    Fold02
# ...
```

### Groupwise Metrics Are Different

**Groupwise metrics** add an extra layer: they temporarily group by a specified column, compute metrics for those groups, then aggregate the results.

```r
# Groupwise metric
accuracy_diff_by_batch <- accuracy_diff(batch)

hpc_cv |>
  accuracy_diff_by_batch(obs, pred)

# 1. Groups by 'batch' internally
# 2. Computes accuracy for each batch
# 3. Aggregates (e.g., takes difference)
# 4. Returns single disparity measure
```

## Creating Groupwise Metrics

Use `new_groupwise_metric()` to create a groupwise metric:

```r
new_groupwise_metric(
  fn = metric_function,        # Existing yardstick metric
  name = "metric_name",         # Name for your new metric
  aggregate = aggregation_fn,   # How to combine group results
  direction = "minimize"        # Optimization direction
)
```

### Two-Step Process

Groupwise metrics are **function factories** that return function factories:

```r
# Step 1: Create the metric factory
accuracy_diff <- new_groupwise_metric(
  fn = accuracy,
  name = "accuracy_diff",
  aggregate = function(x) {
    diff(range(x$.estimate))
  }
)

# Step 2: Specify the grouping variable
accuracy_diff_by_batch <- accuracy_diff(batch)

# Step 3: Use like any other metric
accuracy_diff_by_batch(data, truth, estimate)
```

## Complete Example: Accuracy Difference

Measure the difference in accuracy between two batches:

```r
library(yardstick)
library(dplyr)

# Create sample data with batch column
set.seed(1)
hpc <- hpc_cv |>
  mutate(batch = sample(c("a", "b"), nrow(hpc_cv), replace = TRUE)) |>
  select(obs, pred, batch, Resample)

# Step 1: Create groupwise metric factory
accuracy_diff <- new_groupwise_metric(
  fn = accuracy,
  name = "accuracy_diff",
  aggregate = function(acc_by_group) {
    # Take difference between max and min
    diff(range(acc_by_group$.estimate))
  },
  direction = "minimize"  # Zero difference is ideal
)

# Step 2: Specify grouping variable
accuracy_diff_by_batch <- accuracy_diff(batch)

# Step 3: Use the metric
hpc |>
  filter(Resample == "Fold01") |>
  accuracy_diff_by_batch(obs, pred)

# Output:
# .metric        .by   .estimator .estimate
# accuracy_diff  batch multiclass 0.123
```

## Aggregation Functions

The `aggregate` function determines how to combine metric values across groups into a single disparity measure.

### Common Aggregation Patterns

**1. Difference of range (max - min):**
```r
diff_range <- function(x) {
  diff(range(x$.estimate))
}

# Used by demographic_parity(), equal_opportunity(), equalized_odds()
```

**2. Ratio of range:**
```r
ratio_range <- function(x) {
  range_vals <- range(x$.estimate)
  range_vals[1] / range_vals[2]
}
```

**3. Standard deviation:**
```r
sd_metric <- function(x) {
  sd(x$.estimate)
}
```

**4. Max absolute difference from overall mean:**
```r
max_abs_diff <- function(x) {
  overall_mean <- mean(x$.estimate)
  max(abs(x$.estimate - overall_mean))
}
```

**5. Custom comparison:**
```r
# Compare first group to others
first_vs_rest <- function(x) {
  abs(x$.estimate[1] - mean(x$.estimate[-1]))
}
```

### Aggregation Function Requirements

The `aggregate` function must:

- Accept metric results as first argument (tibble with `.estimate` column)

- Return a **single numeric value**

- Handle variable number of groups gracefully

```r
# Good: Returns single numeric
function(x) diff(range(x$.estimate))

# Bad: Returns vector
function(x) x$.estimate - mean(x$.estimate)

# Bad: Returns non-numeric
function(x) x
```

## Using Groupwise Metrics

### Standalone Use

```r
accuracy_diff_by_batch(data, obs, pred)
```

### In Metric Sets

```r
my_metrics <- metric_set(
  accuracy,                    # Regular metric
  accuracy_diff_by_batch       # Groupwise metric
)

my_metrics(data, truth = obs, estimate = pred)
```

### With Existing Groups

Groupwise metrics are group-aware. When data has existing groups, results are computed per group:

```r
# Compute accuracy difference by batch within each resample
hpc |>
  group_by(Resample) |>
  accuracy_diff_by_batch(obs, pred)

# Returns one row per Resample
# .metric        .by   .estimator .estimate Resample
# accuracy_diff  batch multiclass 0.089     Fold01
# accuracy_diff  batch multiclass 0.112     Fold02
# ...
```

### Cannot Group By Same Variable

You cannot group data by the same variable that the groupwise metric uses internally:

```r
# ERROR: batch is used both ways
hpc |>
  group_by(batch) |>
  accuracy_diff_by_batch(obs, pred)

# Error: Metric is internally grouped by 'batch';
#        grouping data by 'batch' is not well-defined
```

## Built-in Fairness Metrics

Yardstick includes several fairness metrics built with `new_groupwise_metric()`:

### demographic_parity()

Measures disparity in detection prevalence (predicted positive rate) across groups.

```r
dem_parity <- demographic_parity(group_column)
dem_parity(data, truth, estimate)

# Zero means equal predicted positive rates across groups
```

### equal_opportunity()

Measures disparity in recall (true positive rate) across groups.

```r
eq_opp <- equal_opportunity(group_column)
eq_opp(data, truth, estimate)

# Zero means equal recall across groups
```

### equalized_odds()

Measures disparity in both sensitivity and specificity across groups.

```r
eq_odds <- equalized_odds(group_column)
eq_odds(data, truth, estimate)

# Zero means equal TPR and FPR across groups
```

## Advanced Examples

### Multiple Aggregation Strategies

```r
# Maximum disparity
accuracy_max_diff <- new_groupwise_metric(
  fn = accuracy,
  name = "accuracy_max_diff",
  aggregate = function(x) diff(range(x$.estimate))
)

# Average absolute deviation
accuracy_avg_dev <- new_groupwise_metric(
  fn = accuracy,
  name = "accuracy_avg_dev",
  aggregate = function(x) {
    mean(abs(x$.estimate - mean(x$.estimate)))
  }
)

# Coefficient of variation
accuracy_cv <- new_groupwise_metric(
  fn = accuracy,
  name = "accuracy_cv",
  aggregate = function(x) {
    sd(x$.estimate) / mean(x$.estimate)
  }
)
```

### Using Metric Sets with Groupwise

```r
# Create groupwise version
precision_diff <- new_groupwise_metric(
  fn = precision,
  name = "precision_diff",
  aggregate = function(x) diff(range(x$.estimate))
)

# Use in metric set with base metric
my_metrics <- metric_set(
  accuracy,
  precision,
  accuracy_diff(batch),
  precision_diff(batch)
)

my_metrics(data, truth = obs, estimate = pred)
```

### Custom Metric in Groupwise

```r
# Create custom metric first
my_custom_metric <- function(data, truth, estimate, ...) {
  # ... implementation
}

my_custom_metric <- new_class_metric(
  my_custom_metric,
  direction = "maximize"
)

# Then create groupwise version
my_custom_diff <- new_groupwise_metric(
  fn = my_custom_metric,
  name = "my_custom_diff",
  aggregate = function(x) diff(range(x$.estimate))
)

my_custom_diff_by_group <- my_custom_diff(group_var)
```

## Testing Groupwise Metrics

```r
# tests/testthat/test-my-groupwise-metric.R

test_that("groupwise metric works correctly", {
  # Create test data with groups
  df <- data.frame(
    truth = factor(c("A", "B", "A", "B", "A", "B")),
    estimate = factor(c("A", "B", "A", "A", "B", "B")),
    group = c("g1", "g1", "g1", "g2", "g2", "g2")
  )

  # Create groupwise metric
  acc_diff <- new_groupwise_metric(
    fn = accuracy,
    name = "acc_diff",
    aggregate = function(x) diff(range(x$.estimate))
  )

  acc_diff_by_group <- acc_diff(group)

  result <- acc_diff_by_group(df, truth, estimate)

  expect_equal(result$.metric, "acc_diff")
  expect_equal(result$.by, "group")
  expect_true(is.numeric(result$.estimate))
  expect_true(result$.estimate >= 0)
})

test_that("groupwise metric returns zero for equal groups", {
  # Create data where both groups have same accuracy
  df <- data.frame(
    truth = factor(rep(c("A", "B"), 4)),
    estimate = factor(rep(c("A", "B"), 4)),
    group = rep(c("g1", "g2"), each = 4)
  )

  acc_diff <- new_groupwise_metric(
    fn = accuracy,
    name = "acc_diff",
    aggregate = function(x) diff(range(x$.estimate))
  )

  acc_diff_by_group <- acc_diff(group)
  result <- acc_diff_by_group(df, truth, estimate)

  expect_equal(result$.estimate, 0)
})

test_that("groupwise metric errors on duplicate grouping", {
  df <- data.frame(
    truth = factor(c("A", "B")),
    estimate = factor(c("A", "B")),
    group = c("g1", "g2")
  )

  acc_diff_by_group <- new_groupwise_metric(
    fn = accuracy,
    name = "acc_diff",
    aggregate = function(x) diff(range(x$.estimate))
  )(group)

  # Cannot group by same variable
  expect_error(
    df |> group_by(group) |> acc_diff_by_group(truth, estimate),
    "internally grouped"
  )
})

test_that("groupwise metric works with existing groups", {
  df <- data.frame(
    truth = factor(rep(c("A", "B"), 8)),
    estimate = factor(rep(c("A", "B"), 8)),
    group = rep(c("g1", "g2"), 8),
    fold = rep(c("f1", "f2"), each = 8)
  )

  acc_diff_by_group <- new_groupwise_metric(
    fn = accuracy,
    name = "acc_diff",
    aggregate = function(x) diff(range(x$.estimate))
  )(group)

  result <- df |>
    group_by(fold) |>
    acc_diff_by_group(truth, estimate)

  # One row per fold
  expect_equal(nrow(result), 2)
  expect_true(all(c("f1", "f2") %in% result$fold))
})
```

## Best Practices

1. **Choose meaningful aggregation**: The aggregation function should reflect your fairness/disparity goals
2. **Use descriptive names**: Make it clear what disparity is being measured
3. **Set appropriate direction**: Usually "minimize" for fairness metrics (zero = fair)
4. **Document interpretation**: Explain what the value means (e.g., "difference in accuracy between groups")
5. **Validate group sizes**: Ensure adequate sample sizes in each group
6. **Consider multiple metrics**: Look at disparity across several metrics, not just one
7. **Test with equal groups**: Verify metric returns zero when groups are identical

## Common Use Cases

### Fairness Analysis

- Demographic parity across protected attributes

- Equal opportunity across sensitive features

- Equalized odds for fair classification

### Model Monitoring

- Performance drift across customer segments

- Accuracy consistency across geographic regions

- Reliability across product categories

### A/B Testing

- Outcome differences between treatment groups

- Consistency of effects across subpopulations

- Heterogeneous treatment effects

### Quality Control

- Performance variation across manufacturing batches

- Consistency across different operators

- Stability over time periods

## Limitations and Considerations

1. **Group size matters**: Small groups lead to unstable estimates
2. **Multiple groups**: Some aggregations work better with 2 groups than many
3. **Statistical significance**: Groupwise metrics don't include confidence intervals
4. **Intersectionality**: Single groupwise metric doesn't capture interactions between groups
5. **Context dependent**: What counts as "fair" depends on your application

## See Also

- [Metric System](metric-system.md) - Understanding basic metric architecture

- [Class Metrics](class-metrics.md) - Base metrics for classification

- [Combining Metrics](metric-set.md) - Using metric_set() with groupwise metrics

- `vignette("grouping", "yardstick")` - Detailed vignette on grouping behavior
