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

- [Extension Prerequisites](./package-extension-prerequisites.md)

- Basic R package development knowledge

**Parsnip Knowledge:**

- [Engine Implementation](engine-implementation.md) - Core concepts

- Which model you're extending

---

## Quick Start

Create package structure, add parsnip dependency, register engine in .onLoad():

```r
# R/zzz.R
.onLoad <- function(libname, pkgname) {
  register_my_engine()
}

register_my_engine <- function() {
  # 1. Register engine
  parsnip::set_model_engine("linear_reg", "regression", "my_engine")

  # 2. Dependencies
  parsnip::set_dependency("linear_reg", "my_engine", "mypackage", "regression")

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

---

## Key Constraints

**Extension development constraints:**
1. Always use `parsnip::` prefix
2. Only use exported functions
3. Register in .onLoad()
4. Cannot access internals with `:::`

---

## Testing

```r
test_that("my_engine works", {
  skip_if_not_installed("mypackage")

  spec <- linear_reg() |> parsnip::set_engine("my_engine")
  fit <- parsnip::fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, mtcars[1:5, ])
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
})
```

---

## Additional Resources

See main skill references:

- [Engine Implementation](engine-implementation.md) - Complete guide

- [Fit and Predict Methods](fit-predict-methods.md) - Implementation details

- [Prediction Types](prediction-types.md) - All prediction types

- [Mode Handling](mode-handling.md) - Multi-mode support

- [Encoding Options](encoding-options.md) - Interface types
