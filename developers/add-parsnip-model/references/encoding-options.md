# Encoding Options in Parsnip

This guide covers the three interface types (formula, matrix, xy) that control how data is passed from parsnip to modeling engines.

---

## Overview

**Encoding** determines how parsnip translates the user's data into the format the engine expects.

Parsnip supports three interface types:

1. **`"formula"`** - Traditional R formula interface
2. **`"matrix"`** - Numeric matrix for predictors
3. **`"xy"`** - Separate predictor and outcome objects

The choice depends on what the underlying engine function expects.

---

## Formula Interface

### When to Use

Use formula interface when the engine function expects:
```r
engine_function(formula, data, ...)
```

**Common examples:**

- `lm()`, `glm()` - Base R modeling

- Most traditional R modeling functions

- Functions that handle factor encoding automatically

### How It Works

**User provides:**
```r
spec <- linear_reg() |> set_engine("lm")
fit(spec, mpg ~ hp + wt, data = mtcars)
```

**Parsnip passes to engine:**
```r
lm(formula = mpg ~ hp + wt, data = mtcars)
```

No translation needed - formula and data pass through directly.

### Registration

```r
set_fit(
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

**Key fields:**

- `interface = "formula"` - Use formula interface

- `protect = c("formula", "data")` - Don't let user override these arguments

### Formula Interface Characteristics

**Advantages:**

- Simple and familiar to R users

- Engine handles factor encoding

- Engine handles interaction terms

- Engine handles missing data

**Limitations:**

- Some engines don't support formulas

- Can be slower for large datasets

- Less control over preprocessing

**What parsnip does:**

- Passes formula through unchanged

- Passes data frame through unchanged

- No matrix conversion

- No factor preprocessing

---

## Matrix Interface

### When to Use

Use matrix interface when the engine function expects:
```r
engine_function(x, y, ...)
```

Where `x` is a numeric matrix and `y` is a vector.

**Common examples:**

- `glmnet()` - Elastic net regression

- `xgboost::xgb.train()` - Gradient boosting

- Many machine learning libraries (they expect numeric matrices)

### How It Works

**User provides:**
```r
spec <- linear_reg(penalty = 0.1) |> set_engine("glmnet")
fit(spec, mpg ~ hp + wt, data = mtcars)
```

**Parsnip converts and passes to engine:**
```r
x <- as.matrix(mtcars[, c("hp", "wt")])
y <- mtcars$mpg
glmnet(x = x, y = y, lambda = 0.1)
```

Parsnip automatically:

- Extracts predictors from formula

- Converts to numeric matrix

- Extracts outcome variable

- Handles factor encoding (dummy variables)

### Registration

```r
set_fit(
  model = "linear_reg",
  eng = "glmnet",
  mode = "regression",
  value = list(
    interface = "matrix",
    protect = c("x", "y"),
    func = c(pkg = "glmnet", fun = "glmnet"),
    defaults = list(family = "gaussian")
  )
)
```

**Key fields:**

- `interface = "matrix"` - Convert formula to matrices

- `protect = c("x", "y")` - Reserve these argument names

### Matrix Interface Characteristics

**Advantages:**

- Works with engines requiring numeric input

- Efficient for large datasets

- Explicit about what gets passed

**Automatic conversions by parsnip:**

- Factors → Dummy variables (one-hot encoding)

- Character → Factor → Dummy variables

- Formula terms → Column names

- Interactions expanded automatically

**Limitations:**

- Loses factor ordering information

- One-hot encoding can create many columns

- Engine must accept matrix input

### Factor Encoding Example

```r
# Data with factor
data <- data.frame(
  y = 1:6,
  x1 = 1:6,
  x2 = factor(c("A", "B", "C", "A", "B", "C"))
)

# User provides formula
fit(spec, y ~ x1 + x2, data = data)

# Parsnip converts to matrix:
#   x1  x2B  x2C
# 1  1    0    0
# 2  2    1    0
# 3  3    0    1
# 4  4    0    0
# 5  5    1    0
# 6  6    0    1
```

First factor level ("A") becomes baseline (all zeros in dummy columns).

---

## XY Interface

### When to Use

Use XY interface when:

- User provides `fit_xy()` instead of `fit()`

- Engine expects separate x and y arguments

- Similar to matrix but different API

**Common examples:**

- `knn()` functions expecting `train` and `cl` arguments

- Some older R functions

- Custom functions with specific argument names

### How It Works

**User provides:**
```r
spec <- nearest_neighbor() |> set_engine("kknn")
fit_xy(spec, x = mtcars[, -1], y = mtcars$mpg)
```

**Parsnip passes to engine:**
```r
# Arguments translated based on registration
kknn(train = x, cl = y, ...)
```

### Registration

```r
set_fit(
  model = "nearest_neighbor",
  eng = "kknn",
  mode = "regression",
  value = list(
    interface = "xy",
    protect = c("train", "cl"),
    func = c(pkg = "kknn", fun = "train.kknn"),
    defaults = list()
  )
)

# Or using formula interface with set_encoding()
set_encoding(
  model = "nearest_neighbor",
  eng = "kknn",
  mode = "regression",
  options = list(
    predictor_indicators = "traditional",
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)
```

### XY Interface Characteristics

**Differences from matrix:**

- May use different argument names (not always `x` and `y`)

- User explicitly provides separated data

- No formula parsing needed

**When user uses formula with XY engine:**
```r
# User still uses formula
fit(spec, mpg ~ hp + wt, data = mtcars)

# Parsnip converts to XY internally
x <- model.matrix(~ hp + wt - 1, data = mtcars)
y <- mtcars$mpg
```

---

## Using `set_encoding()`

`set_encoding()` provides fine-grained control over how formulas are converted.

### Purpose

Control specific aspects of formula encoding:

- Indicator variables for factors

- Intercept handling

- Missing data handling

### Common Options

**`predictor_indicators`:**

- `"traditional"` - Standard R dummy coding (n-1 dummies)

- `"one_hot"` - Full one-hot encoding (n dummies)

- `"none"` - Keep factors as-is

**`compute_intercept`:**

- `TRUE` - Add intercept column to matrix

- `FALSE` - No intercept column

**`remove_intercept`:**

- `TRUE` - Remove intercept from formula if present

- `FALSE` - Keep intercept in formula

### Example Usage

```r
set_encoding(
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

**What this does:**

- Use traditional dummy coding (n-1 levels)

- Don't add intercept column to matrix

- Remove intercept from formula before conversion

### Why Control Encoding?

**Some engines handle intercepts internally:**
```r
# glmnet adds its own intercept
# Don't want intercept in x matrix
set_encoding(
  ...,
  options = list(
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)
```

**Some engines need one-hot encoding:**
```r
# xgboost works better with full one-hot
set_encoding(
  ...,
  options = list(
    predictor_indicators = "one_hot"
  )
)
```

---

## Choosing the Right Interface

### Decision Tree

**Does the engine function take a formula?**

- Yes → Use `interface = "formula"`

- No → Continue

**Does the engine expect numeric matrices?**

- Yes, as `x` and `y` → Use `interface = "matrix"`

- Yes, with different names → Use `interface = "xy"` or `interface = "matrix"` with custom encoding

### By Engine Type

**Traditional R functions:**
```r
lm(), glm(), nls()
→ interface = "formula"
```

**Modern ML libraries:**
```r
glmnet(), ranger(), xgboost()
→ interface = "matrix"
```

**Older ML functions:**
```r
knn(), some classification functions
→ interface = "xy"
```

---

## Interface Compatibility

### User Can Use Either API

Regardless of engine interface, users can use either:

**Formula API:**
```r
fit(spec, y ~ x1 + x2, data = data)
```

**XY API:**
```r
fit_xy(spec, x = data[, c("x1", "x2")], y = data$y)
```

**Parsnip handles conversion:**

- Formula → Matrix/XY (for matrix/xy engines)

- XY → Internal processing (for all engines)

### Formula with Matrix Engine

```r
# User provides formula
spec <- linear_reg() |> set_engine("glmnet")  # matrix interface
fit(spec, mpg ~ hp + wt, data = mtcars)

# Parsnip converts:
# 1. Extracts predictors: mtcars[, c("hp", "wt")]
# 2. Converts to matrix: as.matrix(...)
# 3. Extracts outcome: mtcars$mpg
# 4. Calls: glmnet(x = matrix, y = outcome)
```

### XY with Formula Engine

```r
# User provides XY
spec <- linear_reg() |> set_engine("lm")  # formula interface
fit_xy(spec, x = mtcars[, c("hp", "wt")], y = mtcars$mpg)

# Parsnip converts:
# 1. Creates formula: y ~ hp + wt
# 2. Creates data frame: cbind(y, x)
# 3. Calls: lm(formula = y ~ hp + wt, data = df)
```

---

## Prediction Implications

The interface choice affects prediction too.

### Formula Interface Predictions

```r
# Fit with formula interface
spec <- linear_reg() |> set_engine("lm")
fit <- fit(spec, mpg ~ hp + wt, data = mtcars)

# Predictions need data frame with same columns
new_data <- data.frame(hp = 100, wt = 3.0)
predict(fit, new_data)
```

Engine's `predict()` method gets data frame.

### Matrix Interface Predictions

```r
# Fit with matrix interface
spec <- linear_reg() |> set_engine("glmnet")
fit <- fit(spec, mpg ~ hp + wt, data = mtcars)

# new_data is converted to matrix automatically
new_data <- data.frame(hp = 100, wt = 3.0)
predict(fit, new_data)

# Behind the scenes:
# new_matrix <- as.matrix(new_data[, c("hp", "wt")])
# predict(fit$fit, newx = new_matrix)
```

Parsnip converts `new_data` to matrix for prediction.

### Factor Consistency

**Important:** Factor levels must match training data.

```r
# Training data
train <- data.frame(
  y = 1:6,
  x = factor(c("A", "B", "C", "A", "B", "C"))
)

fit <- fit(spec, y ~ x, data = train)

# New data must have same levels
new_data <- data.frame(x = factor("B", levels = c("A", "B", "C")))
predict(fit, new_data)  # ✓ Works

# Missing levels will error
new_data <- data.frame(x = factor("B"))
predict(fit, new_data)  # ✗ Error
```

---

## Testing Interface Behavior

### Test Formula and XY Equivalence

```r
test_that("formula and xy interfaces give same results", {
  # Formula interface
  spec <- linear_reg() |> set_engine("lm")
  fit_formula <- fit(spec, mpg ~ hp + wt, data = mtcars)
  pred_formula <- predict(fit_formula, mtcars[1:5, ])

  # XY interface
  fit_xy <- fit_xy(spec, x = mtcars[, c("hp", "wt")], y = mtcars$mpg)
  pred_xy <- predict(fit_xy, mtcars[1:5, ])

  # Should be equivalent
  expect_equal(pred_formula, pred_xy, tolerance = 1e-10)
})
```

### Test Factor Encoding

```r
test_that("factors are encoded correctly", {
  data <- data.frame(
    y = 1:6,
    x = factor(c("A", "B", "C", "A", "B", "C"))
  )

  spec <- linear_reg() |> set_engine("glmnet")  # matrix interface
  fit <- fit(spec, y ~ x, data = data)

  # Should have 2 dummy columns (not 3)
  # glmnet uses n-1 encoding by default
  expect_equal(ncol(fit$fit$beta), 1)  # Just the x matrix
})
```

### Test Interface Selection

```r
test_that("correct interface is used", {
  # Formula engine should use formula
  spec_lm <- linear_reg() |> set_engine("lm")
  fit_lm <- fit(spec_lm, mpg ~ hp, data = mtcars)
  expect_s3_class(fit_lm$fit, "lm")

  # Matrix engine should work too
  spec_glmnet <- linear_reg() |> set_engine("glmnet")
  fit_glmnet <- fit(spec_glmnet, mpg ~ hp, data = mtcars)
  expect_s3_class(fit_glmnet$fit, "glmnet")
})
```

---

## Common Patterns

### Pattern 1: Simple Formula Interface

```r
set_fit(
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

Direct pass-through, no conversion.

### Pattern 2: Matrix Interface with Default Encoding

```r
set_fit(
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
```

Parsnip handles formula → matrix conversion automatically.

### Pattern 3: Matrix Interface with Custom Encoding

```r
set_fit(
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

set_encoding(
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

Custom encoding behavior for specific needs.

### Pattern 4: XY Interface with Custom Names

```r
set_fit(
  model = "nearest_neighbor",
  eng = "kknn",
  mode = "regression",
  value = list(
    interface = "xy",
    protect = c("formula", "train"),  # Custom argument names
    func = c(pkg = "kknn", fun = "train.kknn"),
    defaults = list()
  )
)
```

For engines with non-standard argument names.

---

## Interface Troubleshooting

### Issue: Factor Levels Don't Match

**Problem:** Predictions fail because new data has different levels.

**Solution:** Ensure new data has all training levels:
```r
new_data$x <- factor(new_data$x, levels = levels(train$x))
```

### Issue: Engine Doesn't Accept Matrix

**Problem:** Using `interface = "matrix"` but engine needs formula.

**Solution:** Change to `interface = "formula"`:
```r
set_fit(..., value = list(interface = "formula", ...))
```

### Issue: Too Many Dummy Columns

**Problem:** One-hot encoding creates too many columns.

**Solution:** Use traditional encoding:
```r
set_encoding(
  ...,
  options = list(predictor_indicators = "traditional")
)
```

### Issue: Intercept Handled Twice

**Problem:** Both parsnip and engine add intercept.

**Solution:** Tell parsnip not to add intercept:
```r
set_encoding(
  ...,
  options = list(
    compute_intercept = FALSE,
    remove_intercept = TRUE
  )
)
```

---

## Summary

**Three interfaces:**

1. **Formula** (`interface = "formula"`)

   - Engine expects: `func(formula, data, ...)`

   - Use for: Traditional R functions

   - Conversion: None (pass-through)

2. **Matrix** (`interface = "matrix"`)

   - Engine expects: `func(x, y, ...)`

   - Use for: Modern ML libraries

   - Conversion: Formula → numeric matrix + vector

3. **XY** (`interface = "xy"`)

   - Engine expects: Custom x/y argument names

   - Use for: Functions with non-standard names

   - Conversion: Similar to matrix

**Key concepts:**

- Interface determines how parsnip passes data to engine

- Users can use either `fit()` or `fit_xy()` regardless of interface

- Parsnip handles conversions automatically

- Use `set_encoding()` for fine-tuned control

- Factor encoding is automatic for matrix interface

- Factor levels must match between training and prediction

**Quick selection guide:**

| Engine Type | Interface | Example |
|------------|-----------|---------|
| Base R stats | formula | lm, glm |
| Modern ML | matrix | glmnet, xgboost |
| Older ML | xy | knn functions |
