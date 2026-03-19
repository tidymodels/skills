# Best Practices for Recipes Source Development

**Context:** This guide is for **source development** - contributing to the recipes package directly.

**Key principle:** ✅ **You CAN use internal functions** - you're developing the package, so internals are available.

For extension development (creating new packages), see [Best Practices (Extension)](../best-practices-extension.md).

---

## Using Internal Functions in Recipes

### When to Use Internal Functions

✅ **Use internal functions when:**
- Standard operations like variable selection or validation
- Complex calculations already implemented
- Consistency with existing steps is needed
- Avoiding code duplication

❌ **Don't use internal functions when:**
- Simple logic can be written inline
- The internal function doesn't quite fit
- It would make code less readable

### Finding Existing Internal Functions

```r
# List all objects (including internals)
ls("package:recipes", all.names = TRUE)

# Search for specific pattern
ls("package:recipes", all.names = TRUE, pattern = "^check_")

# View internal function
recipes:::check_type

# Search in package directory
# grep -r "check_type" R/
```

### Common Internal Helpers

#### `recipes_eval_select()` - Variable Selection

The most important internal function for resolving variable selections:

```r
prep.step_center <- function(x, training, info = NULL, ...) {
  # Resolve variable selections to actual column names
  col_names <- recipes_eval_select(x$terms, training, info)

  # Now col_names contains actual column names
  # ...
}
```

**Use for:**
- Converting `all_numeric()` to actual numeric column names
- Converting `all_predictors()` to predictor names
- Resolving manual selections like `c(disp, hp)`

#### `get_case_weights()` - Extract Case Weights

```r
prep.step_center <- function(x, training, info = NULL, ...) {
  col_names <- recipes_eval_select(x$terms, training, info)

  # Extract case weights if they exist
  wts <- get_case_weights(info, training)
  were_weights_used <- are_weights_used(wts, unsupervised = TRUE)

  if (isFALSE(were_weights_used)) {
    wts <- NULL
  }

  # Use wts in calculations
  # ...
}
```

**Handles:**
- Finding case_weights role in recipe
- Extracting weight column
- Converting to appropriate format

#### `check_type()` - Validate Column Types

```r
prep.step_center <- function(x, training, info = NULL, ...) {
  col_names <- recipes_eval_select(x$terms, training, info)

  # Validate that columns are numeric
  check_type(training[, col_names], types = c("double", "integer"))

  # Proceed with confidence that types are correct
  # ...
}
```

**Common type checks:**
- `c("double", "integer")` - Numeric data
- `c("factor", "ordered")` - Categorical data
- `"character"` - Text data
- `"logical"` - Boolean data

#### `check_new_data()` - Validate Columns Exist in New Data

```r
bake.step_center <- function(object, new_data, ...) {
  col_names <- names(object$means)

  # Verify all required columns exist in new_data
  check_new_data(col_names, object, new_data)

  # Safe to proceed
  # ...
}
```

**Provides:**
- Clear error message if columns missing
- Consistent error format across steps

#### `remove_original_cols()` - Handle keep_original_cols

For steps that create new columns:

```r
bake.step_dummy <- function(object, new_data, ...) {
  # Create new columns
  # ...

  # Handle removal of original columns
  new_data <- remove_original_cols(
    new_data,
    object,
    names(object$levels)  # Original column names
  )

  new_data
}
```

#### `print_step()` - Standard Printing

```r
print.step_center <- function(x, width = max(20, options()$width - 30), ...) {
  title <- "Centering for "

  print_step(
    x$columns,       # Variable names (after training)
    x$terms,         # Variable selector (before training)
    x$trained,       # Training status
    title,           # Step description
    width,           # Width for printing
    case_weights = x$case_weights  # Whether weights were used
  )

  invisible(x)
}
```

#### `sel2char()` - Convert Selections to Strings

For tidy() on untrained steps:

```r
tidy.step_center <- function(x, ...) {
  if (is_trained(x)) {
    # After training: use actual column names
    res <- tibble(
      terms = names(x$means),
      value = unname(x$means)
    )
  } else {
    # Before training: convert selectors to character
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

## File Naming Conventions

Recipes organizes steps by name (less strict than yardstick):

### Source File Names

- **Step files**: `R/[step_name].R`
  - Examples: `center.R`, `normalize.R`, `pca.R`, `dummy.R`

### Test File Names Match Source

- `R/center.R` → `tests/testthat/test-center.R`
- `R/normalize.R` → `tests/testthat/test-normalize.R`

## Documentation Patterns

Recipes uses extensive `@inheritParams` to avoid duplication.

### Inheriting Standard Parameters

```r
#' Center numeric variables
#'
#' @inheritParams step_normalize
#' @param na_rm A logical value indicating whether NA values should be removed
#'   when computing means.
#' @param means A named numeric vector of means. This is `NULL` until computed
#'   by [prep()].
#'
#' @export
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
  # ...
}
```

**Common inheritParams sources:**
- `step_normalize` - For normalization-type steps
- `step_center` - For centering-type steps
- `step_pca` - For dimension reduction steps
- `step_dummy` - For encoding steps

### Standard Parameter Documentation

Parameters shared across most steps:

```r
#' @param recipe A recipe object
#' @param ... One or more selector functions to choose variables
#' @param role Role for new variables (use NA for in-place modifications)
#' @param trained Logical indicating if step has been trained
#' @param skip Logical indicating if step should be skipped during bake()
#' @param id Character string identifier for the step
```

### Using @template

Recipes has some templates, but uses them less than yardstick:

```r
#' @template step-return
```

### Cross-Referencing Steps

Link to related steps:

```r
#' @seealso [step_normalize()], [step_scale()]
#' @family normalization steps
```

## Code Style Specific to Recipes

### The Three-Function Pattern

Every step needs three functions (plus S3 methods):

```r
# 1. Step constructor (user-facing, exported)
#' @export
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

# 2. Step initialization (internal constructor)
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

# 3. S3 methods (all exported)
#' @export
prep.step_center <- function(x, training, info = NULL, ...) {
  # Training logic
}

#' @export
bake.step_center <- function(object, new_data, ...) {
  # Application logic
}

#' @export
print.step_center <- function(x, width = max(20, options()$width - 30), ...) {
  # Printing logic
}

#' @rdname tidy.recipe
#' @export
tidy.step_center <- function(x, ...) {
  # Tidying logic
}
```

### Use add_step() to Add to Recipe

```r
step_center <- function(recipe, ...) {
  add_step(
    recipe,
    step_center_new(...)
  )
}
```

**Don't manually modify the recipe object.**

### Use step() to Create Step Object

```r
step_center_new <- function(terms, role, ...) {
  step(
    subclass = "center",  # Must match function name
    terms = terms,
    role = role,
    ...
  )
}
```

**The subclass must match the step name** (minus "step_" prefix).

### prep() Method Structure

```r
prep.step_center <- function(x, training, info = NULL, ...) {
  # 1. Resolve variable selections
  col_names <- recipes_eval_select(x$terms, training, info)

  # 2. Validate column types
  check_type(training[, col_names], types = c("double", "integer"))

  # 3. Get case weights (if applicable)
  wts <- get_case_weights(info, training)
  were_weights_used <- are_weights_used(wts, unsupervised = TRUE)
  if (isFALSE(were_weights_used)) {
    wts <- NULL
  }

  # 4. Calculate step parameters (e.g., means, scales, etc.)
  means <- calculate_means(training[, col_names], wts, x$na_rm)

  # 5. Check for issues (e.g., Inf, NaN)
  check_for_problems(means, col_names)

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

### bake() Method Structure

```r
bake.step_center <- function(object, new_data, ...) {
  # 1. Get column names from trained step
  col_names <- names(object$means)

  # 2. Validate columns exist in new data
  check_new_data(col_names, object, new_data)

  # 3. Apply transformation
  for (col_name in col_names) {
    new_data[[col_name]] <- new_data[[col_name]] - object$means[[col_name]]
  }

  # 4. Return modified data
  new_data
}
```

**Key points:**
- Use column names from trained object (not from x$terms)
- Validate before transforming
- Return the modified data frame

## Step Type Best Practices

### Modify-in-Place Steps

```r
# Use role = NA (preserve existing role)
step_center <- function(recipe, ..., role = NA, ...) {
  # ...
}

# Don't add keep_original_cols parameter
# These steps modify in place, not create new columns
```

### Create-New-Columns Steps

```r
# Use role = "predictor" (or other appropriate role)
step_dummy <- function(recipe, ..., role = "predictor",
                      keep_original_cols = FALSE, ...) {
  # ...
}

# In bake(), handle keep_original_cols
bake.step_dummy <- function(object, new_data, ...) {
  # Create new columns
  # ...

  # Remove originals unless keep_original_cols = TRUE
  new_data <- remove_original_cols(new_data, object, original_cols)

  new_data
}
```

### Row-Operation Steps

```r
# Default skip = TRUE (usually don't apply to new data)
step_filter <- function(recipe, ..., skip = TRUE, ...) {
  # ...
}

# In bake(), respect skip parameter
bake.step_filter <- function(object, new_data, ...) {
  if (object$skip) {
    return(new_data)
  }

  # Apply filter
  # ...
}
```

## Creating New Internal Helpers

### When to Create Internal Helpers

Create internal helpers when:
- Logic is shared by 2+ steps
- Complex operation used repeatedly
- Abstraction improves clarity

### Naming Conventions

Internal helpers typically:
- Have descriptive names
- Are NOT exported
- Use `@keywords internal` and `@noRd`

### Example Internal Helper

```r
#' Calculate weighted mean with NA handling
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
    # Handle hardhat weights
    if (inherits(wts, c("hardhat_importance_weights",
                        "hardhat_frequency_weights"))) {
      wts <- as.double(wts)
    }
    weighted.mean(x, w = wts, na.rm = na_rm)
  }
}
```

## Error Messages

### Use cli Functions

```r
if (bad_input) {
  cli::cli_abort(
    "{.arg na_rm} must be a single logical value, not {.obj_type_friendly {na_rm}}.",
    call = call
  )
}

if (missing_columns) {
  cli::cli_warn(
    "Column{?s} {.var {missing}} not found and will be ignored."
  )
}
```

### Pass call for Context

```r
prep.step_center <- function(x, training, info = NULL, ...,
                            call = rlang::caller_env()) {
  # Use call in error messages
  if (problem) {
    cli::cli_abort("Error message", call = call)
  }
}
```

## Variable Selection Best Practices

### Always Use recipes_eval_select()

```r
# Good
col_names <- recipes_eval_select(x$terms, training, info)

# Bad - don't try to resolve manually
col_names <- dplyr::select(training, !!!x$terms) |> names()
```

### Support All Standard Selectors

Your step should work with:
- `all_numeric()`
- `all_numeric_predictors()`
- `all_nominal()`
- `all_predictors()`
- `all_outcomes()`
- `has_role("predictor")`
- Manual selection: `c(disp, hp)`

Test all of these!

## Case Weight Best Practices

### Extract Weights in prep()

```r
wts <- get_case_weights(info, training)
were_weights_used <- are_weights_used(wts, unsupervised = TRUE)

if (isFALSE(were_weights_used)) {
  wts <- NULL
}
```

### Store Whether Weights Were Used

```r
step_center_new(
  # ...
  case_weights = were_weights_used  # Store TRUE/FALSE
)
```

### Use Weights in Calculations

```r
if (is.null(wts)) {
  mean(x)
} else {
  # Convert hardhat weights
  if (inherits(wts, c("hardhat_importance_weights",
                      "hardhat_frequency_weights"))) {
    wts <- as.double(wts)
  }
  weighted.mean(x, w = wts)
}
```

## Performance Considerations

### Vectorize Operations

```r
# Good - vectorized
for (col_name in col_names) {
  new_data[[col_name]] <- new_data[[col_name]] - object$means[[col_name]]
}

# Avoid - row-by-row
for (i in seq_len(nrow(new_data))) {
  new_data[i, col_names] <- new_data[i, col_names] - object$means
}
```

### Avoid Unnecessary Copies

```r
# Good - modify in place
for (col in cols) {
  new_data[[col]] <- transform(new_data[[col]])
}

# Avoid - creates copies
new_data <- new_data |>
  mutate(across(all_of(cols), transform))
```

## Consistency with Existing Steps

### Study Similar Steps

Before implementing:
- For normalization: `R/center.R`, `R/scale.R`, `R/normalize.R`
- For encoding: `R/dummy.R`, `R/novel.R`
- For dimension reduction: `R/pca.R`, `R/ica.R`
- For filtering: `R/filter.R`, `R/sample.R`

### Match Parameter Patterns

Keep standard parameters in standard order:

```r
step_name <- function(
  recipe,            # Always first
  ...,              # Variable selection
  role = NA,        # Role for new variables
  trained = FALSE,  # Training status
  # Step-specific parameters here
  skip = FALSE,     # Skip in bake()?
  id = rand_id("name")  # Unique ID
) {
  # ...
}
```

## Next Steps

- Review [Testing Patterns (Source)](testing-patterns-source.md) for testing guidance
- Check [Troubleshooting (Source)](troubleshooting-source.md) for common issues
- Study existing steps in the recipes repository
- Follow [Extension Best Practices](../best-practices-extension.md) for code style basics
