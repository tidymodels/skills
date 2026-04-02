# Source Development Guide: Contributing to Recipes

Complete guide for contributing new preprocessing steps to the recipes package itself.

---

## When to Use This Guide

✅ **Use this guide if you are:**

- Contributing a PR directly to the recipes package

- Working inside the recipes repository

- Adding steps that should be part of recipes core

- Modifying existing recipes steps

❌ **Don't use this guide if you are:**

- Creating a new package that extends recipes → Use [Extension Development Guide](extension-guide.md)

- Building standalone steps → Use [Extension Development Guide](extension-guide.md)

---

## Prerequisites

### Clone the Recipes Repository

```bash
# Clone from GitHub
git clone https://github.com/tidymodels/recipes.git
cd recipes

# Create a feature branch
git checkout -b feature/add-step-name
```

See [Repository Access](package-repository-access.md) for more details.

### Install Development Dependencies

```r
# Install recipes with all dependencies
devtools::install_dev_deps()

# Load the package for development
devtools::load_all()
```

---

## Understanding Recipes Architecture

### Package Organization

```
recipes/
├── R/
│   ├── center.R         # Normalization steps
│   ├── dummy.R          # Encoding steps
│   ├── pca.R            # Dimension reduction
│   ├── filter.R         # Row operations
│   ├── aaa-*.R          # Core infrastructure
│   └── utils-*.R        # Internal utilities
├── tests/testthat/
│   ├── test-center.R
│   ├── test-dummy.R
│   └── helper-*.R       # Test helpers
└── man/                 # Documentation
```

### File Naming Conventions

**Source files:** `R/[step_name].R`

- Examples: `center.R`, `normalize.R`, `pca.R`, `dummy.R`

**Test files:** `tests/testthat/test-[step_name].R`

- Examples: `test-center.R`, `test-normalize.R`

---

## Working with Internal Functions

### ✅ You CAN Use Internal Functions

When developing recipes itself, internal functions are available:

```r
# ✅ GOOD - You're developing the package
prep.step_center <- function(x, training, info = NULL, ...) {
  # Use internal function (no prefix needed)
  col_names <- recipes_eval_select(x$terms, training, info)

  # Core calculation
  # ...
}
```

### Common Internal Helpers

#### `recipes_eval_select()` - Variable Selection

The most important function for resolving variable selections:

```r
# Converts all_numeric(), manual selections, etc. to column names
col_names <- recipes_eval_select(x$terms, training, info)
```

#### `get_case_weights()` - Extract Case Weights

```r
wts <- get_case_weights(info, training)
were_weights_used <- are_weights_used(wts, unsupervised = TRUE)

if (isFALSE(were_weights_used)) {
  wts <- NULL
}
```

#### `check_type()` - Validate Column Types

```r
# Validates that columns are the correct type
check_type(training[, col_names], types = c("double", "integer"))
```

#### `check_new_data()` - Validate Columns Exist

```r
# In bake(), check required columns exist
check_new_data(col_names, object, new_data)
```

#### `remove_original_cols()` - Handle keep_original_cols

```r
# For create-new-columns steps
new_data <- remove_original_cols(new_data, object, original_cols)
```

#### `print_step()` - Standard Printing

```r
print_step(x$columns, x$terms, x$trained, title, width,
           case_weights = x$case_weights)
```

#### `sel2char()` - Convert Selections to Strings

```r
# For tidy() on untrained steps
term_names <- sel2char(x$terms)
```

See [Best Practices (Source)](best-practices-source.md) for complete guide to internal functions.

---

## Step-by-Step Implementation

### Step 1: Choose Your Step Type

Determine which category your step falls into:

- **Modify-in-place**: Transforms existing columns

- **Create-new-columns**: Generates new columns

- **Row-operation**: Filters or removes rows

See [Step Architecture](step-architecture.md) for decision tree.

### Step 2: Create Source File

Create `R/[step_name].R`:

```r
# R/center.R

#' Center numeric variables
#'
#' `step_center()` creates a *specification* of a recipe step that will
#' normalize numeric data to have a mean of zero.
#'
#' @inheritParams step_normalize
#' @param ... One or more selector functions to choose variables for this step.
#'   See [selections()] for more details.
#' @param role Not used by this step since no new variables are created.
#' @param na_rm A logical value indicating whether NA values should be removed
#'   when computing means.
#' @param means A named numeric vector of means. This is `NULL` until computed
#'   by [prep()].
#'
#' @template step-return
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
#' @template case-weights-unsupervised
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
step_center <- function(
  recipe,
  ...,
  role = NA,
  trained = FALSE,
  means = NULL,
  na_rm = TRUE,
  skip = FALSE,
  id = rand_id("center")
) {
  add_step(
    recipe,
    step_center_new(
      terms = enquos(...),
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
  step(
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

#' @export
prep.step_center <- function(x, training, info = NULL, ...) {
  # 1. Resolve variable selections (internal function)
  col_names <- recipes_eval_select(x$terms, training, info)

  # 2. Validate column types (internal function)
  check_type(training[, col_names], types = c("double", "integer"))

  # 3. Get case weights (internal function)
  wts <- get_case_weights(info, training)
  were_weights_used <- are_weights_used(wts, unsupervised = TRUE)
  if (isFALSE(were_weights_used)) {
    wts <- NULL
  }

  # 4. Calculate means
  means <- vapply(
    training[, col_names],
    weighted_mean,  # Could use internal helper if it exists
    numeric(1),
    wts = wts,
    na_rm = x$na_rm
  )

  # 5. Check for issues
  inf_cols <- col_names[is.infinite(means)]
  if (length(inf_cols) > 0) {
    cli::cli_warn(
      "Column{?s} {.var {inf_cols}} returned Inf or NaN."
    )
  }

  # 6. Return updated step
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

#' @export
bake.step_center <- function(object, new_data, ...) {
  col_names <- names(object$means)

  # Validate columns exist (internal function)
  check_new_data(col_names, object, new_data)

  # Apply transformation
  for (col_name in col_names) {
    new_data[[col_name]] <- new_data[[col_name]] - object$means[[col_name]]
  }

  new_data
}

#' @export
print.step_center <- function(x, width = max(20, options()$width - 30), ...) {
  title <- "Centering for "

  # Use internal print helper
  print_step(x$columns, x$terms, x$trained, title, width,
             case_weights = x$case_weights)

  invisible(x)
}

#' @rdname tidy.recipe
#' @export
tidy.step_center <- function(x, ...) {
  if (is_trained(x)) {
    res <- tibble(
      terms = names(x$means),
      value = unname(x$means)
    )
  } else {
    # Use internal helper
    term_names <- sel2char(x$terms)
    res <- tibble(
      terms = term_names,
      value = na_dbl
    )
  }
  res$id <- x$id
  res
}
```

### Step 3: Create Test File

Create `tests/testthat/test-center.R`:

```r
test_that("centering works correctly", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  prepped <- prep(rec, training = mtcars)
  results <- bake(prepped, mtcars)

  expect_equal(mean(results$disp), 0, tolerance = 1e-7)
  expect_equal(mean(results$hp), 0, tolerance = 1e-7)

  # Check tidy output
  trained_tidy <- tidy(prepped, 1)
  expect_equal(trained_tidy$value, c(mean(mtcars$disp), mean(mtcars$hp)))
})

test_that("centering handles selectors", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(all_numeric_predictors())

  prepped <- prep(rec, training = mtcars)

  # Check correct columns selected
  selected <- prepped$steps[[1]]$columns
  expect_true("disp" %in% selected)
  expect_false("mpg" %in% selected)  # outcome, not predictor
})

test_that("centering works with case weights", {
  mtcars_weighted <- mtcars
  mtcars_weighted$wt_col <- hardhat::importance_weights(seq_len(nrow(mtcars)))

  rec <- recipe(mpg ~ ., data = mtcars_weighted) |>
    update_role(wt_col, new_role = "case_weights") |>
    step_center(disp)

  prepped <- prep(rec, training = mtcars_weighted)

  # Weighted mean should differ from unweighted
  expect_false(
    prepped$steps[[1]]$means[["disp"]] == mean(mtcars$disp)
  )
})

test_that("centering validates input", {
  df <- data.frame(x = letters[1:5], y = 1:5)

  rec <- recipe(~ ., data = df) |>
    step_center(x)

  expect_error(prep(rec, training = df))
})

test_that("centering handles NA", {
  mtcars_na <- mtcars
  mtcars_na$disp[1:5] <- NA

  rec <- recipe(mpg ~ ., data = mtcars_na) |>
    step_center(disp, na_rm = TRUE)

  prepped <- prep(rec, training = mtcars_na)
  baked <- bake(prepped, mtcars_na)

  # NA values remain NA
  expect_true(all(is.na(baked$disp[1:5])))
  expect_false(any(is.na(baked$disp[6:nrow(mtcars_na)])))
})
```

See [Testing Patterns (Source)](testing-patterns-source.md) for comprehensive guide.

### Step 4: Run Tests and Check

```r
# Document
devtools::document()

# Load
devtools::load_all()

# Test
devtools::test()

# Full check
devtools::check()
```

---

## Documentation Patterns

### Using @inheritParams

Recipes uses extensive parameter inheritance:

```r
#' @inheritParams step_normalize
```

This inherits all standard parameters from `step_normalize`.

### Using @template

```r
#' @template step-return
#' @template case-weights-unsupervised
```

Available templates are in templates or inline documentation.

### Cross-Referencing Steps

```r
#' @seealso [step_normalize()], [step_scale()]
#' @family normalization steps
```

### Documentation Files to Create

**INSTRUCTIONS FOR CLAUDE:**

Create ONLY these files by default:
1. **R/[step_name].R** - Complete implementation
2. **tests/testthat/test-[step_name].R** - Test suite
3. **README.md** - Overview with basic usage example (200-300 lines)

Do NOT create unless user explicitly requests:
- ❌ IMPLEMENTATION_SUMMARY.md
- ❌ QUICKSTART.md
- ❌ example_usage.R
- ❌ Additional documentation files

If user wants more documentation, they will ask (e.g., "add comprehensive documentation").

---

## The Three-Function Pattern

Every step needs these three functions:

### 1. Step Constructor (User-Facing)

```r
#' @export
step_center <- function(recipe, ..., role = NA, ...) {
  add_step(recipe, step_center_new(...))
}
```

### 2. Step Initialization (Internal)

```r
step_center_new <- function(terms, role, trained, ...) {
  step(subclass = "center", ...)
}
```

### 3. S3 Methods (All Exported)

```r
#' @export
prep.step_center <- function(x, training, info = NULL, ...) { }

#' @export
bake.step_center <- function(object, new_data, ...) { }

#' @export
print.step_center <- function(x, ...) { }

#' @export
tidy.step_center <- function(x, ...) { }
```

---

## Step Type Best Practices

### Modify-in-Place Steps

```r
# Use role = NA
step_center <- function(recipe, ..., role = NA, ...) { }

# No keep_original_cols parameter
# Columns modified in place
```

### Create-New-Columns Steps

```r
# Use role = "predictor"
step_dummy <- function(recipe, ..., role = "predictor",
                      keep_original_cols = FALSE, ...) { }

# In bake(), handle keep_original_cols
new_data <- remove_original_cols(new_data, object, original_cols)
```

### Row-Operation Steps

```r
# Default skip = TRUE
step_filter <- function(recipe, ..., skip = TRUE, ...) { }

# In bake(), respect skip
if (object$skip) {
  return(new_data)
}
```

---

## Creating New Internal Helpers

### When to Create

Create internal helpers when:

- Logic is shared by 2+ steps

- Complex operation used repeatedly

- Abstraction improves clarity

### Example Internal Helper

```r
#' Calculate weighted mean with case weight handling
#'
#' @param x Numeric vector
#' @param wts Numeric weights (or NULL)
#' @param na_rm Remove NA values?
#'
#' @return Numeric scalar
#' @keywords internal
#' @noRd
weighted_mean_na <- function(x, wts = NULL, na_rm = TRUE) {
  if (is.null(wts)) {
    mean(x, na.rm = na_rm)
  } else {
    if (inherits(wts, c("hardhat_importance_weights",
                        "hardhat_frequency_weights"))) {
      wts <- as.double(wts)
    }
    weighted.mean(x, w = wts, na.rm = na_rm)
  }
}
```

Use:

- `@keywords internal`

- `@noRd`

- Don't export

---

## Error Messages

Use cli for consistent errors:

```r
if (bad_input) {
  cli::cli_abort(
    "{.arg na_rm} must be a single logical value, not {.obj_type_friendly {na_rm}}.",
    call = call
  )
}
```

Pass `call` parameter for better error context:

```r
prep.step_center <- function(x, training, info = NULL, ...,
                            call = rlang::caller_env()) {
  if (problem) {
    cli::cli_abort("Error message", call = call)
  }
}
```

---

## PR Submission

### Before Submitting

1. **Run full check:**
   ```r
   devtools::check()
   ```

2. **Update NEWS.md:**
   ```md
   ## recipes (development version)

   * Added `step_center()` for centering numeric predictors (#123).
   ```

3. **Commit changes:**
   ```bash
   git add .
   git commit -m "Add step_center()"
   git push origin feature/add-step-center
   ```

### Creating the PR

1. Go to https://github.com/tidymodels/recipes
2. Click "New pull request"
3. Select your branch
4. Fill in description:

   - What does this step do?

   - Why is it useful?

   - Reference any related issues

### Review Process

Common feedback:

- Add tests for all selectors

- Match existing documentation style

- Use internal helpers

- Add more examples

- Fix code style issues

See [Troubleshooting (Source)](troubleshooting-source.md) for common review feedback.

---

## Reference Documentation

### Source Development

- [Testing Patterns (Source)](testing-patterns-source.md) - Testing with internal helpers

- [Best Practices (Source)](best-practices-source.md) - Code style and internal functions

- [Troubleshooting (Source)](troubleshooting-source.md) - Common issues

### Step Types

- [Step Architecture](step-architecture.md)

- [Modify-in-Place Steps](modify-in-place-steps.md)

- [Create-New-Columns Steps](create-new-columns-steps.md)

- [Row-Operation Steps](row-operation-steps.md)

### Core Concepts

- [Helper Functions](helper-functions.md)

- [Optional Methods](optional-methods.md)

### Shared References

- [Extension Prerequisites](package-extension-prerequisites.md)

- [Development Workflow](package-development-workflow.md)

- [Roxygen Documentation](package-roxygen-documentation.md)

---

## Next Steps

1. **Clone recipes repository**
2. **Create feature branch**
3. **Implement your step** following this guide
4. **Test thoroughly** with recipes test patterns
5. **Run `devtools::check()`**
6. **Submit PR** to tidymodels/recipes

---

## Getting Help

- Check [Troubleshooting (Source)](troubleshooting-source.md)

- Study existing steps in the repository

- Review [Best Practices (Source)](best-practices-source.md)

- Open an issue on GitHub for questions

- Tag maintainers in your PR
