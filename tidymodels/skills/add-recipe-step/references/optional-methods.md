# Optional S3 Methods for Recipe Steps

Beyond the required methods (`prep`, `bake`, `print`, `tidy`), recipe steps can implement optional methods to support additional functionality.

## Overview

Optional methods:
- **`tunable()`**: Declares parameters that can be tuned with the tune package
- **`required_pkgs()`**: Declares external package dependencies
- **`.recipes_preserve_sparsity()`**: Indicates if sparse data stays sparse
- **`.recipes_estimate_sparsity()`**: Estimates sparsity for new columns created

## tunable() - Hyperparameter Tuning Support

### When to implement

Implement `tunable()` if your step has parameters that:
- Have reasonable ranges to explore
- Significantly affect model performance
- Users would want to optimize

### Implementation pattern

```r
#' @export
tunable.step_yourname <- function(x, ...) {
  tibble::tibble(
    name = c("param1", "param2"),
    call_info = list(
      list(pkg = "dials", fun = "param1_range"),
      list(pkg = "dials", fun = "param2_range")
    ),
    source = "recipe",
    component = "step_yourname",
    component_id = x$id
  )
}
```

### Column descriptions

- **`name`**: Character vector of parameter names (must match step parameters)
- **`call_info`**: List of lists specifying dials function for each parameter
- **`source`**: Always `"recipe"` for recipe steps
- **`component`**: Step name (e.g., `"step_yourname"`)
- **`component_id`**: Unique step identifier (`x$id`)

### Example: step_spline_natural

```r
#' @export
tunable.step_spline_natural <- function(x, ...) {
  tibble::tibble(
    name = c("deg_free"),
    call_info = list(
      list(pkg = "dials", fun = "spline_degree")
    ),
    source = "recipe",
    component = "step_spline_natural",
    component_id = x$id
  )
}
```

This allows users to tune the degrees of freedom:

```r
recipe(mpg ~ ., data = mtcars) |>
  step_spline_natural(disp, deg_free = tune())
```

### Dials integration

The `call_info` references dials parameter objects:
- `dials::spline_degree()`: Range for spline degrees of freedom
- `dials::num_comp()`: Number of components (PCA, PLS)
- `dials::threshold()`: Threshold values

If no suitable dials function exists, you may need to create one in your package.

## required_pkgs() - Package Dependencies

### When to implement

Implement `required_pkgs()` if your step:
- Uses functions from packages not in Imports
- Depends on optional packages (in Suggests)
- Needs specific packages at runtime

### Implementation pattern

```r
#' @export
required_pkgs.step_yourname <- function(x, ...) {
  c("package1", "package2")
}
```

Return a character vector of package names needed by your step.

### Checking for packages

Use `recipes_pkg_check()` in your step constructor:

```r
step_yourname <- function(recipe, ...) {
  # Check packages are available before adding step
  recipes::recipes_pkg_check(required_pkgs.step_yourname())

  recipes::add_step(
    recipe,
    step_yourname_new(...)
  )
}
```

### Example: step_ica

```r
#' @export
required_pkgs.step_ica <- function(x, ...) {
  c("fastICA")
}

step_ica <- function(recipe, ...) {
  recipes::recipes_pkg_check(required_pkgs.step_ica())
  # ... rest of function
}
```

This ensures fastICA is available before adding the step to the recipe.

### Multiple packages

```r
#' @export
required_pkgs.step_umap <- function(x, ...) {
  c("uwot", "RSpectra")
}
```

### Runtime checking

The package check happens when the step is **added** to the recipe, not when it's executed. This gives users immediate feedback if they're missing dependencies.

## .recipes_preserve_sparsity() - Sparse Data Preservation

### When to implement

Implement this if your step:
- Takes sparse matrices as input
- Can perform its operation without densifying
- Returns sparse output

**Note:** This is for steps that **preserve** sparsity in existing columns, not steps that create new sparse columns.

### Implementation pattern

```r
#' @export
.recipes_preserve_sparsity.step_yourname <- function(x, ...) {
  TRUE  # This step preserves sparsity
}
```

Return `TRUE` if sparse stays sparse, `FALSE` otherwise (or don't implement).

### Examples

**Preserves sparsity:**
```r
# Scaling: multiplying sparse matrix by scalar preserves sparsity
.recipes_preserve_sparsity.step_scale <- function(x, ...) {
  TRUE
}

# Centering: subtracting value from sparse matrix usually destroys sparsity
.recipes_preserve_sparsity.step_center <- function(x, ...) {
  FALSE  # Or don't implement at all
}
```

### Internal method

The `.recipes_preserve_sparsity()` method is **internal** (note the leading dot). It's used by the recipes infrastructure but not directly by users.

## .recipes_estimate_sparsity() - Sparsity Estimation

### When to implement

Implement this if your step:
- **Creates new columns** (not modifies existing)
- Creates columns that are likely sparse
- Examples: dummy variables, one-hot encoding, interaction terms

**Note:** This is for create-new-columns steps only. See [create-new-columns-steps.md](create-new-columns-steps.md) for more details.

### Implementation pattern

```r
#' @export
.recipes_estimate_sparsity.step_yourname <- function(x, data, ...) {
  # Get column names that will be processed
  col_names <- recipes::recipes_eval_select(
    x$terms,
    data,
    recipes::get_recipe_info(data)
  )

  # Estimate number of new columns that will be created
  n_new_cols <- estimate_output_columns(data[, col_names])

  # Estimate proportion of zeros in the new columns (0 to 1)
  est_sparsity <- estimate_zero_proportion(data[, col_names])

  list(
    n_cols = n_new_cols,
    sparsity = est_sparsity
  )
}
```

### Return value

Must return a list with:
- **`n_cols`**: Integer, number of columns that will be created
- **`sparsity`**: Numeric between 0 and 1, estimated proportion of zeros

### Example: step_dummy

```r
#' @export
.recipes_estimate_sparsity.step_dummy <- function(x, data, ...) {
  col_names <- recipes::recipes_eval_select(
    x$terms,
    data,
    recipes::get_recipe_info(data)
  )

  # Count levels across all factor columns
  # Dummy coding creates k-1 columns per k-level factor
  n_new_cols <- sum(vapply(
    data[col_names],
    function(col) nlevels(col) - 1,
    integer(1)
  ))

  # For dummy variables, estimate high sparsity
  # Most observations are in one category, creating many zeros
  est_sparsity <- 0.8

  list(n_cols = n_new_cols, sparsity = est_sparsity)
}
```

### Why this matters

The recipes infrastructure uses sparsity estimates to:
- Decide whether to use sparse matrix representations
- Optimize memory usage for large datasets
- Choose efficient algorithms for sparse operations

## When to Skip Optional Methods

### tunable()

Skip if:
- Your step has no tunable parameters
- Parameters are deterministic (e.g., column names)
- Parameters have obvious single best values

### required_pkgs()

Skip if:
- All dependencies are in your package's Imports
- Your step uses only base R and recipes functions

### Sparsity methods

Skip if:
- Your step only works with dense data
- Sparsity preservation is unclear or complex
- Your step modifies values in place (not creating columns)

## Testing Optional Methods

### Testing tunable()

```r
test_that("tunable method returns correct structure", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourname(disp)

  tunable_info <- tunable(rec$steps[[1]])

  expect_s3_class(tunable_info, "tbl_df")
  expect_named(tunable_info, c("name", "call_info", "source", "component", "component_id"))
  expect_equal(tunable_info$name, "your_param")
})
```

### Testing required_pkgs()

```r
test_that("required_pkgs returns correct packages", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourname(disp)

  pkgs <- required_pkgs(rec$steps[[1]])

  expect_type(pkgs, "character")
  expect_true("yourpackage" %in% pkgs)
})
```

### Testing sparsity estimation

```r
test_that("sparsity estimation is reasonable", {
  skip_if_not_installed("Matrix")

  sparse_data <- Matrix::Matrix(
    sample(c(0, 0, 0, 1), 100, replace = TRUE),
    nrow = 10
  )

  rec <- recipe(~ ., data = sparse_data) |>
    step_yourname(all_predictors())

  est <- .recipes_estimate_sparsity(rec$steps[[1]], sparse_data)

  expect_type(est, "list")
  expect_named(est, c("n_cols", "sparsity"))
  expect_true(est$n_cols > 0)
  expect_true(est$sparsity >= 0 && est$sparsity <= 1)
})
```

## Documentation

Document optional methods in your main step documentation:

```r
#' @details
#'
#' [Other details...]
#'
#' # Tuning Parameters
#'
#' This step has 1 tuning parameter:
#' - `your_param`: description (type: numeric)
#'
#' # Required Packages
#'
#' This step requires the yourpackage package. Install it with
#' `install.packages("yourpackage")`.
```

## Next Steps

- Understand architecture: [step-architecture.md](step-architecture.md)
- Implement basic steps: [modify-in-place-steps.md](modify-in-place-steps.md), [create-new-columns-steps.md](create-new-columns-steps.md)
- Learn helper functions: [helper-functions.md](helper-functions.md)
- Document thoroughly: [../../shared-references/roxygen-documentation.md](../../shared-references/roxygen-documentation.md)
- Test comprehensively: [../../shared-references/testing-patterns.md](../../shared-references/testing-patterns.md)
