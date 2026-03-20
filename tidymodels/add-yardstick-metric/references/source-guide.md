# Source Development Guide: Contributing to Yardstick

Complete guide for contributing new metrics to the yardstick package itself.

---

## When to Use This Guide

✅ **Use this guide if you are:**
- Contributing a PR directly to the yardstick package
- Working inside the yardstick repository
- Adding metrics that should be part of yardstick core
- Modifying existing yardstick metrics

❌ **Don't use this guide if you are:**
- Creating a new package that extends yardstick → Use [Extension Development Guide](extension-guide.md)
- Building standalone metrics → Use [Extension Development Guide](extension-guide.md)

---

## Prerequisites

### Clone the Yardstick Repository

```bash
# Clone from GitHub
git clone https://github.com/tidymodels/yardstick.git
cd yardstick

# Create a feature branch
git checkout -b feature/add-metric-name
```

See [Repository Access](package-repository-access.md) for more details.

### Install Development Dependencies

```r
# Install yardstick with all dependencies
devtools::install_dev_deps()

# Load the package for development
devtools::load_all()
```

---

## Understanding Yardstick's Architecture

### Package Organization

```
yardstick/
├── R/
│   ├── num-*.R          # Numeric metrics
│   ├── class-*.R        # Classification metrics
│   ├── prob-*.R         # Probability metrics
│   ├── surv-*.R         # Survival metrics
│   ├── aaa-*.R          # Core infrastructure
│   └── utils-*.R        # Internal utilities
├── tests/testthat/
│   ├── test-num-*.R
│   ├── test-class-*.R
│   └── _snaps/          # Snapshot test outputs
└── man-roxygen/         # Documentation templates
```

### File Naming Conventions

**Source files must follow strict naming:**
- Numeric: `R/num-[name].R` → `R/num-mae.R`
- Class: `R/class-[name].R` → `R/class-accuracy.R`
- Probability: `R/prob-[name].R` → `R/prob-roc_auc.R`
- Survival: `R/surv-[name].R` → `R/surv-concordance_survival.R`

**Test files must match:**
- `R/num-mae.R` → `tests/testthat/test-num-mae.R`

---

## Working with Internal Functions

### ✅ You CAN Use Internal Functions

When developing yardstick itself, internal functions are available:

```r
# ✅ GOOD - You're developing the package
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  # Use internal helper
  yardstick_mean(errors, case_weights = case_weights)
}
```

### Common Internal Helpers

#### `yardstick_mean()` - Weighted Mean

Handles case weights consistently:

```r
yardstick_mean <- function(x, case_weights = NULL) {
  if (is.null(case_weights)) {
    mean(x)
  } else {
    if (inherits(case_weights, c("hardhat_importance_weights",
                                 "hardhat_frequency_weights"))) {
      case_weights <- as.double(case_weights)
    }
    weighted.mean(x, w = case_weights)
  }
}
```

#### `finalize_estimator_internal()` - Estimator Selection

For multiclass metrics:

```r
accuracy.data.frame <- function(data, truth, estimate,
                                estimator = NULL, ...,
                                call = rlang::caller_env()) {
  estimator <- finalize_estimator_internal(
    estimator,
    metric_class = "accuracy",
    call = call
  )

  # Rest of implementation
}
```

#### Validation Functions

```r
# These provide consistent error messages
check_numeric_metric(truth, estimate, case_weights)
check_class_metric(truth, estimate, case_weights)
check_prob_metric(truth, estimate, case_weights)
```

### Finding Internal Functions

```r
# List all internal functions
ls("package:yardstick", all.names = TRUE)

# Search in source
# grep -r "yardstick_" R/

# View source
yardstick:::yardstick_mean
```

See [Best Practices (Source)](best-practices-source.md) for complete guide to internal functions.

---

## Step-by-Step Implementation

### Step 1: Choose Your Metric Type

Determine which category your metric falls into:
- Numeric (regression)
- Class (classification with classes)
- Probability (classification with probabilities)
- Survival (time-to-event)

See the main [SKILL.md](../SKILL.md) for the complete decision tree.

### Step 2: Create Source File

Create `R/num-[name].R` (or class-, prob-, etc.):

```r
# R/num-mae.R

#' Mean Absolute Error
#'
#' @family numeric metrics
#' @family accuracy metrics
#' @templateVar fn mae
#' @template return
#' @template event_first
#'
#' @inheritParams rmse
#'
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}

mae <- new_numeric_metric(mae, direction = "minimize")

#' @export
#' @rdname mae
mae.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                           case_weights = NULL, ...) {
  numeric_metric_summarizer(
    name = "mae",
    fn = mae_vec,
    data = data,
    truth = !!enquo(truth),
    estimate = !!enquo(estimate),
    na_rm = na_rm,
    case_weights = !!enquo(case_weights)
  )
}

#' @export
mae_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  check_numeric_metric(truth, estimate, case_weights)

  if (na_rm) {
    result <- yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  mae_impl(truth, estimate, case_weights)
}

# Internal implementation
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  # Use internal helper
  yardstick_mean(errors, case_weights = case_weights)
}
```

### Step 3: Document with Templates

Yardstick uses extensive templates:

```r
#' @templateVar fn mae
#' @template return
#' @template event_first
```

Templates are defined in `man-roxygen/` directory.

### Step 4: Create Test File

Create `tests/testthat/test-num-mae.R`:

```r
test_that("mae works correctly", {
  # Use internal test data
  df <- data_altman()

  result <- mae(df, pathology, scan)

  # Use snapshot testing
  expect_snapshot(result)
})

test_that("mae works with numeric vectors", {
  truth <- c(1, 2, 3, 4, 5)
  estimate <- c(1.5, 2.5, 2.5, 3.5, 4.5)

  expect_equal(mae_vec(truth, estimate), 0.5)
})

test_that("mae handles NA correctly", {
  df <- data_altman()
  df$pathology[1:10] <- NA

  result_remove <- mae(df, pathology, scan, na_rm = TRUE)
  expect_false(is.na(result_remove$.estimate))

  result_keep <- mae(df, pathology, scan, na_rm = FALSE)
  expect_true(is.na(result_keep$.estimate))
})

test_that("mae validates input types", {
  df <- data.frame(
    truth = 1:5,
    estimate = letters[1:5]
  )

  expect_snapshot(error = TRUE, {
    mae(df, truth, estimate)
  })
})

test_that("mae works with case weights", {
  df <- data_altman()
  df$weights <- seq_len(nrow(df))

  result_unweighted <- mae(df, pathology, scan)
  result_weighted <- mae(df, pathology, scan, case_weights = weights)

  expect_false(
    result_unweighted$.estimate == result_weighted$.estimate
  )
})
```

See [Testing Patterns (Source)](testing-patterns-source.md) for comprehensive testing guide.

### Step 5: Run Tests and Check

```r
# Document
devtools::document()

# Load
devtools::load_all()

# Test
devtools::test()

# Full check
devtools::check()
```

---

## Documentation Patterns

### Using @template

```r
#' @templateVar fn mae
#' @template return
```

Available templates (in `man-roxygen/`):
- `@template return` - Standard return value
- `@template event_first` - Event level for class metrics
- `@template multiclass` - Multiclass documentation

### Using @templateVar

Define variables before templates:

```r
#' @templateVar fn mae
#' @templateVar metric_fn mae
```

### Inheriting Parameters

Use `@inheritParams` extensively:

```r
#' @inheritParams rmse
```

This inherits all parameters from `rmse` documentation.

---

## Multiclass Metrics

### Supporting Multiple Estimators

For class metrics:

```r
accuracy.data.frame <- function(data, truth, estimate,
                                estimator = NULL, na_rm = TRUE,
                                case_weights = NULL, ...,
                                call = rlang::caller_env()) {
  # Finalize estimator
  estimator <- finalize_estimator_internal(
    estimator,
    metric_class = "accuracy",
    call = call
  )

  class_metric_summarizer(
    name = "accuracy",
    fn = accuracy_vec,
    data = data,
    truth = !!enquo(truth),
    estimate = !!enquo(estimate),
    estimator = estimator,
    na_rm = na_rm,
    case_weights = !!enquo(case_weights),
    call = call
  )
}
```

### Implement Binary and Estimator Variants

```r
accuracy_vec <- function(truth, estimate, estimator = NULL,
                        na_rm = TRUE, case_weights = NULL, ...,
                        call = rlang::caller_env()) {
  # ... validation ...

  if (is_binary(estimator)) {
    accuracy_binary(truth, estimate, case_weights)
  } else {
    accuracy_estimator_impl(truth, estimate, estimator, case_weights)
  }
}
```

---

## Using Internal Test Data

### Available Test Helpers

```r
# Binary classification
data <- data_altman()

# Three-class data
data <- data_three_class()

# Cross-validation data
data <- data_hpc_cv1()
```

See [Testing Patterns (Source)](testing-patterns-source.md) for complete list.

---

## Snapshot Testing

Yardstick uses snapshots extensively:

```r
test_that("mae returns correct structure", {
  df <- data_altman()
  result <- mae(df, pathology, scan)

  # Snapshot entire result
  expect_snapshot(result)
})

test_that("mae errors appropriately", {
  expect_snapshot(error = TRUE, {
    mae_vec(1:5, letters[1:5])
  })
})
```

### Reviewing Snapshots

```r
# Review snapshot changes
testthat::snapshot_review()

# Accept changes
testthat::snapshot_accept()
```

---

## Consistency with Existing Metrics

### Study Similar Metrics

Before implementing:
- For numeric: `R/num-mae.R`, `R/num-rmse.R`
- For class: `R/class-accuracy.R`, `R/class-precision.R`
- For probability: `R/prob-roc_auc.R`

### Match Function Structure

```r
# 1. Generic (exported)
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}

# 2. Wrap with new_*_metric
mae <- new_numeric_metric(mae, direction = "minimize")

# 3. Data frame method (exported)
#' @export
#' @rdname mae
mae.data.frame <- function(...) {
  numeric_metric_summarizer(...)
}

# 4. Vector method (exported)
#' @export
mae_vec <- function(...) {
  # ... validation and NA handling ...
  mae_impl(...)
}

# 5. Implementation (NOT exported - internal)
mae_impl <- function(truth, estimate, case_weights = NULL) {
  # Core calculation
}
```

---

## Creating New Internal Helpers

### When to Create

Create internal helpers when:
- Logic is shared by 2+ metrics
- Complex calculation used repeatedly
- Abstraction improves clarity

### Naming and Documentation

```r
#' Calculate weighted mean with case weight handling
#'
#' @param x Numeric vector
#' @param case_weights Optional case weights
#'
#' @return Numeric scalar
#' @keywords internal
#' @noRd
yardstick_mean <- function(x, case_weights = NULL) {
  # Implementation
}
```

Use:
- `@keywords internal` to mark as internal
- `@noRd` to skip documentation generation
- Don't use `@export`

---

## Error Messages

Use cli for consistent errors:

```r
if (invalid) {
  cli::cli_abort(
    "{.arg estimator} must be {.val binary}, {.val macro}, or {.val micro}, not {.val {estimator}}.",
    call = call
  )
}
```

Always pass `call` parameter for better error context.

---

## PR Submission

### Before Submitting

1. **Run full check:**
   ```r
   devtools::check()
   ```
   Fix all errors, warnings, and notes.

2. **Update NEWS.md:**
   ```md
   ## yardstick (development version)

   * Added `mae()` metric for mean absolute error (#123).
   ```

3. **Commit changes:**
   ```bash
   git add .
   git commit -m "Add mae() metric"
   git push origin feature/add-metric-name
   ```

### Creating the PR

1. Go to https://github.com/tidymodels/yardstick
2. Click "New pull request"
3. Select your branch
4. Fill in description:
   - What metric does this add?
   - Why is it useful?
   - Reference any related issues

### Review Process

The tidymodels team will review your PR. Common feedback:
- Add more tests
- Match existing documentation style
- Use internal helpers
- Add examples
- Fix code style issues

See [Troubleshooting (Source)](troubleshooting-source.md) for common review feedback.

---

## Reference Documentation

### Source Development
- [Testing Patterns (Source)](testing-patterns-source.md) - Testing with internal helpers
- [Best Practices (Source)](best-practices-source.md) - Code style and internal functions
- [Troubleshooting (Source)](troubleshooting-source.md) - Common issues

### Metric Types
- [Numeric Metrics](numeric-metrics.md)
- [Class Metrics](class-metrics.md)
- [Probability Metrics](probability-metrics.md)
- [Survival Metrics](static-survival-metrics.md)

### Core Concepts
- [Metric System Architecture](metric-system.md)
- [Confusion Matrix](confusion-matrix.md)
- [Case Weights](case-weights.md)

### Shared References
- [Extension Prerequisites](package-extension-prerequisites.md)
- [Development Workflow](package-development-workflow.md)
- [Roxygen Documentation](package-roxygen-documentation.md)

---

## Next Steps

1. **Clone yardstick repository**
2. **Create feature branch**
3. **Implement your metric** following this guide
4. **Test thoroughly** using internal test data
5. **Run `devtools::check()`**
6. **Submit PR** to tidymodels/yardstick

---

## Getting Help

- Check [Troubleshooting (Source)](troubleshooting-source.md)
- Study existing metrics in the repository
- Review [Best Practices (Source)](best-practices-source.md)
- Open an issue on GitHub for questions
- Tag maintainers in your PR
