# Registration Sequence

This guide covers the complete sequence of registration functions needed to add a new model to parsnip's registry system.

---

## Overview

After creating a model constructor, you must register all components with parsnip. Registration happens in a specific order and must be complete before the model can be used.

**Registration location:**

- Extension packages: In `.onLoad()` function

- Source development: In `R/[model]_data.R` file

---

## Complete Registration Sequence

### Step 1: Declare the Model (`set_new_model`)

First, declare that your model exists:

```r
parsnip::set_new_model("my_model")
```

**Purpose:**

- Adds model to parsnip's registry

- Creates storage for model information

- Must happen before any other registration

**When:**

- Once per model

- Before registering modes or engines

**Extension vs Source:**
```r
# Extension - use namespace
parsnip::set_new_model("my_model")

# Source - no namespace needed
set_new_model("my_model")
```

### Step 2: Register Modes (`set_model_mode`)

Declare which modes the model supports:

```r
parsnip::set_model_mode(model = "my_model", mode = "regression")
parsnip::set_model_mode(model = "my_model", mode = "classification")
```

**Purpose:**

- Specifies valid modes for this model

- Enables mode-specific registration

- Required before registering engines

**Call once per supported mode:**

- Single-mode model: One call

- Multi-mode model: Multiple calls

### Step 3: Register Engine (`set_model_engine`)

Register each computational engine:

```r
parsnip::set_model_engine(
  model = "my_model",
  mode = "regression",
  eng = "lm"
)

parsnip::set_model_engine(
  model = "my_model",
  mode = "regression",
  eng = "glmnet"
)
```

**Purpose:**

- Declares engine exists for model/mode combination

- Required before other engine-specific registration

**Call once per engine-mode combination:**

- If supporting 2 engines and 2 modes = 4 calls (if all combinations valid)

### Step 4: Declare Dependencies (`set_dependency`)

Specify required packages for each engine:

```r
parsnip::set_dependency(
  model = "my_model",
  eng = "glmnet",
  pkg = "glmnet",
  mode = "regression"
)

# Can specify multiple dependencies
parsnip::set_dependency(
  model = "my_model",
  eng = "keras",
  pkg = c("keras", "tensorflow"),  # Multiple packages
  mode = "regression"
)
```

**Purpose:**

- Ensures required packages are installed

- Provides helpful error messages

- Documents package requirements

**Call once per engine-mode combination** (even if no extra packages needed):
```r
# Base R functions still need declaration
parsnip::set_dependency(
  model = "linear_reg",
  eng = "lm",
  pkg = "stats",  # base R, always available
  mode = "regression"
)
```

### Step 5: Translate Main Arguments (`set_model_arg`)

Map main arguments to engine-specific arguments:

```r
parsnip::set_model_arg(
  model = "linear_reg",
  eng = "glmnet",
  parsnip = "penalty",         # parsnip name
  original = "lambda",         # glmnet name
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = TRUE
)

parsnip::set_model_arg(
  model = "linear_reg",
  eng = "glmnet",
  parsnip = "mixture",
  original = "alpha",
  func = list(pkg = "dials", fun = "mixture"),
  has_submodel = FALSE
)
```

**Purpose:**

- Translates standardized names to engine names

- Links to dials parameter objects (for tuning)

- Enables submodel optimization

**Call once per main argument per engine:**

- If you have 3 main arguments and 2 engines = 6 calls

- Only for arguments the engine actually uses

**Arguments explained:**

**`parsnip`** - Standardized argument name:

- As used in model constructor

- Example: `penalty`, not `lambda`

**`original`** - Engine's argument name:

- What the engine function expects

- Example: `lambda` for glmnet, `reg_param` for spark

**`func`** - Dials parameter function:

- Used for tuning ranges/defaults

- List with `pkg` and `fun`

- Example: `list(pkg = "dials", fun = "penalty")`

**`has_submodel`** - Optimization flag:

- `TRUE` if changing this argument doesn't require refitting

- `FALSE` if requires complete refit

- Example: `lambda` in glmnet supports submodels (TRUE)

### Step 6: Register Fitting Method (`set_fit`)

Specify how to fit the model:

```r
parsnip::set_fit(
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

**Purpose:**

- Specifies how to call the engine

- Defines data interface (formula, matrix, xy)

- Sets engine defaults

**Call once per engine-mode combination.**

**Value components:**

**`interface`** - How data is passed:

- `"formula"` - `func(formula, data, ...)`

- `"matrix"` - `func(x, y, ...)`

- `"xy"` - Custom x/y argument names

**`protect`** - Reserved arguments:

- Arguments users shouldn't override

- Example: `c("formula", "data")` or `c("x", "y")`

**`func`** - Function to call:

- `c(pkg = "glmnet", fun = "glmnet")` → `glmnet::glmnet()`

- Can omit `pkg` for base R: `c(fun = "lm")`

**`defaults`** - Default arguments:

- Passed to engine function

- Example: `list(family = "gaussian")`

### Step 7: Configure Encoding (`set_encoding`)

Optional: Control how formulas are converted (for matrix/xy interfaces):

```r
parsnip::set_encoding(
  model = "linear_reg",
  eng = "glmnet",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE,
    allow_sparse_x = TRUE
  )
)
```

**Purpose:**

- Controls factor encoding

- Handles intercept

- Configures matrix conversion

**When needed:**

- Matrix or XY interfaces that need special handling

- Skip for formula interfaces

- Most engines can use defaults

**Options:**

**`predictor_indicators`:**

- `"traditional"` - n-1 dummy variables (default)

- `"one_hot"` - n dummy variables

- `"none"` - Keep factors

**`compute_intercept`:**

- `TRUE` - Add intercept column to matrix

- `FALSE` - No intercept in matrix (engine adds it)

**`remove_intercept`:**

- `TRUE` - Remove intercept from formula before conversion

- `FALSE` - Keep intercept in formula

**`allow_sparse_x`:**

- `TRUE` - Allow sparse matrices (if engine supports)

- `FALSE` - Convert to dense matrix

### Step 8: Register Prediction Types (`set_pred`)

Register each prediction type the engine supports:

```r
# Numeric predictions
parsnip::set_pred(
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

# Confidence intervals
parsnip::set_pred(
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

**Purpose:**

- Defines how to make predictions

- Standardizes output format

- Handles pre/post processing

**Call once per prediction type per engine-mode combination:**

- Regression engines might register: `numeric`, `conf_int`, `pred_int`, `raw`

- Classification engines might register: `class`, `prob`, `raw`

**Value components:**

**`pre`** - Pre-processing function:

- Signature: `function(new_data, object)`

- Prepare data before prediction

- Return modified `new_data`

**`post`** - Post-processing function:

- Signature: `function(results, object)`

- Convert engine output to standard format

- Return tibble with standard column names

**`func`** - Prediction function:

- Function to call for prediction

- Often just `c(fun = "predict")`

**`args`** - Arguments to prediction function:

- Use `rlang::expr()` for delayed evaluation

- Example: `object = rlang::expr(object$fit)`

---

## Registration Example: Complete Model

Here's a complete registration for a new model with one engine:

```r
# In .onLoad() for extensions, or R/my_model_data.R for source

# Step 1: Declare model
parsnip::set_new_model("sparse_reg")

# Step 2: Register mode
parsnip::set_model_mode("sparse_reg", "regression")

# Step 3: Register engine
parsnip::set_model_engine(
  model = "sparse_reg",
  mode = "regression",
  eng = "glmnet"
)

# Step 4: Declare dependencies
parsnip::set_dependency(
  model = "sparse_reg",
  eng = "glmnet",
  pkg = "glmnet",
  mode = "regression"
)

# Step 5: Translate main arguments
parsnip::set_model_arg(
  model = "sparse_reg",
  eng = "glmnet",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = TRUE
)

parsnip::set_model_arg(
  model = "sparse_reg",
  eng = "glmnet",
  parsnip = "mixture",
  original = "alpha",
  func = list(pkg = "dials", fun = "mixture"),
  has_submodel = FALSE
)

# Step 6: Register fit method
parsnip::set_fit(
  model = "sparse_reg",
  eng = "glmnet",
  mode = "regression",
  value = list(
    interface = "matrix",
    protect = c("x", "y", "weights"),
    func = c(pkg = "glmnet", fun = "glmnet"),
    defaults = list(family = "gaussian")
  )
)

# Step 7: Configure encoding (optional but recommended for matrix interface)
parsnip::set_encoding(
  model = "sparse_reg",
  eng = "glmnet",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)

# Step 8: Register prediction types
parsnip::set_pred(
  model = "sparse_reg",
  eng = "glmnet",
  mode = "regression",
  type = "numeric",
  value = list(
    pre = NULL,
    post = NULL,
    func = c(fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newx = rlang::expr(as.matrix(new_data)),
      type = "response"
    )
  )
)

parsnip::set_pred(
  model = "sparse_reg",
  eng = "glmnet",
  mode = "regression",
  type = "raw",
  value = list(
    pre = NULL,
    post = NULL,
    func = c(fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newx = rlang::expr(as.matrix(new_data))
    )
  )
)
```

---

## Multi-Engine Registration

When adding multiple engines, repeat steps 3-8 for each engine:

```r
# Model and mode (once)
parsnip::set_new_model("my_model")
parsnip::set_model_mode("my_model", "regression")

# First engine
parsnip::set_model_engine("my_model", "regression", "lm")
parsnip::set_dependency("my_model", "lm", "stats", "regression")
# ... continue with fit and predict for lm

# Second engine
parsnip::set_model_engine("my_model", "regression", "glmnet")
parsnip::set_dependency("my_model", "glmnet", "glmnet", "regression")
parsnip::set_model_arg(...)  # Only if glmnet uses main args
# ... continue with fit and predict for glmnet

# Third engine
parsnip::set_model_engine("my_model", "regression", "keras")
parsnip::set_dependency("my_model", "keras", c("keras", "tensorflow"), "regression")
# ... continue with fit and predict for keras
```

---

## Multi-Mode Registration

When supporting multiple modes, register each mode-engine combination:

```r
# Model (once)
parsnip::set_new_model("my_model")

# Both modes
parsnip::set_model_mode("my_model", "regression")
parsnip::set_model_mode("my_model", "classification")

# Engine for regression
parsnip::set_model_engine("my_model", "regression", "xgboost")
parsnip::set_dependency("my_model", "xgboost", "xgboost", "regression")
parsnip::set_fit(
  model = "my_model",
  eng = "xgboost",
  mode = "regression",  # Regression-specific
  value = list(
    defaults = list(objective = "reg:squarederror")
  )
)
parsnip::set_pred("my_model", "xgboost", "regression", "numeric", ...)

# Same engine for classification
parsnip::set_model_engine("my_model", "classification", "xgboost")
parsnip::set_dependency("my_model", "xgboost", "xgboost", "classification")
parsnip::set_fit(
  model = "my_model",
  eng = "xgboost",
  mode = "classification",  # Classification-specific
  value = list(
    defaults = list(objective = "multi:softprob")
  )
)
parsnip::set_pred("my_model", "xgboost", "classification", "class", ...)
parsnip::set_pred("my_model", "xgboost", "classification", "prob", ...)
```

---

## Registration Location

### Extension Packages

Register in `.onLoad()`:

```r
# R/zzz.R

.onLoad <- function(libname, pkgname) {
  # Model registration
  parsnip::set_new_model("my_model")
  parsnip::set_model_mode("my_model", "regression")

  # Engine registration
  parsnip::set_model_engine("my_model", "regression", "default")
  parsnip::set_dependency("my_model", "default", "defaultpkg", "regression")

  # Argument translation
  parsnip::set_model_arg(...)

  # Fit method
  parsnip::set_fit(...)

  # Prediction methods
  parsnip::set_pred(...)
  parsnip::set_pred(...)
}
```

**Why `.onLoad()`?**

- Runs when package is loaded

- Registers model before use

- No user action required

### Source Development (Parsnip)

Register in `R/[model]_data.R`:

```r
# R/my_model_data.R

# Model registration
set_new_model("my_model")
set_model_mode("my_model", "regression")

# lm engine
set_model_engine("my_model", "regression", "lm")
set_dependency("my_model", "lm", "stats", "regression")
set_fit(...)
set_pred(...)

# glmnet engine
set_model_engine("my_model", "regression", "glmnet")
set_dependency("my_model", "glmnet", "glmnet", "regression")
set_model_arg(...)
set_fit(...)
set_pred(...)
```

**File organization:**

- Constructor: `R/my_model.R`

- Registration: `R/my_model_data.R`

- Tests: `tests/testthat/test-my_model.R`

---

## Checking Registration

### Verify Registration Worked

```r
# Check available engines
parsnip::show_engines("my_model")

# Try creating and fitting
spec <- my_model() |> set_engine("glmnet")
fit <- fit(spec, mpg ~ ., data = mtcars)

# Try predicting
predict(fit, mtcars[1:5, ])
```

### Common Registration Issues

**Issue: "Engine not found"**

- Forgot `set_model_engine()`

- Typo in engine name

**Issue: "Package required"**

- Forgot `set_dependency()`

- Wrong package name

**Issue: "Argument not found"**

- Forgot `set_model_arg()`

- Wrong argument name mapping

**Issue: "Prediction type not available"**

- Forgot `set_pred()` for that type

- Wrong mode specified

---

## Testing Registration

Test that registration completed successfully:

```r
test_that("model is registered", {
  engines <- parsnip::show_engines("my_model")
  expect_true("glmnet" %in% engines$engine)
})

test_that("can create spec and fit", {
  spec <- my_model() |> set_engine("glmnet")
  expect_s3_class(spec, "my_model")

  fit <- fit(spec, mpg ~ ., data = mtcars)
  expect_s3_class(fit, "model_fit")
})

test_that("predictions work", {
  spec <- my_model() |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  pred <- predict(fit, mtcars[1:3, ])
  expect_s3_class(pred, "tbl_df")
  expect_named(pred, ".pred")
  expect_equal(nrow(pred), 3)
})
```

---

## Summary

**Registration sequence (in order):**

1. **`set_new_model()`** - Declare model exists
2. **`set_model_mode()`** - Declare each supported mode
3. **`set_model_engine()`** - Register each engine-mode combination
4. **`set_dependency()`** - Declare package requirements
5. **`set_model_arg()`** - Translate each main argument
6. **`set_fit()`** - Specify how to fit
7. **`set_encoding()`** - Configure data conversion (if needed)
8. **`set_pred()`** - Register each prediction type

**Key points:**

- Registration must happen in this order

- Each engine-mode combination needs its own registration

- All main arguments need translation

- Each prediction type needs separate registration

- Use `.onLoad()` for extensions, `R/*_data.R` for source

- Test registration works before moving on

**The registration system is the bridge between your constructor and the parsnip engine system.**
