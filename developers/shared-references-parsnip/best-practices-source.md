# Best Practices for Parsnip Source Development

Guidelines and best practices for contributing to the parsnip package source code.

---

## Overview

When contributing to parsnip itself (not creating extensions), follow these practices to maintain code quality and consistency with the existing codebase.

---

## Code Organization

### File Structure

**Model constructors:** `R/[model_type].R`
```r
R/linear_reg.R      # linear_reg() constructor
R/boost_tree.R      # boost_tree() constructor
R/rand_forest.R     # rand_forest() constructor
```

**Engine registrations:** `R/[model]_data.R`
```r
R/linear_reg_data.R     # All linear_reg engines
R/boost_tree_data.R     # All boost_tree engines
```

**Infrastructure:** Core system files
```r
R/aaa_models.R      # Model environment setup
R/misc.R            # Helper functions
R/fit.R             # Fit methods
R/predict.R         # Predict methods
```

### Group Related Code

Keep all engines for a model in the same file:

```r
# R/linear_reg_data.R

# lm engine
set_model_engine("linear_reg", "regression", "lm")
set_dependency(...)
set_fit(...)
set_pred(...)

# glmnet engine
set_model_engine("linear_reg", "regression", "glmnet")
set_dependency(...)
set_fit(...)
set_pred(...)

# keras engine
set_model_engine("linear_reg", "regression", "keras")
set_dependency(...)
set_fit(...)
set_pred(...)
```

---

## Registration Patterns

### Complete Registration Sequence

For each engine, register in this order:

```r
# 1. Declare engine exists
set_model_engine(
  model = "linear_reg",
  mode = "regression",
  eng = "glmnet"
)

# 2. Declare package dependencies
set_dependency(
  model = "linear_reg",
  eng = "glmnet",
  pkg = "glmnet",
  mode = "regression"
)

# 3. Translate main arguments
set_model_arg(
  model = "linear_reg",
  eng = "glmnet",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = TRUE
)

# 4. Register fit method
set_fit(
  model = "linear_reg",
  eng = "glmnet",
  mode = "regression",
  value = list(...)
)

# 5. Register encoding (if needed)
set_encoding(
  model = "linear_reg",
  eng = "glmnet",
  mode = "regression",
  options = list(...)
)

# 6. Register each prediction type
set_pred(
  model = "linear_reg",
  eng = "glmnet",
  mode = "regression",
  type = "numeric",
  value = list(...)
)

set_pred(
  model = "linear_reg",
  eng = "glmnet",
  mode = "regression",
  type = "conf_int",
  value = list(...)
)
```

### Use Consistent Naming

**Main arguments:** Follow established parsnip conventions
```r
# ✓ Good - consistent with other models
penalty    # not lambda, not reg_param
mixture    # not alpha, not l1_ratio
trees      # not n_estimators, not num_boost_round
```

**Engine names:** Use package or algorithm name
```r
# ✓ Good
"lm"        # From stats package
"glmnet"    # From glmnet package
"xgboost"   # From xgboost package

# ✗ Avoid
"linear_model"
"elastic_net"
"boosted_trees"
```

---

## Using Internal Functions

### When to Use Internal Functions

Source development can use internal parsnip functions:

```r
# ✓ Allowed in parsnip source
func = c(pkg = "parsnip", fun = "xgb_train")  # Internal helper

# Helper functions for complex conversions
pre = function(new_data, object) {
  parsnip:::prepare_data_for_engine(new_data, object)
}
```

### Common Internal Helpers

**Data conversion:**
```r
parsnip:::convert_data_to_matrix()
parsnip:::prepare_survival_data()
```

**Prediction post-processing:**
```r
parsnip:::format_class_predictions()
parsnip:::format_prob_matrix()
```

**Validation:**
```r
parsnip:::check_outcome_type()
parsnip:::validate_prediction_type()
```

### Document Internal Function Usage

When using internal functions, add comments explaining why:

```r
set_pred(
  ...,
  value = list(
    # Using internal helper for complex survival curve extraction
    post = function(results, object) {
      parsnip:::extract_surv_curves(results, object)
    },
    ...
  )
)
```

---

## Error Handling

### Use Informative Error Messages

```r
# ✓ Good - explains the problem and solution
post = function(results, object) {
  if (!inherits(results, "expected_class")) {
    rlang::abort(
      "Expected output from engine to be class 'expected_class'",
      "i" = "Check that the engine is returning the correct format",
      "i" = "Consider updating the engine package"
    )
  }
  format_results(results)
}

# ✗ Bad - generic error
post = function(results, object) {
  if (!inherits(results, "expected_class")) {
    stop("Wrong type")
  }
  format_results(results)
}
```

### Validate at Registration Time

Check for common issues early:

```r
set_fit(
  ...,
  value = list(
    interface = "matrix",
    protect = c("x", "y"),
    func = c(pkg = "glmnet", fun = "glmnet"),
    defaults = list(family = "gaussian")
  )
)

# Validate that function exists
if (!requireNamespace("glmnet", quietly = TRUE)) {
  rlang::warn("glmnet package not available for testing")
}
```

---

## Testing

### Test Files Organization

**Model-specific tests:** `tests/testthat/test-[model].R`
```r
tests/testthat/test-boost_tree.R
tests/testthat/test-linear_reg.R
```

**Engine-specific tests:** Within model test file
```r
# In test-linear_reg.R

test_that("lm engine works", { ... })
test_that("glmnet engine works", { ... })
test_that("keras engine works", { ... })
```

### Essential Tests for Each Engine

```r
test_that("glmnet engine fits and predicts", {
  skip_if_not_installed("glmnet")

  # Fit
  spec <- linear_reg(penalty = 0.1) |>
    set_engine("glmnet") |>
    set_mode("regression")

  fit <- fit(spec, mpg ~ ., data = mtcars)
  expect_s3_class(fit, "model_fit")

  # Predict
  preds <- predict(fit, mtcars[1:5, ])
  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
})

test_that("glmnet engine handles factors", {
  skip_if_not_installed("glmnet")

  data <- data.frame(
    y = 1:10,
    x1 = 1:10,
    x2 = factor(rep(c("A", "B"), 5))
  )

  spec <- linear_reg() |> set_engine("glmnet")
  fit <- fit(spec, y ~ x1 + x2, data = data)

  # Predictions should work
  preds <- predict(fit, data[1:3, ])
  expect_equal(nrow(preds), 3)
})

test_that("glmnet engine supports multiple prediction types", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg() |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  # Numeric
  pred_num <- predict(fit, mtcars[1:5, ], type = "numeric")
  expect_named(pred_num, ".pred")

  # Raw
  pred_raw <- predict(fit, mtcars[1:5, ], type = "raw")
  expect_true(!is.null(pred_raw))
})
```

### Test Both Formula and XY Interfaces

```r
test_that("formula and xy interfaces produce same results", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg() |> set_engine("glmnet")

  # Formula
  fit_formula <- fit(spec, mpg ~ hp + wt, data = mtcars)
  pred_formula <- predict(fit_formula, mtcars[1:5, ])

  # XY
  fit_xy <- fit_xy(spec, x = mtcars[, c("hp", "wt")], y = mtcars$mpg)
  pred_xy <- predict(fit_xy, mtcars[1:5, ])

  # Should match
  expect_equal(pred_formula, pred_xy, tolerance = 1e-5)
})
```

### Test Error Conditions

```r
test_that("glmnet engine errors appropriately", {
  skip_if_not_installed("glmnet")

  spec <- linear_reg() |> set_engine("glmnet")

  # Wrong mode
  expect_error(
    fit(spec, Species ~ ., data = iris),
    "factor"
  )

  # Missing data (if engine doesn't handle it)
  data_na <- mtcars
  data_na$mpg[1] <- NA
  expect_error(
    fit(spec, mpg ~ ., data = data_na),
    "missing"
  )
})
```

---

## Documentation

### Model Constructor Documentation

Follow roxygen2 conventions:

```r
#' Linear Regression
#'
#' `linear_reg()` defines a model that can predict a numeric outcome from
#' one or more predictors.
#'
#' @param mode A single character string for the model type. The only possible
#'   value for this model is "regression".
#' @param penalty A non-negative number for the amount of regularization
#'   (glmnet, keras engines only). Used by glmnet as `lambda` and by keras
#'   as the L2 penalty.
#' @param mixture A number between 0 and 1 for the proportion of L1
#'   regularization. Used by glmnet and keras engines.
#' @param engine A character string for the software to fit the model.
#'   Default is "lm".
#'
#' @details
#' The available engines are:
#' - `"lm"` (default) - Uses [stats::lm()]
#' - `"glmnet"` - Uses [glmnet::glmnet()]
#' - `"keras"` - Uses keras neural network
#'
#' @seealso [fit.model_spec()], [set_engine()]
#'
#' @examples
#' # Basic linear regression
#' linear_reg() |>
#'   set_engine("lm") |>
#'   fit(mpg ~ ., data = mtcars)
#'
#' # Regularized regression
#' linear_reg(penalty = 0.1, mixture = 0.5) |>
#'   set_engine("glmnet") |>
#'   fit(mpg ~ ., data = mtcars)
#'
#' @export
linear_reg <- function(mode = "regression",
                       penalty = NULL,
                       mixture = NULL,
                       engine = "lm") {
  # Implementation
}
```

### Document Engine Requirements

Explain what each engine needs:

```r
#' @details
#' ## Engine: glmnet
#'
#' Requires the glmnet package. This engine uses elastic net regularization.
#'
#' **Main arguments:**
#' - `penalty` → `lambda` - Amount of regularization
#' - `mixture` → `alpha` - Mix of L1 and L2 (0 = ridge, 1 = lasso)
#'
#' **Engine-specific arguments:**
#' - `nlambda` - Number of lambda values (default: 100)
#' - `standardize` - Standardize predictors (default: TRUE)
#' - Pass to `set_engine("glmnet", nlambda = 50)`
#'
#' **Prediction types:**
#' - `numeric` - Point predictions
#' - `raw` - Raw glmnet object
```

### Add Examples for Each Engine

```r
#' @examples
#' # lm engine (default)
#' linear_reg() |>
#'   fit(mpg ~ ., data = mtcars)
#'
#' # glmnet engine with regularization
#' linear_reg(penalty = 0.1) |>
#'   set_engine("glmnet") |>
#'   fit(mpg ~ ., data = mtcars)
#'
#' # keras engine with custom architecture
#' linear_reg() |>
#'   set_engine("keras", epochs = 100) |>
#'   fit(mpg ~ ., data = mtcars)
```

---

## Argument Translation

### Follow Tidymodels Naming

When translating main arguments to engine arguments:

```r
# ✓ Good - clear translation
set_model_arg(
  model = "boost_tree",
  eng = "xgboost",
  parsnip = "trees",        # Tidymodels standard
  original = "nrounds",     # xgboost name
  func = list(pkg = "dials", fun = "trees"),
  has_submodel = TRUE
)

# ✗ Avoid engine-specific names in main arguments
set_model_arg(
  model = "boost_tree",
  eng = "xgboost",
  parsnip = "nrounds",      # Too xgboost-specific
  original = "nrounds",
  ...
)
```

### Document Argument Mappings

```r
# In R/boost_tree_data.R

# xgboost engine
# Argument translations:
# - trees → nrounds
# - tree_depth → max_depth
# - learn_rate → eta
# - loss_reduction → gamma

set_model_arg(...)
```

---

## Compatibility Considerations

### Package Version Requirements

Document minimum versions when needed:

```r
set_dependency(
  model = "linear_reg",
  eng = "glmnet",
  pkg = "glmnet",
  mode = "regression"
)

# If specific version needed, add to DESCRIPTION
# Imports: glmnet (>= 4.0)
```

### Handle Package Changes

Add version checks for breaking changes:

```r
set_fit(
  ...,
  value = list(
    pre = function(data, object) {
      # Handle glmnet version differences
      if (packageVersion("glmnet") >= "4.0") {
        # New behavior
      } else {
        # Old behavior
      }
      data
    },
    ...
  )
)
```

---

## Multi-Mode Implementation

### Register Each Mode Separately

```r
# Register both modes
set_model_mode(model = "boost_tree", mode = "regression")
set_model_mode(model = "boost_tree", mode = "classification")

# Fit for regression
set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "regression",
  value = list(
    defaults = list(objective = "reg:squarederror")
  )
)

# Fit for classification
set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "classification",
  value = list(
    defaults = list(objective = "multi:softprob")
  )
)
```

### Share Common Code

Extract common patterns:

```r
# Internal helper function
xgb_train_wrapper <- function(x, y, ...) {
  # Common xgboost setup
  dtrain <- xgb.DMatrix(data = x, label = y)
  xgb.train(data = dtrain, ...)
}

# Use in both modes
set_fit(
  ...,
  mode = "regression",
  value = list(
    func = c(pkg = "parsnip", fun = "xgb_train_wrapper"),
    ...
  )
)

set_fit(
  ...,
  mode = "classification",
  value = list(
    func = c(pkg = "parsnip", fun = "xgb_train_wrapper"),
    ...
  )
)
```

---

## Performance Considerations

### Lazy Evaluation

Use `rlang::expr()` to delay evaluation:

```r
# ✓ Good - delays evaluation
args = list(
  object = rlang::expr(object$fit),
  newdata = rlang::expr(new_data)
)

# ✗ Bad - evaluates immediately
args = list(
  object = object$fit,      # object doesn't exist yet!
  newdata = new_data        # new_data doesn't exist yet!
)
```

### Avoid Unnecessary Conversions

```r
# ✓ Good - only convert if needed
post = function(results, object) {
  if (is.matrix(results)) {
    tibble::as_tibble(results)
  } else {
    tibble::tibble(.pred = results)
  }
}

# ✗ Bad - always converts (unnecessary for vectors)
post = function(results, object) {
  results <- as.matrix(results)  # Wasteful if already correct type
  tibble::as_tibble(results)
}
```

---

## Summary

**Key practices:**

1. **Follow file organization** - Constructors in `R/[model].R`, registrations in `R/[model]_data.R`
2. **Complete registration sequence** - Engine, dependency, args, fit, encoding, predictions
3. **Use consistent naming** - Follow tidymodels conventions for main arguments
4. **Can use internal functions** - Source development has access to `:::` functions
5. **Write comprehensive tests** - Test each engine, both interfaces, error conditions
6. **Document thoroughly** - Model constructor, engine details, argument translations
7. **Handle multi-mode carefully** - Register each mode separately, share common code
8. **Consider performance** - Use lazy evaluation, avoid unnecessary conversions

**Before submitting:**

- Run `devtools::check()` to verify package integrity

- Ensure all tests pass

- Update NEWS.md with changes

- Follow tidymodels code style

- Add examples to documentation
