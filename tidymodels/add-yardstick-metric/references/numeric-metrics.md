# Creating Numeric Metrics

Numeric metrics are the simplest to implement. They measure continuous predictions against continuous truth values.

## Overview

Numeric metrics are used for regression problems where both truth and predictions are continuous values. Examples include:
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- Mean Absolute Error (MAE)
- R-squared

**Canonical implementations in yardstick:**
- Simple error metrics: `R/num-mae.R`, `R/num-rmse.R`, `R/num-mse.R`
- Percentage error metrics: `R/num-mape.R` (Mean Absolute Percentage Error)
- Robust metrics: `R/num-huber_loss.R` (has tuning parameter for outliers)
- Correlation-based: `R/num-ccc.R` (Concordance Correlation Coefficient)

**Test patterns:**
- Basic testing: `tests/testthat/test-num-mae.R`
- Parameterized metrics: `tests/testthat/test-num-huber_loss.R`

## Step 1: Define the implementation function

Create the core calculation function. Use the `_impl` suffix.

**Reference implementations:**
- Simple calculation: `R/num-mae.R` (mean absolute error)
- Squared errors: `R/num-mse.R`, `R/num-rmse.R`
- With parameters: `R/num-huber_loss.R` (has delta parameter for robust loss)

```r
# Example: Mean Squared Error
mse_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- (truth - estimate) ^ 2

  if (is.null(case_weights)) {
    mean(errors)
  } else {
    # Handle hardhat weights
    wts <- if (inherits(case_weights, "hardhat_importance_weights") ||
               inherits(case_weights, "hardhat_frequency_weights")) {
      as.double(case_weights)
    } else {
      case_weights
    }
    weighted.mean(errors, w = wts)
  }
}
```

**Key patterns:**
- Take `truth`, `estimate`, and optionally `case_weights`
- Return a single numeric value
- Use `weighted.mean()` for weighted calculations
- Handle hardhat weight classes by converting to numeric

> **Source Development:** When contributing to yardstick itself, you can use `yardstick_mean()` instead of manually handling case weights. This internal helper automatically handles hardhat weights and unweighted cases. See [Best Practices (Source)](best-practices-source.md).

## Step 2: Create the vector function

```r
mse_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Validate na_rm
  if (!is.logical(na_rm) || length(na_rm) != 1) {
    cli::cli_abort("{.arg na_rm} must be a single logical value.")
  }

  # Validate inputs
  yardstick::check_numeric_metric(truth, estimate, case_weights)

  # Handle NA values
  if (na_rm) {
    result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  mse_impl(truth, estimate, case_weights)
}
```

**Required elements:**
- Validate `na_rm` parameter explicitly
- Use `check_numeric_metric()` for validation
- Handle NA values consistently using `yardstick_remove_missing()`
- Return `NA_real_` if `na_rm = FALSE` and NAs present

## Step 3: Create the data frame method

```r
mse <- function(data, ...) {
  UseMethod("mse")
}

mse <- yardstick::new_numeric_metric(
  mse,
  direction = "minimize",  # or "maximize" or "zero"
  range = c(0, Inf)
)

#' @export
#' @rdname mse
mse.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                           case_weights = NULL, ...) {
  yardstick::numeric_metric_summarizer(
    name = "mse",
    fn = mse_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights)
  )
}
```

**Key patterns:**
- Use `new_numeric_metric()` to create the metric function
- Set `direction` to "minimize", "maximize", or "zero"
- Specify `range` as `c(min, max)` (use `Inf` or `-Inf` for unbounded)
- Use `rlang::enquo()` and `!!` for NSE support
- Export the data frame method with `@export`

### Direction values

**"minimize"**: Lower is better (MSE, RMSE, MAE)
```r
direction = "minimize"
range = c(0, Inf)
```

**"maximize"**: Higher is better (R-squared, correlation)
```r
direction = "maximize"
range = c(-Inf, 1)  # or c(0, 1) depending on metric
```

**"zero"**: Zero is optimal (bias, some error metrics)
```r
direction = "zero"
range = c(-Inf, Inf)
```

## Step 4: Handling Custom Parameters (Optional)

If your metric needs custom parameters beyond the standard ones (na_rm, case_weights), use the `fn_options` parameter in `numeric_metric_summarizer()`.

### Example with threshold parameter

```r
#' @param threshold Threshold value for the metric. Default is 0.1.
threshold_accuracy.data.frame <- function(data, truth, estimate, threshold = 0.1,
                                          na_rm = TRUE, case_weights = NULL, ...) {
  yardstick::numeric_metric_summarizer(
    name = "threshold_accuracy",
    fn = threshold_accuracy_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights),
    fn_options = list(threshold = threshold)  # Pass custom parameter here
  )
}
```

### Validate custom parameters in your _vec function

```r
threshold_accuracy_vec <- function(truth, estimate, threshold = 0.1, na_rm = TRUE,
                                   case_weights = NULL, ...) {
  # Validate threshold
  if (!is.numeric(threshold) || length(threshold) != 1 || threshold < 0) {
    cli::cli_abort("{.arg threshold} must be a single non-negative numeric value.")
  }

  # Validate na_rm
  if (!is.logical(na_rm) || length(na_rm) != 1) {
    cli::cli_abort("{.arg na_rm} must be a single logical value.")
  }

  # Validate inputs
  yardstick::check_numeric_metric(truth, estimate, case_weights)

  # Handle NAs
  if (na_rm) {
    result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  # Your calculation using threshold
  threshold_accuracy_impl(truth, estimate, threshold, case_weights)
}
```

### Common validation patterns

**Numeric range:**
```r
if (threshold < 0 || threshold > 1) {
  cli::cli_abort("{.arg threshold} must be between 0 and 1.")
}
```

**Single value:**
```r
if (length(param) != 1) {
  cli::cli_abort("{.arg param} must be a single value.")
}
```

**Character options:**
```r
param <- rlang::arg_match(param, c("option1", "option2"))
```

## Complete Example

Here's a complete implementation of a simple metric. This follows the same pattern as `R/num-mae.R` in the yardstick repository.

```r
# File: R/num-mae.R

#' Mean Absolute Error
#'
#' Calculate the mean absolute error between truth and estimate.
#'
#' @family numeric metrics
#' @param data A data frame containing truth and estimate columns.
#' @param truth Column identifier for true values (numeric).
#' @param estimate Column identifier for predicted values (numeric).
#' @param na_rm Logical indicating whether to remove NA values. Default TRUE.
#' @param case_weights Optional column identifier for case weights.
#' @param ... Not currently used.
#'
#' @return A tibble with columns `.metric`, `.estimator`, and `.estimate`.
#'
#' @details
#' MAE should be minimized. The output ranges from 0 to Inf, with 0 indicating
#' perfect predictions.
#'
#' @examples
#' df <- data.frame(
#'   truth = c(1, 2, 3, 4, 5),
#'   estimate = c(1.1, 2.2, 2.9, 4.1, 5.2)
#' )
#'
#' mae(df, truth, estimate)
#'
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}

mae <- yardstick::new_numeric_metric(
  mae,
  direction = "minimize",
  range = c(0, Inf)
)

#' @export
#' @rdname mae
mae.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                           case_weights = NULL, ...) {
  yardstick::numeric_metric_summarizer(
    name = "mae",
    fn = mae_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights)
  )
}

#' @export
#' @rdname mae
mae_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Validate na_rm
  if (!is.logical(na_rm) || length(na_rm) != 1) {
    cli::cli_abort("{.arg na_rm} must be a single logical value.")
  }

  # Validate inputs
  yardstick::check_numeric_metric(truth, estimate, case_weights)

  # Handle NA values
  if (na_rm) {
    result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  mae_impl(truth, estimate, case_weights)
}

mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  if (is.null(case_weights)) {
    mean(errors)
  } else {
    # Handle hardhat weights
    wts <- if (inherits(case_weights, "hardhat_importance_weights") ||
               inherits(case_weights, "hardhat_frequency_weights")) {
      as.double(case_weights)
    } else {
      case_weights
    }
    weighted.mean(errors, w = wts)
  }
}
```

## Testing Numeric Metrics

See [package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements) for comprehensive testing guide.

**Reference test files:**
- Standard tests: `tests/testthat/test-num-mae.R` (correctness, NA handling, weights)
- Edge cases: `tests/testthat/test-num-huber_loss.R` (parameter validation, robustness)

### Key tests for numeric metrics

```r
test_that("calculations are correct", {
  df <- data.frame(
    truth = c(1, 2, 3, 4, 5),
    estimate = c(1.1, 2.2, 2.9, 4.1, 4.8)
  )

  # Calculate expected value by hand
  expected <- mean(abs(df$truth - df$estimate))

  expect_equal(mae_vec(df$truth, df$estimate), expected)
})

test_that("perfect predictions give zero", {
  truth <- c(10, 20, 30, 40, 50)
  estimate <- c(10, 20, 30, 40, 50)

  expect_equal(mae_vec(truth, estimate), 0)
})

test_that("case weights work correctly", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.5, 2.5, 3.5),
    weights = c(1, 2, 1)
  )

  # Weighted calculation
  expected <- weighted.mean(abs(df$truth - df$estimate), df$weights)

  expect_equal(mae_vec(df$truth, df$estimate, case_weights = df$weights), expected)
})
```

## File Naming

- **Source file**: `R/num-mae.R` (or `R/num-your-metric.R`)
- **Test file**: `tests/testthat/test-num-mae.R`

Use `num-` prefix to indicate numeric metrics.

## Next Steps

- Document your metric: [package-roxygen-documentation.md](package-roxygen-documentation.md)
- Write tests: [package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements)
- Understand metric system: [metric-system.md](metric-system.md)
- Add visualization (optional): [autoplot.md](autoplot.md)
