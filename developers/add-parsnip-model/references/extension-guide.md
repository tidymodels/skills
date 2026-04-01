# Extension Guide: Creating New Parsnip Models

Step-by-step guide for creating new model specifications in your own R package (extension development).

---

## When to Use This Guide

Use this guide when:

- Creating a new R package that defines a novel model type

- The model type doesn't exist in parsnip yet

- You want to extend parsnip without modifying its source code

**Don't use this guide for:**

- Adding engines to existing models → See [add-parsnip-engine](../../add-parsnip-engine/SKILL.md)

- Contributing to parsnip source → See [source-guide.md](source-guide.md)

---

## Prerequisites

Before starting, ensure you have:

**R Package Setup:**

- [Extension Prerequisites](../../shared-references/package-extension-prerequisites.md) - Package structure, DESCRIPTION, etc.

- Basic R package development knowledge

- devtools or usethis installed

**Parsnip Knowledge:**

- [Model Specification System](model-specification-system.md) - Core concepts

- Understanding of modes and prediction types

---

## Key Constraints for Extension Development

**Critical limitations:**

1. **Use `parsnip::` prefix** - Always namespace all parsnip functions
2. **No internal functions** - Cannot use `:::` to access parsnip internals
3. **Exported functions only** - Only use documented, exported functions
4. **Registration in .onLoad()** - All `set_*()` calls must run when package loads

---

## Step-by-Step Implementation

### Step 1: Set Up Package Structure

Create the basic package structure:

```r
# If starting fresh
usethis::create_package("mymodels")

# Add parsnip as dependency
usethis::use_package("parsnip", "Imports")
usethis::use_package("rlang", "Imports")
```

**Package structure:**
```
mymodels/
├── DESCRIPTION
├── NAMESPACE
├── R/
│   ├── my_model.R        # Model constructor
│   └── zzz.R             # .onLoad() with registration
└── tests/
    └── testthat/
        └── test-my_model.R
```

### Step 2: Create Model Constructor

Create `R/my_model.R` with your model specification function:

```r
#' My Custom Model
#'
#' A model specification for my custom algorithm.
#'
#' @param mode A single character string for the type of model.
#'   Possible values are "regression" and "classification".
#' @param penalty A non-negative number for the regularization penalty.
#' @param mixture A number between 0 and 1 for the mixing proportion.
#' @param engine A character string for the software to use. Default is "custom".
#'
#' @details
#' This model implements a custom algorithm for both regression and classification tasks.
#'
#' @return A model specification object with class `my_model`.
#'
#' @examples
#' # Regression
#' my_model(mode = "regression")
#'
#' # Classification with parameters
#' my_model(mode = "classification", penalty = 0.1)
#'
#' @export
my_model <- function(mode = "unknown",
                     penalty = NULL,
                     mixture = NULL,
                     engine = "custom") {

  # Validate mode
  if (!mode %in% c("unknown", "regression", "classification")) {
    rlang::abort("mode must be 'regression' or 'classification'")
  }

  # Capture arguments
  args <- list(
    penalty = rlang::enquo(penalty),
    mixture = rlang::enquo(mixture)
  )

  # Create model specification
  parsnip::new_model_spec(
    "my_model",
    args = args,
    eng_args = NULL,
    mode = mode,
    user_specified_mode = !missing(mode),
    method = NULL,
    engine = engine,
    user_specified_engine = !missing(engine)
  )
}
```

**Key points:**

- Always use `parsnip::new_model_spec()` with namespace

- Use `rlang::enquo()` for all main arguments

- Track user specification with `!missing()`

- Export with `@export`

### Step 3: Register Model in .onLoad()

Create `R/zzz.R` to register your model when the package loads:

```r
# R/zzz.R

.onLoad <- function(libname, pkgname) {
  # Declare model exists
  parsnip::set_new_model("my_model")

  # Register modes
  parsnip::set_model_mode("my_model", "regression")
  parsnip::set_model_mode("my_model", "classification")

  # Register regression engine
  register_my_model_regression()

  # Register classification engine
  register_my_model_classification()
}

register_my_model_regression <- function() {
  # Engine declaration
  parsnip::set_model_engine(
    model = "my_model",
    mode = "regression",
    eng = "custom"
  )

  # Dependencies
  parsnip::set_dependency(
    model = "my_model",
    eng = "custom",
    pkg = "stats",  # Or your algorithm package
    mode = "regression"
  )

  # Argument translation
  parsnip::set_model_arg(
    model = "my_model",
    eng = "custom",
    parsnip = "penalty",
    original = "lambda",
    func = list(pkg = "dials", fun = "penalty"),
    has_submodel = FALSE
  )

  parsnip::set_model_arg(
    model = "my_model",
    eng = "custom",
    parsnip = "mixture",
    original = "alpha",
    func = list(pkg = "dials", fun = "mixture"),
    has_submodel = FALSE
  )

  # Fit method
  parsnip::set_fit(
    model = "my_model",
    eng = "custom",
    mode = "regression",
    value = list(
      interface = "formula",
      protect = c("formula", "data"),
      func = c(pkg = "stats", fun = "lm"),
      defaults = list()
    )
  )

  # Numeric predictions
  parsnip::set_pred(
    model = "my_model",
    eng = "custom",
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

  # Raw predictions
  parsnip::set_pred(
    model = "my_model",
    eng = "custom",
    mode = "regression",
    type = "raw",
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

register_my_model_classification <- function() {
  # Similar structure for classification mode
  parsnip::set_model_engine(
    model = "my_model",
    mode = "classification",
    eng = "custom"
  )

  parsnip::set_dependency(
    model = "my_model",
    eng = "custom",
    pkg = "stats",
    mode = "classification"
  )

  # ... continue with fit and predict for classification
}
```

**Why .onLoad()?**

- Runs automatically when package loads

- Users don't need to call anything

- Registration happens before they use the model

### Step 4: Add Documentation

Document your model thoroughly:

```r
#' @details
#' ## Available Engines
#'
#' The `my_model()` function can be used with the following engines:
#'
#' - **custom** (default): Uses a custom implementation
#'
#' ## Main Arguments
#'
#' - `penalty`: Controls regularization strength (larger = more regularization)
#' - `mixture`: Mix of L1 (lasso) and L2 (ridge) penalties (0 = pure ridge, 1 = pure lasso)
#'
#' ## Modes
#'
#' This model supports:
#' - `"regression"`: For numeric outcomes
#' - `"classification"`: For categorical outcomes
#'
#' Set the mode with:
#' ```r
#' my_model(mode = "regression")
#' my_model(mode = "classification")
#' ```
#'
#' @seealso [parsnip::fit.model_spec()], [parsnip::set_engine()]
```

### Step 5: Add Tests

Create comprehensive tests in `tests/testthat/test-my_model.R`:

```r
test_that("my_model constructor works", {
  spec <- my_model()

  expect_s3_class(spec, "my_model")
  expect_s3_class(spec, "model_spec")
  expect_equal(spec$mode, "unknown")
})

test_that("my_model accepts arguments", {
  spec <- my_model(penalty = 0.1, mixture = 0.5)

  expect_true(rlang::is_quosure(spec$args$penalty))
  expect_equal(rlang::eval_tidy(spec$args$penalty), 0.1)

  expect_true(rlang::is_quosure(spec$args$mixture))
  expect_equal(rlang::eval_tidy(spec$args$mixture), 0.5)
})

test_that("my_model fits with regression mode", {
  spec <- my_model(mode = "regression") |>
    parsnip::set_engine("custom")

  fit <- parsnip::fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")
  expect_s3_class(fit$fit, "lm")
})

test_that("my_model makes predictions", {
  spec <- my_model(mode = "regression") |>
    parsnip::set_engine("custom")

  fit <- parsnip::fit(spec, mpg ~ ., data = mtcars)
  preds <- predict(fit, new_data = mtcars[1:5, ])

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
  expect_type(preds$.pred, "double")
})

test_that("my_model works with workflows", {
  skip_if_not_installed("workflows")

  spec <- my_model(mode = "regression") |>
    parsnip::set_engine("custom")

  wf <- workflows::workflow() |>
    workflows::add_formula(mpg ~ .) |>
    workflows::add_model(spec)

  fit <- parsnip::fit(wf, data = mtcars)
  preds <- predict(fit, new_data = mtcars[1:5, ])

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred")
})
```

### Step 6: Build and Load Package

Test your package:

```r
# Load all code
devtools::load_all()

# Test the model
spec <- my_model(mode = "regression") |>
  set_engine("custom")

fit <- fit(spec, mpg ~ ., data = mtcars)
predict(fit, mtcars[1:5, ])

# Run tests
devtools::test()

# Check package
devtools::check()
```

---

## Complete Example: Single-Mode Model

Simpler example with only regression support:

```r
# R/simple_model.R

#' @export
simple_model <- function(penalty = NULL, engine = "default") {
  args <- list(penalty = rlang::enquo(penalty))

  parsnip::new_model_spec(
    "simple_model",
    args = args,
    eng_args = NULL,
    mode = "regression",  # Fixed mode
    user_specified_mode = FALSE,
    method = NULL,
    engine = engine,
    user_specified_engine = !missing(engine)
  )
}

# R/zzz.R

.onLoad <- function(libname, pkgname) {
  parsnip::set_new_model("simple_model")
  parsnip::set_model_mode("simple_model", "regression")

  parsnip::set_model_engine("simple_model", "regression", "default")
  parsnip::set_dependency("simple_model", "default", "stats", "regression")

  parsnip::set_fit(
    model = "simple_model",
    eng = "default",
    mode = "regression",
    value = list(
      interface = "formula",
      protect = c("formula", "data"),
      func = c(pkg = "stats", fun = "lm"),
      defaults = list()
    )
  )

  parsnip::set_pred(
    model = "simple_model",
    eng = "default",
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

---

## Common Patterns

### Pattern 1: Matrix Interface Engine

For engines requiring numeric matrices:

```r
parsnip::set_fit(
  model = "my_model",
  eng = "glmnet_engine",
  mode = "regression",
  value = list(
    interface = "matrix",
    protect = c("x", "y"),
    func = c(pkg = "glmnet", fun = "glmnet"),
    defaults = list(family = "gaussian")
  )
)

parsnip::set_encoding(
  model = "my_model",
  eng = "glmnet_engine",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)
```

### Pattern 2: Post-Processing Predictions

When engine returns non-standard format:

```r
parsnip::set_pred(
  model = "my_model",
  eng = "custom",
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

### Pattern 3: Multiple Engines

Register different engines in separate helper functions:

```r
.onLoad <- function(libname, pkgname) {
  parsnip::set_new_model("my_model")
  parsnip::set_model_mode("my_model", "regression")

  register_lm_engine()
  register_glmnet_engine()
  register_custom_engine()
}

register_lm_engine <- function() {
  parsnip::set_model_engine("my_model", "regression", "lm")
  # ... rest of registration
}

register_glmnet_engine <- function() {
  parsnip::set_model_engine("my_model", "regression", "glmnet")
  # ... rest of registration
}
```

---

## Development Workflow

**Iterative development cycle:**

1. **Write code** - Add or modify constructor/registration
2. **Load package** - `devtools::load_all()`
3. **Test interactively** - Try `fit()` and `predict()`
4. **Write tests** - Add formal tests
5. **Check** - Run `devtools::check()`
6. **Iterate** - Fix issues and repeat

**Fast iteration:**
```r
# In console
devtools::load_all()

spec <- my_model(mode = "regression") |> set_engine("custom")
fit <- fit(spec, mpg ~ ., mtcars)
predict(fit, mtcars[1:3, ])
```

See [Development Workflow](../../shared-references/package-development-workflow.md) for more details.

---

## Integration with Tidymodels

### Using with Workflows

```r
library(workflows)

wf <- workflow() |>
  add_formula(mpg ~ .) |>
  add_model(my_model(mode = "regression"))

fit <- fit(wf, data = mtcars)
predict(fit, mtcars[1:5, ])
```

### Using with Recipes

```r
library(recipes)

rec <- recipe(mpg ~ ., data = mtcars) |>
  step_normalize(all_numeric_predictors())

wf <- workflow() |>
  add_recipe(rec) |>
  add_model(my_model(mode = "regression"))

fit <- fit(wf, data = mtcars)
```

### Using with Tune

```r
library(tune)

spec <- my_model(penalty = tune(), mixture = tune()) |>
  set_engine("custom") |>
  set_mode("regression")

# Use in tune_grid(), tune_bayes(), etc.
```

---

## Troubleshooting

### Issue: "could not find function 'new_model_spec'"

**Problem:** Missing namespace prefix.

**Solution:**
```r
# Wrong
spec <- new_model_spec(...)

# Correct
spec <- parsnip::new_model_spec(...)
```

### Issue: "engine not found"

**Problem:** Registration didn't run.

**Solution:** Check that `.onLoad()` is defined and `set_model_engine()` is called.

```r
# Debug registration
devtools::load_all()
parsnip::show_engines("my_model")
```

### Issue: Predictions fail

**Problem:** Prediction type not registered.

**Solution:** Add `set_pred()` call for each type you want to support.

### Issue: Tests fail on CI

**Problem:** Package dependencies not declared.

**Solution:** Add all dependencies to DESCRIPTION:
```r
usethis::use_package("parsnip", "Imports")
usethis::use_package("rlang", "Imports")
usethis::use_package("stats", "Imports")  # If using stats functions
```

---

## Next Steps

After creating your model:

1. **Test thoroughly** - All modes, prediction types, edge cases
2. **Document comprehensively** - Help users understand your model
3. **Add vignettes** - Show real-world examples
4. **Consider CRAN** - Share with the community
5. **Maintain** - Keep up with parsnip updates

---

## Additional Resources

**Reference guides:**

- [Model Constructors](model-constructors.md) - Detailed constructor design

- [Registration Sequence](registration-sequence.md) - Complete registration steps

- [Argument Design](argument-design.md) - Main argument patterns

**Shared references:**

- [Fit and Predict Methods](fit-predict-methods.md) - Implementation details

- [Prediction Types](prediction-types.md) - All 11 types

- [Mode Handling](mode-handling.md) - Multi-mode support

**Testing:**


**Best practices:**

- [Extension Prerequisites](../../shared-references/package-extension-prerequisites.md) - Package setup

- [Development Workflow](../../shared-references/package-development-workflow.md) - Iteration cycle
