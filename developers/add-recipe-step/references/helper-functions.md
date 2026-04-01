# Recipe Helper Functions Reference

The recipes package provides helper functions to standardize common operations in recipe steps. Use these instead of implementing your own versions.

> **Note for Source Development:** If you're contributing directly to the recipes package, these helper functions are available without the `recipes::` prefix. See the [Source Development Guide](source-guide.md) for details.

## Overview

**Helper function implementations in recipes:**
- Variable selection: `R/recipes_eval_select.R` (tidyselect resolution)
- Validation functions: `R/check.R` (type checking, new data validation)
- Case weights: `R/case_weights.R` (weight extraction and checking)
- Column operations: `R/remove_original_cols.R` (handle keep_original_cols)
- Utilities: `R/misc.R` (rand_id, print_step, sel2char, is_trained)

**Examples in step implementations:**
- Variable selection: `R/center.R` (uses `recipes_eval_select()`)
- Type checking: `R/normalize.R` (uses `check_type()`)
- Case weights: `R/pca.R` (uses `get_case_weights()`)
- Column removal: `R/dummy.R` (uses `remove_original_cols()`)
- Name checking: `R/interact.R` (uses `check_name()`)

**Test patterns:**
- Helper function tests: `tests/testthat/test-misc.R`
- Selection tests: `tests/testthat/test-selections.R`

## Overview

| Function | Purpose | Typical Usage |
|----------|---------|---------------|
| `recipes_eval_select()` | Convert quosures to column names | `prep()` method |
| `check_type()` | Validate column types | `prep()` method |
| `check_new_data()` | Verify columns exist in new data | `bake()` method |
| `check_name()` | Prevent column name conflicts | When creating new columns |
| `get_case_weights()` | Extract case weights from info | `prep()` method |
| `are_weights_used()` | Check if weights should be used | `prep()` method |
| `rand_id()` | Generate unique step IDs | Step constructor |
| `print_step()` | Standard step printing | `print()` method |
| `remove_original_cols()` | Handle keep_original_cols | `bake()` method |
| `sel2char()` | Convert selections to strings | `tidy()` method |
| `is_trained()` | Check training status | `tidy()` method |
| `add_step()` | Add step to recipe | Step constructor |
| `yardstick_any_missing()` | Check for NA values | Both `prep()` and `bake()` |
| `yardstick_remove_missing()` | Remove rows with NAs | Both `prep()` and `bake()` |

## Variable Selection and Resolution

### recipes_eval_select()

**Purpose:** Resolves tidyselect expressions to actual column names.

**When to use:** In `prep()` to convert user's variable selections (like `all_numeric()`) to actual column names.

**Signature:**
```r
recipes_eval_select(quos, data, info)
```

**Arguments:**
- `quos`: Quosures from `rlang::enquos(...)`
- `data`: Training data frame
- `info`: Recipe info object (from `prep()` parameter)

**Example:**
```r
prep.step_yourname <- function(x, training, info = NULL, ...) {
  # Convert user selection to actual column names
  col_names <- recipes::recipes_eval_select(x$terms, training, info)
  # col_names is now a character vector like c("mpg", "disp", "hp")

  # ... rest of prep
}
```

**Returns:** Character vector of column names

### sel2char()

**Purpose:** Converts tidyselect expressions to human-readable strings.

**When to use:** In `tidy()` method for untrained steps to show what will be selected.

**Example:**
```r
tidy.step_yourname <- function(x, ...) {
  if (recipes::is_trained(x)) {
    # Use actual column names from trained step
    res <- tibble::tibble(terms = names(x$params))
  } else {
    # Convert selection to readable strings
    term_names <- recipes::sel2char(x$terms)
    res <- tibble::tibble(terms = term_names)
  }
  res$id <- x$id
  res
}
```

**Returns:** Character vector of selection names (e.g., `"all_numeric()"`, `"disp"`)

## Validation Functions

### check_type()

**Purpose:** Validates that columns are of expected types.

**When to use:** In `prep()` after resolving column names, before computing parameters.

**Signature:**
```r
check_type(dat, types = NULL)
```

**Arguments:**
- `dat`: Data frame subset with columns to check
- `types`: Character vector of allowed types

**Example:**
```r
prep.step_yourname <- function(x, training, info = NULL, ...) {
  col_names <- recipes::recipes_eval_select(x$terms, training, info)

  # Validate columns are numeric or integer
  recipes::check_type(
    training[, col_names],
    types = c("double", "integer")
  )

  # If wrong type, check_type() throws an error
  # ... continue with prep
}
```

**Common type values:**
- `"double"`: Numeric values
- `"integer"`: Integer values
- `"factor"`: Factor/categorical
- `"logical"`: Boolean
- `"character"`: Text

**Behavior:** Throws error if any column doesn't match allowed types.

### check_new_data()

**Purpose:** Validates that required columns exist in new data.

**When to use:** At the start of `bake()` to ensure columns needed by the step are present.

**Signature:**
```r
check_new_data(col_names, object, new_data)
```

**Arguments:**
- `col_names`: Character vector of required column names
- `object`: The trained step object
- `new_data`: New data frame to validate

**Example:**
```r
bake.step_yourname <- function(object, new_data, ...) {
  col_names <- object$columns  # or names(object$params)

  # Check columns exist in new_data
  recipes::check_new_data(col_names, object, new_data)

  # If missing columns, check_new_data() throws informative error
  # ... continue with bake
}
```

**Behavior:** Throws error with helpful message if columns are missing.

### check_name()

**Purpose:** Checks if proposed column name already exists, prevents conflicts.

**When to use:** In `bake()` for create-new-columns steps before adding new columns.

**Signature:**
```r
check_name(new_names, data, object, newname)
```

**Arguments:**
- `new_names`: Character vector of proposed new column names
- `data`: Data frame where columns will be added
- `object`: Step object
- `newname`: Alternative name to suggest if conflict exists

**Example:**
```r
bake.step_yourname <- function(object, new_data, ...) {
  # Generate new column names
  new_col_names <- paste0(object$columns, "_transformed")

  # Check for conflicts
  new_col_names <- recipes::check_name(
    new_col_names,
    new_data,
    object,
    newname = "transformed"
  )

  # ... create new columns with validated names
}
```

**Returns:** Modified names if conflicts exist, original names otherwise.

## Case Weights

### get_case_weights()

**Purpose:** Extracts case weight column from recipe info.

**When to use:** In `prep()` to get case weights for weighted computations.

**Signature:**
```r
get_case_weights(info, data)
```

**Arguments:**
- `info`: Recipe info object
- `data`: Training data

**Example:**
```r
prep.step_yourname <- function(x, training, info = NULL, ...) {
  col_names <- recipes::recipes_eval_select(x$terms, training, info)

  # Get case weights if present
  wts <- recipes::get_case_weights(info, training)
  were_weights_used <- recipes::are_weights_used(wts, unsupervised = TRUE)

  if (isFALSE(were_weights_used)) {
    wts <- NULL
  }

  # Use wts in weighted computations if not NULL
  # ... rest of prep
}
```

**Returns:** Weight vector or NULL if no weights specified.

### are_weights_used()

**Purpose:** Determines if case weights should be used for this operation.

**When to use:** After `get_case_weights()` to decide whether to use them.

**Signature:**
```r
are_weights_used(wts, unsupervised = FALSE)
```

**Arguments:**
- `wts`: Weights from `get_case_weights()`
- `unsupervised`: Whether this is an unsupervised operation (TRUE for most recipe steps)

**Example:**
```r
wts <- recipes::get_case_weights(info, training)
were_weights_used <- recipes::are_weights_used(wts, unsupervised = TRUE)

if (isFALSE(were_weights_used)) {
  wts <- NULL
}

# Store the fact that weights were used
step_yourname_new(
  # ... other params,
  case_weights = were_weights_used
)
```

**Returns:** Logical indicating whether weights should be used.

## Step Construction

### add_step()

**Purpose:** Adds a step to a recipe.

**When to use:** In your step constructor function.

**Signature:**
```r
add_step(recipe, step_object)
```

**Example:**
```r
step_yourname <- function(recipe, ...) {
  recipes::add_step(
    recipe,
    step_yourname_new(
      terms = rlang::enquos(...),
      # ... other parameters
    )
  )
}
```

**Returns:** Updated recipe with step added.

### rand_id()

**Purpose:** Generates unique identifier for a step.

**When to use:** As default value for `id` parameter in step constructor.

**Signature:**
```r
rand_id(prefix)
```

**Example:**
```r
step_yourname <- function(
  recipe,
  ...,
  id = recipes::rand_id("yourname")  # Default unique ID
) {
  # ... function body
}
```

**Returns:** Character string like `"yourname_a7b2c"`.

## Column Operations

### remove_original_cols()

**Purpose:** Removes original columns based on `keep_original_cols` parameter.

**When to use:** In `bake()` for create-new-columns steps, after adding new columns.

**Signature:**
```r
remove_original_cols(data, object, col_names)
```

**Arguments:**
- `data`: Data frame with both original and new columns
- `object`: Trained step object (must have `keep_original_cols` field)
- `col_names`: Character vector of original column names

**Example:**
```r
bake.step_yourname <- function(object, new_data, ...) {
  col_names <- object$columns

  # Create new columns
  new_cols <- create_new_columns(new_data[, col_names], object$params)
  new_data <- vctrs::vec_cbind(new_data, new_cols)

  # Remove originals if keep_original_cols = FALSE
  new_data <- recipes::remove_original_cols(new_data, object, col_names)

  new_data
}
```

**Returns:** Data frame with original columns removed (if `keep_original_cols = FALSE`).

**Important:** Only use for steps with `keep_original_cols` parameter. The helper correctly handles role preservation and column ordering.

## Status and Printing

### is_trained()

**Purpose:** Checks if a step has been trained.

**When to use:** In `tidy()` method to decide what to return.

**Example:**
```r
tidy.step_yourname <- function(x, ...) {
  if (recipes::is_trained(x)) {
    # Return actual learned values
    res <- tibble::tibble(
      terms = names(x$params),
      value = unname(x$params)
    )
  } else {
    # Return placeholders
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

**Returns:** Logical, `TRUE` if step has been prepped.

### print_step()

**Purpose:** Provides standardized printing for recipe steps.

**When to use:** In `print()` method.

**Signature:**
```r
print_step(col_names, terms, trained, title, width, case_weights = NULL)
```

**Arguments:**
- `col_names`: Resolved column names (if trained) or NULL
- `terms`: Original quosures from step
- `trained`: Whether step is trained
- `title`: Description of operation
- `width`: Maximum width for printing
- `case_weights`: Whether case weights were used

**Example:**
```r
print.step_yourname <- function(x, width = max(20, options()$width - 30), ...) {
  title <- "Centering for "
  recipes::print_step(
    x$columns,      # NULL if untrained
    x$terms,        # Original selection
    x$trained,      # TRUE/FALSE
    title,
    width,
    case_weights = x$case_weights
  )
  invisible(x)
}
```

**Output:**
```
Centering for disp, hp, ... (3 columns) [trained]
```

## NA Handling

### yardstick_any_missing()

**Purpose:** Checks if any values are NA across multiple vectors.

**When to use:** When `na_rm = FALSE`, to decide whether to return NA.

**Example:**
```r
if (!na_rm) {
  if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }
}
```

**Returns:** Logical, TRUE if any NA values exist.

### yardstick_remove_missing()

**Purpose:** Removes rows with NA values from multiple vectors.

**When to use:** When `na_rm = TRUE`, to filter out missing values.

**Example:**
```r
if (na_rm) {
  result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
  truth <- result$truth
  estimate <- result$estimate
  case_weights <- result$case_weights
}
```

**Returns:** List with filtered vectors (maintains alignment).

## Best Practices

1. **Always use helpers**: Don't reimplement functionality that helpers provide
2. **Check early**: Validate in `prep()`, trust in `bake()`
3. **Consistent patterns**: Use helpers the same way across all steps
4. **Error messages**: Helpers provide consistent, user-friendly errors

## Common Patterns

### Complete prep() pattern

```r
prep.step_yourname <- function(x, training, info = NULL, ...) {
  # 1. Resolve selections
  col_names <- recipes::recipes_eval_select(x$terms, training, info)

  # 2. Validate types
  recipes::check_type(training[, col_names], types = c("double", "integer"))

  # 3. Get case weights
  wts <- recipes::get_case_weights(info, training)
  were_weights_used <- recipes::are_weights_used(wts, unsupervised = TRUE)
  if (isFALSE(were_weights_used)) {
    wts <- NULL
  }

  # 4. Compute parameters
  params <- compute_params(training[, col_names], wts, x$your_param)

  # 5. Return trained step
  step_yourname_new(
    terms = x$terms,
    trained = TRUE,
    columns = col_names,
    params = params,
    case_weights = were_weights_used,
    # ... other fields
  )
}
```

### Complete bake() pattern

```r
bake.step_yourname <- function(object, new_data, ...) {
  # 1. Get column names
  col_names <- object$columns

  # 2. Validate columns exist
  recipes::check_new_data(col_names, object, new_data)

  # 3. Apply transformation
  for (col in col_names) {
    new_data[[col]] <- apply_transform(new_data[[col]], object$params[[col]])
  }

  # 4. Return modified data
  new_data
}
```

## Internal Helpers (Source Development Only)

When contributing to recipes itself, all the helpers listed above can be used **without the `recipes::` prefix**. They're internal functions available directly in the package environment.

### Additional Internal Helpers

When developing recipes source code, you may also encounter:

- **Variable selection internals**: Functions that support `recipes_eval_select()`
- **Type checking internals**: Extended validation beyond `check_type()`
- **Column name utilities**: Functions for managing column names and conflicts
- **Role management**: Functions for assigning and updating column roles

### Usage in Source Development

```r
# Extension development (requires recipes:: prefix)
col_names <- recipes::recipes_eval_select(x$terms, training, info)
recipes::check_type(training[, col_names], types = c("double", "integer"))

# Source development (no prefix needed)
col_names <- recipes_eval_select(x$terms, training, info)
check_type(training[, col_names], types = c("double", "integer"))
```

### When to Create New Internal Helpers

If contributing to recipes and you find yourself duplicating logic across multiple steps:

1. **Check existing internals first**: Browse `R/aaa-*.R` and `R/utils-*.R` files
2. **Consider generalization**: Will this helper be useful for other steps?
3. **Document thoroughly**: Use `@keywords internal` and `@noRd`
4. **Don't export**: Internal helpers should not be in `NAMESPACE`

See the [Source Development Guide](source-guide.md) for complete patterns and examples.

---

## Next Steps

- Understand step architecture: [step-architecture.md](step-architecture.md)
- Implement modify-in-place steps: [modify-in-place-steps.md](modify-in-place-steps.md)
- Implement create-new-columns steps: [create-new-columns-steps.md](create-new-columns-steps.md)
- Implement row-operation steps: [row-operation-steps.md](row-operation-steps.md)
- Add optional methods: [optional-methods.md](optional-methods.md)
- Review best practices: [package-extension-requirements.md#best-practices](package-extension-requirements.md#best-practices)
