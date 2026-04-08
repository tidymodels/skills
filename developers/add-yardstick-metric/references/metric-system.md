# Understanding the Yardstick Metric System

Before creating metrics, understanding how yardstick's metric system works helps
you build metrics that integrate properly with the ecosystem.

> **Note for Source Development:** If you're contributing directly to the
> yardstick package, you can use internal helper functions like
> `yardstick_mean()`, `finalize_estimator_internal()`, and validation helpers.
> See the [Source Development Guide](source-guide.md) for details.

## Overview

The yardstick metric system provides a consistent interface for creating,
composing, and evaluating performance metrics across different prediction types.

**Core system implementations:**

- Metric constructors: `R/metric.R` (defines `new_numeric_metric()`,
  `new_class_metric()`, `new_prob_metric()`, etc.)

- Metric composition: `R/metric_set.R` (implements `metric_set()` for combining
  metrics)

- Estimator finalization: `R/finalize_estimator.R` (determines
  binary/macro/micro/etc.)

- Data frame methods: `R/num_metric.R`, `R/class_metric.R`, `R/prob_metric.R`
  (metric summarizers)

**Integration patterns:**

- Metric sets: `R/metric_set.R` (combines multiple metrics)

- Direction attributes: Used by tune package for optimization

- Range attributes: Used for validation and visualization

**Test patterns:**

- Constructor tests: `tests/testthat/test-metric.R`

- Metric set tests: `tests/testthat/test-metric_set.R`

- Estimator tests: `tests/testthat/test-finalize_estimator.R`

## What `new_*_metric()` does

When you wrap your metric function with `new_numeric_metric()`,
`new_class_metric()`, or `new_prob_metric()`, it:

1. **Sets attributes** that describe your metric:

   - `direction`: "minimize", "maximize", or "zero" (what's optimal?)

   - `range`: `c(min, max)` (possible values the metric can take)

2. **Creates a class hierarchy**:
   ```r
   # Example for accuracy
   class(accuracy)
   # [1] "accuracy" "class_metric" "metric" "function"
   ```

3. **Enables ecosystem integration**:

   - `metric_set()` knows how to combine your metric with others

   - The metric can be identified and validated

   - Automatic method dispatch works correctly

## Why this matters

### For `metric_set()` composition

```r
metrics <- metric_set(accuracy, precision, recall)
```

The metric class hierarchy allows `metric_set()` to:

- Verify all metrics are compatible

- Group results by `.estimator` appropriately

- Apply metrics to data correctly

### For direction and range

```r
# These attributes help users understand the metric
attr(accuracy, "direction")  # "maximize"
attr(accuracy, "range")       # c(0, 1)
```

Tools can use this to:

- Know if higher is better or worse

- Validate metric values are in expected range

- Create appropriate visualizations

## The `.estimator` column

Every metric returns a tibble with a `.estimator` column:

### For numeric metrics

```r
# Always "standard"
mae(df, truth, estimate)
# .metric .estimator .estimate
# mae     standard   0.5
```

### For class metrics

```r
# Depends on number of classes
accuracy(df_binary, truth, estimate)
# .metric  .estimator .estimate
# accuracy binary     0.75

accuracy(df_multiclass, truth, estimate)
# .metric  .estimator .estimate
# accuracy multiclass 0.68
```

### The estimator value comes from `finalize_estimator()`

- Binary classification → "binary"

- Multiclass with 3+ levels → "macro", "micro", or "macro_weighted"

- Numeric/regression → "standard"

### Why it matters

When you use `metric_set()`, results are grouped by `.estimator`:

```r
metrics <- metric_set(accuracy, precision, recall)
metrics(df, truth, estimate)
# All three metrics share the same .estimator value
```

## Class naming conventions

Your metric's primary class should match the function name:

```r
mse <- new_numeric_metric(mse, direction = "minimize", range = c(0, Inf))
class(mse)
# [1] "mse" "numeric_metric" "metric" "function"
```

This enables S3 dispatch for methods like `autoplot.mse()`.

## Design Considerations

Before implementing a new metric, consider whether you actually need to create
one.

### When to create a new metric

**Create a new metric when:**

- It measures a genuinely different aspect of model performance

- It's commonly used in your domain and not available in yardstick

- It has a well-defined formula or calculation method

- You'll use it repeatedly across multiple projects

**Don't create a new metric if:**

- It's just a transformation of an existing metric (use `metric_tweak()`
  instead)

- It can be composed from existing metrics

- It's a one-off calculation for a specific analysis

- It's too domain-specific for general use

### Using `metric_tweak()` for variations

For simple variations of existing metrics, use `metric_tweak()`:

```r
# Create a variant of F-measure with beta = 2
f2_meas <- metric_tweak("f2_meas", f_meas, beta = 2)

# Use it like any other metric
f2_meas(df, truth, estimate)
metric_set(accuracy, f2_meas)
```

This is much simpler than creating a full new metric.

### Naming conventions

**Follow yardstick patterns:**

- Use lowercase with underscores: `mean_squared_error` → `mse`

- Avoid camelCase or PascalCase

- Be consistent with existing naming

**Abbreviations vs full names:**

- Well-known abbreviations: `rmse`, `mae`, `auc` (widely recognized)

- Full names for clarity: `accuracy`, `precision`, `recall` (already short)

- When in doubt, use the full name

**Avoid conflicts:**

```r
# Bad: too generic
error()  # Conflicts with base::error
metric()  # Too vague

# Good: specific and descriptive
prediction_error()
classification_metric()
```

**Examples of good names:**

- `miss_rate` (clear, descriptive)

- `huber_loss` (named after the technique)

- `roc_auc` (standard abbreviation)

### Parameter design

**What should be arguments:**

```r
# Hyperparameters that affect calculation
huber_loss(data, truth, estimate, delta = 1.0)

# Configuration that changes behavior
f_meas(data, truth, estimate, beta = 1)

# Thresholds or cutoffs
classification_cost(data, truth, estimate, costs = c(1, 2))
```

**What should NOT be arguments:**

- Constants that are part of the metric definition

- Values that would break the metric's meaning

- Options that should be separate metrics

**Keep parameters minimal:**

```r
# Good: focused parameters
mse(data, truth, estimate, na_rm = TRUE, case_weights = NULL)

# Bad: too many options
mse(data, truth, estimate, na_rm = TRUE, case_weights = NULL,
    sqrt = FALSE, relative = FALSE, log_scale = FALSE)
# These should be separate metrics: rmse(), relative_mse(), log_mse()
```

Users can always wrap your metric if they need variations:

```r
my_custom_mse <- function(data, truth, estimate) {
  result <- mse(data, truth, estimate)
  result$.estimate <- sqrt(result$.estimate)
  result
}
```

### Single responsibility principle

**Each metric should do one thing well:**

```r
# Good: accuracy measures one thing
accuracy(data, truth, estimate)

# Bad: don't combine multiple metrics
accuracy_and_precision()  # Should be two separate metrics
combined_scores()         # Use metric_set() instead
```

**Compose with `metric_set()` instead:**

```r
# Let users compose metrics
metrics <- metric_set(accuracy, precision, recall, f_meas)
metrics(data, truth, estimate)
```

### Scope and reusability

**Design for general use:**

- Avoid hard-coded domain-specific values

- Make assumptions explicit in documentation

- Allow customization through parameters when appropriate

**Example:**

```r
# Bad: too specific
credit_risk_score(data, truth, estimate)  # Hard-codes credit risk logic

# Good: general with parameters
classification_cost(data, truth, estimate, costs = c(fp = 2, fn = 5))
# Users can set costs for their domain
```

## Exported vs Internal Functions

Many yardstick helper functions are INTERNAL and not exported. Using them will
cause runtime errors.

### ❌ Don't Use (Internal/Not Exported)

- `yardstick_mean()` - NOT EXPORTED

- `get_weights()` - NOT EXPORTED

- `metric_range()` - NOT EXPORTED

- `metric_optimal()` - NOT EXPORTED

- `metric_direction()` - NOT EXPORTED

- `data_altman()` - NOT EXPORTED (test helper)

- `data_three_class()` - NOT EXPORTED (test helper)

### ✅ Use Instead

**For weighted calculations:**

```r
# Instead of yardstick_mean(), use base R weighted.mean()
if (is.null(case_weights)) {
  mean(values)
} else {
  # Handle hardhat weights (convert to numeric)
  wts <- if (inherits(case_weights, "hardhat_importance_weights") ||
             inherits(case_weights, "hardhat_frequency_weights")) {
    as.double(case_weights)
  } else {
    case_weights
  }
  weighted.mean(values, w = wts)
}
```

### EXPORTED yardstick functions you CAN safely use

- `check_numeric_metric()` ✓

- `check_class_metric()` ✓

- `check_prob_metric()` ✓

- `yardstick_remove_missing()` ✓

- `yardstick_any_missing()` ✓

- `yardstick_table()` ✓

- `finalize_estimator()` ✓

- `validate_estimator()` ✓

- `abort_if_class_pred()` ✓

- `as_factor_from_class_pred()` ✓

- `numeric_metric_summarizer()` ✓

- `class_metric_summarizer()` ✓

- `prob_metric_summarizer()` ✓

- `new_numeric_metric()` ✓

- `new_class_metric()` ✓

- `new_prob_metric()` ✓

## Next Steps

- Create numeric metrics: [numeric-metrics.md](numeric-metrics.md)

- Create class metrics: [class-metrics.md](class-metrics.md)

- Create probability metrics: [probability-metrics.md](probability-metrics.md)

- Understand confusion matrices: [confusion-matrix.md](confusion-matrix.md)
