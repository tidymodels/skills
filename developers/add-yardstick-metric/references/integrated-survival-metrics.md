# Integrated Survival Metrics

Integrated survival metrics aggregate time-dependent performance across all evaluation times into a single overall value. These are summary metrics calculated from dynamic survival metrics.

## Overview

**Use when:**
- Truth is a **Surv object** (from the survival package)
- Predictions are **survival probabilities** at multiple time points
- You want **one overall value** that summarizes performance across time

**Key characteristics:**
- Builds on dynamic survival metrics
- Uses area-under-curve integration (trapezoidal rule)
- Normalizes by max evaluation time
- Returns `.estimator = "standard"`

**Examples:** Integrated Brier Score, Integrated ROC AUC

**Reference implementation:** `R/surv-brier_survival_integrated.R` in yardstick repository

## Pattern: Two-Function Approach

Unlike other metric types, integrated metrics typically:
1. Call the corresponding dynamic metric
2. Integrate the results

### 1. Implementation Function

```r
# Internal calculation logic
my_metric_integrated_impl <- function(truth, estimate, case_weights) {
  # Call the dynamic version
  res <- my_metric_vec(
    truth = truth,
    estimate = estimate,
    na_rm = FALSE,
    case_weights = case_weights
  )

  # Integrate using trapezoidal rule
  # Normalize by max eval_time to keep same scale
  auc(res$.eval_time, res$.estimate) / max(res$.eval_time)
}
```

### 2. Vector Interface

```r
#' @export
my_metric_integrated_vec <- function(truth, estimate, na_rm = TRUE,
                                     case_weights = NULL, ...) {
  # Validate na_rm parameter
  check_bool(na_rm)

  # Validate inputs (uses dynamic survival check)
  check_dynamic_survival_metric(truth, estimate, case_weights)

  # Check minimum evaluation times
  num_eval_times <- get_unique_eval_times(estimate)
  if (num_eval_times < 2) {
    cli::cli_abort(
      "At least 2 evaluation times are required.
      Only {num_eval_times} unique time was given."
    )
  }

  # Handle missing values
  if (na_rm) {
    result <- yardstick_remove_missing(truth, seq_along(estimate), case_weights)
    truth <- result$truth
    estimate <- estimate[result$estimate]
    case_weights <- result$case_weights
  } else {
    any_missing <- yardstick_any_missing(truth, estimate, case_weights)
    if (any_missing) {
      return(NA_real_)
    }
  }

  # Call implementation
  my_metric_integrated_impl(truth, estimate, case_weights)
}

# Helper to get number of evaluation times
get_unique_eval_times <- function(x) {
  length(x[[1]]$.eval_time)
}
```

### 3. Data Frame Method

```r
#' My Integrated Survival Metric
#'
#' Integrated version of my_metric across all evaluation times.
#'
#' @family integrated survival metrics
#' @templateVar fn my_metric_integrated
#' @template return-dynamic-survival
#'
#' @param data A data frame
#' @param truth Unquoted column with Surv object
#' @param ... Unquoted column(s) with survival predictions (list-column)
#' @param na_rm Remove missing values (default TRUE)
#' @param case_weights Optional case weights column
#'
#' @export
my_metric_integrated <- function(data, ...) {
  UseMethod("my_metric_integrated")
}

my_metric_integrated <- new_integrated_survival_metric(
  my_metric_integrated,
  direction = "minimize",  # or "maximize"
  range = c(0, 1)  # or other appropriate range
)

#' @export
#' @rdname my_metric_integrated
my_metric_integrated.data.frame <- function(data, truth, ..., na_rm = TRUE,
                                            case_weights = NULL) {
  # Note: Uses dynamic_survival_metric_summarizer
  dynamic_survival_metric_summarizer(
    name = "my_metric_integrated",
    fn = my_metric_integrated_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    ...,
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights)
  )
}
```

## Complete Example: Integrated Brier Score

Integrated Brier score summarizes time-dependent Brier scores across all evaluation times.

```r
# R/brier_survival_integrated.R

# 1. Implementation function
brier_survival_integrated_impl <- function(truth, estimate, case_weights) {
  # Call dynamic version
  res <- brier_survival_vec(
    truth = truth,
    estimate = estimate,
    na_rm = FALSE,
    case_weights = case_weights
  )

  # Integrate and normalize
  auc(res$.eval_time, res$.estimate) / max(res$.eval_time)
}

# Helper to get unique eval times
get_unique_eval_times <- function(x) {
  # Since validation ensures they're all the same
  length(x[[1]]$.eval_time)
}

# 2. Vector interface
#' @export
brier_survival_integrated_vec <- function(truth, estimate, na_rm = TRUE,
                                          case_weights = NULL, ...) {
  check_bool(na_rm)
  check_dynamic_survival_metric(truth, estimate, case_weights)

  num_eval_times <- get_unique_eval_times(estimate)
  if (num_eval_times < 2) {
    cli::cli_abort(
      "At least 2 evaluation times are required.
      Only {num_eval_times} unique time was given."
    )
  }

  if (na_rm) {
    result <- yardstick_remove_missing(truth, seq_along(estimate), case_weights)
    truth <- result$truth
    estimate <- estimate[result$estimate]
    case_weights <- result$case_weights
  } else {
    any_missing <- yardstick_any_missing(truth, estimate, case_weights)
    if (any_missing) {
      return(NA_real_)
    }
  }

  brier_survival_integrated_impl(truth, estimate, case_weights)
}

# 3. Data frame method
#' @export
brier_survival_integrated <- function(data, ...) {
  UseMethod("brier_survival_integrated")
}

brier_survival_integrated <- new_integrated_survival_metric(
  brier_survival_integrated,
  direction = "minimize",
  range = c(0, 1)
)

#' @export
#' @rdname brier_survival_integrated
brier_survival_integrated.data.frame <- function(data, truth, ..., na_rm = TRUE,
                                                 case_weights = NULL) {
  dynamic_survival_metric_summarizer(
    name = "brier_survival_integrated",
    fn = brier_survival_integrated_vec,
    data = data,
    truth = !!enquo(truth),
    ...,
    na_rm = na_rm,
    case_weights = !!enquo(case_weights)
  )
}
```

## Key Validation Function

```r
check_dynamic_survival_metric(truth, estimate, case_weights)
```

Integrated metrics use the same validation as dynamic metrics since they operate on the same input format.

**Additional validation:**
- At least 2 evaluation times are required for integration
- All observations must have the same evaluation times

## Input Format

Same as dynamic survival metrics. See [Dynamic Survival Metrics](dynamic-survival-metrics.md).

### Truth: Surv Object

```r
library(survival)
truth <- Surv(time = c(5, 8, 10, 12), event = c(1, 0, 1, 1))
```

### Estimate: List-Column of Data Frames

```r
# Each observation has predictions at multiple eval_times
estimate <- list(
  data.frame(
    .eval_time = c(100, 200, 300),
    .pred_survival = c(0.9, 0.8, 0.7),
    .weight_censored = c(1.0, 1.05, 1.1)
  ),
  data.frame(
    .eval_time = c(100, 200, 300),
    .pred_survival = c(0.95, 0.85, 0.75),
    .weight_censored = c(1.0, 1.05, 1.1)
  )
)
```

## Integration Method

Integrated metrics use the **trapezoidal rule** to approximate area under the curve:

```r
# Example: Brier scores at different times
eval_times <- c(100, 200, 300, 400)
brier_scores <- c(0.05, 0.08, 0.12, 0.15)

# Trapezoidal rule
area <- auc(eval_times, brier_scores)
# ≈ (100 * (0.05 + 0.08)/2) + (100 * (0.08 + 0.12)/2) + ...

# Normalize by max time to keep same scale as dynamic metric
integrated_score <- area / max(eval_times)
# = area / 400
```

This normalization ensures:
- Same scale as the underlying dynamic metric (e.g., 0-1 for Brier)
- Comparable across different time ranges
- Interpretable as "average" performance over time

## Testing

```r
# tests/testthat/test-brier_survival_integrated.R

test_that("brier_survival_integrated works correctly", {
  lung_surv <- data.frame(
    time = c(100, 200, 150),
    event = c(1, 0, 1)
  )
  lung_surv$surv_obj <- survival::Surv(lung_surv$time, lung_surv$event)

  lung_surv$.pred <- list(
    data.frame(.eval_time = c(50, 100, 150),
               .pred_survival = c(0.9, 0.8, 0.7),
               .weight_censored = c(1.0, 1.0, 1.0)),
    data.frame(.eval_time = c(50, 100, 150),
               .pred_survival = c(0.95, 0.9, 0.85),
               .weight_censored = c(1.0, 1.0, 1.0)),
    data.frame(.eval_time = c(50, 100, 150),
               .pred_survival = c(0.85, 0.7, 0.6),
               .weight_censored = c(1.0, 1.0, 1.0))
  )

  result <- brier_survival_integrated(lung_surv, truth = surv_obj, .pred)

  # Should return single row (integrated across times)
  expect_equal(nrow(result), 1)
  expect_equal(result$.metric, "brier_survival_integrated")
  expect_true(result$.estimate >= 0 && result$.estimate <= 1)
})

test_that("brier_survival_integrated requires multiple eval_times", {
  lung_surv <- data.frame(
    time = c(100, 200),
    event = c(1, 0)
  )
  lung_surv$surv_obj <- survival::Surv(lung_surv$time, lung_surv$event)

  # Only one eval_time
  lung_surv$.pred <- list(
    data.frame(.eval_time = 100, .pred_survival = 0.8,
               .weight_censored = 1.0),
    data.frame(.eval_time = 100, .pred_survival = 0.9,
               .weight_censored = 1.0)
  )

  expect_error(
    brier_survival_integrated(lung_surv, truth = surv_obj, .pred),
    "At least 2 evaluation times"
  )
})

test_that("brier_survival_integrated < max dynamic score", {
  # Integrated score should be reasonable relative to dynamic scores
  lung_surv <- data.frame(
    time = c(100, 200, 150),
    event = c(1, 0, 1)
  )
  lung_surv$surv_obj <- survival::Surv(lung_surv$time, lung_surv$event)

  lung_surv$.pred <- list(
    data.frame(.eval_time = c(50, 100),
               .pred_survival = c(0.9, 0.8),
               .weight_censored = c(1.0, 1.0)),
    data.frame(.eval_time = c(50, 100),
               .pred_survival = c(0.95, 0.9),
               .weight_censored = c(1.0, 1.0)),
    data.frame(.eval_time = c(50, 100),
               .pred_survival = c(0.85, 0.7),
               .weight_censored = c(1.0, 1.0))
  )

  integrated <- brier_survival_integrated(lung_surv, truth = surv_obj, .pred)
  dynamic <- brier_survival(lung_surv, truth = surv_obj, .pred)

  # Integrated should be between min and max of dynamic scores
  expect_true(integrated$.estimate >= min(dynamic$.estimate))
  expect_true(integrated$.estimate <= max(dynamic$.estimate))
})
```

## Common Patterns

### Calling Dynamic Metric

```r
# Get time-specific values
res <- my_metric_vec(
  truth = truth,
  estimate = estimate,
  na_rm = FALSE,  # Already handled
  case_weights = case_weights
)
# Returns tibble with .eval_time and .estimate columns
```

### Integration with Normalization

```r
# Integrate using trapezoidal rule
area <- auc(res$.eval_time, res$.estimate)

# Normalize by time range
integrated_value <- area / max(res$.eval_time)
```

### Validation for Integration

```r
# Check sufficient evaluation times
num_eval_times <- get_unique_eval_times(estimate)
if (num_eval_times < 2) {
  cli::cli_abort("At least 2 evaluation times are required.")
}
```

## Key Differences from Other Metric Types

| Aspect | Integrated Survival | Dynamic Survival | Static Survival |
|--------|---------------------|------------------|-----------------|
| Output | Single value | Multiple (per time) | Single value |
| Calculation | Integration | Per eval_time | Overall |
| Predictions | Survival curves | Survival curves | Single numeric |
| Interpretation | Average over time | Time-specific | Overall |

## Relationship to Dynamic Metrics

Integrated metrics are **aggregations** of dynamic metrics:

```
Dynamic Metric → Multiple values (one per eval_time)
                    ↓
              (Integration)
                    ↓
Integrated Metric → Single value (across all times)
```

Think of integrated metrics as:
- **Time-averaged** performance
- **Area under the performance curve**
- **Overall summary** of time-specific metrics

## Best Practices

1. **Require minimum 2 eval_times**: Integration needs at least two points
2. **Reuse dynamic implementation**: Call the dynamic _vec function internally
3. **Normalize by time range**: Divide by max eval_time to maintain scale
4. **Use trapezoidal rule**: Via `auc()` helper function
5. **Validate consistently**: Use same validation as dynamic metrics
6. **Document interpretation**: Explain that it's an average over time
7. **Check time consistency**: All observations should have same eval_times

## Common Metrics

- **Integrated Brier Score**: Average Brier score across time
- **Integrated ROC AUC**: Average AUC across time
- **Integrated Calibration**: Average calibration across time

## Helper Functions

```r
# Get unique evaluation times
get_unique_eval_times <- function(x) {
  length(x[[1]]$.eval_time)
}

# Area under curve (trapezoidal rule)
auc <- function(x, y) {
  # Typically available in yardstick or you implement:
  n <- length(x)
  sum(diff(x) * (y[-1] + y[-n]) / 2)
}
```

## See Also

- [Dynamic Survival Metrics](dynamic-survival-metrics.md) - Base time-dependent metrics
- [Static Survival Metrics](static-survival-metrics.md) - Overall metrics without time
- [Metric System](metric-system.md) - Understanding metric architecture
