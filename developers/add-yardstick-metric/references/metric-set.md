# Combining Metrics with metric_set()

`metric_set()` allows you to combine multiple yardstick metrics into a single function that calculates all of them at once. This is more efficient than calling metrics individually and integrates seamlessly with tidymodels workflows.

> **Note for Source Development:** If you're contributing directly to the yardstick package, see how `metric_set()` validates and combines metrics internally. See the [Source Development Guide](source-guide.md) for details.

## Overview

**Use when:**
- You want to calculate multiple metrics on the same data
- You're using tidymodels workflows (tune, recipes, workflows)
- You want to avoid repeating metric calculations
- You need consistent metric evaluation across resamples

**Key benefits:**
- **Efficiency**: Shared calculations performed once (e.g., confusion matrix)
- **Convenience**: One function call instead of many
- **Integration**: Works with tune package for model tuning
- **Consistency**: All metrics use same data preprocessing

**Implementation:**
- Metric set creation: `R/metric_set.R` (implements `metric_set()` and validation)
- Compatibility checking: Validates metric types can be combined
- Function generation: Creates composite function that calls each metric

**Usage in tidymodels:**
- Tune integration: Used by `tune_grid()`, `tune_bayes()` for model evaluation
- Resampling: Applied consistently across all resamples
- Workflow integration: Works with `fit_resamples()`, `last_fit()`

**Test patterns:**
- Metric set creation: `tests/testthat/test-metric_set.R`
- Compatibility validation: Tests for valid/invalid metric combinations
- Integration tests: Tests with tune and workflows packages

## Basic Usage

```r
library(yardstick)

# Create a metric set
my_metrics <- metric_set(rmse, rsq, mae)

# Use it like any other metric function
my_metrics(data, truth = actual, estimate = predicted)

# Returns tibble with all metrics:
# .metric .estimator .estimate
# rmse    standard   0.123
# rsq     standard   0.891
# mae     standard   0.098
```

## Compatibility Rules

Metrics in a set must be compatible. You can mix:

### ✓ Valid Combinations

**1. All numeric metrics:**
```r
numeric_metrics <- metric_set(rmse, mae, rsq, huber_loss)
```

**2. Mix of class and class probability metrics:**
```r
class_metrics <- metric_set(accuracy, precision, recall, roc_auc, pr_auc)
```

**3. Mix of survival metrics (any combination):**
```r
surv_metrics <- metric_set(
  concordance_survival,       # Static
  brier_survival,             # Dynamic
  brier_survival_integrated   # Integrated
)
```

### ✗ Invalid Combinations

**Cannot mix metric types:**
```r
# ERROR: Cannot mix numeric and classification
metric_set(rmse, accuracy)

# ERROR: Cannot mix classification and survival
metric_set(accuracy, concordance_survival)
```

## Function Signatures by Type

The returned function has different arguments depending on metric types:

### Numeric Metrics

```r
regression_metrics <- metric_set(rmse, mae, rsq)

# Signature:
regression_metrics(
  data,
  truth,
  estimate,
  na_rm = TRUE,
  case_weights = NULL,
  ...
)

# Usage:
regression_metrics(test_data, truth = y, estimate = y_pred)
```

### Class/Probability Metrics

```r
class_metrics <- metric_set(accuracy, roc_auc, pr_auc)

# Signature:
class_metrics(
  data,
  truth,
  ...,              # For probability columns
  estimate,         # Must be named!
  estimator = NULL,
  na_rm = TRUE,
  event_level = yardstick_event_level(),
  case_weights = NULL
)

# Usage - note estimate is named:
class_metrics(
  test_data,
  truth = obs,
  VF:L,               # Probability columns
  estimate = pred     # Named argument!
)
```

### Survival Metrics

```r
surv_metrics <- metric_set(concordance_survival, brier_survival)

# Signature:
surv_metrics(
  data,
  truth,
  ...,              # For survival predictions
  estimate,         # Named for time predictions
  na_rm = TRUE,
  case_weights = NULL
)
```

## Important: Named `estimate` Argument

⚠️ **For class/probability and survival metric sets, you MUST name the `estimate` argument.**

```r
class_metrics <- metric_set(accuracy, roc_auc)

# ✓ Correct
class_metrics(data, truth = obs, estimate = pred)

# ✗ Wrong - estimate captured by ...
class_metrics(data, truth = obs, pred)
# Error: Can't find estimate column
```

**Why?** The `estimate` argument comes after `...` in the signature, so unnamed arguments get captured by `...`.

## Working with Groups

Metric sets respect `dplyr::group_by()`:

```r
metrics <- metric_set(accuracy, kap, roc_auc)

# Compute metrics for each resample
hpc_cv |>
  group_by(Resample) |>
  metrics(truth = obs, VF:L, estimate = pred)

# Returns one row per metric per group:
# .metric  .estimator .estimate Resample
# accuracy multiclass 0.709     Fold01
# kap      multiclass 0.583     Fold01
# roc_auc  hand_till  0.901     Fold01
# accuracy multiclass 0.713     Fold02
# ...
```

## Using metric_tweak() with metric_set()

Use `metric_tweak()` to set custom defaults for metrics before adding them to a set:

```r
# Create tweaked version with custom parameter
f2_meas <- metric_tweak("f2_meas", f_meas, beta = 2)
mase12 <- metric_tweak("mase12", mase, m = 12)

# Add to metric set
my_metrics <- metric_set(
  precision,
  recall,
  f_meas,    # Default beta = 1
  f2_meas    # Custom beta = 2
)

my_metrics(data, truth = obs, estimate = pred)

# Both f_meas and f2_meas calculated with different beta values
```

**Why this matters:** Once metrics are in a set, you can't change their parameters. Tweak them first.

## Complete Examples

### Regression Workflow

```r
library(yardstick)
library(dplyr)

# Define metric set
regression_metrics <- metric_set(
  rmse,
  mae,
  rsq,
  huber_loss
)

# Use on test data
results <- regression_metrics(
  solubility_test,
  truth = solubility,
  estimate = prediction
)

results
# .metric     .estimator .estimate
# rmse        standard   0.789
# mae         standard   0.582
# rsq         standard   0.892
# huber_loss  standard   0.341
```

### Classification with Probabilities

```r
# Mix class and probability metrics
class_metrics <- metric_set(
  accuracy,
  precision,
  recall,
  f_meas,
  roc_auc,
  pr_auc
)

# Use with class probabilities
results <- class_metrics(
  two_class_example,
  truth = truth,
  Class1,           # Probability column
  estimate = predicted
)

results
# .metric   .estimator .estimate
# accuracy  binary     0.838
# precision binary     0.819
# recall    binary     0.875
# f_meas    binary     0.846
# roc_auc   binary     0.939
# pr_auc    binary     0.946
```

### Multiclass Classification

```r
multi_metrics <- metric_set(
  accuracy,
  bal_accuracy,
  kap,
  roc_auc,
  precision,
  recall
)

# Specify macro averaging for precision/recall
hpc_cv |>
  multi_metrics(
    truth = obs,
    VF:L,               # Probability columns
    estimate = pred,
    estimator = "macro"
  )
```

### Cross-Validation

```r
library(rsample)

# Define metrics once
cv_metrics <- metric_set(rmse, rsq, mae)

# Use across all folds
cv_results <- vfold_cv(training_data, v = 10) |>
  mutate(
    metrics = map(splits, function(split) {
      # Fit model and predict
      model <- fit_model(analysis(split))
      preds <- predict(model, assessment(split))

      # Calculate all metrics at once
      cv_metrics(
        assessment(split),
        truth = outcome,
        estimate = preds
      )
    })
  )

# Aggregate across folds
cv_results |>
  unnest(metrics) |>
  group_by(.metric) |>
  summarize(mean = mean(.estimate), se = sd(.estimate))
```

### With Groupwise Metrics

```r
# Create groupwise metric
accuracy_diff <- new_groupwise_metric(
  fn = accuracy,
  name = "accuracy_diff",
  aggregate = function(x) diff(range(x$.estimate))
)

# Combine with regular metrics
fairness_metrics <- metric_set(
  accuracy,
  precision,
  recall,
  accuracy_diff(protected_attr)  # Add groupwise metric
)

fairness_metrics(data, truth = obs, estimate = pred)
```

## Creating Custom Metrics for metric_set()

To use your custom metric in a set, wrap it with the appropriate `new_*_metric()`:

```r
# Define your metric function
my_custom_metric <- function(data, truth, estimate, na_rm = TRUE, ...) {
  # Implementation
  # ...

  tibble(
    .metric = "my_custom",
    .estimator = "standard",
    .estimate = result
  )
}

# Wrap with new_*_metric() - required for metric_set()
my_custom_metric <- new_numeric_metric(
  my_custom_metric,
  direction = "maximize"
)

# Now it works in metric sets
my_metrics <- metric_set(rmse, mae, my_custom_metric)
```

**Key requirements:**
1. Must be wrapped with `new_*_metric()`
2. Must follow standard yardstick signature patterns
3. Must return standard yardstick output format

## Using with tune Package

Metric sets integrate with tune for model tuning:

```r
library(tune)
library(workflows)

# Define metrics for tuning
tune_metrics <- metric_set(
  rmse,
  rsq,
  mae
)

# Use in tune_grid()
tune_results <- tune_grid(
  workflow,
  resamples = cv_folds,
  grid = param_grid,
  metrics = tune_metrics  # Pass metric set
)

# Best models selected based on all metrics
show_best(tune_results, metric = "rmse")
```

## Performance Benefits

Metric sets are more efficient than individual calls:

```r
# Inefficient - confusion matrix calculated 3 times
accuracy(data, truth, estimate)
precision(data, truth, estimate)
recall(data, truth, estimate)

# Efficient - confusion matrix calculated once, shared
metrics <- metric_set(accuracy, precision, recall)
metrics(data, truth, estimate)
```

**Shared calculations:**
- Confusion matrices (for class metrics)
- ROC curves (for ROC-based metrics)
- Group-by operations
- Missing value handling

## Advanced Patterns

### Conditional Metrics

```r
# Select metrics based on data
metrics <- if (is_binary) {
  metric_set(accuracy, sensitivity, specificity, roc_auc)
} else {
  metric_set(accuracy, bal_accuracy, kap)
}

metrics(data, truth = obs, estimate = pred)
```

### Parameterized Sets

```r
create_metric_set <- function(include_auc = TRUE) {
  base_metrics <- c(accuracy, precision, recall)

  if (include_auc) {
    base_metrics <- c(base_metrics, list(roc_auc))
  }

  do.call(metric_set, base_metrics)
}

# Use
metrics <- create_metric_set(include_auc = TRUE)
```

### Multiple Tweaked Versions

```r
# Different F-measures
f0.5 <- metric_tweak("f0.5_meas", f_meas, beta = 0.5)
f1 <- f_meas
f2 <- metric_tweak("f2_meas", f_meas, beta = 2)

# All in one set
f_metrics <- metric_set(f0.5, f1, f2)
```

## Troubleshooting

### Error: Cannot mix metric types

```r
# Error
metric_set(rmse, accuracy)
```

**Solution:** Keep metrics of compatible types together.

### Error: `estimate` not found

```r
# Wrong
class_metrics(data, truth, pred)
```

**Solution:** Name the estimate argument:
```r
class_metrics(data, truth, estimate = pred)
```

### Error: Metric doesn't work in set

```r
my_metric <- function(data, truth, estimate) { ... }
metric_set(rmse, my_metric)  # Error
```

**Solution:** Wrap custom metrics:
```r
my_metric <- new_numeric_metric(my_metric, direction = "minimize")
metric_set(rmse, my_metric)  # Works
```

## Best Practices

1. **Define once, use everywhere**: Create metric sets at the top of your analysis
2. **Name your sets**: Use descriptive names like `classification_metrics`, not `metrics`
3. **Use with groups**: Leverage group-aware behavior for cross-validation
4. **Tweak before combining**: Set custom parameters with `metric_tweak()` first
5. **Keep compatible types**: Don't mix numeric, class, and survival metrics
6. **Named estimate**: Always name the `estimate` argument for class/survival metrics
7. **Integration**: Use with tune package for consistent tuning metrics

## Common Metric Sets

```r
# Standard regression
regression_std <- metric_set(rmse, mae, rsq)

# Regression with alternatives
regression_robust <- metric_set(mae, huber_loss, mape)

# Binary classification
binary_clf <- metric_set(
  accuracy, sensitivity, specificity,
  roc_auc, pr_auc
)

# Multiclass classification
multiclass_clf <- metric_set(
  accuracy, bal_accuracy, kap,
  roc_auc  # Uses hand_till method for multiclass
)

# Survival analysis
survival_std <- metric_set(
  concordance_survival,
  brier_survival,
  brier_survival_integrated
)

# Fairness analysis
fairness_set <- metric_set(
  accuracy,
  demographic_parity(group),
  equal_opportunity(group)
)
```

## See Also

- [Metric System](metric-system.md) - Understanding basic metric architecture
- [Groupwise Metrics](groupwise-metrics.md) - Creating disparity metrics
- [metric_tweak()](metric-system.md#using-metric_tweak-for-variations) - Customizing metric parameters
- `?metric_set` - Full documentation
