# Extension Development Guide

**Creating custom tuning parameters in new R packages**

This guide is for developers creating new R packages that define custom tuning parameters using dials.

---

## When to Use This Guide

**Use extension development when:**

- Creating a new R package with custom tuning parameters

- Your package DESCRIPTION has `Package: yourpackage` (NOT `Package: dials`)

- You need to define parameters for custom models, recipe steps, or workflows

- You want to extend Tidymodels with domain-specific tuning parameters

**Do NOT use this guide when:**

- Contributing parameters directly to tidymodels/dials repository

- Your DESCRIPTION has `Package: dials`

- → Use [Source Development Guide](source-guide.md) instead

---

## Prerequisites

Before creating custom parameters, ensure your R package is properly set up:

**📘 See [Extension Prerequisites](package-extension-prerequisites.md) for complete setup instructions.**

Key requirements:

- R package structure created with `usethis::create_package()`

- DESCRIPTION file configured with dependencies

- Roxygen2 documentation system enabled

- testthat testing framework installed

---

## Key Constraints

When developing in an extension package:

### ✅ You CAN:

- Use all exported dials functions

- Create quantitative and qualitative parameters

- Define custom finalize functions

- Use transformations from scales package

- Test parameters with grid generation functions

### ❌ You CANNOT:

- Use internal dials functions with `:::`

- Access unexported helper functions like `check_type()` or `check_range()`

- Directly manipulate parameter internals

### 📋 You MUST:

- Always use `dials::` prefix for all dials functions

- Export your parameter functions with `@export`

- Document with roxygen2 comments

- Test parameter behavior with grid functions

---

## Step-by-Step Implementation

### Step 1: Choose Parameter Type

Decide whether you need a quantitative or qualitative parameter:

**Quantitative (`dials::new_quant_param()`)**: Numeric values (continuous or integer)

- Examples: penalties, thresholds, counts, rates

- Has range, type (double/integer), optional transformation

- Can have data-dependent bounds with `dials::unknown()`

**Qualitative (`dials::new_qual_param()`)**: Categorical options

- Examples: methods, algorithms, activation functions

- Has discrete values, type (character/logical)

- Rarely needs finalization

See [Parameter System Overview](parameter-system.md) for detailed comparison.

### Step 2: Create Parameter Function

Create a new file in your package's `R/` directory:

```r
# R/param_my_parameter.R

#' Parameter description
#'
#' Detailed description of what this parameter controls.
#'
#' @param range A two-element vector with the lower and upper bounds.
#' @param trans A transformation object (default NULL).
#'
#' @details
#' Additional details about usage and behavior.
#'
#' @examples
#' my_parameter()
#' my_parameter(range = c(0, 10))
#'
#' @export
my_parameter <- function(range = c(0, 1), trans = NULL) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_parameter = "Parameter Label"),
    finalize = NULL
  )
}
```

### Step 3: Add Roxygen Documentation

Include complete roxygen documentation:

```r
#' @param range A two-element vector with bounds
#' @param trans A transformation object (default NULL)
#' @details
#' Describe when and how to use this parameter.
#' @examples
#' # Show basic usage
#' my_parameter()
#'
#' # Show with custom range
#' my_parameter(range = c(1, 10))
#'
#' # Show with grid generation
#' dials::grid_regular(my_parameter(), levels = 5)
#' @export
```

See [Roxygen Documentation](package-roxygen-documentation.md) for complete patterns.

### Step 4: Export Parameter

The `@export` roxygen tag makes your parameter available to users:

```r
#' @export
my_parameter <- function(...) {
  # implementation
}
```

After adding or modifying documentation:

```r
devtools::document()  # Generates NAMESPACE and .Rd files
```

### Step 5: Test Parameter

Create tests in `tests/testthat/test-my-parameter.R`:

```r
test_that("my_parameter creates valid parameter", {
  param <- my_parameter()

  expect_s3_class(param, "quant_param")
  expect_equal(param$type, "double")
  expect_equal(param$range$lower, 0)
  expect_equal(param$range$upper, 1)
})

test_that("my_parameter works with grid functions", {
  param <- my_parameter()

  grid <- dials::grid_regular(param, levels = 5)
  expect_equal(nrow(grid), 5)
  expect_true(all(grid$my_parameter >= 0 & grid$my_parameter <= 1))
})
```

See [Testing Requirements](package-extension-requirements.md#testing-requirements) for complete testing guide.

---

## Complete Examples

### Example 1: Simple Quantitative Parameter

A basic parameter with fixed range:

```r
# R/param_threshold.R

#' Classification threshold
#'
#' The threshold value for binary classification.
#'
#' @param range A two-element vector with the lower and upper bounds.
#' @param trans A transformation object (default NULL).
#'
#' @details
#' This parameter controls the decision threshold for converting
#' predicted probabilities to class predictions.
#'
#' @examples
#' threshold()
#' threshold(range = c(0.3, 0.7))
#'
#' # Generate grid
#' dials::grid_regular(threshold(), levels = 10)
#'
#' @export
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
```

### Example 2: Transformed Quantitative Parameter

A parameter with log transformation:

```r
# R/param_regularization.R

#' Regularization strength
#'
#' The strength of regularization on log scale.
#'
#' @param range A two-element vector with bounds (in log10 units).
#' @param trans A transformation object (default log10).
#'
#' @details
#' This parameter uses log10 transformation. A range of c(-5, 0)
#' represents actual values from 10^-5 to 1.
#'
#' @examples
#' regularization()
#' regularization(range = c(-3, 0))
#'
#' # Sample values
#' set.seed(123)
#' dials::value_sample(regularization(), n = 5)
#'
#' @export
regularization <- function(range = c(-5, 0),
                          trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(regularization = "Regularization Strength"),
    finalize = NULL
  )
}
```

See [Transformations](transformations.md) for detailed guide on using transformations.

### Example 3: Data-Dependent Quantitative Parameter

A parameter with unknown upper bound:

```r
# R/param_max_features.R

#' Maximum features to select
#'
#' The maximum number of features to select from data.
#'
#' @param range A two-element vector with bounds.
#' @param trans A transformation object (default NULL).
#'
#' @details
#' The upper bound is unknown and must be finalized with training data.
#' Uses `dials::get_p` to set upper bound to number of predictors.
#'
#' @examples
#' max_features()
#'
#' # Finalize with data
#' param <- max_features()
#' finalized <- dials::finalize(param, mtcars[, -1])
#' finalized$range$upper
#'
#' @export
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
```

See [Data-Dependent Parameters](data-dependent-parameters.md) for complete guide on finalization.

### Example 4: Qualitative Parameter

A categorical parameter with discrete options:

```r
# R/param_method.R

#' Aggregation method
#'
#' The method to use for aggregating results.
#'
#' @param values A character vector of possible methods.
#'
#' @details
#' This parameter defines how results are aggregated across samples.
#'
#' @examples
#' values_method
#' method()
#' method(values = c("mean", "median"))
#'
#' # Sample random values
#' set.seed(123)
#' dials::value_sample(method(), n = 3)
#'
#' @export
method <- function(values = values_method) {
  dials::new_qual_param(
    type = "character",
    values = values,
    default = "mean",
    label = c(method = "Aggregation Method")
  )
}

#' @rdname method
#' @export
values_method <- c("mean", "median", "min", "max")
```

See [Qualitative Parameters](qualitative-parameters.md) for complete guide.

---

## Common Patterns

### Pattern 1: Integer Parameters with Bounded Range

For count-based parameters:

```r
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
```

### Pattern 2: Probability Parameters

For parameters between 0 and 1:

```r
dropout_rate <- function(range = c(0, 0.5), trans = NULL) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(FALSE, FALSE),  # Strictly between bounds
    trans = trans,
    label = c(dropout_rate = "Dropout Rate"),
    finalize = NULL
  )
}
```

### Pattern 3: Log-Scale Parameters

For parameters spanning multiple orders of magnitude:

```r
learning_rate <- function(range = c(-5, -1),
                         trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(learning_rate = "Learning Rate"),
    finalize = NULL
  )
}
```

### Pattern 4: Qualitative with Values Vector

For categorical parameters:

```r
#' @export
optimizer <- function(values = values_optimizer) {
  dials::new_qual_param(
    type = "character",
    values = values,
    default = "adam",
    label = c(optimizer = "Optimizer")
  )
}

#' @rdname optimizer
#' @export
values_optimizer <- c("adam", "sgd", "rmsprop", "adagrad")
```

---

## Development Workflow

### Fast Iteration Cycle

1. **Create** parameter function in `R/` directory
2. **Load** package with `devtools::load_all()`
3. **Test** interactively in console:
   ```r
   my_param()
   dials::value_sample(my_param(), 5)
   dials::grid_regular(my_param(), levels = 3)
   ```
4. **Document** with roxygen comments
5. **Generate** docs with `devtools::document()`
6. **Test** with `devtools::test()`

See [Development Workflow](package-development-workflow.md) for detailed workflow patterns.

---

## Package Integration

### Adding dials to DESCRIPTION

Add dials to your package imports:

```r
usethis::use_package("dials", type = "Imports")
```

Or manually in DESCRIPTION:

```yaml
Imports:
    dials
```

See [Package Imports](package-imports.md) for managing dependencies.

### Using Parameters in Your Package

Parameters work seamlessly with tune workflows:

```r
# In your model specification
my_model_spec <- parsnip::linear_reg(penalty = tune::tune()) |>
  parsnip::set_engine("glmnet")

# Extract and update parameter
params <- workflows::extract_parameter_set_dials(workflow_obj)
params <- params |>
  recipes::update(penalty = regularization())  # Your custom parameter

# Generate grid
grid <- dials::grid_regular(params, levels = 5)
```

---

## Testing

### Essential Tests

All parameters should have tests for:

1. **Parameter creation**: Valid parameter object
2. **Range validation**: Accepts custom ranges
3. **Grid integration**: Works with grid functions
4. **Value utilities**: `value_sample()` and `value_seq()` work
5. **Edge cases**: Invalid inputs produce errors

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

See [Testing Requirements](package-extension-requirements.md#testing-requirements) for comprehensive testing guide.

---

## Best Practices

### General Best Practices

**📘 See [Best Practices](package-extension-requirements.md#best-practices) for universal R package patterns.**

Key practices:

- Use base pipe `|>` not `%>%`

- Prefer for-loops over `purrr::map()`

- Use `cli::cli_abort()` for errors

- Follow tidyverse style guide

### Parameter-Specific Best Practices

1. **Choose meaningful names**: `learning_rate()` not `lr()`
2. **Use appropriate ranges**: Match typical use cases
3. **Add transformations when needed**: Log scale for parameters spanning orders of magnitude
4. **Document finalization**: Explain data-dependent parameters clearly
5. **Create values vectors**: For qualitative parameters, use `values_*` naming
6. **Test grid integration**: Ensure parameters work with all grid functions
7. **Provide examples**: Show parameter in realistic tune workflow

---

## Troubleshooting

### Common Issues

**📘 See [Common Issues & Solutions](package-extension-requirements.md#common-issues-solutions) for general troubleshooting.**

### Parameter-Specific Issues

**Issue: "could not find function 'new_quant_param'"**

Solution: Use `dials::new_quant_param()` with package prefix

**Issue: "range must have length 2"**

Solution: Provide two-element vector: `range = c(lower, upper)`

**Issue: "values must be character"**

Solution: For qualitative parameters, ensure `type = "character"` matches `values` type

**Issue: Grid generation produces unexpected values**

Solution: Check if transformation is applied correctly. Range should be in transformed units.

**Issue: Parameter won't finalize with data**

Solution: Ensure finalize function is provided and has correct signature: `function(object, x)`

**Issue: Integer range produces no values**

Solution: Check `inclusive` argument. With `c(FALSE, FALSE)` and small integer range, no valid values may exist.

---

## Next Steps

1. **Choose your parameter type**:

   - [Quantitative Parameters](quantitative-parameters.md) for numeric values

   - [Qualitative Parameters](qualitative-parameters.md) for categorical options

2. **Add advanced features**:

   - [Transformations](transformations.md) for log-scale parameters

   - [Data-Dependent Parameters](data-dependent-parameters.md) for unknown bounds

3. **Integrate with tune**:

   - [Grid Integration](grid-integration.md) for grid generation patterns

4. **Learn from examples**:

   - Study dials package: `repos/dials/R/param_*.R`

   - Read tidymodels.org tutorial on custom parameters

---

**Last Updated:** 2026-03-31
