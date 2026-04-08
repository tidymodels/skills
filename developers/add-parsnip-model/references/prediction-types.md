# Parsnip Prediction Types

This guide covers all 11 prediction types supported by parsnip, how to implement
them, and when to use each type.

--------------------------------------------------------------------------------

## Overview

Parsnip standardizes prediction outputs across different modeling engines. Each
prediction type returns a tibble with specific column naming conventions.

**Available prediction types:**

**Regression modes:**

- `numeric` - Point predictions

- `conf_int` - Confidence intervals for mean

- `pred_int` - Prediction intervals for new observations

- `raw` - Raw engine output

**Classification modes:**

- `class` - Predicted class labels

- `prob` - Class probabilities

- `raw` - Raw engine output

**Censored regression modes:**

- `time` - Predicted event time

- `survival` - Survival probabilities

- `hazard` - Hazard estimates

- `linear_pred` - Linear predictor values

- `raw` - Raw engine output

**Quantile regression modes:**

- `quantile` - Quantile predictions

- `raw` - Raw engine output

--------------------------------------------------------------------------------

## Regression Prediction Types

### Numeric Predictions

**Purpose:** Point predictions for continuous outcomes.

**Output format:**

```r
tibble::tibble(.pred = c(1.2, 3.4, 5.6))
```

**Implementation:**

```r
set_pred(
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
```

**Column naming:**

- `.pred` - Required name for numeric predictions

- Must be numeric vector

- One value per row in `new_data`

**When to use:**

- Default prediction type for regression

- When you want single-value predictions

- For model comparison and evaluation

### Confidence Intervals

**Purpose:** Intervals for the mean response at given predictor values.

**Output format:**

```r
tibble::tibble(
  .pred_lower = c(1.0, 3.0, 5.0),
  .pred_upper = c(1.5, 4.0, 6.0)
)
```

**Implementation:**

```r
set_pred(
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

**Column naming:**

- `.pred_lower` - Lower bound of interval

- `.pred_upper` - Upper bound of interval

- Both must be numeric vectors

- Same length as `new_data` rows

**When to use:**

- When you need uncertainty quantification for mean response

- For statistical inference about population mean

- When showing confidence regions in plots

**Common pattern - using `post` for format conversion:**

```r
post = function(results, object) {
  # Engine may return matrix with different column names
  # Convert to standard format
  tibble::tibble(
    .pred_lower = results[, "lower"],  # or results[, 1]
    .pred_upper = results[, "upper"]   # or results[, 2]
  )
}
```

### Prediction Intervals

**Purpose:** Intervals for individual new observations (wider than confidence
intervals).

**Output format:**

```r
tibble::tibble(
  .pred_lower = c(0.5, 2.5, 4.5),
  .pred_upper = c(2.0, 4.5, 6.5)
)
```

**Implementation:**

```r
set_pred(
  model = "linear_reg",
  eng = "lm",
  mode = "regression",
  type = "pred_int",
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
      interval = "prediction",
      level = 0.95
    )
  )
)
```

**Column naming:**

- Same as confidence intervals: `.pred_lower` and `.pred_upper`

- Both must be numeric vectors

**When to use:**

- When predicting individual observations (not means)

- For uncertainty about specific future values

- When prediction uncertainty is more relevant than parameter uncertainty

**Key difference from conf_int:**

- Prediction intervals are wider (account for individual variation)

- Confidence intervals are for mean response

- Use `interval = "prediction"` vs `interval = "confidence"` in args

--------------------------------------------------------------------------------

## Classification Prediction Types

### Class Predictions

**Purpose:** Predicted class labels.

**Output format:**

```r
tibble::tibble(.pred_class = factor(c("setosa", "versicolor", "virginica")))
```

**Implementation:**

```r
set_pred(
  model = "logistic_reg",
  eng = "glm",
  mode = "classification",
  type = "class",
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

**Column naming:**

- `.pred_class` - Required name

- Must be a factor

- Levels should match training data levels

**When to use:**

- When you need hard predictions (not probabilities)

- For confusion matrices

- For classification accuracy metrics

**Common pattern - converting probabilities to classes:**

```r
post = function(results, object) {
  # results is probability matrix
  # Convert to class predictions
  pred_class <- apply(results, 1, which.max)
  pred_class <- colnames(results)[pred_class]
  tibble::tibble(.pred_class = factor(pred_class, levels = colnames(results)))
}
```

### Probability Predictions

**Purpose:** Probability estimates for each class.

**Output format:**

```r
tibble::tibble(
  .pred_setosa = c(0.8, 0.2, 0.1),
  .pred_versicolor = c(0.15, 0.7, 0.3),
  .pred_virginica = c(0.05, 0.1, 0.6)
)
```

**Implementation:**

```r
set_pred(
  model = "logistic_reg",
  eng = "glm",
  mode = "classification",
  type = "prob",
  value = list(
    pre = NULL,
    post = function(results, object) {
      # Convert to tibble with .pred_ prefix
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

**Column naming:**

- One column per class: `.pred_{class_name}`

- All columns must be numeric (0 to 1)

- Should sum to 1 across columns per row

- Column names must exactly match class levels

**When to use:**

- When you need probability estimates

- For ROC curves and calibration plots

- For threshold tuning

- When you want prediction confidence

**Common pattern - handling binary classification:**

```r
post = function(results, object) {
  # Binary classification may return single column
  # Need to create complementary probability
  if (is.vector(results)) {
    # results is probability of second class
    tibble::tibble(
      .pred_class1 = 1 - results,
      .pred_class2 = results
    )
  } else {
    # Already has both columns
    results <- as.data.frame(results)
    names(results) <- paste0(".pred_", names(results))
    tibble::as_tibble(results)
  }
}
```

--------------------------------------------------------------------------------

## Censored Regression Prediction Types

Used for survival analysis and time-to-event data.

### Time Predictions

**Purpose:** Predicted event times.

**Output format:**

```r
tibble::tibble(.pred_time = c(120, 450, 890))
```

**Implementation:**

```r
set_pred(
  model = "survival_reg",
  eng = "flexsurv",
  mode = "censored regression",
  type = "time",
  value = list(
    pre = NULL,
    post = NULL,
    func = c(pkg = "flexsurv", fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data),
      type = "response"
    )
  )
)
```

**Column naming:**

- `.pred_time` - Required name

- Must be numeric (time values)

- Units match training data

**When to use:**

- When you need point predictions for event time

- For median survival time

- For expected event times

### Survival Predictions

**Purpose:** Survival probability curves over time.

**Output format:**

```r
tibble::tibble(
  .pred = list(
    tibble(.eval_time = c(0, 10, 20), .pred_survival = c(1.0, 0.8, 0.6)),
    tibble(.eval_time = c(0, 10, 20), .pred_survival = c(1.0, 0.9, 0.7))
  )
)
```

**Implementation:**

```r
set_pred(
  model = "survival_reg",
  eng = "flexsurv",
  mode = "censored regression",
  type = "survival",
  value = list(
    pre = NULL,
    post = function(results, object) {
      # results is list of survival curves
      tibble::tibble(.pred = results)
    },
    func = c(pkg = "flexsurv", fun = "summary"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data),
      type = "survival",
      tidy = TRUE
    )
  )
)
```

**Column naming:**

- `.pred` - List column containing survival curves

- Each element is a tibble with:

  - `.eval_time` - Time points

  - `.pred_survival` - Survival probabilities

**When to use:**

- When you need full survival curves

- For plotting Kaplan-Meier style curves

- For time-dependent predictions

### Hazard Predictions

**Purpose:** Hazard rate estimates.

**Output format:**

```r
tibble::tibble(.pred_hazard = c(0.01, 0.05, 0.02))
```

**Implementation:**

```r
set_pred(
  model = "survival_reg",
  eng = "flexsurv",
  mode = "censored regression",
  type = "hazard",
  value = list(
    pre = NULL,
    post = NULL,
    func = c(pkg = "flexsurv", fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data),
      type = "hazard"
    )
  )
)
```

**Column naming:**

- `.pred_hazard` - Required name

- Must be numeric (hazard rates)

**When to use:**

- When working with proportional hazards models

- For risk assessment

- When hazard interpretation is more natural than survival

### Linear Predictor Predictions

**Purpose:** Linear predictor values from survival models.

**Output format:**

```r
tibble::tibble(.pred_linear_pred = c(-0.5, 1.2, 0.3))
```

**Implementation:**

```r
set_pred(
  model = "survival_reg",
  eng = "flexsurv",
  mode = "censored regression",
  type = "linear_pred",
  value = list(
    pre = NULL,
    post = NULL,
    func = c(pkg = "flexsurv", fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data),
      type = "link"
    )
  )
)
```

**Column naming:**

- `.pred_linear_pred` - Required name

- Must be numeric

**When to use:**

- When you need the linear predictor scale

- For model diagnostics

- When working on log-hazard scale

--------------------------------------------------------------------------------

## Quantile Regression Prediction Types

### Quantile Predictions

**Purpose:** Predictions at specific quantiles.

**Output format:**

```r
tibble::tibble(
  .pred = c(1.5, 3.2, 5.1),
  .quantile = c(0.5, 0.5, 0.5)
)
```

Or for multiple quantiles:

```r
tibble::tibble(
  .pred_lower = c(1.0, 2.5, 4.5),
  .pred = c(1.5, 3.2, 5.1),
  .pred_upper = c(2.0, 4.0, 6.0)
)
```

**Implementation:**

```r
set_pred(
  model = "linear_reg",
  eng = "quantreg",
  mode = "quantile regression",
  type = "quantile",
  value = list(
    pre = NULL,
    post = function(results, object) {
      tibble::tibble(
        .pred = results,
        .quantile = 0.5
      )
    },
    func = c(pkg = "quantreg", fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data),
      tau = 0.5
    )
  )
)
```

**Column naming:**

- `.pred` - Required for single quantile

- `.quantile` - Which quantile was predicted

- For multiple quantiles, use descriptive names (`.pred_lower`, `.pred`,
  `.pred_upper`)

**When to use:**

- When you need median (50th percentile) predictions

- For robust regression (less sensitive to outliers)

- When you need prediction intervals at specific quantiles

--------------------------------------------------------------------------------

## Raw Predictions

**Purpose:** Return engine's native output without standardization.

**Output format:**

```r
# Variable - whatever the engine returns
# Could be vector, matrix, list, custom object
```

**Implementation:**

```r
set_pred(
  model = "linear_reg",
  eng = "lm",
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
```

**No standardization:**

- No column name requirements

- No format requirements

- Returns exactly what engine returns

**When to use:**

- When you need engine-specific output format

- For debugging prediction issues

- When standard types don't capture what you need

- For custom post-processing

**When NOT to use:**

- For standard workflows (use typed predictions)

- When working with tidymodels ecosystem tools

- When you want consistent output format

--------------------------------------------------------------------------------

## Implementation Patterns

### Pattern 1: Direct Prediction (No Post-Processing)

Engine returns exactly the right format:

```r
set_pred(
  ...,
  type = "numeric",
  value = list(
    pre = NULL,
    post = NULL,  # No transformation needed
    func = c(fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newdata = rlang::expr(new_data)
    )
  )
)
```

### Pattern 2: Simple Post-Processing

Engine returns vector, convert to tibble:

```r
set_pred(
  ...,
  type = "numeric",
  value = list(
    pre = NULL,
    post = function(results, object) {
      tibble::tibble(.pred = as.numeric(results))
    },
    func = c(fun = "predict"),
    args = list(...)
  )
)
```

### Pattern 3: Matrix to Tibble Conversion

Engine returns matrix, need column renaming:

```r
set_pred(
  ...,
  type = "prob",
  value = list(
    pre = NULL,
    post = function(results, object) {
      results <- as.data.frame(results)
      names(results) <- paste0(".pred_", names(results))
      tibble::as_tibble(results)
    },
    func = c(fun = "predict"),
    args = list(...)
  )
)
```

### Pattern 4: Complex Restructuring

Engine returns list or complex object:

```r
set_pred(
  ...,
  type = "survival",
  value = list(
    pre = NULL,
    post = function(results, object) {
      # Extract survival curves from complex object
      curves <- lapply(results, function(x) {
        tibble::tibble(
          .eval_time = x$time,
          .pred_survival = x$surv
        )
      })
      tibble::tibble(.pred = curves)
    },
    func = c(pkg = "survival", fun = "survfit"),
    args = list(...)
  )
)
```

### Pattern 5: Conditional Output

Output format depends on engine settings:

```r
post = function(results, object) {
  if (is.matrix(results)) {
    # Multiple quantiles
    tibble::as_tibble(results)
  } else {
    # Single quantile
    tibble::tibble(.pred = results)
  }
}
```

--------------------------------------------------------------------------------

## Multi-Type Registration

Most models support multiple prediction types. Register each separately:

```r
# Numeric predictions
set_pred(..., type = "numeric", ...)

# Confidence intervals
set_pred(..., type = "conf_int", ...)

# Raw output
set_pred(..., type = "raw", ...)
```

**Not all engines support all types:**

- Only register types the engine can actually produce

- Some engines can't provide intervals

- Some classification engines can't provide probabilities

**Mode-specific types:**

- Don't register `prob` for regression modes

- Don't register `numeric` for classification modes

- Only register survival types for censored regression mode

--------------------------------------------------------------------------------

## Testing Prediction Types

Essential tests for each prediction type:

```r
test_that("numeric predictions have correct format", {
  spec <- linear_reg() |> set_engine("lm")
  fit <- fit(spec, mpg ~ ., data = mtcars)
  preds <- predict(fit, mtcars[1:5, ], type = "numeric")

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred")
  expect_type(preds$.pred, "double")
  expect_equal(nrow(preds), 5)
})

test_that("probability predictions sum to 1", {
  spec <- logistic_reg() |> set_engine("glm")
  fit <- fit(spec, Species ~ ., data = iris)
  preds <- predict(fit, iris[1:5, ], type = "prob")

  expect_s3_class(preds, "tbl_df")
  expect_true(all(grepl("^\\.pred_", names(preds))))
  row_sums <- rowSums(preds)
  expect_equal(row_sums, rep(1, 5), tolerance = 1e-10)
})

test_that("conf_int predictions have both bounds", {
  spec <- linear_reg() |> set_engine("lm")
  fit <- fit(spec, mpg ~ ., data = mtcars)
  preds <- predict(fit, mtcars[1:5, ], type = "conf_int")

  expect_s3_class(preds, "tbl_df")
  expect_named(preds, c(".pred_lower", ".pred_upper"))
  expect_true(all(preds$.pred_lower <= preds$.pred_upper))
})
```

--------------------------------------------------------------------------------

## Common Issues and Solutions

### Issue: Wrong Column Names

**Problem:**

```r
# Engine returns data.frame with wrong names
predict(...)
#>   lower  upper
#> 1  1.0    2.0
```

**Solution:**

```r
post = function(results, object) {
  tibble::tibble(
    .pred_lower = results$lower,
    .pred_upper = results$upper
  )
}
```

### Issue: Wrong Data Type

**Problem:**

```r
# Predictions are character, need factor
predict(...)
#>   class
#> 1 "A"
```

**Solution:**

```r
post = function(results, object) {
  tibble::tibble(
    .pred_class = factor(results$class, levels = object$lvl)
  )
}
```

### Issue: Matrix Instead of Tibble

**Problem:**

```r
# Engine returns matrix
predict(...)
#>      A    B
#> [1,] 0.8  0.2
```

**Solution:**

```r
post = function(results, object) {
  results <- as.data.frame(results)
  names(results) <- paste0(".pred_", names(results))
  tibble::as_tibble(results)
}
```

### Issue: Inconsistent Dimensions

**Problem:** Predictions don't match `new_data` rows.

**Solution:** Check in `post`:

```r
post = function(results, object) {
  if (length(results) != nrow(new_data)) {
    rlang::abort("Prediction length doesn't match data rows")
  }
  tibble::tibble(.pred = results)
}
```

--------------------------------------------------------------------------------

## Summary

**Key principles:**

1. **Each type has specific column names** - Follow conventions strictly
2. **Use `post` for format conversion** - Transform engine output to standard
   format
3. **Register each type separately** - Use `set_pred()` for each type
4. **Not all types for all engines** - Only register what the engine supports
5. **Test output format** - Verify column names, types, and dimensions
6. **Mode determines available types** - Regression, classification, censored
   regression, quantile regression have different types

**Column naming quick reference:**

- Numeric: `.pred`

- Class: `.pred_class`

- Probabilities: `.pred_{class_name}`

- Intervals: `.pred_lower`, `.pred_upper`

- Time: `.pred_time`

- Survival: `.pred` (list column with `.eval_time`, `.pred_survival`)

- Hazard: `.pred_hazard`

- Linear predictor: `.pred_linear_pred`

- Quantile: `.pred`, `.quantile`
