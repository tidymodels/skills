# Parsnip Model Specification System

This document explains the architecture and design of parsnip's model specification system. This applies to both creating new models and adding engines to existing models.

---

## Overview

**parsnip** provides a unified interface to diverse modeling functions across R packages. It separates:

1. **Model specification** - What type of model (linear_reg, boost_tree, etc.)
2. **Engine** - How to compute it (lm, glmnet, xgboost, etc.)
3. **Mode** - What type of prediction (regression, classification, etc.)

This separation allows the same model specification to work with multiple computational engines while maintaining a consistent interface.

---

## Model Specification Objects

### Structure

A model specification is an S3 object created by functions like `linear_reg()`, `boost_tree()`, etc. It contains:

```r
linear_reg()
#> Linear Regression Model Specification (regression)
#>
#> Computational engine: lm
```

**Key properties stored in the object:**

- `args` - Main arguments (penalty, mixture, trees, etc.)

- `eng_args` - Engine-specific arguments (passed via `set_engine()`)

- `mode` - The prediction mode ("regression", "classification", etc.)

- `engine` - The computational backend (e.g., "lm", "glmnet", "xgboost")

- `method` - Internal: fitting method

- `user_specified_mode` - Whether user explicitly set mode

- `user_specified_engine` - Whether user explicitly set engine

### Class Hierarchy

Model specifications have a class hierarchy:

```r
class(linear_reg())
#> [1] "linear_reg"  "model_spec"
```

This allows:

- Method dispatch (e.g., `fit.linear_reg()`)

- Type checking (is it a `model_spec`?)

- Model-specific behaviors

The class is created using `make_classes()` which prepends the model type to `"model_spec"`.

### Difference from Fitted Models

**Model specification (`model_spec`):**

- Blueprint for fitting

- No data involved

- Lightweight (just configuration)

- Created by `linear_reg()`, `boost_tree()`, etc.

**Fitted model (`model_fit`):**

- Result of `fit()`

- Contains trained parameters

- Has actual model object (e.g., `lm` object)

- Used for prediction

---

## Engine Registration System

### How Engines Work

Engines connect model specifications to actual computational implementations:

```
linear_reg(penalty = 0.1) + set_engine("glmnet")
         ↓
    glmnet::glmnet(lambda = 0.1, ...)
```

Each model-engine-mode combination must be registered with:

1. `set_model_engine()` - Register that this engine exists
2. `set_dependency()` - Specify required packages
3. `set_model_arg()` - Translate main arguments to engine arguments
4. `set_fit()` - Specify how to fit the model
5. `set_pred()` - Specify how to make predictions (for each type)

### The Registration Database

Registered models are stored in an environment accessible via `get_model_env()`:

```r
env <- get_model_env()
ls(env)  # Lists all registered models
```

For each model, there's a table of engine/mode combinations with their fit and prediction specifications.

### Looking Up Available Engines

```r
show_engines("linear_reg")
#> Shows all registered engines and modes
```

This queries the registration database to show what's available.

---

## Model Modes

### Available Modes

From `R/aaa_models.R`, parsnip supports:

- `"regression"` - Numeric outcomes

- `"classification"` - Categorical outcomes

- `"censored regression"` - Survival/time-to-event outcomes

- `"quantile regression"` - Quantile predictions

- `"unknown"` - Placeholder before user sets mode

### Setting Modes

**In constructor (default mode):**
```r
linear_reg(mode = "regression")  # Default
```

**Change with `set_mode()`:**
```r
nearest_neighbor(mode = "unknown") |>
  set_mode("classification")
```

### Mode-Specific Behaviors

Different modes have different:

**Prediction types:**

- Regression: `numeric`, `conf_int`, `pred_int`, `raw`

- Classification: `class`, `prob`, `raw`

- Censored regression: `time`, `survival`, `hazard`, `linear_pred`, `raw`

- Quantile regression: `quantile`, `raw`

**Engine requirements:**

- Some engines only support certain modes

- Must register separately for each mode

**Validation:**

- parsnip checks mode compatibility before fitting

- Error if engine doesn't support the mode

---

## Main Arguments vs Engine Arguments

### Philosophy

parsnip distinguishes between:

**Main arguments** - Standardized across engines

- Common tuning parameters

- Defined in model constructor

- Named consistently (e.g., `penalty`, `trees`, `mtry`)

- May not apply to all engines (ignored if not applicable)

**Engine arguments** - Engine-specific

- Passed via `set_engine()`

- Not standardized

- Go directly to underlying function

- Use engine's native names

### When to Add Main Arguments

Main arguments should be:

- Common across multiple engines

- Important tuning parameters

- Worth standardizing for tune integration

**Example: `penalty` in linear_reg()**

- glmnet: `lambda`

- keras: `penalty`

- spark: `reg_param`

All get standardized as `penalty` in parsnip.

### Using Engine Arguments for Flexibility

Engine arguments allow access to engine-specific features:

```r
boost_tree() |>
  set_engine("xgboost",
             tree_method = "hist",  # xgboost-specific
             gpu_id = 0)            # xgboost-specific
```

These bypass translation and go straight to the engine.

---

## Integration with Tidymodels Ecosystem

### Fitting Workflows

**Direct fit:**
```r
spec <- linear_reg() |> set_engine("lm")
fit <- fit(spec, mpg ~ ., data = mtcars)
```

**With workflows:**
```r
library(workflows)

wf <- workflow() |>
  add_model(spec) |>
  add_formula(mpg ~ .)

fit <- fit(wf, data = mtcars)
```

### Prediction

**Multiple types:**
```r
predict(fit, new_data = mtcars, type = "numeric")
predict(fit, new_data = mtcars, type = "conf_int")
```

The type depends on mode and engine capabilities.

### Tuning

**With tune package:**
```r
spec <- boost_tree(trees = tune(), tree_depth = tune()) |>
  set_engine("xgboost")

# Tune with tune::tune_grid()
```

Main arguments can be marked for tuning using `tune()`.

### Recipes and Workflows

Parsnip integrates seamlessly:

```r
library(recipes)

recipe <- recipe(mpg ~ ., data = mtcars) |>
  step_normalize(all_numeric_predictors())

workflow() |>
  add_recipe(recipe) |>
  add_model(spec) |>
  fit(data = mtcars)
```

---

## The Fit → Model_fit → Predict Pipeline

### 1. Specification

User creates a model specification:

```r
spec <- boost_tree(trees = 100) |> set_engine("xgboost")
```

### 2. Translation

When `fit()` is called, arguments are translated:

- Main arguments mapped to engine arguments via `set_model_arg()`

- Engine arguments passed through unchanged

- Formula converted to engine's expected interface

### 3. Fitting

The engine's fit function is called:

```r
# Behind the scenes:
xgboost::xgb.train(
  nrounds = 100,  # translated from trees
  ...
)
```

### 4. Wrapping

Result is wrapped in a `model_fit` object:

```r
class(fit)
#> [1] "model_fit"
```

This contains:

- The original spec

- The fitted model object

- Preprocessing information

### 5. Prediction

When `predict()` is called:

- Extract the fitted model object

- Call engine-specific prediction function

- Post-process to standard format (tibble with `.pred` columns)

- Return consistently named output

This pipeline ensures consistent interface while allowing engine flexibility.

---

## Design Considerations

### When Creating New Models

**Consider:**
1. Is this model type distinct from existing ones?
2. What main arguments are common across implementations?
3. What modes should it support?
4. What prediction types make sense?

**Example:** `survival_reg()` is distinct from `linear_reg()` because:

- Different outcome type (censored data)

- Different prediction types (time, survival, hazard)

- Different evaluation metrics

### When Adding Engines

**Consider:**
1. Does the model type already exist?
2. What's the natural interface (formula, matrix, xy)?
3. Which prediction types can this engine support?
4. What main arguments does it support?
5. What engine-specific arguments are valuable?

### Model Naming

Follow parsnip conventions:

- Descriptive of algorithm: `linear_reg()`, `rand_forest()`, `boost_tree()`

- Not package-specific: Not `glmnet_model()` or `xgboost_model()`

- Function form: `nearest_neighbor()`, not `nearest_neighbors` or `knn`

---

## Internal Architecture

### Key Internal Functions

**Constructor:**

- `new_model_spec()` - Core constructor helper

- `make_classes()` - Creates class hierarchy

**Validation:**

- `spec_is_possible()` - Checks if model/engine/mode combination could exist

- `spec_is_loaded()` - Checks if it's actually registered

- `check_empty_ellipse()` - Validates no extra arguments

**Environment Management:**

- `get_model_env()` - Access model registry

- `get_from_env()` - Retrieve registration data

- `set_in_env()` - Store registration data

**Error Handling:**

- `stop_incompatible_mode()` - Mode not supported

- `stop_incompatible_engine()` - Engine not available

- `stop_missing_engine()` - No engine specified

### File Organization in parsnip Source

**Model constructors:** `R/[model_type].R`

- Example: `R/linear_reg.R`, `R/boost_tree.R`

- Contains the user-facing function

**Engine registrations:** `R/[model]_data.R`

- Example: `R/linear_reg_data.R`, `R/boost_tree_data.R`

- Contains all `set_*()` calls for that model

**Infrastructure:** `R/aaa_models.R`, `R/misc.R`

- Model environment setup

- Core helper functions

---

## Summary

Parsnip's architecture separates:

- **What** (model type) from **how** (engine) from **why** (mode)

- **Interface** (user-facing) from **implementation** (engine-specific)

- **Specification** (pre-fit) from **fitted model** (post-fit)

This design enables:

- Consistent interface across diverse engines

- Easy engine switching

- Integration with tidymodels ecosystem (tune, workflows, recipes)

- Extension by third-party packages

Understanding this architecture is essential for both creating new models and adding engines to existing ones.
