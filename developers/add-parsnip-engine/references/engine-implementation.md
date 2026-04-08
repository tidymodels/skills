# Engine Implementation Guide

Complete guide to implementing engines for existing parsnip models. This is the
focused, actionable guide for the most common parsnip development task.

--------------------------------------------------------------------------------

## Overview

An **engine** connects a parsnip model specification to a computational
implementation. Adding an engine means making an existing model work with a new
R package, Python library, or custom algorithm.

**This guide covers:**

- Complete registration sequence

- Fit and predict implementation

- Handling different interfaces

- Supporting prediction types

- Testing engines

--------------------------------------------------------------------------------

## Implementation Philosophy

**Be Direct and Concise:**

When implementing engines, write minimal, focused code:

- ✅ **DO:** Get straight to registration - run verification, add engine, test

- ✅ **DO:** Link to references for complex topics instead of inline
  explanations

- ✅ **DO:** Create 2-3 files total (R/, tests/, optional README)

- ❌ **DON'T:** Create summary documents (IMPLEMENTATION_SUMMARY.md,
  QUICK_REFERENCE.md)

- ❌ **DON'T:** Create example files (example_usage.R) - examples go in README
  or tests

- ❌ **DON'T:** Over-explain in comments - code should be self-documenting

- ❌ **DON'T:** Create helper files for simple operations

**For complex topics (multi-mode, survival, encoding):**

- Point to specific reference docs rather than duplicating explanations

- Keep registration code clean and pattern-based

- Let parsnip infrastructure handle complexity

**When refusing internal functions:**

- Refuse in 1 sentence, suggest alternative, move forward

- Don't write long explanations about why internal functions are bad

### Token Budget Awareness

Target token usage by complexity:

- **Simple engines** (single mode, formula interface): <50,000 tokens

- **Complex engines** (multi-mode, matrix interface): <70,000 tokens

- **Very complex** (3+ modes, survival): <80,000 tokens

If approaching these limits, you're over-explaining. Link to references instead.

### Automated File Count Check

**INSTRUCTIONS FOR CLAUDE:** After implementation, verify file discipline:

```bash
# Count files created
find . -type f \( -name "*.R" -o -name "*.md" \) | wc -l
```

**Expected counts:**

- Extension development: 2-3 files (R/zzz.R, tests/test-\*.R, optional
  README.md)

- Source development: 0-1 new files (modify existing R/*\_data.R, test-*.R)

**If you created >3 files, CONSOLIDATE immediately:**

1. Delete summary docs (IMPLEMENTATION_SUMMARY.md, NOTES.md, QUICK_REFERENCE.md)

   - Content goes in code comments or README
2. Delete example files (example_usage.R, examples.R)

   - Examples go in README.md or tests
3. Delete helper files (utils.R, helpers.R)

   - Simple helpers go inline; complex ones indicate over-engineering
4. Merge duplicate content into single files

**Check before proceeding** - don't continue with 8+ files thinking "file
discipline failed." Fix it before moving forward.

--------------------------------------------------------------------------------

## Planning Your Engine

### Identify the Model

Before adding an engine, determine which model to extend:

```r
# Check existing models in parsnip
parsnip::show_models()

# Check current engines for a specific model
parsnip::show_engines("linear_reg")
```

**Verify your engine is new:**

- Not already registered for this model

- Provides distinct computational approach or benefits

- Worth the maintenance burden

### When to Add an Engine

**Add an engine when:**

- Model type already exists in parsnip (e.g., `linear_reg()`, `boost_tree()`)

- You want to connect it to a new package

- The new engine provides different benefits (speed, features, scale)

**Don't add an engine when:**

- Model type doesn't exist → See
  [add-parsnip-model](../../add-parsnip-model/SKILL.md)

- Engine already exists with same functionality

- Package is experimental or unmaintained

--------------------------------------------------------------------------------

## Complete Registration Sequence

Follow these steps in order for each engine-mode combination:

### Step 1: Register Engine

Declare that the engine exists:

```r
parsnip::set_model_engine(
  model = "linear_reg",
  mode = "regression",
  eng = "my_engine"
)
```

### Step 2: Declare Dependencies

Specify required packages:

```r
parsnip::set_dependency(
  model = "linear_reg",
  eng = "my_engine",
  pkg = "mypackage",
  mode = "regression"
)

# Multiple packages
parsnip::set_dependency(
  model = "linear_reg",
  eng = "my_engine",
  pkg = c("mypackage", "helper"),
  mode = "regression"
)
```

### Step 3: Translate Main Arguments

Map parsnip arguments to engine arguments:

```r
parsnip::set_model_arg(
  model = "linear_reg",
  eng = "my_engine",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = FALSE
)
```

Do this for each main argument the engine supports.

### Step 4: Register Fit Method

Specify how to fit:

```r
parsnip::set_fit(
  model = "linear_reg",
  eng = "my_engine",
  mode = "regression",
  value = list(
    interface = "matrix",
    protect = c("x", "y"),
    func = c(pkg = "mypackage", fun = "fit_func"),
    defaults = list(family = "gaussian")
  )
)
```

### Step 5: Configure Encoding (if needed)

For matrix/xy interfaces:

```r
parsnip::set_encoding(
  model = "linear_reg",
  eng = "my_engine",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)
```

### Step 6: Register Predictions

For each prediction type:

```r
parsnip::set_pred(
  model = "linear_reg",
  eng = "my_engine",
  mode = "regression",
  type = "numeric",
  value = list(
    pre = NULL,
    post = NULL,
    func = c(fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data)
    )
  )
)
```

--------------------------------------------------------------------------------

## Choosing Interface Type

### Formula Interface

Use when engine expects `func(formula, data, ...)`:

```r
parsnip::set_fit(
  model = "linear_reg",
  eng = "my_engine",
  mode = "regression",
  value = list(
    interface = "formula",
    protect = c("formula", "data"),
    func = c(pkg = "stats", fun = "lm"),
    defaults = list()
  )
)
```

**No encoding needed** - formula passes through unchanged.

### Matrix Interface

Use when engine expects `func(x, y, ...)`:

```r
parsnip::set_fit(
  model = "linear_reg",
  eng = "my_engine",
  mode = "regression",
  value = list(
    interface = "matrix",
    protect = c("x", "y"),
    func = c(pkg = "glmnet", fun = "glmnet"),
    defaults = list(family = "gaussian")
  )
)

# Configure how formula converts to matrix
parsnip::set_encoding(
  model = "linear_reg",
  eng = "my_engine",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)
```

**Encoding needed** - parsnip converts formula to matrices.

### XY Interface

Use when engine has custom argument names:

```r
parsnip::set_fit(
  model = "my_model",
  eng = "my_engine",
  mode = "regression",
  value = list(
    interface = "xy",
    protect = c("train", "cl"),  # Custom names
    func = c(pkg = "kknn", fun = "train.kknn"),
    defaults = list()
  )
)
```

--------------------------------------------------------------------------------

## Implementing Predictions

### Simple Numeric Prediction

No transformation needed:

```r
parsnip::set_pred(
  model = "linear_reg",
  eng = "my_engine",
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

### With Post-Processing

Engine returns non-standard format:

```r
parsnip::set_pred(
  model = "linear_reg",
  eng = "my_engine",
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
      interval = "confidence"
    )
  )
)
```

### Classification Probabilities

Multiple columns to format:

```r
parsnip::set_pred(
  model = "logistic_reg",
  eng = "my_engine",
  mode = "classification",
  type = "prob",
  value = list(
    pre = NULL,
    post = function(results, object) {
      results <- as.data.frame(results)
      names(results) <- paste0(".pred_", names(results))
      tibble::as_tibble(results)
    },
    func = c(fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data),
      type = "prob"
    )
  )
)
```

--------------------------------------------------------------------------------

## Multi-Mode Engines

Some engines support multiple modes. Register each separately:

```r
# Regression mode
parsnip::set_model_engine("boost_tree", "regression", "xgboost")
parsnip::set_dependency("boost_tree", "xgboost", "xgboost", "regression")

parsnip::set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "regression",
  value = list(
    interface = "matrix",
    func = c(pkg = "xgboost", fun = "xgb.train"),
    defaults = list(objective = "reg:squarederror")  # Regression objective
  )
)

parsnip::set_pred(
  model = "boost_tree",
  eng = "xgboost",
  mode = "regression",
  type = "numeric",
  value = list(...)
)

# Classification mode
parsnip::set_model_engine("boost_tree", "classification", "xgboost")
parsnip::set_dependency("boost_tree", "xgboost", "xgboost", "classification")

parsnip::set_fit(
  model = "boost_tree",
  eng = "xgboost",
  mode = "classification",
  value = list(
    interface = "matrix",
    func = c(pkg = "xgboost", fun = "xgb.train"),
    defaults = list(objective = "multi:softprob")  # Classification objective
  )
)

parsnip::set_pred(
  model = "boost_tree",
  eng = "xgboost",
  mode = "classification",
  type = "class",
  value = list(...)
)

parsnip::set_pred(
  model = "boost_tree",
  eng = "xgboost",
  mode = "classification",
  type = "prob",
  value = list(...)
)
```

--------------------------------------------------------------------------------

## Complete Example: Adding glmnet to linear_reg

Full registration for a new engine:

```r
# In .onLoad() for extensions, or R/linear_reg_data.R for source

# Step 1: Register engine
parsnip::set_model_engine(
  model = "linear_reg",
  mode = "regression",
  eng = "glmnet"
)

# Step 2: Dependencies
parsnip::set_dependency(
  model = "linear_reg",
  eng = "glmnet",
  pkg = "glmnet",
  mode = "regression"
)

# Step 3: Translate arguments
parsnip::set_model_arg(
  model = "linear_reg",
  eng = "glmnet",
  parsnip = "penalty",
  original = "lambda",
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

# Step 4: Fit method
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

# Step 5: Encoding
parsnip::set_encoding(
  model = "linear_reg",
  eng = "glmnet",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)

# Step 6: Predictions
parsnip::set_pred(
  model = "linear_reg",
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
  model = "linear_reg",
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

--------------------------------------------------------------------------------

## Complete Example: Adding H2O to linear_reg

Full registration for a data.frame interface engine:

```r
# In .onLoad() for extensions, or R/linear_reg_data.R for source

# Step 1: Register engine
parsnip::set_model_engine(
  model = "linear_reg",
  mode = "regression",
  eng = "h2o"
)

# Step 2: Declare dependencies
parsnip::set_dependency(
  model = "linear_reg",
  eng = "h2o",
  pkg = "h2o",
  mode = "regression"
)

# Step 3: Translate main arguments (if engine uses them)
parsnip::set_model_arg(
  model = "linear_reg",
  eng = "h2o",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = FALSE
)

# Step 4: Register fit method
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

# Step 5: Register predictions
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

**Usage example:**

```r
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

--------------------------------------------------------------------------------

## Testing Your Engine

Essential tests for engine implementation:

```r
test_that("my_engine fits", {
  skip_if_not_installed("mypackage")

  spec <- linear_reg() |>
    parsnip::set_engine("my_engine")

  fit <- parsnip::fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")
  expect_s3_class(fit$fit, "expected_class")
})

test_that("my_engine makes predictions", {
  skip_if_not_installed("mypackage")

  spec <- linear_reg() |>
    parsnip::set_engine("my_engine")

  fit <- parsnip::fit(spec, mpg ~ ., data = mtcars)
  preds <- predict(fit, mtcars[1:5, ])

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
  expect_type(preds$.pred, "double")
})

test_that("my_engine formula and xy equivalent", {
  skip_if_not_installed("mypackage")

  spec <- linear_reg() |>
    parsnip::set_engine("my_engine")

  fit_formula <- parsnip::fit(spec, mpg ~ hp + wt, data = mtcars)
  fit_xy <- parsnip::fit_xy(spec, x = mtcars[, c("hp", "wt")], y = mtcars$mpg)

  pred_formula <- predict(fit_formula, mtcars[1:5, ])
  pred_xy <- predict(fit_xy, mtcars[1:5, ])

  expect_equal(pred_formula, pred_xy, tolerance = 1e-5)
})
```

--------------------------------------------------------------------------------

## Common Patterns

### Pattern 1: Base R Function

Simple formula interface:

```r
parsnip::set_fit(
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

### Pattern 2: Matrix-Based ML Library

Requires numeric matrices:

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

parsnip::set_encoding(
  model = "linear_reg",
  eng = "glmnet",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)
```

### Pattern 3: Custom Post-Processing

Engine returns non-standard output:

```r
parsnip::set_pred(
  model = "my_model",
  eng = "my_engine",
  mode = "regression",
  type = "numeric",
  value = list(
    pre = NULL,
    post = function(results, object) {
      # Extract predictions from nested structure
      preds <- results$predictions$values
      tibble::tibble(.pred = as.numeric(preds))
    },
    func = c(pkg = "mypackage", fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data)
    )
  )
)
```

### Pattern 4: Pre-Processing Data

Data needs preparation before prediction:

```r
parsnip::set_pred(
  model = "my_model",
  eng = "my_engine",
  mode = "regression",
  type = "numeric",
  value = list(
    pre = function(new_data, object) {
      # Convert factors to integers for this engine
      new_data$category <- as.integer(new_data$category)
      new_data
    },
    post = NULL,
    func = c(pkg = "mypackage", fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data)
    )
  )
)
```

--------------------------------------------------------------------------------

## Troubleshooting

### Issue: "engine not found"

**Problem:** Engine not registered.

**Solution:**

```r
parsnip::set_model_engine("linear_reg", "regression", "my_engine")
```

### Issue: "could not find function"

**Problem:** Package not declared as dependency.

**Solution:**

```r
parsnip::set_dependency("linear_reg", "my_engine", "mypackage", "regression")
```

### Issue: Wrong prediction format

**Problem:** Engine returns matrix but need tibble.

**Solution:**

```r
post = function(results, object) {
  tibble::tibble(.pred = as.numeric(results))
}
```

### Issue: Argument not translated

**Problem:** Main argument not mapped to engine argument.

**Solution:**

```r
parsnip::set_model_arg(
  model = "linear_reg",
  eng = "my_engine",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = FALSE
)
```

--------------------------------------------------------------------------------

## Next Steps

After implementing your engine:

1. **Test thoroughly** - All prediction types, edge cases
2. **Document** - Show usage examples
3. **Benchmark** - Compare with existing engines
4. **Share** - Consider contributing to parsnip

--------------------------------------------------------------------------------

## Additional Resources

**Implementation details:**

- [Fit and Predict Methods](fit-predict-methods.md) - Core implementation

- [Prediction Types](prediction-types.md) - All 11 types

- [Encoding Options](encoding-options.md) - Interface types

- [Mode Handling](mode-handling.md) - Multi-mode support

**Development:**

- [Extension Guide](extension-guide.md) - Adding engines in your package

- [Source Guide](source-guide.md) - Contributing to parsnip

- [Best Practices (Source)](best-practices-source.md) - Parsnip conventions
