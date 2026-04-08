# Implementing Fit and Predict Methods

This guide covers how to implement fit and predict methods for parsnip models.
This applies to both new model specifications and new engines.

--------------------------------------------------------------------------------

## Overview

The fit/predict lifecycle in parsnip:

1. **User calls `fit()`** with model spec, formula/data
2. **parsnip translates** arguments and prepares data
3. **Engine function** is called to fit the model
4. **Result wrapped** in `model_fit` object
5. **User calls `predict()`** with new data and type
6. **Engine prediction** function is called
7. **Result standardized** to tibble format with `.pred` columns

--------------------------------------------------------------------------------

## Fit Method Structure

### Standard Signature

```r
fit(object, formula, data, control = control_parsnip(), ...)
```

**Arguments:**

- `object` - Model specification

- `formula` - Model formula

- `data` - Training data

- `control` - Control object for verbosity, error handling

- `...` - Additional arguments passed to engine

### Fit Implementation via `set_fit()`

Instead of writing `fit.model_spec()` methods directly, you use `set_fit()` to
register how to fit:

```r
set_fit(
  model = "linear_reg",
  eng = "lm",
  mode = "regression",
  value = list(
    interface = "formula",
    protect = c("formula", "data"),
    func = c(pkg = "stats", fun = "lm"),
    defaults = list()
  )
)
```

**Components:**

**`interface`** - How data is passed to the engine:

- `"formula"` - Formula interface: `lm(formula, data)`

- `"matrix"` - Matrix interface: `glmnet(x, y)`

- `"xy"` - Separate x and y: `knn(train = x, cl = y)`

**`protect`** - Arguments that shouldn't be overridden by user

**`func`** - The function to call (package and function name)

**`defaults`** - Default arguments to pass to the engine

### Data Preparation

parsnip handles data conversion based on `interface`:

**Formula interface (`"formula"`):**

```r
# User provides:
fit(spec, mpg ~ hp + wt, data = mtcars)

# Engine receives:
lm(formula = mpg ~ hp + wt, data = mtcars)
```

**Matrix interface (`"matrix"`):**

```r
# User provides:
fit(spec, mpg ~ hp + wt, data = mtcars)

# Engine receives:
glmnet(x = as.matrix(mtcars[, c("hp", "wt")]), y = mtcars$mpg)
```

parsnip automatically converts formula to matrices.

**XY interface (`"xy"`):**

```r
# User can provide:
fit_xy(spec, x = predictors, y = outcome)

# Or from formula:
fit(spec, mpg ~ hp + wt, data = mtcars)
# Converted to x/y internally
```

### Calling the Engine Function

The `func` specification tells parsnip what to call:

```r
func = c(pkg = "stats", fun = "lm")
# Becomes: stats::lm(...)

func = c(pkg = "xgboost", fun = "xgb.train")
# Becomes: xgboost::xgb.train(...)
```

### Wrapping in `model_fit`

parsnip automatically wraps the result:

```r
# Engine returns lm object
fit_result <- lm(mpg ~ hp, data = mtcars)

# parsnip wraps it:
model_fit <- structure(
  list(
    spec = original_spec,
    fit = fit_result,
    preproc = preprocessing_info
  ),
  class = "model_fit"
)
```

--------------------------------------------------------------------------------

## Predict Method Structure

### Standard Signature

```r
predict(object, new_data, type = "numeric", ...)
```

**Arguments:**

- `object` - Fitted model (`model_fit`)

- `new_data` - Data frame with new observations

- `type` - Type of prediction (depends on mode)

- `...` - Additional arguments

### Prediction Implementation via `set_pred()`

Register each prediction type separately:

```r
set_pred(
  model = "linear_reg",
  eng = "lm",
  mode = "regression",
  type = "numeric",
  value = list(
    pre = NULL,
    post = NULL,
    func = c(fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data),
      type = "response"
    )
  )
)
```

**Components:**

**`pre`** - Function to run before prediction (data preparation)

**`post`** - Function to run after prediction (format conversion)

**`func`** - The prediction function to call

**`args`** - Arguments to pass (using `rlang::expr()` for delayed evaluation)

### Pre-Processing (`pre`)

Use `pre` when you need to prepare data before prediction:

```r
pre = function(new_data, object) {
  # Convert factors to integers for this engine
  new_data$category <- as.integer(new_data$category)
  new_data
}
```

**Signature:** `function(new_data, object)`

**Returns:** Modified `new_data`

### Post-Processing (`post`)

Use `post` to convert engine output to standard format:

```r
post = function(results, object) {
  # Engine returns matrix with columns "lower", "upper"
  # Convert to tibble with standard names
  tibble::tibble(
    .pred_lower = results[, "lower"],
    .pred_upper = results[, "upper"]
  )
}
```

**Signature:** `function(results, object)`

**Returns:** Tibble with standardized column names

### Prediction Function Arguments

Use `rlang::expr()` to delay evaluation:

```r
args = list(
  object = rlang::expr(object$fit),  # The fitted model
  newdata = rlang::expr(new_data),   # New data
  type = "response"                   # Static argument
)
```

**Why `rlang::expr()`?**

- Prevents evaluation until prediction time

- Allows access to the actual fitted object

- Enables proper scoping

### Multiple Prediction Types

Register each type separately:

```r
# Numeric predictions
set_pred(..., type = "numeric", ...)

# Confidence intervals
set_pred(..., type = "conf_int", ...)

# Raw predictions
set_pred(..., type = "raw", ...)
```

Each can have different `pre`, `post`, and `args`.

--------------------------------------------------------------------------------

## Common Implementation Patterns

### Pattern 1: Formula-Based Fit

**Example: lm engine for linear_reg**

```r
set_fit(
  model = "linear_reg",
  eng = "lm",
  mode = "regression",
  value = list(
    interface = "formula",
    protect = c("formula", "data"),
    func = c(pkg = "stats", fun = "lm"),
    defaults = list()
  )
)
```

Simple and direct - parsnip handles everything.

### Pattern 2: Matrix-Based Fit

**Example: glmnet engine**

```r
set_fit(
  model = "linear_reg",
  eng = "glmnet",
  mode = "regression",
  value = list(
    interface = "matrix",
    protect = c("x", "y", "weights"),
    func = c(pkg = "glmnet", fun = "glmnet"),
    defaults = list(family = "gaussian")
  )
)
```

parsnip converts formula to matrices automatically.

### Pattern 3: Simple Prediction

**Example: Numeric prediction with lm**

```r
set_pred(
  model = "linear_reg",
  eng = "lm",
  mode = "regression",
  type = "numeric",
  value = list(
    pre = NULL,
    post = NULL,
    func = c(fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data),
      type = "response"
    )
  )
)
```

Direct call to `predict()` method, no transformation needed.

### Pattern 4: Prediction with Post-Processing

**Example: Confidence intervals**

```r
set_pred(
  model = "linear_reg",
  eng = "lm",
  mode = "regression",
  type = "conf_int",
  value = list(
    pre = NULL,
    post = function(results, object) {
      tibble::tibble(
        .pred_lower = results[, "lwr"],
        .pred_upper = results[, "upr"]
      )
    },
    func = c(fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data),
      interval = "confidence",
      level = 0.95
    )
  )
)
```

Engine returns matrix, `post` converts to standard format.

### Pattern 5: Multi-Mode Model

**Example: Model supporting both regression and classification**

```r
# Regression fit
set_fit(
  model = "my_model",
  eng = "custom",
  mode = "regression",
  value = list(...)
)

# Classification fit
set_fit(
  model = "my_model",
  eng = "custom",
  mode = "classification",
  value = list(...)
)

# Regression prediction
set_pred(
  model = "my_model",
  eng = "custom",
  mode = "regression",
  type = "numeric",
  value = list(...)
)

# Classification predictions
set_pred(
  model = "my_model",
  eng = "custom",
  mode = "classification",
  type = "class",
  value = list(...)
)

set_pred(
  model = "my_model",
  eng = "custom",
  mode = "classification",
  type = "prob",
  value = list(...)
)
```

Register fit and predictions separately for each mode.

--------------------------------------------------------------------------------

## Column Naming Conventions

parsnip has strict conventions for prediction column names:

**Numeric predictions:**

```r
tibble::tibble(.pred = c(1.2, 3.4, 5.6))
```

**Class predictions:**

```r
tibble::tibble(.pred_class = factor(c("A", "B", "A")))
```

**Probability predictions:**

```r
tibble::tibble(
  .pred_A = c(0.8, 0.2, 0.7),
  .pred_B = c(0.2, 0.8, 0.3)
)
```

**Confidence intervals:**

```r
tibble::tibble(
  .pred_lower = c(1.0, 3.0, 5.0),
  .pred_upper = c(1.5, 4.0, 6.0)
)
```

Always use these exact names in `post` functions.

--------------------------------------------------------------------------------

## Error Handling

### Missing Required Packages

Check for packages before fitting:

```r
set_dependency(
  model = "boost_tree",
  eng = "xgboost",
  pkg = "xgboost",
  mode = "regression"
)
```

parsnip will error with helpful message if package not installed.

### Incompatible Mode/Type Combinations

Only register prediction types that make sense:

```r
# DON'T register "prob" for regression models
# DON'T register "numeric" for classification models
```

parsnip will error if user requests unavailable type.

### Invalid New Data

Engine functions handle this, but you can add validation in `pre`:

```r
pre = function(new_data, object) {
  if (nrow(new_data) == 0) {
    rlang::abort("new_data must have at least one row")
  }
  new_data
}
```

--------------------------------------------------------------------------------

## Testing Fit and Predict

Essential tests for any fit/predict implementation:

**Fit tests:**

```r
test_that("model fits with formula", {
  spec <- my_model() |> set_engine("custom")
  fit <- fit(spec, mpg ~ ., data = mtcars)
  expect_s3_class(fit, "model_fit")
})

test_that("model fits with xy", {
  spec <- my_model() |> set_engine("custom")
  fit <- fit_xy(spec, x = mtcars[, -1], y = mtcars$mpg)
  expect_s3_class(fit, "model_fit")
})
```

**Predict tests:**

```r
test_that("numeric predictions work", {
  spec <- my_model() |> set_engine("custom")
  fit <- fit(spec, mpg ~ ., data = mtcars)
  preds <- predict(fit, new_data = mtcars[1:5, ])

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
})

test_that("predictions match new_data rows", {
  spec <- my_model() |> set_engine("custom")
  fit <- fit(spec, mpg ~ ., data = mtcars)
  preds <- predict(fit, new_data = mtcars[1:10, ])

  expect_equal(nrow(preds), 10)
})
```

**Interface tests:**

```r
test_that("formula and xy produce same results", {
  spec <- my_model() |> set_engine("custom")

  fit_formula <- fit(spec, mpg ~ hp + wt, data = mtcars)
  fit_xy <- fit_xy(spec, x = mtcars[, c("hp", "wt")], y = mtcars$mpg)

  pred_formula <- predict(fit_formula, mtcars[1:5, ])
  pred_xy <- predict(fit_xy, mtcars[1:5, ])

  expect_equal(pred_formula, pred_xy, tolerance = 1e-5)
})
```

--------------------------------------------------------------------------------

## Extension vs Source Development

### Extension Development

When creating engines in your own package:

**Always use `parsnip::` prefix:**

```r
parsnip::set_fit(...)
parsnip::set_pred(...)
```

**You can only use exported functions:**

```r
func = c(pkg = "stats", fun = "lm")  # ✅ Exported
func = c(fun = "lm")                  # ✅ Also works
```

### Source Development

When contributing to parsnip itself:

**No prefix needed:**

```r
set_fit(...)
set_pred(...)
```

**Can reference internal functions:**

```r
func = c(pkg = "parsnip", fun = "xgb_train")  # Internal helper
```

**Follow parsnip file organization:**

- Fit/predict code in `R/[model]_data.R`

- Group all engines for a model together

--------------------------------------------------------------------------------

## Summary

Implementing fit and predict:

1. **Use `set_fit()`** to register fitting function and interface
2. **Use `set_pred()`** for each prediction type
3. **Use `pre`** for data preparation
4. **Use `post`** for result formatting
5. **Use `rlang::expr()`** for argument evaluation
6. **Follow column naming conventions** strictly
7. **Register each mode separately** if multi-mode
8. **Test thoroughly** with different data types and interfaces

The registration system handles most complexity - you just specify what to call
and how to format results.
