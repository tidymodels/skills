# Creating Modify-in-Place Steps

This is the simplest type of step. It transforms existing columns without
creating new ones.

> **Note for Source Development:** If you're contributing directly to the
> recipes package, you can use internal helpers directly (no `recipes::` prefix
> needed): `recipes_eval_select()`, `check_type()`, `check_new_data()`, etc. See
> the [Source Development Guide](source-guide.md) for details.

## Overview

Modify-in-place steps:

- Transform existing columns

- Don't create new columns

- Preserve column names and roles

- Examples: `step_center`, `step_scale`, `step_normalize`, `step_log`

**Canonical implementations in recipes:**

- Simple location/scale: `R/center.R`, `R/scale.R`, `R/normalize.R`

- Math transformations: `R/log.R`, `R/sqrt.R`, `R/logit.R`, `R/invlogit.R`

- Power transformations: `R/BoxCox.R` (Box-Cox with lambda parameter)

- Trigonometric: `R/hyperbolic.R`, `R/harmonic.R`

**Test patterns:**

- Basic transformations: `tests/testthat/test-center.R`,
  `tests/testthat/test-scale.R`

- Parameterized steps: `tests/testthat/test-normalize.R`

## Characteristics

- **`role = NA`**: Preserves existing column roles

- **No `keep_original_cols`**: Not needed since columns are modified in place

- **Returns same columns**: Modified values but same column structure

- **Simpler than create-new-columns**: Fewer parameters to handle

## Complete Template

This template follows the same pattern as `R/center.R` in the recipes
repository.

```r
#' Title for your preprocessing step
#'
#' `step_yourname()` creates a *specification* of a recipe step that will
#' [describe what the step does to the data].
#'
#' @param recipe A recipe object. The step will be added to the sequence of
#'   operations for this recipe.
#' @param ... One or more selector functions to choose variables for this step.
#'   See [recipes::selections()] for more details.
#' @param role Not used by this step since no new variables are created.
#' @param trained A logical to indicate if the quantities for preprocessing have
#'   been estimated.
#' @param [your_param] Description of your step-specific parameter. [Include
#'   type, default value, and what it controls].
#' @param columns A character vector of column names that will be populated
#'   (eventually) by the [terms] argument. This is `NULL` until computed by
#'   [prep()].
#' @param skip A logical. Should the step be skipped when the recipe is baked by
#'   [bake()]? While all operations are baked when [prep()] is run, some
#'   operations may not be able to be conducted on new data (e.g. processing the
#'   outcome variable(s)). Care should be taken when using `skip = TRUE` as it
#'   may affect the computations for subsequent operations.
#' @param id A character string that is unique to this step to identify it.
#'
#' @return An updated version of `recipe` with the new step added to the
#'   sequence of any existing operations.
#'
#' @family [your step category] steps
#' @export
#'
#' @details
#'
#' [Detailed explanation of what the step does, including any important
#' mathematical formulas or computational details.]
#'
#' The step estimates [what parameters] from the data used in the `training`
#' argument of [prep()]. [bake()] then applies [the transformation] to new
#' data sets using these [parameters].
#'
#' # Tidying
#'
#' When you [`tidy()`][recipes::tidy.recipe()] this step, a tibble is returned with
#' columns `terms`, `value`, and `id`:
#'
#' \describe{
#'   \item{terms}{character, the selectors or variables selected}
#'   \item{value}{numeric, the [description of stored values]}
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
#' biomass_tr <- biomass[biomass$dataset == "Training", ]
#' biomass_te <- biomass[biomass$dataset == "Testing", ]
#'
#' rec <- recipe(
#'   HHV ~ carbon + hydrogen + oxygen + nitrogen + sulfur,
#'   data = biomass_tr
#' )
#'
#' # Apply your step
#' step_trans <- rec |>
#'   step_yourname(carbon, hydrogen)
#'
#' # View before training
#' step_trans
#'
#' # Train the step
#' step_trained <- prep(step_trans, training = biomass_tr)
#'
#' # View after training
#' step_trained
#'
#' # Apply to new data
#' transformed_te <- bake(step_trained, biomass_te)
#'
#' # View results
#' biomass_te[1:5, c("carbon", "hydrogen")]
#' transformed_te[1:5, c("carbon", "hydrogen")]
#'
#' # View learned parameters
#' tidy(step_trans, number = 1)
#' tidy(step_trained, number = 1)
step_yourname <- function(
  recipe,
  ...,
  role = NA,
  trained = FALSE,
  your_param = default_value,
  columns = NULL,
  skip = FALSE,
  id = recipes::rand_id("yourname")
) {
  recipes::add_step(
    recipe,
    step_yourname_new(
      terms = rlang::enquos(...),
      trained = trained,
      role = role,
      your_param = your_param,
      columns = columns,
      skip = skip,
      id = id,
      case_weights = NULL
    )
  )
}

## Initialize the step - this is internal
step_yourname_new <- function(terms, role, trained, your_param, columns,
                              skip, id, case_weights) {
  recipes::step(
    subclass = "yourname",
    terms = terms,
    role = role,
    trained = trained,
    your_param = your_param,
    columns = columns,
    skip = skip,
    id = id,
    case_weights = case_weights
  )
}

#' @export
prep.step_yourname <- function(x, training, info = NULL, ...) {
  # 1. Resolve variable selections to actual column names
  # Reference: R/center.R, R/scale.R for standard prep() patterns
  col_names <- recipes::recipes_eval_select(x$terms, training, info)

  # 2. Validate column types (adjust types as needed for your step)
  recipes::check_type(training[, col_names], types = c("double", "integer"))

  # 3. Extract case weights if applicable
  wts <- recipes::get_case_weights(info, training)
  were_weights_used <- recipes::are_weights_used(wts, unsupervised = TRUE)
  if (isFALSE(were_weights_used)) {
    wts <- NULL
  }

  # 4. Compute parameters needed for transformation
  # Use for-loops over map() for consistency and better error handling
  params <- vector("list", length(col_names))
  names(params) <- col_names

  for (col_name in col_names) {
    # Your computation here
    # Example: compute mean
    if (is.null(wts)) {
      params[[col_name]] <- mean(training[[col_name]], na.rm = x$your_param)
    } else {
      # Handle weighted computation
      params[[col_name]] <- weighted.mean(
        training[[col_name]],
        w = as.double(wts),
        na.rm = x$your_param
      )
    }
  }

  # Convert list to named vector if appropriate
  params <- unlist(params)

  # 5. Optional: Add warnings or checks
  # Example: check for infinite values
  inf_cols <- col_names[is.infinite(params)]
  if (length(inf_cols) > 0) {
    cli::cli_warn(
      "Column{?s} {.var {inf_cols}} returned Inf or NaN. \\
      Consider checking your data before preprocessing."
    )
  }

  # 6. Return updated step with trained = TRUE and parameters stored
  step_yourname_new(
    terms = x$terms,
    role = x$role,
    trained = TRUE,
    your_param = x$your_param,
    columns = col_names,  # Store resolved column names
    skip = x$skip,
    id = x$id,
    case_weights = were_weights_used
  )
}

#' @export
bake.step_yourname <- function(object, new_data, ...) {
  # 1. Get column names from trained step
  col_names <- object$columns

  # 2. Validate required columns exist in new data
  recipes::check_new_data(col_names, object, new_data)

  # 3. Apply transformation using stored parameters
  # Use for-loop for consistency
  for (col_name in col_names) {
    param <- object$your_param[[col_name]]  # or however you stored it
    # Example transformation: subtract mean
    new_data[[col_name]] <- new_data[[col_name]] - param
  }

  # 4. Return modified data
  new_data
}

#' @export
print.step_yourname <- function(x, width = max(20, options()$width - 30), ...) {
  title <- "Your operation description for "
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
tidy.step_yourname <- function(x, ...) {
  if (recipes::is_trained(x)) {
    # When trained, return actual values
    res <- tibble::tibble(
      terms = names(x$your_stored_param),
      value = unname(x$your_stored_param)
    )
  } else {
    # When untrained, return placeholders
    term_names <- recipes::sel2char(x$terms)
    res <- tibble::tibble(
      terms = term_names,
      value = rlang::na_dbl
    )
  }
  res$id <- x$id
  res
}
```

## Case Weights

**INSTRUCTIONS FOR CLAUDE:** Include case weight handling based on operation
type.

### Include Case Weights IF Step Computes Statistics:

**Required when prep() aggregates across rows:**

- ✅ Mean, median, mode

- ✅ Quantiles, percentiles, quartiles (e.g., 5th, 95th percentile)

- ✅ IQR (interquartile range)

- ✅ Variance, standard deviation

- ✅ Min/Max for scaling/normalization

**Examples that NEED case weights:**

- step_center() - computes means

- step_normalize() - computes min/max or mean/sd

- step_range() - computes min/max for scaling

- step_winsorize() - computes percentiles

### Skip Case Weights IF Step Only Does Per-Row Operations:

**Not required when operation is per-row:**

- ❌ Character counting: nchar()

- ❌ NA detection: is.na()

- ❌ Simple comparisons: x < threshold

- ❌ Type conversions: as.character()

- ❌ String manipulation

- ❌ Math operations on individual values: log(), sqrt(), exp()

**Examples that DON'T need case weights:**

- step_log() - applies log() to each value

- step_sqrt() - applies sqrt() to each value

- step_mutate() - per-row transformations

### Detection Rule:

Ask: "Does prep() compute a statistic by aggregating across multiple rows?"

- **YES** → Include case weights (add parameters, implement weighted
  calculations, add tests)

- **NO** → Skip case weights entirely

**Implementation when needed:**

- Add `case_weights` parameter to constructor

- Use `get_case_weights()` and `are_weights_used()` in prep()

- Implement weighted calculations (weighted.mean, weighted quantiles, etc.)

- Add 2 case weight tests (frequency weights, importance weights)

## Key Implementation Notes

### For prep()

- **Always use `recipes_eval_select()`** to resolve variable selections

- **Use `check_type()`** to validate column types early

- **Handle case weights** with `get_case_weights()` and `are_weights_used()`

- **Use for-loops, not `map()`** for better error messages

- **Return a new step object** (don't modify in place)

- **Set `trained = TRUE`** in the returned object

### For bake()

- **Always validate** with `check_new_data()`

- **Use for-loops** for applying transformations

- **Work with columns in place** (modify `new_data` directly)

- **Return the modified data frame**

### For print()

- **Use the `print_step()` helper** function

- **Pass `case_weights`** if your step supports them

### For tidy()

- **Return a tibble** with at minimum: `terms`, relevant value columns, and `id`

- **Handle both trained and untrained states**

- **Use `sel2char()`** to convert untrained term selections to strings

## Common Patterns

### Centering (subtracting mean)

```r
prep: means <- colMeans(training[, col_names], na.rm = TRUE)
bake: new_data[[col]] <- new_data[[col]] - means[[col]]
```

### Scaling (dividing by standard deviation)

```r
prep: sds <- apply(training[, col_names], 2, sd, na.rm = TRUE)
bake: new_data[[col]] <- new_data[[col]] / sds[[col]]
```

### Log transformation

```r
prep: # No parameters to learn, just validate columns exist
bake: new_data[[col]] <- log(new_data[[col]])
```

### Range normalization [0, 1]

```r
prep:
  mins <- apply(training[, col_names], 2, min, na.rm = TRUE)
  maxs <- apply(training[, col_names], 2, max, na.rm = TRUE)
bake:
  new_data[[col]] <- (new_data[[col]] - mins[[col]]) / (maxs[[col]] - mins[[col]])
```

## Testing

See
[package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements)
for comprehensive testing guide.

### Key tests for modify-in-place steps

```r
test_that("working correctly", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourname(disp, hp)

  # Test untrained tidy()
  untrained_tidy <- tidy(rec, 1)
  expect_equal(untrained_tidy$value, rep(rlang::na_dbl, 2))

  # Test prep()
  prepped <- prep(rec, training = mtcars)

  # Verify parameters were learned correctly
  expect_equal(
    prepped$steps[[1]]$your_param,
    expected_values
  )

  # Test trained tidy()
  trained_tidy <- tidy(prepped, 1)
  expect_equal(trained_tidy$value, expected_values)

  # Test bake()
  results <- bake(prepped, mtcars)

  # Verify transformation was applied correctly
  expect_equal(
    results$disp,
    expected_transformed_values,
    tolerance = 1e-7
  )
})
```

## Next Steps

- Understand architecture: [step-architecture.md](step-architecture.md)

- Create new columns: [create-new-columns-steps.md](create-new-columns-steps.md)

- Add optional methods: [optional-methods.md](optional-methods.md)

- Learn helper functions: [helper-functions.md](helper-functions.md)

- Document your step:
  [package-roxygen-documentation.md](package-roxygen-documentation.md)

- Write tests:
  [package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements)
