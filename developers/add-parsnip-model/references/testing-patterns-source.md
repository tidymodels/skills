# Testing Patterns for Parsnip Model Source Development

Testing strategies specifically for contributing new models to the parsnip
package (source development).

--------------------------------------------------------------------------------

## Overview

When contributing models to parsnip source, testing requirements are more
comprehensive than for extensions. You have access to parsnip's internal test
infrastructure and must follow established patterns.

**Key differences from extension testing:**

- Use snapshot testing for errors and output

- Direct access to test helpers

- More extensive edge case coverage

- Organized by model and engine

--------------------------------------------------------------------------------

## Test File Organization

### File Naming Conventions

**Model constructor tests:** ```
tests/testthat/test-my_model.R
```

**Engine-specific tests (if complex):**
```
tests/testthat/test-my_model-custom.R
tests/testthat/test-my_model-glmnet.R
```

**General structure:**

- One file per model type

- Separate files for complex engines (optional)

- Group related tests with comment separators

--------------------------------------------------------------------------------

## Required Test Categories

### 1. Constructor Tests

Test that model specification is created correctly:

```r
test_that("my_model constructor creates valid object", {
  spec <- my_model()

  expect_s3_class(spec, "my_model")
  expect_s3_class(spec, "model_spec")
  expect_equal(spec$mode, "unknown")
  expect_null(spec$engine)
})

test_that("my_model accepts arguments", {
  spec <- my_model(penalty = 0.1, mixture = 0.5)

  expect_true(rlang::is_quosure(spec$args$penalty))
  expect_equal(rlang::eval_tidy(spec$args$penalty), 0.1)

  expect_true(rlang::is_quosure(spec$args$mixture))
  expect_equal(rlang::eval_tidy(spec$args$mixture), 0.5)
})

test_that("my_model tracks user specifications", {
  spec1 <- my_model()
  expect_false(spec1$user_specified_mode)
  expect_false(spec1$user_specified_engine)

  spec2 <- my_model(mode = "regression")
  expect_true(spec2$user_specified_mode)

  spec3 <- my_model() |> set_engine("custom")
  expect_true(spec3$user_specified_engine)
})
```

### 2. Mode Validation Tests

Test mode handling and validation:

```r
test_that("my_model validates mode", {
  expect_snapshot(
    my_model(mode = "invalid"),
    error = TRUE
  )
})

test_that("my_model accepts valid modes", {
  expect_no_error(my_model(mode = "regression"))
  expect_no_error(my_model(mode = "classification"))
})

test_that("set_mode works", {
  spec <- my_model() |> set_mode("regression")
  expect_equal(spec$mode, "regression")

  spec <- spec |> set_mode("classification")
  expect_equal(spec$mode, "classification")
})
```

### 3. Printing Tests

Use snapshot tests for printed output:

```r
test_that("printing works", {
  expect_snapshot(my_model())
  expect_snapshot(my_model(mode = "regression"))
  expect_snapshot(my_model(penalty = 0.1, mixture = 0.5))

  spec <- my_model(mode = "regression") |> set_engine("custom")
  expect_snapshot(spec)
})
```

### 4. Fitting Tests

Test that models fit successfully:

```r
test_that("my_model fits with formula interface", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")
  expect_s3_class(fit$fit, "lm")  # Underlying fit object
})

test_that("my_model fits with xy interface", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")
  fit <- fit_xy(spec, x = mtcars[, -1], y = mtcars$mpg)

  expect_s3_class(fit, "model_fit")
})

test_that("formula and xy interfaces give same results", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")

  fit_formula <- fit(spec, mpg ~ hp + wt, data = mtcars)
  fit_xy <- fit_xy(spec, x = mtcars[, c("hp", "wt")], y = mtcars$mpg)

  pred_formula <- predict(fit_formula, mtcars[1:5, ])
  pred_xy <- predict(fit_xy, mtcars[1:5, ])

  expect_equal(pred_formula, pred_xy, tolerance = 1e-5)
})
```

### 5. Prediction Tests

Test all prediction types:

```r
test_that("my_model numeric predictions", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  preds <- predict(fit, new_data = mtcars[1:5, ])

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
  expect_type(preds$.pred, "double")
})

test_that("my_model class predictions", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "classification") |> set_engine("custom")

  data <- data.frame(
    y = factor(rep(c("A", "B"), each = 10)),
    x1 = rnorm(20),
    x2 = rnorm(20)
  )

  fit <- fit(spec, y ~ ., data = data)
  preds <- predict(fit, new_data = data[1:5, ])

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred_class")
  expect_s3_class(preds$.pred_class, "factor")
  expect_equal(nrow(preds), 5)
})

test_that("my_model probability predictions", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "classification") |> set_engine("custom")

  data <- data.frame(
    y = factor(rep(c("A", "B"), each = 10)),
    x1 = rnorm(20),
    x2 = rnorm(20)
  )

  fit <- fit(spec, y ~ ., data = data)
  preds <- predict(fit, new_data = data[1:5, ], type = "prob")

  expect_s3_class(preds, "tbl_df")
  expect_true(all(grepl("^\\.pred_", names(preds))))
  expect_equal(ncol(preds), 2)  # Binary classification
  expect_equal(nrow(preds), 5)

  # Check probabilities sum to 1
  row_sums <- rowSums(preds)
  expect_equal(row_sums, rep(1, 5), tolerance = 1e-10)
})

test_that("my_model raw predictions", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  preds_raw <- predict(fit, mtcars[1:5, ], type = "raw")

  expect_type(preds_raw, "double")
  expect_equal(length(preds_raw), 5)
})
```

### 6. Edge Case Tests

Test boundary conditions and unusual inputs:

```r
test_that("my_model handles single row prediction", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  preds <- predict(fit, mtcars[1, ])

  expect_equal(nrow(preds), 1)
  expect_named(preds, ".pred")
})

test_that("my_model handles factor predictors", {
  skip_if_not_installed("stats")

  data <- mtcars
  data$cyl <- factor(data$cyl)

  spec <- my_model(mode = "regression") |> set_engine("custom")
  fit <- fit(spec, mpg ~ cyl + hp, data = data)

  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, data[1:5, ])
  expect_equal(nrow(preds), 5)
})

test_that("my_model errors on incompatible mode-type combinations", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_snapshot(
    predict(fit, mtcars, type = "prob"),
    error = TRUE
  )
})
```

### 7. Integration Tests

Test integration with tidymodels ecosystem:

```r
test_that("my_model works with workflows", {
  skip_if_not_installed("workflows")
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")

  wf <- workflows::workflow() |>
    workflows::add_formula(mpg ~ .) |>
    workflows::add_model(spec)

  fit <- fit(wf, data = mtcars)
  preds <- predict(fit, mtcars[1:5, ])

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
})

test_that("my_model works with recipes", {
  skip_if_not_installed("workflows")
  skip_if_not_installed("recipes")
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")

  rec <- recipes::recipe(mpg ~ ., data = mtcars) |>
    recipes::step_normalize(recipes::all_numeric_predictors())

  wf <- workflows::workflow() |>
    workflows::add_recipe(rec) |>
    workflows::add_model(spec)

  fit <- fit(wf, data = mtcars)
  preds <- predict(fit, mtcars[1:5, ])

  expect_equal(nrow(preds), 5)
})
```

--------------------------------------------------------------------------------

## Snapshot Testing Patterns

### Error Messages

Always use snapshots for error messages:

```r
test_that("informative errors for invalid mode", {
  expect_snapshot(
    my_model(mode = "invalid"),
    error = TRUE
  )
})

test_that("informative errors for invalid engine", {
  spec <- my_model(mode = "regression")

  expect_snapshot(
    set_engine(spec, "nonexistent"),
    error = TRUE
  )
})

test_that("informative errors for missing required args", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")

  expect_snapshot(
    fit(spec, mpg ~ ., data = NULL),
    error = TRUE
  )
})
```

### Printed Output

Snapshot printed model specifications:

```r
test_that("print method works", {
  # Default
  expect_snapshot(print(my_model()))

  # With mode
  expect_snapshot(print(my_model(mode = "regression")))

  # With arguments
  expect_snapshot(print(my_model(penalty = 0.1, mixture = 0.5)))

  # After set_engine
  spec <- my_model(mode = "regression") |> set_engine("custom")
  expect_snapshot(print(spec))
})
```

--------------------------------------------------------------------------------

## Multi-Mode Testing

Test each mode separately:

```r
# ------------------------------------------------------------------------------
# Regression mode

test_that("my_model regression mode fits", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, mtcars[1:5, ])
  expect_named(preds, ".pred")
})

# ------------------------------------------------------------------------------
# Classification mode

test_that("my_model classification mode fits", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "classification") |> set_engine("custom")

  data <- data.frame(
    y = factor(rep(c("A", "B"), each = 10)),
    x1 = rnorm(20),
    x2 = rnorm(20)
  )

  fit <- fit(spec, y ~ ., data = data)

  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, data[1:5, ])
  expect_named(preds, ".pred_class")
})
```

--------------------------------------------------------------------------------

## Multi-Engine Testing

If model supports multiple engines, test each:

```r
# ------------------------------------------------------------------------------
# lm engine

test_that("my_model with lm engine", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("lm")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit$fit, "lm")
})

# ------------------------------------------------------------------------------
# glmnet engine

test_that("my_model with glmnet engine", {
  skip_if_not_installed("glmnet")

  spec <- my_model(mode = "regression", penalty = 0.1) |>
    set_engine("glmnet")

  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit$fit, "glmnet")
})
```

--------------------------------------------------------------------------------

## Using Test Helpers

### Available Helpers

From `tests/testthat/helper-objects.R`:

```r
# Test data
hpc           # Classification data
lending_club  # More classification data
mtcars        # Regression data

# Fitted models
lm_fit        # Simple lm fit
glm_fit       # Logistic regression fit

# Control objects
ctrl          # Standard control
quiet_ctrl    # Suppress output
caught_ctrl   # Capture warnings/errors
```

### Using Helpers

```r
test_that("my_model works with standard test data", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |> set_engine("custom")

  # Use standard mtcars
  fit <- fit(spec, mpg ~ ., data = mtcars)
  expect_s3_class(fit, "model_fit")
})
```

--------------------------------------------------------------------------------

## Test Organization Pattern

Organize tests with clear sections:

```r
# tests/testthat/test-my_model.R

# ------------------------------------------------------------------------------
# Model constructor

test_that("constructor works", { ... })
test_that("validates arguments", { ... })

# ------------------------------------------------------------------------------
# Mode handling

test_that("mode validation", { ... })
test_that("set_mode works", { ... })

# ------------------------------------------------------------------------------
# Regression mode - custom engine

test_that("fits with formula", { ... })
test_that("fits with xy", { ... })
test_that("numeric predictions", { ... })
test_that("raw predictions", { ... })

# ------------------------------------------------------------------------------
# Classification mode - custom engine

test_that("fits with formula", { ... })
test_that("class predictions", { ... })
test_that("prob predictions", { ... })

# ------------------------------------------------------------------------------
# Integration

test_that("works with workflows", { ... })
test_that("works with recipes", { ... })

# ------------------------------------------------------------------------------
# Edge cases

test_that("single row", { ... })
test_that("factors", { ... })
test_that("errors", { ... })
```

--------------------------------------------------------------------------------

## Coverage Requirements

Aim for comprehensive coverage:

**Essential coverage:**

- ✅ All modes

- ✅ All engines

- ✅ All prediction types

- ✅ Both fit interfaces (formula and xy)

- ✅ Error conditions

- ✅ Edge cases

**Check coverage:**

```r
covr::package_coverage()
```

--------------------------------------------------------------------------------

## Common Test Patterns

### Pattern 1: Skip If Package Not Available

```r
test_that("my_model with custom engine", {
  skip_if_not_installed("custompackage")

  # Test code
})
```

### Pattern 2: Expect Equal with Tolerance

For numerical comparisons:

```r
expect_equal(pred_formula, pred_xy, tolerance = 1e-5)
```

### Pattern 3: Snapshot Errors

```r
expect_snapshot(
  my_model(mode = "invalid"),
  error = TRUE
)
```

### Pattern 4: Check Column Names

```r
expect_named(preds, ".pred")
expect_true(all(grepl("^\\.pred_", names(preds))))
```

--------------------------------------------------------------------------------

## Testing Checklist

Before submitting PR:

- [ ] Constructor creates valid object

- [ ] All modes tested

- [ ] All engines tested

- [ ] All prediction types tested

- [ ] Both fit() and fit_xy() tested

- [ ] Formula and xy give same results

- [ ] Single row predictions work

- [ ] Factor predictors handled

- [ ] Error messages have snapshots

- [ ] Print method has snapshots

- [ ] Works with workflows

- [ ] Works with recipes

- [ ] Edge cases covered

- [ ] All tests pass

- [ ] Good test coverage (>90%)

--------------------------------------------------------------------------------

## Debugging Failed Tests

### Check Test Output

```r
# Run specific test
devtools::test_file("tests/testthat/test-my_model.R")

# Run single test
devtools::test_file("tests/testthat/test-my_model.R", filter = "constructor")
```

### Interactive Debugging

```r
# Run test interactively
testthat::test_file("tests/testthat/test-my_model.R", reporter = "stop")

# Or use browser()
test_that("debugging test", {
  spec <- my_model()
  browser()  # Stops here
  fit <- fit(spec, mpg ~ ., mtcars)
})
```

### Update Snapshots

If error messages change intentionally:

```r
# Review changes
testthat::snapshot_review()

# Accept changes
testthat::snapshot_accept()
```

--------------------------------------------------------------------------------

## Additional Resources

**Test examples in parsnip:**

- `tests/testthat/test-linear_reg.R` - Simple model tests

- `tests/testthat/test-boost_tree.R` - Multi-mode tests

- `tests/testthat/helper-objects.R` - Available helpers

**Related guides:**

- [Best Practices (Source)](best-practices-source.md) - Code conventions

- [Troubleshooting (Source)](troubleshooting-source.md) - Common issues
