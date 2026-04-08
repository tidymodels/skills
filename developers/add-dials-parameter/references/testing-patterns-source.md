# Testing Patterns (Source Development)

**dials-specific testing patterns for contributing to tidymodels/dials**

This guide covers testing patterns specific to source development when
contributing parameters to the dials package itself.

--------------------------------------------------------------------------------

## Key Differences from Extension Testing

### Test File Organization

**Extension development**: One test file per parameter

```
tests/testthat/
├── test-my-parameter.R
├── test-another-parameter.R
└── test-third-parameter.R
```

**Source development**: Shared test files by category

```
tests/testthat/
├── test-params.R          # Range tests for ALL parameters
├── test-constructors.R    # Constructor argument validation
├── test-finalize.R        # Finalization tests
├── test-grids.R          # Grid generation tests
└── test-*.R              # Other test categories
```

### Function Calls

**Extension development**: Use `dials::` prefix

```r
test_that("my_parameter works", {
  param <- my_parameter()
  expect_s3_class(param, "quant_param")

  grid <- dials::grid_regular(param, levels = 5)
  expect_equal(nrow(grid), 5)
})
```

**Source development**: Direct function calls

```r
test_that("my_parameter works", {
  param <- my_parameter()
  expect_s3_class(param, "quant_param")

  grid <- grid_regular(param, levels = 5)
  expect_equal(nrow(grid), 5)
})
```

### Test Helpers

**Extension development**: Standard testthat only

**Source development**: Access to internal test helpers and utilities

--------------------------------------------------------------------------------

## Test File Organization in dials

### test-params.R

**Purpose**: Range validation for all parameters

**Pattern**: Add tests for new parameters to this shared file

```r
# tests/testthat/test-params.R

# Existing tests for penalty, mixture, etc...

test_that("my_parameter has correct range", {
  expect_equal(
    range_get(my_parameter()),
    list(lower = 0, upper = 1)
  )
  expect_equal(
    range_get(my_parameter(range = c(0.2, 0.8))),
    list(lower = 0.2, upper = 0.8)
  )
})
```

**Keep alphabetical order**: Add new tests in alphabetical order by parameter
name

### test-constructors.R

**Purpose**: Constructor argument validation

**Pattern**: Test that invalid arguments produce errors

```r
# tests/testthat/test-constructors.R

test_that("new_quant_param validates arguments", {
  expect_snapshot(
    error = TRUE,
    new_quant_param(
      type = "double",
      range = c(1, 0),  # Invalid: lower > upper
      inclusive = c(TRUE, TRUE),
      trans = NULL,
      label = c(test = "Test")
    )
  )

  expect_snapshot(
    error = TRUE,
    new_quant_param(
      type = "double",
      range = 0,  # Invalid: length != 2
      inclusive = c(TRUE, TRUE),
      trans = NULL,
      label = c(test = "Test")
    )
  )
})
```

### test-finalize.R

**Purpose**: Finalization tests for data-dependent parameters

**Pattern**: Test that finalization resolves unknown() correctly

```r
# tests/testthat/test-finalize.R

test_that("my_parameter finalizes correctly", {
  param <- my_parameter()

  # Before finalization
  expect_s3_class(param$range$upper, "unknown")

  # After finalization
  finalized <- finalize(param, mtcars[, -1])
  expect_type(finalized$range$upper, "integer")
  expect_equal(finalized$range$upper, ncol(mtcars) - 1)
})
```

### test-grids.R

**Purpose**: Grid generation tests

**Pattern**: Test that parameters work with all grid functions

```r
# tests/testthat/test-grids.R

test_that("my_parameter works with grids", {
  param <- my_parameter()

  # Regular grid
  grid_reg <- grid_regular(param, levels = 5)
  expect_equal(nrow(grid_reg), 5)

  # Random grid
  set.seed(123)
  grid_rand <- grid_random(param, size = 10)
  expect_equal(nrow(grid_rand), 10)

  # Space-filling grid
  grid_space <- grid_space_filling(param, size = 8)
  expect_equal(nrow(grid_space), 8)
})
```

--------------------------------------------------------------------------------

## Required Test Categories

### 1. Range Validation

Test that parameters accept valid ranges and reject invalid ones.

**In test-params.R**:

```r
test_that("my_parameter range validation", {
  # Default range
  expect_equal(
    range_get(my_parameter()),
    list(lower = 0, upper = 1)
  )

  # Custom range
  expect_equal(
    range_get(my_parameter(range = c(0.1, 0.9))),
    list(lower = 0.1, upper = 0.9)
  )

  # Range with unknown
  param_unknown <- my_parameter(range = c(1L, unknown()))
  expect_equal(param_unknown$range$lower, 1L)
  expect_s3_class(param_unknown$range$upper, "unknown")
})
```

**In test-constructors.R** (for invalid ranges):

```r
test_that("my_parameter rejects invalid ranges", {
  expect_snapshot(
    error = TRUE,
    my_parameter(range = c(1, 0))  # lower > upper
  )

  expect_snapshot(
    error = TRUE,
    my_parameter(range = c(0, NA))  # NA value
  )

  expect_snapshot(
    error = TRUE,
    my_parameter(range = 0)  # length != 2
  )
})
```

### 2. Type Checking

Test correct type enforcement.

```r
test_that("my_parameter enforces type", {
  param_double <- my_parameter()
  expect_equal(param_double$type, "double")

  param_int <- my_integer_parameter()
  expect_equal(param_int$type, "integer")

  # Values from grid should match type
  grid <- grid_regular(param_int, levels = 5)
  expect_type(grid$my_integer_parameter, "integer")
})
```

### 3. Transformation

Test that transformed values are generated correctly.

```r
test_that("my_parameter transformation works", {
  param <- penalty()  # Has log10 transformation

  # Range in transformed space
  expect_equal(param$range$lower, -10)
  expect_equal(param$range$upper, 0)

  # Generated values in actual space
  grid <- grid_regular(param, levels = 5)

  # Should span 10^-10 to 10^0
  expect_true(min(grid$penalty) >= 1e-10)
  expect_true(max(grid$penalty) <= 1)

  # Log10 of values should be evenly spaced
  log_vals <- log10(grid$penalty)
  diffs <- diff(log_vals)
  expect_true(all(abs(diffs - diffs[1]) < 0.01))
})
```

### 4. Finalization

Test data-dependent parameters finalize properly.

**In test-finalize.R**:

```r
test_that("my_parameter finalization", {
  param <- my_parameter()

  # Has unknown bound
  expect_s3_class(param$range$upper, "unknown")

  # Finalize with data
  test_data <- mtcars[, -1]  # 10 predictors
  finalized <- finalize(param, test_data)

  # Unknown resolved
  expect_false(inherits(finalized$range$upper, "unknown"))
  expect_equal(finalized$range$upper, ncol(test_data))

  # Works with different data sizes
  large_data <- matrix(rnorm(100 * 50), ncol = 50)
  finalized_large <- finalize(param, large_data)
  expect_equal(finalized_large$range$upper, 50)
})

test_that("my_parameter custom finalize function", {
  param <- num_initial_terms()

  # Small dataset
  small_data <- mtcars[, -1]  # 10 predictors
  finalized_small <- finalize(param, small_data)
  expected_small <- min(200, max(20, 2 * 10)) + 1
  expect_equal(finalized_small$range$upper, expected_small)

  # Large dataset
  large_data <- matrix(rnorm(100 * 100), ncol = 100)
  finalized_large <- finalize(param, large_data)
  expected_large <- min(200, max(20, 2 * 100)) + 1
  expect_equal(finalized_large$range$upper, expected_large)
})
```

### 5. Grid Integration

Test parameters work with all grid functions.

**In test-grids.R**:

```r
test_that("my_parameter grid integration", {
  param <- my_parameter()

  # Regular grid
  grid_reg <- grid_regular(param, levels = 5)
  expect_equal(nrow(grid_reg), 5)
  expect_true(all(grid_reg$my_parameter >= param$range$lower))
  expect_true(all(grid_reg$my_parameter <= param$range$upper))

  # Random grid
  set.seed(123)
  grid_rand <- grid_random(param, size = 20)
  expect_equal(nrow(grid_rand), 20)
  expect_true(all(grid_rand$my_parameter >= param$range$lower))
  expect_true(all(grid_rand$my_parameter <= param$range$upper))

  # Space-filling grid
  set.seed(456)
  grid_space <- grid_space_filling(param, size = 15)
  expect_equal(nrow(grid_space), 15)
  expect_true(all(grid_space$my_parameter >= param$range$lower))
  expect_true(all(grid_space$my_parameter <= param$range$upper))
})

test_that("my_parameter works in parameter sets", {
  params <- parameters(
    my_parameter = my_parameter(),
    penalty = penalty()
  )

  grid <- grid_regular(params, levels = 3)
  expect_equal(nrow(grid), 9)  # 3 x 3
  expect_equal(ncol(grid), 2)
})
```

### 6. Value Utilities

Test `value_sample()` and `value_seq()`.

```r
test_that("my_parameter value utilities", {
  param <- my_parameter()

  # value_sample
  set.seed(123)
  samples <- value_sample(param, n = 10)
  expect_length(samples, 10)
  expect_true(all(samples >= param$range$lower))
  expect_true(all(samples <= param$range$upper))

  # value_seq
  seq_vals <- value_seq(param, n = 5)
  expect_length(seq_vals, 5)
  expect_true(all(seq_vals >= param$range$lower))
  expect_true(all(seq_vals <= param$range$upper))

  # Sequence should be ordered
  expect_true(all(diff(seq_vals) >= 0))
})
```

### 7. Edge Cases

Test boundary conditions and edge cases.

```r
test_that("my_parameter edge cases", {
  param <- my_parameter()

  # Single value range
  param_single <- my_parameter(range = c(0.5, 0.5))
  grid <- grid_regular(param_single, levels = 5)
  expect_true(all(grid$my_parameter == 0.5))

  # Very small range
  param_tiny <- my_parameter(range = c(0.9999, 1.0000))
  grid <- grid_random(param_tiny, size = 5)
  expect_true(all(grid$my_parameter >= 0.9999))
  expect_true(all(grid$my_parameter <= 1.0000))
})
```

--------------------------------------------------------------------------------

## Complete Test Examples

### Example 1: Quantitative Parameter (Simple)

```r
# In test-params.R
test_that("threshold range validation", {
  expect_equal(
    range_get(threshold()),
    list(lower = 0, upper = 1)
  )

  expect_equal(
    range_get(threshold(range = c(0.2, 0.8))),
    list(lower = 0.2, upper = 0.8)
  )
})

# In test-constructors.R
test_that("threshold rejects invalid ranges", {
  expect_snapshot(
    error = TRUE,
    threshold(range = c(1, 0))
  )

  expect_snapshot(
    error = TRUE,
    threshold(range = c(0, NA))
  )
})

# In test-grids.R
test_that("threshold works with grids", {
  param <- threshold()

  grid <- grid_regular(param, levels = 5)
  expect_equal(nrow(grid), 5)
  expect_true(all(grid$threshold >= 0 & grid$threshold <= 1))
})
```

### Example 2: Quantitative Parameter (Transformed)

```r
# In test-params.R
test_that("penalty range validation", {
  expect_equal(
    range_get(penalty()),
    list(lower = -10, upper = 0)
  )

  # Has transformation
  expect_s3_class(penalty()$trans, "transform")
})

# In test-grids.R
test_that("penalty transformation in grids", {
  param <- penalty()
  grid <- grid_regular(param, levels = 11)

  # Values should span 10^-10 to 10^0
  expect_true(min(grid$penalty) >= 1e-10)
  expect_true(max(grid$penalty) <= 1.0)

  # Log10 spacing should be even
  log_vals <- log10(grid$penalty)
  expect_equal(log_vals, seq(-10, 0, by = 1))
})
```

### Example 3: Data-Dependent Parameter

```r
# In test-params.R
test_that("mtry range validation", {
  param <- mtry()

  expect_equal(param$range$lower, 1L)
  expect_s3_class(param$range$upper, "unknown")
})

# In test-finalize.R
test_that("mtry finalization", {
  param <- mtry()

  # Finalize with data
  finalized <- finalize(param, mtcars[, -1])

  expect_equal(finalized$range$lower, 1L)
  expect_equal(finalized$range$upper, ncol(mtcars) - 1)

  # Different data size
  large_data <- matrix(rnorm(100 * 50), ncol = 50)
  finalized_large <- finalize(param, large_data)
  expect_equal(finalized_large$range$upper, 50)
})

# In test-grids.R
test_that("mtry works with grids after finalization", {
  param <- mtry()
  finalized <- finalize(param, mtcars[, -1])

  grid <- grid_regular(finalized, levels = 5)
  expect_equal(nrow(grid), 5)
  expect_true(all(grid$mtry >= 1))
  expect_true(all(grid$mtry <= finalized$range$upper))
})
```

### Example 4: Qualitative Parameter

```r
# In test-params.R
test_that("activation values validation", {
  param <- activation()

  expect_equal(param$type, "character")
  expect_equal(param$values, values_activation)
  expect_true(length(param$values) > 0)
})

# In test-constructors.R
test_that("activation rejects invalid values", {
  expect_snapshot(
    error = TRUE,
    activation(values = character(0))  # Empty
  )

  expect_snapshot(
    error = TRUE,
    activation(values = NULL)
  )
})

# In test-grids.R
test_that("activation works with grids", {
  param <- activation()

  # Regular grid uses all values
  grid <- grid_regular(param)
  expect_equal(nrow(grid), length(values_activation))
  expect_true(all(grid$activation %in% values_activation))

  # Random grid samples with replacement
  set.seed(123)
  grid_rand <- grid_random(param, size = 20)
  expect_equal(nrow(grid_rand), 20)
  expect_true(all(grid_rand$activation %in% values_activation))
})

# Test companion vector
test_that("values_activation is correct", {
  expect_type(values_activation, "character")
  expect_true(all(nchar(values_activation) > 0))
  expect_true(all(!duplicated(values_activation)))
})
```

--------------------------------------------------------------------------------

## Using expect_snapshot()

For error messages and output that should remain consistent:

### Testing Error Messages

```r
test_that("constructor validates arguments", {
  expect_snapshot(
    error = TRUE,
    new_quant_param(
      type = "double",
      range = c(1, 0),
      inclusive = c(TRUE, TRUE),
      trans = NULL,
      label = c(test = "Test")
    )
  )
})
```

First run creates snapshot file:

```
# tests/testthat/_snaps/constructors.md

    Code
      new_quant_param(type = "double", range = c(1, 0), inclusive = c(TRUE, TRUE),
        trans = NULL, label = c(test = "Test"))
    Error <simpleError>
      The range for 'test' is invalid: lower bound (1) must be less than upper bound (0)
```

### Accepting Snapshots

After first run or when errors change intentionally:

```r
testthat::snapshot_accept()
```

### When to Use Snapshots

**Use `expect_snapshot()` for**:

- Error messages

- Warning messages

- Complex printed output

- Messages that should stay consistent

**Don't use snapshots for**:

- Simple value comparisons (`expect_equal()` is better)

- Numeric tests (`expect_true()`, `expect_equal()`)

- Tests that might have platform-specific output

--------------------------------------------------------------------------------

## Source-Specific Patterns

### Testing Internal Functions

Source development can test internal functions:

```r
test_that("internal validation works", {
  expect_silent(check_type("double"))
  expect_silent(check_type("integer"))

  expect_error(check_type("numeric"))
  expect_error(check_type("string"))
})

test_that("range manipulation works", {
  param <- penalty()

  # Get range
  bounds <- range_get(param)
  expect_equal(bounds$lower, -10)
  expect_equal(bounds$upper, 0)

  # Set range
  new_bounds <- list(lower = -5, upper = -1)
  param_updated <- range_set(param, new_bounds)
  expect_equal(range_get(param_updated), new_bounds)
})
```

### Testing with Internal Helpers

Use internal test helpers when available:

```r
test_that("parameter uses correct finalize helper", {
  param <- mtry()

  # Check finalize function is correct
  expect_identical(param$finalize, get_p)
})
```

### Alphabetical Organization

Keep tests in alphabetical order in shared files:

```r
# test-params.R

# ... earlier parameters ...

test_that("mixture range validation", {
  # Tests for mixture
})

test_that("mtry range validation", {
  # Tests for mtry (comes after mixture)
})

test_that("penalty range validation", {
  # Tests for penalty (comes after mtry)
})

# ... later parameters ...
```

--------------------------------------------------------------------------------

## Running Tests

### Run All Tests

```r
devtools::test()
```

### Run Specific Test File

```r
devtools::test_active_file()  # If file is open
testthat::test_file("tests/testthat/test-params.R")
```

### Run Specific Test

```r
testthat::test_file(
  "tests/testthat/test-params.R",
  filter = "my_parameter"
)
```

### Check Package

```r
devtools::check()  # Runs all tests plus R CMD check
```

--------------------------------------------------------------------------------

## Best Practices

### 1. Add Tests to Correct Files

- **Range validation** → `test-params.R`

- **Invalid arguments** → `test-constructors.R`

- **Finalization** → `test-finalize.R`

- **Grid generation** → `test-grids.R`

### 2. Keep Alphabetical Order

Add new tests in alphabetical order within shared files.

### 3. Test All Grid Functions

Always test `grid_regular()`, `grid_random()`, and `grid_space_filling()`.

### 4. Test Edge Cases

- Single-value ranges

- Very small ranges

- Unknown bounds

- Empty qualitative values

### 5. Use Snapshots for Errors

Use `expect_snapshot()` for error messages to catch unintended changes.

### 6. Test Data of Different Sizes

For data-dependent parameters, test with small, medium, and large datasets.

### 7. Set Seeds for Reproducibility

Always use `set.seed()` before random grid generation in tests.

--------------------------------------------------------------------------------

## Checklist for New Parameter

When adding a new parameter, ensure tests cover:

- [ ] Range validation in `test-params.R`

- [ ] Invalid argument errors in `test-constructors.R`

- [ ] Grid generation in `test-grids.R`

      - [ ] `grid_regular()`

      - [ ] `grid_random()`

      - [ ] `grid_space_filling()`
- [ ] Value utilities work

      - [ ] `value_sample()`

      - [ ] `value_seq()`
- [ ] Transformation (if applicable)

- [ ] Finalization (if applicable) in `test-finalize.R`

- [ ] Edge cases handled

- [ ] Companion `values_*` vector (if qualitative)

- [ ] All tests pass: `devtools::test()`

- [ ] Package check passes: `devtools::check()`

- [ ] Snapshots accepted: `testthat::snapshot_accept()`

--------------------------------------------------------------------------------

## Next Steps

### Learn More

- **Best practices**: [Best Practices (Source)](best-practices-source.md)

- **Troubleshooting**: [Troubleshooting (Source)](troubleshooting-source.md)

- **Source guide**: [Source Development Guide](source-guide.md)

### External Resources

- [testthat package documentation](https://testthat.r-lib.org/)

- [Testing chapter in R Packages book](https://r-pkgs.org/testing-basics.html)

--------------------------------------------------------------------------------

**Last Updated:** 2026-03-31
