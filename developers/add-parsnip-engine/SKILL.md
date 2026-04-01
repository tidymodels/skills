# Add Parsnip Engine

Add new computational engines to existing parsnip models. This skill covers registering new engines (like adding "spark" to `linear_reg()`) without creating entirely new model types.

**Use this skill when:** Adding a new engine to an existing parsnip model type.

**For creating new models:** See [add-parsnip-model](../add-parsnip-model/SKILL.md) skill instead.

---

## Prerequisites

Before adding a new engine, ensure you have:

**R Package Development:**

- [Extension Prerequisites](references/package-extension-prerequisites.md) - Required for extension packages

- [Development Workflow](references/package-development-workflow.md) - Fast iteration practices

**Parsnip Fundamentals:**

- [Fit and Predict Methods](references/fit-predict-methods.md) - Implementation basics

- [Prediction Types](references/prediction-types.md) - Available output formats

---

## Adding a New Engine

### 1. Identify the Model

**Determine which model** to extend:

```r
# Check existing models
parsnip::show_models()

# Check current engines for a model
parsnip::show_engines("linear_reg")
```

**Verify your engine is new:**

- Not already registered for this model

- Provides distinct computational approach or benefits

- Worth the maintenance burden

### 2. Plan Engine Implementation

**Start here:** [Engine Implementation Guide](references/engine-implementation.md)

Decide on:

- Which modes to support (regression, classification, both?)

- Which prediction types the engine can provide

- Data interface (formula, matrix, xy)

- Which main arguments the engine supports

- Engine-specific configuration needed

### 3. Implement Fit Method

**Core implementation:** [Fit and Predict Methods](references/fit-predict-methods.md)

Register how to fit the model:

- Choose interface type (formula, matrix, xy)

- Map main arguments to engine arguments

- Set engine defaults

- Handle data conversion

### 4. Implement Prediction Types

**Standardize output:** [Prediction Types](references/prediction-types.md)

For each prediction type:

- Check what the engine can provide

- Implement pre-processing if needed

- Format output with standard column names

- Handle engine-specific quirks

### 5. Configure Mode Handling

**If multi-mode:** [Mode Handling](references/mode-handling.md)

For engines supporting multiple modes:

- Register each mode separately

- Set mode-specific defaults

- Implement appropriate prediction types per mode

### 6. Set Encoding Options

**For matrix/xy interfaces:** [Encoding Options](references/encoding-options.md)

Configure data conversion:

- Choose interface type

- Set factor encoding

- Handle intercept

- Configure sparse matrix support

---

## Registration Steps

### Complete Registration Sequence

For each engine-mode combination:

1. **Register engine:** `set_model_engine()`

2. **Declare dependencies:** `set_dependency()`

3. **Translate arguments:** `set_model_arg()` (if using main arguments)

4. **Register fit method:** `set_fit()`

5. **Configure encoding:** `set_encoding()` (if needed)

6. **Register predictions:** `set_pred()` for each type

**See:** [Engine Implementation Guide](references/engine-implementation.md) for detailed sequence.

---

## Testing Your Engine

**Essential tests:**

- Engine fits successfully

- Formula and xy interfaces work (if applicable)

- Each prediction type returns correct format

- Predictions match data dimensions

- Factor handling works correctly

- Error messages are clear

**Test each mode separately:**

```r
test_that("xgboost engine works for regression", {
  skip_if_not_installed("xgboost")

  spec <- boost_tree() |>
    set_engine("xgboost") |>
    set_mode("regression")

  fit <- fit(spec, mpg ~ ., data = mtcars)
  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, mtcars[1:5, ])
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
})
```

---

## Contributing to Parsnip Source

**For PRs to tidymodels/parsnip:**

Additional resources for source development:

- [Best Practices (Source)](references/best-practices-source.md) - Parsnip-specific patterns

- [Troubleshooting (Source)](references/troubleshooting-source.md) - Common issues

- [Testing Patterns (Source)](references/testing-patterns-source.md) - Comprehensive tests

**Key differences from extensions:**

- Can use internal functions (`:::`)

- Add to existing `R/[model]_data.R` file

- Add to parsnip documentation

- More comprehensive testing required

- Consider existing engine patterns

---

## Example: Adding H2O to linear_reg

**Hypothetical new engine for linear regression:**

### Registration

```r
# In .onLoad() for extensions, or R/linear_reg_data.R for source

# 1. Register engine
parsnip::set_model_engine(
  model = "linear_reg",
  mode = "regression",
  eng = "h2o"
)

# 2. Declare dependencies
parsnip::set_dependency(
  model = "linear_reg",
  eng = "h2o",
  pkg = "h2o",
  mode = "regression"
)

# 3. Translate main arguments (if engine uses them)
parsnip::set_model_arg(
  model = "linear_reg",
  eng = "h2o",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = FALSE
)

# 4. Register fit method
parsnip::set_fit(
  model = "linear_reg",
  eng = "h2o",
  mode = "regression",
  value = list(
    interface = "data.frame",  # h2o uses data frames
    protect = c("x", "y", "training_frame"),
    func = c(pkg = "h2o", fun = "h2o.glm"),
    defaults = list(family = "gaussian")
  )
)

# 5. Register predictions
parsnip::set_pred(
  model = "linear_reg",
  eng = "h2o",
  mode = "regression",
  type = "numeric",
  value = list(
    pre = NULL,
    post = function(results, object) {
      tibble::tibble(.pred = as.vector(results))
    },
    func = c(pkg = "h2o", fun = "h2o.predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data)
    )
  )
)

parsnip::set_pred(
  model = "linear_reg",
  eng = "h2o",
  mode = "regression",
  type = "raw",
  value = list(
    pre = NULL,
    post = NULL,
    func = c(pkg = "h2o", fun = "h2o.predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data)
    )
  )
)
```

### Usage

```r
# User workflow
library(parsnip)
library(h2o)

# Initialize h2o
h2o.init()

# Use new engine
spec <- linear_reg(penalty = 0.1) |>
  set_engine("h2o")

fit <- fit(spec, mpg ~ ., data = mtcars)
predict(fit, mtcars[1:5, ])
```

---

## Common Patterns

### Pattern 1: Adding Matrix Interface Engine

Engine requires numeric matrices:

```r
parsnip::set_fit(
  model = "linear_reg",
  eng = "new_engine",
  mode = "regression",
  value = list(
    interface = "matrix",
    protect = c("x", "y"),
    func = c(pkg = "newpkg", fun = "fit_func"),
    defaults = list()
  )
)

parsnip::set_encoding(
  model = "linear_reg",
  eng = "new_engine",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)
```

### Pattern 2: Adding Formula Interface Engine

Engine uses traditional R formula:

```r
parsnip::set_fit(
  model = "linear_reg",
  eng = "new_engine",
  mode = "regression",
  value = list(
    interface = "formula",
    protect = c("formula", "data"),
    func = c(pkg = "newpkg", fun = "fit_func"),
    defaults = list()
  )
)

# No encoding needed - formula passes through
```

### Pattern 3: Engine with Complex Output

Engine returns non-standard format:

```r
parsnip::set_pred(
  model = "linear_reg",
  eng = "new_engine",
  mode = "regression",
  type = "numeric",
  value = list(
    pre = NULL,
    post = function(results, object) {
      # Extract predictions from complex structure
      pred_values <- results$predictions$point_estimate
      tibble::tibble(.pred = as.numeric(pred_values))
    },
    func = c(pkg = "newpkg", fun = "predict_func"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data)
    )
  )
)
```

### Pattern 4: Multi-Mode Engine

Same engine for regression and classification:

```r
# Regression mode
parsnip::set_model_engine("my_model", "regression", "new_engine")
parsnip::set_fit(
  model = "my_model",
  eng = "new_engine",
  mode = "regression",
  value = list(
    defaults = list(objective = "regression")
  )
)

# Classification mode
parsnip::set_model_engine("my_model", "classification", "new_engine")
parsnip::set_fit(
  model = "my_model",
  eng = "new_engine",
  mode = "classification",
  value = list(
    defaults = list(objective = "classification")
  )
)
```

---

## Common Pitfalls

1. **Wrong interface type** - Match engine's expected input format

2. **Missing `set_dependency()`** - Always declare package dependencies

3. **Incorrect column names** - Must follow `.pred*` conventions

4. **No argument translation** - If engine uses main arguments, must map them

5. **Incomplete prediction types** - Register all types engine can provide

6. **Engine-specific defaults not set** - Use `defaults` in `set_fit()`

---

## When to Add an Engine

**Add an engine when:**

- It provides different computational approach

- It offers performance benefits

- It has unique features users need

- It's well-maintained and stable

**Don't add an engine when:**

- Functionally identical to existing engine

- Package is unmaintained or unstable

- Only cosmetic differences

- Would require significant maintenance

**Examples:**

- ✓ Add spark to linear_reg() - Distributed computing

- ✓ Add keras to linear_reg() - Neural network approach

- ✗ Add lm.fit to linear_reg() - Same as lm, no user benefit

- ✗ Add experimental package - May break or disappear

---

## Checking Compatibility

### Check What Model Already Has

```r
# See existing engines
parsnip::show_engines("linear_reg")

# See what main arguments exist
spec <- linear_reg(penalty = 0.1)
spec$args
```

### Verify Engine Capabilities

**Can it provide:**

- Required prediction types for the mode?

- Support for main arguments?

- Reasonable performance?

- Clear error messages?

**Document what it can't do:**

- Some engines don't support all prediction types

- Some don't use certain main arguments

- Some have limitations (e.g., no missing data)

---

## Related Skills

- [add-parsnip-model](../add-parsnip-model/SKILL.md) - Create new model specifications (if model doesn't exist yet)
- [add-dials-parameter](../add-dials-parameter/SKILL.md) - Define tunable parameters for engine arguments
- [add-recipe-step](../add-recipe-step/SKILL.md) - Preprocess data before model fitting
- [add-yardstick-metric](../add-yardstick-metric/SKILL.md) - Evaluate engine predictions with custom metrics

## Next Steps

After adding your engine:

1. **Test thoroughly** - All interfaces, prediction types, edge cases

2. **Document** - Add examples showing engine usage

3. **Share** - Consider contributing to parsnip

4. **Monitor** - Watch for engine package updates

5. **Maintain** - Keep up with parsnip changes

For questions or contributions, see:

- [Tidymodels GitHub](https://github.com/tidymodels/parsnip)

- [Tidymodels Community](https://community.rstudio.com/c/ml)

---

## Skill vs Source Context

**This skill primarily covers:**

- Adding engines to existing models

- Extension package development

- Registration patterns

**For creating entirely new models:**

- See [add-parsnip-model](../add-parsnip-model/SKILL.md) skill

- Includes constructor design, mode setup, argument design

**For source contributions:**

- Same registration process applies

- Additional patterns in Best Practices (Source)

- More comprehensive testing expected
