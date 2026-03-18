---
name: add-yardstick-metric
description: Guide for creating new yardstick metrics. Use when a developer needs to extend yardstick with a custom performance metric, including numeric, class, probability, ordered probability, survival (static, dynamic, integrated, linear predictor), and quantile metrics.
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
- Optional autoplot support for visualization (curves and confusion matrices)

## Repository Access (Optional but Recommended)

For enhanced guidance with real implementation examples from the yardstick package, you can clone the source code repository locally.

**Benefits:**
- See actual metric implementations
- Reference real test patterns
- Search through source code
- Understand package architecture

**Quick Setup:**

Run from your R package directory:

```bash
# macOS/Linux/WSL
./path/to/skills-personal/tidymodels/skills/shared-scripts/clone-tidymodels-repos.sh yardstick

# Windows (PowerShell)
.\path\to\skills-personal\tidymodels\skills\shared-scripts\clone-tidymodels-repos.ps1 yardstick

# Any platform (Python)
python3 /path/to/skills-personal/tidymodels/skills/shared-scripts/clone-tidymodels-repos.py yardstick
```

**For complete instructions**, see: [Repository Access Setup](../shared-references/repository-access.md)

**Note:** Repository access is optional. This skill works with built-in references if you choose not to clone.

## Quick Navigation

**Reference Files:**
- [Metric System Architecture](references/metric-system.md) - How new_*_metric() works, .estimator column, design considerations
- [Combining Metrics](references/metric-set.md) - Using metric_set() to combine multiple metrics
- [Groupwise Metrics](references/groupwise-metrics.md) - Creating disparity/fairness metrics
- [Numeric Metrics](references/numeric-metrics.md) - Regression metrics (MAE, RMSE, MSE)
- [Class Metrics](references/class-metrics.md) - Classification metrics (accuracy, precision, recall)
- [Probability Metrics](references/probability-metrics.md) - Probability-based metrics (ROC AUC, log loss)
- [Ordered Probability Metrics](references/ordered-probability-metrics.md) - Ordinal classification metrics (Ranked Probability Score)
- [Static Survival Metrics](references/static-survival-metrics.md) - Overall survival metrics (Concordance Index)
- [Dynamic Survival Metrics](references/dynamic-survival-metrics.md) - Time-dependent survival metrics (Brier Survival)
- [Integrated Survival Metrics](references/integrated-survival-metrics.md) - Integrated survival metrics (Integrated Brier)
- [Linear Predictor Survival Metrics](references/linear-predictor-survival-metrics.md) - Linear predictor metrics (Royston's D)
- [Quantile Metrics](references/quantile-metrics.md) - Quantile prediction metrics (Weighted Interval Score)
- [Confusion Matrix](references/confusion-matrix.md) - Working with yardstick_table()
- [Case Weights](references/case-weights.md) - Handling weighted observations
- [Autoplot Support](references/autoplot.md) - Optional visualization (curves, confusion matrices)

**Shared References:**
- [R Package Setup](../shared-references/r-package-setup.md) - Package initialization and structure
- [Development Workflow](../shared-references/development-workflow.md) - Fast iteration cycle
- [Testing Patterns](../shared-references/testing-patterns.md) - Comprehensive test guide
- [Roxygen Documentation](../shared-references/roxygen-documentation.md) - Documentation templates
- [Package Imports](../shared-references/package-imports.md) - Managing dependencies
- [Best Practices](../shared-references/best-practices.md) - Code style and patterns
- [Troubleshooting](../shared-references/troubleshooting.md) - Common issues and solutions

## Prerequisites

See [R Package Setup](../shared-references/r-package-setup.md) for complete details.

**Quick setup:**

```r
# Check if this is a new package or existing package
if (!file.exists("DESCRIPTION")) {
  # New package - create full structure
  usethis::create_package(".", open = FALSE)
  usethis::use_mit_license()
  usethis::use_package("yardstick")
  usethis::use_package("rlang")
  usethis::use_package("cli")
  usethis::use_testthat()
} else {
  # Existing package - ensure dependencies
  usethis::use_package("yardstick")
  usethis::use_package("rlang")
  usethis::use_package("cli")
  if (!dir.exists("tests/testthat")) {
    usethis::use_testthat()
  }
}
```

## Development Workflow

See [Development Workflow](../shared-references/development-workflow.md) for complete details.

**Fast iteration cycle (run repeatedly):**

1. `devtools::document()` - Generate documentation
2. `devtools::load_all()` - Load your package
3. `devtools::test()` - Run tests

**Final validation (run once at end):**

4. `devtools::check()` - Full R CMD check

**WARNING:** Do NOT run `check()` during iteration. It takes 1-2 minutes and is unnecessary until you're done.

## Choosing Your Metric Type

```
┌─────────────────────────────────────────────────────────────┐
│ What type of data do you have?                              │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┬───────────────────┐
        │                   │                   │                   │
        ▼                   ▼                   ▼                   ▼
   Regression        Classification    Survival Analysis    Quantile Forecasting
        │                   │                   │                   │
        ▼                   ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   NUMERIC   │     │ CLASS-BASED │     │  SURVIVAL   │     │  QUANTILE   │
│   METRICS   │     │   METRICS   │     │   METRICS   │     │   METRICS   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
        │                   │                   │                   │
        │                   ├───────────────────┤                   │
        │                   │                   │                   │
        │                   ▼                   ▼                   │
        │            ┌─────────────┐     ┌─────────────┐           │
        │            │   Classes   │     │Probabilities│           │
        │            └─────────────┘     └─────────────┘           │
        │                   │                   │                   │
        │                   ├───────────────────┤                   │
        │                   │                   │                   │
        │                   ▼                   ▼                   │
        │            ┌─────────────┐     ┌─────────────┐           │
        │            │Unordered?   │     │Unordered?   │           │
        │            │  CLASS      │     │ PROBABILITY │           │
        │            └─────────────┘     └─────────────┘           │
        │                   │                   │                   │
        │                   ▼                   ▼                   │
        │            ┌─────────────┐     ┌─────────────┐           │
        │            │Ordered?     │     │Ordered?     │           │
        │            │ORDERED PROB │     │ORDERED PROB │           │
        │            └─────────────┘     └─────────────┘           │
        │                                                            │
        │            ┌───────────────────┬───────────────┬─────────┤
        │            │                   │               │         │
        ▼            ▼                   ▼               ▼         ▼
  Examples:     Examples:          Examples:      Examples:  Examples:
  - MAE         - Accuracy         - ROC AUC      - Concordance - WIS
  - RMSE        - Precision        - Log Loss     - Brier       - Pinball
  - R²          - F1 Score         - PR AUC       - Royston's D - Coverage
                - Ranked Prob Score

  Survival Metrics Breakdown:
  - STATIC: Single overall value (e.g., Concordance)
  - DYNAMIC: Value per time point (e.g., Time-dependent Brier)
  - INTEGRATED: Averaged across time (e.g., Integrated Brier)
  - LINEAR PRED: From Cox models (e.g., Royston's D)
```

**Decision guide:**
- **Numeric metric**: Truth and predictions are continuous numbers → [Numeric Metrics](references/numeric-metrics.md)
- **Class metric**: Truth and predictions are unordered factor classes → [Class Metrics](references/class-metrics.md)
- **Probability metric**: Truth is unordered factor, predictions are probabilities → [Probability Metrics](references/probability-metrics.md)
- **Ordered probability metric**: Truth is ordered factor, predictions are probabilities → [Ordered Probability Metrics](references/ordered-probability-metrics.md)
- **Static survival metric**: Truth is Surv object, single numeric prediction → [Static Survival Metrics](references/static-survival-metrics.md)
- **Dynamic survival metric**: Truth is Surv object, time-dependent predictions → [Dynamic Survival Metrics](references/dynamic-survival-metrics.md)
- **Integrated survival metric**: Truth is Surv object, integrated across time → [Integrated Survival Metrics](references/integrated-survival-metrics.md)
- **Linear predictor survival metric**: Truth is Surv object, linear predictor from Cox model → [Linear Predictor Survival Metrics](references/linear-predictor-survival-metrics.md)
- **Quantile metric**: Truth is numeric, predictions are quantiles → [Quantile Metrics](references/quantile-metrics.md)

## Complete Example: Numeric Metric (MAE)

This example shows all required components for a numeric metric.

**Reference implementation:** `R/num-mae.R` in yardstick repository

### 1. Implementation function

```r
# R/mae.R

mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  if (is.null(case_weights)) {
    mean(errors)
  } else {
    # Handle hardhat weights
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

### 2. Vector interface

```r
#' @export
mae_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Validate na_rm parameter
  if (!is.logical(na_rm) || length(na_rm) != 1) {
    cli::cli_abort("{.arg na_rm} must be a single logical value.")
  }

  # Validate inputs
  yardstick::check_numeric_metric(truth, estimate, case_weights)

  # Handle missing values
  if (na_rm) {
    result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  # Call implementation
  mae_impl(truth, estimate, case_weights)
}
```

### 3. Data frame method

```r
#' Mean Absolute Error
#'
#' Calculate the mean absolute error between truth and estimate.
#'
#' @family numeric metrics
#' @family accuracy metrics
#' @templateVar fn mae
#' @template return
#' @template event_first
#'
#' @inheritParams rmse
#'
#' @author Your Name
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
```

### 4. Tests

```r
# tests/testthat/test-mae.R

test_that("mae works correctly", {
  df <- data.frame(
    truth = c(1, 2, 3, 4, 5),
    estimate = c(1.5, 2.5, 2.5, 3.5, 4.5)
  )

  result <- mae(df, truth, estimate)

  # Expected: mean(abs(c(0.5, 0.5, 0.5, 0.5, 0.5))) = 0.5
  expect_equal(result$.estimate, 0.5)
  expect_equal(result$.metric, "mae")
  expect_equal(result$.estimator, "standard")
})

test_that("mae handles NA correctly", {
  df <- data.frame(
    truth = c(1, 2, NA, 4, 5),
    estimate = c(1.5, 2.5, 2.5, 3.5, 4.5)
  )

  # With na_rm = TRUE (default)
  result_remove <- mae(df, truth, estimate, na_rm = TRUE)
  expect_false(is.na(result_remove$.estimate))

  # With na_rm = FALSE
  result_keep <- mae(df, truth, estimate, na_rm = FALSE)
  expect_true(is.na(result_keep$.estimate))
})

test_that("mae validates inputs", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c("a", "b", "c")  # Wrong type
  )

  expect_error(mae(df, truth, estimate))
})

test_that("mae works with case weights", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.5, 2.5, 3.5),
    weights = c(1, 2, 1)
  )

  # Calculate expected weighted value
  # errors = abs(c(0.5, 0.5, 0.5))
  # weighted mean = (1*0.5 + 2*0.5 + 1*0.5) / (1+2+1) = 0.5

  result <- mae(df, truth, estimate, case_weights = weights)
  expect_equal(result$.estimate, 0.5)
})
```

**Reference test pattern:** `tests/testthat/test-num-mae.R` in yardstick repository

See [Testing Patterns](../shared-references/testing-patterns.md) for comprehensive testing guide.

## Implementation Guide by Metric Type

### Numeric Metrics

**Use for:** Regression metrics where truth and predictions are continuous numbers.

**Pattern:** Three-function approach (_impl, _vec, data.frame method)

**Complete guide:** [Numeric Metrics](references/numeric-metrics.md)

**Key points:**
- Always use `check_numeric_metric()` for validation
- Handle case weights with `weighted.mean()`
- Use `yardstick_remove_missing()` for NA handling
- Return `.estimator = "standard"`

**Examples:** MAE, RMSE, MSE, Huber Loss, R-squared

**Reference implementations:**
- Simple metrics: `R/num-mae.R`, `R/num-rmse.R`, `R/num-mse.R`
- Parameterized metrics: `R/num-huber_loss.R` (has delta parameter)
- Complex metrics: `R/num-ccc.R` (correlation-based)

### Class Metrics

**Use for:** Classification metrics where truth and predictions are factor classes.

**Pattern:** Uses confusion matrix from `yardstick_table()`

**Complete guide:** [Class Metrics](references/class-metrics.md)

**Key points:**
- Use `yardstick_table()` to create weighted confusion matrix
- Implement separate `_binary` and `_estimator_impl` functions
- Handle factor level ordering with `event_level` parameter
- Support multiclass with macro, micro, macro_weighted averaging

**Examples:** Accuracy, Precision, Recall, F1, Specificity

**Reference implementations:**
- Simple metrics: `R/class-accuracy.R`, `R/class-precision.R`, `R/class-recall.R`
- Combined metrics: `R/class-f_meas.R` (F1 score)
- Balanced metrics: `R/class-bal_accuracy.R` (handles class imbalance)

### Probability Metrics

**Use for:** Metrics that evaluate predicted probabilities against true classes.

**Pattern:** Similar to class metrics but uses probability columns

**Complete guide:** [Probability Metrics](references/probability-metrics.md)

**Key points:**
- Truth is factor, estimate is probabilities
- Convert factor to binary for binary metrics
- Handle multiple probability columns for multiclass
- Use `check_prob_metric()` for validation

**Examples:** ROC AUC, Log Loss, Brier Score, PR AUC

**Reference implementations:**
- Curve-based: `R/prob-roc_auc.R`, `R/prob-pr_auc.R`
- Scoring rules: `R/prob-brier_class.R`, `R/prob-mn_log_loss.R`

### Ordered Probability Metrics

**Use for:** Ordinal classification metrics where class ordering matters.

**Pattern:** Three-function approach with cumulative probabilities

**Complete guide:** [Ordered Probability Metrics](references/ordered-probability-metrics.md)

**Key points:**
- Truth must be ordered factor
- Uses cumulative probabilities to respect ordering
- Use `check_ordered_prob_metric()` for validation
- No averaging types (works same for any number of classes)

**Examples:** Ranked Probability Score (RPS)

### Static Survival Metrics

**Use for:** Overall survival metrics with single numeric predictions.

**Pattern:** Three-function approach with Surv objects

**Complete guide:** [Static Survival Metrics](references/static-survival-metrics.md)

**Key points:**
- Truth is Surv object from survival package
- Estimate is single numeric per observation
- Handles right-censoring with comparable pairs
- Use `check_static_survival_metric()` for validation

**Examples:** Concordance Index (C-index)

### Dynamic Survival Metrics

**Use for:** Time-dependent survival metrics at specific evaluation times.

**Pattern:** Three-function approach with list-column predictions

**Complete guide:** [Dynamic Survival Metrics](references/dynamic-survival-metrics.md)

**Key points:**
- Truth is Surv object
- Estimate is list-column of data.frames with `.eval_time`, `.pred_survival`, `.weight_censored`
- Returns multiple rows (one per eval_time)
- Uses inverse probability of censoring weights (IPCW)

**Examples:** Time-dependent Brier Score, Time-dependent ROC AUC

### Integrated Survival Metrics

**Use for:** Overall survival metrics integrated across evaluation times.

**Pattern:** Two-function approach (calls dynamic metric, then integrates)

**Complete guide:** [Integrated Survival Metrics](references/integrated-survival-metrics.md)

**Key points:**
- Same input format as dynamic survival metrics
- Integrates across time using trapezoidal rule
- Normalizes by max evaluation time
- Requires at least 2 evaluation times

**Examples:** Integrated Brier Score, Integrated ROC AUC

### Linear Predictor Survival Metrics

**Use for:** Metrics for linear predictors from Cox models.

**Pattern:** Three-function approach with transformations

**Complete guide:** [Linear Predictor Survival Metrics](references/linear-predictor-survival-metrics.md)

**Key points:**
- Truth is Surv object
- Estimate is linear predictor values (unbounded)
- Often uses transformations (e.g., normal scores)
- Use `check_linear_pred_survival_metric()` for validation

**Examples:** Royston's D statistic, R²_D

### Quantile Metrics

**Use for:** Quantile prediction metrics for uncertainty quantification.

**Pattern:** Three-function approach with quantile_pred objects

**Complete guide:** [Quantile Metrics](references/quantile-metrics.md)

**Key points:**
- Truth is numeric
- Estimate is `hardhat::quantile_pred` object
- Handles missing quantiles (impute, drop, or propagate)
- Uses `fn_options` for additional parameters

**Examples:** Weighted Interval Score (WIS), Pinball Loss

## Documentation

See [Roxygen Documentation](../shared-references/roxygen-documentation.md) for complete templates.

**Required roxygen tags:**
```r
#' @family [metric category] metrics
#' @export
#' @inheritParams [similar_metric]
#' @param data A data frame
#' @param truth Unquoted column with true values
#' @param estimate Unquoted column with predictions
#' @param na_rm Remove missing values (default TRUE)
#' @param case_weights Optional case weights column
#' @return A tibble with .metric, .estimator, .estimate columns
```

## Testing

See [Testing Patterns](../shared-references/testing-patterns.md) for comprehensive guide.

**Required test categories:**
1. **Correctness**: Metric calculates correctly
2. **NA handling**: Both `na_rm = TRUE` and `FALSE`
3. **Input validation**: Wrong types, mismatched lengths
4. **Case weights**: Weighted and unweighted differ
5. **Edge cases**: All correct, all wrong, empty data

## Common Patterns

### Using the confusion matrix

See [Confusion Matrix](references/confusion-matrix.md) for complete guide.

```r
# Get confusion matrix
xtab <- yardstick::yardstick_table(truth, estimate, case_weights)

# Extract values (for binary classification)
tp <- xtab[2, 2]  # True positives: truth = second, pred = second
tn <- xtab[1, 1]  # True negatives: truth = first, pred = first
fp <- xtab[1, 2]  # False positives: truth = first, pred = second
fn <- xtab[2, 1]  # False negatives: truth = second, pred = first
```

### Handling case weights

See [Case Weights](references/case-weights.md) for complete guide.

```r
# Check and convert hardhat weights
if (!is.null(case_weights)) {
  if (inherits(case_weights, c("hardhat_importance_weights",
                               "hardhat_frequency_weights"))) {
    case_weights <- as.double(case_weights)
  }
}

# Use in calculations
if (is.null(case_weights)) {
  mean(values)
} else {
  weighted.mean(values, w = case_weights)
}
```

### Multiclass averaging

See [Class Metrics](references/class-metrics.md) for complete guide.

**Macro averaging:** Average of per-class metrics (treats all classes equally)
**Micro averaging:** Pool all observations, calculate once (treats all observations equally)
**Macro-weighted averaging:** Weighted average by class prevalence

## Advanced Topics

### Combining Metrics with metric_set()

Once you've created your metric, you can combine it with other metrics using `metric_set()`:

```r
my_metrics <- metric_set(mae, rmse, my_custom_metric)
my_metrics(data, truth = y, estimate = y_pred)
```

**Key benefits:**
- Calculate multiple metrics at once
- More efficient (shared calculations)
- Integrates with tune package
- Works with grouped data

See [Combining Metrics](references/metric-set.md) for complete guide.

### Creating Groupwise Metrics

Groupwise metrics measure disparity in metric values across groups (useful for fairness):

```r
accuracy_diff <- new_groupwise_metric(
  fn = accuracy,
  name = "accuracy_diff",
  aggregate = function(x) diff(range(x$.estimate))
)

accuracy_diff_by_group <- accuracy_diff(group_column)
accuracy_diff_by_group(data, truth, estimate)
```

**Use cases:**
- Fairness analysis across demographic groups
- Performance consistency across segments
- Disparity quantification

See [Groupwise Metrics](references/groupwise-metrics.md) for complete guide.

## Package Integration

### Package-level documentation

See [Package Imports](../shared-references/package-imports.md) for complete guide.

Create `R/{packagename}-package.R`:

```r
#' @keywords internal
"_PACKAGE"

#' @importFrom rlang .data := !! enquo enquos
#' @importFrom yardstick new_numeric_metric new_class_metric new_prob_metric
NULL
```

### Exports

All metrics must be exported:
```r
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}
```

## Best Practices

See [Best Practices](../shared-references/best-practices.md) for complete guide.

**Key principles:**
- Use base pipe `|>` not magrittr pipe `%>%`
- Prefer for-loops over `purrr::map()` for better error messages
- Use `cli::cli_abort()` for error messages
- Keep functions focused on single responsibility
- Validate early (in `_vec`), trust data in `_impl`

## Troubleshooting

See [Troubleshooting](../shared-references/troubleshooting.md) for complete guide.

**Common issues:**
- "No visible global function definition" → Add to package imports
- "Object not found" in tests → Use `devtools::load_all()` before testing
- NA handling bugs → Check both `na_rm = TRUE` and `FALSE` cases
- Case weights not working → Convert hardhat weights to numeric

## Next Steps

1. **Understand the system:** Read [Metric System](references/metric-system.md)
2. **Choose metric type:**
   - Regression: [Numeric](references/numeric-metrics.md)
   - Classification: [Class](references/class-metrics.md), [Probability](references/probability-metrics.md), [Ordered Probability](references/ordered-probability-metrics.md)
   - Survival: [Static](references/static-survival-metrics.md), [Dynamic](references/dynamic-survival-metrics.md), [Integrated](references/integrated-survival-metrics.md), [Linear Predictor](references/linear-predictor-survival-metrics.md)
   - Quantile: [Quantile](references/quantile-metrics.md)
3. **Follow the template:** Use complete examples from reference files
4. **Test thoroughly:** See [Testing Patterns](../shared-references/testing-patterns.md)
5. **Document completely:** See [Roxygen Documentation](../shared-references/roxygen-documentation.md)
6. **Run final check:** `devtools::check()` before publishing
