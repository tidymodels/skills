# Source Development Guide

**Contributing parameter definitions to tidymodels/dials repository**

This guide is for developers contributing parameters directly to the dials package via pull requests.

---

## When to Use This Guide

**Use source development when:**

- Contributing parameters to tidymodels/dials repository
- Your working directory has `Package: dials` in DESCRIPTION
- You're adding universal parameters like `num_features()` to dials itself
- You need to use internal helper functions

**Do NOT use this guide when:**

- Creating a new R package with custom parameters
- Your DESCRIPTION has `Package: yourpackage`
- → Use [Extension Development Guide](extension-guide.md) instead

---

## Prerequisites

### Clone the Repository

```bash
git clone https://github.com/tidymodels/dials
cd dials
```

### Install Dependencies

```r
# Install development dependencies
pak::pak()

# Or using remotes
remotes::install_deps(dependencies = TRUE)
```

### Load the Package

```r
# Load all functions for interactive development
devtools::load_all()
```

### Verify Setup

```r
# Check that you can access internal functions
ls("package:dials", all.names = TRUE)

# Test a simple parameter
penalty()
```

---

## Understanding dials Architecture

### File Organization

dials follows strict file naming conventions:

```
R/
├── aaa_*.R              # Infrastructure files (loaded first)
├── constructors.R       # new_quant_param(), new_qual_param()
├── finalize.R          # Finalization system
├── param_*.R           # Individual parameter definitions
├── range.R             # range_get(), range_set()
├── grids.R             # Grid generation functions
└── values.R            # value_sample(), value_seq()
```

**Key principles:**

- One parameter per file (usually): `R/param_[name].R`
- Infrastructure files prefixed with `aaa_` to load first
- Core constructors in dedicated file
- Helper functions grouped by functionality

### Core Constructors

Located in `R/constructors.R`:

```r
new_quant_param(
  type,           # "double" or "integer"
  range,          # Two-element vector
  inclusive,      # Two-element logical
  trans = NULL,   # Transformation from scales
  label,          # Named character for display
  finalize = NULL # Optional finalize function
)

new_qual_param(
  type,           # "character" or "logical"
  values,         # Vector of options
  default = NULL, # Optional default (first value if NULL)
  label,          # Named character for display
  finalize = NULL # Rarely used
)
```

### Infrastructure Files

Files prefixed with `aaa_` provide core functionality:

- `aaa_unknown.R`: `unknown()` placeholder for data-dependent ranges
- `aaa_utils.R`: Internal utility functions
- `aaa_globals.R`: Global variables and constants

These load before other files due to R's alphabetical loading order.

---

## Working Without dials:: Prefix

### Direct Function Calls

In source development, use functions directly:

```r
# Source development (correct)
new_quant_param(
  type = "double",
  range = c(0, 1),
  ...
)

# Extension development (not needed here)
dials::new_quant_param(...)
```

### Accessing Internal Functions

Source development gives you access to unexported helpers:

```r
# Internal validation
check_type(type)
check_range(range, type)

# Range manipulation
bounds <- range_get(object)
range_set(object, new_bounds)

# Value generation
value_sample(param, n = 10)
value_seq(param, n = 5)
```

---

## Internal Functions Available

### Validation Functions

**`check_type(type)`**

Validates parameter type:

```r
check_type("double")  # OK
check_type("integer") # OK
check_type("numeric") # Error
```

**`check_range(range, type)`**

Validates range specification:

```r
check_range(c(0, 1), "double")           # OK
check_range(c(1L, 10L), "integer")       # OK
check_range(c(1, 0), "double")           # Error: lower > upper
check_range(c(0), "double")              # Error: length != 2
```

### Range Manipulation

**`range_get(object)`**

Extract current range from parameter:

```r
param <- penalty()
bounds <- range_get(param)
# Returns: list(lower = -10, upper = 0)
```

**`range_set(object, range)`**

Set new range on parameter:

```r
new_bounds <- list(lower = -5, upper = 0)
param <- range_set(param, new_bounds)
```

Used in custom finalize functions:

```r
custom_finalize <- function(object, x) {
  bounds <- range_get(object)
  bounds$upper <- ncol(x)
  range_set(object, bounds)
}
```

### Value Generation

**`value_sample(param, n)`**

Generate random values from parameter:

```r
param <- penalty()
value_sample(param, n = 5)
# [1] 0.001 0.1 0.00001 0.5 0.01
```

**`value_seq(param, n)`**

Generate sequence of values:

```r
param <- penalty()
value_seq(param, n = 5)
# [1] 1e-10 1e-07 1e-04 1e-01 1e+00
```

### Built-in Finalize Functions

Located in `R/finalize.R`:

- `get_p()`: Set upper bound to number of predictors
- `get_n()`: Set upper bound to number of observations
- `get_n_frac()`: Set upper bound to fraction of observations
- `get_log_p()`: Set upper bound to log of predictors

Example usage:

```r
mtry <- function(range = c(1L, unknown()), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = get_p  # Use built-in finalize
  )
}
```

---

## File Naming Conventions

### Parameter Files

Pattern: `R/param_[name].R`

Examples:
- `R/param_penalty.R`
- `R/param_learn_rate.R`
- `R/param_mtry.R`
- `R/param_activation.R`

**One parameter per file** (usually). Related parameters may share a file:

- `R/param_activation.R`: Contains `activation()` and `activation_2()`

### Test Files

Tests for parameters go in **shared test files**:

- `tests/testthat/test-params.R`: Range validation for all parameters
- `tests/testthat/test-constructors.R`: Constructor argument validation
- `tests/testthat/test-finalize.R`: Finalization tests
- `tests/testthat/test-grids.R`: Grid generation tests

**Not** `test-param_name.R` like in extension packages.

See [Testing Patterns (Source)](testing-patterns-source.md) for details.

---

## Documentation Patterns

### Use @inheritParams

Inherit parameter documentation from constructors:

```r
#' @inheritParams new_quant_param
#' @param range A two-element vector with the lower and upper bounds.
```

Common inherited parameters:
- From `new_quant_param`: `trans`, `label`, `finalize`
- From `new_qual_param`: `label`, `finalize`

### Use @seealso

Link related parameters:

```r
#' @seealso [penalty()], [mixture()]
```

### Use @details

Explain parameter usage and behavior:

```r
#' @details
#' This parameter uses a log10 transformation, so the range is specified
#' in log10 units. The default range of c(-10, 0) represents values from
#' 10^-10 to 1.
```

### Use @examples

Show practical usage:

```r
#' @examples
#' penalty()
#' penalty(range = c(-5, 0))
#'
#' # Generate grid
#' grid_regular(penalty(), levels = 5)
#'
#' # Sample values
#' set.seed(123)
#' value_sample(penalty(), n = 5)
```

See [Roxygen Documentation](../../shared-references/package-roxygen-documentation.md) for complete patterns.

---

## Creating Parameters

### Simple Quantitative Parameter

```r
# R/param_threshold.R

#' Threshold value
#'
#' A threshold parameter for classification decisions.
#'
#' @inheritParams new_quant_param
#' @param range A two-element vector with the lower and upper bounds.
#'
#' @details
#' This parameter controls the decision threshold for binary classification.
#'
#' @examples
#' threshold()
#' threshold(range = c(0.3, 0.7))
#' @export
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

### Transformed Quantitative Parameter

```r
# R/param_penalty.R

#' Amount of regularization
#'
#' The total amount of regularization.
#'
#' @inheritParams new_quant_param
#' @param range A two-element vector with the lower and upper bounds
#'   (in log10 units).
#'
#' @details
#' This parameter uses a log10 transformation. The default range of
#' c(-10, 0) represents penalty values from 10^-10 to 1.
#'
#' @examples
#' penalty()
#' penalty(range = c(-5, 0))
#'
#' @seealso [mixture()], [cost()]
#' @export
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

### Data-Dependent Parameter

```r
# R/param_mtry.R

#' Number of randomly sampled predictors
#'
#' The number of predictors randomly sampled at each split.
#'
#' @inheritParams new_quant_param
#' @param range A two-element vector with the lower and upper bounds.
#'
#' @details
#' The upper bound depends on the number of predictors in the data.
#' Use `finalize()` with training data to set the upper bound.
#'
#' @examples
#' mtry()
#'
#' # Finalize with data
#' mtry() %>% finalize(mtcars[, -1])
#'
#' @export
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

### Custom Finalize Function

```r
# R/param_num_terms.R

#' Number of MARS terms
#'
#' The number of terms in a MARS model.
#'
#' @inheritParams new_quant_param
#' @param range A two-element vector with the lower and upper bounds.
#'
#' @details
#' The upper bound is calculated using the earth package formula:
#' min(200, max(20, 2 * ncol(x))) + 1
#'
#' @examples
#' num_terms()
#'
#' # Finalize with data
#' num_terms() %>% finalize(mtcars[, -1])
#'
#' @export
num_terms <- function(range = c(1L, unknown()), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(num_terms = "# Model Terms"),
    finalize = get_num_terms
  )
}

get_num_terms <- function(object, x) {
  upper_bound <- min(200, max(20, 2 * ncol(x))) + 1
  upper_bound <- as.integer(upper_bound)

  bounds <- range_get(object)
  bounds$upper <- upper_bound
  range_set(object, bounds)
}
```

### Qualitative Parameter

```r
# R/param_activation.R

#' Activation functions
#'
#' The activation function for neural networks.
#'
#' @inheritParams new_qual_param
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
  new_qual_param(
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

---

## PR Submission Checklist

Before submitting your pull request:

### Code

- [ ] Parameter function follows naming conventions
- [ ] File named `R/param_[name].R`
- [ ] Uses appropriate constructor (`new_quant_param` or `new_qual_param`)
- [ ] Includes `@export` tag
- [ ] No `dials::` prefix needed (source development)

### Documentation

- [ ] Complete roxygen documentation
- [ ] Uses `@inheritParams` for common arguments
- [ ] Includes `@details` explaining usage
- [ ] Includes `@examples` with practical usage
- [ ] Uses `@seealso` to link related parameters
- [ ] Runs `devtools::document()` successfully

### Testing

- [ ] Tests added to `tests/testthat/test-params.R`
- [ ] Constructor validation tests in `test-constructors.R`
- [ ] Tests for finalization (if applicable) in `test-finalize.R`
- [ ] All tests pass with `devtools::test()`
- [ ] Snapshots accepted if needed

See [Testing Patterns (Source)](testing-patterns-source.md) for complete testing guide.

### Package Checks

- [ ] `devtools::check()` passes with no errors, warnings, or notes
- [ ] `devtools::spell_check()` passes
- [ ] NEWS.md updated with new parameter

### NEWS.md Format

Add entry under "Development" section:

```markdown
## Development

* New parameter `my_parameter()` for [use case] (#PR_NUMBER).
```

### Git

- [ ] Commit messages follow package conventions
- [ ] Branch named descriptively (e.g., `add-my-parameter`)
- [ ] PR description explains the need for new parameter
- [ ] PR references any related issues

---

## Next Steps

### Learn the System

1. **Understand architecture**: [Parameter System Overview](parameter-system.md)
2. **Study examples**: Review existing parameters in `R/param_*.R`
3. **Learn patterns**: Read [Best Practices (Source)](best-practices-source.md)

### Create Your Parameter

1. **Choose type**: [Quantitative](quantitative-parameters.md) or [Qualitative](qualitative-parameters.md)
2. **Add features**: [Transformations](transformations.md) or [Finalization](data-dependent-parameters.md)
3. **Test thoroughly**: [Testing Patterns (Source)](testing-patterns-source.md)

### Get Help

- **Issues**: [Troubleshooting (Source)](troubleshooting-source.md)
- **Questions**: Ask in tidymodels GitHub discussions
- **Examples**: Study `repos/dials/` cloned repository

---

**Last Updated:** 2026-03-31
