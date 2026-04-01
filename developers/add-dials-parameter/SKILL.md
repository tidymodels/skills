# Add Dials Parameter

**Create custom tuning parameters for hyperparameter tuning in Tidymodels**

Guide for creating new dials parameters for hyperparameter tuning. Use when a developer needs to define custom tuning parameters for models, recipes, or workflows, including quantitative parameters (continuous/integer), qualitative parameters (categorical), parameters with transformations, and data-dependent parameters requiring finalization.

---

## Two Development Contexts

This skill supports **two distinct development contexts** with different capabilities and constraints:

### 1. Extension Development (Primary Context)

**Use when:** Creating a new R package that defines custom tuning parameters

- ✅ Build new packages extending Tidymodels with custom parameters

- ✅ Use all exported dials functions with `dials::` prefix

- ❌ Cannot use internal functions (`:::`)

- 📘 **Start here:** [Extension Development Guide](references/extension-guide.md)

**Package detection:** DESCRIPTION file does NOT have `Package: dials`

### 2. Source Development (Advanced Context)

**Use when:** Contributing parameter definitions directly to tidymodels/dials repository

- ✅ Contribute parameters to dials package itself

- ✅ Access internal helper functions without `dials::` prefix

- ✅ Use validation helpers (`check_type()`, `check_range()`)

- ✅ Create custom finalize functions with `range_get()`/`range_set()`

- 📗 **Start here:** [Source Development Guide](references/source-guide.md)

**Package detection:** DESCRIPTION file has `Package: dials`

---

## Getting Started

**Before you begin**, verify your development context:

```r
# Extension development (most common)
usethis::create_package("myextension")
# DESCRIPTION will have: Package: myextension

# Source development (contributing to dials)
# Clone repository: git clone https://github.com/tidymodels/dials
# DESCRIPTION will have: Package: dials
```

---

## Overview

**dials** is the tuning parameter infrastructure package for Tidymodels. It provides:

- Parameter object definitions (quantitative and qualitative)

- Parameter range specifications and transformations

- Grid generation methods (regular, random, space-filling)

- Integration with tune, parsnip, recipes, and workflows packages

The name reflects the idea that tuning predictive models can be like turning a set of dials on a complex machine.

### Key Concepts

1. **Parameter Types**: Quantitative (numeric) vs Qualitative (categorical)
2. **Range Specification**: Fixed ranges, unknown bounds, transformations
3. **Finalization**: Resolving data-dependent parameters with training data
4. **Grid Integration**: How parameters work with grid generation functions

---

## Repository Access (Optional but Recommended)

**INSTRUCTIONS FOR CLAUDE:** Check if `repos/dials/` exists in the current working directory. Use this to guide development:

**If `repos/dials/` exists:**

- ✅ Use it as a reference throughout development

- Read source files (e.g., `repos/dials/R/param_mtry.R`) to study implementation patterns

- Read test files (e.g., `repos/dials/tests/testthat/test-param_mtry.R`) for testing patterns

- Reference these files when answering complex questions or solving problems

- Look at actual code structure, validation patterns, and edge case handling

**If `repos/dials/` does NOT exist:**

- Suggest cloning the repository using the scripts in [Repository Access Guide](references/package-repository-access.md)

- This is **optional but strongly recommended** for high-quality development

- If the user declines, reference files using GitHub URLs:

  - Format: `https://github.com/tidymodels/dials/blob/main/R/[file-name].R`

  - Example: https://github.com/tidymodels/dials/blob/main/R/param_mtry.R

  - This allows users to click through to see implementations

**When to use repository references:**

- Complex implementation questions (e.g., "How does dials handle finalization?")

- Debugging issues (compare user's code to working implementation)

- Understanding patterns (study similar parameters)

- Test design (see how dials tests edge cases)

- Architecture decisions (understand internal structure)

See [Repository Access Guide](references/package-repository-access.md) for setup instructions.

---

## Parameter Type Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│ What type of tuning parameter do you need?                 │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
   Numeric values                      Categorical choices
   (continuous or integer)             (discrete options)
        │                                       │
        ▼                                       ▼
┌─────────────────┐                    ┌─────────────────┐
│  QUANTITATIVE   │                    │   QUALITATIVE   │
│    PARAMETER    │                    │    PARAMETER    │
└─────────────────┘                    └─────────────────┘
        │                                       │
        │                                       │
        ├───────────┬────────────┐             │
        ▼           ▼            ▼             ▼
    Simple      Transformed   Data-         Examples:
    range       (log scale)   dependent     - activation()
                                             - weight_func()
        │           │            │           - prune_method()
        ▼           ▼            ▼
    Examples:   Examples:    Examples:
    - threshold  - penalty    - mtry
    - mixture    - learn_rate - num_comp
    - neighbors  - cost       - sample_size
```

**Decision guide:**

- **Quantitative, simple range**: Fixed numeric bounds, no transformation → [Quantitative Parameters](references/quantitative-parameters.md)

- **Quantitative, transformed**: Log scale or other transformation → [Quantitative Parameters](references/quantitative-parameters.md) + [Transformations](references/transformations.md)

- **Quantitative, data-dependent**: Upper bound depends on dataset → [Quantitative Parameters](references/quantitative-parameters.md) + [Data-Dependent Parameters](references/data-dependent-parameters.md)

- **Qualitative**: Discrete categorical options → [Qualitative Parameters](references/qualitative-parameters.md)

---

## Complete Examples

### Example 1: Simple Quantitative Parameter

A threshold parameter with fixed range (extension pattern):

```r
# R/param_my_threshold.R

#' Threshold value
#'
#' A threshold parameter for filtering or classification decisions.
#'
#' @param range A two-element vector with the lower and upper bounds.
#' @param trans A transformation object (default NULL for no transformation).
#'
#' @details
#' This parameter is used for models or recipes that require a threshold value.
#'
#' @examples
#' my_threshold()
#' my_threshold(range = c(0, 0.5))
#'
#' @export
my_threshold <- function(range = c(0, 1), trans = NULL) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_threshold = "Threshold Value"),
    finalize = NULL
  )
}
```

### Example 2: Transformed Quantitative Parameter

A penalty parameter on log scale (extension pattern):

```r
# R/param_my_penalty.R

#' Penalty amount
#'
#' A penalty parameter for regularization on log scale.
#'
#' @param range A two-element vector with the lower and upper bounds
#'   (in log10 units).
#' @param trans A transformation object (default log10 transformation).
#'
#' @details
#' This parameter uses a log10 transformation, so `range = c(-5, 0)`
#' represents actual penalty values from 10^-5 to 1.
#'
#' @examples
#' my_penalty()  # Range: 10^-10 to 1
#' my_penalty(range = c(-5, 0))  # Range: 10^-5 to 1
#'
#' @export
my_penalty <- function(range = c(-10, 0), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_penalty = "Penalty Amount"),
    finalize = NULL
  )
}
```

### Example 3: Data-Dependent Parameter with Built-in Finalize

A parameter with unknown upper bound (extension pattern):

```r
# R/param_num_features.R

#' Number of features
#'
#' The number of features to select, depends on data.
#'
#' @param range A two-element vector with the lower and upper bounds.
#' @param trans A transformation object (default NULL).
#'
#' @details
#' The upper bound is set to `unknown()` and must be finalized using
#' `finalize()` with training data.
#'
#' @examples
#' num_features()
#'
#' # Finalize with data
#' param <- num_features()
#' finalized <- dials::finalize(param, mtcars[, -1])
#' finalized$range$upper  # Will be number of columns
#'
#' @export
num_features <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(num_features = "# Features to Select"),
    finalize = dials::get_p  # Built-in finalize function
  )
}
```

### Example 4: Custom Finalize Function

A parameter with custom finalization logic (extension pattern):

```r
# R/param_num_initial_terms.R

#' Number of initial MARS terms
#'
#' The number of initial terms for MARS model, depends on data.
#'
#' @param range A two-element vector with the lower and upper bounds.
#' @param trans A transformation object (default NULL).
#'
#' @details
#' The upper bound is set to `unknown()` and is finalized using a custom
#' function based on the earth package formula: min(200, max(20, 2 * ncol(x))) + 1
#'
#' @examples
#' num_initial_terms()
#'
#' # Finalize with data
#' param <- num_initial_terms()
#' finalized <- dials::finalize(param, mtcars[, -1])
#' finalized$range$upper
#'
#' @export
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
  # Calculate upper bound based on number of predictors
  upper_bound <- min(200, max(20, 2 * ncol(x))) + 1
  upper_bound <- as.integer(upper_bound)

  # Get current range and update upper bound
  bounds <- dials::range_get(object)
  bounds$upper <- upper_bound
  dials::range_set(object, bounds)
}
```

### Example 5: Qualitative Parameter

A categorical parameter with options (extension pattern):

```r
# R/param_aggregation.R

#' Aggregation method
#'
#' The method to use for aggregating embeddings.
#'
#' @param values A character vector of possible methods.
#'
#' @details
#' This parameter defines how embeddings are aggregated.
#' By default, no aggregation is performed.
#'
#' @examples
#' values_aggregation
#' aggregation()
#' aggregation(values = c("none", "mean"))
#'
#' # Sample values
#' set.seed(123)
#' aggregation() %>% dials::value_sample(3)
#'
#' @export
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
```

---

## Quick Navigation

### Core Guides

- [Extension Development Guide](references/extension-guide.md) - Creating new packages with custom parameters

- [Source Development Guide](references/source-guide.md) - Contributing to dials package

### Parameter Types

- [Parameter System Overview](references/parameter-system.md) - Architecture and parameter classes

- [Quantitative Parameters](references/quantitative-parameters.md) - Creating numeric parameters

- [Qualitative Parameters](references/qualitative-parameters.md) - Creating categorical parameters

- [Transformations](references/transformations.md) - Using log scale and custom transformations

- [Data-Dependent Parameters](references/data-dependent-parameters.md) - Using unknown() and finalization

- [Grid Integration](references/grid-integration.md) - How parameters work with grids

### Source Development

- [Testing Patterns (Source)](references/testing-patterns-source.md) - dials-specific testing

- [Best Practices (Source)](references/best-practices-source.md) - dials conventions and patterns

- [Troubleshooting (Source)](references/troubleshooting-source.md) - Common issues in dials

---

## Prerequisites

### For Extension Development

Before creating custom parameters in a new package, ensure your package is properly set up:

- **R Package Structure**: See [Extension Prerequisites](references/package-extension-prerequisites.md)

- **Dependencies**: Add `dials` to DESCRIPTION Imports

- **Roxygen**: Configure documentation system

- **Testing**: Set up testthat framework

### For Source Development

To contribute parameters to dials:

1. Clone the repository:
   ```bash
   git clone https://github.com/tidymodels/dials
   cd dials
   ```

2. Install dependencies:
   ```r
   pak::pak()
   ```

3. Load the package:
   ```r
   devtools::load_all()
   ```

See [Source Development Guide](references/source-guide.md) for complete setup.

---

## Development Workflow

### Fast Iteration Cycle

For rapid parameter development:

1. **Create** parameter function in `R/` directory
2. **Load** with `devtools::load_all()`
3. **Test** interactively in console
4. **Document** with roxygen comments
5. **Verify** with tests

See [Development Workflow](references/package-development-workflow.md) for details.

### Testing Your Parameters

Essential tests for all parameters:

- **Range validation**: Parameter accepts valid ranges

- **Type checking**: Correct type enforcement

- **Grid integration**: Works with `grid_regular()`, `grid_random()`

- **Value utilities**: `value_sample()` and `value_seq()` work correctly

- **Edge cases**: Invalid inputs produce errors

See testing guides:

- Extension: [Testing Requirements](references/package-extension-requirements.md#testing-requirements)

- Source: [Testing Patterns (Source)](references/testing-patterns-source.md)

---

## Package-Specific Patterns

### File Naming (Source Development)

dials follows strict naming conventions:

- Parameter files: `R/param_[name].R`

- Test files: `tests/testthat/test-params.R` (shared), `test-constructors.R`

- One parameter per file (usually)

### Documentation Patterns

Use roxygen tags consistently:

```r
#' @inheritParams new_quant_param
#' @param range A two-element vector with the lower and upper bounds.
#' @details
#' This parameter is used for...
#' @examples
#' my_param()
#' @export
```

See [Roxygen Documentation](references/package-roxygen-documentation.md) for complete patterns.

### Creating Companion Values Vectors

For qualitative parameters, create a `values_*` vector:

```r
#' @rdname param_name
#' @export
values_param_name <- c("option1", "option2", "option3")
```

This convention is strongly recommended for consistency.

---

## Next Steps

### For Extension Developers

1. Read [Extension Development Guide](references/extension-guide.md)
2. Choose your parameter type: [Quantitative](references/quantitative-parameters.md) or [Qualitative](references/qualitative-parameters.md)
3. Implement your parameter following the examples above
4. Add tests following [Testing Requirements](references/package-extension-requirements.md#testing-requirements)
5. Document with roxygen following [Documentation Guide](references/package-roxygen-documentation.md)

### For Source Contributors

1. Read [Source Development Guide](references/source-guide.md)
2. Study existing parameters in `repos/dials/R/param_*.R`
3. Understand [Parameter System Overview](references/parameter-system.md)
4. Follow [Best Practices (Source)](references/best-practices-source.md)
5. Add tests to `tests/testthat/test-params.R`
6. Submit PR following [Source Guide](references/source-guide.md) checklist

### Related Skills

- [add-yardstick-metric](../add-yardstick-metric/SKILL.md) - Custom metrics may need custom tuning parameters

- [add-recipe-step](../add-recipe-step/SKILL.md) - Recipe steps often have tunable parameters

- [add-parsnip-model](../add-parsnip-model/SKILL.md) - Model specifications have tunable main arguments

- [add-parsnip-engine](../add-parsnip-engine/SKILL.md) - Model engines have tunable parameters

---

**Last Updated:** 2026-03-31
