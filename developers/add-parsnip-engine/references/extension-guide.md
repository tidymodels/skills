# Extension Guide: Adding Engines to Parsnip Models

Step-by-step guide for adding engines to existing parsnip models in your own R package (extension development).

---

## When to Use This Guide

Use this guide when:

- Adding an engine to an existing parsnip model in your own package

- The model type already exists (e.g., `linear_reg()`, `boost_tree()`)

- You want to connect it to a new computational backend

**Don't use this guide for:**

- Creating new model types → See [add-parsnip-model](../../add-parsnip-model/SKILL.md)

- Contributing to parsnip source → See [source-guide.md](source-guide.md)

---

## Prerequisites

**R Package Setup:**

- [Extension Prerequisites](package-extension-prerequisites.md) - Complete package setup

- Basic R package development knowledge

**Parsnip Knowledge:**

- [Engine Implementation](engine-implementation.md) - Core concepts

- Which model you're extending

---

## Key Constraints for Extension Development

### ❌ Never Use Internal Functions

**Critical:** You CANNOT use functions accessed with `:::`.

```r
# ❌ WRONG - Cannot use in extensions
result <- parsnip:::check_outcome()

# ✅ CORRECT - Use only exported functions
result <- parsnip::set_model_engine(...)
```

### ✅ Only Use Exported Functions

Safe to use in extensions:

- `parsnip::set_model_engine()`

- `parsnip::set_dependency()`

- `parsnip::set_model_arg()`

- `parsnip::set_fit()`

- `parsnip::set_encoding()`

- `parsnip::set_pred()`

- `parsnip::fit()`

- `parsnip::fit_xy()`

- `parsnip::set_engine()`

- `parsnip::set_mode()`

### ✅ Self-Contained Implementations

You must implement all logic yourself without relying on parsnip internals.

### 🚫 Quick Refusal Pattern for Internal Functions

**When user asks to use internal functions:**

1. **Refuse immediately** - "Extension packages cannot use `parsnip:::function()` - these are unstable and will cause CRAN check failures."

2. **Provide fast alternative:**

   - Factor encoding: Use `set_encoding(options = list(predictor_indicators = "traditional"))`

   - Validation: Implement yourself or use base R checks

   - Utilities: Write your own simple version

3. **Mention source development option** - "If internal functions are truly needed, contribute via PR to parsnip instead."

**Keep response to 2-3 sentences. Don't explain WHY at length - just refuse, suggest alternative, move on.**

---

## Step-by-Step Implementation

### Step 1: Plan Your Engine

Decide on:

1. **Which model to extend:**

   - Check existing models: `parsnip::show_models()`

   - Check current engines: `parsnip::show_engines("linear_reg")`

2. **Which modes to support:**

   - Regression only?

   - Classification only?

   - Both?

3. **Which interface:**

   - Formula interface (`formula, data`)

   - Matrix interface (`x, y`)

   - Data frame interface (`data.frame`)

   - XY interface (custom names)

4. **Which prediction types:**

   - Numeric (regression)

   - Class (classification)

   - Prob (class probabilities)

   - Raw (engine's native output)

   - Others (conf_int, pred_int, quantile, etc.)

5. **Which main arguments:**

   - Does engine use penalty/regularization?

   - Does it use trees/mtry?

   - Other tunable parameters?

See [Engine Implementation Guide](engine-implementation.md) for detailed planning guidance.

### Step 2: Create Registration Function

Create a function that contains all engine registration calls:

```r
# R/register_my_engine.R

register_my_engine <- function() {
  # All registration calls go here
  parsnip::set_model_engine("linear_reg", "regression", "my_engine")
  parsnip::set_dependency("linear_reg", "my_engine", "mypackage", "regression")
  # ... more registration calls
}
```

Why a function?

- Keeps registration organized

- Easy to test

- Can be called from `.onLoad()`

### Step 3: Register in .onLoad()

Hook into package loading:

```r
# R/zzz.R

.onLoad <- function(libname, pkgname) {
  register_my_engine()
}
```

This ensures your engine is available when your package loads.

### Step 4: Implement Complete Registration

Follow the 6-step registration sequence:

```r
register_my_engine <- function() {
  # 1. Register engine
  parsnip::set_model_engine(
    model = "linear_reg",
    mode = "regression",
    eng = "my_engine"
  )

  # 2. Dependencies
  parsnip::set_dependency(
    model = "linear_reg",
    eng = "my_engine",
    pkg = "mypackage",
    mode = "regression"
  )

  # 3. Translate arguments (if needed)
  parsnip::set_model_arg(
    model = "linear_reg",
    eng = "my_engine",
    parsnip = "penalty",
    original = "lambda",
    func = list(pkg = "dials", fun = "penalty"),
    has_submodel = FALSE
  )

  # 4. Fit method
  parsnip::set_fit(
    model = "linear_reg",
    eng = "my_engine",
    mode = "regression",
    value = list(
      interface = "matrix",
      protect = c("x", "y"),
      func = c(pkg = "mypackage", fun = "fit_func"),
      defaults = list()
    )
  )

  # 5. Encoding (if matrix/xy interface)
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

  # 6. Predictions
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
}
```

See [Engine Implementation Guide](engine-implementation.md) for detailed explanation of each step.

### Step 5: Test Thoroughly

Create comprehensive tests:

```r
# tests/testthat/test-my_engine.R

test_that("my_engine fits successfully", {
  skip_if_not_installed("mypackage")

  spec <- parsnip::linear_reg() |>
    parsnip::set_engine("my_engine")

  fit <- parsnip::fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")
})

test_that("my_engine makes predictions", {
  skip_if_not_installed("mypackage")

  spec <- parsnip::linear_reg() |>
    parsnip::set_engine("my_engine")

  fit <- parsnip::fit(spec, mpg ~ ., data = mtcars)
  preds <- predict(fit, mtcars[1:5, ])

  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
  expect_type(preds$.pred, "double")
})

test_that("my_engine formula and xy equivalent", {
  skip_if_not_installed("mypackage")

  spec <- parsnip::linear_reg() |>
    parsnip::set_engine("my_engine")

  fit_formula <- parsnip::fit(spec, mpg ~ hp + wt, data = mtcars)
  fit_xy <- parsnip::fit_xy(spec, x = mtcars[, c("hp", "wt")], y = mtcars$mpg)

  pred_formula <- predict(fit_formula, mtcars[1:5, ])
  pred_xy <- predict(fit_xy, mtcars[1:5, ])

  expect_equal(pred_formula, pred_xy, tolerance = 1e-5)
})
```

### Step 6: Document and Iterate

- Run `devtools::document()` to generate documentation

- Run `devtools::load_all()` to test interactively

- Run `devtools::test()` to verify tests pass

- Run `devtools::check()` for final validation

---

## Complete Examples

### Example 1: Matrix Interface Engine (Minimal)

Adding a simple matrix-based engine:

```r
# R/register_glmnet_engine.R

register_glmnet_engine <- function() {
  parsnip::set_model_engine("linear_reg", "regression", "glmnet")

  parsnip::set_dependency("linear_reg", "glmnet", "glmnet", "regression")

  parsnip::set_model_arg(
    model = "linear_reg",
    eng = "glmnet",
    parsnip = "penalty",
    original = "lambda",
    func = list(pkg = "dials", fun = "penalty"),
    has_submodel = TRUE
  )

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
}

# R/zzz.R
.onLoad <- function(libname, pkgname) {
  register_glmnet_engine()
}
```

### Example 2: Formula Interface Engine

Adding a simple formula-based engine:

```r
# R/register_lm_engine.R

register_lm_engine <- function() {
  parsnip::set_model_engine("linear_reg", "regression", "lm")

  parsnip::set_dependency("linear_reg", "lm", "stats", "regression")

  # No argument translation needed for this example

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

  # No encoding needed - formula passes through

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
        level = rlang::expr(level)
      )
    )
  )
}
```

### Example 3: Multi-Mode Engine

Adding an engine that supports both regression and classification:

```r
# R/register_xgboost_engine.R

register_xgboost_engine <- function() {
  # Regression mode
  parsnip::set_model_engine("boost_tree", "regression", "xgboost")

  parsnip::set_dependency("boost_tree", "xgboost", "xgboost", "regression")

  parsnip::set_fit(
    model = "boost_tree",
    eng = "xgboost",
    mode = "regression",
    value = list(
      interface = "matrix",
      protect = c("x", "y", "weights"),
      func = c(pkg = "xgboost", fun = "xgb.train"),
      defaults = list(
        nrounds = 15,
        objective = "reg:squarederror",  # Regression objective
        verbose = 0
      )
    )
  )

  parsnip::set_pred(
    model = "boost_tree",
    eng = "xgboost",
    mode = "regression",
    type = "numeric",
    value = list(
      pre = NULL,
      post = NULL,
      func = c(fun = "predict"),
      args = list(
        object = rlang::expr(object$fit),
        newdata = rlang::expr(as.matrix(new_data))
      )
    )
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
      protect = c("x", "y", "weights"),
      func = c(pkg = "xgboost", fun = "xgb.train"),
      defaults = list(
        nrounds = 15,
        objective = "multi:softprob",  # Classification objective
        verbose = 0
      )
    )
  )

  parsnip::set_pred(
    model = "boost_tree",
    eng = "xgboost",
    mode = "classification",
    type = "class",
    value = list(
      pre = NULL,
      post = function(results, object) {
        tibble::tibble(.pred_class = factor(results, levels = object$lvl))
      },
      func = c(fun = "predict"),
      args = list(
        object = rlang::expr(object$fit),
        newdata = rlang::expr(as.matrix(new_data)),
        reshape = TRUE
      )
    )
  )

  parsnip::set_pred(
    model = "boost_tree",
    eng = "xgboost",
    mode = "classification",
    type = "prob",
    value = list(
      pre = NULL,
      post = function(results, object) {
        results <- as.data.frame(results)
        names(results) <- paste0(".pred_", object$lvl)
        tibble::as_tibble(results)
      },
      func = c(fun = "predict"),
      args = list(
        object = rlang::expr(object$fit),
        newdata = rlang::expr(as.matrix(new_data)),
        reshape = TRUE
      )
    )
  )
}
```

---

## Common Patterns

### Pattern 1: Engine with Post-Processing

Engine returns non-standard output format:

```r
parsnip::set_pred(
  model = "linear_reg",
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

### Pattern 2: Engine with Pre-Processing

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

### Pattern 3: Multiple Dependencies

Engine requires multiple packages:

```r
# Declare all dependencies
parsnip::set_dependency("linear_reg", "my_engine", "mainpkg", "regression")
parsnip::set_dependency("linear_reg", "my_engine", "helperpkg", "regression")
parsnip::set_dependency("linear_reg", "my_engine", "matrixpkg", "regression")
```

---

## Development Workflow

See [Development Workflow](package-development-workflow.md) for complete details.

**Fast iteration cycle (run repeatedly):**

1. `devtools::document()` - Generate documentation
2. `devtools::load_all()` - Load your package
3. `devtools::test()` - Run tests

**Final validation (run once at end):**

4. `devtools::check()` - Full R CMD check

---

## Package Integration

### Directory Structure

```
myenginepackage/
├── R/
│   ├── zzz.R                    # .onLoad() hook
│   └── register_my_engine.R     # Registration function
├── tests/
│   └── testthat/
│       └── test-my_engine.R     # Engine tests
├── DESCRIPTION
├── NAMESPACE
└── README.md
```

### DESCRIPTION File

Add dependencies:

```
Package: myenginepackage
...
Imports:
    parsnip,
    rlang,
    tibble,
    mypackage
Suggests:
    testthat
```

### NAMESPACE File

Generated automatically by roxygen2 - no manual edits needed.

### README.md

Show usage example:

````markdown
# myenginepackage

Add my_engine to parsnip models.

## Installation

```r
# install.packages("devtools")
devtools::install_github("username/myenginepackage")
```

## Usage

```r
library(parsnip)
library(myenginepackage)

spec <- linear_reg() |>
  set_engine("my_engine")

fit <- fit(spec, mpg ~ ., data = mtcars)
predict(fit, mtcars[1:5, ])
```
````

---

## Testing

See [Testing Patterns (Extension)](package-extension-requirements.md#testing-requirements) for comprehensive guide.

**Required test categories:**

1. **Engine Registration** - Engine is available
2. **Fit Tests** - Model fits successfully
3. **Prediction Tests** - Each prediction type works
4. **Interface Tests** - Formula and xy interfaces equivalent
5. **Edge Cases** - Missing data, single row, factor handling

---

## Best Practices

See [Best Practices (Extension)](package-extension-requirements.md#best-practices) for complete guide.

**Key principles:**

- Use base pipe `|>` not `%>%`

- Prefer for-loops over `purrr::map()`

- Use `cli::cli_abort()` for errors

- Always use `parsnip::` prefix

- Test all prediction types

- Document engine limitations

---

## Troubleshooting

See [Troubleshooting (Extension)](package-extension-requirements.md#common-issues-solutions) for complete guide.

**Common issues:**

- "engine not found" → Run `devtools::load_all()` to load registration

- "could not find function" → Check `set_dependency()` declaration

- Wrong prediction format → Add post-processing function

- Interface mismatch → Verify `protect` names match engine expectations

---

## Implementation Patterns

**Use these as templates - don't elaborate beyond what's shown:**

### Simple Single-Mode (2 files: R/zzz.R, tests/test-*.R)

For single mode + formula/data.frame interface. See [mode-handling.md](mode-handling.md) for multi-mode.

### Matrix Interface (2 files + set_encoding)

For matrix/xy interfaces, add `set_encoding()` after `set_fit()`. See [encoding-options.md](encoding-options.md) for details.

### Multi-Mode (2-3 files: R/zzz.R, tests, optional README)

Register each mode separately with mode-specific defaults. Classification needs both "class" and "prob" predictions. See [mode-handling.md](mode-handling.md) for complete examples.

**Keep it minimal** - reference docs for details, don't replicate them.

---

## File Organization

**Extension development:** Create only necessary files:

- `R/zzz.R` - Engine registration in .onLoad()

- `tests/testthat/test-[engine-name].R` - Engine tests

- `README.md` (if needed) - Usage examples

**Do NOT create these files:**

- IMPLEMENTATION_NOTES.md - Use roxygen @details instead

- IMPLEMENTATION_SUMMARY.md - Not needed

- example_usage.R - Use roxygen @examples instead

- DESIGN_DECISIONS.md - Use roxygen @details instead

- engine-comparison.R - Not needed

- TESTING_PLAN.md - Not needed

**Content belongs in code:**

| Content Type | ❌ Wrong | ✅ Correct |
| --- | --- | --- |
| Examples | example_usage.R | roxygen @examples |
| Notes | IMPLEMENTATION_NOTES.txt | roxygen @details |
| Design decisions | DESIGN_DECISIONS.md | roxygen @details |

---

## Reference Documentation

### Engine Implementation

- [Engine Implementation Guide](engine-implementation.md) - Complete registration details

- [Fit and Predict Methods](fit-predict-methods.md) - Implementation patterns

- [Prediction Types](prediction-types.md) - All 11 types

- [Mode Handling](mode-handling.md) - Multi-mode support

- [Encoding Options](encoding-options.md) - Interface configuration

### Model System

- [Model Specification System](model-specification-system.md) - How parsnip models work

### Shared References

- [Extension Prerequisites](package-extension-prerequisites.md) - Package setup

- [Development Workflow](package-development-workflow.md) - Fast iteration

- [Extension Requirements](package-extension-requirements.md) - Complete guide

- [Roxygen Documentation](package-roxygen-documentation.md)

- [Package Imports](package-imports.md)

---

## Next Steps

1. **Complete extension prerequisites** following [Extension Prerequisites](package-extension-prerequisites.md)
2. **Plan your engine** - Model, modes, interface, prediction types
3. **Implement registration** - Follow step-by-step guide above
4. **Test thoroughly** - All interfaces and prediction types
5. **Document** - README with usage examples
6. **Consider contributing** - PR to parsnip if broadly useful

---

## Getting Help

- Check [Troubleshooting Guide](package-extension-requirements.md#common-issues-solutions)

- Review existing engines in reference documentation

- Study the main [Engine Implementation Guide](engine-implementation.md)

- Search GitHub issues: https://github.com/tidymodels/parsnip/issues
