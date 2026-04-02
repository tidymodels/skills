# Extension Development Requirements

**Context:** This guide is for **extension development** - creating new packages that extend tidymodels packages like yardstick or recipes.

**Key principle:** ❌ **Never use internal functions** (accessed with `:::`) - they are not guaranteed to be stable and will cause CRAN check failures.

For source development (contributing to tidymodels packages directly), see the package-specific source guides.

---

Complete requirements for developing high-quality R package extensions to tidymodels packages. This guide covers best practices, testing, and troubleshooting in one place.

## Table of Contents

1. [Best Practices](#best-practices)

   - [Code Style](#code-style)

   - [Error Messages](#error-messages)

   - [Documentation Standards](#documentation-standards)

   - [Performance](#performance)

   - [Code Validation](#code-validation)

   - [Memory Management](#memory-management)

   - [Code Formatting](#code-formatting)

   - [Version Control](#version-control)

2. [Testing Requirements](#testing-requirements)

   - [Test File Organization](#test-file-organization)

   - [Creating Test Data](#creating-test-data)

   - [Standard Test Categories](#standard-test-categories)

   - [Integration Tests](#integration-tests)

   - [Infrastructure Tests](#infrastructure-tests-required-for-recipe-steps)

   - [Edge Case Tests](#edge-case-tests)

   - [Best Practices](#testing-best-practices)

   - [Running Tests](#running-tests)

   - [Test Coverage](#test-coverage)

3. [Common Issues & Solutions](#common-issues-solutions)

   - [Build and Check Issues](#build-and-check-issues)

   - [Function and Object Errors](#function-and-object-errors)

   - [Testing Errors](#testing-errors)

   - [Documentation Errors](#documentation-errors)

   - [Method and S3 Errors](#method-and-s3-errors)

   - [Custom Parameter Issues](#custom-parameter-issues)

   - [Dependency Issues](#dependency-issues)

   - [Performance Issues](#performance-issues)

   - [Memory Issues](#memory-issues)

   - [Git and Workflow Issues](#git-and-workflow-issues)

   - [Getting Help](#getting-help)

4. [Quick Reference](#quick-reference)

---

## Best Practices

Guide to writing high-quality R code for tidymodels extension packages.

### Code Style

#### Use base pipe

```r
# Good
recipe(mpg ~ ., data = mtcars) |>
  step_center(all_numeric_predictors())

# Avoid
recipe(mpg ~ ., data = mtcars) %>%
  step_center(all_numeric_predictors())
```

The base pipe `|>` is faster, built-in, and the tidymodels standard.

#### Anonymous functions

```r
# Single line: use backslash notation
map(x, \(i) i + 1)

# Multi-line: use function()
map(x, function(i) {
  result <- complex_computation(i)
  result + 1
})
```

#### For-loops over map()

```r
# Preferred (better error messages)
for (col in columns) {
  new_data[[col]] <- transform(new_data[[col]])
}

# Avoid (harder to debug)
new_data <- map(columns, \(col) transform(new_data[[col]]))
```

**Why prefer for-loops:**

- Better error messages (shows which iteration failed)

- More familiar to most R users

- Easier to debug with `browser()`

- Consistent with tidymodels style

#### Minimal comments

```r
# Good: code is self-documenting
means <- colMeans(data)
centered <- sweep(data, 2, means, "-")

# Avoid: over-commenting obvious code
# Calculate column means
means <- colMeans(data)
# Subtract means from each column
centered <- sweep(data, 2, means, "-")
```

Write clear code that doesn't need comments. Add comments only for:

- Complex algorithms

- Non-obvious optimization tricks

- Warnings about edge cases

### Error Messages

#### Use cli functions

```r
# Good: cli provides better formatting
if (invalid) {
  cli::cli_abort("{.arg param} must be positive, not {.val {param}}.")
}

if (risky) {
  cli::cli_warn("Column{?s} {.var {col_names}} returned Inf or NaN.")
}

# Avoid: base R error functions
stop("param must be positive")
warning("columns returned Inf or NaN")
```

#### cli formatting syntax

```r
# Argument names
cli::cli_abort("{.arg your_param} must be numeric.")

# Code/function names
cli::cli_abort("Use {.code binary} estimator for two classes.")

# Values
cli::cli_abort("Expected 3 columns, got {.val {ncol(data)}}.")

# Variable names
cli::cli_warn("Column{?s} {.var {col_names}} has/have missing values.")

# Pluralization
cli::cli_abort("Found {length(x)} error{?s}.")  # Handles 1 vs many
```

#### Error message guidelines

- Be specific about what's wrong

- Tell users what they can do to fix it

- Include actual values when helpful

- Use proper English grammar

```r
# Good
cli::cli_abort(
  "{.arg threshold} must be between 0 and 1, not {.val {threshold}}."
)

# Avoid
stop("Invalid threshold")
```

### Documentation Standards

#### Be explicit

```r
#' @param threshold Threshold value for classification. Must be a numeric
#'   value between 0 and 1. Default is 0.5.
```

**Include:**

- Type (numeric, logical, character, factor)

- Valid range or options

- Default value

- Effect on function behavior

#### US English

- Use American spelling: "normalize" not "normalise"

- Use sentence case: "Calculate the mean" not "calculate the mean"

- Be consistent throughout

#### Wrap roxygen at 80 characters

```r
#' This is a long line that should be wrapped to ensure it doesn't exceed the
#' 80-character limit for better readability in various text editors.
```

#### Include practical examples

```r
#' @examples
#' # Basic usage
#' metric_name(data, truth, estimate)
#'
#' # With grouped data
#' data |>
#'   dplyr::group_by(fold) |>
#'   metric_name(truth, estimate)
```

Show realistic use cases, not just minimal examples.

#### Don't use dynamic roxygen code

```r
# Bad: calling non-exported functions
#' @return Range: `r metric_range()`  # metric_range() not exported

# Good: static documentation
#' @return Range: 0 to 1
```

### Performance

#### Vectorization over loops

**Always prefer vectorized operations:**

```r
# Good: vectorized
errors <- truth - estimate
squared_errors <- errors^2
mean(squared_errors)

# Bad: loop
total <- 0
for (i in seq_along(truth)) {
  total <- total + (truth[i] - estimate[i])^2
}
total / length(truth)
```

**Vectorized functions:**

- Arithmetic: `+`, `-`, `*`, `/`, `^`

- Comparisons: `==`, `!=`, `>`, `<`, `>=`, `<=`

- Logical: `&`, `|`, `!`

- Math: `abs()`, `sqrt()`, `log()`, `exp()`, `sin()`, `cos()`

- Aggregations: `sum()`, `mean()`, `max()`, `min()`, `median()`

#### Use matrix operations

**Efficient per-class calculations:**

```r
# Good: matrix operations
confusion_matrix <- yardstick_table(truth, estimate)
tp <- diag(confusion_matrix)
fp <- colSums(confusion_matrix) - tp
fn <- rowSums(confusion_matrix) - tp

# Bad: looping over classes
tp <- numeric(n_classes)
for (i in seq_len(n_classes)) {
  tp[i] <- confusion_matrix[i, i]
}
```

**Use `colSums()` and `rowSums()`:**
```r
# Good
class_totals <- colSums(confusion_matrix)

# Avoid
class_totals <- apply(confusion_matrix, 2, sum)  # Slower
```

#### Avoid repeated computations

**General principle:** Calculate once, use many times.

```r
# Good: compute once in prep() for recipe steps
prep.step_yourname <- function(x, training, ...) {
  means <- colMeans(training[col_names])  # Computed once, stored
}

# Good: validate once at entry point
metric_vec <- function(truth, estimate, ...) {
  check_numeric_metric(truth, estimate, case_weights)  # Validate once
  metric_impl(truth, estimate, ...)  # Trust the data
}

# Good: pre-compute before loops
levels_list <- levels(truth)
n_levels <- length(levels_list)
for (i in seq_len(n_levels)) {
  # Use pre-computed values
}

# Bad: recomputing unnecessarily
for (i in seq_len(length(levels(truth)))) {
  levels_list <- levels(truth)  # Redundant!
}
```

#### Handle case weights efficiently

**Convert hardhat weights once:**

```r
# Good: convert once at the start
if (!is.null(case_weights)) {
  if (inherits(case_weights, c("hardhat_importance_weights",
                               "hardhat_frequency_weights"))) {
    case_weights <- as.double(case_weights)
  }
  # Now use case_weights multiple times
}

# Bad: converting repeatedly
if (!is.null(case_weights)) {
  result1 <- weighted.mean(x, as.double(case_weights))
  result2 <- weighted.mean(y, as.double(case_weights))  # Converting again!
}
```

#### Profile before optimizing

**Focus optimization where it matters:**

1. Start with clear, correct code
2. Profile with `profvis::profvis()` if performance is an issue
3. Optimize the actual bottlenecks
4. Don't prematurely optimize

```r
# Profile your code
profvis::profvis({
  for (i in 1:100) {
    your_function(data)
  }
})
```

#### When performance doesn't matter

**Don't optimize unnecessarily:**

- Functions typically called once or few times per evaluation

- Calculation is usually fast compared to model fitting

- Readability and correctness are more important

**Do optimize when:**

- Function called thousands of times (tuning, cross-validation)

- Working with very large datasets (millions of observations)

- Profiling shows the function is the bottleneck

### Code Validation

#### Validate early

```r
step_yourname <- function(recipe, ..., your_param = 1) {
  # Validate parameters early
  if (!is.numeric(your_param) || your_param <= 0) {
    cli::cli_abort("{.arg your_param} must be a positive number.")
  }

  # ... rest of function
}

prep.step_yourname <- function(x, training, ...) {
  # Validate data early
  col_names <- recipes_eval_select(x$terms, training, info)
  check_type(training[, col_names], types = c("double", "integer"))

  # ... rest of function
}
```

#### Give actionable error messages

```r
# Good: tells user what to do
cli::cli_abort(
  "Columns {.var {bad_cols}} must be numeric.
  Convert to numeric with {.code as.numeric()}."
)

# Avoid: vague errors
stop("Invalid columns")
```

### Memory Management

#### Don't store entire datasets

```r
# Good: store only necessary parameters
prep.step_center <- function(x, training, ...) {
  means <- colMeans(training[col_names])  # Just means, not data
  # Return step with means stored
}

# Bad: storing entire training set
prep.step_center <- function(x, training, ...) {
  # Return step with training data stored (memory leak!)
}
```

#### Consider memory usage for large data

- Store statistics/parameters, not raw data

- Use sparse matrices when appropriate

- Consider memory-mapped files for very large data

### Code Formatting

After writing code, format it:

```r
# Format current package
air::air_format(".")
```

Or use RStudio: Code → Reformat Code (Cmd/Ctrl + Shift + A)

### Version Control

#### Commit messages

```r
# Good: descriptive commits
"Add support for multiclass metrics"
"Fix NA handling in case weights"
"Update documentation examples"

# Avoid: vague commits
"Fix bug"
"Update code"
"Changes"
```

#### Commit frequency

- Commit after each logical unit of work

- Commit working, tested code

- Don't commit broken code (except on branches)

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

## Common Issues & Solutions

Common issues and solutions when developing tidymodels extension packages.

### Build and Check Issues

#### "Non-standard files/directories found"

**Symptom:**
```
* checking top-level files ... NOTE
Non-standard files/directories found at top level:
  '.claude' '.here' 'example.R'
```

**Cause:** Hidden files or example files not excluded from package build

**Solution:** Set up `.Rbuildignore`:

```r
# Add common exclusions to .Rbuildignore
writeLines(c(
  "^\\.here$",
  "^\\.claude$",
  "^example.*\\.R$",
  "^.*\\.Rproj$",
  "^\\.Rproj\\.user$"
), ".Rbuildignore", useBytes = TRUE)
```

Or manually edit `.Rbuildignore` to include these patterns.

See [package-extension-prerequisites.md](package-extension-prerequisites.md) for details.

#### "No visible global function definition"

**Symptom:**
```
checking R code for possible problems ... NOTE
  your_function: no visible global function definition for 'weighted.mean'
  Undefined global functions or variables:
    weighted.mean
```

**Cause:** Using function from base/stats without importing

**Solution:** Add package-level documentation file:

Create `R/{packagename}-package.R`:
```r
#' @keywords internal
#' @importFrom stats weighted.mean
"_PACKAGE"

## usethis namespace: start
## usethis namespace: end
NULL
```

Then run `devtools::document()`.

See [package-imports.md](package-imports.md) for details.

#### "No visible binding for global variable"

**Symptom:**
```
checking R code for possible problems ... NOTE
  your_function: no visible binding for global variable 'column_name'
```

**Cause:** Using NSE variables (common with dplyr/ggplot2) without declaring them

**Solution:** Use `.data` pronoun or declare globals:

**Option 1: Use .data pronoun (preferred)**
```r
dplyr::mutate(data, new_col = .data$column_name * 2)
```

**Option 2: Declare global variables**
```r
# In R/{packagename}-package.R
utils::globalVariables(c("column_name", "another_column"))
```

### Function and Object Errors

#### Function not found or not exported

**Symptoms:**
```
Error: could not find function "your_function"
Error: 'your_function' is not an exported object from 'namespace:yourpackage'
```

**Cause:** Missing `@export` tag or namespace not updated

**Solution:**
```r
# 1. Add @export to your roxygen block
#' @export
your_function <- function() { ... }

# 2. Update namespace and load
devtools::document()
devtools::load_all()
```

#### Internal functions not available

**Symptoms:**
```
Error: could not find function "yardstick_mean"
Error: 'internal_function' is not exported by 'namespace:yardstick'
```

**Cause:** Trying to use internal functions (not exported)

**Solution:** Use exported alternatives or implement yourself:

```r
# Instead of yardstick_mean() - NOT EXPORTED
if (is.null(case_weights)) {
  mean(values)
} else {
  weighted.mean(values, w = as.double(case_weights))
}
```

See yardstick skill for list of internal vs exported functions.

### Testing Errors

#### Tests fail with "object 'data_altman' not found"

**Symptom:**
```
Error: object 'data_altman' not found
```

**Cause:** Using yardstick internal test data

**Solution:** Create simple test data inline:

```r
# Don't rely on internal helpers
# data <- data_altman()  # NOT EXPORTED

# Create your own test data
test_data <- data.frame(
  truth = c(1, 2, 3, 4, 5),
  estimate = c(1.1, 2.2, 2.9, 4.1, 4.8)
)
```

#### "Could not find function in tests"

**Symptom:**
```
Error in test: could not find function "your_function"
```

**Cause:** Package not loaded before running tests

**Solution:**
```r
# Load package before testing
devtools::load_all()
devtools::test()
```

#### Tests pass locally but fail in check()

**Symptom:** Tests work with `devtools::test()` but fail with `devtools::check()`

**Cause:** Test relies on local environment

**Solution:** Make tests self-contained:

- Don't assume specific working directory

- Don't rely on installed packages not in DESCRIPTION

- Don't use external files without checking they exist

#### Floating point comparison failures

**Problem:** Exact equality fails for floating point

**Solution:** Use tolerance
```r
expect_equal(result, expected, tolerance = 1e-7)
```

#### Snapshot tests fail after updating

**Problem:** Output changed (expected or unexpected)

**Solution:** Review changes, update snapshots if correct
```r
# In test file, after verifying change is correct
testthat::snapshot_accept()
```

#### Tests are slow

**Solution:**

- Use smaller test datasets

- Skip slow tests with `skip_if_not(interactive())`

- Profile tests to find bottlenecks

### Documentation Errors

#### "Cannot find template 'return'"

**Symptom:**
```
Error: Cannot find template 'return'
```

**Cause:** Using `@template return` which doesn't exist in your package

**Solution:** Use explicit `@return` documentation:

```r
# Don't use @template
#' @template return  # Won't work

# Use explicit documentation
#' @return A tibble with columns `.metric`, `.estimator`, and `.estimate`
```

#### "Link to unknown function"

**Symptom:**
```
Warning: Link to unknown function 'some_function'
```

**Cause:** Documentation references function that doesn't exist or isn't imported

**Solution:**

- Check spelling

- Make sure function is exported

- Link to correct package: `[package::function()]`

### Method and S3 Errors

#### "No applicable method"

**Symptom:**
```
Error: no applicable method for 'metric_name' applied to an object of class "data.frame"
```

**Cause:** Calling `UseMethod()` after `new_*_metric()` or data.frame method not defined

**Solution:** Correct order:

```r
# Correct order
metric_name <- function(data, ...) {
  UseMethod("metric_name")  # First
}

metric_name <- new_numeric_metric(  # Second
  metric_name,
  direction = "minimize",
  range = c(0, Inf)
)

#' @export
#' @rdname metric_name
metric_name.data.frame <- function(data, truth, estimate, ...) {  # Third
  # Implementation
}
```

### Custom Parameter Issues

#### "Can't find custom parameter in _vec function"

**Symptom:**
```
Error in metric_vec: argument "threshold" is missing, with no default
```

**Cause:** Custom parameters not passed through `fn_options`

**Solution:** Pass custom parameters via `fn_options`:

```r
#' @export
metric_name.data.frame <- function(data, truth, estimate, threshold = 0.5, ...) {
  numeric_metric_summarizer(
    name = "metric_name",
    fn = metric_name_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    fn_options = list(threshold = threshold)  # Pass custom parameter here
  )
}
```

### Dependency Issues

Common dependency problems and solutions:

**Package not available:**
```r
# Install missing package
install.packages("xxx")

# Or add to DESCRIPTION
usethis::use_package("xxx")
```

**Unused dependencies:**

- "Namespace dependencies not required" → Remove unused imports from package-level doc

- "All declared Imports should be used" → Remove from DESCRIPTION or add `@importFrom`

Then run `devtools::document()` to update NAMESPACE

### Performance Issues

#### Slow test runs

**Problem:** Tests take too long during development

**Solution:**
```r
# Run only one test file
devtools::test_active_file()

# Run only tests matching a pattern
devtools::test(filter = "your_function")

# Skip slow tests during development
test_that("slow integration test", {
  skip_if_not(interactive(), "Slow test - run manually")

  # Expensive test here
})
```

#### Slow check()

**Problem:** `devtools::check()` takes too long

**Reminder:** Don't run `check()` during development!

Use the fast iteration cycle instead:
```r
devtools::document()  # Fast
devtools::load_all()  # Fast
devtools::test()      # Fast (seconds to minutes)
```

Only run `check()` once at the very end.

See [package-development-workflow.md](package-development-workflow.md) for details.

### Memory Issues

#### "Cannot allocate vector of size"

**Problem:** Running out of memory

**Solution:**

- Don't store entire datasets in objects

- Store only necessary parameters/statistics

- Consider sparse matrices for appropriate data

- Process data in chunks if necessary

### Git and Workflow Issues

#### Pre-commit hook fails

**Problem:** Commit fails due to hook

**Solution:** Fix the underlying issue, don't skip hooks:

```r
# DON'T skip hooks
git commit --no-verify  # Bad practice

# DO fix the issue
# - Fix linting errors
# - Fix test failures
# - Then commit normally
```

#### Accidentally committed sensitive files

**Problem:** Committed .env or credentials

**Solution:**
1. Remove from git history (complex, search online)
2. Add to .gitignore
3. Rotate compromised credentials immediately

**Prevention:** Set up .gitignore properly from the start

### Getting Help

#### Built-in help

```r
# View function documentation
?your_function

# View package documentation
help(package = "yourpackage")

# Search documentation
??search_term
```

#### Package debugging

```r
# View function source
your_function

# Debug function
debug(your_function)
your_function(test_data)  # Will pause at start

# Add breakpoint
browser()  # Add this line in function code
```

#### External resources

- [R Packages book](https://r-pkgs.org/) - Comprehensive guide

- [Tidymodels developer guide](https://www.tidymodels.org/learn/develop/)

- Package documentation (yardstick, recipes, etc.)

- Stack Overflow with tag `[r]`

- RStudio Community

#### When to ask for help

After you've:
1. Read relevant documentation
2. Searched for similar issues
3. Created a minimal reproducible example
4. Tried suggested solutions

#### Creating a reproducible example

```r
# Install reprex package
install.packages("reprex")

# Copy your code to clipboard
# Then run:
reprex::reprex()

# Paste the output when asking for help
```

---

## Quick Reference

### Development Checklist

#### Before First Commit

- [ ] All functions documented with roxygen2

- [ ] Tests written for all exported functions

- [ ] `devtools::document()` runs without errors

- [ ] `devtools::load_all()` loads successfully

- [ ] `devtools::test()` passes all tests

- [ ] Code follows tidymodels style (base pipe, for-loops, cli errors)

#### Before Release

- [ ] `devtools::check()` passes with no errors, warnings, or notes

- [ ] All examples run successfully

- [ ] Test coverage at 90%+

- [ ] NEWS.md updated

- [ ] Version bumped in DESCRIPTION

### Essential Commands

```r
# Fast development cycle (run repeatedly)
devtools::document()  # Update docs and NAMESPACE
devtools::load_all()  # Load package
devtools::test()      # Run tests

# Once at the end
devtools::check()     # Full R CMD check (slow)

# Debugging
debug(function_name)  # Step through function
browser()            # Add breakpoint in code
```

### Next Steps

- Complete setup: [package-extension-prerequisites.md](package-extension-prerequisites.md)

- Follow workflow: [package-development-workflow.md](package-development-workflow.md)

- Document functions: [package-roxygen-documentation.md](package-roxygen-documentation.md)

- Manage dependencies: [package-imports.md](package-imports.md)
