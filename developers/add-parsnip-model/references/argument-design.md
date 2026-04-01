# Argument Design for Parsnip Models

This guide covers how to design main arguments for parsnip models that work consistently across different computational engines.

---

## Overview

Main arguments are standardized parameters that work across multiple engines. Good argument design is crucial for a consistent user experience and tune package integration.

**Main arguments should:**

- Use consistent names across engines

- Map to engine-specific parameters

- Support tuning workflows

- Follow tidymodels conventions

- Be commonly adjusted by users

---

## Main Arguments vs Engine Arguments

### Main Arguments

**Characteristics:**

- Standardized across engines

- Defined in model constructor

- Translated to engine-specific names

- Integrated with dials package

- Users specify in constructor or with `set_args()`

**Example:**
```r
linear_reg(penalty = 0.1, mixture = 0.5)
#          ^^^^^^^ main arguments
```

### Engine Arguments

**Characteristics:**

- Engine-specific

- Passed via `set_engine()`

- Not standardized

- Go directly to engine function

- Use engine's native names

**Example:**
```r
linear_reg() |>
  set_engine("glmnet", nlambda = 100, standardize = TRUE)
#                      ^^^^^^^^^^^ engine arguments
```

### Decision Criteria

**Make it a main argument if:**

- ✓ Multiple engines support it

- ✓ Users frequently tune it

- ✓ It's conceptually similar across engines

- ✓ It benefits from standardization

**Keep it as engine argument if:**

- ✓ Only one engine uses it

- ✓ Rarely adjusted

- ✓ Engine-specific behavior

- ✓ No clear analog in other engines

---

## Naming Conventions

### Use Tidymodels Standard Names

Follow established parsnip conventions:

**Regularization:**

- `penalty` - Not `lambda`, `reg_param`, or `C`

- `mixture` - Not `alpha`, `l1_ratio`, or `elastic_net_param`

**Tree models:**

- `trees` - Not `n_estimators`, `num_boost_round`, or `nrounds`

- `tree_depth` - Not `max_depth`

- `min_n` - Not `min_samples_split` or `min_child_weight`

- `mtry` - Not `max_features` or `colsample_bytree`

- `learn_rate` - Not `eta`, `shrinkage`, or `learning_rate`

**Neural networks:**

- `hidden_units` - Not `units` or `neurons`

- `epochs` - Not `iterations` or `max_iter`

- `activation` - Standard name

**Sampling:**

- `sample_size` - Not `subsample` or `sample_frac`

### Why Standardize?

**Consistency:**
```r
# Same name works across engines
boost_tree(learn_rate = 0.1) |> set_engine("xgboost")  # eta
boost_tree(learn_rate = 0.1) |> set_engine("C5.0")     # CF
boost_tree(learn_rate = 0.1) |> set_engine("spark")    # stepSize
```

**Tuning integration:**
```r
# tune knows about learn_rate
boost_tree(learn_rate = tune()) |>
  set_engine("xgboost")

# dials provides sensible ranges
dials::learn_rate()
#> Learning Rate (quantitative)
#> Transformer: log-10 [1e-10, 1]
```

---

## Argument Types

### Numeric Arguments

Most common type for tuning parameters:

```r
linear_reg <- function(penalty = NULL, mixture = NULL, ...) {
  # penalty: non-negative number
  # mixture: number between 0 and 1
}
```

**Considerations:**

- Range constraints (e.g., penalty ≥ 0)

- Scale (linear, log-scale)

- Typical values

- NULL means "use engine default"

**Examples:**

- `penalty` - Amount of regularization (0 to ∞)

- `mixture` - L1/L2 mix (0 to 1)

- `learn_rate` - Learning rate (0 to 1, often log-scale)

- `cost_complexity` - Tree pruning parameter (0 to ∞)

### Integer Arguments

For count-based parameters:

```r
rand_forest <- function(trees = NULL, min_n = NULL, ...) {
  # trees: positive integer
  # min_n: positive integer
}
```

**Examples:**

- `trees` - Number of trees

- `min_n` - Minimum observations in node

- `tree_depth` - Maximum tree depth

- `neighbors` - Number of neighbors

- `hidden_units` - Nodes in layer

### Categorical Arguments

For discrete choices:

```r
nearest_neighbor <- function(neighbors = NULL, weight_func = NULL, ...) {
  # weight_func: character ("rectangular", "triangular", etc.)
}
```

**Examples:**

- `weight_func` - Distance weighting function

- `activation` - Activation function name

- `tree_method` - Algorithm variant

---

## Designing for Multiple Engines

### 1. Survey Engine Implementations

Check how different engines handle the concept:

**Example: Penalty parameter**

- `glmnet`: `lambda` parameter

- `keras`: L2 regularization coefficient

- `spark`: `reg_param` in linear models

- `LiblineaR`: `cost` parameter (inverse)

**Commonality:** All control regularization strength.

**Design:** Use `penalty` as standardized name.

### 2. Choose Common Denominator

Pick a design that works for all engines:

**Example: Tree depth**

- `rpart`: `maxdepth` (unlimited if omitted)

- `ranger`: `max.depth` (unlimited if NULL)

- `xgboost`: `max_depth` (default 6)

- `C5.0`: Doesn't directly control depth

**Design:**

- Name: `tree_depth`

- NULL default (let engine choose)

- Note in docs that some engines don't support it

### 3. Handle Engine Differences

Some engines may need special translation:

**Example: Mixture parameter**

- `glmnet`: `alpha` (0 = ridge, 1 = lasso)

- `spark`: `elasticNetParam` (same scale)

- Other engines: May not support elastic net

**Translation:**
```r
set_model_arg(
  model = "linear_reg",
  eng = "glmnet",
  parsnip = "mixture",   # User provides
  original = "alpha",    # glmnet expects
  func = list(pkg = "dials", fun = "mixture"),
  has_submodel = FALSE
)
```

### 4. Document Engine Support

Clearly state which engines support which arguments:

```r
#' @param trees Number of trees. Used by `ranger`, `randomForest`, and
#'   `xgboost` engines. Not used by `conditional_inference_tree` engine.
```

---

## Default Values

### Use NULL Defaults

Recommended pattern:

```r
linear_reg <- function(penalty = NULL, mixture = NULL, ...) {
  # NULL means "use engine default"
}
```

**Advantages:**

- Engine can use its own defaults

- Clear when user specified vs default

- More flexible across engines

- Required for tune::tune() to work

### When to Use Specific Defaults

Only set specific defaults when:

- All engines need the same value

- NULL would be ambiguous

- Users almost always want that value

**Example where specific default makes sense:**
```r
mlp <- function(hidden_units = NULL,
                activation = "relu",  # Good default across engines
                ...) {
  # Most engines default to sigmoid/tanh
  # But relu is usually better - set as default
}
```

---

## Integration with Dials

### Link to Parameter Objects

Each main argument should link to a dials parameter:

```r
set_model_arg(
  model = "linear_reg",
  eng = "glmnet",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),  # Links to dials
  has_submodel = TRUE
)
```

**Why?**

- Provides default tuning ranges

- Enables grid functions

- Documents parameter behavior

### Parameter Properties in Dials

The dials parameter object specifies:

```r
dials::penalty()
#> Amount of Regularization (quantitative)
#> Transformer: log-10 [1e-10, 1]
#> Range (transformed scale): [-10, 0]
```

**Properties:**

- **Range:** Default bounds for tuning

- **Transform:** Log-scale, identity, logit, etc.

- **Type:** Numeric, integer, categorical

### Create Dials Parameters

If standard parameter doesn't exist, create one:

```r
# In your package or in dials PR
my_custom_param <- function(range = c(0, 10), trans = NULL) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_custom_param = "Custom Parameter"),
    finalize = NULL
  )
}
```

---

## Submodel Optimization

### What are Submodels?

Some engines can generate predictions for multiple parameter values from a single fit.

**Example: glmnet**
```r
# Fits with multiple lambda values simultaneously
fit <- glmnet(x, y, lambda = c(0.1, 0.01, 0.001))

# Can predict for any lambda value
predict(fit, newx, s = 0.05)  # Interpolates
```

### Indicating Submodel Support

```r
set_model_arg(
  model = "linear_reg",
  eng = "glmnet",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = TRUE  # Enables optimization
)
```

**When TRUE:**

- Tune package can optimize grid search

- Fit once, predict multiple parameter values

- Much faster for large grids

**When FALSE:**

- Must refit for each parameter value

- Use when engine doesn't support submodels

---

## Argument Constraints

### Specify Valid Ranges

Document constraints clearly:

```r
#' @param penalty A non-negative number for the amount of regularization.
#'   For engines that support it, `penalty = 0` means no regularization.
#'   Default is NULL (uses engine's default, often automatic selection).
```

**Common constraints:**

- `penalty` ≥ 0

- `mixture` ∈ [0, 1]

- `trees` > 0 (integer)

- `learn_rate` ∈ (0, 1)

### Validation Strategy

**Light validation in constructor:**
```r
linear_reg <- function(penalty = NULL, ...) {
  if (!is.null(penalty) && penalty < 0) {
    rlang::abort("`penalty` must be non-negative")
  }
  # Continue...
}
```

**Most validation at fit time:**
```r
# Parsnip checks at fit time:
# - Arguments are correct types
# - Values are in valid ranges
# - Required arguments are present
```

---

## Argument Translation Examples

### Example 1: Simple One-to-One

```r
# parsnip name: penalty
# glmnet name: lambda

set_model_arg(
  model = "linear_reg",
  eng = "glmnet",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = TRUE
)
```

### Example 2: Same Name, Different Engines

```r
# trees → nrounds (xgboost)
set_model_arg(
  model = "boost_tree",
  eng = "xgboost",
  parsnip = "trees",
  original = "nrounds",
  func = list(pkg = "dials", fun = "trees"),
  has_submodel = FALSE
)

# trees → ntree (randomForest)
set_model_arg(
  model = "rand_forest",
  eng = "randomForest",
  parsnip = "trees",
  original = "ntree",
  func = list(pkg = "dials", fun = "trees"),
  has_submodel = FALSE
)
```

### Example 3: Transformation Needed

Some engines use inverse or different scales:

```r
# LiblineaR uses cost = 1/penalty
# Handle in set_fit() defaults or pre function
set_fit(
  model = "linear_reg",
  eng = "LiblineaR",
  mode = "regression",
  value = list(
    interface = "matrix",
    protect = c("x", "y"),
    func = c(pkg = "LiblineaR", fun = "LiblineaR"),
    defaults = list(
      cost = rlang::expr(1 / penalty)  # Inverse transformation
    )
  )
)
```

---

## Mode-Specific Arguments

Some arguments may only apply to certain modes:

```r
boost_tree <- function(mode = "unknown",
                       trees = NULL,           # Both modes
                       tree_depth = NULL,      # Both modes
                       min_n = NULL,           # Both modes
                       loss_reduction = NULL,  # Both modes
                       sample_size = NULL,     # Both modes
                       mtry = NULL,            # Both modes
                       learn_rate = NULL,      # Both modes
                       stop_iter = NULL) {     # Both modes
  # All arguments work for both regression and classification
}
```

Most tree arguments work for both modes. Mode-specific behavior handled in registration, not constructor.

**If truly mode-specific:**

- Document clearly

- May need separate constructors for different modes

- Rare in practice

---

## Testing Argument Design

### Test Argument Acceptance

```r
test_that("constructor accepts arguments", {
  spec <- my_model(penalty = 0.1, mixture = 0.5)

  expect_true(rlang::is_quosure(spec$args$penalty))
  expect_equal(rlang::eval_tidy(spec$args$penalty), 0.1)

  expect_true(rlang::is_quosure(spec$args$mixture))
  expect_equal(rlang::eval_tidy(spec$args$mixture), 0.5)
})
```

### Test Argument Translation

```r
test_that("arguments are translated correctly", {
  spec <- my_model(penalty = 0.1) |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  # Check that glmnet received lambda = 0.1
  expect_equal(fit$fit$lambda, 0.1)
})
```

### Test with tune()

```r
test_that("arguments work with tune", {
  spec <- my_model(penalty = tune(), mixture = tune()) |>
    set_engine("glmnet")

  expect_true(rlang::is_quosure(spec$args$penalty))

  # Check that tune placeholder is preserved
  penalty_expr <- rlang::eval_tidy(spec$args$penalty)
  expect_s3_class(penalty_expr, "tune")
})
```

### Test NULL Handling

```r
test_that("NULL arguments use engine defaults", {
  spec <- my_model(penalty = NULL) |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  # glmnet should have selected its own lambda sequence
  expect_true(length(fit$fit$lambda) > 1)
})
```

---

## Documentation Best Practices

### Parameter Documentation

```r
#' @param penalty A non-negative number for the total amount of regularization.
#'
#'   **Engine details:**
#'   - **glmnet**: Controls the `lambda` parameter. The model fits a path of
#'     solutions, so you can also use `penalty = NULL` to fit multiple values.
#'   - **keras**: Controls the L2 penalty. Only single values supported.
#'   - **spark**: Controls the `regParam` parameter.
#'
#'   For tuning, use `penalty = tune()` and [dials::penalty()] provides
#'   reasonable default ranges.
```

### Engine Support Table

```markdown
## Main Arguments

| Argument | glmnet | keras | spark |
|----------|--------|-------|-------|
| penalty  | ✓      | ✓     | ✓     |
| mixture  | ✓      | ✗     | ✓     |
```

### Examples Showing Arguments

```r
#' @examples
#' # Using main arguments
#' linear_reg(penalty = 0.1, mixture = 0.5) |>
#'   set_engine("glmnet") |>
#'   fit(mpg ~ ., data = mtcars)
#'
#' # Tuning main arguments
#' library(tune)
#' linear_reg(penalty = tune(), mixture = tune()) |>
#'   set_engine("glmnet")
```

---

## Common Patterns

### Pattern 1: Regularization Parameters

```r
# Penalty and mixture are standard
model_fn <- function(penalty = NULL, mixture = NULL, ...) {
  args <- list(
    penalty = rlang::enquo(penalty),
    mixture = rlang::enquo(mixture)
  )
  # ...
}

# Translation
set_model_arg(..., parsnip = "penalty", original = "lambda", ...)
set_model_arg(..., parsnip = "mixture", original = "alpha", ...)
```

### Pattern 2: Tree Parameters

```r
# Common tree arguments
tree_model <- function(trees = NULL,
                       tree_depth = NULL,
                       min_n = NULL,
                       ...) {
  args <- list(
    trees = rlang::enquo(trees),
    tree_depth = rlang::enquo(tree_depth),
    min_n = rlang::enquo(min_n)
  )
  # ...
}
```

### Pattern 3: Ensemble Parameters

```r
# Random forest style
ensemble_model <- function(trees = NULL, mtry = NULL, ...) {
  args <- list(
    trees = rlang::enquo(trees),
    mtry = rlang::enquo(mtry)
  )
  # ...
}
```

---

## Summary

**Key principles for argument design:**

1. **Standardize names** - Use tidymodels conventions
2. **NULL defaults** - Let engines use their defaults
3. **Link to dials** - Enable tuning workflows
4. **Document clearly** - Explain engine differences
5. **Common denominator** - Design for all engines
6. **Use rlang::enquo()** - Support tune() placeholders

**Good main arguments are:**

- Conceptually similar across engines

- Frequently tuned by users

- Well-integrated with tune/dials

- Clearly documented

- Consistently named

**The main arguments define your model's API - invest time in getting them right.**
