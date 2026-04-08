# Quantitative Parameters

**Creating numeric tuning parameters for continuous and integer values**

This guide covers everything you need to create quantitative parameters with
`new_quant_param()`.

> **Note for Source Development:** If contributing to dials, you can use
> internal validation and helper functions. See the [Source Development
> Guide](source-guide.md) for dials-specific patterns.

--------------------------------------------------------------------------------

## Overview

Quantitative parameters represent numeric values that can vary continuously or
discretely across a defined range. These are the most common type of tuning
parameters in machine learning.

**Reference implementations in dials:**

- Simple quantitative: `R/param_penalty.R` (regularization penalty),
  `R/param_learn_rate.R` (learning rate)

- With transformations: `R/param_penalty.R` (log10 transformation),
  `R/param_sample_size.R` (log2 transformation)

- Data-dependent: `R/param_mtry.R` (finalize with `get_p`), `R/param_num_comp.R`
  (finalize with `get_p`)

- Integer parameters: `R/param_num_trees.R`, `R/param_num_terms.R`

**Test patterns:**

- Basic parameter tests: `tests/testthat/test-param_penalty.R`

- Finalization tests: `tests/testthat/test-param_mtry.R`

- Transformation tests: `tests/testthat/test-param_learn_rate.R`

--------------------------------------------------------------------------------

## When to Use Quantitative Parameters

Use quantitative parameters when your tuning parameter:

- ✅ Takes **numeric values** (continuous or integer)

- ✅ Has a **natural ordering** (more vs less makes sense)

- ✅ Can be **interpolated** (values between bounds are meaningful)

- ✅ Benefits from **regular spacing** in grid search

**Common examples**:

- Regularization amounts (penalty, cost, lambda)

- Learning rates and decay factors

- Number of features, neighbors, trees, layers

- Thresholds and cutoffs

- Proportions, fractions, mixtures

- Degrees of freedom, polynomial degrees

**When NOT to use**:

- ❌ Categorical choices (use [Qualitative
  Parameters](qualitative-parameters.md))

- ❌ Text-based options (method names, algorithms)

- ❌ Unordered discrete options

--------------------------------------------------------------------------------

## Parameter Function Structure

### Basic Pattern

```r
# Extension pattern (use dials:: prefix)
my_parameter <- function(range = c(lower, upper), trans = NULL) {
  dials::new_quant_param(
    type = "double" or "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_parameter = "Display Label"),
    finalize = NULL
  )
}

# Source pattern (no dials:: prefix)
my_parameter <- function(range = c(lower, upper), trans = NULL) {
  new_quant_param(
    type = "double" or "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_parameter = "Display Label"),
    finalize = NULL
  )
}
```

### Function Arguments

**Standard arguments**:

- `range`: Allow users to customize bounds

- `trans`: Allow users to change or remove transformation

**Default values**:

- Choose sensible defaults that work for most cases

- Wide ranges are better (users can narrow)

- Match transformations to how parameter is used in practice

--------------------------------------------------------------------------------

## Required Arguments

### type

**Controls numeric precision**:

```r
type = "double"   # Continuous values (floating-point)
type = "integer"  # Discrete whole numbers
```

**Use "double" for**:

- Continuous parameters (penalties, rates, proportions)

- Parameters that can take any real value

- When precision matters (learning rates, tolerances)

**Use "integer" for**:

- Count-based parameters (number of trees, neighbors, features)

- Parameters that must be whole numbers

- When fractional values don't make sense

**Examples**:

```r
# Double: penalty can be any value from 10^-10 to 1
new_quant_param(type = "double", range = c(-10, 0), ...)

# Integer: number of neighbors must be whole number
new_quant_param(type = "integer", range = c(1L, 15L), ...)
```

### range

**Specifies parameter bounds**:

```r
range = c(lower, upper)
```

**Rules**:

- Must be two-element vector

- `lower` must be less than `upper`

- Can include `unknown()` for data-dependent bounds

- If `trans` is provided, range is in **transformed space**

**Fixed range examples**:

```r
range = c(0, 1)          # Proportion from 0 to 1
range = c(1L, 100L)      # Integer count from 1 to 100
range = c(-10, 0)        # Log-scale: 10^-10 to 10^0
```

**Data-dependent range examples**:

```r
range = c(1L, unknown())     # Upper bound depends on data
range = c(0.01, unknown())   # Lower fixed, upper from data
```

See [Data-Dependent Parameters](data-dependent-parameters.md) for `unknown()`
details.

### inclusive

**Controls whether endpoints can be sampled**:

```r
inclusive = c(lower_inclusive, upper_inclusive)
```

**Options**:

- `c(TRUE, TRUE)`: Both endpoints included (most common)

- `c(FALSE, FALSE)`: Both endpoints excluded

- `c(TRUE, FALSE)`: Lower included, upper excluded

- `c(FALSE, TRUE)`: Lower excluded, upper included

**Common patterns**:

```r
# Most parameters: include both endpoints
inclusive = c(TRUE, TRUE)
# Example: neighbors from 1 to 15, both valid

# Probabilities strictly between 0 and 1
inclusive = c(FALSE, FALSE)
# Example: dropout rate from 0.001 to 0.499

# Rates where zero is valid but upper bound is exclusive
inclusive = c(TRUE, FALSE)
# Example: learning rate from 0 to just under 1
```

**⚠️ Warning with integer ranges**:

With `inclusive = c(FALSE, FALSE)` and `range = c(1L, 3L)`, only value 2 is
valid. Be careful with small integer ranges!

--------------------------------------------------------------------------------

## Optional Arguments

### trans

**Apply scale transformation**:

```r
trans = NULL                      # No transformation (default)
trans = scales::transform_log10() # Base-10 logarithm
trans = scales::transform_log()   # Natural logarithm
trans = scales::transform_sqrt()  # Square root
```

**When to use transformations**:

- Parameter spans multiple orders of magnitude

- Equal steps in transformed space are more meaningful

- Literature commonly discusses parameter on that scale

**Key point**: When `trans` is provided, `range` is in **transformed space**

**Example**:

```r
# Range in log10 space: -10 to 0
# Actual values: 10^-10 to 10^0 = 0.0000000001 to 1
penalty <- function(range = c(-10, 0), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(penalty = "Amount of Regularization"),
    finalize = NULL
  )
}
```

See [Transformations](transformations.md) for comprehensive guide.

### finalize

**Resolve data-dependent ranges**:

```r
finalize = NULL           # No finalization (default)
finalize = dials::get_p   # Built-in: set upper to # predictors
finalize = dials::get_n   # Built-in: set upper to # observations
finalize = custom_fn      # Custom finalize function
```

**When to use**:

- Upper bound depends on dataset size

- Number of features/observations matters

- Parameter meaningfulness depends on data dimensions

**Built-in finalize functions**:

- `get_p()`: Number of predictors (ncol)

- `get_n()`: Number of observations (nrow)

- `get_n_frac()`: Fraction of observations

- `get_log_p()`: Log of predictors

See [Data-Dependent Parameters](data-dependent-parameters.md) for details.

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
label = c(penalty = "Amount of Regularization")
label = c(mtry = "# Randomly Selected Predictors")
label = c(learn_rate = "Learning Rate")
label = c(num_comp = "# Principal Components")
```

--------------------------------------------------------------------------------

## Common Patterns

### Pattern 1: Simple Integer Parameter

Count-based parameters with fixed range:

```r
# Extension pattern
num_neighbors <- function(range = c(1L, 15L), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(num_neighbors = "# Nearest Neighbors"),
    finalize = NULL
  )
}

# Source pattern
num_neighbors <- function(range = c(1L, 15L), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(num_neighbors = "# Nearest Neighbors"),
    finalize = NULL
  )
}
```

**Use for**: tree depth, number of layers, number of iterations

### Pattern 2: Simple Double Parameter

Continuous parameters with fixed range:

```r
# Extension pattern
threshold <- function(range = c(0, 1), trans = NULL) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(threshold = "Classification Threshold"),
    finalize = NULL
  )
}

# Source pattern
threshold <- function(range = c(0, 1), trans = NULL) {
  new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(threshold = "Classification Threshold"),
    finalize = NULL
  )
}
```

**Use for**: proportions, mixtures, rates (when range is narrow)

### Pattern 3: Transformed Parameter (Log Scale)

Parameters spanning orders of magnitude:

```r
# Extension pattern
penalty <- function(range = c(-10, 0), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(penalty = "Amount of Regularization"),
    finalize = NULL
  )
}

# Source pattern
penalty <- function(range = c(-10, 0), trans = transform_log10()) {
  new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(penalty = "Amount of Regularization"),
    finalize = NULL
  )
}
```

**Use for**: penalties, costs, learning rates, decay factors

### Pattern 4: Data-Dependent Parameter

Parameters with unknown upper bound:

```r
# Extension pattern
mtry <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = dials::get_p
  )
}

# Source pattern
mtry <- function(range = c(1L, unknown()), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = get_p
  )
}
```

**Use for**: feature counts, component counts, sample sizes

--------------------------------------------------------------------------------

## Complete Examples

### Example 1: Simple Integer Parameter

Number of trees in a random forest:

```r
# Extension pattern
num_trees <- function(range = c(1L, 2000L), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(num_trees = "# Trees"),
    finalize = NULL
  )
}

# Usage
num_trees()
#> # Trees (quantitative)
#> Range: [1, 2000]

# Custom range
num_trees(range = c(100L, 500L))
#> # Trees (quantitative)
#> Range: [100, 500]

# Generate grid
dials::grid_regular(num_trees(), levels = 5)
#> # A tibble: 5 × 1
#>   num_trees
#>       <int>
#> 1         1
#> 2       500
#> 3      1000
#> 4      1500
#> 5      2000
```

### Example 2: Simple Double Parameter

Mixture proportion for elastic net:

```r
# Extension pattern
mixture <- function(range = c(0, 1), trans = NULL) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mixture = "Proportion of Lasso Penalty"),
    finalize = NULL
  )
}

# Usage
mixture()
#> Proportion of Lasso Penalty (quantitative)
#> Range: [0, 1]

# Sample values
set.seed(123)
dials::value_sample(mixture(), n = 5)
#> [1] 0.287 0.788 0.409 0.883 0.940

# Generate sequence
dials::value_seq(mixture(), n = 5)
#> [1] 0.00 0.25 0.50 0.75 1.00
```

### Example 3: Transformed Parameter

Learning rate on log scale:

```r
# Extension pattern
learn_rate <- function(range = c(-5, -1), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(learn_rate = "Learning Rate"),
    finalize = NULL
  )
}

# Usage
learn_rate()
#> Learning Rate (quantitative)
#> Transformer: log-10
#> Range (transformed scale): [-5, -1]

# Actual values: 10^-5 to 10^-1
learn_rate_param <- learn_rate()

# Regular grid in transformed space
grid <- dials::grid_regular(learn_rate_param, levels = 5)
grid
#> # A tibble: 5 × 1
#>   learn_rate
#>        <dbl>
#> 1   0.00001  # 10^-5
#> 2   0.0001   # 10^-4
#> 3   0.001    # 10^-3
#> 4   0.01     # 10^-2
#> 5   0.1      # 10^-1

# Even spacing on log scale!
```

### Example 4: Data-Dependent Parameter

Maximum number of features to select:

```r
# Extension pattern
max_features <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(max_features = "# Maximum Features"),
    finalize = dials::get_p
  )
}

# Usage
max_features()
#> # Maximum Features (quantitative)
#> Range: [1, ?]

# Finalize with data
param <- max_features()
finalized <- dials::finalize(param, mtcars[, -1])  # 10 predictors
finalized
#> # Maximum Features (quantitative)
#> Range: [1, 10]

# Now can generate grid
dials::grid_regular(finalized, levels = 5)
#> # A tibble: 5 × 1
#>   max_features
#>          <int>
#> 1            1
#> 2            3
#> 3            5
#> 4            8
#> 5           10
```

### Example 5: Custom Finalize Function

Number of initial MARS terms:

```r
# Extension pattern
num_initial_terms <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(num_initial_terms = "# Initial MARS Terms"),
    finalize = get_initial_mars_terms
  )
}

# Custom finalize function
get_initial_mars_terms <- function(object, x) {
  # Earth package formula: min(200, max(20, 2 * ncol(x))) + 1
  upper_bound <- min(200, max(20, 2 * ncol(x))) + 1
  upper_bound <- as.integer(upper_bound)

  # Update range
  bounds <- dials::range_get(object)
  bounds$upper <- upper_bound
  dials::range_set(object, bounds)
}

# Usage
num_initial_terms()
#> # Initial MARS Terms (quantitative)
#> Range: [1, ?]

# Finalize with small dataset (10 predictors)
param <- num_initial_terms()
finalized <- dials::finalize(param, mtcars[, -1])
finalized
#> # Initial MARS Terms (quantitative)
#> Range: [1, 41]  # min(200, max(20, 2*10)) + 1 = 41

# Finalize with large dataset (100 predictors)
large_data <- matrix(rnorm(100 * 100), ncol = 100)
finalized_large <- dials::finalize(param, large_data)
finalized_large
#> # Initial MARS Terms (quantitative)
#> Range: [1, 201]  # min(200, max(20, 2*100)) + 1 = 201
```

--------------------------------------------------------------------------------

## Extension vs Source Patterns

### Extension Development

**Always use `dials::` prefix**:

```r
my_param <- function(range = c(0, 1), trans = NULL) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_param = "My Parameter"),
    finalize = NULL
  )
}

# Use dials:: for all functions
dials::unknown()
dials::get_p
dials::range_get()
dials::range_set()
scales::transform_log10()  # scales is separate package
```

See [Extension Development Guide](extension-guide.md) for complete guide.

### Source Development

**No `dials::` prefix needed**:

```r
my_param <- function(range = c(0, 1), trans = NULL) {
  new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_param = "My Parameter"),
    finalize = NULL
  )
}

# Direct function calls
unknown()
get_p
range_get()
range_set()
transform_log10()  # Available in dials namespace
```

See [Source Development Guide](source-guide.md) for complete guide.

--------------------------------------------------------------------------------

## Testing Considerations

### Essential Tests

All quantitative parameters should test:

1. **Parameter creation**: Valid object structure
2. **Custom ranges**: Accepts user-provided bounds
3. **Type enforcement**: Correct numeric type
4. **Grid integration**: Works with `grid_regular()`, `grid_random()`
5. **Value utilities**: `value_sample()` and `value_seq()` work
6. **Range validation**: Rejects invalid ranges
7. **Transformation**: If applicable, transformed values are correct
8. **Finalization**: If applicable, data-dependent bounds resolve

### Example Test Suite

```r
# tests/testthat/test-my-parameter.R

test_that("my_parameter creates valid parameter", {
  param <- my_parameter()

  expect_s3_class(param, "quant_param")
  expect_equal(param$type, "double")
  expect_equal(param$range$lower, 0)
  expect_equal(param$range$upper, 1)
})

test_that("my_parameter accepts custom range", {
  param <- my_parameter(range = c(0.2, 0.8))

  expect_equal(param$range$lower, 0.2)
  expect_equal(param$range$upper, 0.8)
})

test_that("my_parameter works with grid_regular", {
  param <- my_parameter()
  grid <- dials::grid_regular(param, levels = 5)

  expect_equal(nrow(grid), 5)
  expect_true(all(grid$my_parameter >= 0))
  expect_true(all(grid$my_parameter <= 1))
})

test_that("my_parameter works with grid_random", {
  set.seed(123)
  param <- my_parameter()
  grid <- dials::grid_random(param, size = 10)

  expect_equal(nrow(grid), 10)
  expect_true(all(grid$my_parameter >= 0))
  expect_true(all(grid$my_parameter <= 1))
})

test_that("my_parameter works with value utilities", {
  param <- my_parameter()

  # value_sample
  set.seed(456)
  samples <- dials::value_sample(param, n = 5)
  expect_length(samples, 5)
  expect_true(all(samples >= 0 & samples <= 1))

  # value_seq
  seq_vals <- dials::value_seq(param, n = 5)
  expect_length(seq_vals, 5)
  expect_true(all(seq_vals >= 0 & seq_vals <= 1))
})

test_that("my_parameter rejects invalid ranges", {
  expect_error(my_parameter(range = c(1, 0)))    # lower > upper
  expect_error(my_parameter(range = c(0, NA)))   # NA value
  expect_error(my_parameter(range = 0))          # length != 2
})
```

For extension development, see [Testing
Requirements](package-extension-requirements.md#testing-requirements).

For source development, see [Testing Patterns
(Source)](testing-patterns-source.md).

--------------------------------------------------------------------------------

## Next Steps

### Learn Advanced Features

- **Transformations**: [Transformations Guide](transformations.md)

- **Data-dependent ranges**: [Data-Dependent Parameters
  Guide](data-dependent-parameters.md)

- **Grid integration**: [Grid Integration Guide](grid-integration.md)

### Explore Related Topics

- **Qualitative parameters**: [Qualitative Parameters
  Guide](qualitative-parameters.md)

- **Parameter system**: [Parameter System Overview](parameter-system.md)

### Implementation Guides

- **Extension development**: [Extension Development Guide](extension-guide.md)

- **Source development**: [Source Development Guide](source-guide.md)

--------------------------------------------------------------------------------

**Last Updated:** 2026-03-31
