# Phase 2 Implementation Examples

**Date:** 2026-03-18
**Purpose:** Concrete examples showing extension vs. source development differences

---

## Example 1: MAE Metric Implementation

### Extension Development (New Package)

**Context:** User creating `mymetrics` package that extends yardstick

**File: R/mae.R**
```r
#' Mean Absolute Error
#'
#' Calculate the mean absolute error between truth and estimate.
#'
#' @family numeric metrics
#' @family accuracy metrics
#' @inheritParams rmse
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}

mae <- yardstick::new_numeric_metric(
  mae,
  direction = "minimize",
  range = c(0, Inf)
)

#' @export
#' @rdname mae
mae.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                           case_weights = NULL, ...) {
  yardstick::numeric_metric_summarizer(
    name = "mae",
    fn = mae_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights)
  )
}

#' @export
mae_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  if (!is.logical(na_rm) || length(na_rm) != 1) {
    cli::cli_abort("{.arg na_rm} must be a single logical value.")
  }

  yardstick::check_numeric_metric(truth, estimate, case_weights)

  if (na_rm) {
    result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  mae_impl(truth, estimate, case_weights)
}

# Implementation function - MUST handle weights manually
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  # EXTENSION: Can't use yardstick:::yardstick_mean()
  # Must implement weight handling ourselves
  if (is.null(case_weights)) {
    mean(errors)
  } else {
    # Convert hardhat weights to numeric
    wts <- if (inherits(case_weights, c("hardhat_importance_weights",
                                        "hardhat_frequency_weights"))) {
      as.double(case_weights)
    } else {
      case_weights
    }
    weighted.mean(errors, w = wts)
  }
}
```

**File: tests/testthat/test-mae.R**
```r
# EXTENSION: Must create own test data
test_that("mae works correctly", {
  df <- data.frame(
    truth = c(1, 2, 3, 4, 5),
    estimate = c(1.5, 2.5, 2.5, 3.5, 4.5)
  )

  result <- mae(df, truth, estimate)

  expect_equal(result$.estimate, 0.5)
  expect_equal(result$.metric, "mae")
  expect_equal(result$.estimator, "standard")
})

# EXTENSION: Can't use yardstick:::data_altman()
test_that("mae handles NA correctly", {
  df <- data.frame(
    truth = c(1, 2, NA, 4, 5),
    estimate = c(1.5, 2.5, 2.5, 3.5, 4.5)
  )

  result_remove <- mae(df, truth, estimate, na_rm = TRUE)
  expect_false(is.na(result_remove$.estimate))

  result_keep <- mae(df, truth, estimate, na_rm = FALSE)
  expect_true(is.na(result_keep$.estimate))
})
```

### Source Development (Contributing to Yardstick)

**Context:** User contributing to yardstick package itself

**File: R/num-mae.R**
```r
#' Mean Absolute Error
#'
#' Calculate the mean absolute error between truth and estimate.
#'
#' @family numeric metrics
#' @family accuracy metrics
#' @templateVar fn mae
#' @template return
#' @template event_first
#'
#' @inheritParams rmse
#'
#' @author Max Kuhn
#'
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}

mae <- new_numeric_metric(mae, direction = "minimize")

#' @export
#' @rdname mae
mae.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                           case_weights = NULL, ...) {
  numeric_metric_summarizer(
    name = "mae",
    fn = mae_vec,
    data = data,
    truth = !!enquo(truth),
    estimate = !!enquo(estimate),
    na_rm = na_rm,
    case_weights = !!enquo(case_weights)
  )
}

#' @export
mae_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  check_numeric_metric(truth, estimate, case_weights)

  if (na_rm) {
    result <- yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  mae_impl(truth, estimate, case_weights)
}

# Implementation function - SOURCE: Can use internal helpers
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  # SOURCE: Can use internal helper!
  # This is cleaner and consistent with other metrics
  yardstick_mean(errors, case_weights = case_weights)
}
```

**File: tests/testthat/test-num-mae.R**
```r
# SOURCE: Can use internal test data
test_that("mae works correctly", {
  # Using internal test helper - we're developing yardstick
  df <- data_altman()

  result <- mae(df, pathology, scan)

  # SOURCE: Can use snapshot testing like rest of package
  expect_snapshot(result)
})

test_that("mae works on numeric vectors", {
  truth <- c(1, 2, 3, 4, 5)
  estimate <- c(1.5, 2.5, 2.5, 3.5, 4.5)

  expect_equal(mae_vec(truth, estimate), 0.5)
})

# SOURCE: More comprehensive tests matching package standards
test_that("mae errors on mismatched lengths", {
  expect_snapshot(
    error = TRUE,
    mae_vec(1:5, 1:4)
  )
})

test_that("mae works with case weights", {
  # SOURCE: Can use internal test helpers
  df <- data_three_class()

  result <- mae(df, obs, pred, case_weights = weights)

  expect_snapshot(result)
})
```

**Key Differences:**
1. ✅ **Internal functions:** Source can use `yardstick_mean()`, extension cannot
2. ✅ **Test data:** Source uses `data_altman()`, extension creates own
3. ✅ **Documentation:** Source uses `@template`, extension uses standard roxygen
4. ✅ **Snapshot testing:** Source uses it extensively, extension doesn't
5. ✅ **File naming:** Source uses `num-mae.R`, extension uses `mae.R`

---

## Example 2: Recipe Step Implementation

### Extension Development (New Package)

**Context:** User creating `mysteps` package that extends recipes

**File: R/step_center.R**
```r
#' Center numeric variables
#'
#' @inheritParams recipes::step_normalize
#' @param ... One or more selector functions
#' @param role Not used by this step
#' @param na_rm Remove NA when computing means
#' @param means Computed means (NULL until trained)
#' @export
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

#' @export
prep.step_center <- function(x, training, info = NULL, ...) {
  # EXTENSION: Must use exported function
  col_names <- recipes::recipes_eval_select(x$terms, training, info)

  # EXTENSION: Must manually extract case weights
  wts <- recipes::get_case_weights(info, training)
  were_weights_used <- recipes::are_weights_used(wts, unsupervised = TRUE)
  if (isFALSE(were_weights_used)) {
    wts <- NULL
  }

  # EXTENSION: Must implement mean calculation ourselves
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
  recipes::check_new_data(col_names, object, new_data)

  for (col_name in col_names) {
    new_data[[col_name]] <- new_data[[col_name]] - object$means[[col_name]]
  }

  new_data
}

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
```

**File: tests/testthat/test-step_center.R**
```r
# EXTENSION: Use standard datasets
test_that("centering works correctly", {
  rec <- recipes::recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  prepped <- recipes::prep(rec, training = mtcars)
  results <- recipes::bake(prepped, mtcars)

  expect_equal(mean(results$disp), 0, tolerance = 1e-7)
  expect_equal(mean(results$hp), 0, tolerance = 1e-7)
})

# EXTENSION: Create own test data
test_that("centering handles NA correctly", {
  df <- mtcars
  df$disp[1:3] <- NA

  rec <- recipes::recipe(mpg ~ ., data = df) |>
    step_center(disp, na_rm = TRUE)

  prepped <- recipes::prep(rec, training = df)
  results <- recipes::bake(prepped, df)

  expect_true(all(is.na(results$disp[1:3])))
})
```

### Source Development (Contributing to Recipes)

**Context:** User contributing to recipes package itself

**File: R/center.R**
```r
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
#' biomass_te[1:10, names(transformed_te)]
#' transformed_te
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
  col_names <- recipes_eval_select(x$terms, training, info)

  check_type(training[, col_names], types = c("double", "integer"))

  # SOURCE: Use internal helpers
  wts <- get_case_weights(info, training)
  were_weights_used <- are_weights_used(wts, unsupervised = TRUE)
  if (isFALSE(were_weights_used)) {
    wts <- NULL
  }

  # SOURCE: Can use internal averaging function if it exists
  # Or implement inline like this (recipes doesn't have yardstick_mean equivalent)
  means <- vapply(
    training[, col_names],
    weighted_mean,
    numeric(1),
    wts = wts,
    na_rm = x$na_rm
  )

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
  check_new_data(col_names, object, new_data)

  # SOURCE: Can use internal loop helpers if they exist
  for (col_name in col_names) {
    new_data[[col_name]] <- new_data[[col_name]] - object$means[[col_name]]
  }

  new_data
}

#' @export
print.step_center <- function(x, width = max(20, options()$width - 30), ...) {
  title <- "Centering for "
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

**File: tests/testthat/test-center.R**
```r
# SOURCE: Can use internal test data/helpers
test_that("centering works correctly", {
  # SOURCE: Could use internal test recipe if it exists
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(disp, hp)

  prepped <- prep(rec, training = mtcars)
  results <- bake(prepped, mtcars)

  expect_equal(mean(results$disp), 0, tolerance = 1e-7)
  expect_equal(mean(results$hp), 0, tolerance = 1e-7)

  # SOURCE: Match package testing style
  expect_snapshot(tidy(prepped, number = 1))
})

# SOURCE: More comprehensive tests matching package
test_that("centering with selectors", {
  rec <- recipe(mpg ~ ., data = mtcars) |>
    step_center(all_numeric_predictors())

  expect_snapshot(rec)

  prepped <- prep(rec)
  expect_snapshot(tidy(prepped, number = 1))
})

test_that("centering errors correctly", {
  df <- data.frame(x = letters[1:5], y = 1:5)

  rec <- recipe(~., data = df) |>
    step_center(x)

  expect_snapshot(error = TRUE, {
    prep(rec)
  })
})
```

**Key Differences:**
1. ✅ **Internal functions:** Source uses `recipes_eval_select()` without prefix, extension needs `recipes::`
2. ✅ **Documentation:** Source uses `@template`, `@inheritParams` more heavily
3. ✅ **Testing:** Source uses snapshots, more selectors, more edge cases
4. ✅ **Examples:** Source has more extensive examples with package data
5. ✅ **File location:** Source in recipes repo, extension in separate package

---

## Example 3: Testing Patterns Documentation

### testing-patterns-extension.md (New File)

```markdown
# Testing Patterns for Extension Packages

Guide to testing R packages that extend tidymodels packages.

## Key Principle

❌ **Never use internal functions or test helpers**

They are not exported and may change without notice.

## Creating Test Data

### DO: Create your own test data

**Simple, explicit test data is best:**

```r
# Numeric/regression data
test_data <- data.frame(
  truth = c(1, 2, 3, 4, 5),
  estimate = c(1.1, 2.2, 2.9, 4.1, 4.8)
)

# Binary classification data
binary_data <- data.frame(
  truth = factor(c("yes", "yes", "no", "no"), levels = c("yes", "no")),
  estimate = factor(c("yes", "no", "yes", "no"), levels = c("yes", "no"))
)
```

### DON'T: Use internal test helpers

**Avoid:**
```r
# DON'T - Not exported
data <- yardstick:::data_altman()
data <- recipes:::iris_rec
```

These are internal and can change.

### DO: Use standard datasets

```r
# Built-in R datasets
data(mtcars)
data(iris)

# modeldata package (add to Suggests)
data(biomass, package = "modeldata")
```

## Standard Test Categories

Every function should have tests for:

1. **Correctness**: Verify calculation
2. **NA handling**: Test `na_rm = TRUE` and `FALSE`
3. **Input validation**: Wrong types, mismatched lengths
4. **Case weights**: Weighted vs unweighted differ
5. **Edge cases**: All correct, all wrong, empty data

[Rest of extension-specific testing patterns...]
```

### testing-patterns-source.md (New File)

```markdown
# Testing Patterns for Source Package Development

Guide to testing when contributing to tidymodels source packages.

## Key Principle

✅ **You CAN use internal functions and test helpers**

You're developing the package, so internals are available.

## Using Internal Test Helpers

### Yardstick Internal Helpers

```r
# You CAN use these when developing yardstick
test_that("metric works with altman data", {
  data <- data_altman()  # Internal helper - OK!

  result <- your_metric(data, pathology, scan)
  expect_snapshot(result)
})

test_that("multiclass metric works", {
  data <- data_three_class()  # Internal helper - OK!

  result <- your_metric(data, obs, pred)
  expect_snapshot(result)
})
```

**Available internal test helpers in yardstick:**
- `data_altman()` - Binary classification data
- `data_three_class()` - Multiclass data
- `data_hpc_cv1()` - Cross-validation data
- And more... (see `R/data.R`)

### Recipes Internal Helpers

```r
# You CAN use internal recipes helpers
test_that("step works with recipe", {
  rec <- iris_rec  # Internal - OK when developing recipes!

  rec <- rec |> step_your_step(all_numeric())

  expect_snapshot(prep(rec))
})
```

## Snapshot Testing

### When to use snapshots

Use `expect_snapshot()` for:
- ✅ Complex output structures (tibbles with multiple columns)
- ✅ Error messages
- ✅ Print output
- ✅ Warning messages

```r
test_that("metric returns correct structure", {
  data <- data_altman()

  result <- your_metric(data, pathology, scan)

  # Snapshot the entire result
  expect_snapshot(result)
})

test_that("metric errors on bad input", {
  expect_snapshot(error = TRUE, {
    your_metric_vec(1:5, letters[1:5])
  })
})
```

[Rest of source-specific testing patterns...]
```

**Key Differences:**
1. ✅ Extension: Never use internals, create own data
2. ✅ Source: Can use internals, leverage internal test helpers
3. ✅ Extension: Standard testthat assertions
4. ✅ Source: Heavy use of snapshot testing
5. ✅ Extension: Simple test structure
6. ✅ Source: More comprehensive edge cases

---

## Summary of Differences

### File Usage

| Aspect | Extension Development | Source Development |
|--------|----------------------|-------------------|
| **Internal Functions** | ❌ Never use (not exported) | ✅ Can use (part of package) |
| **Test Data** | Create own or use standard datasets | Can use internal test helpers |
| **Documentation** | Standard roxygen2 | Package-specific templates |
| **Testing Style** | Basic testthat | Snapshots + comprehensive cases |
| **File Naming** | Flexible | Must match package conventions |
| **Package Prefix** | Always use `package::` | Often omit (internal context) |

### When to Use Each

**Extension Development:**
- ✅ Creating a new package
- ✅ Publishing to CRAN
- ✅ Building on tidymodels
- ✅ Avoiding tight coupling

**Source Development:**
- ✅ Contributing to tidymodels packages
- ✅ Submitting PRs
- ✅ Adding core functionality
- ✅ Maintaining consistency with package

### Navigation Between Files

**Extension Path:**
```
SKILL.md (auto-detects)
  → extension-guide.md
    → testing-patterns-extension.md
    → best-practices-extension.md
    → troubleshooting-extension.md
```

**Source Path:**
```
SKILL.md (auto-detects)
  → source-guide.md
    → testing-patterns-source.md
    → best-practices-source.md
    → troubleshooting-source.md
```

Both paths share common reference files (metric-system.md, numeric-metrics.md, etc.) since the patterns themselves don't change.

---

## Implementation Notes

### Auto-Detection Implementation

The skill will check:

```r
# Pseudo-code for detection logic
if (file.exists("DESCRIPTION")) {
  pkg_name <- read.dcf("DESCRIPTION", fields = "Package")

  if (pkg_name == "yardstick") {
    context <- "SOURCE"
    message("Detected: Contributing to yardstick package")
  } else if (pkg_name == "recipes") {
    context <- "SOURCE"
    message("Detected: Contributing to recipes package")
  } else {
    context <- "EXTENSION"
    message("Detected: Creating extension package: ", pkg_name)
  }
} else if (length(list.files()) > 0) {
  context <- "EXTENSION"
  message("Detected: Extension development (no package yet)")
} else {
  # Ask user
  context <- ask_user("Extension or Source development?")
}
```

This detection happens automatically when the skill is invoked, providing seamless context-appropriate guidance.
