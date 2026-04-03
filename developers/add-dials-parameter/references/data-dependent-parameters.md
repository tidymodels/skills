# Data-Dependent Parameters

**Creating parameters with unknown bounds resolved by training data**

This guide covers how to create parameters whose ranges depend on dataset characteristics using `unknown()` and the finalization system.

> **Note for Source Development:** If contributing to dials, you can use internal finalization functions. See the [Source Development Guide](source-guide.md) for dials-specific patterns.

---

## Overview

Data-dependent parameters have ranges that cannot be determined until the training dataset is available. They use `unknown()` placeholders and finalization functions to resolve bounds based on data characteristics.

**Reference implementations in dials:**

- Predictor-dependent: `R/param_mtry.R` (uses `get_p` for number of predictors), `R/param_num_comp.R` (PCA components)

- Observation-dependent: `R/param_sample_size.R` (uses `get_n` for number of observations), `R/param_min_n.R` (minimum node size)

- Term-dependent: `R/param_num_terms.R` (uses `get_p` for model terms)

**Finalization functions:**

- `get_p`: Resolves to number of predictors in dataset

- `get_n`: Resolves to number of observations in dataset

- `get_n_frac`: Resolves to fraction of observations

- `get_n_frac_range`: Resolves range based on observation fraction

- `get_rbf_range`: Resolves radial basis function range

**Test patterns:**

- Finalization tests: `tests/testthat/test-param_mtry.R` (demonstrates `finalize()` usage)

- Unknown handling: `tests/testthat/test-unknown.R` (placeholder behavior)

---

## Understanding unknown()

### The Placeholder

`unknown()` is a special placeholder for parameter bounds that cannot be determined until you see the data:

```r
# Extension pattern
mtry <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,  # Upper bound is unknown
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = dials::get_p
  )
}

mtry()
#> # Randomly Selected Predictors (quantitative)
#> Range: [1, ?]
#> ^^^ Question mark indicates unknown bound
```

### Why unknown() Exists

Some parameters depend on dataset properties:

- **Number of predictors**: Can't sample more features than exist

- **Number of observations**: Sample size must be ≤ dataset size

- **Number of columns**: PCA components ≤ number of variables

Without seeing the data, we can't set sensible upper bounds.

### Where unknown() Appears

Typically in the **upper bound** of the range:

```r
range = c(1L, unknown())        # Most common: lower fixed, upper unknown
range = c(unknown(), 100L)      # Rare: upper fixed, lower unknown
range = c(unknown(), unknown()) # Very rare: both bounds unknown
```

---

## When Parameters Need Data-Dependent Ranges

Use `unknown()` and finalization when:

### Number of Predictors Determines Upper Bound

**Examples**:

- `mtry()`: Randomly selected predictors in random forests

- `num_comp()`: Number of PCA components

- `max_features`: Maximum features to select

- `num_terms()`: Number of model terms based on predictors

**Reason**: Can't select more features than exist in the dataset

```r
# Can't set upper bound without knowing # predictors
mtry <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = dials::get_p  # Will set upper = ncol(x)
  )
}
```

### Number of Observations Affects Range

**Examples**:

- `sample_size()`: Rows to sample

- `min_n()`: Minimum observations in node

- `bootstrap_sample()`: Bootstrap sample size

**Reason**: Sample size must be ≤ number of rows

```r
sample_size <- function(range = c(dials::unknown(), dials::unknown())) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = NULL,
    label = c(sample_size = "# Observations Sampled"),
    finalize = dials::get_n_frac
  )
}
```

### Complex Data-Dependent Logic

**Examples**:

- `num_initial_terms()`: MARS terms based on earth package formula

- Custom bounds based on multiple data properties

- Heuristic-based range adjustment

**Reason**: Upper bound follows package-specific or domain-specific rules

```r
num_initial_terms <- function(range = c(1L, dials::unknown())) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = NULL,
    label = c(num_initial_terms = "# Initial MARS Terms"),
    finalize = get_initial_mars_terms  # Custom logic
  )
}
```

---

## The Finalization System

### Overview

Finalization resolves `unknown()` bounds using training data:

```
Parameter with unknown() → finalize(param, data) → Parameter with known bounds
```

### The finalize Argument

When creating a parameter, provide a `finalize` function:

```r
my_param <- function(range = c(1L, unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_param = "My Parameter"),
    finalize = get_my_bound  # Finalize function
  )
}
```

### Finalize Function Signature

```r
finalize_function <- function(object, x) {
  # object: Parameter object with unknown() bounds
  # x: Predictor data (matrix, data frame, or tibble)
  #
  # Returns: Parameter object with resolved bounds
}
```

**Key points**:

- Takes parameter object and predictor data

- Examines data properties (ncol, nrow, etc.)

- Updates the parameter's range

- Returns modified parameter object

---

## Built-in Finalize Functions

dials provides several built-in finalize functions for common cases.

### get_p()

**Sets upper bound to number of predictors (columns)**

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

# Usage
param <- mtry()
param
#> Range: [1, ?]

finalized <- dials::finalize(param, mtcars[, -1])  # 10 predictors
finalized
#> Range: [1, 10]
```

**Use for**: Parameters bounded by number of features/predictors

### get_n()

**Sets upper bound to number of observations (rows)**

```r
# Extension pattern
max_samples <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(max_samples = "# Maximum Samples"),
    finalize = dials::get_n
  )
}

# Usage
param <- max_samples()
finalized <- dials::finalize(param, mtcars[, -1])  # 32 rows
finalized
#> Range: [1, 32]
```

**Use for**: Parameters bounded by number of observations

### get_n_frac()

**Sets both bounds as fractions of observations**

```r
# Extension pattern
sample_prop <- function(range = c(dials::unknown(), dials::unknown())) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = NULL,
    label = c(sample_prop = "# Sampled Observations"),
    finalize = dials::get_n_frac
  )
}

# Usage
param <- sample_prop()
finalized <- dials::finalize(param, mtcars[, -1])  # 32 rows
finalized
#> Range: [floor(0.1 * 32), 32] = [3, 32]
```

**Use for**: Sample sizes as proportion of dataset

### get_log_p()

**Sets upper bound to log of number of predictors**

```r
# Extension pattern
sparse_features <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(sparse_features = "# Sparse Features"),
    finalize = dials::get_log_p
  )
}

# Usage
param <- sparse_features()
large_data <- matrix(rnorm(100 * 100), ncol = 100)
finalized <- dials::finalize(param, large_data)
finalized
#> Range: [1, log(100)] ≈ [1, 5]
```

**Use for**: Parameters that scale logarithmically with predictors

---

## Creating Custom Finalize Functions

For complex logic, create custom finalize functions using `range_get()` and `range_set()`.

### Pattern

```r
# Extension pattern
custom_finalize <- function(object, x) {
  # 1. Calculate new bound(s) based on data
  new_upper <- calculate_upper_bound(x)

  # 2. Get current range
  bounds <- dials::range_get(object)

  # 3. Update bound(s)
  bounds$upper <- new_upper

  # 4. Set new range and return
  dials::range_set(object, bounds)
}
```

### range_get()

**Extract current range from parameter**:

```r
param <- mtry()
bounds <- dials::range_get(param)
bounds
#> $lower
#> [1] 1
#>
#> $upper
#> unknown()
```

Returns a list with `$lower` and `$upper`.

### range_set()

**Set new range on parameter**:

```r
new_bounds <- list(lower = 1, upper = 10)
updated_param <- dials::range_set(param, new_bounds)
updated_param
#> Range: [1, 10]
```

Takes parameter and list with `$lower` and `$upper`, returns updated parameter.

### Step-by-Step: Writing a Custom Finalize Function

Here's a detailed walkthrough of creating a custom finalize function:

```r
# STEP 1: Create the parameter function
num_genes <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(num_genes = "# Genes to Select"),
    finalize = get_num_genes  # Reference your custom finalize function
  )
}

# STEP 2: Create the custom finalize function
get_num_genes <- function(object, x) {
  # object: The parameter object with unknown() bounds
  # x: The predictor data (data frame or matrix)

  # STEP 2A: Calculate the new bound based on data
  # Goal: Set upper bound to 80% of available genes (columns)
  num_available_genes <- ncol(x)
  new_upper <- floor(0.8 * num_available_genes)

  # STEP 2B: Ensure bound is valid
  # At least 1 gene must be selectable
  new_upper <- max(1L, new_upper)
  # Ensure it's an integer type
  new_upper <- as.integer(new_upper)

  # STEP 2C: Get the current range from the parameter
  # This returns a list with $lower and $upper
  bounds <- dials::range_get(object)
  # bounds$lower is still 1L (unchanged)
  # bounds$upper is currently unknown()

  # STEP 2D: Update the upper bound
  # Keep lower bound unchanged, update upper
  bounds$upper <- new_upper

  # STEP 2E: Set the new range and return
  # This updates the parameter object and returns it
  updated_param <- dials::range_set(object, bounds)
  return(updated_param)
}
```

**Key Insights:**

1. **range_get() returns a list**: It has `$lower` and `$upper` components
2. **Modify the list**: Update `bounds$upper` or `bounds$lower` as needed
3. **range_set() returns parameter**: It doesn't modify in-place, it returns a new parameter
4. **Type matters**: Convert to integer for integer parameters, double for double parameters
5. **Validation**: Always ensure bounds are sensible (lower < upper, at least 1, etc.)

### Common Patterns for Custom Finalize

**Pattern 1: Percentage of predictors**
```r
upper_bound <- floor(0.8 * ncol(x))  # 80% of features
```

**Pattern 2: Percentage of observations**
```r
upper_bound <- floor(0.5 * nrow(x))  # 50% of samples
```

**Pattern 3: Minimum of both dimensions** (for matrix factorization)
```r
upper_bound <- min(nrow(x), ncol(x)) - 1  # Rank constraint
```

**Pattern 4: Complex formula** (earth package style)
```r
upper_bound <- min(200, max(20, 2 * ncol(x))) + 1
```

**Pattern 5: Both bounds** (adaptive neighbors)
```r
bounds$lower <- max(3L, floor(0.01 * nrow(x)))
bounds$upper <- min(50L, floor(0.10 * nrow(x)))
```

### Custom Finalize Checklist

Before completing a custom finalize function, verify:

- [ ] Function signature is `function(object, x)`

- [ ] Calculates new bound(s) based on `ncol(x)` or `nrow(x)`

- [ ] Uses `dials::range_get(object)` to get current range

- [ ] Updates `bounds$upper` and/or `bounds$lower`

- [ ] Uses `dials::range_set(object, bounds)` to update

- [ ] Returns the updated parameter object

- [ ] Converts bounds to correct type (integer or double)

- [ ] Validates bounds (lower < upper, at least 1, etc.)

- [ ] Tests with sample data of different sizes

---

## Complete Examples

### Example 1: Using Built-in get_p()

Number of PCA components:

```r
# Extension pattern
num_comp <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(num_comp = "# Principal Components"),
    finalize = dials::get_p
  )
}

# Usage
num_comp()
#> # Principal Components (quantitative)
#> Range: [1, ?]

# Finalize with data
param <- num_comp()
finalized <- dials::finalize(param, mtcars[, -1])
finalized
#> # Principal Components (quantitative)
#> Range: [1, 10]

# Now can generate grid
grid <- dials::grid_regular(finalized, levels = 5)
grid
#> # A tibble: 5 × 1
#>   num_comp
#>      <int>
#> 1        1
#> 2        3
#> 3        5
#> 4        8
#> 5       10
```

### Example 2: Using Built-in get_n()

Maximum observations to use:

```r
# Extension pattern
max_obs <- function(range = c(10L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(max_obs = "# Maximum Observations"),
    finalize = dials::get_n
  )
}

# Usage
param <- max_obs()
finalized <- dials::finalize(param, mtcars[, -1])  # 32 rows
finalized
#> Range: [10, 32]
```

### Example 3: Custom Finalize with Simple Logic

Maximum features to select (80% of predictors):

```r
# Extension pattern
max_features <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(max_features = "# Maximum Features"),
    finalize = get_max_features
  )
}

get_max_features <- function(object, x) {
  # Set upper bound to 80% of predictors
  upper_bound <- floor(0.8 * ncol(x))
  upper_bound <- max(1L, upper_bound)  # At least 1
  upper_bound <- as.integer(upper_bound)

  # Update range
  bounds <- dials::range_get(object)
  bounds$upper <- upper_bound
  dials::range_set(object, bounds)
}

# Usage
param <- max_features()
finalized <- dials::finalize(param, mtcars[, -1])  # 10 predictors
finalized
#> Range: [1, 8]  # floor(0.8 * 10) = 8
```

### Example 4: Custom Finalize with Complex Logic

MARS initial terms (earth package formula):

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

get_initial_mars_terms <- function(object, x) {
  # Earth package formula: min(200, max(20, 2 * ncol(x))) + 1
  p <- ncol(x)
  upper_bound <- min(200, max(20, 2 * p)) + 1
  upper_bound <- as.integer(upper_bound)

  # Update range
  bounds <- dials::range_get(object)
  bounds$upper <- upper_bound
  dials::range_set(object, bounds)
}

# Usage
param <- num_initial_terms()

# Small dataset (10 predictors)
finalized_small <- dials::finalize(param, mtcars[, -1])
finalized_small
#> Range: [1, 41]  # min(200, max(20, 2*10)) + 1 = 41

# Large dataset (100 predictors)
large_data <- matrix(rnorm(100 * 100), ncol = 100)
finalized_large <- dials::finalize(param, large_data)
finalized_large
#> Range: [1, 201]  # min(200, max(20, 2*100)) + 1 = 201
```

### Example 5: Updating Both Bounds

Neighbor range based on data size:

```r
# Extension pattern
neighbors_adaptive <- function(range = c(dials::unknown(), dials::unknown())) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = NULL,
    label = c(neighbors_adaptive = "# Adaptive Neighbors"),
    finalize = get_adaptive_neighbors
  )
}

get_adaptive_neighbors <- function(object, x) {
  n <- nrow(x)

  # Set lower bound: at least 3, or 1% of data
  lower_bound <- max(3L, floor(0.01 * n))

  # Set upper bound: at most 50, or 10% of data
  upper_bound <- min(50L, floor(0.10 * n))

  # Ensure lower < upper
  if (lower_bound >= upper_bound) {
    lower_bound <- max(1L, upper_bound - 1L)
  }

  # Update range
  bounds <- list(
    lower = as.integer(lower_bound),
    upper = as.integer(upper_bound)
  )
  dials::range_set(object, bounds)
}

# Usage
param <- neighbors_adaptive()

# Small dataset (32 rows)
finalized_small <- dials::finalize(param, mtcars[, -1])
finalized_small
#> Range: [3, 3]  # max(3, floor(0.01*32)) to min(50, floor(0.10*32))

# Large dataset (1000 rows)
large_data <- matrix(rnorm(1000 * 10), ncol = 10)
finalized_large <- dials::finalize(param, large_data)
finalized_large
#> Range: [10, 50]  # floor(0.01*1000)=10 to min(50, floor(0.10*1000))=50
```

---

## How Finalization Works in tune Workflows

### Manual Finalization

Explicitly finalize before tuning:

```r
# Define parameter with unknown bound
mtry_param <- mtry()

# Finalize with training data
mtry_finalized <- dials::finalize(mtry_param, train_x)

# Use in grid
grid <- dials::grid_regular(mtry_finalized, levels = 5)

# Tune
tune::tune_grid(model_spec, resamples, grid = grid)
```

### Automatic Finalization in tune

The tune package automatically finalizes parameters during tuning:

```r
# Model with tunable parameter
rf_spec <- parsnip::rand_forest(mtry = tune::tune()) |>
  parsnip::set_engine("ranger") |>
  parsnip::set_mode("regression")

# Create workflow
wf <- workflows::workflow() |>
  workflows::add_model(rf_spec) |>
  workflows::add_formula(mpg ~ .)

# tune_grid automatically finalizes mtry using training data
results <- tune::tune_grid(
  wf,
  resamples = vfold_cv(mtcars),
  grid = 10  # Grid will use finalized mtry
)
```

### Workflow with Finalization

```r
# Extract parameter set
params <- workflows::extract_parameter_set_dials(wf)
params
#> Collection of 1 parameters for tuning
#>    id    parameter type object class
#>  mtry         mtry nparam[?]
#> Model parameters needing finalization: mtry

# Finalize parameters
params_finalized <- dials::finalize(params, mtcars[, -1])
params_finalized
#> Collection of 1 parameters for tuning
#>    id    parameter type object class
#>  mtry         mtry nparam[+]

# Generate grid with finalized parameters
grid <- dials::grid_regular(params_finalized, levels = 5)
```

---

## Extension vs Source Patterns

### Extension Development

**Use `dials::` prefix throughout**:

```r
# Parameter definition
mtry <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = dials::get_p  # Built-in finalize
  )
}

# Custom finalize function
custom_finalize <- function(object, x) {
  upper_bound <- calculate_bound(x)
  bounds <- dials::range_get(object)
  bounds$upper <- upper_bound
  dials::range_set(object, bounds)
}

# Usage
dials::finalize(param, data)
```

### Source Development

**No `dials::` prefix needed**:

```r
# Parameter definition
mtry <- function(range = c(1L, unknown()), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = get_p  # Built-in finalize
  )
}

# Custom finalize function
custom_finalize <- function(object, x) {
  upper_bound <- calculate_bound(x)
  bounds <- range_get(object)
  bounds$upper <- upper_bound
  range_set(object, bounds)
}

# Usage
finalize(param, data)
```

---

## Testing Data-Dependent Parameters

### Essential Tests

1. **Parameter with unknown bound**: Object created correctly
2. **Finalization works**: `finalize()` resolves unknown bounds
3. **Bounds are sensible**: Finalized range makes sense for data
4. **Grid generation**: Finalized parameter works with grid functions
5. **Edge cases**: Small datasets, single column, etc.

### Example Test Suite

```r
# tests/testthat/test-my-data-dependent-param.R

test_that("my_param creates parameter with unknown bound", {
  param <- my_param()

  expect_s3_class(param, "quant_param")
  expect_equal(param$range$lower, 1L)
  expect_s3_class(param$range$upper, "unknown")
})

test_that("my_param finalizes with data", {
  param <- my_param()
  finalized <- dials::finalize(param, mtcars[, -1])

  expect_s3_class(finalized, "quant_param")
  expect_type(finalized$range$upper, "integer")
  expect_false(inherits(finalized$range$upper, "unknown"))
})

test_that("my_param finalized range is sensible", {
  param <- my_param()
  finalized <- dials::finalize(param, mtcars[, -1])

  # Upper bound should be number of predictors
  expect_equal(finalized$range$upper, ncol(mtcars) - 1)
  expect_true(finalized$range$upper >= finalized$range$lower)
})

test_that("finalized my_param works with grid functions", {
  param <- my_param()
  finalized <- dials::finalize(param, mtcars[, -1])

  grid <- dials::grid_regular(finalized, levels = 5)
  expect_equal(nrow(grid), 5)
  expect_true(all(grid$my_param >= finalized$range$lower))
  expect_true(all(grid$my_param <= finalized$range$upper))
})

test_that("my_param handles small datasets", {
  small_data <- mtcars[1:5, 1:3]  # 5 rows, 2 predictors

  param <- my_param()
  finalized <- dials::finalize(param, small_data[, -1])

  expect_equal(finalized$range$upper, 2L)
  expect_true(finalized$range$lower <= finalized$range$upper)
})

test_that("my_param handles single column", {
  single_col <- data.frame(x = rnorm(10))

  param <- my_param()
  finalized <- dials::finalize(param, single_col)

  expect_equal(finalized$range$upper, 1L)
})
```

---

## Best Practices

1. **Use built-in finalize functions when possible**: `get_p()`, `get_n()` cover most cases

2. **Document finalization logic**: Explain in `@details` how bounds are determined

3. **Handle edge cases**: Single column, single row, empty data

4. **Ensure lower < upper**: Always check bounds are valid after finalization

5. **Use integer types appropriately**: Cast to integer with `as.integer()` for integer parameters

6. **Test with various data sizes**: Small, medium, and large datasets

7. **Consider reasonable bounds**: Avoid extreme values that don't make sense

---

## Next Steps

### Learn More

- **Quantitative parameters**: [Quantitative Parameters Guide](quantitative-parameters.md)

- **Grid integration**: [Grid Integration Guide](grid-integration.md)

- **Parameter system**: [Parameter System Overview](parameter-system.md)

### Implementation Guides

- **Extension development**: [Extension Development Guide](extension-guide.md)

- **Source development**: [Source Development Guide](source-guide.md)

---

**Last Updated:** 2026-03-31
