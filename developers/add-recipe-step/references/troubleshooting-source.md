# Troubleshooting Recipes Source Development

**Context:** This guide is for **source development** - contributing to the recipes package directly.

**Key focus:** Working with package internals, prep/bake workflow issues, and recipes-specific problems.

For extension development (creating new packages), see [Troubleshooting (Extension)](package-extension-requirements.md#common-issues-solutions).

---

## Working with Recipes Internals

### Finding Internal Functions

**Problem:** How do I know what internal functions are available?

**Solutions:**

```r
# List all objects including internals
ls("package:recipes", all.names = TRUE)

# Filter for specific patterns
ls("package:recipes", all.names = TRUE, pattern = "^check_")
ls("package:recipes", all.names = TRUE, pattern = "^get_")

# View source of internal function
recipes:::check_type
recipes:::recipes_eval_select

# Search in source files
# In terminal from recipes root:
# grep -r "check_type" R/
```

### When Internal Functions Change

**Problem:** Internal function changed and broke my step.

**Solution:**
1. Check git history: `git log --all --full-history -- R/your-file.R`
2. Review recent PRs that modified the function
3. Update your step to match new behavior
4. Add regression tests

**Prevention:**

- Document WHY you're using an internal function

- Add tests that would catch interface changes

- Use stable internals when possible

### Internal Function Not Found

**Problem:**
```r
Error: object 'internal_helper' not found
```

**Causes & Solutions:**

1. **Function doesn't exist**

   - Check spelling

   - Search codebase

2. **Function was removed/renamed**

   - Check git history

   - Implement functionality yourself

3. **Need to use different helper**

   - Ask maintainers for recommendation

## Variable Selection Issues

### Selector Doesn't Work

**Problem:** `all_numeric()` or other selector isn't working.

**Symptom:**
```r
rec <- recipe(mpg ~ ., data = mtcars) |>
  step_center(all_numeric())

prep(rec)
# Error: Can't select columns that don't exist
```

**Cause:** Using selector incorrectly.

**Solution:** Use `recipes_eval_select()` in prep():

```r
prep.step_center <- function(x, training, info = NULL, ...) {
  # This resolves the selector
  col_names <- recipes_eval_select(x$terms, training, info)

  # Now col_names contains actual column names
  # ...
}
```

### Wrong Columns Selected

**Problem:** Selector picks wrong columns (e.g., includes outcome).

**Diagnosis:**

```r
rec <- recipe(mpg ~ ., data = mtcars) |>
  step_center(all_numeric())

prepped <- prep(rec)

# Check what was selected
prepped$steps[[1]]$columns
```

**Solution:** Use the right selector:

```r
# Includes outcome
all_numeric()

# Excludes outcome
all_numeric_predictors()

# Only specific role
has_role("predictor")
```

### Selector Fails on New Data

**Problem:** Step works on training data but fails on new data.

**Symptom:**
```r
bake(prepped_rec, new_data)
# Error: Column 'x' doesn't exist
```

**Cause:** Column was in training but not in new data.

**Solution:** Use `check_new_data()` in bake():

```r
bake.step_center <- function(object, new_data, ...) {
  col_names <- names(object$means)

  # This will give clear error if columns missing
  check_new_data(col_names, object, new_data)

  # ...
}
```

### Manual Selection Not Working

**Problem:** Selecting columns by name doesn't work.

**Example:**
```r
step_center(disp, hp)  # Doesn't work
```

**Cause:** Need to use tidyselect syntax.

**Solution:** User code is actually correct. In prep():

```r
# This handles both:
# - step_center(disp, hp)
# - step_center(all_numeric())
col_names <- recipes_eval_select(x$terms, training, info)
```

## prep/bake Workflow Issues

### prep() Fails

**Problem:** Error during prep().

**Common causes:**

1. **Wrong column types**

```r
prep.step_center <- function(x, training, info = NULL, ...) {
  col_names <- recipes_eval_select(x$terms, training, info)

  # Add type validation
  check_type(training[, col_names], types = c("double", "integer"))

  # This will error if types wrong
}
```

2. **Missing values cause issues**

```r
# If your calculation can't handle NA
if (any(is.na(training[, col_names])) && !x$na_rm) {
  cli::cli_warn("NA values found but {.arg na_rm = FALSE}.")
}
```

3. **Insufficient data**

```r
if (nrow(training) == 0) {
  cli::cli_abort("Training data has 0 rows.")
}
```

### bake() Fails

**Problem:** Error during bake().

**Common causes:**

1. **Required columns missing**

```r
bake.step_center <- function(object, new_data, ...) {
  col_names <- names(object$means)

  # This catches missing columns
  check_new_data(col_names, object, new_data)

  # ...
}
```

2. **Wrong data types in new data**

```r
# New data has different types than training
# Solution: Validate types in bake() or document assumptions
```

3. **Step wasn't trained**

```r
if (!object$trained) {
  cli::cli_abort("Step must be trained before baking.")
}
```

### Parameters Not Stored

**Problem:** Parameters calculated in prep() aren't available in bake().

**Example:**
```r
prep.step_center <- function(x, training, info = NULL, ...) {
  col_names <- recipes_eval_select(x$terms, training, info)

  # Calculate means
  means <- colMeans(training[, col_names])

  # PROBLEM: Where do means go?
}
```

**Solution:** Return them in the updated step:

```r
prep.step_center <- function(x, training, info = NULL, ...) {
  col_names <- recipes_eval_select(x$terms, training, info)

  means <- colMeans(training[, col_names])

  # Return updated step with parameters
  step_center_new(
    terms = x$terms,
    role = x$role,
    trained = TRUE,
    means = means,  # Store parameters here
    na_rm = x$na_rm,
    skip = x$skip,
    id = x$id,
    case_weights = NULL
  )
}
```

### Step Applied Twice

**Problem:** Transformation applied multiple times.

**Example:**
```r
rec <- recipe(mpg ~ ., data = mtcars) |>
  step_center(disp)

prepped <- prep(rec)
baked1 <- bake(prepped, mtcars)
baked2 <- bake(prepped, baked1)  # Applied again!
```

**Cause:** bake() is designed to be idempotent but data might not be.

**Solution:** Document that bake() should only be used on original data, or make transformation truly idempotent.

## Case Weight Issues

### Weights Not Working

**Problem:** Case weights seem to be ignored.

**Diagnosis:**

```r
# Test if weights matter
mtcars_weighted <- mtcars
mtcars_weighted$wt <- hardhat::importance_weights(seq_len(nrow(mtcars)))

rec <- recipe(mpg ~ ., data = mtcars_weighted) |>
  update_role(wt, new_role = "case_weights") |>
  step_center(disp)

prepped_weighted <- prep(rec, training = mtcars_weighted)
prepped_unweighted <- prep(
  recipe(mpg ~ ., data = mtcars) |> step_center(disp),
  training = mtcars
)

# These should differ
prepped_weighted$steps[[1]]$means
prepped_unweighted$steps[[1]]$means
```

**Solutions:**

1. **Extract weights in prep()**

```r
wts <- get_case_weights(info, training)
were_weights_used <- are_weights_used(wts, unsupervised = TRUE)

if (isFALSE(were_weights_used)) {
  wts <- NULL
}
```

2. **Use weights in calculations**

```r
if (is.null(wts)) {
  means <- colMeans(training[, col_names], na.rm = x$na_rm)
} else {
  # Convert hardhat weights and use
  wts <- as.double(wts)
  means <- vapply(
    training[, col_names],
    function(col) weighted.mean(col, w = wts, na.rm = x$na_rm),
    numeric(1)
  )
}
```

### Weights Not Recognized

**Problem:**
```r
Error: No case weights found
```

**Cause:** Weight column doesn't have `case_weights` role.

**Solution:**

```r
# User must set role
df$wt <- hardhat::importance_weights(df$weight_values)

rec <- recipe(y ~ ., data = df) |>
  update_role(wt, new_role = "case_weights") |>
  step_your_step(...)
```

## Role and Column Management

### role = NA vs role = "predictor"

**Problem:** Confusion about when to use `role = NA`.

**Solution:**

- **role = NA**: Modify-in-place steps (preserve existing role)
  ```r
  step_center <- function(recipe, ..., role = NA, ...)
  ```

- **role = "predictor"**: Create-new-columns steps (assign role to new cols)
  ```r
  step_dummy <- function(recipe, ..., role = "predictor", ...)
  ```

### Column Role Changed Unexpectedly

**Problem:** Column role changed after step.

**Check:**
```r
rec <- recipe(mpg ~ ., data = mtcars) |>
  step_your_step(disp)

prepped <- prep(rec)

# Check role
prepped$var_info |>
  dplyr::filter(variable == "disp") |>
  dplyr::pull(role)
```

**Solution:**

- Use `role = NA` for modify-in-place steps

- Document role behavior clearly

### Original Columns Not Removed

**Problem:** Original columns remain after create-new-columns step.

**Cause:** Not using `remove_original_cols()`.

**Solution:**

```r
bake.step_dummy <- function(object, new_data, ...) {
  # Create new dummy columns
  # ...

  # Remove originals (unless keep_original_cols = TRUE)
  new_data <- remove_original_cols(
    new_data,
    object,
    names(object$levels)  # Original column names
  )

  new_data
}
```

## Skip Parameter Issues

### Step Applied to Test Data When It Shouldn't Be

**Problem:** Row-operation step applied to test data.

**Example:**
```r
rec <- recipe(~ ., data = mtcars) |>
  step_filter(mpg > 20)  # Should only filter training

prepped <- prep(rec, training = mtcars)
baked <- bake(prepped, new_data = test_data)

# Test data was filtered! (Probably wrong)
```

**Solution:** Use `skip = TRUE` for row-operation steps:

```r
step_filter <- function(recipe, ..., skip = TRUE, ...) {
  # ...
}

# In bake()
bake.step_filter <- function(object, new_data, ...) {
  if (object$skip) {
    return(new_data)
  }

  # Apply filter only if skip = FALSE
  # ...
}
```

### Skip Parameter Ignored

**Problem:** `skip = TRUE` but step still applied in bake().

**Cause:** Not checking skip in bake().

**Solution:**

```r
bake.step_your_step <- function(object, new_data, ...) {
  # Always check skip first
  if (object$skip) {
    return(new_data)
  }

  # Apply transformation
  # ...
}
```

## Integration Issues

### Step Doesn't Work with tune

**Problem:** Step works alone but fails in `tune_grid()`.

**Diagnosis:**

```r
library(tune)
library(workflows)

# Test in workflow
wf <- workflow() |>
  add_recipe(
    recipe(mpg ~ ., data = mtcars) |>
      step_your_step(...)
  ) |>
  add_model(linear_reg())

# Test with resamples
result <- fit_resamples(wf, resamples = vfold_cv(mtcars))
```

**Common Issues:**

1. **Step fails on resampled data**

   - Some folds might have different characteristics

   - Add validation for edge cases

2. **Step modifies outcome accidentally**

   - Check that selectors don't include outcome

   - Use `all_predictors()` not `all_numeric()`

3. **Step is too slow**

   - Optimize calculations

   - Avoid unnecessary copies

### Recipe Doesn't Work After Adding Step

**Problem:** Recipe fails after adding your step.

**Diagnosis:**

```r
# Test incrementally
rec1 <- recipe(mpg ~ ., data = mtcars) |>
  step_normalize(all_numeric_predictors())

prep(rec1)  # Works

rec2 <- rec1 |>
  step_your_step(disp)

prep(rec2)  # Fails
```

**Common causes:**

- Your step expects data in certain format

- Your step modifies data unexpectedly

- Your step doesn't preserve required columns

### Grouped Data Issues

**Problem:** Step fails with grouped data frames.

**Solution:** Make sure step preserves grouping:

```r
bake.step_center <- function(object, new_data, ...) {
  # Save groups
  groups <- dplyr::group_vars(new_data)

  # Do transformation
  # ...

  # Restore groups
  if (length(groups) > 0) {
    new_data <- dplyr::group_by(new_data, !!!rlang::syms(groups))
  }

  new_data
}
```

## Package Check Issues

### Check Fails: Example Errors

**Problem:**
```r
checking examples ... ERROR
Error in step_your_step(...): object not found
```

**Causes:**

1. **Example uses unexported function**

   - Make sure all functions in examples are exported

2. **Example uses undeclared dependency**

   - Add package to Suggests: `usethis::use_package("pkg", "Suggests")`

   - Use `@examplesIf` if package optional

3. **Example too complex**

   - Simplify

   - Use `\donttest{}` for slow examples

### Check Fails: Tests Too Slow

**Problem:** Test suite exceeds time limit.

**Solutions:**

```r
# Skip slow tests on CRAN
test_that("slow operation works", {
  skip_on_cran()

  # Slow test here
})

# Use smaller datasets
test_data <- mtcars[1:10, ]  # Instead of full mtcars

# Reduce iterations
for (i in 1:10) {  # Instead of 1:1000
  # ...
}
```

### Check Fails: Undefined Global Variables

**Problem:**
```r
checking R code for possible problems ... NOTE
  step_center: no visible binding for global variable 'disp'
```

**Cause:** Using bare column names without proper NSE handling.

**Solution:** Use `.data` pronoun:

```r
# In dplyr operations
data |> dplyr::mutate(new = .data$disp * 2)

# Or declare global variables (less preferred)
utils::globalVariables(c("disp", "hp"))
```

## Performance Issues

### Step is Slow

**Problem:** Step takes too long on large datasets.

**Diagnosis:**

```r
# Profile
profvis::profvis({
  prep(rec, training = large_data)
})
```

**Common bottlenecks:**

1. **Non-vectorized operations**
   ```r
   # Slow
   for (i in seq_len(nrow(data))) {
     data[i, col] <- transform(data[i, col])
   }

   # Fast
   data[[col]] <- transform(data[[col]])
   ```

2. **Repeated column selections**
   ```r
   # Slow - selects each time
   for (col in cols) {
     new_data <- new_data |> dplyr::mutate(...)
   }

   # Fast - vectorized
   for (col in cols) {
     new_data[[col]] <- transform(new_data[[col]])
   }
   ```

3. **Inefficient aggregations**
   ```r
   # Use built-in functions
   colMeans(data)

   # Avoid manual
   vapply(data, mean, numeric(1))
   ```

## Git and PR Issues

### Merge Conflicts in NAMESPACE

**Problem:** NAMESPACE has conflicts.

**Solution:**

```bash
# Don't edit NAMESPACE manually
# Instead, resolve R code conflicts and regenerate
git checkout your-branch
# Fix R code conflicts
devtools::document()  # Regenerates NAMESPACE
git add NAMESPACE
git commit
```

### PR Build Fails

**Common failures:**

1. **R CMD check errors**

   - Run locally: `devtools::check()`

   - Fix all errors, warnings, notes

2. **Test failures**

   - Run: `devtools::test()`

   - Check that tests pass locally first

3. **Code style issues**

   - Run: `styler::style_pkg()`

   - Run: `lintr::lint_package()`

## Common Review Feedback

### "Add tests for selectors"

Requested tests:
```r
test_that("step works with all_numeric()", { ... })
test_that("step works with all_numeric_predictors()", { ... })
test_that("step works with manual selection", { ... })
test_that("step works with has_role()", { ... })
```

### "Add case weight tests"

```r
test_that("step respects case weights", {
  # Test with and without weights
  # Results should differ
})
```

### "Use internal helper"

Reviewer suggests existing internal function:

- Check if it exists

- Review its implementation

- Refactor to use it

### "Match style of existing steps"

- Look at similar steps

- Match their structure

- Use same helper functions

## Getting Help

### Check Existing Issues

Search recipes GitHub:
https://github.com/tidymodels/recipes/issues

### Study Existing Steps

Look at similar steps:

- Normalization: `R/center.R`, `R/scale.R`

- Encoding: `R/dummy.R`, `R/novel.R`

- Filtering: `R/filter.R`

### Ask Tidymodels Team

- Open GitHub issue

- Ask in tidymodels forums

- Tag maintainers in PR

## Next Steps

- Review [Testing Patterns (Source)](testing-patterns-source.md) for testing guidance

- Check [Best Practices (Source)](best-practices-source.md) for coding standards

- See [Extension Troubleshooting](package-extension-requirements.md#common-issues-solutions) for general R package issues
