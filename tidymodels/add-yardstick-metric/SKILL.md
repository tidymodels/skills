---
name: add-yardstick-metric
description: Guide for creating new yardstick metrics. Use when a developer needs to extend yardstick with a custom performance metric, including numeric, class, or probability metrics.
---

# Add Yardstick Metric

Guide for developing new metrics that extend the yardstick package. This skill provides best practices, code templates, and testing patterns for creating custom performance metrics.

## Overview

Creating a custom yardstick metric provides:
- Standardization with existing metrics
- Automatic error handling for types and lengths
- Support for multiclass implementations
- NA handling
- Grouped data frame support
- Integration with `metric_set()`

## Prerequisites

### Check project structure

If the current directory is not an R package, create a skeleton package first:

```r
usethis::create_package(".")
usethis::use_mit_license()
usethis::use_package("yardstick")
usethis::use_package("rlang")
```

## Metric types

Yardstick supports several metric types:
- **Numeric metrics**: For regression (e.g., MAE, RMSE, MSE)
- **Class metrics**: For classification (e.g., accuracy, precision, recall)
- **Probability metrics**: For class probabilities (e.g., ROC AUC, log loss)
- **Survival metrics**: For survival analysis
- **Quantile metrics**: For quantile predictions

## Creating a numeric metric

Numeric metrics are the simplest to implement. They measure continuous predictions against continuous truth values.

### Step 1: Define the implementation function

Create the core calculation function. Use the `_impl` suffix:

```r
# Example: Mean Squared Error
mse_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- (truth - estimate) ^ 2
  if (is.null(case_weights)) {
    mean(errors)
  } else {
    yardstick::yardstick_mean(errors, case_weights = case_weights)
  }
}
```

**Key patterns:**
- Take `truth`, `estimate`, and optionally `case_weights`
- Return a single numeric value
- Use `yardstick_mean()` for weighted calculations

### Step 2: Create the vector function

```r
mse_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  check_bool(na_rm)
  yardstick::check_numeric_metric(truth, estimate, case_weights)

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
- Use `check_numeric_metric()` for validation
- Handle NA values consistently using `yardstick_remove_missing()`
- Return `NA_real_` if `na_rm = FALSE` and NAs present

### Step 3: Create the data frame method

```r
mse <- function(data, ...) {
  UseMethod("mse")
}

mse <- yardstick::new_numeric_metric(
  mse,
  direction = "minimize",  # or "maximize" or "zero"
  range = c(0, Inf)
)

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

## Creating a class metric

Class metrics are more complex due to multiclass support.

### Step 1: Binary implementation

```r
# Example: Miss Rate (False Negative Rate)
miss_rate_binary <- function(data, event_level) {
  # data is a confusion matrix (table)
  col <- if (identical(event_level, "first")) {
    colnames(data)[[1]]
  } else {
    colnames(data)[[2]]
  }
  col2 <- setdiff(colnames(data), col)

  tp <- data[col, col]
  fn <- data[col2, col]

  fn / (fn + tp)
}
```

### Step 2: Multiclass implementation (optional)

```r
miss_rate_multiclass <- function(data, estimator) {
  # Calculate per-class values
  tp <- diag(data)
  tpfn <- colSums(data)
  fn <- tpfn - tp

  # For micro averaging, sum first
  if (estimator == "micro") {
    tp <- sum(tp)
    fn <- sum(fn)
  }

  # Return vector of per-class values (or single value for micro)
  fn / (fn + tp)
}
```

### Step 3: Estimator implementation

```r
miss_rate_estimator_impl <- function(data, estimator, event_level) {
  if (estimator == "binary") {
    miss_rate_binary(data, event_level)
  } else {
    # Get weights based on estimator type (macro, macro_weighted, micro)
    wt <- yardstick:::get_weights(data, estimator)
    res <- miss_rate_multiclass(data, estimator)
    weighted.mean(res, wt)
  }
}

miss_rate_impl <- function(truth, estimate, estimator, event_level, case_weights) {
  xtab <- yardstick::yardstick_table(truth, estimate, case_weights = case_weights)
  miss_rate_estimator_impl(xtab, estimator, event_level)
}
```

### Step 4: Vector function

```r
miss_rate_vec <- function(truth, estimate, estimator = NULL, na_rm = TRUE,
                          case_weights = NULL, event_level = "first", ...) {
  check_bool(na_rm)
  yardstick::abort_if_class_pred(truth)
  estimate <- yardstick::as_factor_from_class_pred(estimate)

  estimator <- yardstick::finalize_estimator(
    truth,
    estimator,
    metric_class = "miss_rate"
  )

  yardstick::check_class_metric(truth, estimate, case_weights, estimator)

  if (na_rm) {
    result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  miss_rate_impl(truth, estimate, estimator, event_level, case_weights)
}
```

### Step 5: Data frame method

```r
miss_rate <- function(data, ...) {
  UseMethod("miss_rate")
}

miss_rate <- yardstick::new_class_metric(
  miss_rate,
  direction = "minimize",
  range = c(0, 1)
)

miss_rate.data.frame <- function(data, truth, estimate, estimator = NULL,
                                 na_rm = TRUE, case_weights = NULL,
                                 event_level = "first", ...) {
  yardstick::class_metric_summarizer(
    name = "miss_rate",
    fn = miss_rate_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    estimator = estimator,
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights),
    event_level = event_level
  )
}
```

### Step 6: Restrict estimator (optional)

If your metric only supports binary classification:

```r
finalize_estimator_internal.miss_rate <- function(metric_dispatcher, x,
                                                   estimator, call) {
  yardstick::validate_estimator(estimator, estimator_override = "binary")

  if (!is.null(estimator)) {
    return(estimator)
  }

  lvls <- levels(x)
  if (length(lvls) > 2) {
    cli::cli_abort(
      "A multiclass {.arg truth} input was provided, but only {.code binary} is supported."
    )
  }

  "binary"
}
```

## Documentation

### Roxygen template

```r
#' Metric name
#'
#' Brief description of what the metric measures.
#'
#' @family [metric-family] metrics
#' @seealso [All [metric-family] metrics][metric-family-metrics]
#' @templateVar fn metric_name
#' @template return
#'
#' @section Multiclass:
#'
#' Explanation of multiclass behavior (if applicable).
#'
#' @inheritParams [similar_metric]
#'
#' @param additional_param Description of any additional parameters.
#'
#' @details
#' [Metric name] is a metric that should be `r attr(metric_name, "direction")`d.
#' The output ranges from `r metric_range(metric_name)[1]` to
#' `r metric_range(metric_name)[2]`, with `r metric_optimal(metric_name)`
#' indicating perfect predictions.
#'
#' The formula for [metric name] is:
#'
#' \deqn{formula here}
#'
#' @author Your Name
#'
#' @examples
#' library(dplyr)
#' data("two_class_example")
#'
#' # Two class
#' metric_name(two_class_example, truth, predicted)
#'
#' @export
```

### Common roxygen patterns

- Use `@family` to group related metrics
- Use `@templateVar fn` and `@template return` for standard return docs
- Use `@inheritParams` to inherit parameter docs from similar metrics
- Include formula in `@details` using `\deqn{}`
- Use inline R with backticks for dynamic values
- Include practical examples

## Testing

### Test file structure

Tests go in `tests/testthat/test-[metric-type]-[metric-name].R`:

```r
test_that("Calculations are correct - two class", {
  # Use existing test data
  lst <- data_altman()
  pathology <- lst$pathology

  expect_equal(
    metric_name_vec(pathology$pathology, pathology$scan),
    expected_value  # Calculate by hand or use reference
  )
})

test_that("Calculations are correct - multiclass", {
  lst <- data_three_class()
  three_class <- lst$three_class

  expect_equal(
    metric_name_vec(three_class$obs, three_class$pred),
    expected_value
  )
})

test_that("Case weights calculations are correct", {
  df <- data.frame(
    truth = factor(c("x", "x", "y"), levels = c("x", "y")),
    estimate = factor(c("x", "y", "x"), levels = c("x", "y")),
    case_weights = c(1L, 1L, 2L)
  )

  expect_identical(
    metric_name(df, truth, estimate, case_weights = case_weights)[[".estimate"]],
    expected_weighted_value
  )
})

test_that("works with hardhat case weights", {
  lst <- data_altman()
  df <- lst$pathology
  imp_wgt <- hardhat::importance_weights(seq_len(nrow(df)))
  freq_wgt <- hardhat::frequency_weights(seq_len(nrow(df)))

  expect_no_error(
    metric_name_vec(df$pathology, df$scan, case_weights = imp_wgt)
  )

  expect_no_error(
    metric_name_vec(df$pathology, df$scan, case_weights = freq_wgt)
  )
})

test_that("na_rm argument works", {
  expect_snapshot(
    error = TRUE,
    metric_name_vec(1, 1, na_rm = "yes")
  )
})

test_that("range values are correct", {
  direction <- metric_direction(metric_name)
  range <- metric_range(metric_name)
  perfect <- ifelse(direction == "minimize", range[1], range[2])
  worst <- ifelse(direction == "minimize", range[2], range[1])

  df <- tibble::tibble(
    truth = c(1, 2, 3, 4, 5),
    perfect = c(1, 2, 3, 4, 5),
    off = c(2, 3, 4, 5, 6)
  )

  expect_equal(
    metric_name_vec(df$truth, df$perfect),
    perfect
  )

  if (direction == "minimize") {
    expect_gt(metric_name_vec(df$truth, df$off), perfect)
    expect_lte(metric_name_vec(df$truth, df$off), worst)
  }
  if (direction == "maximize") {
    expect_lt(metric_name_vec(df$truth, df$off), perfect)
    expect_gte(metric_name_vec(df$truth, df$off), worst)
  }
})
```

### Run tests

```bash
# Test specific file
Rscript -e "devtools::test_active_file('R/metric-name.R')"

# Run all tests
Rscript -e "devtools::test()"
```

## File naming conventions

- **Source files**: `R/[type]-[name].R`
  - Examples: `R/num-mae.R`, `R/class-accuracy.R`, `R/prob-roc_auc.R`
- **Test files**: `tests/testthat/test-[type]-[name].R`
  - Examples: `test-num-mae.R`, `test-class-accuracy.R`
- Use prefixes: `num-`, `class-`, `prob-`, `surv-`, etc.

## Key yardstick helpers

| Function | Purpose |
|----------|---------|
| `check_numeric_metric()` | Validate numeric metric inputs |
| `check_class_metric()` | Validate class metric inputs |
| `check_prob_metric()` | Validate probability metric inputs |
| `yardstick_remove_missing()` | Remove NA values consistently |
| `yardstick_any_missing()` | Check for NA values |
| `yardstick_mean()` | Weighted mean |
| `yardstick_table()` | Create confusion matrix with case weights |
| `finalize_estimator()` | Auto-select estimator type |
| `validate_estimator()` | Validate estimator input |
| `abort_if_class_pred()` | Reject class_pred for truth |
| `as_factor_from_class_pred()` | Convert class_pred estimate to factor |

## Best practices

### Code style
- Use base pipe `|>` not `%>%`
- Use `\() ...` for single-line anonymous functions
- Use `function() {...}` for multi-line functions
- Run `air format .` after writing code
- Keep tests minimal with few comments

### Documentation
- Wrap roxygen at 80 characters
- Use US English and sentence case
- Reference formulas and academic sources
- Include practical examples

### Performance
- Separate multiclass logic for reusability
- Apply weighting once at the end
- Use vectorized operations
- Cache confusion matrices

### Error messages
- Use `cli::cli_abort()` for errors
- Use `cli::cli_warn()` for warnings
- Include argument names in braces: `{.arg truth}`
- Include code in braces: `{.code binary}`

## Common patterns

### Confusion matrix metrics

Use `yardstick_table()` to create weighted confusion matrices:

```r
xtab <- yardstick_table(truth, estimate, case_weights = case_weights)
```

Access elements:
- True positives: `xtab[event, event]`
- False positives: `xtab[event, control]`
- False negatives: `xtab[control, event]`
- True negatives: `xtab[control, control]`

### Multiclass averaging

Three types:
- **macro**: Unweighted average across classes
- **macro_weighted**: Weighted by class frequency in truth
- **micro**: Pool all classes, calculate once

Get weights: `wt <- get_weights(xtab, estimator)`

### Case weights

Always include `case_weights = NULL` parameter. Use:
- `yardstick_mean(values, case_weights)`
- `yardstick_table(truth, estimate, case_weights)`

## Checklist

Before submitting:

- [ ] Created implementation function `[name]_impl()`
- [ ] Created vector function `[name]_vec()`
- [ ] Created data frame method `[name].data.frame()`
- [ ] Used appropriate `new_*_metric()` constructor
- [ ] Set correct `direction` and `range`
- [ ] Added roxygen documentation with examples
- [ ] Added tests for binary/multiclass cases
- [ ] Added tests for NA handling
- [ ] Added tests for case weights
- [ ] Added tests for range validation
- [ ] Ran `air format .`
- [ ] Ran `devtools::test()`
- [ ] Ran `devtools::document()`
- [ ] Tested with `metric_set()`

## References

- [Custom performance metrics tutorial](https://www.tidymodels.org/learn/develop/metrics/)
- [Yardstick reference](https://yardstick.tidymodels.org/reference/)
- [Multiclass metrics vignette](https://yardstick.tidymodels.org/articles/multiclass.html)
- Source examples: `yardstick/R/class-accuracy.R`, `yardstick/R/num-mae.R`
