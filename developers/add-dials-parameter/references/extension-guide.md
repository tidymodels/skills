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

## Critical Requirements

When creating dials parameters, certain patterns are **non-negotiable**:

### ✅ MUST DO

1. **Always use dials:: prefix** in extension development
   ```r
   # ✅ CORRECT
   dials::new_quant_param(...)
   dials::unknown()
   dials::finalize()

   # ❌ WRONG - Do not use internal functions
   new_quant_param(...)  # Missing prefix
   dials:::internal_helper()  # Using internal function
   ```

2. **Always export parameters** with @export tag
   ```r
   #' @export
   my_parameter <- function(...) { }
   ```

3. **Always provide working examples** in @examples
   ```r
   #' @examples
   #' # Basic usage
   #' my_parameter()
   #'
   #' # With grid generation
   #' dials::grid_regular(my_parameter(), levels = 5)
   ```

4. **Always test grid integration**

   - Test with grid_regular()

   - Test with grid_random()

   - Test value_sample() and value_seq() for quantitative parameters

### ❌ MUST NOT DO

1. **Never use internal functions** (:::) in extension development

   - You cannot access check_type(), check_range(), or any unexported functions

   - All logic must use exported dials functions only

2. **Never create parameters without finalize logic** for data-dependent bounds

   - If using unknown(), MUST provide finalize function

   - Test finalization with sample data

3. **Never skip test coverage** for critical features

   - Range validation

   - Grid generation

   - Finalization (if applicable)

   - Edge cases (invalid inputs)

**INSTRUCTIONS FOR CLAUDE:**

If the user attempts to use internal functions in extension development:
1. **STOP and explain the constraint**
2. Provide the correct exported function alternative
3. If no alternative exists, explain they need source development instead

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

### Step 5: Verify Your Implementation

**⚠️ CRITICAL: FILE CREATION DISCIPLINE ⚠️**

**STOP! Before creating ANY files, read this entire section.**

You will create **EXACTLY 3 files** for extension development. Not 4. Not 5. Not 8. **EXACTLY 3.**

#### Mandatory Pre-Flight Checklist

Before creating files, verify:

- [ ] I will create R/param_[name].R

- [ ] I will create tests/testthat/test-param_[name].R

- [ ] I will create README.md (ONLY if package has no README)

- [ ] I will NOT create any other files

- [ ] All examples go in roxygen @examples, NOT in separate files

- [ ] All documentation goes in roxygen comments, NOT in separate .md files

#### Files You Will Create

1. **R/param_[name].R** - Parameter function with roxygen documentation
2. **tests/testthat/test-param_[name].R** - Comprehensive tests
3. **README.md** - Brief usage guide (optional, only if package doesn't have one)

#### Files You Will NOT Create

**INSTRUCTIONS FOR CLAUDE: STOP IMMEDIATELY IF YOU ARE ABOUT TO CREATE ANY OF THESE FILES.**

**❌ NEVER CREATE THESE FILES:**

- ❌ IMPLEMENTATION_SUMMARY.md

- ❌ QUICKSTART.md

- ❌ example_usage.R (examples belong in roxygen @examples)

- ❌ MANIFEST.md

- ❌ INDEX.md

- ❌ INTEGRATION_GUIDE.md

- ❌ IMPLEMENTATION_NOTES.md

- ❌ KEY_CODE_PATTERNS.md

- ❌ FILE_ORGANIZATION.txt

- ❌ DELIVERY_SUMMARY.md

- ❌ SUMMARY.md or SUMMARY.txt

- ❌ Any other supplementary documentation files

**If starting a new package**, you may ALSO need:

- DESCRIPTION (package metadata)

- NAMESPACE (will be generated by devtools::document())

- [packagename]-package.R (package-level documentation, optional)

**These package infrastructure files are ONLY created when initializing a new package. When adding a parameter to an existing package, create ONLY the 3 core files listed above.**

#### File Creation Discipline

- **Parameter code:** Goes in R/param_[name].R with roxygen @examples

- **Tests:** Go in tests/testthat/test-param_[name].R

- **Usage guide:** Goes in README.md (only if package needs one)

- **Examples:** Go in roxygen @examples in the R file, NOT in separate example_usage.R

- **Implementation notes:** Go in roxygen @details in the R file, NOT in separate IMPLEMENTATION_SUMMARY.md

- **Everything else:** Does NOT get created

#### Why This Matters

Creating extra documentation files is the most common mistake in parameter development. These files:

- Create clutter without adding value

- Duplicate information already in roxygen comments

- Violate R package conventions

- Make the package harder to maintain

**All necessary documentation belongs in roxygen comments and README. Period.**

### Step 6: Test Parameter

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

## Development Best Practices

**Focus on correctness and completeness:**

✅ **Provide complete, working examples** in roxygen @examples
✅ **Explain key concepts** briefly (transformations, finalization)
✅ **Show common patterns** with code snippets
✅ **Include comprehensive tests** covering all features

⚠️ **But avoid over-explanation:**

- Don't repeat information already in linked references

- Keep README brief (< 150 lines)

- Examples in roxygen are sufficient; don't create separate example files

- Trust that users can read reference docs for deep dives

**Quality indicators:**

- All required parameter fields specified (type, range/values, label, etc.)

- Tests cover correctness, edge cases, and grid integration

- Documentation includes working examples

- Code follows dials conventions (naming, structure, style)

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

See [Data-Dependent Parameters](data-dependent-parameters.md) for complete guide including step-by-step custom finalization.

### Example 3B: Custom Finalization Logic

A parameter with custom finalization using range_get and range_set:

```r
# R/param_num_genes.R

#' Number of genes to select
#'
#' The number of genes to select, with upper bound set to 80% of available genes.
#'
#' @param range A two-element vector with bounds.
#' @param trans A transformation object (default NULL).
#'
#' @details
#' The upper bound is unknown and finalized to 80% of total available genes.
#' This uses a custom finalize function to implement the 80% rule.
#'
#' @examples
#' num_genes()
#'
#' # Finalize with data (100 genes available)
#' param <- num_genes()
#' finalized <- dials::finalize(param, matrix(rnorm(100*100), ncol=100))
#' finalized$range$upper  # Will be 80 (80% of 100)
#'
#' @export
num_genes <- function(range = c(1L, dials::unknown()), trans = NULL) {
  dials::new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(num_genes = "# Genes to Select"),
    finalize = get_num_genes
  )
}

# Custom finalize function
get_num_genes <- function(object, x) {
  # Step 1: Calculate new bound (80% of available genes)
  num_available <- ncol(x)
  new_upper <- floor(0.8 * num_available)
  new_upper <- max(1L, new_upper)  # At least 1
  new_upper <- as.integer(new_upper)

  # Step 2: Get current range
  bounds <- dials::range_get(object)

  # Step 3: Update upper bound
  bounds$upper <- new_upper

  # Step 4: Set new range and return
  dials::range_set(object, bounds)
}
```

**Key points about custom finalization:**

- Custom finalize function has signature `function(object, x)`

- Use `dials::range_get(object)` to extract current bounds

- Modify the bounds list (`bounds$upper` or `bounds$lower`)

- Use `dials::range_set(object, bounds)` to update and return

- Always ensure bounds are valid (correct type, lower < upper, at least 1)

See [Data-Dependent Parameters](data-dependent-parameters.md) for detailed step-by-step guide on custom finalization.

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

### Pattern 4: Qualitative with Companion Values Vector

**CRITICAL:** Qualitative parameters MUST follow this pattern. This is non-negotiable.

For categorical parameters, you create **TWO things that work together**:

1. **The parameter function** - Creates the parameter object
2. **The values vector** - Provides the allowed options

#### Complete Example

```r
# R/param_optimizer.R

#' Optimizer selection
#'
#' The optimization algorithm to use for training.
#'
#' @param values A character vector of optimizer names.
#'
#' @details
#' This parameter allows selection of optimization algorithm.
#' Common options include "adam", "sgd", "rmsprop", and "adagrad".
#'
#' @examples
#' values_optimizer
#' optimizer()
#' optimizer(values = c("adam", "sgd"))
#'
#' # Sample random values
#' set.seed(123)
#' dials::value_sample(optimizer(), n = 3)
#'
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

#### Key Components Explained

**1. The Parameter Function (`optimizer()`):**

- Takes `values` parameter with default `values_optimizer`

- Uses `dials::new_qual_param()` constructor

- Specifies `type = "character"` for categorical strings

- Includes `@export` tag to make function available

**2. The Values Vector (`values_optimizer`):**

- Character vector listing all allowed options

- Exported separately with its own `@export` tag

- Named with `values_` prefix (dials convention)

- Grouped with parameter using `@rdname`

**3. The @rdname Tag (REQUIRED):**

- `@rdname optimizer` on the values vector

- Groups both function and vector in same help page

- Without this, they appear on separate help pages

- This is **required** - don't skip it

#### Qualitative Parameter Checklist

Before completing a qualitative parameter, verify:

- [ ] Created parameter function with `dials::new_qual_param()`

- [ ] Created companion `values_*` vector with options

- [ ] Used `@rdname` to group function and values vector

- [ ] Added `@export` to BOTH function and values vector

- [ ] Parameter function defaults to the `values_*` vector

- [ ] Examples show both the function and values vector

- [ ] Both items are in the SAME file (R/param_[name].R)

#### Common Mistakes

❌ **Missing companion vector** - Parameter alone without values vector
❌ **Missing @rdname** - Function and vector on separate help pages
❌ **Missing @export on vector** - Values vector not accessible to users
❌ **Wrong naming** - Not using `values_` prefix for vector

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
