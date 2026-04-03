# Source Guide: Contributing Engines to Parsnip

Guide for contributing engines directly to the tidymodels/parsnip package (source development).

---

## When to Use This Guide

Use this guide when:

- Contributing an engine to tidymodels/parsnip via PR

- The engine is broadly useful to the community

- You're working inside the parsnip repository

**Don't use this guide for:**

- Adding engines in your own package → See [extension-guide.md](extension-guide.md)

- Creating new model types → See [../../add-parsnip-model](../../add-parsnip-model/SKILL.md)

---

## Quick Start

Fork repository, create branch, add engine to existing `R/[model]_data.R`:

```r
# In R/linear_reg_data.R, add new section:

# ------------------------------------------------------------------------------
# my_engine

set_model_engine("linear_reg", "regression", "my_engine")
set_dependency("linear_reg", "my_engine", "mypackage", "regression")

set_model_arg(
  model = "linear_reg",
  eng = "my_engine",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = FALSE
)

set_fit(
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

set_encoding(
  model = "linear_reg",
  eng = "my_engine",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)

set_pred(
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

Add tests to `tests/testthat/test-linear_reg.R` or create `test-linear_reg-my_engine.R`.

Update `NEWS.md`:
```markdown
## New Features

* Added "my_engine" engine for `linear_reg()` (#PR_NUMBER)
```

---

## Key Advantages

**Source development benefits:**
1. No `parsnip::` prefix needed
2. Can use internal functions if necessary
3. Part of official tidymodels
4. Better discovery by users

**Responsibilities:**

- Follow parsnip conventions

- Comprehensive testing

- Maintain for releases

- Respond to issues

---

## File Organization

**CRITICAL: Add to existing files, don't create new ones**

### Registration Files

**Always add to existing `R/[model]_data.R` file:**

```r
# R/linear_reg_data.R already exists in parsnip
# Add your engine to this file, don't create linear_reg_my_engine_data.R

# ------------------------------------------------------------------------------
# my_engine  ← Add comment header like other engines

set_model_engine(...)  # ← NO parsnip:: prefix
set_dependency(...)    # ← NO parsnip:: prefix
set_fit(...)          # ← NO parsnip:: prefix
```

**File should contain ONLY registrations:**
- ✅ DO: Add `set_*()` calls to `R/[model]_data.R`
- ❌ DON'T: Create `R/[model]_my_engine.R`
- ❌ DON'T: Create helper files like `R/my_engine_utils.R`
- ❌ DON'T: Add implementation code (that goes in prediction `func`)

### Test Files

**Add tests to existing `tests/testthat/test-[model].R`:**

```r
# tests/testthat/test-linear_reg.R already exists
# Add your tests to this file with comment header

# ------------------------------------------------------------------------------
# my_engine

test_that("my_engine fits", {
  skip_if_not_installed("mypackage")
  # ... tests
})
```

**Or create engine-specific test file:**
```r
# tests/testthat/test-linear_reg-my_engine.R
# Only if many tests or complex scenarios
```

**Target: 1-2 files total**
- Extension development: 2-3 files (R/, tests/, maybe README)
- Source development: **1-2 files** (additions to existing files)

---

## NO Prefix Pattern

**CRITICAL DIFFERENCE from extension development:**

```r
# ❌ WRONG - Extension pattern (with prefix)
parsnip::set_model_engine("linear_reg", "regression", "my_engine")
parsnip::set_dependency("linear_reg", "my_engine", "mypackage", "regression")

# ✅ CORRECT - Source pattern (NO prefix)
set_model_engine("linear_reg", "regression", "my_engine")
set_dependency("linear_reg", "my_engine", "mypackage", "regression")
```

**Why no prefix?**
- You're working INSIDE the parsnip package
- These functions are already available in the package namespace
- Using `parsnip::` is redundant and against conventions

**Quick check:** If you see `parsnip::` in your registration code, you're doing it wrong for source development.

---

## Deterministic Source Development Pattern

**Exact steps for adding an engine to parsnip source:**

### Step 1: Identify Target File

```bash
# Find the correct *_data.R file
ls R/*_data.R
# Example: R/linear_reg_data.R, R/boost_tree_data.R
```

### Step 2: Add Engine Registration (NO prefix)

```r
# In R/linear_reg_data.R - add at end of file

# ------------------------------------------------------------------------------
# xgboost

set_model_engine("linear_reg", "regression", "xgboost")  # NO parsnip::
set_dependency("linear_reg", "xgboost", "xgboost", "regression")

set_model_arg(
  model = "linear_reg",
  eng = "xgboost",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = FALSE
)

set_fit(
  model = "linear_reg",
  eng = "xgboost",
  mode = "regression",
  value = list(
    interface = "matrix",
    protect = c("x", "y"),
    func = c(pkg = "xgboost", fun = "xgb.train"),
    defaults = list(objective = "reg:squarederror")
  )
)

set_encoding(
  model = "linear_reg",
  eng = "xgboost",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)

set_pred(
  model = "linear_reg",
  eng = "xgboost",
  mode = "regression",
  type = "numeric",
  value = list(...)
)
```

### Step 3: Add Tests to Existing Test File

```r
# In tests/testthat/test-linear_reg.R - add at end

# ------------------------------------------------------------------------------
# xgboost

test_that("xgboost fits", {
  skip_if_not_installed("xgboost")
  # ... tests using NO prefix
  spec <- linear_reg() |> set_engine("xgboost")
  fit <- fit(spec, mpg ~ ., data = mtcars)
  expect_s3_class(fit, "model_fit")
})
```

### Step 4: Update NEWS.md

```markdown
## New Features

* Added "xgboost" engine for `linear_reg()` (@your_github, #PR_NUMBER)
```

**Total files modified: 2** (R/*_data.R, tests/testthat/test-*.R)
**Total files created: 0** (add to existing files)

---

## Testing

```r
# In tests/testthat/test-linear_reg.R

# ------------------------------------------------------------------------------
# my_engine

test_that("my_engine fits", {
  skip_if_not_installed("mypackage")

  spec <- linear_reg() |> set_engine("my_engine")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, mtcars[1:5, ])
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
})

test_that("my_engine formula and xy equivalent", {
  skip_if_not_installed("mypackage")

  spec <- linear_reg() |> set_engine("my_engine")

  fit_formula <- fit(spec, mpg ~ hp + wt, data = mtcars)
  fit_xy <- fit_xy(spec, x = mtcars[, c("hp", "wt")], y = mtcars$mpg)

  pred_formula <- predict(fit_formula, mtcars[1:5, ])
  pred_xy <- predict(fit_xy, mtcars[1:5, ])

  expect_equal(pred_formula, pred_xy, tolerance = 1e-5)
})
```

---

## PR Checklist

- [ ] Engine registered in `R/[model]_data.R`

- [ ] All prediction types implemented

- [ ] Tests added for engine

- [ ] Formula and xy interfaces tested

- [ ] NEWS.md updated

- [ ] `devtools::check()` passes

- [ ] Snapshot tests for errors (if applicable)

---

## Additional Resources

See:

- [Engine Implementation](engine-implementation.md) - Complete registration guide

- [Best Practices (Source)](best-practices-source.md) - Parsnip conventions

- [Troubleshooting (Source)](troubleshooting-source.md) - Common issues

- [Testing Patterns (Source)](testing-patterns-source.md) - Testing guide
