# Static Survival Metrics

Static survival metrics evaluate a single numeric prediction against
right-censored survival data. These metrics produce one overall value per
observation.

## Overview

**Use when:**

- Truth is a **Surv object** (from the survival package)

- Predictions are **single numeric values** (e.g., predicted time, risk score)

- You want one overall metric value (not time-dependent)

**Key characteristics:**

- Works with right-censored data

- Handles comparable pairs (accounts for censoring)

- Returns `.estimator = "standard"`

**Examples:** Concordance Index

**Reference implementation:** `R/surv-concordance_survival.R` in yardstick
repository

## Pattern: Three-Function Approach

### 1. Implementation Function

```r
# Internal calculation logic
my_metric_impl <- function(truth, estimate, case_weights = NULL) {
  # truth: Surv object
  # estimate: numeric vector
  # case_weights: numeric vector or NULL

  if (is.null(case_weights)) {
    case_weights <- rep(1, length(estimate))
  } else {
    case_weights <- vctrs::vec_cast(case_weights, to = double())
  }

  # Use survival package functions
  survival::concordance(truth ~ estimate, weights = case_weights)$concordance
}
```

### 2. Vector Interface

```r
#' @export
my_metric_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Validate na_rm parameter
  check_bool(na_rm)

  # Validate inputs
  check_static_survival_metric(truth, estimate, case_weights)

  # Handle missing values
  if (na_rm) {
    result <- yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  # Call implementation
  my_metric_impl(truth, estimate, case_weights)
}
```

### 3. Data Frame Method

```r
#' My Static Survival Metric
#'
#' Description of what this metric measures.
#'
#' @family static survival metrics
#' @templateVar fn my_metric
#' @template return
#'
#' @param data A data frame
#' @param truth Unquoted column with Surv object
#' @param estimate Unquoted column with numeric predictions
#' @param na_rm Remove missing values (default TRUE)
#' @param case_weights Optional case weights column
#' @param ... Not currently used
#'
#' @export
my_metric <- function(data, ...) {
  UseMethod("my_metric")
}

my_metric <- new_static_survival_metric(
  my_metric,
  direction = "maximize",  # or "minimize"
  range = c(0, 1)  # or other appropriate range
)

#' @export
#' @rdname my_metric
my_metric.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                                 case_weights = NULL, ...) {
  static_survival_metric_summarizer(
    name = "my_metric",
    fn = my_metric_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights)
  )
}
```

## Complete Example: Concordance Index

The concordance index measures the proportion of comparable pairs where
predictions and outcomes are concordant.

```r
# R/concordance_survival.R

# 1. Implementation function
concordance_survival_impl <- function(truth, estimate, case_weights) {
  if (is.null(case_weights)) {
    case_weights <- rep(1, length(estimate))
  } else {
    case_weights <- vctrs::vec_cast(case_weights, to = double())
  }

  survival::concordance(truth ~ estimate, weights = case_weights)$concordance
}

# 2. Vector interface
#' @export
concordance_survival_vec <- function(truth, estimate, na_rm = TRUE,
                                     case_weights = NULL, ...) {
  check_bool(na_rm)
  check_static_survival_metric(truth, estimate, case_weights)

  if (na_rm) {
    result <- yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  concordance_survival_impl(truth, estimate, case_weights)
}

# 3. Data frame method
#' @export
concordance_survival <- function(data, ...) {
  UseMethod("concordance_survival")
}

concordance_survival <- new_static_survival_metric(
  concordance_survival,
  direction = "maximize",
  range = c(0, 1)
)

#' @export
#' @rdname concordance_survival
concordance_survival.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                                            case_weights = NULL, ...) {
  static_survival_metric_summarizer(
    name = "concordance_survival",
    fn = concordance_survival_vec,
    data = data,
    truth = !!enquo(truth),
    estimate = !!enquo(estimate),
    na_rm = na_rm,
    case_weights = !!enquo(case_weights)
  )
}
```

## Key Validation Function

```r
check_static_survival_metric(truth, estimate, case_weights)
```

This validates:

- `truth` is a Surv object

- `estimate` is a numeric vector

- Lengths match

- `case_weights` are valid (if provided)

## Input Format

### Truth: Surv Object

```r
library(survival)

# Create Surv object
truth <- Surv(
  time = c(5, 8, 10, 12),      # Observed time
  event = c(1, 0, 1, 1)        # 1 = event, 0 = censored
)
```

### Estimate: Numeric Vector

```r
# Single numeric prediction per observation
estimate <- c(4.5, 9.0, 8.5, 11.0)  # Predicted times or risk scores
```

## Understanding Comparable Pairs

Two observations are comparable if: 1. Both experienced an event (at different
times), or 2. The observation with shorter time experienced an event

A pair is concordant if:

- Higher risk score → shorter survival time (for risk predictions)

- Lower predicted time → shorter actual time (for time predictions)

```r
# Example: Concordance logic
# Obs 1: time=5, event=1, pred=4.5
# Obs 2: time=8, event=1, pred=9.0
# Comparable? Yes (both events)
# Concordant? Yes (shorter time has lower prediction)
```

## Testing

```r
# tests/testthat/test-concordance_survival.R

test_that("concordance_survival works correctly", {
  df <- data.frame(
    time = c(5, 8, 10, 12),
    event = c(1, 0, 1, 1),
    pred = c(4.5, 9.0, 8.5, 11.0)
  )
  df$surv_obj <- survival::Surv(df$time, df$event)

  result <- concordance_survival(df, truth = surv_obj, estimate = pred)

  expect_equal(result$.metric, "concordance_survival")
  expect_equal(result$.estimator, "standard")
  expect_true(result$.estimate >= 0 && result$.estimate <= 1)
})

test_that("concordance_survival handles all censored", {
  df <- data.frame(
    time = c(5, 8, 10),
    event = c(0, 0, 0),  # All censored
    pred = c(4.5, 9.0, 8.5)
  )
  df$surv_obj <- survival::Surv(df$time, df$event)

  # May return NA or special value when no comparable pairs
  result <- concordance_survival(df, truth = surv_obj, estimate = pred)
  expect_true(is.na(result$.estimate) || is.numeric(result$.estimate))
})

test_that("concordance_survival validates inputs", {
  df <- data.frame(
    time = c(5, 8, 10),
    event = c(1, 0, 1),
    pred = c("a", "b", "c")  # Wrong type
  )
  df$surv_obj <- survival::Surv(df$time, df$event)

  expect_error(concordance_survival(df, truth = surv_obj, estimate = pred))
})

test_that("concordance_survival works with case weights", {
  df <- data.frame(
    time = c(5, 8, 10, 12),
    event = c(1, 0, 1, 1),
    pred = c(4.5, 9.0, 8.5, 11.0),
    weights = c(1, 2, 1, 1)
  )
  df$surv_obj <- survival::Surv(df$time, df$event)

  result <- concordance_survival(df, truth = surv_obj, estimate = pred,
                                  case_weights = weights)
  expect_true(is.numeric(result$.estimate))
})
```

## Common Patterns

### Creating Surv Objects

```r
# Right-censored data
surv_obj <- survival::Surv(time = time_vec, event = event_vec)

# In data frame
df$surv_obj <- survival::Surv(df$time, df$event)
```

### Using Survival Package Functions

```r
# Concordance
survival::concordance(truth ~ estimate, weights = case_weights)$concordance

# Or use survcomp, survAUC, or other packages as needed
```

### Handling Case Weights

```r
if (is.null(case_weights)) {
  case_weights <- rep(1, length(estimate))
} else {
  case_weights <- vctrs::vec_cast(case_weights, to = double())
}
```

## Key Differences from Other Metric Types

| Aspect        | Static Survival    | Dynamic Survival        | Numeric        |
| ------------- | ------------------ | ----------------------- | -------------- |
| Truth type    | Surv object        | Surv object             | Numeric        |
| Estimate type | Single numeric     | List of data.frames     | Numeric        |
| Output        | One value          | One value per eval_time | One value      |
| Censoring     | Explicitly handled | Explicitly handled      | Not applicable |

## Dependencies

Static survival metrics often depend on the survival package:

```r
# In DESCRIPTION
Imports:
    survival,
    vctrs

# In R/package.R
#' @importFrom survival Surv
```

## Best Practices

1. **Use appropriate survival functions**: Leverage existing implementations
   from survival package
2. **Handle censoring correctly**: Use functions that account for censoring
3. **Validate Surv objects**: Use `check_static_survival_metric()`
4. **Convert case weights**: Always cast to double with `vctrs::vec_cast()`
5. **Document interpretation**: Explain what concordance/other metrics mean for
   survival data
6. **Handle edge cases**: Consider all-censored data, ties, etc.

## Common Metrics

- **Concordance Index (C-index)**: Proportion of concordant pairs

- **Somers' D**: Related to concordance, ranges from -1 to 1

- **Royston's D**: See
  [linear-predictor-survival-metrics.md](linear-predictor-survival-metrics.md)

## See Also

- [Dynamic Survival Metrics](dynamic-survival-metrics.md) - Time-dependent
  metrics

- [Integrated Survival Metrics](integrated-survival-metrics.md) - Integrated
  over time

- [Linear Predictor Survival Metrics](linear-predictor-survival-metrics.md) -
  Using linear predictors

- [Metric System](metric-system.md) - Understanding metric architecture
