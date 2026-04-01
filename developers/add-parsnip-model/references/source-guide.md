# Source Guide: Contributing New Models to Parsnip

Guide for contributing new model specifications directly to the tidymodels/parsnip package (source development).

---

## When to Use This Guide

Use this guide when:

- Contributing a new model type to tidymodels/parsnip via PR

- The model is broadly useful to the Tidymodels community

- You're working inside the parsnip repository

**Don't use this guide for:**

- Creating models in your own package → See [extension-guide.md](extension-guide.md)

- Adding engines to existing models → See [../../add-parsnip-engine](../../add-parsnip-engine/SKILL.md)

---

## Prerequisites

Before starting:

**Repository access:**

- Fork tidymodels/parsnip on GitHub

- Clone your fork locally

- Set up development environment

**Knowledge:**

- [Model Specification System](model-specification-system.md) - Core concepts

- Parsnip architecture and conventions

- Git/GitHub workflow for PRs

---

## Key Advantages of Source Development

**Benefits over extension development:**

1. **No namespace prefix needed** - Use `set_fit()` not `parsnip::set_fit()`
2. **Access internal functions** - Can use `:::` and internal helpers
3. **Integrated testing** - Use parsnip's test infrastructure
4. **Official support** - Part of tidymodels ecosystem
5. **Better discovery** - Users find it automatically

**Responsibilities:**

- Follow parsnip conventions strictly

- Comprehensive testing required

- Maintain for parsnip releases

- Respond to issues/PRs related to your model

---

## Repository Structure

```
parsnip/
├── R/
│   ├── [model_type].R           # Model constructor
│   ├── [model_type]_data.R      # Engine registrations
│   ├── [model]_[engine].R       # Engine documentation stubs
│   ├── aaa_models.R             # Infrastructure
│   └── misc.R                   # Helper functions
├── tests/
│   └── testthat/
│       ├── test-[model].R       # Model tests
│       ├── test-[model]-[engine].R  # Engine-specific tests
│       └── helper-objects.R     # Test data
└── man/                         # Documentation
```

---

## Step-by-Step Implementation

### Step 1: Fork and Clone Repository

```bash
# Fork on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/parsnip.git
cd parsnip

# Add upstream remote
git remote add upstream https://github.com/tidymodels/parsnip.git

# Create branch for your model
git checkout -b add-my-model
```

### Step 2: Create Model Constructor

Create `R/my_model.R`:

```r
#' My Model Specification
#'
#' `my_model()` defines a model for [describe the algorithm].
#'
#' @param mode A single character string for the type of model. Possible values
#'   for this model are "regression" and "classification".
#' @param penalty A non-negative number representing the total amount of
#'   regularization. For `glmnet` engine, this corresponds to lambda.
#' @param mixture A number between zero and one (inclusive) giving the proportion
#'   of L1 regularization (i.e. lasso) in the model.
#' @param engine A single character string specifying what computational engine
#'   to use for fitting. Default is "custom".
#'
#' @templateVar modeltype my_model
#' @template spec-details
#'
#' @template spec-references
#'
#' @seealso \Sexpr[stage=render,results=rd]{parsnip:::make_seealso_list("my_model")}
#'
#' @examplesIf !parsnip:::is_cran_check()
#' # Regression mode
#' my_model(mode = "regression")
#'
#' # Classification mode
#' my_model(mode = "classification", penalty = 0.1)
#'
#' @export
my_model <- function(mode = "unknown",
                     penalty = NULL,
                     mixture = NULL,
                     engine = "custom") {

  # Check mode
  if (!mode %in% c("unknown", "regression", "classification")) {
    cli::cli_abort(
      "mode must be 'regression' or 'classification', not {.val {mode}}"
    )
  }

  # Capture arguments
  args <- list(
    penalty = rlang::enquo(penalty),
    mixture = rlang::enquo(mixture)
  )

  # Create specification
  new_model_spec(
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

#' @export
print.my_model <- function(x, ...) {
  cat("My Model Specification (", x$mode, ")\n\n", sep = "")
  model_printer(x, ...)

  if (!is.null(x$method$fit$args)) {
    cat("Model fit template:\n")
    print(show_call(x))
  }

  invisible(x)
}
```

**Key differences from extension:**

- No `parsnip::` prefix

- Use `new_model_spec()` directly

- Use `cli::cli_abort()` for errors

- Use parsnip's template system

- Dynamic seealso with Sexpr

- Custom print method

### Step 3: Create Engine Registration File

Create `R/my_model_data.R`:

```r
# Declare model and modes
set_new_model("my_model")
set_model_mode("my_model", "regression")
set_model_mode("my_model", "classification")

# ------------------------------------------------------------------------------
# custom engine - regression

set_model_engine("my_model", "regression", "custom")
set_dependency("my_model", "custom", "stats", mode = "regression")

set_model_arg(
  model = "my_model",
  eng = "custom",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = FALSE
)

set_model_arg(
  model = "my_model",
  eng = "custom",
  parsnip = "mixture",
  original = "alpha",
  func = list(pkg = "dials", fun = "mixture"),
  has_submodel = FALSE
)

set_fit(
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

set_pred(
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

set_pred(
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

# ------------------------------------------------------------------------------
# custom engine - classification

set_model_engine("my_model", "classification", "custom")
set_dependency("my_model", "custom", "stats", mode = "classification")

set_fit(
  model = "my_model",
  eng = "custom",
  mode = "classification",
  value = list(
    interface = "formula",
    protect = c("formula", "data"),
    func = c(pkg = "stats", fun = "glm"),
    defaults = list(family = binomial())
  )
)

set_pred(
  model = "my_model",
  eng = "custom",
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
      newdata = rlang::expr(new_data),
      type = "response"
    )
  )
)

set_pred(
  model = "my_model",
  eng = "custom",
  mode = "classification",
  type = "prob",
  value = list(
    pre = NULL,
    post = function(results, object) {
      tibble::tibble(
        .pred_0 = 1 - results,
        .pred_1 = results
      )
    },
    func = c(fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data),
      type = "response"
    )
  )
)
```

**Organization:**

- Group by engine

- Use comment separators (`# ----`)

- Order: set_model_engine → set_dependency → set_model_arg → set_fit → set_pred

- Register all prediction types

### Step 4: Create Engine Documentation Stub

Create `R/my_model_custom.R` (just documentation):

```r
# These functions are the R function calls for fitting and prediction of
# the model. They are executed using the engine `custom` for `my_model()`
# models.
#
# @includeRmd man/rmd/my_model_custom.Rmd details

# ------------------------------------------------------------------------------

#' @keywords internal
#' @rdname my_model_engines
#' @export
make_my_model_custom <- function() {
  parsnip_model(
    "my_model",
    eng = "custom",
    mode = "regression"
  )
}
```

Then create corresponding markdown file in `man/rmd/my_model_custom.Rmd`.

### Step 5: Add Tests

Create `tests/testthat/test-my_model.R`:

```r
# ------------------------------------------------------------------------------
# Setup

test_that("my_model constructor", {
  expect_snapshot(my_model())
  expect_snapshot(my_model(mode = "regression"))
  expect_snapshot(my_model(mode = "classification"))
})

test_that("my_model validates mode", {
  expect_snapshot(
    my_model(mode = "invalid"),
    error = TRUE
  )
})

# ------------------------------------------------------------------------------
# Regression mode

test_that("my_model regression with custom engine", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |>
    set_engine("custom")

  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")
  expect_s3_class(fit$fit, "lm")

  preds <- predict(fit, new_data = mtcars[1:5, ])
  expect_s3_class(preds, "tbl_df")
  expect_equal(nrow(preds), 5)
  expect_named(preds, ".pred")
})

test_that("my_model regression predictions", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |>
    set_engine("custom")

  fit <- fit(spec, mpg ~ ., data = mtcars)

  # Numeric predictions
  preds_num <- predict(fit, mtcars[1:3, ], type = "numeric")
  expect_named(preds_num, ".pred")
  expect_type(preds_num$.pred, "double")

  # Raw predictions
  preds_raw <- predict(fit, mtcars[1:3, ], type = "raw")
  expect_type(preds_raw, "double")
})

# ------------------------------------------------------------------------------
# Classification mode

test_that("my_model classification with custom engine", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "classification") |>
    set_engine("custom")

  # Binary classification
  data <- data.frame(
    y = factor(rep(c("A", "B"), each = 10)),
    x1 = rnorm(20),
    x2 = rnorm(20)
  )

  fit <- fit(spec, y ~ ., data = data)

  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, new_data = data[1:5, ])
  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred_class")
})

test_that("my_model classification predictions", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "classification") |>
    set_engine("custom")

  data <- data.frame(
    y = factor(rep(c("A", "B"), each = 10)),
    x1 = rnorm(20),
    x2 = rnorm(20)
  )

  fit <- fit(spec, y ~ ., data = data)

  # Class predictions
  preds_class <- predict(fit, data[1:3, ], type = "class")
  expect_s3_class(preds_class$.pred_class, "factor")

  # Probability predictions
  preds_prob <- predict(fit, data[1:3, ], type = "prob")
  expect_true(all(grepl("^\\.pred_", names(preds_prob))))
  expect_equal(ncol(preds_prob), 2)
})

# ------------------------------------------------------------------------------
# fit_xy interface

test_that("my_model works with fit_xy", {
  skip_if_not_installed("stats")

  spec <- my_model(mode = "regression") |>
    set_engine("custom")

  fit_formula <- fit(spec, mpg ~ hp + wt, data = mtcars)
  fit_xy <- fit_xy(spec, x = mtcars[, c("hp", "wt")], y = mtcars$mpg)

  pred_formula <- predict(fit_formula, mtcars[1:5, ])
  pred_xy <- predict(fit_xy, mtcars[1:5, ])

  expect_equal(pred_formula, pred_xy, tolerance = 1e-5)
})
```

**Key patterns:**

- Use `expect_snapshot()` for error messages

- Skip tests if packages unavailable

- Test both modes separately

- Test all prediction types

- Test both fit() and fit_xy()

### Step 6: Update NEWS.md

Add entry to `NEWS.md`:

```markdown
# parsnip (development version)

## New Features

* Added `my_model()` specification for [describe algorithm]. Supports both
  regression and classification modes with the "custom" engine. (#PR_NUMBER)

## Bug Fixes

...
```

### Step 7: Build and Check

Test your changes:

```r
# Load package
devtools::load_all()

# Run tests
devtools::test()

# Check package
devtools::check()

# Build documentation
devtools::document()
```

### Step 8: Submit Pull Request

```bash
# Commit changes
git add R/my_model.R R/my_model_data.R tests/testthat/test-my_model.R
git commit -m "Add my_model() specification

- Supports regression and classification modes

- Implements custom engine

- Full test coverage

- Documentation included

Closes #ISSUE_NUMBER"

# Push to your fork
git push origin add-my-model
```

Then create PR on GitHub with description of:

- What the model does

- Which modes/engines are supported

- Example usage

- Testing done

---

## Using Internal Functions

Source development has access to parsnip internals:

```r
# Validation helpers
check_eng_val()
check_mode_val()
check_model_exists()

# Environment management
get_model_env()
get_from_env()
set_in_env()

# Utilities
make_classes()
spec_is_possible()
model_printer()
```

**Use judiciously:**

- Prefer exported functions when available

- Comment why you need the internal function

- Aware they may change in future versions

---

## Documentation Patterns

### Use Template System

```r
#' @templateVar modeltype my_model
#' @template spec-details
#' @template spec-references
```

### Dynamic Content

```r
#' @seealso \Sexpr[stage=render,results=rd]{parsnip:::make_seealso_list("my_model")}
```

### Example Guards

```r
#' @examplesIf !parsnip:::is_cran_check()
#' my_model() |> fit(mpg ~ ., data = mtcars)
```

---

## Testing Patterns

### Snapshot Testing

Use for error messages and printed output:

```r
test_that("errors are informative", {
  expect_snapshot(
    my_model(mode = "invalid"),
    error = TRUE
  )
})

test_that("printing works", {
  expect_snapshot(my_model())
})
```

### Test Helpers

Use helpers from `tests/testthat/helper-objects.R`:

```r
test_that("works with test data", {
  spec <- my_model(mode = "regression") |> set_engine("custom")
  fit <- fit(spec, mpg ~ ., data = mtcars)
  # ...
})
```

---

## Code Style

Follow tidymodels style:

```r
# Use base pipe |>
spec |> set_engine("custom")

# Use cli for errors
cli::cli_abort("Problem: {problem}")

# Two-space indentation
set_fit(
  model = "my_model",
  value = list(...)
)

# Use roxygen2 for documentation
#' @param mode Description
```

---

## PR Checklist

Before submitting:

- [ ] All tests pass (`devtools::test()`)

- [ ] Package checks cleanly (`devtools::check()`)

- [ ] Documentation builds (`devtools::document()`)

- [ ] NEWS.md updated

- [ ] Code follows tidymodels style

- [ ] Snapshot tests for error messages

- [ ] Examples work and are tested

- [ ] All engines fully tested

- [ ] Both modes tested (if multi-mode)

- [ ] All prediction types tested

- [ ] Git history is clean

---

## Maintenance

After PR is merged:

**Monitor:**

- Watch for issues related to your model

- Respond to bug reports promptly

- Keep documentation current

**Update:**

- When new parsnip versions release

- If underlying engine packages change

- When new features are requested

**Support:**

- Answer questions on GitHub/forum

- Help maintain test coverage

- Suggest improvements

---

## Common Review Comments

**Documentation:**

- Add more details to @details

- Improve example clarity

- Fix formatting issues

**Code:**

- Use cli::cli_abort() not stop()

- Add snapshot test for errors

- Simplify complex logic

**Tests:**

- Add edge case tests

- Test with real data

- Cover error conditions

**Style:**

- Use base pipe |>

- Fix indentation

- Remove commented code

---

## Additional Resources

**Parsnip source files to study:**

- `R/linear_reg.R` - Simple model constructor

- `R/boost_tree_data.R` - Complex multi-mode registration

- `tests/testthat/test-linear_reg.R` - Testing patterns

**Best practices:**

- [Best Practices (Source)](best-practices-source.md) - Parsnip conventions

- [Troubleshooting (Source)](troubleshooting-source.md) - Common issues

**Testing:**

- [Testing Patterns (Source)](testing-patterns-source.md) - Source testing guide

