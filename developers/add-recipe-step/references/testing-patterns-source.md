# Testing Patterns for Recipes Source Development

**Context:** This guide is for **source development** - contributing to the
recipes package directly.

**Key principle:** ✅ **You CAN use internal functions and test helpers** -
you're developing the package itself.

For extension development (creating new packages), see [Testing Patterns
(Extension)](package-extension-requirements.md#testing-requirements).

--------------------------------------------------------------------------------

## When to Use Internal Test Helpers

When developing recipes itself, you have access to internal test data and helper
functions. Use them to:

- Maintain consistency with existing tests

- Leverage well-tested recipe structures

- Match the testing style of the package

## Recipes Internal Test Helpers

### Using Internal Test Recipes

Recipes has internal helper recipes that you can use in tests:

```r
# Check if internal recipes exist
# grep -r "iris_rec\|mtcars_rec" tests/testthat/

# Common pattern: create simple test recipes
rec <- recipe(mpg ~ ., data = mtcars) |>
  step_normalize(all_numeric_predictors())
```

### Standard Test Datasets

Use standard R datasets for consistency:

```r
# Built-in datasets
data(mtcars)
data(iris)

# From modeldata (in Suggests)
data(biomass, package = "modeldata")
```

## Testing the prep/bake Workflow

The most critical aspect of testing recipe steps.

### Test prep() Behavior

```r
test_that("step_center trains correctly", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  # Prep the recipe
  prepped <- prep(rec, training = mtcars)

  # Check that step was trained
  expect_true(prepped$steps[[1]]$trained)

  # Check that means were calculated
  expect_type(prepped$steps[[1]]$means, "double")
  expect_named(prepped$steps[[1]]$means, c("disp", "hp"))

  # Check means are correct
  expect_equal(
    prepped$steps[[1]]$means[["disp"]],
    mean(mtcars$disp)
  )
})
```

### Test bake() Behavior

```r
test_that("step_center transforms correctly", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  prepped <- prep(rec, training = mtcars)
  baked <- bake(prepped, new_data = mtcars)

  # Check that columns were centered
  expect_equal(mean(baked$disp), 0, tolerance = 1e-7)
  expect_equal(mean(baked$hp), 0, tolerance = 1e-7)

  # Check other columns unchanged
  expect_equal(baked$mpg, mtcars$mpg)
})
```

### Test prep() with New Data in bake()

```r
test_that("step_center works on new data", {
  train <- mtcars[1:20, ]
  test <- mtcars[21:32, ]

  rec <- recipe(mpg ~ ., data = train) |>
    step_center(disp, hp)

  prepped <- prep(rec, training = train)

  # Bake on new data
  baked_test <- bake(prepped, new_data = test)

  # Test data should be centered using TRAINING means
  # So mean won't be exactly zero
  expect_type(baked_test$disp, "double")
  expect_equal(nrow(baked_test), nrow(test))
})
```

## File Naming Conventions

Recipes organizes tests by step name:

### Test File Names

- **Step files**: `tests/testthat/test-[step_name].R`

  - Example: `test-center.R`, `test-normalize.R`, `test-pca.R`

### Match Source File Names

- `R/center.R` → `tests/testthat/test-center.R`

- `R/normalize.R` → `tests/testthat/test-normalize.R`

## Test Organization in Recipes

### Standard Test Structure

```r
# tests/testthat/test-center.R

test_that("centering works correctly", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  prepped <- prep(rec, training = mtcars)
  results <- bake(prepped, mtcars)

  expect_equal(mean(results$disp), 0, tolerance = 1e-7)
  expect_equal(mean(results$hp), 0, tolerance = 1e-7)
})

test_that("centering handles selectors", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(all_numeric_predictors())

  prepped <- prep(rec, training = mtcars)

  # Check that correct columns were selected
  selected <- prepped$steps[[1]]$columns
  expect_true("disp" %in% selected)
  expect_true("hp" %in% selected)
  expect_false("mpg" %in% selected)  # outcome, not predictor
})

test_that("centering works with case weights", {
  mtcars_weighted <- mtcars
  mtcars_weighted$wt_col <- hardhat::importance_weights(seq_len(nrow(mtcars)))

  rec <- recipe(mpg ~ ., data = mtcars_weighted) |>
    update_role(wt_col, new_role = "case_weights") |>
    step_center(disp)

  prepped <- prep(rec, training = mtcars_weighted)

  # Weighted mean should differ from unweighted
  expect_false(
    prepped$steps[[1]]$means[["disp"]] == mean(mtcars$disp)
  )
})

test_that("centering validates input", {
  # Character column should error
  df <- data.frame(
    x = letters[1:5],
    y = 1:5
  )

  rec <- recipe(~ ., data = df) |>
    step_center(x)

  expect_error(prep(rec, training = df))
})

test_that("centering handles NA", {
  mtcars_na <- mtcars
  mtcars_na$disp[1:5] <- NA

  rec <- recipe(mpg ~ ., data = mtcars_na) |>
    step_center(disp, na_rm = TRUE)

  prepped <- prep(rec, training = mtcars_na)
  baked <- bake(prepped, mtcars_na)

  # NA values should remain NA
  expect_true(all(is.na(baked$disp[1:5])))

  # Non-NA values should be centered
  expect_false(any(is.na(baked$disp[6:nrow(mtcars_na)])))
})
```

## Testing Variable Selection

Test that selectors work correctly:

```r
test_that("step_center works with all_numeric()", {
  rec <- recipe(Species ~ ., data = iris) |>
    step_center(all_numeric())

  prepped <- prep(rec, training = iris)

  # All numeric columns should be selected
  expect_setequal(
    prepped$steps[[1]]$columns,
    c("Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width")
  )
})

test_that("step_center works with all_numeric_predictors()", {
  rec <- recipe(Sepal.Length ~ ., data = iris) |>
    step_center(all_numeric_predictors())

  prepped <- prep(rec, training = iris)

  # Should exclude outcome (Sepal.Length)
  selected <- prepped$steps[[1]]$columns
  expect_false("Sepal.Length" %in% selected)
  expect_true("Sepal.Width" %in% selected)
})

test_that("step_center works with manual selection", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp, cyl)

  prepped <- prep(rec, training = mtcars)

  expect_setequal(
    prepped$steps[[1]]$columns,
    c("disp", "hp", "cyl")
  )
})

test_that("step_center works with has_role()", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    update_role(disp, new_role = "special") |>
    step_center(has_role("special"))

  prepped <- prep(rec, training = mtcars)

  expect_equal(prepped$steps[[1]]$columns, "disp")
})
```

## Testing with Different Step Types

### Modify-in-Place Steps

```r
test_that("step_center preserves column roles", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp)

  prepped <- prep(rec, training = mtcars)
  baked <- bake(prepped, mtcars)

  # Column should still exist with same name
  expect_true("disp" %in% names(baked))

  # Role should be preserved
  expect_equal(
    prepped$var_info$role[prepped$var_info$variable == "disp"],
    "predictor"
  )
})
```

### Create-New-Columns Steps

```r
test_that("step_dummy creates new columns", {
  rec <- recipe(~ Species, data = iris) |>
    step_dummy(Species)

  prepped <- prep(rec, training = iris)
  baked <- bake(prepped, iris)

  # New columns should be created
  expect_true("Species_versicolor" %in% names(baked))
  expect_true("Species_virginica" %in% names(baked))

  # Original column should be removed (default behavior)
  expect_false("Species" %in% names(baked))
})

test_that("step_dummy respects keep_original_cols", {
  rec <- recipe(~ Species, data = iris) |>
    step_dummy(Species, keep_original_cols = TRUE)

  prepped <- prep(rec, training = iris)
  baked <- bake(prepped, iris)

  # Original column should still exist
  expect_true("Species" %in% names(baked))

  # New columns should also exist
  expect_true("Species_versicolor" %in% names(baked))
})
```

### Row-Operation Steps

```r
test_that("step_filter removes rows", {
  rec <- recipe(~ ., data = mtcars) |>
    step_filter(mpg > 20)

  prepped <- prep(rec, training = mtcars)
  baked <- bake(prepped, mtcars)

  # Should have fewer rows
  expect_lt(nrow(baked), nrow(mtcars))

  # All remaining rows should satisfy filter
  expect_true(all(baked$mpg > 20))
})

test_that("step_filter respects skip parameter", {
  rec <- recipe(~ ., data = mtcars) |>
    step_filter(mpg > 20, skip = TRUE)

  prepped <- prep(rec, training = mtcars)

  # Skip = TRUE means bake() doesn't apply filter to new data
  baked <- bake(prepped, mtcars)
  expect_equal(nrow(baked), nrow(mtcars))
})
```

## Testing tidy() Output

Every step should have tidy() method:

```r
test_that("tidy works on untrained step", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  # Before training
  untrained_tidy <- tidy(rec, number = 1)

  expect_s3_class(untrained_tidy, "tbl_df")
  expect_true("terms" %in% names(untrained_tidy))
  expect_true("id" %in% names(untrained_tidy))

  # Values should be NA for untrained step
  expect_true(all(is.na(untrained_tidy$value)))
})

test_that("tidy works on trained step", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  prepped <- prep(rec, training = mtcars)
  trained_tidy <- tidy(prepped, number = 1)

  expect_s3_class(trained_tidy, "tbl_df")
  expect_equal(nrow(trained_tidy), 2)  # Two columns centered

  # Should have actual values
  expect_false(any(is.na(trained_tidy$value)))

  # Values should match calculated means
  expect_equal(
    trained_tidy$value[trained_tidy$terms == "disp"],
    mean(mtcars$disp)
  )
})
```

## Testing print() Output

```r
test_that("print shows step information", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  # Capture print output
  output <- capture.output(print(rec))

  # Should mention the step
  expect_true(any(grepl("Centering", output)))
  expect_true(any(grepl("disp", output)))
  expect_true(any(grepl("hp", output)))
})

test_that("print shows training status", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  untrained_output <- capture.output(print(rec))
  expect_true(any(grepl("\\[trained\\]", untrained_output)))

  prepped <- prep(rec, training = mtcars)
  trained_output <- capture.output(print(prepped))
  expect_true(any(grepl("\\[trained\\]", trained_output)))
})
```

## Testing Integration with Full Recipes

Test steps work in realistic recipe pipelines:

```r
test_that("step_center works in full recipe", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_normalize(all_numeric_predictors()) |>
    step_center(disp) |>
    step_pca(all_numeric_predictors(), num_comp = 2)

  # Should prep without errors
  prepped <- prep(rec, training = mtcars)

  # Should bake without errors
  baked <- bake(prepped, mtcars)

  # Result should be reasonable
  expect_equal(nrow(baked), nrow(mtcars))
  expect_true(all(c("PC1", "PC2") %in% names(baked)))
})
```

## Testing Edge Cases

```r
test_that("step_center handles edge cases", {
  # Empty selection
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(all_nominal())  # No nominal columns

  prepped <- prep(rec, training = mtcars)
  baked <- bake(prepped, mtcars)

  # Should work fine, just do nothing
  expect_equal(baked, mtcars)

  # Single column
  rec2 <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp)

  prepped2 <- prep(rec2, training = mtcars)
  baked2 <- bake(prepped2, mtcars)

  expect_equal(mean(baked2$disp), 0, tolerance = 1e-7)

  # All same values
  df <- data.frame(x = rep(5, 10), y = 1:10)
  rec3 <- recipe(y ~ ., data = df) |>
    step_center(x)

  prepped3 <- prep(rec3, training = df)
  baked3 <- bake(prepped3, df)

  # Centered constant should be zero
  expect_equal(baked3$x, rep(0, 10))
})
```

## Testing with Grouped Data

```r
test_that("step_center works with grouped data", {
  library(dplyr)

  mtcars_grouped <- mtcars |>
    group_by(cyl)

  rec <- recipe(mpg ~ ., data = mtcars_grouped) |>
    step_center(disp)

  # Should preserve grouping through prep/bake
  prepped <- prep(rec, training = mtcars_grouped)
  baked <- bake(prepped, mtcars_grouped)

  expect_s3_class(baked, "grouped_df")
  expect_equal(group_vars(baked), "cyl")
})
```

## Using Internal Validation Functions

Recipes provides internal validation you can use:

```r
# In your prep() method
prep.step_center <- function(x, training, info = NULL, ...) {
  col_names <- recipes_eval_select(x$terms, training, info)

  # Use internal validation
  check_type(training[, col_names], types = c("double", "integer"))

  # Your implementation
  # ...
}
```

## Running Tests

```r
# Run all tests
devtools::test()

# Run specific test file
testthat::test_file("tests/testthat/test-center.R")

# Run tests matching pattern
devtools::test(filter = "center")
```

## Next Steps

- Review [Best Practices (Source)](best-practices-source.md) for recipes coding
  standards

- Check [Troubleshooting (Source)](troubleshooting-source.md) for common issues

- See existing test files in `tests/testthat/` for more examples
