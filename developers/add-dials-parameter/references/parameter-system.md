# Parameter System Overview

**Understanding dials architecture and parameter classes**

This document provides a deep dive into how dials implements the tuning parameter system for Tidymodels.

> **Note for Source Development:** If contributing to dials, you can use internal infrastructure and helper functions. See the [Source Development Guide](source-guide.md) for dials-specific patterns.

---

## Overview

The dials parameter system provides type-safe tuning parameter definitions with flexible ranges, transformations, and integration with Tidymodels workflows.

**Core implementation files:**

- Parameter constructors: `R/constructor.R` (defines `new_quant_param()` and `new_qual_param()`)

- Value generation: `R/value.R` (implements `value_sample()`, `value_seq()`, `value_set()`)

- Finalization system: `R/finalize.R` (implements `finalize()` and finalization functions)

- Parameter sets: `R/parameters.R` (implements `parameters()` for parameter collections)

**Grid generation:**

- Regular grids: `R/grid_regular.R` (factorial combinations)

- Random grids: `R/grid_random.R` (random sampling)

- Space-filling: `R/grid_latin_hypercube.R`, `R/grid_max_entropy.R`

**Test patterns:**

- Constructor tests: `tests/testthat/test-constructors.R`

- Value generation: `tests/testthat/test-value.R`

- Grid generation: `tests/testthat/test-grids.R`

---

## dials Role in Tidymodels

**dials** is the tuning parameter infrastructure package for Tidymodels. It sits between model specifications and the tuning process:

```
parsnip/recipes  →  dials  →  tune  →  workflows
(mark params)    (define)   (search)  (orchestrate)
```

### Key Responsibilities

1. **Parameter Definition**: Define what can be tuned
2. **Range Specification**: Set bounds and constraints
3. **Transformation**: Apply scales (log, reciprocal, etc.)
4. **Finalization**: Resolve data-dependent bounds
5. **Grid Generation**: Create parameter combinations for searching
6. **Value Sampling**: Generate random or sequential values

### Design Philosophy

- **Type-safe**: Parameters enforce type constraints (integer, double, character, logical)

- **Flexible ranges**: Fixed or data-dependent bounds

- **Scale-aware**: Transformations ensure proper sampling across scales

- **Integration-ready**: Seamless workflow with tune, parsnip, recipes, workflows

---

## Parameter Classes

dials provides two main parameter classes:

### 1. Quantitative Parameters (`quant_param`)

**Purpose**: Numeric tuning parameters (continuous or integer)

**Structure**:

```r
structure(
  list(
    type = "double" or "integer",
    range = list(lower = ..., upper = ...),
    inclusive = c(TRUE/FALSE, TRUE/FALSE),
    trans = NULL or transformation object,
    label = c(name = "Display Label"),
    finalize = NULL or finalize function
  ),
  class = c("quant_param", "param")
)
```

**Properties**:

- `type`: Data type - `"double"` for continuous, `"integer"` for discrete

- `range`: Two-element list with `lower` and `upper` bounds

- `inclusive`: Whether endpoints can be sampled `c(lower_inclusive, upper_inclusive)`

- `trans`: Optional transformation from scales package

- `label`: Named character for display purposes

- `finalize`: Optional function to resolve data-dependent ranges

**Common Use Cases**:

- Regularization amounts (penalty, cost)

- Learning rates and decay factors

- Number of features, neighbors, trees

- Thresholds and cutoffs

- Proportions and fractions

### 2. Qualitative Parameters (`qual_param`)

**Purpose**: Categorical tuning parameters with discrete options

**Structure**:

```r
structure(
  list(
    type = "character" or "logical",
    values = c(...),
    default = NULL or default value,
    label = c(name = "Display Label"),
    finalize = NULL
  ),
  class = c("qual_param", "param")
)
```

**Properties**:

- `type`: Data type - `"character"` for text, `"logical"` for TRUE/FALSE

- `values`: Vector of all possible options

- `default`: Default value (defaults to first value in `values` if NULL)

- `label`: Named character for display purposes

- `finalize`: Rarely used (usually NULL for categorical)

**Common Use Cases**:

- Activation functions (relu, sigmoid, tanh)

- Optimization algorithms (adam, sgd, rmsprop)

- Aggregation methods (mean, median, sum)

- Distance metrics (euclidean, manhattan, cosine)

- Model variants or modes

---

## Constructor Functions

### new_quant_param()

Creates quantitative parameters:

```r
new_quant_param(
  type,           # "double" or "integer" (required)
  range,          # Two-element vector c(lower, upper) (required)
  inclusive,      # c(lower_inclusive, upper_inclusive) (required)
  trans = NULL,   # Transformation object (optional)
  label,          # Named character c(name = "Label") (required)
  finalize = NULL # Finalize function (optional)
)
```

**Example**:

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

# Source pattern (no dials:: prefix)
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

### new_qual_param()

Creates qualitative parameters:

```r
new_qual_param(
  type,           # "character" or "logical" (required)
  values,         # Vector of options (required)
  default = NULL, # Default value (optional, uses first value if NULL)
  label,          # Named character c(name = "Label") (required)
  finalize = NULL # Usually NULL for categorical
)
```

**Example**:

```r
# Extension pattern
activation <- function(values = values_activation) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(activation = "Activation Function")
  )
}

values_activation <- c("relu", "sigmoid", "tanh", "softmax")

# Source pattern (no dials:: prefix)
activation <- function(values = values_activation) {
  new_qual_param(
    type = "character",
    values = values,
    label = c(activation = "Activation Function")
  )
}

values_activation <- c("relu", "sigmoid", "tanh", "softmax")
```

---

## Parameter Properties in Detail

### type

**For quantitative parameters**:

- `"double"`: Continuous numeric values (floating-point)

  - Examples: penalties, rates, proportions

  - Can take any value within range

- `"integer"`: Discrete whole numbers

  - Examples: counts, tree depths, neighbors

  - Values rounded to nearest integer when sampling

**For qualitative parameters**:

- `"character"`: Text-based options

  - Examples: method names, algorithm choices

  - Most common qualitative type

- `"logical"`: TRUE/FALSE options

  - Examples: binary flags, boolean settings

  - Rare in practice (usually use character with two values)

### range

**Structure**: Two-element list or vector with `lower` and `upper`

**Fixed ranges**:

```r
range = c(0, 1)          # Fixed bounds
range = c(1L, 100L)      # Integer bounds
```

**Data-dependent ranges**:

```r
range = c(1L, unknown()) # Upper bound depends on data
range = c(0.01, unknown()) # Lower fixed, upper unknown
```

See [Data-Dependent Parameters](data-dependent-parameters.md) for details on `unknown()`.

### inclusive

**Controls whether endpoints can be sampled**:

```r
inclusive = c(TRUE, TRUE)   # Both endpoints included (most common)
inclusive = c(FALSE, FALSE) # Both endpoints excluded
inclusive = c(TRUE, FALSE)  # Lower included, upper excluded
inclusive = c(FALSE, TRUE)  # Lower excluded, upper included
```

**Common patterns**:

- `c(TRUE, TRUE)`: Default for most parameters

- `c(FALSE, FALSE)`: Probabilities strictly between 0 and 1

- `c(TRUE, FALSE)`: Rates where upper bound is exclusive

**Impact on integer ranges**:

With `c(FALSE, FALSE)` and `range = c(1L, 3L)`:

- Only value 2 is valid

- Be careful with small integer ranges!

### trans

**Purpose**: Transform parameter scale for better grid coverage

**Common transformations** (from scales package):

- `transform_log10()`: Base-10 logarithm

- `transform_log()`: Natural logarithm

- `transform_log2()`: Base-2 logarithm

- `transform_log1p()`: log(1 + x), for values near zero

- `transform_reciprocal()`: 1/x

- `transform_sqrt()`: Square root

**Example with transformation**:

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

### label

**Named character for display purposes**:

```r
label = c(parameter_name = "Display Label")
```

**Conventions**:

- Name should match parameter function name

- Label uses title case

- Describe what the parameter controls

- Keep concise (under 50 characters)

**Examples**:

```r
label = c(penalty = "Amount of Regularization")
label = c(mtry = "# Randomly Selected Predictors")
label = c(learn_rate = "Learning Rate")
label = c(activation = "Activation Function")
```

### finalize

**Purpose**: Resolve data-dependent ranges with training data

**Function signature**:

```r
finalize_function <- function(object, x) {
  # object: parameter object
  # x: predictor data (matrix or data frame)
  # Returns: parameter with updated range
}
```

**Built-in finalize functions**:

- `get_p()`: Set upper bound to number of predictors (ncol)

- `get_n()`: Set upper bound to number of observations (nrow)

- `get_n_frac()`: Set upper bound to fraction of observations

- `get_log_p()`: Set upper bound to log of predictors

**Custom finalize example**:

```r
# Extension pattern
get_initial_mars_terms <- function(object, x) {
  upper_bound <- min(200, max(20, 2 * ncol(x))) + 1
  upper_bound <- as.integer(upper_bound)

  bounds <- dials::range_get(object)
  bounds$upper <- upper_bound
  dials::range_set(object, bounds)
}
```

See [Data-Dependent Parameters](data-dependent-parameters.md) for complete guide.

### values (Qualitative Only)

**Vector of all possible options**:

```r
values = c("relu", "sigmoid", "tanh", "softmax")
values = c("adam", "sgd", "rmsprop")
values = c(TRUE, FALSE)
```

**Best practice**: Create companion `values_*` vector:

```r
values_activation <- c("relu", "sigmoid", "tanh", "softmax")

activation <- function(values = values_activation) {
  dials::new_qual_param(
    type = "character",
    values = values,
    label = c(activation = "Activation Function")
  )
}
```

### default (Qualitative Only)

**Specify default value** (optional):

```r
# Explicitly set default
new_qual_param(
  type = "character",
  values = c("mean", "median", "min", "max"),
  default = "mean",  # Explicit default
  label = c(method = "Aggregation Method")
)

# If NULL, uses first value in `values`
new_qual_param(
  type = "character",
  values = c("mean", "median", "min", "max"),
  # default = "mean" implicitly (first value)
  label = c(method = "Aggregation Method")
)
```

---

## Integration with Tidymodels

### With Grid Generation

Parameters integrate with grid functions:

```r
# Regular grid
penalty_param <- penalty()
grid_regular(penalty_param, levels = 5)

# Random grid
grid_random(penalty_param, size = 10)

# Space-filling designs
grid_space_filling(penalty_param, size = 20)
```

See [Grid Integration](grid-integration.md) for complete guide.

### With tune Package

Parameters work in tuning workflows:

```r
# Mark parameters to tune
model_spec <- linear_reg(penalty = tune(), mixture = tune()) |>
  set_engine("glmnet")

# Extract parameter set
params <- extract_parameter_set_dials(model_spec)

# Update with custom parameters
params <- params |>
  update(penalty = my_penalty())

# Generate grid
grid <- grid_regular(params, levels = 5)

# Tune
tune_grid(model_spec, preprocessor, resamples, grid = grid)
```

### With parsnip Models

Parameters referenced in model specifications:

```r
# Model with tunable parameters
rand_forest(
  mtry = tune(),        # Uses dials::mtry()
  trees = tune(),       # Uses dials::trees()
  min_n = tune()        # Uses dials::min_n()
) |>
  set_engine("ranger")
```

### With recipe Steps

Parameters used in preprocessing:

```r
recipe(outcome ~ ., data = train) |>
  step_pca(all_numeric(), num_comp = tune()) |>  # Uses dials::num_comp()
  step_normalize(all_numeric())
```

### With workflows

Parameters orchestrated across entire workflow:

```r
workflow() |>
  add_model(model_spec) |>
  add_recipe(recipe_spec) |>
  extract_parameter_set_dials() |>
  # Returns all tunable parameters from model + recipe
  update(
    mtry = mtry(range = c(1, 10)),
    num_comp = num_comp(range = c(1, 5))
  )
```

---

## Design Considerations

### When to Make a Parameter Quantitative vs Qualitative

**Use quantitative when:**

- Parameter has natural ordering (more vs less)

- Values form a continuous or discrete numeric range

- Interpolation makes sense

- Grid search benefits from regular spacing

**Examples**: penalty, learning rate, number of trees, threshold

**Use qualitative when:**

- Parameter represents discrete categorical choices

- No natural ordering exists

- Values are non-numeric or symbolic

- Each option is fundamentally different

**Examples**: activation function, optimizer, distance metric, aggregation method

### Choosing Ranges

**Principles**:

1. **Cover typical use cases**: Default range should work for most problems
2. **Allow extremes**: Users can narrow range for specific cases
3. **Use domain knowledge**: Consult literature and practitioners
4. **Consider scale**: Wide ranges often benefit from transformations

**Examples**:

```r
# Penalty: wide range on log scale
range = c(-10, 0)  # 10^-10 to 1

# Learning rate: moderate range on log scale
range = c(-5, -1)  # 10^-5 to 0.1

# Number of neighbors: small integer range
range = c(1L, 15L)

# Mixture: probability on linear scale
range = c(0, 1)
```

### Choosing Transformations

**Use transformations when:**

- Parameter spans multiple orders of magnitude

- Equal steps in transformed space are more meaningful

- Literature commonly discusses parameter on transformed scale

- Grid coverage needs to be uniform in transformed space

**Examples**:

- **Penalties**: Log scale (10^-6, 10^-3, 1 are equally spaced)

- **Learning rates**: Log scale (magnitudes matter more than absolute differences)

- **Counts**: Usually linear (1, 2, 3, 4 are naturally equally spaced)

- **Proportions**: Usually linear (0.2, 0.4, 0.6, 0.8 are meaningful)

### Data-Dependent vs Fixed Ranges

**Use fixed ranges when:**

- Bounds are universal across datasets

- Domain knowledge provides clear limits

- Parameter behavior doesn't depend on data size

**Examples**: penalty (0 to ∞), mixture (0 to 1), activation (fixed set)

**Use data-dependent ranges when:**

- Upper bound depends on dataset characteristics

- Number of features/observations matters

- Parameter meaningfulness depends on data dimensions

**Examples**: mtry (≤ # predictors), num_comp (≤ # columns), sample_size (≤ # rows)

---

## Next Steps

### Learn More

- **Quantitative parameters**: [Quantitative Parameters Guide](quantitative-parameters.md)

- **Qualitative parameters**: [Qualitative Parameters Guide](qualitative-parameters.md)

- **Transformations**: [Transformations Guide](transformations.md)

- **Data-dependent ranges**: [Data-Dependent Parameters Guide](data-dependent-parameters.md)

- **Grid integration**: [Grid Integration Guide](grid-integration.md)

### Implementation Guides

- **Extension development**: [Extension Development Guide](extension-guide.md)

- **Source development**: [Source Development Guide](source-guide.md)

---

**Last Updated:** 2026-03-31
