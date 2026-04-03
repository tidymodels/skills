# Qualitative Parameters

**Creating categorical tuning parameters with discrete options**

This guide covers everything you need to create qualitative parameters with `new_qual_param()`.

> **Note for Source Development:** If contributing to dials, you can use internal validation and helper functions. See the [Source Development Guide](source-guide.md) for dials-specific patterns.

---

## Overview

Qualitative parameters represent categorical choices where options have no inherent numeric ordering. These parameters define discrete sets of alternatives for algorithm configuration.

**Reference implementations in dials:**

- Simple qualitative: `R/param_weight_func.R` (weight function choices), `R/param_activation.R` (activation functions)

- Multiple parameters: `R/param_activation.R` (contains `activation()` and `activation_2()`)

- Preprocessing methods: `R/param_normalize.R` (normalization methods)

- Algorithm choices: `R/param_degree_svm.R` (SVM kernel degree)

**Test patterns:**

- Basic qualitative tests: `tests/testthat/test-param_weight_func.R`

- Multiple parameter tests: `tests/testthat/test-param_activation.R`

---

## When to Use Qualitative Parameters

Use qualitative parameters when your tuning parameter:

- ✅ Represents **discrete categorical choices**

- ✅ Has **no natural ordering** (options are not "more" or "less")

- ✅ Uses **non-numeric values** or symbolic names

- ✅ Consists of **fundamentally different options**

**Common examples**:

- Activation functions (relu, sigmoid, tanh, softmax)

- Optimization algorithms (adam, sgd, rmsprop, adagrad)

- Distance metrics (euclidean, manhattan, cosine)

- Aggregation methods (mean, median, min, max, sum)

- Model modes or variants (classification, regression)

- Loss functions (cross-entropy, mse, hinge)

**When NOT to use**:

- ❌ Numeric values with ordering (use [Quantitative Parameters](quantitative-parameters.md))

- ❌ Counts or continuous values

- ❌ Parameters where interpolation makes sense

---

## Parameter Function Structure

### Basic Pattern

```r
# Extension pattern (use dials:: prefix)
my_parameter <- function(values = values_my_parameter) {
  dials::new_qual_param(
    type = "character",
    values = values,
    default = "default_value",  # Optional
    label = c(my_parameter = "Display Label")
  )
}

#' @rdname my_parameter
#' @export
values_my_parameter <- c("option1", "option2", "option3")

# Source pattern (no dials:: prefix)
my_parameter <- function(values = values_my_parameter) {
  new_qual_param(
    type = "character",
    values = values,
    default = "default_value",  # Optional
    label = c(my_parameter = "Display Label")
  )
}

#' @rdname my_parameter
#' @export
values_my_parameter <- c("option1", "option2", "option3")
```

### Function Arguments

**Standard arguments**:

- `values`: Allow users to customize available options

**Default values**:

- Reference companion `values_*` vector

- Let users subset or replace options

---

## Required Arguments

### type

**Controls data type of options**:

```r
type = "character"  # Text-based options (most common)
type = "logical"    # TRUE/FALSE options (rare)
```

**Use "character" for**:

- Method names (activation functions, optimizers)

- Algorithm choices (distance metrics, aggregation methods)

- Most categorical parameters

**Use "logical" for**:

- Binary flags

- TRUE/FALSE settings

- Very rare in practice (usually use character with two values instead)

**Examples**:

```r
# Character: activation functions
new_qual_param(
  type = "character",
  values = c("relu", "sigmoid", "tanh"),
  ...
)

# Logical: binary flag (rare)
new_qual_param(
  type = "logical",
  values = c(TRUE, FALSE),
  ...
)
```

### values

**Vector of all possible options**:

```r
values = c("option1", "option2", "option3")
```

**Rules**:

- Must be non-empty

- Type must match `type` argument

- All values must be unique

- Order matters (first value is default if `default` not specified)

**Best practice**: Create companion `values_*` vector:

```r
#' @rdname my_parameter
#' @export
values_my_parameter <- c("option1", "option2", "option3")

my_parameter <- function(values = values_my_parameter) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(my_parameter = "My Parameter")
  )
}
```

This pattern:

- ✅ Documents options clearly

- ✅ Allows users to see available values

- ✅ Enables subsetting: `my_parameter(values = values_my_parameter[1:2])`

- ✅ Follows dials package conventions

---

## Optional Arguments

### default

**Specify default value**:

```r
default = "specific_value"  # Explicit default
default = NULL              # Use first value in `values` (default)
```

**Behavior**:

- If `default = NULL` (the default), first value in `values` is used

- If explicit default provided, must be in `values`

**Examples**:

```r
# Explicit default
aggregation <- function(values = values_aggregation) {
  dials::new_qual_param(
    type = "character",
    values = values,
    default = "mean",  # Explicit
    label = c(aggregation = "Aggregation Method")
  )
}
values_aggregation <- c("mean", "median", "min", "max")

# Implicit default (first value)
aggregation <- function(values = values_aggregation) {
  dials::new_qual_param(
    type = "character",
    values = values,
    # default = "mean" implicitly
    label = c(aggregation = "Aggregation Method")
  )
}
values_aggregation <- c("mean", "median", "min", "max")
```

**When to use explicit default**:

- Default is not the first value alphabetically

- Want to emphasize recommended option

- Documentation clarity

**When to use implicit default**:

- First value in `values` is the desired default

- Simpler code

- Most common pattern in dials

### label

**Display name for parameter**:

```r
label = c(parameter_name = "Display Label")
```

**Conventions**:

- Name matches function name

- Label uses title case

- Concise but descriptive

- Describes what parameter controls

**Examples**:

```r
label = c(activation = "Activation Function")
label = c(optimizer = "Optimization Algorithm")
label = c(weight_func = "Distance Weighting Function")
label = c(aggregation = "Aggregation Method")
```

### finalize

**Rarely used for qualitative parameters**:

```r
finalize = NULL  # Almost always NULL for categorical
```

Qualitative parameters typically don't need finalization because options don't depend on data characteristics. The rare exception might be a parameter where available options depend on data properties, but this is uncommon.

---

## Creating Companion values_* Vectors

### Pattern and Convention

**Strong recommendation**: Always create a `values_*` vector alongside your parameter function.

```r
#' Activation function
#'
#' The activation function for neural networks.
#'
#' @param values A character vector of possible activation functions.
#'
#' @details
#' This parameter defines the activation function between layers.
#'
#' @examples
#' values_activation
#' activation()
#' activation(values = c("relu", "sigmoid"))
#'
#' @export
activation <- function(values = values_activation) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(activation = "Activation Function")
  )
}

#' @rdname activation
#' @export
values_activation <- c(
  "relu", "sigmoid", "tanh", "softmax",
  "elu", "selu", "softplus", "softsign"
)
```

### Why Use values_* Vectors?

**For users**:

```r
# See available options
values_activation
#> [1] "relu"     "sigmoid"  "tanh"     "softmax"
#> [5] "elu"      "selu"     "softplus" "softsign"

# Use default (all options)
activation()

# Subset to specific options
activation(values = c("relu", "tanh"))

# Use first few options
activation(values = values_activation[1:4])
```

**For package maintainers**:

- Single source of truth for options

- Easy to update available values

- Clear documentation

- Consistent with dials conventions

### Naming Convention

- Vector name: `values_[parameter_name]`

- If parameter is `activation()`, vector is `values_activation`

- If parameter is `weight_func()`, vector is `values_weight_func`

- Export both with `@export` tag

- Link with `@rdname` for shared documentation

### Step-by-Step: Creating Companion Vectors

Here's a detailed walkthrough for creating qualitative parameters with companion vectors:

```r
# STEP 1: Define the values vector with @rdname and @export
#' Activation function
#'
#' @param values A character vector of possible activation functions.
#' @examples
#' values_activation
#' activation()
#' @export
activation <- function(values = values_activation) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(activation = "Activation Function")
  )
}

# STEP 2: Create the companion vector using @rdname for shared documentation
#' @rdname activation
#' @export
values_activation <- c("relu", "sigmoid", "tanh", "softmax")
```

**Key Components Explained:**

1. **@rdname tag**: Links the values vector to the parameter function documentation
   - Both appear on the same help page
   - Users can see the vector when looking up the parameter
   - Maintains consistency between function and values

2. **values_* naming**: Following the `values_[parameter_name]` convention
   - Clear relationship between parameter and its values
   - Consistent with dials package standards
   - Easy to discover and use

3. **@export on both**: Both the function AND the vector must be exported
   - Parameter function: Users call this to create the parameter
   - Values vector: Users reference this to see/subset options

4. **Default argument**: `values = values_my_parameter` in function signature
   - Links the function to its companion vector
   - Allows users to subset: `my_parameter(values = values_my_parameter[1:3])`
   - Makes the vector the default source of options

### Companion Vector Checklist

Before completing a qualitative parameter with companion vector, verify:

- [ ] Created parameter function with `new_qual_param()`
- [ ] Created companion `values_*` vector following naming convention
- [ ] Used `@rdname` to group them in documentation
- [ ] Added `@export` to BOTH the function and the vector
- [ ] Set function default argument to reference the vector: `values = values_my_parameter`
- [ ] Vector contains at least one valid option
- [ ] Vector type matches the `type` argument in `new_qual_param()`

---

## Common Patterns

### Pattern 1: Character Parameter with Values Vector

Most common pattern for categorical parameters:

```r
# Extension pattern
optimizer <- function(values = values_optimizer) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(optimizer = "Optimization Algorithm")
  )
}

#' @rdname optimizer
#' @export
values_optimizer <- c("adam", "sgd", "rmsprop", "adagrad")

# Source pattern
optimizer <- function(values = values_optimizer) {
  new_qual_param(
    type = "character",
    values = values,
    label = c(optimizer = "Optimization Algorithm")
  )
}

#' @rdname optimizer
#' @export
values_optimizer <- c("adam", "sgd", "rmsprop", "adagrad")
```

### Pattern 2: Character Parameter with Explicit Default

When default is not first value:

```r
# Extension pattern
aggregation <- function(values = values_aggregation) {
  dials::new_qual_param(
    type = "character",
    values = values,
    default = "none",  # Explicit default
    label = c(aggregation = "Aggregation Method")
  )
}

#' @rdname aggregation
#' @export
values_aggregation <- c("none", "min", "max", "mean", "sum")
```

### Pattern 3: Logical Parameter

Rare, but occasionally useful:

```r
# Extension pattern
use_weights <- function(values = c(TRUE, FALSE)) {
  dials::new_qual_param(
    type = "logical",
    values = values,
    label = c(use_weights = "Use Case Weights")
  )
}

# Source pattern
use_weights <- function(values = c(TRUE, FALSE)) {
  new_qual_param(
    type = "logical",
    values = values,
    label = c(use_weights = "Use Case Weights")
  )
}
```

**Note**: Usually better to use character with two values instead:

```r
weighting <- function(values = c("weighted", "unweighted")) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(weighting = "Weighting Method")
  )
}
```

### Pattern 4: Multiple Related Parameters

When you need variants (e.g., activation for different layers):

```r
# First activation parameter
activation <- function(values = values_activation) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(activation = "Activation Function")
  )
}

#' @rdname activation
#' @export
values_activation <- c("relu", "sigmoid", "tanh", "softmax")

# Second activation parameter (for output layer)
activation_2 <- function(values = values_activation_2) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(activation_2 = "Activation Function (Second Layer)")
  )
}

#' @rdname activation_2
#' @export
values_activation_2 <- c("sigmoid", "softmax", "linear")
```

---

## Complete Examples

### Example 1: Basic Character Parameter

Distance weighting function:

```r
# Extension pattern
weight_func <- function(values = values_weight_func) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(weight_func = "Distance Weighting Function")
  )
}

#' @rdname weight_func
#' @export
values_weight_func <- c(
  "rectangular", "triangular", "epanechnikov",
  "biweight", "triweight", "cosine",
  "gaussian", "rank"
)

# Usage
weight_func()
#> Distance Weighting Function (qualitative)
#> 8 possible values include:
#> 'rectangular', 'triangular', 'epanechnikov', 'biweight', 'triweight' and 2 more

# See all options
values_weight_func
#> [1] "rectangular"  "triangular"   "epanechnikov" "biweight"
#> [5] "triweight"    "cosine"       "gaussian"     "rank"

# Use subset
weight_func(values = c("rectangular", "gaussian", "rank"))

# Sample values
set.seed(123)
dials::value_sample(weight_func(), n = 3)
#> [1] "biweight"   "gaussian"   "triangular"
```

### Example 2: Character Parameter with Explicit Default

Aggregation method with "none" as default:

```r
# Extension pattern
aggregation <- function(values = values_aggregation) {
  dials::new_qual_param(
    type = "character",
    values = values,
    default = "none",
    label = c(aggregation = "Aggregation Method")
  )
}

#' @rdname aggregation
#' @export
values_aggregation <- c("none", "min", "max", "mean", "sum")

# Usage
aggregation()
#> Aggregation Method (qualitative)
#> 5 possible values include:
#> 'none', 'min', 'max', 'mean' and 'sum'

# Generate grid with all values
grid <- dials::grid_regular(aggregation())
grid
#> # A tibble: 5 × 1
#>   aggregation
#>   <chr>
#> 1 none
#> 2 min
#> 3 max
#> 4 mean
#> 5 sum

# Generate random grid (sampling with replacement)
set.seed(456)
grid <- dials::grid_random(aggregation(), size = 10)
grid
#> # A tibble: 10 × 1
#>    aggregation
#>    <chr>
#>  1 max
#>  2 none
#>  3 sum
#>  4 mean
#>  # ... with 6 more rows
```

### Example 3: Optimization Algorithm

Common ML parameter:

```r
# Extension pattern
optimizer <- function(values = values_optimizer) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(optimizer = "Optimization Algorithm")
  )
}

#' @rdname optimizer
#' @export
values_optimizer <- c("adam", "sgd", "rmsprop", "adagrad")

# Usage
optimizer()
#> Optimization Algorithm (qualitative)
#> 4 possible values include:
#> 'adam', 'sgd', 'rmsprop' and 'adagrad'

# Custom subset
optimizer(values = c("adam", "sgd"))
#> Optimization Algorithm (qualitative)
#> 2 possible values include:
#> 'adam' and 'sgd'

# Use in grid
params <- dials::parameters(
  learn_rate = dials::learn_rate(),
  optimizer = optimizer()
)

grid <- dials::grid_regular(params, levels = c(3, 4))
grid
#> # A tibble: 12 × 2
#>    learn_rate optimizer
#>         <dbl> <chr>
#>  1   0.0000001 adam
#>  2   0.0000001 sgd
#>  3   0.0000001 rmsprop
#>  4   0.0000001 adagrad
#>  5   0.001     adam
#>  # ... with 7 more rows
```

---

## Extension vs Source Patterns

### Extension Development

**Always use `dials::` prefix**:

```r
my_param <- function(values = values_my_param) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(my_param = "My Parameter")
  )
}

#' @rdname my_param
#' @export
values_my_param <- c("option1", "option2", "option3")

# Use dials:: for grid functions
dials::grid_regular(my_param())
dials::value_sample(my_param(), n = 3)
```

See [Extension Development Guide](extension-guide.md) for complete guide.

### Source Development

**No `dials::` prefix needed**:

```r
my_param <- function(values = values_my_param) {
  new_qual_param(
    type = "character",
    values = values,
    label = c(my_param = "My Parameter")
  )
}

#' @rdname my_param
#' @export
values_my_param <- c("option1", "option2", "option3")

# Direct function calls
grid_regular(my_param())
value_sample(my_param(), n = 3)
```

See [Source Development Guide](source-guide.md) for complete guide.

---

## Testing Considerations

### Essential Tests

All qualitative parameters should test:

1. **Parameter creation**: Valid object structure
2. **Custom values**: Accepts user-provided options
3. **Type enforcement**: Correct value types
4. **Grid integration**: Works with `grid_regular()`, `grid_random()`
5. **Value utilities**: `value_sample()` works
6. **Default value**: Correct default (explicit or implicit)
7. **Values validation**: Rejects empty or invalid values

### Example Test Suite

```r
# tests/testthat/test-my-parameter.R

test_that("my_parameter creates valid parameter", {
  param <- my_parameter()

  expect_s3_class(param, "qual_param")
  expect_equal(param$type, "character")
  expect_equal(param$values, values_my_parameter)
})

test_that("my_parameter accepts custom values", {
  custom_values <- c("option1", "option2")
  param <- my_parameter(values = custom_values)

  expect_equal(param$values, custom_values)
})

test_that("my_parameter has correct default", {
  param <- my_parameter()

  # If explicit default set
  expect_equal(param$default, "option1")

  # If implicit (first value)
  expect_equal(param$default, values_my_parameter[1])
})

test_that("my_parameter works with grid_regular", {
  param <- my_parameter()
  grid <- dials::grid_regular(param)

  expect_equal(nrow(grid), length(values_my_parameter))
  expect_true(all(grid$my_parameter %in% values_my_parameter))
})

test_that("my_parameter works with grid_random", {
  set.seed(123)
  param <- my_parameter()
  grid <- dials::grid_random(param, size = 10)

  expect_equal(nrow(grid), 10)
  expect_true(all(grid$my_parameter %in% values_my_parameter))
})

test_that("my_parameter works with value_sample", {
  set.seed(456)
  param <- my_parameter()
  samples <- dials::value_sample(param, n = 5)

  expect_length(samples, 5)
  expect_true(all(samples %in% values_my_parameter))
})

test_that("my_parameter rejects invalid values", {
  expect_error(my_parameter(values = character(0)))  # Empty
  expect_error(my_parameter(values = NULL))          # NULL
  expect_error(my_parameter(values = c(1, 2, 3)))   # Wrong type
})

test_that("values_my_parameter is exported and correct", {
  expect_true("values_my_parameter" %in% ls("package:mypackage"))
  expect_type(values_my_parameter, "character")
  expect_true(length(values_my_parameter) > 0)
})
```

For extension development, see [Testing Requirements](package-extension-requirements.md#testing-requirements).

For source development, see [Testing Patterns (Source)](testing-patterns-source.md).

---

## Next Steps

### Learn Related Topics

- **Quantitative parameters**: [Quantitative Parameters Guide](quantitative-parameters.md)

- **Parameter system**: [Parameter System Overview](parameter-system.md)

- **Grid integration**: [Grid Integration Guide](grid-integration.md)

### Implementation Guides

- **Extension development**: [Extension Development Guide](extension-guide.md)

- **Source development**: [Source Development Guide](source-guide.md)

---

**Last Updated:** 2026-03-31
