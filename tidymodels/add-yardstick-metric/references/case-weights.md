# Handling Case Weights in Metrics

Case weights allow different observations to contribute differently to metric calculations. Understanding how to handle them properly is important for creating robust metrics.

## What Are Case Weights?

Case weights assign importance to individual observations:
- **Frequency weights**: Observation occurs multiple times
- **Importance weights**: Observation has different importance

## Parameter Signature

Always include `case_weights = NULL` parameter in your metric functions:

```r
metric_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Implementation
}

metric.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                              case_weights = NULL, ...) {
  # Implementation
}
```

## Handling Hardhat Weights

Hardhat (the package underlying tidymodels) provides special weight classes. Convert them to numeric:

```r
if (!is.null(case_weights)) {
  # Handle hardhat weights
  if (inherits(case_weights, "hardhat_importance_weights") ||
      inherits(case_weights, "hardhat_frequency_weights")) {
    case_weights <- as.double(case_weights)
  }
  # Now case_weights is numeric and can be used
}
```

## Using Case Weights in Calculations

### Numeric metrics

Use `weighted.mean()` from base R:

```r
metric_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  if (is.null(case_weights)) {
    mean(errors)
  } else {
    # Convert hardhat weights
    wts <- if (inherits(case_weights, c("hardhat_importance_weights",
                                        "hardhat_frequency_weights"))) {
      as.double(case_weights)
    } else {
      case_weights
    }
    weighted.mean(errors, w = wts)
  }
}
```

### Class metrics

Pass case_weights to `yardstick_table()`:

```r
metric_impl <- function(truth, estimate, estimator, event_level, case_weights) {
  # yardstick_table handles weights internally
  xtab <- yardstick::yardstick_table(truth, estimate, case_weights = case_weights)

  # Confusion matrix now has weighted counts
  metric_estimator_impl(xtab, estimator, event_level)
}
```

The confusion matrix will have weighted counts instead of simple counts.

### Probability metrics

Similar to numeric metrics:

```r
if (is.null(case_weights)) {
  mean((prob_estimate - truth_binary)^2)
} else {
  wts <- as.double(case_weights)  # Convert if needed
  weighted.mean((prob_estimate - truth_binary)^2, w = wts)
}
```

## NA Handling with Case Weights

Use `yardstick_remove_missing()` which handles case_weights automatically:

```r
if (na_rm) {
  result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
  truth <- result$truth
  estimate <- result$estimate
  case_weights <- result$case_weights  # Also filtered
} else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
  return(NA_real_)
}
```

## Validation

Validation functions handle case_weights:

```r
# For numeric metrics
yardstick::check_numeric_metric(truth, estimate, case_weights)

# For class metrics
yardstick::check_class_metric(truth, estimate, case_weights, estimator)

# For probability metrics
yardstick::check_prob_metric(truth, estimate, case_weights, estimator)
```

## Testing with Case Weights

### Test with numeric vectors

```r
test_that("case weights work correctly", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.5, 2.5, 3.5),
    weights = c(1, 2, 1)
  )

  # Calculate expected weighted value by hand
  # errors = abs(c(0.5, 0.5, 0.5))
  # weighted mean = (1*0.5 + 2*0.5 + 1*0.5) / (1+2+1) = 2/4 = 0.5

  result <- metric_vec(df$truth, df$estimate, case_weights = df$weights)
  expect_equal(result, 0.5)
})
```

### Test with hardhat weights

```r
test_that("works with hardhat case weights", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.5, 2.5, 3.5)
  )

  imp_wgt <- hardhat::importance_weights(c(1, 2, 1))
  freq_wgt <- hardhat::frequency_weights(c(1, 2, 1))

  expect_no_error(
    metric_vec(df$truth, df$estimate, case_weights = imp_wgt)
  )

  expect_no_error(
    metric_vec(df$truth, df$estimate, case_weights = freq_wgt)
  )
})
```

### Test that weighted differs from unweighted

```r
test_that("weighted and unweighted give different results", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.5, 2.0, 4.0),  # Different errors
    weights = c(1, 10, 1)          # Heavy weight on middle observation
  )

  unweighted <- metric_vec(df$truth, df$estimate)
  weighted <- metric_vec(df$truth, df$estimate, case_weights = df$weights)

  expect_false(unweighted == weighted)
})
```

## Common Patterns

### Converting weights once

Convert hardhat weights once at the start, not repeatedly:

```r
# Good: convert once
metric_impl <- function(truth, estimate, case_weights = NULL) {
  if (!is.null(case_weights)) {
    if (inherits(case_weights, c("hardhat_importance_weights",
                                 "hardhat_frequency_weights"))) {
      case_weights <- as.double(case_weights)
    }
  }

  # Now use case_weights multiple times
  weighted.mean(values1, w = case_weights)
  weighted.mean(values2, w = case_weights)
}

# Bad: converting repeatedly
metric_impl <- function(truth, estimate, case_weights = NULL) {
  result1 <- weighted.mean(values1, w = as.double(case_weights))
  result2 <- weighted.mean(values2, w = as.double(case_weights))  # Converting again!
}
```

### Conditional logic

```r
if (is.null(case_weights)) {
  mean(values)
} else {
  # Convert if needed
  wts <- if (inherits(case_weights, c("hardhat_importance_weights",
                                      "hardhat_frequency_weights"))) {
    as.double(case_weights)
  } else {
    case_weights
  }
  weighted.mean(values, w = wts)
}
```

## Documentation

Document case_weights in your roxygen:

```r
#' @param case_weights The optional column identifier for case weights. This
#'   should be an unquoted column name. Default is `NULL`.
```

Add case weights section to details:

```r
#' # Case weights
#'
#' This step performs an unsupervised operation that can utilize case weights.
#' As a result, case weights are used with frequency weights as well as
#' importance weights. For more information, see the documentation in
#' [yardstick::case_weights] and the examples on `tidymodels.org`.
```

## Edge Cases

### All-zero weights

```r
# weighted.mean() with all-zero weights returns NaN
weights <- c(0, 0, 0)
result <- weighted.mean(c(1, 2, 3), w = weights)
# result is NaN

# This is expected behavior - no observations have any weight
```

### Negative weights

Negative weights are mathematically possible but uncommon. Your validation (`check_*_metric()`) should catch invalid weights.

## Performance Tips

- Convert hardhat weights once, not in loops
- Pass weights to vectorized functions rather than implementing manual weighting
- Use `weighted.mean()` rather than manual `sum(x * w) / sum(w)`

## Next Steps

- Understand metric system: [metric-system.md](metric-system.md)
- Create numeric metrics: [numeric-metrics.md](numeric-metrics.md)
- Create class metrics: [class-metrics.md](class-metrics.md)
- Test comprehensively: [extension-requirements.md#testing-requirements](extension-requirements.md#testing-requirements)
