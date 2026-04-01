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

**Where to add:**
- Registration: `R/[model]_data.R`
- Tests: `tests/testthat/test-[model].R` or `test-[model]-[engine].R`
- Documentation stub: `R/[model]_[engine].R` (optional)

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
