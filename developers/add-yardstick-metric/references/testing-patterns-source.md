# Testing Patterns for Yardstick Source Development

**Context:** This guide is for **source development** - contributing to the
yardstick package directly.

**Key principle:** ✅ **You CAN use internal functions and test helpers** -
you're developing the package itself.

For extension development (creating new packages), see [Testing Patterns
(Extension)](package-extension-requirements.md#testing-requirements).

--------------------------------------------------------------------------------

## When to Use Internal Test Helpers

When developing yardstick itself, you have access to internal test data and
helpers. Use them to:

- Maintain consistency with existing tests

- Leverage well-tested data structures

- Match the testing style of the package

## Yardstick Internal Test Helpers

### Available Test Data

```r
# Binary classification data
data <- data_altman()
# tibble with: pathology (truth), scan (estimate)

# Three-class data
data <- data_three_class()
# tibble with: obs (truth), pred (estimate), VF, F, M (probabilities)

# HPC cross-validation data
data <- data_hpc_cv1()
# tibble with: obs, pred, VF, F, M, L, Resample

# Two-class example data
data <- two_class_example
# Exported data: truth, Class1, Class2, predicted

# Multi-class example data
data <- hpc_cv
# Exported data: obs, pred, VF, F, M, L, Resample
```

### When to Use Each

**`data_altman()`** - Binary classification

- Use for: accuracy, sensitivity, specificity, ppv, npv

- Has: 251 observations, well-balanced classes

**`data_three_class()`** - Multiclass classification

- Use for: multiclass metrics with estimator variants

- Has: obs (truth), pred (estimate), probabilities for 3 classes

- Good for testing macro, micro, macro_weighted averaging

**`hpc_cv`** - Cross-validation data

- Use for: metrics with resamples

- Has: multiple folds for grouped calculations

## Snapshot Testing in Yardstick

Yardstick uses snapshot testing extensively with `testthat::expect_snapshot()`.

### When to Use Snapshots

✅ **Use snapshots for:**

- Full metric output (tibbles with .metric, .estimator, .estimate)

- Error messages

- Warning messages

- Print output from metric objects

- Complex multiclass outputs

❌ **Don't use snapshots for:**

- Simple numeric comparisons (use `expect_equal()`)

- Testing specific values (use assertions)

- Edge cases that need explicit checks

### Snapshot Testing Examples

```r
test_that("mae returns correct structure", {
  # Using internal test data
  df <- data_altman()

  result <- mae(df, pathology, scan)

  # Snapshot the entire result
  expect_snapshot(result)
})

test_that("mae errors on wrong input", {
  df <- data.frame(
    truth = 1:5,
    estimate = letters[1:5]  # Wrong type
  )

  expect_snapshot(error = TRUE, {
    mae(df, truth, estimate)
  })
})

test_that("multiclass metric shows all estimators", {
  df <- data_three_class()

  # All three estimator types
  result_macro <- accuracy(df, obs, pred, estimator = "macro")
  result_micro <- accuracy(df, obs, pred, estimator = "micro")
  result_weighted <- accuracy(df, obs, pred, estimator = "macro_weighted")

  expect_snapshot({
    result_macro
    result_micro
    result_weighted
  })
})
```

### Updating Snapshots

When metric behavior changes intentionally:

```r
# Run tests and review changes
testthat::snapshot_review()

# Or accept all changes (use carefully)
testthat::snapshot_accept()
```

## File Naming Conventions

Yardstick organizes tests by metric type:

### Test File Names

- **Numeric metrics**: `tests/testthat/test-num-[name].R`

  - Example: `test-num-mae.R`, `test-num-rmse.R`
- **Class metrics**: `tests/testthat/test-class-[name].R`

  - Example: `test-class-accuracy.R`, `test-class-precision.R`
- **Probability metrics**: `tests/testthat/test-prob-[name].R`

  - Example: `test-prob-roc_auc.R`, `test-prob-mn_log_loss.R`
- **Survival metrics**: `tests/testthat/test-surv-[name].R`

  - Example: `test-surv-concordance_survival.R`

### Match Source File Names

Test files should match source file names:

- `R/num-mae.R` → `tests/testthat/test-num-mae.R`

- `R/class-accuracy.R` → `tests/testthat/test-class-accuracy.R`

## Test Organization in Yardstick

### Standard Test Structure

```r
# tests/testthat/test-num-mae.R

test_that("mae works correctly", {
  # Use internal test data
  df <- data_altman()

  result <- mae(df, pathology, scan)
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

  # With na_rm = TRUE
  result_remove <- mae(df, pathology, scan, na_rm = TRUE)
  expect_false(is.na(result_remove$.estimate))

  # With na_rm = FALSE
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

  # Weights should affect result
  expect_false(
    result_unweighted$.estimate == result_weighted$.estimate
  )
})

test_that("mae errors on length mismatch", {
  expect_snapshot(error = TRUE, {
    mae_vec(1:5, 1:4)
  })
})
```

## Testing Multiclass Metrics

For metrics with estimator variants:

```r
test_that("accuracy works with all estimators", {
  df <- data_three_class()

  # Binary (automatically detected)
  binary_df <- df[df$obs != "VF", ]
  binary_df$obs <- droplevels(binary_df$obs)
  binary_df$pred <- droplevels(binary_df$pred)

  expect_snapshot(accuracy(binary_df, obs, pred))

  # Multiclass with different estimators
  expect_snapshot(accuracy(df, obs, pred, estimator = "macro"))
  expect_snapshot(accuracy(df, obs, pred, estimator = "micro"))
  expect_snapshot(accuracy(df, obs, pred, estimator = "macro_weighted"))
})
```

## Testing with Probabilities

For probability-based metrics:

```r
test_that("roc_auc works with probability columns", {
  df <- data_three_class()

  # Binary case
  binary_df <- df[df$obs != "VF", ]
  binary_df$obs <- droplevels(binary_df$obs)

  result <- roc_auc(binary_df, obs, M)
  expect_snapshot(result)

  # Multiclass case (hand-till method)
  result_multi <- roc_auc(df, obs, VF, F, M, estimator = "hand_till")
  expect_snapshot(result_multi)
})
```

## Testing Grouped Data

For metrics with grouped data frames:

```r
test_that("mae works with grouped data", {
  df <- hpc_cv
  df_grouped <- dplyr::group_by(df, Resample)

  result <- mae(df_grouped, obs, pred)

  # Should have one row per group
  expect_equal(nrow(result), length(unique(df$Resample)))
  expect_snapshot(result)
})
```

## Testing Case Weights

All metrics should support case weights:

```r
test_that("mae respects case weights", {
  df <- data.frame(
    truth = c(1, 2, 3, 4, 5),
    estimate = c(1, 2, 3, 4, 5),
    weights = c(1, 1, 1, 1, 100)  # Heavy weight on last obs
  )

  # Perfect except for last observation
  df$estimate[5] <- 10  # Error of 5 on heavily weighted obs

  # With importance weights
  df$wt <- hardhat::importance_weights(df$weights)

  result_weighted <- mae(df, truth, estimate, case_weights = wt)
  result_unweighted <- mae(df, truth, estimate)

  # Weighted should be much higher due to heavy weight on error
  expect_true(result_weighted$.estimate > result_unweighted$.estimate)
})
```

## Testing Edge Cases

Always test edge cases:

```r
test_that("mae handles edge cases", {
  # Perfect predictions
  df <- data.frame(truth = 1:5, estimate = 1:5)
  expect_equal(mae_vec(df$truth, df$estimate), 0)

  # All wrong (maximum error)
  df <- data.frame(truth = c(0, 0, 0), estimate = c(10, 10, 10))
  expect_equal(mae_vec(df$truth, df$estimate), 10)

  # Single observation
  expect_equal(mae_vec(1, 1.5), 0.5)

  # All NA
  expect_true(is.na(mae_vec(c(NA, NA), c(1, 2), na_rm = FALSE)))
})
```

## Testing Metric Set Integration

Test that metrics work in `metric_set()`:

```r
test_that("mae works in metric_set", {
  df <- data_altman()

  metrics <- metric_set(mae, rmse, mse)
  result <- metrics(df, pathology, scan)

  # Should have 3 rows
  expect_equal(nrow(result), 3)

  # Should have mae in results
  expect_true("mae" %in% result$.metric)

  expect_snapshot(result)
})
```

## Common Testing Patterns

### Test Both Interfaces

Always test both data frame and vector interfaces:

```r
test_that("mae data frame interface works", {
  df <- data.frame(truth = 1:5, estimate = c(1.5, 2.5, 2.5, 3.5, 4.5))
  result <- mae(df, truth, estimate)
  expect_snapshot(result)
})

test_that("mae vector interface works", {
  result <- mae_vec(1:5, c(1.5, 2.5, 2.5, 3.5, 4.5))
  expect_equal(result, 0.5)
})
```

### Test Parameter Validation

```r
test_that("mae validates na_rm parameter", {
  expect_snapshot(error = TRUE, {
    mae_vec(1:5, 1:5, na_rm = "yes")  # Should be logical
  })

  expect_snapshot(error = TRUE, {
    mae_vec(1:5, 1:5, na_rm = c(TRUE, FALSE))  # Should be length 1
  })
})
```

## Using Internal Validation Functions

Yardstick has internal validation functions you can use:

```r
# In your _vec function
mae_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Use internal validation
  check_numeric_metric(truth, estimate, case_weights)

  # Your implementation
  # ...
}
```

These provide consistent error messages across all metrics.

## Snapshot File Organization

Snapshots are stored in:
```
tests/testthat/_snaps/
├── test-num-mae.md
├── test-class-accuracy.md
└── test-prob-roc_auc.md
```

Each test file gets its own snapshot file.

## Running Tests

```r
# Run all tests
devtools::test()

# Run specific test file
testthat::test_file("tests/testthat/test-num-mae.R")

# Run tests matching pattern
devtools::test(filter = "mae")

# Review snapshot changes
testthat::snapshot_review()
```

## Next Steps

- Review [Best Practices (Source)](best-practices-source.md) for yardstick
  coding standards

- Check [Troubleshooting (Source)](troubleshooting-source.md) for common issues

- See existing test files in `tests/testthat/` for more examples
