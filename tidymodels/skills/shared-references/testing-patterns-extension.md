# Testing Patterns for Extension Packages

**Context:** This guide is for **extension development** - creating new packages that extend tidymodels packages like yardstick or recipes.

**Key principle:** ❌ **Never use internal functions or test helpers** - they are not exported and may change without notice.

For source development (contributing to tidymodels packages directly), see the package-specific source guides.

---

Comprehensive guide to testing R packages in the tidymodels ecosystem using testthat.

## Test File Organization

### File naming conventions

- **Source files**: `R/yourfile.R`
- **Test files**: `tests/testthat/test-yourfile.R`

The test file name should match the source file name with `test-` prefix.

### Test structure

```r
# tests/testthat/test-yourfunction.R

test_that("descriptive test name", {
  # Arrange: Set up test data
  data <- prepare_test_data()

  # Act: Call the function
  result <- your_function(data)

  # Assert: Verify expectations
  expect_equal(result, expected_value)
})
```

## Creating Test Data

### DO: Create your own test data

**Simple, explicit test data is best:**

```r
# Numeric/regression data
test_data <- data.frame(
  truth = c(1, 2, 3, 4, 5),
  estimate = c(1.1, 2.2, 2.9, 4.1, 4.8)
)

# Binary classification data
binary_data <- data.frame(
  truth = factor(c("yes", "yes", "no", "no"), levels = c("yes", "no")),
  estimate = factor(c("yes", "no", "yes", "no"), levels = c("yes", "no"))
)

# Multiclass data
multiclass_data <- data.frame(
  truth = factor(c("A", "A", "B", "B", "C", "C")),
  estimate = factor(c("A", "B", "B", "C", "C", "A"))
)
```

### DON'T: Rely on internal test helpers

**Avoid:**
```r
# DON'T use internal yardstick helpers
data <- data_altman()  # NOT EXPORTED
data <- data_three_class()  # NOT EXPORTED
```

These are internal functions and may change or disappear.

### Use standard datasets

For recipe steps and general R package testing:

```r
# Built-in R datasets
data(mtcars)
data(iris)

# modeldata package (add to Suggests)
data(biomass, package = "modeldata")
```

## Standard Test Categories

Every function should have tests for these categories:

### 1. Correctness Tests

Verify the calculation produces correct results:

```r
test_that("calculations are correct", {
  # Prepare data with known results
  truth <- c(10, 20, 30, 40, 50)
  estimate <- c(10, 20, 30, 40, 50)

  # Calculate expected value by hand
  expected <- 0  # Perfect predictions

  result <- your_metric_vec(truth, estimate)

  expect_equal(result, expected)
})
```

**For recipe steps:**
```r
test_that("working correctly", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourname(disp, hp)

  # Test untrained tidy()
  untrained_tidy <- tidy(rec, 1)
  expect_equal(untrained_tidy$value, rep(rlang::na_dbl, 2))

  # Test prep()
  prepped <- prep(rec, training = mtcars)

  # Verify parameters learned correctly
  expect_equal(
    prepped$steps[[1]]$your_param,
    expected_values
  )

  # Test trained tidy()
  trained_tidy <- tidy(prepped, 1)
  expect_equal(trained_tidy$value, expected_values)

  # Test bake()
  results <- bake(prepped, mtcars)
  expect_equal(
    results$disp,
    expected_transformed_values,
    tolerance = 1e-7
  )
})
```

### 2. Parameter Validation Tests

Verify parameters are validated correctly:

```r
test_that("parameter validation works", {
  # Test invalid na_rm
  expect_error(
    your_function(data, truth, estimate, na_rm = "yes"),
    "must be a single logical value"
  )

  # Test invalid custom parameter
  expect_error(
    your_function(data, truth, estimate, threshold = -1),
    "must be non-negative"
  )
})
```

**Use snapshots for detailed error messages:**
```r
test_that("parameter validation produces clear errors", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourname(disp, invalid_param = "bad")

  expect_snapshot(error = TRUE, prep(rec, training = mtcars))
})
```

### 3. NA Handling Tests

Test both `na_rm = TRUE` and `na_rm = FALSE`:

```r
test_that("NA handling with na_rm = TRUE", {
  truth <- c(1, 2, NA, 4)
  estimate <- c(1.1, NA, 3.1, 4.1)

  # Only use non-NA pairs: (1, 1.1) and (4, 4.1)
  result <- your_function_vec(truth, estimate, na_rm = TRUE)

  expect_equal(result, expected_value_from_complete_pairs)
})

test_that("NA handling with na_rm = FALSE", {
  truth <- c(1, 2, NA)
  estimate <- c(1, 2, 3)

  result <- your_function_vec(truth, estimate, na_rm = FALSE)

  expect_equal(result, NA_real_)
})
```

### 4. Case Weights Tests

Test with and without case weights:

```r
test_that("case weights calculations are correct", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.5, 2.5, 3.5),
    case_weights = c(1, 2, 1)
  )

  # Calculate weighted expectation by hand
  # errors = (0.5, 0.5, 0.5)
  # weighted = (1*0.5 + 2*0.5 + 1*0.5) / (1+2+1) = 2/4 = 0.5
  expect_equal(
    your_metric_vec(df$truth, df$estimate, case_weights = df$case_weights),
    0.5
  )
})

test_that("works with hardhat case weights", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.5, 2.5, 3.5)
  )

  imp_wgt <- hardhat::importance_weights(c(1, 2, 1))
  freq_wgt <- hardhat::frequency_weights(c(1, 2, 1))

  expect_no_error(
    your_metric_vec(df$truth, df$estimate, case_weights = imp_wgt)
  )

  expect_no_error(
    your_metric_vec(df$truth, df$estimate, case_weights = freq_wgt)
  )
})
```

**For recipe steps:**
```r
test_that("step works with case weights", {
  mtcars_freq <- mtcars
  mtcars_freq$cyl <- hardhat::frequency_weights(mtcars_freq$cyl)

  rec <- recipe(mpg ~ ., mtcars_freq) |>
    step_yourname(disp, hp) |>
    prep()

  # Verify weighted computation differs from unweighted
  expect_equal(
    tidy(rec, number = 1)[["value"]],
    expected_weighted_values
  )

  # Snapshot to show case weights were used
  expect_snapshot(rec)
})
```

### 5. Single Column/Predictor Tests

Test with minimal input:

```r
test_that("single predictor works", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourname(disp)  # Only one column

  prepped <- prep(rec, training = mtcars)
  results <- bake(prepped, mtcars)

  expect_equal(results$disp, expected_values)
})
```

### 6. Data Frame Method Tests (for metrics)

```r
test_that("data frame method works", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.1, 2.2, 3.3)
  )

  result <- your_metric(df, truth, estimate)

  expect_s3_class(result, "tbl_df")
  expect_equal(result$.metric, "your_metric")
  expect_equal(result$.estimator, "standard")
  expect_equal(nrow(result), 1)
})
```

### 7. Attribute Tests (for metrics)

```r
test_that("metric has correct attributes", {
  expect_equal(attr(your_metric, "direction"), "maximize")
  expect_equal(attr(your_metric, "range"), c(0, 1))
})
```

## Integration Tests

### Testing with metric_set() (for metrics)

```r
test_that("works in metric_set", {
  df <- data.frame(
    truth = c(1, 2, 3, 4, 5),
    estimate = c(1.1, 2.2, 2.9, 4.1, 5.2)
  )

  metrics <- yardstick::metric_set(your_metric, yardstick::rmse)
  result <- metrics(df, truth, estimate)

  expect_s3_class(result, "tbl_df")
  expect_equal(nrow(result), 2)
  expect_true("your_metric" %in% result$.metric)
  expect_true("rmse" %in% result$.metric)
})
```

### Testing with grouped data

```r
test_that("works with grouped data", {
  df <- data.frame(
    group = rep(c("A", "B"), each = 3),
    truth = c(1, 2, 3, 4, 5, 6),
    estimate = c(1.1, 2.1, 3.1, 4.1, 5.1, 6.1)
  )

  result <- df |>
    dplyr::group_by(group) |>
    your_metric(truth, estimate)

  expect_equal(nrow(result), 2)
  expect_equal(result$group, c("A", "B"))
})
```

## Infrastructure Tests (Required for Recipe Steps)

These ensure recipe steps work in edge cases:

```r
test_that("bake method errors when needed columns are missing", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourname(disp, hp)

  rec_trained <- prep(rec, training = mtcars)

  expect_snapshot(
    error = TRUE,
    bake(rec_trained, new_data = mtcars[, 1:2])
  )
})

test_that("empty printing", {
  rec <- recipe(mpg ~ ., mtcars) |>
    step_yourname()

  expect_snapshot(rec)
  expect_snapshot(prep(rec, mtcars))
})

test_that("empty selection prep/bake is a no-op", {
  rec1 <- recipe(mpg ~ ., mtcars)
  rec2 <- step_yourname(rec1)

  rec1 <- prep(rec1, mtcars)
  rec2 <- prep(rec2, mtcars)

  baked1 <- bake(rec1, mtcars)
  baked2 <- bake(rec2, mtcars)

  expect_identical(baked1, baked2)
})

test_that("empty selection tidy method works", {
  rec <- recipe(mpg ~ ., mtcars) |>
    step_yourname()

  expect <- tibble::tibble(
    terms = character(),
    value = double(),
    id = character()
  )

  expect_identical(tidy(rec, number = 1), expect)

  rec <- prep(rec, mtcars)
  expect_identical(tidy(rec, number = 1), expect)
})

test_that("printing", {
  rec <- recipe(mpg ~ ., mtcars) |>
    step_yourname(disp)

  expect_snapshot(print(rec))
  expect_snapshot(prep(rec))
})

test_that("0 and 1 rows data work in bake method", {
  rec <- recipe(~., data = mtcars) |>
    step_yourname(mpg, disp) |>
    prep()

  expect_identical(
    nrow(bake(rec, dplyr::slice(mtcars, 1))),
    1L
  )
  expect_identical(
    nrow(bake(rec, dplyr::slice(mtcars, 0))),
    0L
  )
})
```

## Edge Case Tests

Test edge cases explicitly to avoid surprises in production:

### Empty data

```r
test_that("handles empty data frames", {
  df <- data.frame(truth = numeric(0), estimate = numeric(0))
  result <- your_metric(df, truth, estimate)

  expect_s3_class(result, "tbl_df")
  # .estimate will be NA or NaN (mean(numeric(0)) = NaN)
})
```

### All-NA values

```r
test_that("handles all-NA values", {
  result <- your_metric_vec(c(NA, NA), c(1, 2), na_rm = TRUE)
  expect_true(is.na(result) || is.nan(result))  # Empty after removing NAs
})
```

### Perfect predictions

```r
test_that("perfect predictions give optimal value", {
  truth <- c(10, 20, 30, 40, 50)
  estimate <- c(10, 20, 30, 40, 50)

  result <- your_metric_vec(truth, estimate)

  expect_equal(result, optimal_value)  # 0 for minimize, 1 for maximize
})
```

### Single observation

```r
test_that("works with single observation", {
  # May be undefined for variance-based metrics
  result <- your_metric_vec(c(1), c(1.1))

  expect_true(is.numeric(result))
})
```

### Extreme numeric values

```r
test_that("handles extreme values", {
  # Very large values
  result_large <- your_metric_vec(c(1e10, 2e10), c(1.1e10, 2.1e10))
  expect_true(is.finite(result_large))

  # Very small values
  result_small <- your_metric_vec(c(1e-10, 2e-10), c(1.1e-10, 2.1e-10))
  expect_true(is.finite(result_small))
})
```

## Best Practices

### Use expect_snapshot()

**For error messages:**
```r
expect_snapshot(error = TRUE, your_function(bad_input))
```

**For warnings:**
```r
expect_snapshot(warning = TRUE, your_function(questionable_input))
```

**For printed output:**
```r
expect_snapshot(print(object))
```

### Write meaningful test names

```r
# Good: descriptive test names
test_that("calculations are correct for binary classification", { ... })
test_that("NA values are removed when na_rm = TRUE", { ... })

# Bad: vague test names
test_that("works", { ... })
test_that("test 1", { ... })
```

### Minimal comments

Let test names and code be self-documenting:

```r
# Good: minimal necessary comments
test_that("weighted mean differs from unweighted", {
  # errors = (0.5, 0.5, 0.5), weights = (1, 2, 1)
  expect_equal(weighted_result, 0.5)
  expect_equal(unweighted_result, 0.5)
})

# Avoid: over-commenting obvious code
test_that("test", {
  # Create a data frame
  df <- data.frame(x = 1:3)
  # Call the function
  result <- my_function(df)
  # Check if result equals 2
  expect_equal(result, 2)
})
```

### Use precise expectations

```r
# Good: specific expectations
expect_equal(result, 0.5)
expect_s3_class(result, "tbl_df")
expect_identical(result1, result2)

# Avoid: imprecise expectations
expect_true(result == 0.5)  # Use expect_equal instead
expect_true(is.data.frame(result))  # Use expect_s3_class instead
```

### Tolerance for floating point

```r
# For floating point comparisons
expect_equal(result, expected, tolerance = 1e-7)

# For exact matches (integers, strings)
expect_identical(result, expected)
```

## Running Tests

### Run all tests

```r
devtools::test()
```

### Run specific test file

```r
devtools::test_active_file()  # Current file in RStudio
devtools::test_file("tests/testthat/test-yourfile.R")
```

### Run tests matching pattern

```r
devtools::test(filter = "your_function")
```

### Skip slow tests during development

```r
test_that("slow integration test", {
  skip_if_not(interactive(), "Slow test - run manually")

  # Expensive test here
})

test_that("requires external resource", {
  skip_on_cran()
  skip_if_offline()

  # Test requiring internet/external resource
})
```

## Test Coverage

Check which lines of code are tested:

```r
# Install covr package
install.packages("covr")

# Run coverage report
covr::package_coverage()

# Interactive HTML report
covr::report()
```

**Aim for:**
- 90%+ coverage of main functions
- 100% coverage of critical paths
- Don't obsess over 100% - some code is hard to test

## Troubleshooting Tests

### Test passes locally but fails in check()

**Problem:** Test relies on local environment

**Solution:** Make tests self-contained, don't rely on:
- Working directory assumptions
- Installed packages not in DESCRIPTION
- External files or data

### Floating point comparison failures

**Problem:** Exact equality fails for floating point

**Solution:** Use tolerance
```r
expect_equal(result, expected, tolerance = 1e-7)
```

### Snapshot tests fail after updating

**Problem:** Output changed (expected or unexpected)

**Solution:** Review changes, update snapshots if correct
```r
# In test file, after verifying change is correct
testthat::snapshot_accept()
```

### Tests are slow

**Solution:**
- Use smaller test datasets
- Skip slow tests with `skip_if_not(interactive())`
- Profile tests to find bottlenecks

## Next Steps

- Document your functions: [roxygen-documentation.md](roxygen-documentation.md)
- Follow coding best practices: [best-practices.md](best-practices.md)
- Review package setup: [r-package-setup.md](r-package-setup.md)
