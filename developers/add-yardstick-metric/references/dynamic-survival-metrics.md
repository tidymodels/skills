# Dynamic Survival Metrics

Dynamic survival metrics evaluate time-dependent survival predictions at
specific evaluation times. These metrics produce one value per evaluation time.

## Overview

**Use when:**

- Truth is a **Surv object** (from the survival package)

- Predictions are **survival probabilities** at specific time points

- You want metrics at each evaluation time (e.g., `.eval_time = 100, 200, 300`)

**Key characteristics:**

- Returns multiple rows (one per `.eval_time`)

- Uses inverse probability of censoring weights (IPCW)

- Automatically groups by `.eval_time`

- Returns `.estimator = "standard"`

**Examples:** Time-dependent Brier Score, Time-dependent ROC AUC

**Reference implementations:**

- Time-dependent Brier: `R/surv-brier_survival.R`

- Time-dependent ROC AUC: `R/surv-roc_auc_survival.R`

## Pattern: Three-Function Approach

### 1. Implementation Function

```r
# Internal calculation logic
my_metric_impl <- function(truth, estimate, censoring_weights, case_weights,
                           eval_time) {
  # truth: Surv object
  # estimate: numeric vector of survival probabilities at eval_time
  # censoring_weights: numeric vector of IPCW weights
  # case_weights: numeric vector or NULL
  # eval_time: single evaluation time (from grouping)

  surv_time <- .extract_surv_time(truth)
  surv_status <- .extract_surv_status(truth)

  if (!is.null(case_weights)) {
    case_weights <- vctrs::vec_cast(case_weights, to = double())
    norm_const <- sum(case_weights)
  } else {
    case_weights <- rep(1, length(estimate))
    norm_const <- sum(!survival::is.na.Surv(truth))
  }

  # Calculate metric using censoring weights
  # ... implementation details ...
}
```

### 2. Vector Interface

```r
#' @export
my_metric_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Validate na_rm parameter
  check_bool(na_rm)

  # Validate inputs
  check_dynamic_survival_metric(truth, estimate, case_weights)

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

  # Group by eval_time and calculate
  dplyr::bind_rows(estimate) |>
    dplyr::group_by(.eval_time) |>
    dplyr::summarize(
      .estimate = my_metric_impl(
        truth,
        .pred_survival,
        .weight_censored,
        case_weights,
        .eval_time
      )
    )
}
```

### 3. Data Frame Method

```r
#' My Dynamic Survival Metric
#'
#' Description of what this metric measures at each evaluation time.
#'
#' @family dynamic survival metrics
#' @templateVar fn my_metric
#' @template return-dynamic-survival
#'
#' @param data A data frame
#' @param truth Unquoted column with Surv object
#' @param ... Unquoted column(s) with survival predictions (list-column)
#' @param na_rm Remove missing values (default TRUE)
#' @param case_weights Optional case weights column
#'
#' @export
my_metric <- function(data, ...) {
  UseMethod("my_metric")
}

my_metric <- new_dynamic_survival_metric(
  my_metric,
  direction = "minimize",  # or "maximize"
  range = c(0, 1)  # or other appropriate range
)

#' @export
#' @rdname my_metric
my_metric.data.frame <- function(data, truth, ..., na_rm = TRUE,
                                 case_weights = NULL) {
  dynamic_survival_metric_summarizer(
    name = "my_metric",
    fn = my_metric_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    ...,
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights)
  )
}
```

## Complete Example: Brier Survival Score

Time-dependent Brier score measures mean squared error at each evaluation time.

```r
# R/brier_survival.R

# 1. Implementation function
brier_survival_impl <- function(truth, estimate, censoring_weights,
                                case_weights, eval_time) {
  surv_time <- .extract_surv_time(truth)
  surv_status <- .extract_surv_status(truth)

  if (!is.null(case_weights)) {
    case_weights <- vctrs::vec_cast(case_weights, to = double())
    norm_const <- sum(case_weights)
  } else {
    case_weights <- rep(1, length(estimate))
    norm_const <- sum(!survival::is.na.Surv(truth))
  }

  # Two categories: event before eval_time, survived past eval_time
  category_1 <- surv_time <= eval_time & surv_status == 1
  category_2 <- surv_time > eval_time

  # Squared error with IPCW weights
  res <- (category_1 * estimate^2 * censoring_weights) +
         (category_2 * (1 - estimate)^2 * censoring_weights)

  res <- res * case_weights
  sum(res, na.rm = TRUE) / norm_const
}

# 2. Vector interface
#' @export
brier_survival_vec <- function(truth, estimate, na_rm = TRUE,
                                case_weights = NULL, ...) {
  check_bool(na_rm)
  check_dynamic_survival_metric(truth, estimate, case_weights)

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

  dplyr::bind_rows(estimate) |>
    dplyr::group_by(.eval_time) |>
    dplyr::summarize(
      .estimate = brier_survival_impl(
        truth,
        .pred_survival,
        .weight_censored,
        case_weights,
        .eval_time
      )
    )
}

# 3. Data frame method
#' @export
brier_survival <- function(data, ...) {
  UseMethod("brier_survival")
}

brier_survival <- new_dynamic_survival_metric(
  brier_survival,
  direction = "minimize",
  range = c(0, 1)
)

#' @export
#' @rdname brier_survival
brier_survival.data.frame <- function(data, truth, ..., na_rm = TRUE,
                                      case_weights = NULL) {
  dynamic_survival_metric_summarizer(
    name = "brier_survival",
    fn = brier_survival_vec,
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

This validates:

- `truth` is a Surv object

- `estimate` is a list-column of data.frames

- Each data.frame has required columns: `.eval_time`, `.pred_survival`,
  `.weight_censored`

- `case_weights` are valid (if provided)

## Input Format

### Truth: Surv Object

```r
library(survival)

# Create Surv object
truth <- Surv(
  time = c(5, 8, 10, 12),
  event = c(1, 0, 1, 1)
)
```

### Estimate: List-Column of Data Frames

Each element is a data.frame with three required columns:

```r
# For one observation
pred_df <- data.frame(
  .eval_time = c(100, 200, 300),           # Evaluation times
  .pred_survival = c(0.9, 0.8, 0.7),       # Predicted P(survive past time)
  .weight_censored = c(1.0, 1.05, 1.1)     # IPCW weights
)

# List column for multiple observations
estimate <- list(
  pred_df_obs1,
  pred_df_obs2,
  pred_df_obs3
)
```

### Creating IPCW Weights

Inverse probability of censoring weights can be created with:

```r
# Using parsnip helper (if available)
.censoring_weights_graf(truth, eval_times)

# Manual calculation using survival::survfit
```

## Understanding IPCW Weights

IPCW (Inverse Probability of Censoring Weighting) adjusts for censoring bias:

- Observations censored before eval_time cannot be classified as events

- IPCW up-weights similar uncensored observations to compensate

- Based on the censoring distribution (Graf et al., 1999)

```r
# Example interpretation
# If 20% of observations are censored at time t,
# remaining observations get weight ≈ 1.25 = 1/0.8
```

## Testing

```r
# tests/testthat/test-brier_survival.R

test_that("brier_survival works correctly", {
  # Create survival predictions
  lung_surv <- data.frame(
    time = c(100, 200, 150),
    event = c(1, 0, 1)
  )
  lung_surv$surv_obj <- survival::Surv(lung_surv$time, lung_surv$event)

  lung_surv$.pred <- list(
    data.frame(.eval_time = c(50, 100), .pred_survival = c(0.9, 0.8),
               .weight_censored = c(1.0, 1.0)),
    data.frame(.eval_time = c(50, 100), .pred_survival = c(0.95, 0.9),
               .weight_censored = c(1.0, 1.0)),
    data.frame(.eval_time = c(50, 100), .pred_survival = c(0.85, 0.7),
               .weight_censored = c(1.0, 1.0))
  )

  result <- brier_survival(lung_surv, truth = surv_obj, .pred)

  # Should have one row per eval_time
  expect_equal(nrow(result), 2)
  expect_equal(result$.eval_time, c(50, 100))
  expect_equal(result$.metric, c("brier_survival", "brier_survival"))
  expect_true(all(result$.estimate >= 0 & result$.estimate <= 1))
})

test_that("brier_survival validates input structure", {
  df <- data.frame(
    surv_obj = survival::Surv(c(10, 20), c(1, 0)),
    .pred = list(
      data.frame(.eval_time = 5),  # Missing required columns
      data.frame(.eval_time = 5)
    )
  )

  expect_error(brier_survival(df, truth = surv_obj, .pred))
})

test_that("brier_survival handles case weights", {
  lung_surv <- data.frame(
    time = c(100, 200, 150),
    event = c(1, 0, 1),
    weights = c(1, 2, 1)
  )
  lung_surv$surv_obj <- survival::Surv(lung_surv$time, lung_surv$event)

  lung_surv$.pred <- list(
    data.frame(.eval_time = 100, .pred_survival = 0.8, .weight_censored = 1.0),
    data.frame(.eval_time = 100, .pred_survival = 0.9, .weight_censored = 1.0),
    data.frame(.eval_time = 100, .pred_survival = 0.7, .weight_censored = 1.0)
  )

  result <- brier_survival(lung_surv, truth = surv_obj, .pred,
                           case_weights = weights)
  expect_true(is.numeric(result$.estimate))
})
```

## Common Patterns

### Extracting Survival Information

```r
# From Surv object
surv_time <- .extract_surv_time(truth)      # Observed time
surv_status <- .extract_surv_status(truth)  # Event indicator (1=event, 0=censored)
```

### Categorizing Observations

```r
# For Brier score at eval_time
category_1 <- surv_time <= eval_time & surv_status == 1  # Event before eval_time
category_2 <- surv_time > eval_time                       # Survived past eval_time

# Note: Censored before eval_time are handled by IPCW weights
```

### Grouping by Evaluation Time

```r
# Automatic grouping in vec function
dplyr::bind_rows(estimate) |>
  dplyr::group_by(.eval_time) |>
  dplyr::summarize(
    .estimate = my_metric_impl(...)
  )
```

## Key Differences from Other Metric Types

| Aspect      | Dynamic Survival             | Static Survival     | Integrated Survival    |
| ----------- | ---------------------------- | ------------------- | ---------------------- |
| Output      | Multiple rows (one per time) | Single value        | Single value           |
| Predictions | Survival probabilities       | Single numeric      | Survival probabilities |
| Eval times  | Explicit `.eval_time`        | Not applicable      | Integrated over times  |
| Use case    | Time-specific performance    | Overall performance | Overall performance    |

## Best Practices

1. **Use IPCW weights**: Always include `.weight_censored` in predictions
2. **Validate structure**: Use `check_dynamic_survival_metric()`
3. **Handle both categories**: Account for events before and survival past
   eval_time
4. **Group by eval_time**: Let the vec function handle grouping automatically
5. **Document time interpretation**: Explain what each eval_time represents
6. **Consider censoring patterns**: IPCW works best with informative censoring
   distribution

## Common Metrics

- **Brier Survival Score**: Mean squared error at each time

- **ROC AUC Survival**: Time-dependent ROC curve area

- **Time-dependent sensitivity/specificity**: Classification at each time

## See Also

- [Integrated Survival Metrics](integrated-survival-metrics.md) - Integrated
  over time

- [Static Survival Metrics](static-survival-metrics.md) - Overall metrics

- [Metric System](metric-system.md) - Understanding metric architecture
