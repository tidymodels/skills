# Creating Row-Operation Steps

This template is for steps that add, remove, or filter rows from the data.

## Overview

Row-operation steps:
- Change the number of rows in the dataset
- Often used only during training (not on new data)
- Typically have `skip = TRUE` by default
- Examples: `step_filter`, `step_sample`, `step_naomit`, `step_slice`

**Canonical implementations in recipes:**
- Filtering: `R/filter.R` (conditional filtering), `R/filter_missing.R`
- Sampling: `R/sample.R` (random sampling)
- Row removal: `R/naomit.R` (remove NAs), `R/slice.R` (select rows by position)

**Test patterns:**
- Skip behavior: `tests/testthat/test-filter.R`
- Sampling: `tests/testthat/test-sample.R`

> **Source Development:** When contributing to recipes itself, internal helpers are available without the `recipes::` prefix. Row operations are simpler but still benefit from helpers like `recipes_eval_select()` when applicable. See [Best Practices (Source)](best-practices-source.md).

## Key Characteristics

1. **`skip = TRUE` default**: Most row operations should not be applied to new data during `bake()`
2. **Often no parameters learned**: Many row operations don't need `prep()` to learn anything
3. **Used primarily in training**: Filtering, sampling, and similar operations typically only apply to training data
4. **May affect downstream steps**: Removing rows can impact statistics computed by later steps

## When skip = TRUE Makes Sense

Most row operations should skip during prediction:

```r
# Training: remove rows with missing values
recipe(y ~ ., data = train) |>
  step_naomit(all_predictors())  # skip = TRUE by default

# During bake() on new data, missing values are NOT removed
# because we need to make predictions for all new observations
```

**Typical skip = TRUE cases:**
- Removing outliers (we want to predict for outliers in new data)
- Sampling rows (we want all new data, not a sample)
- Filtering based on criteria (new data may not meet the criteria)

## When skip = FALSE Makes Sense

Rare cases where row operations should apply to new data:

- Removing rows that are mathematically impossible to process
- Enforcing data quality requirements that apply universally

**Use skip = FALSE cautiously** - usually better to handle at the data preparation stage.

## Complete Template

This template follows the same pattern as `R/filter.R` and `R/sample.R` in the recipes repository.

```r
#' Title for your row operation step
#'
#' `step_yourrowop()` creates a *specification* of a recipe step that will
#' [describe what rows are affected and how].
#'
#' @inheritParams step_center
#' @param ... One or more selector functions to choose variables for this step.
#'   See [recipes::selections()] for more details. For some row operations,
#'   this may not be needed.
#' @param [your_params] Description of step-specific parameters that control
#'   which rows are affected.
#' @param skip A logical. Should the step be skipped when the recipe is baked by
#'   [bake()]? While all operations are baked when [prep()] is run, some
#'   operations may not be able to be conducted on new data (e.g. processing the
#'   outcome variable(s)). Care should be taken when using `skip = TRUE` as it
#'   may affect the computations for subsequent operations. **Note that the
#'   default for this step is `skip = TRUE`** since row operations are typically
#'   only appropriate for the training data.
#' @param id A character string that is unique to this step to identify it.
#'
#' @return An updated version of `recipe` with the new step added to the
#'   sequence of any existing operations.
#'
#' @family row operation steps
#' @export
#'
#' @details
#'
#' [Detailed explanation of what the step does to rows.]
#'
#' Since this step is typically only applied to the training data, it defaults
#' to `skip = TRUE`. This means that during [bake()] on new data, this step
#' will be skipped and all rows will be retained.
#'
#' When you [`tidy()`][recipes::tidy.recipe()] this step, a tibble is returned with
#' columns describing the operation and `id`:
#'
#' \describe{
#'   \item{...}{[columns specific to your operation]}
#'   \item{id}{character, id of this step}
#' }
#'
#' @examplesIf rlang::is_installed("modeldata")
#' data(biomass, package = "modeldata")
#'
#' biomass_tr <- biomass[biomass$dataset == "Training", ]
#' biomass_te <- biomass[biomass$dataset == "Testing", ]
#'
#' rec <- recipe(HHV ~ ., data = biomass_tr)
#'
#' # Apply row operation
#' step_filtered <- rec |>
#'   step_yourrowop(carbon, threshold = 45)
#'
#' # Train the recipe
#' step_trained <- prep(step_filtered, training = biomass_tr)
#'
#' # During prep, rows are filtered
#' prepped_data <- bake(step_trained, new_data = NULL)  # Returns training data
#' nrow(biomass_tr)
#' nrow(prepped_data)  # Fewer rows
#'
#' # During bake on new data, step is skipped (default skip = TRUE)
#' test_data <- bake(step_trained, biomass_te)
#' nrow(biomass_te)
#' nrow(test_data)  # Same number of rows
#'
#' tidy(step_filtered, number = 1)
#' tidy(step_trained, number = 1)
step_yourrowop <- function(
  recipe,
  ...,
  your_param = default_value,
  skip = TRUE,  # Note: TRUE by default for row operations
  id = recipes::rand_id("yourrowop")
) {
  recipes::add_step(
    recipe,
    step_yourrowop_new(
      terms = rlang::enquos(...),
      your_param = your_param,
      skip = skip,
      id = id
    )
  )
}

step_yourrowop_new <- function(terms, your_param, skip, id) {
  recipes::step(
    subclass = "yourrowop",
    terms = terms,
    your_param = your_param,
    skip = skip,
    id = id
  )
}

#' @export
prep.step_yourrowop <- function(x, training, info = NULL, ...) {
  # 1. Resolve variable selections if needed
  col_names <- recipes::recipes_eval_select(x$terms, training, info)

  # 2. Validate if needed
  recipes::check_type(training[, col_names], types = c("double", "integer"))

  # 3. For most row operations, no parameters are learned
  # Just store the column names if needed

  # 4. Return updated step
  step_yourrowop_new(
    terms = x$terms,
    your_param = x$your_param,
    skip = x$skip,
    id = x$id
  )
}

#' @export
bake.step_yourrowop <- function(object, new_data, ...) {
  # Row operations respect the skip parameter
  # If skip = TRUE (default), return data unchanged
  # If skip = FALSE, apply the operation

  # Apply your row operation
  # Example: filter rows based on criteria
  condition <- new_data[[column]] > object$your_param
  new_data[condition, ]
}

#' @export
print.step_yourrowop <- function(x, width = max(20, options()$width - 30), ...) {
  title <- "Row operation on "
  recipes::print_step(
    x$columns,
    x$terms,
    x$trained,
    title,
    width
  )
  invisible(x)
}

#' @rdname tidy.recipe
#' @export
tidy.step_yourrowop <- function(x, ...) {
  # Return information about the operation
  res <- tibble::tibble(
    # Your operation-specific columns
    operation = "your_operation",
    parameter = x$your_param
  )
  res$id <- x$id
  res
}
```

## Common Patterns

### Filtering based on condition

```r
prep:
  # Usually no learning needed
  col_names <- recipes_eval_select(x$terms, training, info)

bake:
  condition <- new_data[[col]] > threshold
  new_data[condition, ]
```

### Removing NA values

```r
prep:
  # No learning needed
  col_names <- recipes_eval_select(x$terms, training, info)

bake:
  complete_rows <- complete.cases(new_data[, col_names])
  new_data[complete_rows, ]
```

### Random sampling

```r
prep:
  # Could store seed or sample size
  n <- floor(nrow(training) * x$prop)

bake:
  if (nrow(new_data) <= object$n) {
    new_data  # Return all if fewer rows than sample size
  } else {
    new_data[sample(nrow(new_data), object$n), ]
  }
```

### Removing outliers

```r
prep:
  # Learn outlier bounds from training data
  col_names <- recipes_eval_select(x$terms, training, info)

  bounds <- list()
  for (col in col_names) {
    q <- quantile(training[[col]], c(0.025, 0.975), na.rm = TRUE)
    bounds[[col]] <- list(lower = q[1], upper = q[2])
  }

  # Store bounds for use in bake

bake:
  # Remove rows outside bounds
  keep <- rep(TRUE, nrow(new_data))
  for (col in names(object$bounds)) {
    keep <- keep &
      new_data[[col]] >= object$bounds[[col]]$lower &
      new_data[[col]] <= object$bounds[[col]]$upper
  }
  new_data[keep, ]
```

## Testing Row-Operation Steps

See [package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements) for comprehensive testing guide.

### Key tests for row-operation steps

```r
test_that("row operation works correctly", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourrowop(disp, threshold = 200)

  prepped <- prep(rec, training = mtcars)

  # Test that prep applies the operation
  train_processed <- bake(prepped, new_data = NULL)
  expect_lt(nrow(train_processed), nrow(mtcars))

  # Test that bake skips by default (skip = TRUE)
  test_processed <- bake(prepped, new_data = mtcars)
  expect_equal(nrow(test_processed), nrow(mtcars))
})

test_that("skip parameter works correctly", {
  # With skip = FALSE, operation applies to new data
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourrowop(disp, threshold = 200, skip = FALSE)

  prepped <- prep(rec, training = mtcars)
  test_processed <- bake(prepped, new_data = mtcars)

  expect_lt(nrow(test_processed), nrow(mtcars))
})

test_that("handles edge cases", {
  # Test with all rows filtered out
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_yourrowop(disp, threshold = 1000)  # No cars have disp > 1000

  prepped <- prep(rec, training = mtcars)
  result <- bake(prepped, new_data = NULL)

  expect_equal(nrow(result), 0)
  expect_equal(names(result), names(mtcars))  # Column structure preserved
})
```

## Important Considerations

### Impact on downstream steps

Row operations affect what subsequent steps see:

```r
recipe(y ~ ., data = train) |>
  step_filter(x > 10) |>      # Removes some rows
  step_center(all_numeric())   # Centers on remaining rows only

# The centering is computed on the filtered data!
```

### Working with outcomes

Be careful with row operations on outcome variables:

```r
# Filtering based on outcome is often problematic
recipe(y ~ ., data = train) |>
  step_filter(y > 0)  # Removes certain outcome values

# This is usually better handled in data preparation, not in recipe
```

### Sampling considerations

Random sampling steps should consider:
- Setting seeds for reproducibility
- Stratification if needed
- Sample size vs data size

## When Not to Use Row Operations

Consider alternatives in these cases:

1. **Data quality issues**: Fix in data preparation before recipe
2. **Outcome-based filtering**: Handle before modeling workflow
3. **Complex logic**: Multiple criteria may be better as data prep
4. **Validation requirements**: Apply to all data, not just training

## Next Steps

- Understand architecture: [step-architecture.md](step-architecture.md)
- Modify in place: [modify-in-place-steps.md](modify-in-place-steps.md)
- Create new columns: [create-new-columns-steps.md](create-new-columns-steps.md)
- Add optional methods: [optional-methods.md](optional-methods.md)
- Learn helper functions: [helper-functions.md](helper-functions.md)
- Document your step: [package-roxygen-documentation.md](package-roxygen-documentation.md)
- Write tests: [package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements)
