# Grid Integration

**How parameters work with grid generation and tune workflows**

This guide covers how dials parameters integrate with grid generation functions and tune workflows for hyperparameter tuning.

> **Note for Source Development:** If contributing to dials, you can use internal grid generation utilities. See the [Source Development Guide](../source-guide.md) for dials-specific patterns.

---

## Overview

dials parameters are designed to work seamlessly with:

1. **Grid generation**: `grid_regular()`, `grid_random()`, `grid_space_filling()`
2. **Value utilities**: `value_sample()`, `value_seq()`
3. **Parameter sets**: `parameters()` for combining multiple parameters
4. **Workflow extraction**: `extract_parameter_set_dials()` from workflows
5. **Tuning functions**: `tune_grid()`, `tune_bayes()` from tune package

**Grid generation implementations:**
- Regular grids: `R/grid_regular.R` (factorial combinations with `value_seq()`)
- Random sampling: `R/grid_random.R` (random sampling with `value_sample()`)
- Latin hypercube: `R/grid_latin_hypercube.R` (space-filling design)
- Maximum entropy: `R/grid_max_entropy.R` (space-filling design)

**Parameter sets:**
- Parameter collections: `R/parameters.R` (implements `parameters()` for combining)
- Workflow extraction: `R/extract_parameter_set_dials.R` (extracts params from workflows)

**Test patterns:**
- Grid tests: `tests/testthat/test-grids.R` (grid generation validation)
- Parameter set tests: `tests/testthat/test-parameters.R` (collection behavior)

---

## Grid Generation Functions

### grid_regular()

**Create factorial designs with regular spacing**

```r
grid_regular(param1, param2, ..., levels = 3, filter = NULL)
```

**For single parameter**:

```r
penalty_param <- penalty()
grid <- dials::grid_regular(penalty_param, levels = 5)
grid
#> # A tibble: 5 × 1
#>      penalty
#>        <dbl>
#> 1 0.0000000001  # 10^-10
#> 2 0.00001       # 10^-7.5
#> 3 0.001         # 10^-5
#> 4 0.01          # 10^-2.5
#> 5 1             # 10^0
```

**For multiple parameters**:

```r
params <- dials::parameters(
  penalty = penalty(),
  mixture = mixture()
)

grid <- dials::grid_regular(params, levels = 3)
grid
#> # A tibble: 9 × 2
#>      penalty mixture
#>        <dbl>   <dbl>
#> 1 1.00e-10    0
#> 2 1.00e-10    0.5
#> 3 1.00e-10    1
#> 4 1.00e-05    0
#> 5 1.00e-05    0.5
#> 6 1.00e-05    1
#> 7 1.00e+00    0
#> 8 1.00e+00    0.5
#> 9 1.00e+00    1
```

**Different levels per parameter**:

```r
grid <- dials::grid_regular(params, levels = c(5, 3))
# 5 levels for penalty, 3 levels for mixture
# Total grid size: 5 × 3 = 15
```

### grid_random()

**Create random grid with uniform sampling**

```r
grid_random(param1, param2, ..., size = 5, filter = NULL)
```

**For single parameter**:

```r
set.seed(123)
penalty_param <- penalty()
grid <- dials::grid_random(penalty_param, size = 5)
grid
#> # A tibble: 5 × 1
#>      penalty
#>        <dbl>
#> 1   0.000204
#> 2   0.130329
#> 3   0.000000100
#> 4   0.524148
#> 5   0.939941
```

**For multiple parameters**:

```r
set.seed(123)
params <- dials::parameters(
  penalty = penalty(),
  mixture = mixture()
)

grid <- dials::grid_random(params, size = 10)
grid
#> # A tibble: 10 × 2
#>       penalty mixture
#>         <dbl>   <dbl>
#>  1   0.000204   0.788
#>  2   0.130329   0.409
#>  3   0.000000100 0.883
#>  # ... with 7 more rows
```

### grid_space_filling()

**Create space-filling designs (Latin hypercube, max entropy)**

```r
grid_space_filling(param1, param2, ..., size = 5, type = "latin_hypercube")
```

**Options for `type`**:

- `"latin_hypercube"`: Latin hypercube sampling (default)
- `"max_entropy"`: Maximum entropy design
- `"audze_eglais"`: Audze-Eglais criterion
- `"uniform"`: Uniform design

**Example**:

```r
set.seed(123)
params <- dials::parameters(
  penalty = penalty(),
  mixture = mixture()
)

grid <- dials::grid_space_filling(params, size = 10, type = "latin_hypercube")
grid
#> # A tibble: 10 × 2
#>       penalty mixture
#>         <dbl>   <dbl>
#>  1   0.00000272  0.550
#>  2   0.0000000344 0.989
#>  3   0.391       0.156
#>  # ... with 7 more rows
```

**Benefits**:

- Better coverage of parameter space than random
- Avoids clustering of grid points
- Good for small grid sizes

---

## Parameter Value Utilities

### value_sample()

**Generate random values from a parameter**

```r
value_sample(object, n, original = TRUE)
```

**For quantitative parameters**:

```r
penalty_param <- penalty()

set.seed(123)
samples <- dials::value_sample(penalty_param, n = 5)
samples
#> [1] 2.042e-04 1.303e-01 1.000e-10 5.241e-01 9.400e-01

# Uniformly distributed in transformed (log10) space
```

**For qualitative parameters**:

```r
activation_param <- activation()

set.seed(456)
samples <- dials::value_sample(activation_param, n = 3)
samples
#> [1] "tanh"    "relu"    "sigmoid"

# Randomly samples from available values
```

### value_seq()

**Generate regular sequence of values from a parameter**

```r
value_seq(object, n, original = TRUE)
```

**For quantitative parameters**:

```r
penalty_param <- penalty()

seq_vals <- dials::value_seq(penalty_param, n = 5)
seq_vals
#> [1] 1e-10  1e-07  1e-04  1e-01  1e+00

# Regular spacing in transformed space
```

**For qualitative parameters**:

```r
activation_param <- activation()

seq_vals <- dials::value_seq(activation_param, n = 3)
seq_vals
#> [1] "relu"    "sigmoid" "tanh"

# Returns first n values (or cycles if n > length)
```

---

## How Parameter Properties Affect Grids

### range: Determines Sampling Bounds

```r
# Wide range
penalty_wide <- penalty(range = c(-10, 0))
grid <- dials::grid_regular(penalty_wide, levels = 5)
range(grid$penalty)
#> [1] 1e-10  1e+00

# Narrow range
penalty_narrow <- penalty(range = c(-5, -2))
grid <- dials::grid_regular(penalty_narrow, levels = 5)
range(grid$penalty)
#> [1] 1e-05  1e-02
```

### trans: Affects Value Distribution

```r
# With transformation (log scale)
penalty_log <- penalty(range = c(-10, 0), trans = scales::transform_log10())
grid <- dials::grid_regular(penalty_log, levels = 5)
grid$penalty
#> [1] 1e-10  1e-07  1e-04  1e-01  1e+00
#> Even spacing on log scale

# Without transformation (linear scale)
penalty_linear <- penalty(range = c(0.0000000001, 1), trans = NULL)
grid <- dials::grid_regular(penalty_linear, levels = 5)
grid$penalty
#> [1] 0.0000000001  0.2500000000  0.5000000000  0.7500000000  1.0000000000
#> Linear spacing (poor coverage of small values)
```

### type: Determines Granularity

```r
# Double: continuous values
threshold_double <- threshold()
grid <- dials::grid_regular(threshold_double, levels = 5)
grid$threshold
#> [1] 0.00 0.25 0.50 0.75 1.00

# Integer: discrete values
num_trees_int <- num_trees(range = c(1L, 100L))
grid <- dials::grid_regular(num_trees_int, levels = 5)
grid$num_trees
#> [1]   1  25  50  75 100
```

### values: Enumerates Options (Qualitative)

```r
# All values
activation_param <- activation()  # 8 options
grid <- dials::grid_regular(activation_param)
nrow(grid)
#> [1] 8

# Subset of values
activation_subset <- activation(values = c("relu", "sigmoid", "tanh"))
grid <- dials::grid_regular(activation_subset)
nrow(grid)
#> [1] 3
```

### inclusive: Controls Endpoint Inclusion

```r
# Both endpoints included
param_inclusive <- threshold(range = c(0, 1))  # inclusive = c(TRUE, TRUE)
seq_vals <- dials::value_seq(param_inclusive, n = 5)
seq_vals
#> [1] 0.00 0.25 0.50 0.75 1.00
#> Includes 0 and 1

# Both endpoints excluded
param_exclusive <- new_quant_param(
  type = "double",
  range = c(0, 1),
  inclusive = c(FALSE, FALSE),
  ...
)
seq_vals <- dials::value_seq(param_exclusive, n = 5)
seq_vals
#> [1] 0.1 0.3 0.5 0.7 0.9
#> Excludes 0 and 1
```

---

## Parameter Sets

### Creating Parameter Sets with parameters()

Combine multiple parameters into a set:

```r
param_set <- dials::parameters(
  penalty = penalty(),
  mixture = mixture(),
  num_trees = num_trees(range = c(100L, 1000L))
)

param_set
#> Collection of 3 parameters for tuning
#>        id   parameter type  object class
#>   penalty      penalty nparam[+] quant_param
#>   mixture      mixture nparam[+] quant_param
#> num_trees    num_trees nparam[+] quant_param
```

### Generating Grids from Parameter Sets

```r
# Regular grid (factorial design)
grid <- dials::grid_regular(param_set, levels = 3)
nrow(grid)
#> [1] 27  # 3 × 3 × 3

# Random grid
grid <- dials::grid_random(param_set, size = 20)
nrow(grid)
#> [1] 20

# Space-filling grid
grid <- dials::grid_space_filling(param_set, size = 15)
nrow(grid)
#> [1] 15
```

### Updating Parameter Ranges

```r
param_set <- dials::parameters(
  penalty = penalty(),
  mixture = mixture()
)

# Update penalty range
param_set_updated <- param_set |>
  recipes::update(penalty = penalty(range = c(-5, -1)))

param_set_updated
#> Collection of 2 parameters for tuning
#>       id parameter type  object class
#>  penalty   penalty nparam[+] quant_param  # Updated range
#>  mixture   mixture nparam[+] quant_param
```

---

## Extracting Parameters from Workflows

### From Model Specifications

```r
# Define model with tunable parameters
rf_spec <- parsnip::rand_forest(
  mtry = tune::tune(),
  trees = tune::tune(),
  min_n = tune::tune()
) |>
  parsnip::set_engine("ranger") |>
  parsnip::set_mode("regression")

# Extract parameter set
params <- parsnip::extract_parameter_set_dials(rf_spec)
params
#> Collection of 3 parameters for tuning
#>      id parameter type  object class
#>    mtry      mtry nparam[?] quant_param  # Needs finalization
#>   trees     trees nparam[+] quant_param
#>   min_n     min_n nparam[+] quant_param
```

### From Workflows

```r
# Create workflow
wf <- workflows::workflow() |>
  workflows::add_model(rf_spec) |>
  workflows::add_formula(mpg ~ .)

# Extract parameters from entire workflow
params <- workflows::extract_parameter_set_dials(wf)
params
#> Collection of 3 parameters for tuning
#>      id parameter type  object class
#>    mtry      mtry nparam[?] quant_param
#>   trees     trees nparam[+] quant_param
#>   min_n     min_n nparam[+] quant_param
```

### Finalizing Extracted Parameters

```r
# Finalize data-dependent parameters
params_finalized <- dials::finalize(params, mtcars[, -1])

# Update ranges
params_updated <- params_finalized |>
  recipes::update(
    mtry = mtry(range = c(1, 5)),
    trees = trees(range = c(500, 1500))
  )

# Generate grid
grid <- dials::grid_regular(params_updated, levels = 3)
```

---

## Complete Workflow Examples

### Example 1: Single Parameter Grid Search

```r
# Define parameter
penalty_param <- penalty()

# Generate grid
grid <- dials::grid_regular(penalty_param, levels = 10)

# Define model
model_spec <- parsnip::linear_reg(penalty = tune::tune()) |>
  parsnip::set_engine("glmnet")

# Create workflow
wf <- workflows::workflow() |>
  workflows::add_model(model_spec) |>
  workflows::add_formula(mpg ~ .)

# Tune
library(tune)
library(rsample)

cv_folds <- vfold_cv(mtcars, v = 5)
results <- tune_grid(wf, resamples = cv_folds, grid = grid)

# Best parameters
show_best(results, metric = "rmse")
```

### Example 2: Multi-Parameter Random Search

```r
# Define parameters
param_set <- dials::parameters(
  penalty = penalty(),
  mixture = mixture()
)

# Generate random grid
set.seed(123)
grid <- dials::grid_random(param_set, size = 25)

# Define model
model_spec <- parsnip::linear_reg(
  penalty = tune::tune(),
  mixture = tune::tune()
) |>
  parsnip::set_engine("glmnet")

# Workflow and tune
wf <- workflows::workflow() |>
  workflows::add_model(model_spec) |>
  workflows::add_formula(mpg ~ .)

results <- tune_grid(wf, resamples = cv_folds, grid = grid)
```

### Example 3: Automatic Grid with Finalization

```r
# Model with data-dependent parameter
rf_spec <- parsnip::rand_forest(
  mtry = tune::tune(),
  trees = tune::tune()
) |>
  parsnip::set_engine("ranger") |>
  parsnip::set_mode("regression")

# Workflow
wf <- workflows::workflow() |>
  workflows::add_model(rf_spec) |>
  workflows::add_formula(mpg ~ .)

# tune_grid automatically finalizes mtry
results <- tune_grid(
  wf,
  resamples = cv_folds,
  grid = 20  # Generates random grid, finalizes mtry
)
```

### Example 4: Custom Parameters in Grid

```r
# Extract default parameters
params <- workflows::extract_parameter_set_dials(wf)

# Finalize and customize
params_custom <- dials::finalize(params, mtcars[, -1]) |>
  recipes::update(
    mtry = mtry(range = c(2, 8)),
    trees = trees(range = c(100, 500))
  )

# Generate space-filling grid
grid <- dials::grid_space_filling(params_custom, size = 30)

# Tune with custom grid
results <- tune_grid(wf, resamples = cv_folds, grid = grid)
```

### Example 5: Recipe + Model Parameters

```r
# Recipe with tunable step
rec <- recipes::recipe(mpg ~ ., data = mtcars) |>
  recipes::step_pca(all_numeric_predictors(), num_comp = tune::tune())

# Model with tunable parameters
model_spec <- parsnip::rand_forest(mtry = tune::tune()) |>
  parsnip::set_engine("ranger") |>
  parsnip::set_mode("regression")

# Workflow
wf <- workflows::workflow() |>
  workflows::add_recipe(rec) |>
  workflows::add_model(model_spec)

# Extract all parameters (from recipe + model)
params <- workflows::extract_parameter_set_dials(wf)
params
#> Collection of 2 parameters for tuning
#>        id parameter type  object class
#>  num_comp  num_comp nparam[?] quant_param
#>      mtry      mtry nparam[?] quant_param

# Finalize and tune
params_finalized <- dials::finalize(params, mtcars[, -1])
grid <- dials::grid_regular(params_finalized, levels = 3)
results <- tune_grid(wf, resamples = cv_folds, grid = grid)
```

---

## Extension vs Source Patterns

### Extension Development

**Use `dials::` prefix for all functions**:

```r
# Create parameters
penalty_param <- penalty()
mixture_param <- mixture()

# Parameter set
param_set <- dials::parameters(
  penalty = penalty_param,
  mixture = mixture_param
)

# Generate grids
grid1 <- dials::grid_regular(param_set, levels = 3)
grid2 <- dials::grid_random(param_set, size = 20)
grid3 <- dials::grid_space_filling(param_set, size = 15)

# Value utilities
samples <- dials::value_sample(penalty_param, n = 10)
seq_vals <- dials::value_seq(penalty_param, n = 5)

# Finalize
finalized <- dials::finalize(param_set, train_data)

# Update
updated <- finalized |>
  recipes::update(penalty = penalty(range = c(-5, -1)))
```

### Source Development

**No `dials::` prefix needed**:

```r
# Create parameters
penalty_param <- penalty()
mixture_param <- mixture()

# Parameter set
param_set <- parameters(
  penalty = penalty_param,
  mixture = mixture_param
)

# Generate grids
grid1 <- grid_regular(param_set, levels = 3)
grid2 <- grid_random(param_set, size = 20)
grid3 <- grid_space_filling(param_set, size = 15)

# Value utilities
samples <- value_sample(penalty_param, n = 10)
seq_vals <- value_seq(penalty_param, n = 5)

# Finalize
finalized <- finalize(param_set, train_data)

# Update (recipes:: still needed)
updated <- finalized |>
  recipes::update(penalty = penalty(range = c(-5, -1)))
```

---

## Best Practices

### Grid Size Selection

**Regular grids**: Grows exponentially with parameters
- 2 parameters × 5 levels = 25 combinations
- 3 parameters × 5 levels = 125 combinations
- 4 parameters × 5 levels = 625 combinations

**Recommendation**:
- Use fewer levels for many parameters
- Consider random or space-filling for 4+ parameters

### Grid Type Selection

**Use `grid_regular()` when**:
- Few parameters (1-3)
- Want complete factorial coverage
- Interpretable grid structure

**Use `grid_random()` when**:
- Many parameters (4+)
- Want to control total grid size
- Computational budget is fixed

**Use `grid_space_filling()` when**:
- Need better coverage than random
- Small grid sizes
- Quality over quantity

### Parameter Combinations

**Avoid unnecessary combinations**:

```r
# Use filter to exclude illogical combinations
grid <- dials::grid_regular(param_set, levels = 5, filter = penalty > 0.001)
```

### Transformation Awareness

**Verify grid coverage**:

```r
param <- penalty()
grid <- dials::grid_regular(param, levels = 5)

# Check transformed values
log10(grid$penalty)
#> Should be evenly spaced
```

---

## Troubleshooting

### "Can't generate grid with unknown() bound"

```r
# Problem: Parameter not finalized
param <- mtry()
grid <- dials::grid_regular(param, levels = 5)
#> Error: Can't generate grid with unknown values

# Solution: Finalize first
param_finalized <- dials::finalize(param, train_data)
grid <- dials::grid_regular(param_finalized, levels = 5)
```

### "Grid size is too large"

```r
# Problem: Too many parameter combinations
params <- dials::parameters(p1, p2, p3, p4, p5)
grid <- dials::grid_regular(params, levels = 5)
#> 5^5 = 3125 combinations!

# Solution: Use random or space-filling
grid <- dials::grid_random(params, size = 50)
grid <- dials::grid_space_filling(params, size = 50)
```

### "Integer parameter produces no values"

```r
# Problem: Exclusive bounds on small integer range
param <- new_quant_param(
  type = "integer",
  range = c(1L, 3L),
  inclusive = c(FALSE, FALSE),  # Only value 2 is valid!
  ...
)

# Solution: Use inclusive bounds or wider range
param <- new_quant_param(
  type = "integer",
  range = c(1L, 3L),
  inclusive = c(TRUE, TRUE),  # 1, 2, 3 all valid
  ...
)
```

---

## Next Steps

### Learn More

- **Quantitative parameters**: [Quantitative Parameters Guide](quantitative-parameters.md)
- **Qualitative parameters**: [Qualitative Parameters Guide](qualitative-parameters.md)
- **Data-dependent parameters**: [Data-Dependent Parameters Guide](data-dependent-parameters.md)
- **Transformations**: [Transformations Guide](transformations.md)

### Implementation Guides

- **Extension development**: [Extension Development Guide](extension-guide.md)
- **Source development**: [Source Development Guide](source-guide.md)

### External Resources

- [tune package documentation](https://tune.tidymodels.org/)
- [Grid search tutorial](https://www.tidymodels.org/learn/work/tune-svm/)
- [Bayesian optimization](https://www.tidymodels.org/learn/work/bayes-opt/)

---

**Last Updated:** 2026-03-31
