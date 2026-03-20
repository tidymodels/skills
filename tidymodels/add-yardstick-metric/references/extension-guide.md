# Extension Development Guide: Yardstick Metrics

Complete guide for creating new packages that extend yardstick with custom metrics.

---


## PREREQUISITES

**CLAUDE: THIS R PACKAGE SETUP IS CUSTOM. IT NEEDS TO BE FOLLOWED TO THE LETTER**

👉 **[FOLLOW THE STEPS IN: Extension Prerequisites Guide](package-extension-prerequisites.md)** (REQUIRED)


**CLAUDE: DO NOT PROCEED WITHOUT GOING THROUGH THE R PACKAGE SETUP GUIDE.**

---


## When to Use This Guide

✅ **Use this guide if you are:**
- Creating a **new R package** that adds custom metrics
- Building on yardstick's foundation without modifying yardstick itself
- Publishing metrics to CRAN or sharing privately
- Want to avoid tight coupling with yardstick internals

❌ **Don't use this guide if you are:**
- Contributing a PR directly to the yardstick package → Use [Source Development Guide](source-guide.md)
- Working inside the yardstick repository → Use [Source Development Guide](source-guide.md)

---

## Prerequisites

### Package Setup Required

**⚠️ IMPORTANT**: Before implementing yardstick metrics, you MUST complete the extension prerequisites:

👉 **[Extension Prerequisites Guide](package-extension-prerequisites.md)** (REQUIRED)

Complete all steps in the setup guide and ensure the verification script passes.

**After setup verification passes, return here to implement your metric.**

---



## Key Constraints for Extension Development

### ❌ Never Use Internal Functions

**Critical:** You CANNOT use functions accessed with `:::`.

```r
# ❌ BAD - Will break, not exported
yardstick:::yardstick_mean(values, case_weights)

# ✅ GOOD - Use base R alternative
if (is.null(case_weights)) {
  mean(values)
} else {
  # Convert hardhat weights manually
  wts <- as.double(case_weights)
  weighted.mean(values, w = wts)
}
```

**Why?**
- Internal functions are not guaranteed to be stable
- They can change without notice
- Your package will fail CRAN checks
- Users will get cryptic errors

### ✅ Only Use Exported Functions

Safe to use:
- `yardstick::new_numeric_metric()`
- `yardstick::new_class_metric()`
- `yardstick::new_prob_metric()`
- `yardstick::check_numeric_metric()`
- `yardstick::check_class_metric()`
- `yardstick::check_prob_metric()`
- `yardstick::yardstick_remove_missing()`
- `yardstick::yardstick_any_missing()`
- `yardstick::numeric_metric_summarizer()`
- `yardstick::class_metric_summarizer()`
- `yardstick::prob_metric_summarizer()`
- `yardstick::yardstick_table()` (for confusion matrices)

### ✅ Self-Contained Implementations

You must implement all logic yourself:

```r
# Your implementation function
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  # Handle weights yourself
  if (is.null(case_weights)) {
    mean(errors)
  } else {
    # Manual conversion of hardhat weights
    if (inherits(case_weights, c("hardhat_importance_weights",
                                 "hardhat_frequency_weights"))) {
      case_weights <- as.double(case_weights)
    }
    weighted.mean(errors, w = case_weights)
  }
}
```

---

## Step-by-Step Implementation

### Step 1: Choose Your Metric Type

See the decision tree in the main [SKILL.md](../SKILL.md#choosing-your-metric-type) to determine:
- Numeric metric (regression)
- Class metric (classification with classes)
- Probability metric (classification with probabilities)
- Survival metric (time-to-event)
- Quantile metric (uncertainty quantification)

### Step 2: Create Implementation Function

```r
# R/mae.R

# Internal implementation (not exported)
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

### Step 3: Create Vector Interface

```r
#' @export
mae_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Validate na_rm parameter
  if (!is.logical(na_rm) || length(na_rm) != 1) {
    cli::cli_abort("{.arg na_rm} must be a single logical value.")
  }

  # Validate inputs (exported function)
  yardstick::check_numeric_metric(truth, estimate, case_weights)

  # Handle missing values (exported functions)
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

### Step 4: Create Data Frame Method

```r
#' Mean Absolute Error
#'
#' Calculate the mean absolute error between truth and estimate.
#'
#' @family numeric metrics
#' @family accuracy metrics
#'
#' @param data A data frame containing the columns specified by truth and estimate.
#' @param truth The column identifier for the true results. Should be unquoted.
#' @param estimate The column identifier for the predicted results. Should be unquoted.
#' @param na_rm A logical value indicating whether NA values should be removed (default TRUE).
#' @param case_weights The optional column identifier for case weights.
#' @param ... Not currently used.
#'
#' @return A tibble with columns .metric, .estimator, and .estimate.
#'
#' @examples
#' df <- data.frame(
#'   truth = c(1, 2, 3, 4, 5),
#'   estimate = c(1.5, 2.5, 2.5, 3.5, 4.5)
#' )
#'
#' mae(df, truth, estimate)
#'
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}

# Create the metric with metadata
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

### Step 5: Document Your Metric

Key roxygen tags:
- `@family` - Group with related metrics
- `@param` - Document all parameters
- `@return` - Describe return value
- `@examples` - Provide working examples
- `@export` - Make function available to users

### Step 6: Test Your Metric

See [Testing Patterns (Extension)](package-extension-requirements.md#testing-requirements) for complete details.

```r
# tests/testthat/test-mae.R

test_that("mae works correctly", {
  df <- data.frame(
    truth = c(1, 2, 3, 4, 5),
    estimate = c(1.5, 2.5, 2.5, 3.5, 4.5)
  )

  result <- mae(df, truth, estimate)

  expect_equal(result$.estimate, 0.5)
  expect_equal(result$.metric, "mae")
  expect_equal(result$.estimator, "standard")
})

test_that("mae handles NA correctly", {
  df <- data.frame(
    truth = c(1, 2, NA, 4, 5),
    estimate = c(1.5, 2.5, 2.5, 3.5, 4.5)
  )

  result_remove <- mae(df, truth, estimate, na_rm = TRUE)
  expect_false(is.na(result_remove$.estimate))

  result_keep <- mae(df, truth, estimate, na_rm = FALSE)
  expect_true(is.na(result_keep$.estimate))
})

test_that("mae validates inputs", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c("a", "b", "c")
  )

  expect_error(mae(df, truth, estimate))
})
```

---

## Complete Examples

### Numeric Metric Example (MAE)

See the complete example in Step-by-Step Implementation above.

### Class Metric Example (Custom Accuracy)

```r
# R/custom_accuracy.R

#' @export
custom_accuracy <- function(data, ...) {
  UseMethod("custom_accuracy")
}

custom_accuracy <- yardstick::new_class_metric(
  custom_accuracy,
  direction = "maximize"
)

#' @export
custom_accuracy.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                                       case_weights = NULL, ...) {
  yardstick::class_metric_summarizer(
    name = "custom_accuracy",
    fn = custom_accuracy_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights)
  )
}

#' @export
custom_accuracy_vec <- function(truth, estimate, na_rm = TRUE,
                                case_weights = NULL, ...) {
  yardstick::check_class_metric(truth, estimate, case_weights)

  if (na_rm) {
    result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  custom_accuracy_impl(truth, estimate, case_weights)
}

custom_accuracy_impl <- function(truth, estimate, case_weights = NULL) {
  # Use yardstick_table (exported) for confusion matrix
  xtab <- yardstick::yardstick_table(truth, estimate, case_weights)

  # Calculate accuracy
  correct <- sum(diag(xtab))
  total <- sum(xtab)

  correct / total
}
```

---

## Common Patterns

### Handling Case Weights

You must convert hardhat weights manually:

```r
if (!is.null(case_weights)) {
  if (inherits(case_weights, c("hardhat_importance_weights",
                               "hardhat_frequency_weights"))) {
    case_weights <- as.double(case_weights)
  }
  weighted.mean(values, w = case_weights)
}
```

### Using Confusion Matrices

```r
# yardstick_table is exported!
xtab <- yardstick::yardstick_table(truth, estimate, case_weights)

# Extract values
tp <- xtab[2, 2]  # True positives
tn <- xtab[1, 1]  # True negatives
fp <- xtab[1, 2]  # False positives
fn <- xtab[2, 1]  # False negatives
```

### NA Handling

Always use the exported functions:

```r
if (na_rm) {
  result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
  truth <- result$truth
  estimate <- result$estimate
  case_weights <- result$case_weights
} else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
  return(NA_real_)
}
```

---

## Development Workflow

See [Development Workflow](package-development-workflow.md) for complete details.

**Fast iteration cycle (run repeatedly):**
1. `devtools::document()` - Generate documentation
2. `devtools::load_all()` - Load your package
3. `devtools::test()` - Run tests

**Final validation (run once at end):**
4. `devtools::check()` - Full R CMD check

---

## Package Integration

### Package-Level Documentation

Create `R/{packagename}-package.R`:

```r
#' @keywords internal
"_PACKAGE"

#' @importFrom rlang .data := !! enquo enquos
#' @importFrom yardstick new_numeric_metric
NULL
```

### Declaring Exports

All metrics must be exported:

```r
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}

#' @export
mae_vec <- function(truth, estimate, ...) {
  # ...
}
```

---

## Testing

See [Testing Patterns (Extension)](package-extension-requirements.md#testing-requirements) for comprehensive guide.

**Required test categories:**
1. **Correctness**: Metric calculates correctly
2. **NA handling**: Both `na_rm = TRUE` and `FALSE`
3. **Input validation**: Wrong types, mismatched lengths
4. **Case weights**: Weighted and unweighted differ
5. **Edge cases**: All correct, all wrong, empty data

---

## Best Practices

See [Best Practices (Extension)](package-extension-requirements.md#best-practices) for complete guide.

**Key principles:**
- Use base pipe `|>` not magrittr pipe `%>%`
- Prefer for-loops over `purrr::map()`
- Use `cli::cli_abort()` for error messages
- Keep functions focused on single responsibility
- Validate early (in `_vec`), trust data in `_impl`

---

## Troubleshooting

See [Troubleshooting (Extension)](package-extension-requirements.md#common-issues-solutions) for complete guide.

**Common issues:**
- "No visible global function definition" → Add to package imports
- "Object not found" in tests → Use `devtools::load_all()` before testing
- NA handling bugs → Check both `na_rm = TRUE` and `FALSE` cases
- Case weights not working → Convert hardhat weights to numeric

---

## Reference Documentation

### Metric Types
- [Numeric Metrics](numeric-metrics.md) - Regression metrics
- [Class Metrics](class-metrics.md) - Classification metrics
- [Probability Metrics](probability-metrics.md) - Probability-based metrics
- [Ordered Probability Metrics](ordered-probability-metrics.md) - Ordinal metrics
- [Survival Metrics](static-survival-metrics.md) - Time-to-event metrics
- [Quantile Metrics](quantile-metrics.md) - Uncertainty metrics

### Core Concepts
- [Metric System Architecture](metric-system.md)
- [Combining Metrics](metric-set.md)
- [Confusion Matrix](confusion-matrix.md)
- [Case Weights](case-weights.md)

### Shared References
- [Extension Prerequisites](package-extension-prerequisites.md)
- [Development Workflow](package-development-workflow.md)
- [Testing Patterns](package-extension-requirements.md#testing-requirements)
- [Roxygen Documentation](package-roxygen-documentation.md)
- [Best Practices](package-extension-requirements.md#best-practices)
- [Troubleshooting](package-extension-requirements.md#common-issues-solutions)

---

## Next Steps

1. **Complete extension prerequisites** following [Extension Prerequisites](package-extension-prerequisites.md)
2. **Choose your metric type** from the [main SKILL.md](../SKILL.md)
3. **Implement your metric** following the step-by-step guide above
4. **Test thoroughly** using [Testing Patterns](package-extension-requirements.md#testing-requirements)
5. **Run `devtools::check()`** to ensure CRAN compliance
6. **Publish** to CRAN or share with your team

---

## Getting Help

- Check [Troubleshooting Guide](package-extension-requirements.md#common-issues-solutions)
- Review existing examples in reference documentation
- Study the main [yardstick SKILL.md](../SKILL.md) for more details
- Search GitHub issues: https://github.com/tidymodels/yardstick/issues
