# Creating Create-New-Columns Steps

This template is for steps that create new columns from existing ones.

> **Note for Source Development:** If you're contributing directly to the recipes package, use internal helpers directly: `recipes_eval_select()`, `remove_original_cols()`, `check_name()`, etc. No `recipes::` prefix needed. See the [Source Development Guide](source-guide.md) for details.

## Overview

Create-new-columns steps:

- Generate new columns based on existing columns

- Can optionally keep or remove original columns

- Assign roles to new columns

- Examples: `step_dummy`, `step_pca`, `step_interact`, `step_poly`

**Canonical implementations in recipes:**

- Encoding: `R/dummy.R` (one-hot encoding), `R/bin2factor.R`

- Dimension reduction: `R/pca.R`, `R/ica.R`, `R/kpca.R`

- Feature engineering: `R/interact.R`, `R/poly.R`, `R/bs.R` (basis splines)

- Date features: `R/date.R`, `R/holiday.R`

**Test patterns:**

- Encoding tests: `tests/testthat/test-dummy.R`

- Dimension reduction: `tests/testthat/test-pca.R`

## Key Differences from Modify-in-Place

1. **`role` default is `"predictor"`** (not `NA`)
2. **Includes `keep_original_cols` parameter**
3. **Calls `remove_original_cols()` in `bake()`**
4. **May need to implement `.recipes_estimate_sparsity()`** for sparse support
5. **`tidy()` returns column names created**, not just input columns

## Complete Template

This template follows the same pattern as `R/dummy.R` and `R/interact.R` in the recipes repository.

```r
#' Title for your step that creates new columns
#'
#' `step_yournewcols()` creates a *specification* of a recipe step that will
#' create new columns based on [description].
#'
#' @inheritParams step_center
#' @param ... One or more selector functions to choose variables for this step.
#'   See [recipes::selections()] for more details.
#' @param role For model terms created by this step, what analysis role should
#'   they be assigned? By default, the new columns created by this step will
#'   be used as predictors in a model.
#' @param [your_params] Description of step-specific parameters.
#' @param columns A character vector of column names that will be populated
#'   (eventually) by the [terms] argument. This is `NULL` until computed by
#'   [prep()].
#' @param [learned_info] Description of information learned during prep().
#'   This is `NULL` until computed by [prep()].
#' @param keep_original_cols A logical to keep the original variables in the
#'   output. Defaults to `FALSE`.
#'
#' @return An updated version of `recipe` with the new step added to the
#'   sequence of any existing operations.
#'
#' @family [your step category] steps
#' @export
#'
#' @details
#'
#' [Detailed explanation of the step, including formulas and computational
#' details.]
#'
#' When you [`tidy()`][recipes::tidy.recipe()] this step, a tibble is returned with
#' columns `terms`, `columns`, and `id`:
#'
#' \describe{
#'   \item{terms}{character, the selectors or variables selected}
#'   \item{columns}{character, names of the new columns created}
#'   \item{id}{character, id of this step}
#' }
#'
#' # Case weights
#'
#' This step performs an unsupervised operation that can utilize case weights.
#' As a result, case weights are used with frequency weights as well as
#' importance weights. For more information, see the documentation in
#' [recipes::case_weights] and the examples on `tidymodels.org`.
#'
#' @examplesIf rlang::is_installed("modeldata")
#' data(biomass, package = "modeldata")
#'
#' rec <- recipe(HHV ~ ., data = biomass)
#'
#' # Create new columns
#' step_trans <- rec |>
#'   step_yournewcols(carbon, hydrogen)
#'
#' step_trained <- prep(step_trans, training = biomass)
#'
#' # See new columns created
#' transformed <- bake(step_trained, biomass)
#' names(transformed)
#'
#' # Keep original columns
#' step_keep <- rec |>
#'   step_yournewcols(carbon, hydrogen, keep_original_cols = TRUE)
#'
#' step_keep_trained <- prep(step_keep, training = biomass)
#' transformed_keep <- bake(step_keep_trained, biomass)
#' names(transformed_keep)
#'
#' tidy(step_trans, number = 1)
#' tidy(step_trained, number = 1)
step_yournewcols <- function(
  recipe,
  ...,
  role = "predictor",
  trained = FALSE,
  your_param = default_value,
  columns = NULL,
  learned_info = NULL,
  keep_original_cols = FALSE,
  skip = FALSE,
  id = recipes::rand_id("yournewcols")
) {
  recipes::add_step(
    recipe,
    step_yournewcols_new(
      terms = rlang::enquos(...),
      trained = trained,
      role = role,
      your_param = your_param,
      columns = NULL,
      learned_info = learned_info,
      keep_original_cols = keep_original_cols,
      skip = skip,
      id = id,
      case_weights = NULL
    )
  )
}

step_yournewcols_new <- function(terms, role, trained, your_param, columns,
                                  learned_info, keep_original_cols, skip, id,
                                  case_weights) {
  recipes::step(
    subclass = "yournewcols",
    terms = terms,
    role = role,
    trained = trained,
    your_param = your_param,
    columns = columns,
    learned_info = learned_info,
    keep_original_cols = keep_original_cols,
    skip = skip,
    id = id,
    case_weights = case_weights
  )
}

#' @export
prep.step_yournewcols <- function(x, training, info = NULL, ...) {
  col_names <- recipes::recipes_eval_select(x$terms, training, info)
  recipes::check_type(training[, col_names], types = c("double", "integer"))

  wts <- recipes::get_case_weights(info, training)
  were_weights_used <- recipes::are_weights_used(wts, unsupervised = TRUE)
  if (isFALSE(were_weights_used)) {
    wts <- NULL
  }

  # Compute information needed to create new columns
  # Example: compute coefficients, levels, loadings, etc.
  learned_info <- compute_your_transformation(
    training[, col_names],
    wts,
    x$your_param
  )

  step_yournewcols_new(
    terms = x$terms,
    role = x$role,
    trained = TRUE,
    your_param = x$your_param,
    columns = col_names,
    learned_info = learned_info,
    keep_original_cols = x$keep_original_cols,
    skip = x$skip,
    id = x$id,
    case_weights = were_weights_used
  )
}

#' @export
bake.step_yournewcols <- function(object, new_data, ...) {
  col_names <- object$columns
  recipes::check_new_data(col_names, object, new_data)

  # Create new columns based on learned information
  # Example: create interaction terms, dummy variables, etc.
  new_cols <- create_new_columns(
    new_data[, col_names],
    object$learned_info,
    object$your_param
  )

  # Add new columns to data
  new_data <- vctrs::vec_cbind(new_data, new_cols)

  # Optionally remove original columns
  new_data <- recipes::remove_original_cols(new_data, object, col_names)

  new_data
}

#' @export
print.step_yournewcols <- function(x, width = max(20, options()$width - 30), ...) {
  title <- "Creating new columns from "
  recipes::print_step(
    x$columns,
    x$terms,
    x$trained,
    title,
    width,
    case_weights = x$case_weights
  )
  invisible(x)
}

#' @rdname tidy.recipe
#' @export
tidy.step_yournewcols <- function(x, ...) {
  if (recipes::is_trained(x)) {
    # Return information about created columns
    res <- tibble::tibble(
      terms = rep(x$columns, times = lengths_of_new_cols),
      columns = names_of_new_columns_created
    )
  } else {
    term_names <- recipes::sel2char(x$terms)
    res <- tibble::tibble(
      terms = term_names,
      columns = rlang::na_chr
    )
  }
  res$id <- x$id
  res
}

# Optional: Implement sparsity estimation if your step can create sparse columns
.recipes_estimate_sparsity.step_yournewcols <- function(x, data, ...) {
  # Estimate how many columns will be created and their sparsity
  # Return a list with n_cols (integer) and sparsity (numeric between 0 and 1)
  col_names <- recipes::recipes_eval_select(x$terms, data, recipes::get_recipe_info(data))

  # Example: dummy coding creates n-1 columns with estimated sparsity
  n_new_cols <- estimate_number_of_columns(data[, col_names])
  est_sparsity <- estimate_sparsity(data[, col_names])

  list(
    n_cols = n_new_cols,
    sparsity = est_sparsity
  )
}
```

## Case Weights

**INSTRUCTIONS FOR CLAUDE:** Include case weight handling based on operation type.

### Include Case Weights IF Step Computes Statistics:

**Required when prep() aggregates across rows:**

- ✅ Mean, median, mode

- ✅ Quantiles, percentiles, quartiles (e.g., 5th, 95th percentile)

- ✅ IQR (interquartile range)

- ✅ Variance, standard deviation

- ✅ Min/Max for scaling/normalization

- ✅ PCA/dimension reduction (uses covariance matrix)

**Examples that NEED case weights:**

- step_pca() - computes covariance/correlation

- step_ica() - statistical decomposition

- step_bin() - computes quantiles for binning

- step_discretize() - computes break points

### Skip Case Weights IF Step Only Does Per-Row Operations:

**Not required when operation is per-row:**

- ❌ Creating dummy/indicator variables from existing factors

- ❌ Polynomial expansion (x, x², x³)

- ❌ Interactions between existing columns

- ❌ Date/time feature extraction

- ❌ Text feature extraction (without aggregation)

**Examples that DON'T need case weights:**

- step_dummy() - creates indicators from factors

- step_interact() - multiplies existing columns

- step_poly() - polynomial expansion

### Detection Rule:

Ask: "Does prep() compute a statistic by aggregating across multiple rows?"

- **YES** → Include case weights (add parameters, implement weighted calculations, add tests)

- **NO** → Skip case weights entirely

**Implementation when needed:**

- Add `case_weights` parameter to constructor

- Use `get_case_weights()` and `are_weights_used()` in prep()

- Implement weighted calculations (weighted.mean, weighted quantiles, etc.)

- Add 2 case weight tests (frequency weights, importance weights)

## Additional Notes for Create-New-Columns Steps

### Column naming

- **Use descriptive, consistent naming conventions**

- **Consider providing a `naming` parameter** for custom naming functions

- **Validate that new names don't conflict** with existing columns using `recipes::check_name()`

Example naming pattern:
```r
# For dummy variables
new_col_names <- paste0(original_col, "_", levels)

# For polynomial features
new_col_names <- paste0(original_col, "_poly_", 1:degree)

# For interactions
new_col_names <- paste(col1, col2, sep = "_x_")
```

### Sparsity support

- **If your step creates sparse columns** (like dummy variables), implement `.recipes_estimate_sparsity()`

- **This allows workflows to optimize sparse data handling**

- **Return a list** with `n_cols` (integer) and `sparsity` (numeric 0-1)

Example:
```r
.recipes_estimate_sparsity.step_dummy <- function(x, data, ...) {
  col_names <- recipes_eval_select(x$terms, data, get_recipe_info(data))

  # Count total levels across all factor columns
  n_new_cols <- sum(sapply(data[col_names], function(x) nlevels(x) - 1))

  # Estimate sparsity: for dummy variables, typically high
  est_sparsity <- 0.8  # 80% zeros for typical categorical data

  list(n_cols = n_new_cols, sparsity = est_sparsity)
}
```

### keep_original_cols

- **Always use `remove_original_cols()` in `bake()`** to handle this parameter

- **Don't implement the logic yourself** - the helper does it correctly

```r
# Good: use the helper
new_data <- recipes::remove_original_cols(new_data, object, col_names)

# Bad: manual implementation (error-prone)
if (!object$keep_original_cols) {
  new_data <- new_data[, !names(new_data) %in% col_names]
}
```

The helper correctly handles:

- Preserving column order

- Handling role assignments

- Edge cases with column names

## Common Patterns

### Dummy variables (one-hot encoding)

```r
prep:
  # Store factor levels for each column
  levels_list <- lapply(training[col_names], levels)

bake:
  # Create dummy variables
  for (col in col_names) {
    dummies <- model.matrix(~ . - 1, data = data.frame(x = new_data[[col]]))
    colnames(dummies) <- paste0(col, "_", levels_list[[col]])
    new_data <- vctrs::vec_cbind(new_data, as.data.frame(dummies))
  }
```

### Polynomial features

```r
prep:
  # Store degree parameter (no learning needed)

bake:
  for (col in col_names) {
    for (deg in 2:degree) {
      new_col_name <- paste0(col, "_poly_", deg)
      new_data[[new_col_name]] <- new_data[[col]]^deg
    }
  }
```

### Interaction terms

```r
prep:
  # Store which pairs to create interactions for

bake:
  for (i in 1:(length(col_names)-1)) {
    for (j in (i+1):length(col_names)) {
      new_col_name <- paste(col_names[i], col_names[j], sep = "_x_")
      new_data[[new_col_name]] <- new_data[[col_names[i]]] * new_data[[col_names[j]]]
    }
  }
```

## Testing

See [package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements) for comprehensive testing guide.

### Key tests for create-new-columns steps

```r
test_that("new columns are created", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yournewcols(cyl, gear)

  prepped <- prep(rec, training = mtcars)
  results <- bake(prepped, mtcars)

  # Verify new columns exist
  expect_true("cyl_new" %in% names(results))
  expect_true("gear_new" %in% names(results))

  # Verify original columns removed by default
  expect_false("cyl" %in% names(results))
  expect_false("gear" %in% names(results))
})

test_that("keep_original_cols works", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yournewcols(cyl, keep_original_cols = TRUE)

  prepped <- prep(rec, training = mtcars)
  results <- bake(prepped, mtcars)

  # Verify both original and new columns exist
  expect_true("cyl" %in% names(results))
  expect_true("cyl_new" %in% names(results))
})

test_that("tidy returns correct information", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yournewcols(cyl, gear)

  # Untrained
  untrained_tidy <- tidy(rec, 1)
  expect_equal(untrained_tidy$columns, rep(NA_character_, 2))

  # Trained
  prepped <- prep(rec, training = mtcars)
  trained_tidy <- tidy(prepped, 1)

  expect_true(all(c("cyl_new", "gear_new") %in% trained_tidy$columns))
})
```

## Next Steps

- Understand architecture: [step-architecture.md](step-architecture.md)

- Modify in place: [modify-in-place-steps.md](modify-in-place-steps.md)

- Row operations: [row-operation-steps.md](row-operation-steps.md)

- Add optional methods: [optional-methods.md](optional-methods.md)

- Learn helper functions: [helper-functions.md](helper-functions.md)

- Document your step: [package-roxygen-documentation.md](package-roxygen-documentation.md)

- Write tests: [package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements)
