# Extension Development Guide: Recipe Steps

Complete guide for creating new packages that extend recipes with custom preprocessing steps.

---

## When to Use This Guide

✅ **Use this guide if you are:**
- Creating a **new R package** that adds custom recipe steps
- Building on recipes' foundation without modifying recipes itself
- Publishing steps to CRAN or sharing privately
- Want to avoid tight coupling with recipes internals

❌ **Don't use this guide if you are:**
- Contributing a PR directly to the recipes package → Use [Source Development Guide](source-guide.md)
- Working inside the recipes repository → Use [Source Development Guide](source-guide.md)

---

## Prerequisites

### Quick Package Setup

See [R Package Setup](../../shared-references/r-package-setup.md) for complete details, including optional Claude Code setup.

```r
# Check if this is a new package or existing package
if (!file.exists("DESCRIPTION")) {
  # New package - create full structure
  usethis::create_package(".", open = FALSE)
  usethis::use_mit_license()
  usethis::use_package("recipes")
  usethis::use_package("rlang")
  usethis::use_package("tibble")
  usethis::use_package("vctrs")
  usethis::use_package("cli")
  usethis::use_testthat()
  usethis::use_package("modeldata", type = "Suggests")
} else {
  # Existing package - ensure dependencies
  usethis::use_package("recipes")
  usethis::use_package("rlang")
  usethis::use_package("tibble")
  usethis::use_package("vctrs")
  usethis::use_package("cli")
  if (!dir.exists("tests/testthat")) {
    usethis::use_testthat()
  }
  usethis::use_package("modeldata", type = "Suggests")
}

# Optional: Set up Claude Code integration (if using Claude Code for development)
# Requires usethis >= 3.2.1.9000
if (packageVersion("usethis") >= "3.2.1.9000") {
  usethis::use_claude_code()
  # This adds tidyverse R package development patterns that complement
  # the recipes-specific guidance in this skill
}
```

---

## Key Constraints for Extension Development

### ❌ Never Use Internal Functions

**Critical:** You CANNOT use functions accessed with `:::`.

```r
# ❌ BAD - Will break, not exported
recipes:::recipes_eval_select(terms, data, info)

# ✅ GOOD - Use exported function
recipes::recipes_eval_select(terms, data, info)
```

**Why?**
- Internal functions are not guaranteed to be stable
- They can change without notice
- Your package will fail CRAN checks
- Users will get cryptic errors

### ✅ Only Use Exported Functions

Safe to use:
- `recipes::recipes_eval_select()`
- `recipes::get_case_weights()`
- `recipes::are_weights_used()`
- `recipes::check_type()`
- `recipes::check_new_data()`
- `recipes::add_step()`
- `recipes::step()`
- `recipes::print_step()`
- `recipes::sel2char()`
- `recipes::is_trained()`
- `recipes::rand_id()`
- `recipes::remove_original_cols()` (for create-new-columns steps)

---

## Step Type Decision

Choose based on what your step does:

### Modify-in-Place Steps

Transforms existing columns (e.g., centering, scaling):
- Use `role = NA`
- No `keep_original_cols` parameter
- Columns keep their names

### Create-New-Columns Steps

Generates new columns (e.g., dummy variables, PCA):
- Use `role = "predictor"`
- Include `keep_original_cols` parameter
- Original columns typically removed

### Row-Operation Steps

Filters or removes rows (e.g., filtering, sampling):
- Default `skip = TRUE`
- Usually only applied to training data

See [Step Architecture](step-architecture.md) for detailed decision tree.

---

## Step-by-Step Implementation

### Step 1: Create Step Constructor

```r
# R/step_center.R

#' Center numeric variables
#'
#' @inheritParams recipes::step_normalize
#' @param ... One or more selector functions to choose variables for this step.
#' @param role Not used by this step since no new variables are created.
#' @param na_rm A logical value indicating whether NA values should be removed
#'   when computing means.
#' @param means A named numeric vector of means. This is `NULL` until computed
#'   by [prep()].
#'
#' @return An updated version of `recipe` with the new step added.
#'
#' @family normalization steps
#' @export
#'
#' @examples
#' library(recipes)
#'
#' rec <- recipe(mpg ~ ., data = mtcars) |>
#'   step_center(disp, hp)
#'
#' prepped <- prep(rec, training = mtcars)
#' baked <- bake(prepped, mtcars)
#'
#' # Columns are centered
#' mean(baked$disp)  # Approximately 0
#'
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
```

### Step 2: Create Step Initialization Function

```r
# Internal constructor with no defaults
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

### Step 3: Create prep() Method

```r
#' @export
prep.step_center <- function(x, training, info = NULL, ...) {
  # 1. Resolve variable selections to actual column names
  col_names <- recipes::recipes_eval_select(x$terms, training, info)

  # 2. Validate column types (exported function)
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
      "Column{?s} {.var {inf_cols}} returned Inf or NaN."
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

### Step 4: Create bake() Method

```r
#' @export
bake.step_center <- function(object, new_data, ...) {
  # 1. Get column names from trained step
  col_names <- names(object$means)

  # 2. Validate required columns exist in new data (exported function)
  recipes::check_new_data(col_names, object, new_data)

  # 3. Apply transformation
  for (col_name in col_names) {
    new_data[[col_name]] <- new_data[[col_name]] - object$means[[col_name]]
  }

  # 4. Return modified data
  new_data
}
```

### Step 5: Create print() and tidy() Methods

```r
#' @export
print.step_center <- function(x, width = max(20, options()$width - 30), ...) {
  title <- "Centering for "

  # Use exported helper
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

### Step 6: Test Your Step

```r
# tests/testthat/test-step_center.R

test_that("centering works correctly", {
  rec <- recipes::recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  prepped <- recipes::prep(rec, training = mtcars)
  results <- recipes::bake(prepped, mtcars)

  # Check means are approximately zero
  expect_equal(mean(results$disp), 0, tolerance = 1e-7)
  expect_equal(mean(results$hp), 0, tolerance = 1e-7)
})

test_that("centering handles NA correctly", {
  df <- mtcars
  df$disp[1:3] <- NA

  rec <- recipes::recipe(mpg ~ ., data = df) |>
    step_center(disp, na_rm = TRUE)

  prepped <- recipes::prep(rec, training = df)
  results <- recipes::bake(prepped, df)

  # NA values should remain NA
  expect_true(all(is.na(results$disp[1:3])))
  expect_false(any(is.na(results$disp[4:nrow(df)])))
})

test_that("centering validates input types", {
  df <- data.frame(
    x = 1:5,
    y = letters[1:5]
  )

  rec <- recipes::recipe(~ ., data = df) |>
    step_center(y)  # Character column

  expect_error(recipes::prep(rec, training = df))
})
```

See [Testing Patterns (Extension)](../../shared-references/testing-patterns-extension.md) for comprehensive testing guide.

---

## Complete Examples

### Create-New-Columns Step

For steps that create new columns (like dummy variables):

```r
step_dummy_simple <- function(
  recipe,
  ...,
  role = "predictor",
  trained = FALSE,
  levels = NULL,
  keep_original_cols = FALSE,
  skip = FALSE,
  id = recipes::rand_id("dummy_simple")
) {
  recipes::add_step(
    recipe,
    step_dummy_simple_new(
      terms = rlang::enquos(...),
      role = role,
      trained = trained,
      levels = levels,
      keep_original_cols = keep_original_cols,
      skip = skip,
      id = id
    )
  )
}

step_dummy_simple_new <- function(terms, role, trained, levels,
                                  keep_original_cols, skip, id) {
  recipes::step(
    subclass = "dummy_simple",
    terms = terms,
    role = role,
    trained = trained,
    levels = levels,
    keep_original_cols = keep_original_cols,
    skip = skip,
    id = id
  )
}

#' @export
prep.step_dummy_simple <- function(x, training, info = NULL, ...) {
  col_names <- recipes::recipes_eval_select(x$terms, training, info)

  # Get factor levels
  levels <- lapply(training[, col_names], levels)

  step_dummy_simple_new(
    terms = x$terms,
    role = x$role,
    trained = TRUE,
    levels = levels,
    keep_original_cols = x$keep_original_cols,
    skip = x$skip,
    id = x$id
  )
}

#' @export
bake.step_dummy_simple <- function(object, new_data, ...) {
  col_names <- names(object$levels)
  recipes::check_new_data(col_names, object, new_data)

  # Create dummy variables
  for (col_name in col_names) {
    col_levels <- object$levels[[col_name]]

    # Create dummy columns (excluding first level)
    for (i in seq_along(col_levels)[-1]) {
      new_col_name <- paste0(col_name, "_", col_levels[i])
      new_data[[new_col_name]] <- as.integer(new_data[[col_name]] == col_levels[i])
    }
  }

  # Handle keep_original_cols (exported helper)
  new_data <- recipes::remove_original_cols(new_data, object, col_names)

  new_data
}
```

---

## Common Patterns

### Handling Case Weights

```r
# Extract weights
wts <- recipes::get_case_weights(info, training)
were_weights_used <- recipes::are_weights_used(wts, unsupervised = TRUE)

if (isFALSE(were_weights_used)) {
  wts <- NULL
}

# Use in calculations
if (is.null(wts)) {
  mean(x)
} else {
  weighted.mean(x, w = as.double(wts))
}
```

### Variable Selection

Always use `recipes_eval_select()`:

```r
# Resolves all selectors: all_numeric(), all_predictors(), manual selection
col_names <- recipes::recipes_eval_select(x$terms, training, info)
```

### Type Validation

```r
# Validate column types
recipes::check_type(
  training[, col_names],
  types = c("double", "integer")
)
```

### Checking New Data

```r
# In bake(), verify columns exist
recipes::check_new_data(col_names, object, new_data)
```

---

## Development Workflow

See [Development Workflow](../../shared-references/development-workflow.md) for complete details.

**Fast iteration cycle:**
1. `devtools::document()` - Generate documentation
2. `devtools::load_all()` - Load your package
3. `devtools::test()` - Run tests

**Final validation:**
4. `devtools::check()` - Full R CMD check

---

## Package Integration

### Package-Level Documentation

Create `R/{packagename}-package.R`:

```r
#' @keywords internal
"_PACKAGE"

#' @importFrom rlang .data := !! enquo enquos
#' @importFrom recipes add_step step recipes_eval_select
NULL
```

---

## Testing

See [Testing Patterns (Extension)](../../shared-references/testing-patterns-extension.md) for comprehensive guide.

**Required test categories:**
1. **Correctness**: Step transforms data correctly
2. **Variable selection**: Works with selectors
3. **NA handling**: Both `na_rm = TRUE` and `FALSE`
4. **Case weights**: Weighted and unweighted differ
5. **Infrastructure**: Works in full recipe pipeline
6. **Edge cases**: Empty selection, single column

---

## Best Practices

See [Best Practices (Extension)](../../shared-references/best-practices-extension.md) for complete guide.

**Key principles:**
- Use base pipe `|>` not `%>%`
- Prefer for-loops over `purrr::map()`
- Use `cli::cli_abort()` for error messages
- Validate early (in prep), trust data in bake
- Use recipes helpers instead of reimplementing

---

## Troubleshooting

See [Troubleshooting (Extension)](../../shared-references/troubleshooting-extension.md) for complete guide.

**Common issues:**
- Column selection not working → Check `recipes_eval_select()` usage
- Type errors in bake() → Add validation in prep()
- Case weights ignored → Check conversion of hardhat weights
- "Object not found" → Use `devtools::load_all()` before testing

---

## Reference Documentation

### Step Types
- [Step Architecture](step-architecture.md) - Three-function pattern
- [Modify-in-Place Steps](modify-in-place-steps.md)
- [Create-New-Columns Steps](create-new-columns-steps.md)
- [Row-Operation Steps](row-operation-steps.md)

### Core Concepts
- [Helper Functions](helper-functions.md)
- [Optional Methods](optional-methods.md)

### Shared References
- [R Package Setup](../../shared-references/r-package-setup.md)
- [Development Workflow](../../shared-references/development-workflow.md)
- [Testing Patterns](../../shared-references/testing-patterns-extension.md)
- [Roxygen Documentation](../../shared-references/roxygen-documentation.md)
- [Best Practices](../../shared-references/best-practices-extension.md)
- [Troubleshooting](../../shared-references/troubleshooting-extension.md)

---

## Next Steps

1. **Set up your package** following [R Package Setup](../../shared-references/r-package-setup.md)
2. **Choose your step type** from [Step Architecture](step-architecture.md)
3. **Implement your step** following the guide above
4. **Test thoroughly** using [Testing Patterns](../../shared-references/testing-patterns-extension.md)
5. **Run `devtools::check()`** to ensure CRAN compliance
6. **Publish** to CRAN or share with your team

---

## Getting Help

- Check [Troubleshooting Guide](../../shared-references/troubleshooting-extension.md)
- Review [Step Architecture](step-architecture.md)
- Study the main [recipes SKILL.md](SKILL.md) for more details
- Search GitHub issues: https://github.com/tidymodels/recipes/issues
