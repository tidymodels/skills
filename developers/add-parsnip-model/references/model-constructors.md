# Model Constructor Design

This guide covers how to design and implement model constructor functions for parsnip (like `linear_reg()`, `boost_tree()`).

---

## Overview

A model constructor is the user-facing function that creates a model specification object. It defines the API users will interact with.

**Key responsibilities:**

- Accept main arguments

- Set default engine and mode

- Create model_spec object

- Validate inputs

---

## Constructor Function Signature

### Basic Template

```r
my_model <- function(mode = "regression",
                     penalty = NULL,
                     mixture = NULL,
                     engine = "default_engine") {

  args <- list(
    penalty = rlang::enquo(penalty),
    mixture = rlang::enquo(mixture)
  )

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
```

### Required Elements

**Function name:**

- Descriptive of algorithm family: `linear_reg()`, `rand_forest()`, `boost_tree()`

- Use snake_case

- Avoid package-specific names (not `glmnet_model()` or `xgboost_model()`)

**Parameters:**

- `mode` - Prediction mode (regression, classification, etc.)

- Main arguments - Tuning parameters

- `engine` - Computational backend (with sensible default)

---

## Mode Parameter

### Single-Mode Models

For models that only support one mode, set it automatically:

```r
linear_reg <- function(penalty = NULL,
                       mixture = NULL,
                       engine = "lm") {

  args <- list(
    penalty = rlang::enquo(penalty),
    mixture = rlang::enquo(mixture)
  )

  new_model_spec(
    "linear_reg",
    args = args,
    eng_args = NULL,
    mode = "regression",  # Fixed mode
    user_specified_mode = FALSE,
    method = NULL,
    engine = engine,
    user_specified_engine = !missing(engine)
  )
}
```

**No mode parameter** - Users can't change it.

### Multi-Mode Models

For models supporting multiple modes, include `mode` parameter:

```r
boost_tree <- function(mode = "unknown",
                       trees = NULL,
                       tree_depth = NULL,
                       learn_rate = NULL,
                       engine = "xgboost") {

  args <- list(
    trees = rlang::enquo(trees),
    tree_depth = rlang::enquo(tree_depth),
    learn_rate = rlang::enquo(learn_rate)
  )

  new_model_spec(
    "boost_tree",
    args = args,
    eng_args = NULL,
    mode = mode,  # User must set
    user_specified_mode = !missing(mode),
    method = NULL,
    engine = engine,
    user_specified_engine = !missing(engine)
  )
}
```

**Use `"unknown"` as default** - Forces users to be explicit.

---

## Main Arguments

### What Makes a Main Argument?

**Include as main argument when:**

- Common across multiple engines

- Important tuning parameter

- Worth standardizing for tune package

- Users will frequently adjust

**Keep as engine argument when:**

- Engine-specific behavior

- Rarely adjusted

- No equivalent in other engines

### Naming Main Arguments

Follow tidymodels conventions:

**Good names (standardized):**

- `penalty` - Regularization amount (not `lambda` or `reg_param`)

- `mixture` - L1/L2 mix (not `alpha` or `l1_ratio`)

- `trees` - Number of trees (not `n_estimators` or `num_boost_round`)

- `tree_depth` - Max tree depth (not `max_depth`)

- `learn_rate` - Learning rate (not `eta` or `shrinkage`)

- `mtry` - Predictors per split (not `max_features`)

**Avoid engine-specific names:**

- Don't use `lambda` - Use `penalty` instead

- Don't use `alpha` - Use `mixture` instead

- Don't use `nrounds` - Use `trees` instead

### Using rlang::enquo()

Capture arguments with `rlang::enquo()` to support tidy evaluation:

```r
args <- list(
  penalty = rlang::enquo(penalty),
  trees = rlang::enquo(trees),
  mtry = rlang::enquo(mtry)
)
```

**Why?**

- Enables `tune()` placeholders

- Supports delayed evaluation

- Required by parsnip infrastructure

### Setting Defaults

**NULL defaults are recommended:**
```r
linear_reg <- function(penalty = NULL, mixture = NULL, ...)
```

**Why NULL?**

- Lets engine use its own defaults

- Clear when user specified vs default

- More flexible across engines

**When to use specific defaults:**

- Only if all engines need the same value

- When NULL would be ambiguous

---

## Engine Parameter

### Choosing Default Engine

Pick a default engine based on:

- Availability (base R > CRAN > GitHub)

- Stability (mature packages preferred)

- Performance (for typical use cases)

- Simplicity (fewer dependencies better)

**Examples:**
```r
linear_reg(engine = "lm")      # base R, always available
boost_tree(engine = "xgboost")  # Popular, well-maintained
rand_forest(engine = "ranger")  # Fast, reliable
```

### Track User Specification

Always track if user specified engine:

```r
new_model_spec(
  ...,
  engine = engine,
  user_specified_engine = !missing(engine)
)
```

**Used for:**

- Error messages

- Default behavior

- Package loading

---

## Using new_model_spec()

### Core Constructor Helper

`new_model_spec()` creates the S3 object:

```r
new_model_spec(
  cls = "my_model",           # Model class name
  args = args,                # Main arguments (enquo'd)
  eng_args = NULL,            # Engine arguments (initially NULL)
  mode = mode,                # Prediction mode
  user_specified_mode = !missing(mode),
  method = NULL,              # Fitting method (initially NULL)
  engine = engine,            # Computational engine
  user_specified_engine = !missing(engine)
)
```

### Fields Explained

**`cls`** - Character string for model type:

- Must match function name

- Used for class hierarchy

- Example: `"linear_reg"` for `linear_reg()` function

**`args`** - List of main arguments:

- Each element is output of `rlang::enquo()`

- Names match parameter names

- Can be NULL or tune() placeholders

**`eng_args`** - Engine-specific arguments:

- Initially NULL

- Populated by `set_engine()`

- User provides via `set_engine(..., arg = value)`

**`mode`** - Prediction mode:

- "regression", "classification", "censored regression", "quantile regression"

- Or "unknown" for multi-mode models without default

**`user_specified_mode`** - Boolean:

- TRUE if user provided mode parameter

- Use `!missing(mode)` to detect

**`method`** - Fitting method:

- Initially NULL

- Set internally by parsnip

- Don't modify in constructor

**`engine`** - Computational backend:

- String naming the engine (e.g., "lm", "glmnet", "xgboost")

- Should have sensible default

**`user_specified_engine`** - Boolean:

- TRUE if user provided engine parameter

- Use `!missing(engine)` to detect

---

## Return Value

### What Gets Returned

The constructor returns a `model_spec` object:

```r
spec <- linear_reg()
class(spec)
#> [1] "linear_reg"  "model_spec"
```

### Class Hierarchy

Classes are automatically created:

- Primary class: Model name (`"linear_reg"`)

- Parent class: `"model_spec"`

Created by `make_classes(cls)` internally.

### Object Structure

```r
spec <- linear_reg(penalty = 0.1)
str(spec)
#> List of 7
#>  $ args             : List of 2
#>   ..$ penalty: quosure
#>   ..$ mixture: quosure
#>  $ eng_args         : NULL
#>  $ mode             : chr "regression"
#>  $ user_specified_mode: logi FALSE
#>  $ method           : NULL
#>  $ engine           : chr "lm"
#>  $ user_specified_engine: logi FALSE
#>  - attr(*, "class")= chr [1:2] "linear_reg" "model_spec"
```

---

## Input Validation

### What to Validate

**In constructor, validate:**

- Mode is valid (if provided)

- Numeric arguments are numeric

- Logical arguments are logical

- Factors/characters when expected

**Don't validate in constructor:**

- Engine availability (checked at fit time)

- Argument compatibility (checked at fit time)

- Data compatibility (checked at fit time)

### Validation Examples

**Check mode validity:**
```r
my_model <- function(mode = "unknown", ...) {
  if (!mode %in% c("unknown", "regression", "classification")) {
    rlang::abort(
      "mode should be 'regression' or 'classification'"
    )
  }

  # Continue with new_model_spec()...
}
```

**Check argument types:**
```r
linear_reg <- function(penalty = NULL, ...) {
  if (!is.null(penalty) && !is.numeric(penalty)) {
    rlang::abort("penalty must be numeric")
  }

  # Continue with new_model_spec()...
}
```

**For tidymodels style, check at registration time instead:**
Most validation happens during registration and fitting, not in constructor.

---

## Documentation

### Roxygen2 Template

```r
#' Linear Regression
#'
#' `linear_reg()` defines a model that uses linear regression to predict
#' a numeric outcome from one or more predictors.
#'
#' @param mode A single character string for the type of model. The only
#'   possible value for this model is "regression".
#' @param penalty A non-negative number for the amount of regularization.
#'   Used by glmnet and keras engines.
#' @param mixture A number between 0 and 1 for the proportion of L1
#'   regularization. Used by glmnet and keras engines.
#' @param engine A character string specifying the computational engine.
#'   Possible values are "lm" (default), "glmnet", and "keras".
#'
#' @details
#' ## Engines
#'
#' This model can be fit using different computational engines. The
#' available engines are:
#'
#' - **lm** (default): Uses [stats::lm()]. No regularization.
#' - **glmnet**: Uses [glmnet::glmnet()]. Supports regularization via
#'   penalty and mixture.
#' - **keras**: Uses keras neural network. Supports regularization.
#'
#' ## Main arguments
#'
#' The main arguments for this model are:
#'
#' - `penalty`: Amount of regularization (lambda in glmnet)
#' - `mixture`: Mix of L1 (lasso) and L2 (ridge) regularization
#'
#' These arguments are only used by engines that support regularization.
#'
#' @return A `linear_reg` model specification.
#'
#' @seealso [set_engine()], [fit.model_spec()]
#'
#' @examples
#' # Basic linear regression
#' linear_reg() |>
#'   fit(mpg ~ ., data = mtcars)
#'
#' # With regularization
#' linear_reg(penalty = 0.1, mixture = 0.5) |>
#'   set_engine("glmnet") |>
#'   fit(mpg ~ ., data = mtcars)
#'
#' @export
linear_reg <- function(mode = "regression",
                       penalty = NULL,
                       mixture = NULL,
                       engine = "lm") {
  # Implementation
}
```

### Key Documentation Sections

**Description:** What the model does

**Parameters:** Each argument with type and purpose

**Details:** Engine-specific information

**Examples:** Show both simple and advanced usage

**Seealso:** Link to related functions

---

## Extension vs Source Patterns

### Extension Package Constructor

In your own package, export the constructor:

```r
#' @export
my_model <- function(mode = "regression", penalty = NULL, ...) {
  args <- list(penalty = rlang::enquo(penalty))

  parsnip::new_model_spec(  # Use namespace
    "my_model",
    args = args,
    eng_args = NULL,
    mode = mode,
    user_specified_mode = !missing(mode),
    method = NULL,
    engine = "default_engine",
    user_specified_engine = !missing(engine)
  )
}
```

**Register in .onLoad():**
```r
.onLoad <- function(libname, pkgname) {
  parsnip::set_new_model("my_model")
  parsnip::set_model_mode("my_model", "regression")
  # ... more registration
}
```

### Source Package Constructor

Contributing to parsnip directly:

```r
# R/my_model.R

#' @export
my_model <- function(mode = "regression", penalty = NULL, ...) {
  args <- list(penalty = rlang::enquo(penalty))

  new_model_spec(  # No namespace needed
    "my_model",
    args = args,
    eng_args = NULL,
    mode = mode,
    user_specified_mode = !missing(mode),
    method = NULL,
    engine = "default_engine",
    user_specified_engine = !missing(engine)
  )
}

# R/my_model_data.R contains registration
```

---

## Common Patterns

### Pattern 1: Single-Mode, Simple Arguments

```r
linear_reg <- function(penalty = NULL,
                       mixture = NULL,
                       engine = "lm") {
  args <- list(
    penalty = rlang::enquo(penalty),
    mixture = rlang::enquo(mixture)
  )

  new_model_spec(
    "linear_reg",
    args = args,
    eng_args = NULL,
    mode = "regression",  # Fixed
    user_specified_mode = FALSE,
    method = NULL,
    engine = engine,
    user_specified_engine = !missing(engine)
  )
}
```

### Pattern 2: Multi-Mode, Multiple Arguments

```r
boost_tree <- function(mode = "unknown",
                       trees = NULL,
                       tree_depth = NULL,
                       learn_rate = NULL,
                       mtry = NULL,
                       min_n = NULL,
                       loss_reduction = NULL,
                       sample_size = NULL,
                       stop_iter = NULL,
                       engine = "xgboost") {
  args <- list(
    trees = rlang::enquo(trees),
    tree_depth = rlang::enquo(tree_depth),
    learn_rate = rlang::enquo(learn_rate),
    mtry = rlang::enquo(mtry),
    min_n = rlang::enquo(min_n),
    loss_reduction = rlang::enquo(loss_reduction),
    sample_size = rlang::enquo(sample_size),
    stop_iter = rlang::enquo(stop_iter)
  )

  new_model_spec(
    "boost_tree",
    args = args,
    eng_args = NULL,
    mode = mode,  # User specifies
    user_specified_mode = !missing(mode),
    method = NULL,
    engine = engine,
    user_specified_engine = !missing(engine)
  )
}
```

### Pattern 3: With Input Validation

```r
my_model <- function(mode = "unknown",
                     penalty = NULL,
                     engine = "default") {

  # Validate mode
  if (!mode %in% c("unknown", "regression", "classification")) {
    rlang::abort("`mode` must be 'regression' or 'classification'")
  }

  # Validate penalty
  if (!is.null(penalty) && (!is.numeric(penalty) || penalty < 0)) {
    rlang::abort("`penalty` must be a non-negative number")
  }

  args <- list(penalty = rlang::enquo(penalty))

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
```

---

## Testing Constructors

Essential tests for model constructors:

```r
test_that("constructor creates correct object", {
  spec <- my_model()

  expect_s3_class(spec, "my_model")
  expect_s3_class(spec, "model_spec")
  expect_equal(spec$mode, "regression")
  expect_equal(spec$engine, "default_engine")
})

test_that("constructor accepts arguments", {
  spec <- my_model(penalty = 0.1)

  # Args are quosures
  expect_true(rlang::is_quosure(spec$args$penalty))

  # Can extract value
  penalty_val <- rlang::eval_tidy(spec$args$penalty)
  expect_equal(penalty_val, 0.1)
})

test_that("constructor tracks user specification", {
  spec1 <- my_model()
  expect_false(spec1$user_specified_engine)

  spec2 <- my_model(engine = "other")
  expect_true(spec2$user_specified_engine)
})

test_that("mode validation works", {
  expect_error(
    my_model(mode = "invalid"),
    "mode"
  )
})
```

---

## Summary

**Key points for constructors:**

1. **Function name** - Descriptive, not engine-specific
2. **Mode parameter** - Required for multi-mode, fixed for single-mode
3. **Main arguments** - Standardized names, use `rlang::enquo()`
4. **Engine parameter** - Sensible default, track if user-specified
5. **Use `new_model_spec()`** - Creates proper structure
6. **Minimal validation** - Most checks happen at fit time
7. **Good documentation** - Explain engines, arguments, examples
8. **Return model_spec** - With correct class hierarchy

**The constructor is the user's first interaction with your model - make it intuitive and well-documented.**
