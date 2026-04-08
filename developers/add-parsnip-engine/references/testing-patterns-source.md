# Testing Patterns for Parsnip Engine Source Development

Testing strategies for contributing engines to the parsnip package (source
development).

--------------------------------------------------------------------------------

## Overview

When contributing engines to parsnip source, testing focuses on engine-specific
behavior rather than model constructor patterns (since the model type already
exists).

**Key testing areas:**

- Engine registration and setup

- Fit interface compatibility (formula vs matrix vs xy)

- All prediction types the engine supports

- Engine-specific argument handling

- Edge cases and error conditions

--------------------------------------------------------------------------------

## Test File Organization

### File Naming

**Engine tests go in existing model test files:**
```
tests/testthat/test-linear_reg.R    # Add glmnet engine tests here
tests/testthat/test-boost_tree.R    # Add lightgbm engine tests here
```

**Or create engine-specific files for complex engines:**
```
tests/testthat/test-linear_reg-glmnet.R
tests/testthat/test-boost_tree-lightgbm.R
```

--------------------------------------------------------------------------------

## Required Test Categories

### 1. Engine Setup Tests

Verify engine can be selected and configured:

```r
test_that("linear_reg can use glmnet engine", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg() |> set_engine("glmnet")

  expect_equal(spec$engine, "glmnet")
  expect_s3_class(spec, "linear_reg")
})

test_that("glmnet engine accepts engine-specific arguments", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg() |>
    set_engine("glmnet", nlambda = 50, thresh = 1e-10)

  expect_equal(spec$eng_args$nlambda, 50)
  expect_equal(spec$eng_args$thresh, 1e-10)
})
```

### 2. Fit Interface Tests

Test all interfaces the engine supports:

```r
test_that("glmnet engine fits with formula interface", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")
  expect_s3_class(fit$fit, "glmnet")
})

test_that("glmnet engine fits with xy interface", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")
  fit <- fit_xy(spec, x = mtcars[, -1], y = mtcars$mpg)

  expect_s3_class(fit, "model_fit")
  expect_s3_class(fit$fit, "glmnet")
})

test_that("formula and xy interfaces give equivalent results", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")

  fit_formula <- fit(spec, mpg ~ hp + wt, data = mtcars)
  fit_xy <- fit_xy(spec, x = mtcars[, c("hp", "wt")], y = mtcars$mpg)

  pred_formula <- predict(fit_formula, mtcars[1:5, ])
  pred_xy <- predict(fit_xy, mtcars[1:5, ])

  expect_equal(pred_formula, pred_xy, tolerance = 1e-5)
})
```

### 3. Prediction Type Tests

Test each prediction type the engine supports:

**Regression predictions:**

```r
test_that("glmnet numeric predictions", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  preds <- predict(fit, mtcars[1:5, ])

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
  expect_type(preds$.pred, "double")
})

test_that("glmnet raw predictions", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  preds <- predict(fit, mtcars[1:5, ], type = "raw")

  expect_type(preds, "double")
  expect_true(is.matrix(preds))
})
```

**Classification predictions:**

```r
test_that("glmnet class predictions", {
  skip_if_not_installed("glmnet")

  spec <- logistic_reg(penalty = 0.1) |> set_engine("glmnet")

  data <- data.frame(
    y = factor(rep(c("A", "B"), each = 10)),
    x1 = rnorm(20),
    x2 = rnorm(20)
  )

  fit <- fit(spec, y ~ ., data = data)
  preds <- predict(fit, data[1:5, ])

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred_class")
  expect_s3_class(preds$.pred_class, "factor")
})

test_that("glmnet probability predictions", {
  skip_if_not_installed("glmnet")

  spec <- logistic_reg(penalty = 0.1) |> set_engine("glmnet")

  data <- data.frame(
    y = factor(rep(c("A", "B"), each = 10)),
    x1 = rnorm(20),
    x2 = rnorm(20)
  )

  fit <- fit(spec, y ~ ., data = data)
  preds <- predict(fit, data[1:5, ], type = "prob")

  expect_s3_class(preds, "tbl_df")
  expect_true(all(grepl("^\\.pred_", names(preds))))
  expect_equal(ncol(preds), 2)

  # Check probabilities sum to 1
  row_sums <- rowSums(preds)
  expect_equal(row_sums, rep(1, 5), tolerance = 1e-10)
})
```

### 4. Argument Translation Tests

Test that main arguments are correctly translated:

```r
test_that("glmnet penalty argument translates correctly", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  # Check lambda was set
  expect_true("lambda" %in% names(fit$fit$call))
  expect_equal(fit$spec$args$penalty, 0.1)
})

test_that("glmnet mixture argument translates correctly", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1, mixture = 0.5) |>
    set_engine("glmnet")

  fit <- fit(spec, mpg ~ ., data = mtcars)

  # Check alpha was set
  expect_true("alpha" %in% names(fit$fit$call))
  expect_equal(fit$spec$args$mixture, 0.5)
})
```

### 5. Edge Case Tests

Test boundary conditions:

```r
test_that("glmnet handles single row prediction", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  preds <- predict(fit, mtcars[1, ])

  expect_equal(nrow(preds), 1)
  expect_named(preds, ".pred")
})

test_that("glmnet handles factor predictors", {
  skip_if_not_installed("glmnet")

  data <- mtcars
  data$cyl <- factor(data$cyl)

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ cyl + hp, data = data)

  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, data[1:5, ])
  expect_equal(nrow(preds), 5)
})

test_that("glmnet handles missing values appropriately", {
  skip_if_not_installed("glmnet")

  data <- mtcars
  data$hp[1:3] <- NA

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")

  # glmnet should error on missing values
  expect_error(
    fit(spec, mpg ~ ., data = data)
  )
})
```

### 6. Multi-Mode Testing

If engine supports multiple modes, test each:

```r
# ------------------------------------------------------------------------------
# Regression mode

test_that("xgboost regression mode", {
  skip_if_not_installed("xgboost")

  spec <- boost_tree(trees = 20) |>
    set_engine("xgboost") |>
    set_mode("regression")

  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, mtcars[1:5, ])
  expect_named(preds, ".pred")
})

# ------------------------------------------------------------------------------
# Classification mode

test_that("xgboost classification mode", {
  skip_if_not_installed("xgboost")

  spec <- boost_tree(trees = 20) |>
    set_engine("xgboost") |>
    set_mode("classification")

  data <- data.frame(
    y = factor(rep(c("A", "B"), each = 10)),
    x1 = rnorm(20),
    x2 = rnorm(20)
  )

  fit <- fit(spec, y ~ ., data = data)

  expect_s3_class(fit, "model_fit")

  preds_class <- predict(fit, data[1:5, ])
  expect_named(preds_class, ".pred_class")

  preds_prob <- predict(fit, data[1:5, ], type = "prob")
  expect_true(all(grepl("^\\.pred_", names(preds_prob))))
})
```

--------------------------------------------------------------------------------

## Snapshot Testing

Use for engine-specific errors:

```r
test_that("glmnet errors informatively on invalid penalty", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = -1) |> set_engine("glmnet")

  expect_snapshot(
    fit(spec, mpg ~ ., data = mtcars),
    error = TRUE
  )
})

test_that("glmnet errors on incompatible mode-type", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_snapshot(
    predict(fit, mtcars, type = "prob"),
    error = TRUE
  )
})
```

--------------------------------------------------------------------------------

## Integration Tests

Test engine works with tidymodels ecosystem:

```r
test_that("glmnet works with workflows", {
  skip_if_not_installed("workflows")
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")

  wf <- workflows::workflow() |>
    workflows::add_formula(mpg ~ .) |>
    workflows::add_model(spec)

  fit <- fit(wf, data = mtcars)
  preds <- predict(fit, mtcars[1:5, ])

  expect_s3_class(preds, "tbl_df")
  expect_equal(nrow(preds), 5)
})

test_that("glmnet works with recipes", {
  skip_if_not_installed("workflows")
  skip_if_not_installed("recipes")
  skip_if_not_installed("glmnet")

  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")

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

## Test Organization Pattern

```r
# tests/testthat/test-linear_reg-glmnet.R

# ------------------------------------------------------------------------------
# Setup and configuration

test_that("can set glmnet engine", { ... })
test_that("glmnet accepts engine args", { ... })

# ------------------------------------------------------------------------------
# Fitting - regression mode

test_that("glmnet fits with formula", { ... })
test_that("glmnet fits with xy", { ... })
test_that("formula and xy equivalent", { ... })

# ------------------------------------------------------------------------------
# Predictions - regression mode

test_that("numeric predictions", { ... })
test_that("raw predictions", { ... })

# ------------------------------------------------------------------------------
# Argument handling

test_that("penalty translates", { ... })
test_that("mixture translates", { ... })

# ------------------------------------------------------------------------------
# Edge cases

test_that("single row", { ... })
test_that("factor predictors", { ... })
test_that("missing values", { ... })

# ------------------------------------------------------------------------------
# Integration

test_that("works with workflows", { ... })
test_that("works with recipes", { ... })
```

--------------------------------------------------------------------------------

## Testing Checklist

Before submitting engine PR:

- [ ] Engine can be selected with `set_engine()`

- [ ] Engine-specific arguments work

- [ ] Formula interface works

- [ ] XY interface works (if supported)

- [ ] Formula and xy give same results

- [ ] All prediction types tested

- [ ] Argument translation verified

- [ ] Single row predictions work

- [ ] Factor predictors handled

- [ ] Edge cases covered

- [ ] Error messages have snapshots

- [ ] Works with workflows

- [ ] Works with recipes

- [ ] All modes tested (if multi-mode)

- [ ] All tests pass

- [ ] Good test coverage

--------------------------------------------------------------------------------

## Common Patterns

### Pattern 1: Test Both Interfaces

```r
test_that("both interfaces work", {
  skip_if_not_installed("pkg")

  spec <- my_model() |> set_engine("new_engine")

  # Formula
  fit1 <- fit(spec, y ~ ., data = data)
  pred1 <- predict(fit1, data[1:3, ])

  # XY
  fit2 <- fit_xy(spec, x = data[, -1], y = data$y)
  pred2 <- predict(fit2, data[1:3, ])

  expect_equal(pred1, pred2, tolerance = 1e-5)
})
```

### Pattern 2: Skip If Package Missing

```r
test_that("engine test", {
  skip_if_not_installed("enginepkg")
  skip_if_not_installed("helperpkg")

  # Test code
})
```

### Pattern 3: Check Prediction Format

```r
# Numeric
expect_named(preds, ".pred")
expect_type(preds$.pred, "double")

# Class
expect_named(preds, ".pred_class")
expect_s3_class(preds$.pred_class, "factor")

# Probability
expect_true(all(grepl("^\\.pred_", names(preds))))
expect_equal(rowSums(preds), rep(1, nrow(preds)), tolerance = 1e-10)
```

--------------------------------------------------------------------------------

## Debugging Engine Tests

### Run Specific Tests

```r
# Run engine-specific file
devtools::test_file("tests/testthat/test-linear_reg-glmnet.R")

# Run specific test
devtools::test_file(
  "tests/testthat/test-linear_reg-glmnet.R",
  filter = "numeric predictions"
)
```

### Interactive Debugging

```r
# Load package
devtools::load_all()

# Run test interactively
test_that("debug test", {
  spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")
  browser()  # Stops here
  fit <- fit(spec, mpg ~ ., data = mtcars)
})
```

--------------------------------------------------------------------------------

## Additional Resources

**Example test files in parsnip:**

- `tests/testthat/test-linear_reg.R` - Multiple engines

- `tests/testthat/test-boost_tree-xgboost.R` - Complex engine

- `tests/testthat/test-mlp.R` - Multi-mode testing

**Related guides:**

- [Engine Implementation](engine-implementation.md) - Implementation guide

- [Best Practices (Source)](./best-practices-source.md) - Code conventions

- [Troubleshooting (Source)](./troubleshooting-source.md) - Common issues
