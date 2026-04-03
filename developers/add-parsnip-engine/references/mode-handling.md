# Mode Handling in Parsnip

This guide covers how to work with modes in parsnip models, including setting modes, mode-specific behaviors, and implementing multi-mode models.

---

## Overview

**Mode** determines what type of prediction task the model performs. It affects:

- Available prediction types

- Default behavior

- Validation rules

- Required arguments

Parsnip supports four modes:

- `"regression"` - Numeric outcomes

- `"classification"` - Categorical outcomes

- `"censored regression"` - Survival/time-to-event data

- `"quantile regression"` - Quantile predictions

---

## Mode Basics

### What Modes Control

**Available prediction types:**

**Regression:**

- `numeric`, `conf_int`, `pred_int`, `raw`

**Classification:**

- `class`, `prob`, `raw`

**Censored regression:**

- `time`, `survival`, `hazard`, `linear_pred`, `raw`

**Quantile regression:**

- `quantile`, `raw`

**Validation:**

- Parsnip checks that mode matches outcome type

- Prevents incompatible mode-type combinations (e.g., `prob` with regression)

**Engine availability:**

- Not all engines support all modes

- Some engines are mode-specific

### Setting Modes

**In model constructor:**
```r
# Default mode
linear_reg(mode = "regression")

# Explicitly set
boost_tree(mode = "classification")
```

**With `set_mode()`:**
```r
# Change mode after creation
spec <- nearest_neighbor() |>
  set_mode("classification")
```

**Mode is required before fitting:**
```r
# This will error
spec <- nearest_neighbor()
fit(spec, Species ~ ., data = iris)
#> Error: Please set the mode

# Must set mode first
spec <- nearest_neighbor() |> set_mode("classification")
fit(spec, Species ~ ., data = iris)  # ✓ Works
```

---

## Single-Mode Models

Most models support only one mode.

### Regression-Only Models

```r
linear_reg()
#> Linear Regression Model Specification (regression)

linear_reg() |> set_mode("classification")
#> Error: linear_reg can only be used for regression
```

**Registration:**
```r
set_model_mode(
  model = "linear_reg",
  mode = "regression"
)

# Only register for regression mode
set_fit(
  model = "linear_reg",
  eng = "lm",
  mode = "regression",  # Only this mode
  value = list(...)
)
```

**Characteristics:**

- Mode is fixed in model definition

- Constructor sets mode automatically

- Users cannot change mode

- Clearer intent and less confusion

### Classification-Only Models

```r
logistic_reg()
#> Logistic Regression Model Specification (classification)

logistic_reg() |> set_mode("regression")
#> Error: logistic_reg can only be used for classification
```

**Registration:**
```r
set_model_mode(
  model = "logistic_reg",
  mode = "classification"
)

set_fit(
  model = "logistic_reg",
  eng = "glm",
  mode = "classification",
  value = list(...)
)
```

---

## Multi-Mode Models

Some models can be used for multiple tasks.

### Implementation Pattern

**Register each mode separately and completely.** Each mode needs its own set_model_engine(), set_dependency(), set_fit() with mode-specific defaults, and set_pred() calls. Classification needs both "class" AND "prob" prediction types.

See examples below for complete patterns.

### Models Supporting Multiple Modes

**Common examples:**

**`boost_tree()`** - Regression and classification:
```r
# For regression
boost_tree(mode = "regression") |>
  set_engine("xgboost")

# For classification
boost_tree(mode = "classification") |>
  set_engine("xgboost")
```

**`nearest_neighbor()`** - Regression and classification:
```r
nearest_neighbor(mode = "regression")
nearest_neighbor(mode = "classification")
```

**`decision_tree()`** - Regression and classification:
```r
decision_tree(mode = "regression")
decision_tree(mode = "classification")
```

### Implementing Multi-Mode Models

**Register all modes:**
```r
# Declare both modes are supported
set_model_mode(
  model = "boost_tree",
  mode = "regression"
)

set_model_mode(
  model = "boost_tree",
  mode = "classification"
)
```

**Register fit for each mode:**
```r
# Regression fit
set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "regression",
  value = list(
    interface = "matrix",
    func = c(pkg = "xgboost", fun = "xgb.train"),
    ...
  )
)

# Classification fit
set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "classification",
  value = list(
    interface = "matrix",
    func = c(pkg = "xgboost", fun = "xgb.train"),
    ...
  )
)
```

**Register predictions for each mode:**
```r
# Regression predictions
set_pred(
  model = "boost_tree",
  eng = "xgboost",
  mode = "regression",
  type = "numeric",
  value = list(...)
)

# Classification predictions
set_pred(
  model = "boost_tree",
  eng = "xgboost",
  mode = "classification",
  type = "class",
  value = list(...)
)

set_pred(
  model = "boost_tree",
  eng = "xgboost",
  mode = "classification",
  type = "prob",
  value = list(...)
)
```

### Mode-Specific Arguments

Some engine arguments may differ by mode:

```r
# Regression might need different objective
set_model_arg(
  model = "boost_tree",
  eng = "xgboost",
  parsnip = "trees",
  original = "nrounds",
  func = list(pkg = "dials", fun = "trees"),
  has_submodel = TRUE
)

# Classification uses same argument name but different engine defaults
set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "classification",
  value = list(
    interface = "matrix",
    func = c(pkg = "xgboost", fun = "xgb.train"),
    defaults = list(
      objective = "multi:softprob"  # Classification default
    )
  )
)

set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "regression",
  value = list(
    interface = "matrix",
    func = c(pkg = "xgboost", fun = "xgb.train"),
    defaults = list(
      objective = "reg:squarederror"  # Regression default
    )
  )
)
```

---

## Mode Detection and Validation

### Automatic Mode Setting

For single-mode models, mode is set automatically:

```r
spec <- linear_reg()
spec$mode
#> [1] "regression"
```

### Mode Validation at Fit Time

Parsnip validates mode compatibility:

```r
# Wrong mode for outcome
spec <- logistic_reg() |> set_engine("glm")
fit(spec, mpg ~ ., data = mtcars)  # mpg is numeric
#> Error: For a classification model, the outcome should be a factor
```

### Checking Mode Before Fitting

```r
spec <- nearest_neighbor()

if (is.null(spec$mode) || spec$mode == "unknown") {
  spec <- set_mode(spec, "classification")
}
```

---

## Mode-Specific Prediction Behavior

### Different Functions by Mode

Same prediction type name, different behavior:

```r
# Regression: numeric predictions
spec_reg <- boost_tree(mode = "regression") |> set_engine("xgboost")
fit_reg <- fit(spec_reg, mpg ~ ., data = mtcars)
predict(fit_reg, mtcars[1:3, ], type = "numeric")
#> # A tibble: 3 × 1
#>   .pred
#>   <dbl>
#> 1  21.4
#> 2  21.4
#> 3  22.8

# Classification: class predictions
spec_cls <- boost_tree(mode = "classification") |> set_engine("xgboost")
fit_cls <- fit(spec_cls, Species ~ ., data = iris)
predict(fit_cls, iris[1:3, ], type = "class")
#> # A tibble: 3 × 1
#>   .pred_class
#>   <fct>
#> 1 setosa
#> 2 setosa
#> 3 setosa
```

### Mode-Specific Error Messages

```r
# Requesting inappropriate type for mode
spec <- linear_reg() |> set_engine("lm")
fit <- fit(spec, mpg ~ ., data = mtcars)
predict(fit, mtcars, type = "prob")
#> Error: `type = 'prob'` is not available for regression models
```

---

## Engine-Mode Compatibility

### Engine May Support Subset of Modes

Not all engines support all modes a model might have:

```r
# boost_tree supports regression and classification
# But a specific engine might only support one

# xgboost supports both
boost_tree(mode = "regression") |> set_engine("xgboost")  # ✓
boost_tree(mode = "classification") |> set_engine("xgboost")  # ✓

# Some hypothetical engine might only support regression
boost_tree(mode = "regression") |> set_engine("other")  # ✓
boost_tree(mode = "classification") |> set_engine("other")  # ✗
```

**Check available combinations:**
```r
parsnip::show_engines("boost_tree")
#> Shows which engines support which modes
```

### Registering Engine for Specific Modes Only

```r
# Engine only supports classification
set_model_engine(
  model = "boost_tree",
  mode = "classification",
  eng = "C50"
)

# Don't register for regression
# No set_model_engine() call with mode = "regression"
```

---

## Unknown Mode Pattern

Some models start with `mode = "unknown"`:

```r
spec <- nearest_neighbor()
spec$mode
#> [1] "unknown"

# Must set before fitting
spec <- spec |> set_mode("classification")
```

**Why use unknown?**

- Model genuinely supports multiple modes

- Forces user to make explicit choice

- Prevents accidental misuse

**Don't use unknown if:**

- Model only supports one mode (set it automatically)

- There's a clear default mode

---

## Testing Mode Behavior

### Test Single-Mode Models

```r
test_that("linear_reg only accepts regression mode", {
  expect_error(
    linear_reg() |> set_mode("classification"),
    "only be used for regression"
  )
})

test_that("mode is set automatically", {
  spec <- linear_reg()
  expect_equal(spec$mode, "regression")
})
```

### Test Multi-Mode Models

```r
test_that("boost_tree accepts both modes", {
  spec_reg <- boost_tree(mode = "regression")
  spec_cls <- boost_tree(mode = "classification")

  expect_equal(spec_reg$mode, "regression")
  expect_equal(spec_cls$mode, "classification")
})

test_that("boost_tree works with both modes", {
  # Regression
  spec_reg <- boost_tree(trees = 5) |>
    set_engine("xgboost") |>
    set_mode("regression")
  fit_reg <- fit(spec_reg, mpg ~ ., data = mtcars)
  pred_reg <- predict(fit_reg, mtcars[1:3, ])

  expect_s3_class(pred_reg, "tbl_df")
  expect_named(pred_reg, ".pred")

  # Classification
  spec_cls <- boost_tree(trees = 5) |>
    set_engine("xgboost") |>
    set_mode("classification")
  fit_cls <- fit(spec_cls, Species ~ ., data = iris)
  pred_cls <- predict(fit_cls, iris[1:3, ])

  expect_s3_class(pred_cls, "tbl_df")
  expect_named(pred_cls, ".pred_class")
})
```

### Test Mode Validation

```r
test_that("mode must be set before fitting", {
  spec <- nearest_neighbor()

  expect_error(
    fit(spec, Species ~ ., data = iris),
    "mode"
  )
})

test_that("mode must match outcome type", {
  spec <- logistic_reg() |> set_engine("glm")

  expect_error(
    fit(spec, mpg ~ ., data = mtcars),  # mpg is numeric
    "outcome should be a factor"
  )
})
```

---

## Mode Documentation

### In Model Constructor

Document mode behavior clearly:

```r
#' @param mode A single character string for the type of model. Possible values
#'   for this model are "regression" and "classification".
boost_tree <- function(
  mode = "unknown",
  trees = NULL,
  ...
) {
  # ...
}
```

### In Package Documentation

Explain which modes are supported:

```
## Modes

This model can be used for:

- Regression: predicting numeric outcomes

- Classification: predicting categorical outcomes

Set the mode with:
```r
boost_tree(mode = "regression")
boost_tree(mode = "classification")
```

### Mode-Specific Examples

Show examples for each mode:

```r
# Regression example
spec <- boost_tree(mode = "regression") |> set_engine("xgboost")
fit(spec, mpg ~ ., data = mtcars)

# Classification example
spec <- boost_tree(mode = "classification") |> set_engine("xgboost")
fit(spec, Species ~ ., data = iris)
```

---

## Common Patterns

### Pattern 1: Single-Mode Model (Regression)

```r
# Constructor sets mode automatically
linear_reg <- function(
  penalty = NULL,
  mixture = NULL,
  engine = "lm"
) {
  # Mode is always "regression"
  new_model_spec(
    "linear_reg",
    args = list(...),
    mode = "regression",
    ...
  )
}

# Only register for one mode
set_model_mode(model = "linear_reg", mode = "regression")
set_fit(model = "linear_reg", mode = "regression", ...)
set_pred(model = "linear_reg", mode = "regression", type = "numeric", ...)
```

### Pattern 2: Single-Mode Model (Classification)

```r
# Constructor sets mode automatically
logistic_reg <- function(
  penalty = NULL,
  mixture = NULL,
  engine = "glm"
) {
  new_model_spec(
    "logistic_reg",
    args = list(...),
    mode = "classification",
    ...
  )
}

# Only register for classification
set_model_mode(model = "logistic_reg", mode = "classification")
set_fit(model = "logistic_reg", mode = "classification", ...)
set_pred(model = "logistic_reg", mode = "classification", type = "class", ...)
set_pred(model = "logistic_reg", mode = "classification", type = "prob", ...)
```

### Pattern 3: Multi-Mode Model

```r
# Constructor allows mode selection
boost_tree <- function(
  mode = "unknown",
  trees = NULL,
  ...
) {
  new_model_spec(
    "boost_tree",
    args = list(...),
    mode = mode,
    ...
  )
}

# Register both modes
set_model_mode(model = "boost_tree", mode = "regression")
set_model_mode(model = "boost_tree", mode = "classification")

# Register fit for both
set_fit(model = "boost_tree", mode = "regression", ...)
set_fit(model = "boost_tree", mode = "classification", ...)

# Register predictions for both
set_pred(model = "boost_tree", mode = "regression", type = "numeric", ...)
set_pred(model = "boost_tree", mode = "classification", type = "class", ...)
set_pred(model = "boost_tree", mode = "classification", type = "prob", ...)
```

### Pattern 4: Mode-Dependent Arguments

```r
# Different defaults based on mode
set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "regression",
  value = list(
    defaults = list(objective = "reg:squarederror")
  )
)

set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "classification",
  value = list(
    defaults = list(objective = "multi:softprob")
  )
)
```

---

## Mode Troubleshooting

### Issue: "Please set the mode"

**Problem:** Mode is unknown when trying to fit.

**Solution:**
```r
spec <- nearest_neighbor() |> set_mode("classification")
```

### Issue: "Can only be used for X"

**Problem:** Trying to use single-mode model with wrong mode.

**Solution:** Check model documentation for supported modes:
```r
# linear_reg only supports regression
spec <- linear_reg()  # Automatically sets mode = "regression"
```

### Issue: Wrong Prediction Type for Mode

**Problem:** Requesting `prob` for regression model.

**Solution:** Check which prediction types are available for the mode:
```r
# Regression supports: numeric, conf_int, pred_int, raw
# Classification supports: class, prob, raw
```

### Issue: Engine Doesn't Support Mode

**Problem:** Combination not registered.

**Solution:** Check available engines:
```r
parsnip::show_engines("boost_tree")
```

---

## Summary

**Key points:**

1. **Mode determines prediction types** - Each mode has specific available types
2. **Single-mode models set automatically** - Linear/logistic regression fix their mode
3. **Multi-mode models need explicit setting** - Use `set_mode()` before fitting
4. **Register separately for each mode** - Use `set_fit()` and `set_pred()` for each
5. **Not all engines support all modes** - Check with `show_engines()`
6. **Validation happens at fit time** - Mode must match outcome type

**Quick reference:**

| Mode | Outcome Type | Prediction Types |
|------|-------------|------------------|
| regression | numeric | numeric, conf_int, pred_int, raw |
| classification | factor | class, prob, raw |
| censored regression | Surv | time, survival, hazard, linear_pred, raw |
| quantile regression | numeric | quantile, raw |
