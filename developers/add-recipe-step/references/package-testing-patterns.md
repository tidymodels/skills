# Extension Development: Testing Patterns

**Context:** This guide is for **extension development** - creating new packages that extend tidymodels packages.

**Key principle:** ❌ **Never use internal functions** (accessed with `:::`)

Complete testing requirements and patterns for tidymodels extension packages.

---

## Testing Requirements

**INSTRUCTIONS FOR CLAUDE:** Test count should match complexity.

**Minimum: 8-10 essential tests** (all steps)
**Add feature-specific tests only when applicable** (see details below)

Target: 8-12 tests for simple steps, 12-18 for moderate, 18-25 for complex.

Comprehensive guide to testing R packages in the tidymodels ecosystem using testthat.

### Test File Organization

#### File naming conventions

- **Source files**: `R/yourfile.R`

- **Test files**: `tests/testthat/test-yourfile.R`

The test file name should match the source file name with `test-` prefix.

#### Test structure

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

### Creating Test Data

#### DO: Create your own test data

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

#### DON'T: Rely on internal test helpers

**Avoid:**
```r
# DON'T use internal yardstick helpers
data <- data_altman()  # NOT EXPORTED
data <- data_three_class()  # NOT EXPORTED
```

These are internal functions and may change or disappear.

#### Use standard datasets

For recipe steps and general R package testing:

```r
# Built-in R datasets
data(mtcars)
data(iris)

# modeldata package (add to Suggests)
data(biomass, package = "modeldata")
```

### Standard Test Categories

Every function should have tests for these categories:

#### 1. Correctness Tests

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

#### 2. Parameter Validation Tests

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

#### 3. NA Handling Tests

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

#### 4. Case Weights Tests

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

#### 5. Single Column/Predictor Tests

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

#### 6. Data Frame Method Tests (for metrics)

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

#### 7. Attribute Tests (for metrics)

```r
test_that("metric has correct attributes", {
  expect_equal(attr(your_metric, "direction"), "maximize")
  expect_equal(attr(your_metric, "range"), c(0, 1))
})
```

### Integration Tests

#### Testing with metric_set() (for metrics)

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

#### Testing with grouped data

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

### Infrastructure Tests (Required for Recipe Steps)

These ensure recipe steps work in edge cases. Required tests:

**1. Bake method errors when columns missing:**
```r
test_that("bake method errors when needed columns are missing", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourname(disp, hp) |>
    prep(training = mtcars)

  expect_snapshot(error = TRUE, bake(rec, new_data = mtcars[, 1:2]))
})
```

**2. Empty printing:**
```r
test_that("empty printing", {
  rec <- recipe(mpg ~ ., mtcars) |>
    step_yourname()

  expect_snapshot(rec)
  expect_snapshot(prep(rec, mtcars))
})
```

**Also required (follow similar patterns):**

- Empty selection prep/bake is a no-op

- Empty selection tidy method returns empty tibble

- Printing with selected columns

- 0 and 1 row data work in bake method

### Edge Case Tests

Test edge cases explicitly to avoid surprises in production:

```r
# Empty data
test_that("handles empty data frames", {
  df <- data.frame(truth = numeric(0), estimate = numeric(0))
  result <- your_metric(df, truth, estimate)
  expect_s3_class(result, "tbl_df")
})

# All-NA values
test_that("handles all-NA values", {
  result <- your_metric_vec(c(NA, NA), c(1, 2), na_rm = TRUE)
  expect_true(is.na(result) || is.nan(result))
})

# Perfect predictions
test_that("perfect predictions give optimal value", {
  result <- your_metric_vec(c(10, 20, 30), c(10, 20, 30))
  expect_equal(result, optimal_value)  # 0 for minimize, 1 for maximize
})

# Single observation (may be undefined for variance-based metrics)
test_that("works with single observation", {
  expect_true(is.numeric(your_metric_vec(c(1), c(1.1))))
})

# Extreme numeric values
test_that("handles extreme values", {
  expect_true(is.finite(your_metric_vec(c(1e10, 2e10), c(1.1e10, 2.1e10))))
  expect_true(is.finite(your_metric_vec(c(1e-10, 2e-10), c(1.1e-10, 2.1e-10))))
})
```

### Testing Best Practices

#### Use expect_snapshot()

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

#### Write meaningful test names

```r
# Good: descriptive test names
test_that("calculations are correct for binary classification", { ... })
test_that("NA values are removed when na_rm = TRUE", { ... })

# Bad: vague test names
test_that("works", { ... })
test_that("test 1", { ... })
```

#### Minimal comments

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

#### Use precise expectations

```r
# Good: specific expectations
expect_equal(result, 0.5)
expect_s3_class(result, "tbl_df")
expect_identical(result1, result2)

# Avoid: imprecise expectations
expect_true(result == 0.5)  # Use expect_equal instead
expect_true(is.data.frame(result))  # Use expect_s3_class instead
```

#### Tolerance for floating point

```r
# For floating point comparisons
expect_equal(result, expected, tolerance = 1e-7)

# For exact matches (integers, strings)
expect_identical(result, expected)
```

### Running Tests

#### Run all tests

```r
devtools::test()
```

#### Run specific test file

```r
devtools::test_active_file()  # Current file in RStudio
devtools::test_file("tests/testthat/test-yourfile.R")
```

#### Run tests matching pattern

```r
devtools::test(filter = "your_function")
```

#### Skip slow tests during development

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

### Test Coverage

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

---

