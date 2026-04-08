---
name: add-recipe-step
description: Create a new preprocessing step for the recipes package following
  tidymodels conventions
---

# Add Recipe Step

Guide for developing new preprocessing steps that extend the recipes package.
This skill provides best practices, complete code templates, and testing
patterns for creating custom recipe steps.

--------------------------------------------------------------------------------

## Two Development Contexts

This skill supports **two distinct development contexts**:

### 🆕 Extension Development (Default)

**Creating a new R package** that extends recipes with custom steps.

- ✅ Use this for: New packages, standalone steps, CRAN submissions

- ⚠️ **Constraint**: Must use `recipes::` prefix for all functions

### 🔧 Source Development (Advanced)

**Contributing directly to recipes** via pull requests.

- ✅ Use this for: Contributing to tidymodels/recipes repository

- ✨ **Benefit**: Can use internal functions directly (no prefix needed)

--------------------------------------------------------------------------------

## Getting Started

**INSTRUCTIONS FOR CLAUDE:** Run the verification script first to determine the
development context:

```bash
Rscript -e 'source(Sys.glob(path.expand("~/.claude/plugins/cache/tidymodels-skills/tidymodels-dev/*/tidymodels/shared-references/scripts/verify-setup.R"))[1])'
```

**Then follow the appropriate path based on the output:**

- **Output: "All checks for source development complete."** → Go to [Source
  Development Guide](references/source-guide.md)

- **Output: "All checks for extension development complete." (no warnings)** →
  Go to [Extension Development Guide](references/extension-guide.md)

- **Output: Shows "Warning - [UUID]" messages** → Go to [Extension
  Prerequisites](references/package-extension-prerequisites.md) to resolve
  warnings first

--------------------------------------------------------------------------------

## Implementation Workflow

**INSTRUCTIONS FOR CLAUDE:** Load references progressively based on step type.

### Step 1: Read Step Type Reference ONLY

Determine step type from user requirements, then read ONLY that reference:

- **Modifies existing columns?** Read
  [modify-in-place-steps.md](references/modify-in-place-steps.md) ONLY

- **Creates new columns?** Read
  [create-new-columns-steps.md](references/create-new-columns-steps.md) ONLY

- **Filters/removes rows?** Read
  [row-operation-steps.md](references/row-operation-steps.md) ONLY

Do NOT read all three references. Read only the one needed for this step type.

### Step 2: Read Additional References If Needed

Read other references ONLY if specifically mentioned or needed:

- **User asks about helpers?** Read
  [helper-functions.md](references/helper-functions.md)

- **User mentions tunable?** Read
  [optional-methods.md](references/optional-methods.md)

- **Troubleshooting?** Read troubleshooting references

Default: Don't pre-load optional references.

--------------------------------------------------------------------------------

## Overview

Creating a custom recipe step provides:

- Integration with the recipes preprocessing pipeline

- Automatic handling of variable selection and roles

- Support for case weights

- Consistent prep/bake workflow

- Integration with tune for hyperparameter optimization

- Proper handling of grouped data frames

- Sparse data support (when applicable)

## Repository Access (Optional but Recommended)

**INSTRUCTIONS FOR CLAUDE:** Check if `repos/recipes/` exists in the current
working directory. Use this to guide development:

**If `repos/recipes/` exists:**

- ✅ Use it as a reference throughout development

- Read source files (e.g., `repos/recipes/R/center.R`) to study implementation
  patterns

- Read test files (e.g., `repos/recipes/tests/testthat/test-step_center.R`) for
  testing patterns

- Reference these files when answering complex questions or solving problems

- Look at actual code structure, validation patterns, and edge case handling

**If `repos/recipes/` does NOT exist:**

- Suggest cloning the repository using the scripts in [Repository Access
  Guide](references/package-repository-access.md)

- This is **optional but strongly recommended** for high-quality development

- If the user declines, reference files using GitHub URLs:

  - Format: `https://github.com/tidymodels/recipes/blob/main/R/[file-name].R`

  - Example: https://github.com/tidymodels/recipes/blob/main/R/center.R

  - This allows users to click through to see implementations

**When to use repository references:**

- Complex implementation questions (e.g., "How does recipes handle variable
  roles?")

- Debugging issues (compare user's code to working implementation)

- Understanding patterns (study similar steps)

- Test design (see how recipes tests edge cases)

- Architecture decisions (understand internal structure)

See [Repository Access Guide](references/package-repository-access.md) for setup
instructions.

## Quick Navigation

**Development Guides:**

- [Extension Development Guide](references/extension-guide.md) - Creating new
  packages that extend recipes

- [Source Development Guide](references/source-guide.md) - Contributing PRs to
  recipes itself

**Reference Files:**

- [Step Architecture](references/step-architecture.md) - Three-function pattern,
  prep/bake workflow, step types

- [Modify-in-Place Steps](references/modify-in-place-steps.md) - Transform
  existing columns

- [Create-New-Columns Steps](references/create-new-columns-steps.md) - Generate
  new columns

- [Row-Operation Steps](references/row-operation-steps.md) - Filter or remove
  rows

- [Optional Methods](references/optional-methods.md) - tunable(),
  required_pkgs(), sparsity methods

- [Helper Functions](references/helper-functions.md) - recipes helper function
  reference

**Shared References (Extension Development):**

- [Extension Prerequisites](references/package-extension-prerequisites.md) -
  Extension prerequisites

- [Development Workflow](references/package-development-workflow.md) - Fast
  iteration cycle

- [Testing Patterns (Extension)](references/package-testing-patterns.md) -
  Extension testing guide

- [Roxygen Documentation](references/package-roxygen-documentation.md) -
  Documentation templates

- [Package Imports](references/package-imports.md) - Managing dependencies

- [Best Practices (Extension)](references/package-best-practices.md) - Extension
  code style

- [Troubleshooting (Extension)](references/package-troubleshooting.md) -
  Extension issues

**Source Development Specific:**

- [Testing Patterns (Source)](references/testing-patterns-source.md) - Using
  internal helpers

- [Best Practices (Source)](references/best-practices-source.md) - Using
  internal functions

- [Troubleshooting (Source)](references/troubleshooting-source.md) -
  Source-specific issues

## Development Workflow

See [Development Workflow](references/package-development-workflow.md) for
complete details.

**Fast iteration cycle (run repeatedly):**

1. `devtools::document()` - Generate documentation
2. `devtools::load_all()` - Load your package
3. `devtools::test()` - Run tests

**Final validation (run once at end):**

4. `devtools::check()` - Full R CMD check

**WARNING:** Do NOT run `check()` during iteration. It takes 1-2 minutes and is
unnecessary until you're done.

## Understanding Recipe Steps

See [Step Architecture](references/step-architecture.md) for complete details.

### The Three-Function Pattern

Every recipe step consists of three functions:

1. **Step constructor** (e.g., `step_center()`) - User-facing function

   - Captures user arguments

   - Uses `enquos(...)` to capture variable selections

   - Returns recipe with step added via `add_step()`

2. **Step initialization** (e.g., `step_center_new()`) - Internal constructor

   - Minimal function with no defaults

   - Calls `step(subclass = "name", ...)` to create S3 object

3. **S3 methods** - Required methods for every step:

   - `prep.step_*()` - Estimates parameters from training data

   - `bake.step_*()` - Applies transformation to new data

   - `print.step_*()` - Displays step in recipe summary

   - `tidy.step_*()` - Returns step information as tibble

### The prep/bake Workflow

**prep() - Training phase:**

- Resolves variable selections (e.g., `all_numeric()` → actual column names)

- Validates column types

- Computes statistics/parameters from training data

- Stores learned parameters in step object

- Returns updated step with `trained = TRUE`

**bake() - Application phase:**

- Takes trained step and new data

- Validates required columns exist

- Applies transformation using stored parameters

- Returns transformed data

**Example workflow:**

```r
# Define recipe with step
rec <- recipe(mpg ~ ., data = mtcars) |>
  step_center(all_numeric_predictors())

# prep() trains the step (calculates means)
trained_rec <- prep(rec, training = mtcars)

# bake() applies the step (subtracts means)
new_data <- bake(trained_rec, new_data = mtcars)
```

## Step Type Decision Tree

Choose the appropriate template based on what your step does:

```
┌─────────────────────────────────────────────────────────────┐
│ What does your step do?                                    │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   Transform           Create new          Remove/filter
   existing            columns             rows
   columns
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  MODIFY IN  │     │   CREATE    │     │     ROW     │
│    PLACE    │     │ NEW COLUMNS │     │  OPERATION  │
└─────────────┘     └─────────────┘     └─────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
  role = NA           role =            skip = TRUE
  No keep_cols    "predictor"          (usually)
                  keep_original_cols
        │                   │                   │
        ▼                   ▼                   ▼
  Examples:           Examples:           Examples:

  - center            - dummy             - filter

  - scale             - pca               - sample

  - normalize         - interact          - naomit

  - log               - poly              - slice
```

**Decision guide:**

- **Modify-in-place**: Transforms existing columns → [Modify-in-Place
  Steps](references/modify-in-place-steps.md)

- **Create new columns**: Generates new columns from existing →
  [Create-New-Columns Steps](references/create-new-columns-steps.md)

- **Row operations**: Filters or removes rows → [Row-Operation
  Steps](references/row-operation-steps.md)

## Complete Example: Modify-in-Place Step (Centering)

This example shows all required components for a modify-in-place step **using
extension development patterns** (with `recipes::` prefix).

**For source development**, see [Source Development
Guide](references/source-guide.md) for examples using internal functions
directly.

**Reference implementation:** `R/center.R` in recipes repository

### 1. Step constructor

```r
# R/step_center.R

#' Center numeric variables
#'
#' `step_center()` creates a *specification* of a recipe step that will
#' normalize numeric data to have a mean of zero.
#'
#' @inheritParams step_normalize
#' @param ... One or more selector functions to choose variables for this step.
#'   See [recipes::selections()] for more details.
#' @param role Not used by this step since no new variables are created.
#' @param na_rm A logical value indicating whether NA values should be removed
#'   when computing means.
#' @param means A named numeric vector of means. This is `NULL` until computed
#'   by [prep()].
#'
#' @return An updated version of `recipe` with the new step added to the
#'   sequence of any existing operations.
#'
#' @family normalization steps
#' @export
#'
#' @details
#' Centering data means that the average of the variable is subtracted from the
#' data. `step_center` estimates the variable means from the data used in the
#' `training` argument of [prep()]. [bake()] then applies the centering to new
#' data sets using these means.
#'
#' # Tidying
#'
#' When you [`tidy()`][recipes::tidy.recipe()] this step, a tibble is returned
#' with columns `terms`, `value`, and `id`:
#'
#' \describe{
#'   \item{terms}{character, the selectors or variables selected}
#'   \item{value}{numeric, the means}
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
#' center_trans <- rec |>
#'   step_center(carbon, hydrogen)
#'
#' center_obj <- prep(center_trans, training = biomass_tr)
#'
#' transformed_te <- bake(center_obj, biomass_te)
#'
#' biomass_te[1:10, names(transformed_te)]
#' transformed_te
#'
#' tidy(center_trans, number = 1)
#' tidy(center_obj, number = 1)
step_center <- function(
  recipe,
  ...,
  role = NA,
  trained = FALSE,
  means = NULL,
  na_rm = TRUE,
  skip = FALSE,
  id = recipes::rand_id("center")
) {
  recipes::add_step(
    recipe,
    step_center_new(
      terms = rlang::enquos(...),
      trained = trained,
      role = role,
      means = means,
      na_rm = na_rm,
      skip = skip,
      id = id,
      case_weights = NULL
    )
  )
}

step_center_new <- function(terms, role, trained, means, na_rm, skip, id,
                            case_weights) {
  recipes::step(
    subclass = "center",
    terms = terms,
    role = role,
    trained = trained,
    means = means,
    na_rm = na_rm,
    skip = skip,
    id = id,
    case_weights = case_weights
  )
}
```

### 2. prep() method

```r
#' @export
prep.step_center <- function(x, training, info = NULL, ...) {
  # 1. Resolve variable selections to actual column names
  col_names <- recipes::recipes_eval_select(x$terms, training, info)

  # 2. Validate column types
  recipes::check_type(training[, col_names], types = c("double", "integer"))

  # 3. Extract case weights if applicable
  wts <- recipes::get_case_weights(info, training)
  were_weights_used <- recipes::are_weights_used(wts, unsupervised = TRUE)
  if (isFALSE(were_weights_used)) {
    wts <- NULL
  }

  # 4. Compute means for each column
  means <- vapply(
    training[, col_names],
    function(col) {
      if (is.null(wts)) {
        mean(col, na.rm = x$na_rm)
      } else {
        weighted.mean(col, w = as.double(wts), na.rm = x$na_rm)
      }
    },
    numeric(1)
  )

  # 5. Check for issues
  inf_cols <- col_names[is.infinite(means)]
  if (length(inf_cols) > 0) {
    cli::cli_warn(
      "Column{?s} {.var {inf_cols}} returned Inf or NaN. \\
      Consider checking your data before preprocessing."
    )
  }

  # 6. Return updated step with trained = TRUE
  step_center_new(
    terms = x$terms,
    role = x$role,
    trained = TRUE,
    means = means,
    na_rm = x$na_rm,
    skip = x$skip,
    id = x$id,
    case_weights = were_weights_used
  )
}
```

### 3. bake() method

```r
#' @export
bake.step_center <- function(object, new_data, ...) {
  # 1. Get column names from trained step
  col_names <- names(object$means)

  # 2. Validate required columns exist in new data
  recipes::check_new_data(col_names, object, new_data)

  # 3. Apply transformation
  for (col_name in col_names) {
    new_data[[col_name]] <- new_data[[col_name]] - object$means[[col_name]]
  }

  # 4. Return modified data
  new_data
}
```

### 4. print() and tidy() methods

```r
#' @export
print.step_center <- function(x, width = max(20, options()$width - 30), ...) {
  title <- "Centering for "
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
tidy.step_center <- function(x, ...) {
  if (recipes::is_trained(x)) {
    res <- tibble::tibble(
      terms = names(x$means),
      value = unname(x$means)
    )
  } else {
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

### 5. Tests

```r
# tests/testthat/test-center.R

test_that("centering works correctly", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  prepped <- prep(rec, training = mtcars)
  results <- bake(prepped, mtcars)

  # Check means are approximately zero
  expect_equal(mean(results$disp), 0, tolerance = 1e-7)
  expect_equal(mean(results$hp), 0, tolerance = 1e-7)

  # Check tidy output
  trained_tidy <- tidy(prepped, 1)
  expect_equal(trained_tidy$value, c(mean(mtcars$disp), mean(mtcars$hp)))
})

test_that("centering handles NA correctly", {
  df <- mtcars
  df$disp[1:3] <- NA

  # With na_rm = TRUE (default)
  rec_remove <- recipe(mpg ~ ., data = df) |>
    step_center(disp, na_rm = TRUE)
  prepped <- prep(rec_remove, training = df)
  results <- bake(prepped, df)

  # Mean should be computed ignoring NAs, then subtracted
  expect_true(all(is.na(results$disp[1:3])))
  expect_false(any(is.na(results$disp[4:nrow(df)])))
})

test_that("centering validates input types", {
  df <- data.frame(
    x = 1:5,
    y = letters[1:5]
  )

  rec <- recipe(~ ., data = df) |>
    step_center(y)  # Character column

  expect_error(prep(rec, training = df))
})

test_that("centering works with case weights", {
  df <- mtcars[1:10, ]
  df$weights <- c(rep(1, 5), rep(10, 5))  # Heavy weight on last 5

  rec <- recipe(mpg ~ ., data = df) |>
    step_center(disp)

  # Without weights
  rec_unweighted <- prep(rec, training = df)

  # With weights (need to add case_weights role)
  df_weighted <- df
  df_weighted$weights <- hardhat::importance_weights(df_weighted$weights)

  rec_weighted <- recipe(mpg ~ ., data = df_weighted) |>
    update_role(weights, new_role = "case_weights") |>
    step_center(disp)
  rec_weighted <- prep(rec_weighted, training = df_weighted)

  # Weighted and unweighted should differ
  expect_false(
    tidy(rec_unweighted, 1)$value[1] == tidy(rec_weighted, 1)$value[1]
  )
})
```

**Reference test pattern:** `tests/testthat/test-center.R` in recipes repository

See [Testing Patterns](references/package-testing-patterns.md) for comprehensive
testing guide.

## Implementation Guide by Step Type

### Modify-in-Place Steps

**Use for:** Transform existing columns without creating new ones.

**Pattern:** role = NA, no keep_original_cols parameter

**Complete guide:** [Modify-in-Place Steps](references/modify-in-place-steps.md)

**Key points:**

- Preserve existing column roles with `role = NA`

- Use `recipes_eval_select()` to resolve selections

- Validate with `check_type()` in prep()

- Apply transformation in place in bake()

**Examples:** center, scale, normalize, log

**Reference implementations:**

- Simple transformations: `R/center.R`, `R/scale.R`, `R/normalize.R`

- Math transformations: `R/log.R`, `R/sqrt.R`, `R/logit.R`

- With parameters: `R/BoxCox.R` (power transformation with lambda)

### Create-New-Columns Steps

**Use for:** Generate new columns from existing ones.

**Pattern:** role = "predictor", keep_original_cols parameter

**Complete guide:** [Create-New-Columns
Steps](references/create-new-columns-steps.md)

**Key points:**

- Assign role to new columns with `role = "predictor"`

- Include `keep_original_cols` parameter (default FALSE)

- Use `remove_original_cols()` helper in bake()

- Consider implementing `.recipes_estimate_sparsity()` for sparse columns

**Examples:** dummy, pca, interact, poly

**Reference implementations:**

- Encoding: `R/dummy.R` (one-hot encoding)

- Dimension reduction: `R/pca.R`, `R/ica.R`

- Feature engineering: `R/interact.R`, `R/poly.R`

### Row-Operation Steps

**Use for:** Filter or remove rows from data.

**Pattern:** skip = TRUE by default

**Complete guide:** [Row-Operation Steps](references/row-operation-steps.md)

**Key points:**

- Default `skip = TRUE` since row ops usually only for training

- prep() typically doesn't learn parameters

- bake() applies filtering logic

- Respect skip parameter in bake()

**Examples:** filter, sample, naomit, slice

**Reference implementations:**

- Filtering: `R/filter.R`, `R/filter_missing.R`

- Sampling: `R/sample.R`

- Row removal: `R/naomit.R`, `R/slice.R`

## Helper Functions

See [Helper Functions](references/helper-functions.md) for complete reference.

**Essential helpers:**

- `recipes_eval_select()` - Convert selections to column names (prep)

- `check_type()` - Validate column types (prep)

- `check_new_data()` - Verify columns exist (bake)

- `get_case_weights()` - Extract case weights (prep)

- `are_weights_used()` - Check if weights apply (prep)

- `remove_original_cols()` - Handle keep_original_cols (bake)

- `print_step()` - Standard printing (print)

- `sel2char()` - Convert selections to strings (tidy)

## Optional Methods

See [Optional Methods](references/optional-methods.md) for complete details.

**Optional S3 methods:**

- `tunable()` - Declare parameters for tune package

- `required_pkgs()` - Declare external package dependencies

- `.recipes_preserve_sparsity()` - Indicate sparse preservation

- `.recipes_estimate_sparsity()` - Estimate sparsity of new columns

## Documentation

See [Roxygen Documentation](references/package-roxygen-documentation.md) for
complete templates.

**Required roxygen tags:**

```r
#' @inheritParams step_center
#' @param ... One or more selector functions
#' @param role Role for new variables (or NA)
#' @param trained Logical for training status
#' @param [params] Step-specific parameters
#' @return Updated recipe object
#' @family [category] steps
#' @export
```

## Testing

See [Testing Patterns (Extension)](references/package-testing-patterns.md) for
comprehensive guide.

**Required test categories:** 1. **Correctness**: Step transforms data correctly
2. **Variable selection**: Works with all_numeric(), all_predictors(), etc. 3.
**NA handling**: Both na_rm = TRUE and FALSE 4. **Case weights**: Weighted and
unweighted differ 5. **Infrastructure**: Works in full recipe pipeline 6. **Edge
cases**: Empty data, all same values, etc.

## Package-Specific Patterns (Source Development)

If you're contributing to recipes itself, you have access to internal functions
and conventions not available in extension development.

### File Naming Conventions

Recipes organizes steps by category:

- Normalization: `R/center.R`, `R/scale.R`, `R/normalize.R`

- Encoding: `R/dummy.R`, `R/novel.R`, `R/other.R`

- Dimension reduction: `R/pca.R`, `R/ica.R`

- Row operations: `R/filter.R`, `R/sample.R`

- Tests: `tests/testthat/test-center.R`

### Internal Functions Available

When developing recipes itself, you can use functions directly (no `recipes::`
prefix):

- `recipes_eval_select()` - Variable selection

- `get_case_weights()`, `are_weights_used()` - Case weight handling

- `check_type()` - Column type validation

- `check_new_data()` - Verify columns exist in new data

- `remove_original_cols()` - Handle keep_original_cols

- `print_step()` - Standard printing

- `sel2char()` - Convert selections to strings

### Documentation Patterns

Recipes uses extensive parameter inheritance:

```r
#' @inheritParams step_normalize
#' @template step-return
#' @template case-weights-unsupervised
```

### The Three-Function Pattern (Source)

```r
# 1. Constructor (exported)
step_center <- function(recipe, ..., role = NA, ...) {
  add_step(recipe, step_center_new(...))
}

# 2. Initialization (internal)
step_center_new <- function(terms, role, trained, ...) {
  step(subclass = "center", ...)
}

# 3. Methods (all exported)
prep.step_center <- function(x, training, info = NULL, ...) {
  # Use internal functions directly
  col_names <- recipes_eval_select(x$terms, training, info)
  check_type(training[, col_names], types = c("double", "integer"))
  # ...
}
```

**Complete source development guide:** [Source Development
Guide](references/source-guide.md)

--------------------------------------------------------------------------------

## Best Practices

See [Best Practices](references/package-best-practices.md) for complete guide.

**Key principles:**

- Use base pipe `|>` not magrittr pipe `%>%`

- Prefer for-loops over `purrr::map()` for better error messages

- Use `cli::cli_abort()` for error messages

- Validate early (in prep), trust data in bake

- Use recipes helpers instead of reimplementing

## Troubleshooting

See [Troubleshooting (Extension)](references/package-troubleshooting.md) for
complete guide.

**Common issues:**

- "No visible global function definition" → Add to package imports

- "Object not found" in tests → Use `devtools::load_all()` before testing

- Column selection not working → Check `recipes_eval_select()` usage

- Case weights ignored → Check conversion of hardhat weights

## Related Skills

- [add-yardstick-metric](../add-yardstick-metric/SKILL.md) - Custom recipe steps
  may generate outputs that need custom metrics

- [add-dials-parameter](../add-dials-parameter/SKILL.md) - Recipe steps often
  have tunable parameters that can be optimized

- [add-parsnip-model](../add-parsnip-model/SKILL.md) - Preprocessed data flows
  into model specifications

- [add-parsnip-engine](../add-parsnip-engine/SKILL.md) - Recipe steps prepare
  data for model engines

## Next Steps

**For Extension Development (creating new packages):**

1. **Extension prerequisites:** [Extension
   Prerequisites](references/package-extension-prerequisites.md) - START HERE

**For Source Development (contributing to recipes):**

1. **Start here:** [Source Development Guide](references/source-guide.md)
2. **Clone repository:** See [Repository
   Access](references/package-repository-access.md)
3. **Study existing steps:** Browse `R/center.R`, `R/dummy.R`, `R/pca.R`, etc.
4. **Follow package conventions:** File naming, internal functions,
   three-function pattern
5. **Test with internal helpers:** See [Testing Patterns
   (Source)](references/testing-patterns-source.md)
6. **Submit PR:** See [Source Development Guide](references/source-guide.md) for
   PR process
