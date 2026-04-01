# Linear Predictor Survival Metrics

Linear predictor survival metrics evaluate linear predictor values (from Cox models or similar) against right-censored survival data. These metrics assess the prognostic separation provided by the linear predictor.

## Overview

**Use when:**

- Truth is a **Surv object** (from the survival package)

- Predictions are **linear predictor values** from a survival model

- You want to measure prognostic separation or explained variation

**Key characteristics:**

- Similar structure to static survival metrics

- Predictions are unbounded (not probabilities)

- Typically used with Cox proportional hazards models

- Returns `.estimator = "standard"`

**Examples:** Royston's D statistic, R² based on D

**Reference implementation:** `R/surv-royston.R` in yardstick repository

## Pattern: Three-Function Approach

### 1. Implementation Function

```r
# Internal calculation logic
my_metric_impl <- function(truth, estimate, case_weights = NULL) {
  # truth: Surv object
  # estimate: numeric vector (linear predictor values)
  # case_weights: numeric vector or NULL

  if (is.null(case_weights)) {
    case_weights <- rep(1, length(estimate))
  } else {
    case_weights <- vctrs::vec_cast(case_weights, to = double())
  }

  # Transform linear predictor to normal scores (Blom's method)
  bns <- normal_score_blom(estimate, case_weights)

  # Fit Cox model with normal scores
  fit <- survival::coxph(truth ~ bns, weights = case_weights)
  est <- unname(stats::coef(fit))

  # Calculate metric (e.g., R²_D for Royston)
  est^2 / (est^2 + pi^2 / 6)
}

# Helper: Blom's normal scores transformation
normal_score_blom <- function(x, case_weights) {
  # Implementation details...
}
```

### 2. Vector Interface

```r
#' @export
my_metric_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Validate na_rm parameter
  check_bool(na_rm)

  # Validate inputs
  check_linear_pred_survival_metric(truth, estimate, case_weights)

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
#' My Linear Predictor Survival Metric
#'
#' Description of what this metric measures.
#'
#' @family linear pred survival metrics
#' @templateVar fn my_metric
#' @template return
#'
#' @param data A data frame
#' @param truth Unquoted column with Surv object
#' @param estimate Unquoted column with linear predictor values
#' @param na_rm Remove missing values (default TRUE)
#' @param case_weights Optional case weights column
#' @param ... Not currently used
#'
#' @export
my_metric <- function(data, ...) {
  UseMethod("my_metric")
}

my_metric <- new_linear_pred_survival_metric(
  my_metric,
  direction = "maximize",  # or "minimize"
  range = c(0, 1)  # or other appropriate range
)

#' @export
#' @rdname my_metric
my_metric.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                                 case_weights = NULL, ...) {
  linear_pred_survival_metric_summarizer(
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

## Complete Example: Royston's D Statistic

Royston's D measures prognostic separation based on the standard deviation of the prognostic index.

```r
# R/royston_survival.R

# 1. Helper: Blom's normal score transformation
normal_score_blom <- function(x, case_weights) {
  # Include observations with zero weights
  x_0 <- tibble::tibble(.row = seq_along(x), x = x)

  rankits <- tibble::tibble(
    .row = rep(seq_along(x), times = case_weights),
    x = rep(x, times = case_weights),
  ) |>
    dplyr::mutate(
      x_first = rank(.data$x, ties.method = "first"),
      # Blom's transformation
      z = stats::qnorm((.data$x_first - 3 / 8) / (dplyr::n() + 1 / 4))
    ) |>
    # Average over ties
    dplyr::mutate(s = mean(.data$z), .by = "x") |>
    dplyr::slice(1, .by = .row)

  dplyr::left_join(x_0, rankits, by = c(".row")) |>
    dplyr::pull("s")
}

# 2. Implementation function
royston_survival_impl <- function(truth, estimate, case_weights) {
  if (is.null(case_weights)) {
    case_weights <- rep(1, length(estimate))
  } else {
    case_weights <- vctrs::vec_cast(case_weights, to = double())
  }

  # Transform to normal scores
  bns <- normal_score_blom(estimate, case_weights)

  # Fit Cox model
  fit <- survival::coxph(truth ~ bns, weights = case_weights)
  est <- unname(stats::coef(fit))

  # Calculate R²_D
  est^2 / (est^2 + pi^2 / 6)
}

# 3. Vector interface
#' @export
royston_survival_vec <- function(truth, estimate, na_rm = TRUE,
                                 case_weights = NULL, ...) {
  check_bool(na_rm)
  check_linear_pred_survival_metric(truth, estimate, case_weights)

  if (na_rm) {
    result <- yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  royston_survival_impl(truth, estimate, case_weights)
}

# 4. Data frame method
#' @export
royston_survival <- function(data, ...) {
  UseMethod("royston_survival")
}

royston_survival <- new_linear_pred_survival_metric(
  royston_survival,
  direction = "maximize",
  range = c(0, 1)
)

#' @export
#' @rdname royston_survival
royston_survival.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                                        case_weights = NULL, ...) {
  linear_pred_survival_metric_summarizer(
    name = "royston_survival",
    fn = royston_survival_vec,
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
check_linear_pred_survival_metric(truth, estimate, case_weights)
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
  time = c(5, 8, 10, 12),
  event = c(1, 0, 1, 1)
)
```

### Estimate: Linear Predictor Values

```r
# Numeric vector of linear predictor values (unbounded)
# From Cox model: linear_pred = X * beta
estimate <- c(-0.5, 0.2, 0.8, 1.2)

# Or from predict.coxph(..., type = "lp")
```

## Understanding Linear Predictors

Linear predictors from Cox models represent:

- **Log hazard ratio** relative to baseline

- **Prognostic index**: higher values = higher risk

- **Unbounded**: can be any real number

```r
# Example Cox model
fit <- survival::coxph(Surv(time, event) ~ age + sex, data = df)

# Linear predictor for new data
lp <- predict(fit, newdata = test_data, type = "lp")
# lp = beta_age * age + beta_sex * sex
```

## Transformations

Many linear predictor metrics use transformations to improve properties:

### Blom's Normal Score Transformation

```r
# Rank-based transformation to approximate normality
# Used in Royston's D

normal_score_blom <- function(x, case_weights) {
  # 1. Replicate based on weights
  # 2. Rank observations
  # 3. Transform ranks to normal quantiles
  # 4. Average over ties
  # See complete implementation above
}
```

This transformation:

- Removes dependence on scale of linear predictor

- Makes metric more robust

- Focuses on rank ordering rather than absolute values

## Testing

```r
# tests/testthat/test-royston_survival.R

test_that("royston_survival works correctly", {
  df <- data.frame(
    time = c(5, 8, 10, 12, 15),
    event = c(1, 0, 1, 1, 1),
    lp = c(-0.5, 0.2, 0.8, 1.2, 1.5)
  )
  df$surv_obj <- survival::Surv(df$time, df$event)

  result <- royston_survival(df, truth = surv_obj, estimate = lp)

  expect_equal(result$.metric, "royston_survival")
  expect_equal(result$.estimator, "standard")
  expect_true(result$.estimate >= 0 && result$.estimate <= 1)
})

test_that("royston_survival validates inputs", {
  df <- data.frame(
    time = c(5, 8, 10),
    event = c(1, 0, 1),
    lp = c("a", "b", "c")  # Wrong type
  )
  df$surv_obj <- survival::Surv(df$time, df$event)

  expect_error(royston_survival(df, truth = surv_obj, estimate = lp))
})

test_that("royston_survival handles perfect separation", {
  # Perfect prognostic separation
  df <- data.frame(
    time = c(1, 2, 3, 4, 5),
    event = c(1, 1, 1, 1, 1),
    lp = c(-2, -1, 0, 1, 2)  # Perfect ordering
  )
  df$surv_obj <- survival::Surv(df$time, df$event)

  result <- royston_survival(df, truth = surv_obj, estimate = lp)
  # Should be close to 1 (perfect)
  expect_true(result$.estimate > 0.9)
})

test_that("royston_survival works with case weights", {
  df <- data.frame(
    time = c(5, 8, 10, 12),
    event = c(1, 0, 1, 1),
    lp = c(-0.5, 0.2, 0.8, 1.2),
    weights = c(1, 2, 1, 1)
  )
  df$surv_obj <- survival::Surv(df$time, df$event)

  result <- royston_survival(df, truth = surv_obj, estimate = lp,
                             case_weights = weights)
  expect_true(is.numeric(result$.estimate))
})
```

## Common Patterns

### Using Cox Models

```r
# Fit Cox model within metric
fit <- survival::coxph(truth ~ transformed_estimate, weights = case_weights)

# Extract coefficient
est <- unname(stats::coef(fit))

# Calculate metric based on coefficient
```

### Handling Case Weights

```r
if (is.null(case_weights)) {
  case_weights <- rep(1, length(estimate))
} else {
  case_weights <- vctrs::vec_cast(case_weights, to = double())
}
```

### Rank-Based Calculations

```r
# Use ranks instead of raw values for robustness
ranks <- rank(estimate, ties.method = "average")

# Or use normal score transformation
normal_scores <- normal_score_blom(estimate, case_weights)
```

## Key Differences from Other Metric Types

| Aspect | Linear Pred Survival | Static Survival | Dynamic Survival |
|--------|---------------------|-----------------|------------------|
| Estimate type | Linear predictor | Any numeric | Survival probabilities |
| Range | Unbounded | Often bounded | Probabilities (0-1) |
| Typical source | Cox model | Various | Survival curves |
| Use case | Prognostic separation | Overall concordance | Time-specific |

## Statistical Background

### Royston's D Statistic

- Measures prognostic separation in survival models

- Related to standard deviation of prognostic index

- R²_D represents explained variation on log hazard scale

- D = β * κ where β is coefficient, κ is scaling constant

### Interpretation

```r
# R²_D values
# 0.0 = no prognostic separation
# 0.5 = moderate separation
# 1.0 = perfect separation (impossible in practice)
```

## Best Practices

1. **Use with Cox models**: These metrics are designed for Cox model output
2. **Apply transformations**: Use normal scores or other transformations as appropriate
3. **Validate inputs**: Use `check_linear_pred_survival_metric()`
4. **Handle case weights**: Convert to numeric with `vctrs::vec_cast()`
5. **Document statistical basis**: Explain the underlying statistical model
6. **Consider alternatives**: Compare with concordance for validation
7. **Check for ties**: Handle tied predictions appropriately

## Common Metrics

- **Royston's D**: Prognostic separation statistic

- **R²_D**: Explained variation based on D

- **Somers' D**: Rank correlation (can also use concordance)

## Dependencies

Linear predictor survival metrics typically depend on:

```r
# In DESCRIPTION
Imports:
    survival,
    vctrs,
    dplyr,
    tibble,
    stats

# In R/package.R
#' @importFrom survival Surv coxph
#' @importFrom stats coef qnorm
```

## See Also

- [Static Survival Metrics](static-survival-metrics.md) - Other overall survival metrics

- [Dynamic Survival Metrics](dynamic-survival-metrics.md) - Time-dependent metrics

- [Metric System](metric-system.md) - Understanding metric architecture
