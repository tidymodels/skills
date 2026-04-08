# Troubleshooting Parsnip Source Development

Common issues and solutions when contributing to the parsnip package source
code.

--------------------------------------------------------------------------------

## Registration Issues

### Issue: Engine Not Found

**Symptom:**

```r
linear_reg() |> set_engine("myengine")
#> Error: Engine 'myengine' is not registered for linear_reg
```

**Causes:** 1. Forgot to register engine with `set_model_engine()` 2.
Registration code not executed 3. Typo in engine name

**Solution:**

```r
# Ensure this runs before use
set_model_engine(
  model = "linear_reg",
  mode = "regression",
  eng = "myengine"
)

# Check registration
parsnip::show_engines("linear_reg")
```

### Issue: Mode Not Available

**Symptom:**

```r
linear_reg() |> set_mode("classification")
#> Error: linear_reg can only be used for regression
```

**Causes:** 1. Model only supports one mode 2. Mode not registered with
`set_model_mode()`

**Solution:**

```r
# For single-mode models, this is expected
# Don't try to change the mode

# For multi-mode models, ensure mode is registered
set_model_mode(
  model = "boost_tree",
  mode = "classification"
)
```

### Issue: Prediction Type Not Available

**Symptom:**

```r
predict(fit, data, type = "conf_int")
#> Error: `type = 'conf_int'` is not available
```

**Causes:** 1. Forgot to register prediction type with `set_pred()` 2. Engine
doesn't support this prediction type 3. Wrong mode for prediction type

**Solution:**

```r
# Register the prediction type
set_pred(
  model = "linear_reg",
  eng = "lm",
  mode = "regression",
  type = "conf_int",
  value = list(...)
)

# Check available prediction types
# Should be documented in model help file
```

--------------------------------------------------------------------------------

## Fit Method Issues

### Issue: Formula Not Passed Correctly

**Symptom:**

```r
fit(spec, mpg ~ hp, data = mtcars)
#> Error: object 'mpg' not found
```

**Causes:** 1. Wrong interface type 2. Formula being evaluated too early 3.
Missing `protect = c("formula", "data")`

**Solution:**

```r
set_fit(
  ...,
  value = list(
    interface = "formula",  # Correct interface
    protect = c("formula", "data"),  # Protect arguments
    func = c(pkg = "stats", fun = "lm"),
    ...
  )
)
```

### Issue: Matrix Conversion Fails

**Symptom:**

```r
fit(spec, y ~ x, data = data)
#> Error: (list) object cannot be coerced to type 'double'
```

**Causes:** 1. Data contains non-numeric columns that can't be converted 2.
Factor encoding failed 3. Missing data not handled

**Solution:**

```r
# Check data types before conversion
pre = function(data, object) {
  # Remove non-numeric columns engine can't handle
  numeric_cols <- sapply(data, is.numeric)
  data[, numeric_cols, drop = FALSE]
}

# Or handle factors explicitly
pre = function(data, object) {
  # Convert factors to indicators
  model.matrix(~ . - 1, data = data)
}
```

### Issue: Arguments Not Translated

**Symptom:**

```r
linear_reg(penalty = 0.1) |> set_engine("glmnet") |> fit(...)
# Warning: unused argument (penalty = 0.1)
```

**Causes:** 1. Missing `set_model_arg()` registration 2. Wrong argument name in
translation

**Solution:**

```r
# Register argument translation
set_model_arg(
  model = "linear_reg",
  eng = "glmnet",
  parsnip = "penalty",    # parsnip name
  original = "lambda",    # glmnet name
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = TRUE
)
```

--------------------------------------------------------------------------------

## Predict Method Issues

### Issue: Wrong Column Names

**Symptom:**

```r
predict(fit, data)
#>   prediction
#> 1       21.4
```

Should have `.pred` column name.

**Causes:** 1. Engine returns data frame with wrong names 2. Missing `post`
function to standardize

**Solution:**

```r
set_pred(
  ...,
  value = list(
    post = function(results, object) {
      tibble::tibble(.pred = as.numeric(results))
    },
    ...
  )
)
```

### Issue: Predictions Wrong Type

**Symptom:**

```r
predict(fit, data, type = "class")
#>   .pred_class
#> 1 "A"          # character, should be factor
```

**Causes:** 1. Engine returns character instead of factor 2. Missing type
conversion in `post`

**Solution:**

```r
post = function(results, object) {
  tibble::tibble(
    .pred_class = factor(results, levels = object$lvl)
  )
}
```

### Issue: Predictions Wrong Dimensions

**Symptom:**

```r
predict(fit, data[1:5, ])
#>   .pred
#> 1  21.4  # Only 1 row, should be 5
```

**Causes:** 1. Engine returns aggregated results 2. Prediction function not
working correctly

**Solution:**

```r
# Debug the prediction function
set_pred(
  ...,
  value = list(
    post = function(results, object) {
      # Check dimensions
      if (length(results) != nrow(new_data)) {
        rlang::abort(
          "Prediction length doesn't match data rows",
          "i" = sprintf("Got %d predictions for %d rows",
                       length(results), nrow(new_data))
        )
      }
      tibble::tibble(.pred = results)
    },
    ...
  )
)
```

### Issue: Probability Columns Don't Sum to 1

**Symptom:**

```r
predict(fit, data, type = "prob")
#>   .pred_A .pred_B
#> 1    0.8     0.3   # Sum is 1.1, not 1.0
```

**Causes:** 1. Engine returns unnormalized probabilities 2. Conversion error in
`post`

**Solution:**

```r
post = function(results, object) {
  # Normalize probabilities
  row_sums <- rowSums(results)
  results <- results / row_sums

  # Convert to tibble with correct names
  results <- as.data.frame(results)
  names(results) <- paste0(".pred_", names(results))
  tibble::as_tibble(results)
}
```

--------------------------------------------------------------------------------

## Encoding Issues

### Issue: Too Many Dummy Variables

**Symptom:**

```r
# 3-level factor creates 3 dummy columns instead of 2
fit <- fit(spec, y ~ x, data = data)
# Model matrix has columns: x_A, x_B, x_C
```

**Causes:** 1. Using one-hot encoding instead of traditional 2. Wrong
`predictor_indicators` setting

**Solution:**

```r
set_encoding(
  ...,
  options = list(
    predictor_indicators = "traditional"  # n-1 encoding
  )
)
```

### Issue: Intercept Handled Twice

**Symptom:**

```r
# Singular matrix error or perfect collinearity
fit <- fit(spec, y ~ x, data = data)
#> Error: system is computationally singular
```

**Causes:** 1. Both parsnip and engine adding intercept 2. Engine expects no
intercept in matrix

**Solution:**

```r
set_encoding(
  ...,
  options = list(
    compute_intercept = FALSE,  # Don't add to matrix
    remove_intercept = TRUE     # Remove from formula
  )
)
```

### Issue: Factor Levels Mismatch

**Symptom:**

```r
predict(fit, new_data)
#> Error: factor x has new levels not in training data
```

**Causes:** 1. New data has different levels than training data 2. Levels not
properly preserved

**Solution:**

```r
# In prediction, check and fix levels
set_pred(
  ...,
  value = list(
    pre = function(new_data, object) {
      # Ensure factor levels match training
      for (col in names(new_data)) {
        if (is.factor(new_data[[col]])) {
          train_levels <- object$lvl[[col]]
          if (!is.null(train_levels)) {
            new_data[[col]] <- factor(new_data[[col]], levels = train_levels)
          }
        }
      }
      new_data
    },
    ...
  )
)
```

--------------------------------------------------------------------------------

## Package Dependency Issues

### Issue: Package Not Available

**Symptom:**

```r
linear_reg() |> set_engine("glmnet")
#> Error: package 'glmnet' is required but not installed
```

**Causes:** 1. Missing `set_dependency()` call 2. Package not in Imports or
Suggests

**Solution:**

```r
# Register dependency
set_dependency(
  model = "linear_reg",
  eng = "glmnet",
  pkg = "glmnet",
  mode = "regression"
)

# Add to DESCRIPTION
# Suggests: glmnet
```

### Issue: Function Not Found

**Symptom:**

```r
fit(spec, y ~ x, data = data)
#> Error: could not find function "glmnet"
```

**Causes:** 1. Wrong package name in `func` 2. Package not loaded 3. Function
not exported

**Solution:**

```r
# Use full package specification
set_fit(
  ...,
  value = list(
    func = c(pkg = "glmnet", fun = "glmnet"),  # Full path
    ...
  )
)

# For internal functions (source development only)
set_fit(
  ...,
  value = list(
    func = c(pkg = "parsnip", fun = "internal_helper"),
    ...
  )
)
```

--------------------------------------------------------------------------------

## Multi-Mode Issues

### Issue: Wrong Mode Selected

**Symptom:**

```r
boost_tree() |> fit(Species ~ ., data = iris)
#> Error: Please set the mode
```

**Causes:** 1. Model supports multiple modes but none specified 2. Default mode
is "unknown"

**Solution:**

```r
# Explicitly set mode
spec <- boost_tree() |> set_mode("classification")

# Or set mode in constructor
spec <- boost_tree(mode = "classification")
```

### Issue: Mode-Specific Behavior Not Working

**Symptom:**

```r
# Both modes using same defaults when they should differ
fit_reg <- fit(boost_tree(mode = "regression"), y ~ x, data = data)
fit_cls <- fit(boost_tree(mode = "classification"), y ~ x, data = data)
# Both use same objective function
```

**Causes:** 1. Forgot to register mode-specific settings 2. `set_fit()` defaults
not mode-specific

**Solution:**

```r
# Register different defaults for each mode
set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "regression",
  value = list(
    defaults = list(objective = "reg:squarederror")  # Regression
  )
)

set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "classification",
  value = list(
    defaults = list(objective = "multi:softprob")  # Classification
  )
)
```

--------------------------------------------------------------------------------

## Testing Issues

### Issue: Tests Fail When Package Not Installed

**Symptom:**

```r
test_that("glmnet engine works", {
  spec <- linear_reg() |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)
  # Error: package 'glmnet' is required
})
```

**Solution:**

```r
# Skip test if package not available
test_that("glmnet engine works", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg() |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)
  expect_s3_class(fit, "model_fit")
})
```

### Issue: Formula and XY Tests Give Different Results

**Symptom:**

```r
test_that("formula and xy equivalent", {
  fit_formula <- fit(spec, y ~ x, data = data)
  fit_xy <- fit_xy(spec, x = data[, "x"], y = data$y)

  pred_formula <- predict(fit_formula, data)
  pred_xy <- predict(fit_xy, data)

  expect_equal(pred_formula, pred_xy)
  # Fails: predictions differ
})
```

**Causes:** 1. Formula includes intercept, xy doesn't 2. Factor encoding differs
3. Different data preprocessing

**Solution:**

```r
# Use appropriate tolerance
expect_equal(pred_formula, pred_xy, tolerance = 1e-5)

# Or investigate why they differ
test_that("understand difference", {
  fit_formula <- fit(spec, y ~ x, data = data)
  fit_xy <- fit_xy(spec, x = data[, "x", drop = FALSE], y = data$y)

  # Check model matrices
  mm_formula <- model.matrix(y ~ x, data = data)
  mm_xy <- as.matrix(data[, "x", drop = FALSE])

  # Should they be the same?
  print(head(mm_formula))
  print(head(mm_xy))
})
```

--------------------------------------------------------------------------------

## Documentation Issues

### Issue: Examples Don't Work

**Symptom:**

```r
# In documentation
#' @examples
#' linear_reg() |> set_engine("glmnet")
# Error when running examples: package not available
```

**Solution:**

```r
# Wrap in \dontrun{} if package may not be installed
#' @examples
#' # Default engine always works
#' linear_reg() |> set_engine("lm")
#'
#' # Optional engine
#' \dontrun{
#' linear_reg() |> set_engine("glmnet")
#' }

# Or use \donttest{} for CRAN
#' @examples
#' \donttest{
#' if (requireNamespace("glmnet", quietly = TRUE)) {
#'   linear_reg() |> set_engine("glmnet")
#' }
#' }
```

### Issue: Unclear Engine Requirements

**Problem:** Users don't know what packages are needed.

**Solution:**

```r
# Document clearly
#' @details
#' ## Engines
#'
#' **lm** (default):
#' - No additional packages required
#' - Uses [stats::lm()]
#'
#' **glmnet**:
#' - Requires: glmnet package
#' - Uses elastic net regularization
#' - Set penalty and mixture arguments
#'
#' **keras**:
#' - Requires: keras and tensorflow packages
#' - Neural network implementation
#' - Set epochs via set_engine()
```

--------------------------------------------------------------------------------

## Performance Issues

### Issue: Slow Data Conversion

**Symptom:** Fitting takes much longer than expected.

**Causes:** 1. Unnecessary data conversions 2. Repeated matrix conversions 3.
Inefficient factor encoding

**Solution:**

```r
# Cache conversions if possible
set_fit(
  ...,
  value = list(
    pre = function(data, object) {
      # Do conversion once, store result
      if (is.null(object$converted_data)) {
        object$converted_data <- expensive_conversion(data)
      }
      object$converted_data
    },
    ...
  )
)

# Or optimize conversion
pre = function(data, object) {
  # Use faster methods
  data.matrix(data)  # Instead of as.matrix()
}
```

### Issue: Memory Usage Too High

**Symptom:** R runs out of memory during fit or predict.

**Causes:** 1. Copying large datasets unnecessarily 2. Creating intermediate
objects 3. Not releasing memory

**Solution:**

```r
# Avoid unnecessary copies
post = function(results, object) {
  # Don't create intermediate objects
  tibble::tibble(.pred = results)  # Direct conversion

  # Instead of:
  # temp <- as.vector(results)
  # temp2 <- as.numeric(temp)
  # tibble::tibble(.pred = temp2)
}

# Clean up after conversion
post = function(results, object) {
  result_tibble <- tibble::tibble(.pred = results)
  rm(results)  # Release memory
  gc()         # Force garbage collection
  result_tibble
}
```

--------------------------------------------------------------------------------

## Version Compatibility Issues

### Issue: Function Signature Changed

**Symptom:**

```r
fit(spec, y ~ x, data = data)
# Error: argument "newarg" is missing
```

Package updated and added required argument.

**Solution:**

```r
# Check version and use appropriate signature
set_fit(
  ...,
  value = list(
    pre = function(data, object) {
      if (packageVersion("package") >= "2.0") {
        # New signature
        list(data = data, newarg = default_value)
      } else {
        # Old signature
        list(data = data)
      }
    },
    ...
  )
)
```

### Issue: Deprecated Function

**Symptom:**

```r
# Warning: 'old_function' is deprecated, use 'new_function'
```

**Solution:**

```r
# Update to new function
set_fit(
  ...,
  value = list(
    func = c(pkg = "package", fun = "new_function"),  # Updated
    ...
  )
)

# Or support both versions
set_fit(
  ...,
  value = list(
    pre = function(data, object) {
      # Choose function based on availability
      if (exists("new_function", where = "package:package")) {
        object$func_to_use <- "new_function"
      } else {
        object$func_to_use <- "old_function"
      }
      data
    },
    ...
  )
)
```

--------------------------------------------------------------------------------

## Debugging Strategies

### Enable Verbose Output

```r
# In registration
set_fit(
  ...,
  value = list(
    pre = function(data, object) {
      message("Pre-processing data...")
      message("Data dimensions: ", nrow(data), " x ", ncol(data))
      data
    },
    ...
  )
)
```

### Inspect Intermediate Results

```r
# Add debugging post-processing
post = function(results, object) {
  message("Raw results class: ", class(results))
  message("Raw results structure: ", str(results))

  formatted <- tibble::tibble(.pred = results)
  message("Formatted results: ", str(formatted))

  formatted
}
```

### Use Browser

```r
# Add interactive debugging
set_pred(
  ...,
  value = list(
    post = function(results, object) {
      browser()  # Stop here for inspection
      tibble::tibble(.pred = results)
    },
    ...
  )
)
```

### Test Registration Directly

```r
# Check registration exists
env <- parsnip:::get_model_env()
ls(env)  # See all registered models

# Get specific registration
fit_info <- parsnip:::get_from_env("linear_reg_fit")
pred_info <- parsnip:::get_from_env("linear_reg_predict")
```

--------------------------------------------------------------------------------

## Getting Help

### Check Existing Implementations

Look at similar models in parsnip source:

```r
# How did linear_reg implement glmnet?
# R/linear_reg_data.R - find glmnet section

# How did boost_tree handle multi-mode?
# R/boost_tree_data.R - see both modes
```

### Run Parsnip Tests

```r
# Run specific test file
testthat::test_file("tests/testthat/test-linear_reg.R")

# Run all tests
devtools::test()
```

### Check Package Status

```r
# Full package check
devtools::check()

# Quick check
devtools::load_all()
devtools::test()
```

--------------------------------------------------------------------------------

## Summary

**Common issue categories:**

1. **Registration** - Missing set\_\* calls, typos, wrong names
2. **Fit method** - Interface type, argument translation, data conversion
3. **Predict method** - Column names, data types, dimensions
4. **Encoding** - Dummy variables, intercept, factor levels
5. **Dependencies** - Missing packages, wrong function names
6. **Multi-mode** - Mode selection, mode-specific behavior
7. **Testing** - Package availability, interface equivalence
8. **Documentation** - Example failures, unclear requirements

**Debugging checklist:**

- [ ] Check registration with `show_engines()`

- [ ] Verify package dependencies with `set_dependency()`

- [ ] Test both formula and xy interfaces

- [ ] Inspect intermediate results with print/message

- [ ] Use `browser()` for interactive debugging

- [ ] Check existing implementations for patterns

- [ ] Run relevant test files

- [ ] Use `devtools::check()` for comprehensive validation

**When stuck:** 1. Look at similar models in parsnip source 2. Run existing
tests to see patterns 3. Use verbose output and browser() 4. Ask on GitHub
issues or tidymodels Slack
