# Troubleshooting Yardstick Source Development

**Context:** This guide is for **source development** - contributing to the yardstick package directly.

**Key focus:** Working with package internals, integration testing, and yardstick-specific issues.

For extension development (creating new packages), see [Troubleshooting (Extension)](package-extension-requirements.md#common-issues-solutions).

---

## Working with Yardstick Internals

### Finding Internal Functions

**Problem:** How do I know what internal functions are available?

**Solutions:**

```r
# List all objects including internals
ls("package:yardstick", all.names = TRUE)

# Filter for yardstick_ helpers
ls("package:yardstick", all.names = TRUE, pattern = "yardstick_")

# View source of internal function
yardstick:::yardstick_mean

# Search in source files
# In terminal from yardstick root:
# grep -r "yardstick_" R/
```

### When Internal Functions Change

**Problem:** Internal function behavior changed and broke my metric.

**Solution:**
1. Check git history: `git log --all --full-history -- R/your-file.R`
2. Review recent PRs that modified the internal function
3. Update your metric to match new behavior
4. Add tests to prevent future breakage

**Prevention:**
- Document WHY you're using an internal (in comments)
- Add tests that would catch internal changes
- Prefer stable internals (e.g., `yardstick_mean`)

### Internal Function Not Found

**Problem:**
```r
Error: object 'yardstick_helper' not found
```

**Causes & Solutions:**

1. **Function doesn't exist**
   - Check spelling
   - Search codebase: `grep -r "yardstick_helper" R/`

2. **Function was removed**
   - Check git history
   - Implement functionality yourself
   - Ask package maintainers

3. **Function is in different file**
   - Make sure file is sourced before yours
   - Check NAMESPACE

## Estimator-Related Issues

### Wrong Estimator Detection

**Problem:** Metric detects wrong estimator (binary vs multiclass).

**Symptoms:**
```r
# Binary data treated as multiclass
df <- data.frame(
  truth = factor(c("A", "B", "A", "B")),
  estimate = factor(c("A", "A", "B", "B"))
)

accuracy(df, truth, estimate)
# Expected: binary estimator
# Got: macro estimator
```

**Solution:**

Use `finalize_estimator_internal()`:

```r
accuracy.data.frame <- function(data, truth, estimate,
                                estimator = NULL, ...,
                                call = rlang::caller_env()) {
  estimator <- finalize_estimator_internal(
    estimator,
    metric_class = "accuracy",  # Your metric name
    call = call
  )

  # Rest of implementation
}
```

### Invalid Estimator Error

**Problem:**
```r
Error: `estimator` must be one of "binary", "macro", "micro", or "macro_weighted"
```

**Cause:** User specified invalid estimator.

**Solution:** This is expected behavior. Error message is correct.

**If you want to add a new estimator type:**
1. Modify `finalize_estimator_internal()`
2. Implement the estimator in your `_estimator_impl()` function
3. Update documentation
4. Add tests for new estimator

### Estimator Not Returned

**Problem:** Result doesn't include `.estimator` column.

**Solution:** Make sure you're using the metric summarizer:

```r
# Good - summarizer adds .estimator
class_metric_summarizer(
  name = "accuracy",
  fn = accuracy_vec,
  data = data,
  truth = !!enquo(truth),
  estimate = !!enquo(estimate),
  estimator = estimator,
  # ...
)

# Bad - manual implementation might forget .estimator
tibble::tibble(
  .metric = "accuracy",
  .estimate = result
  # Missing .estimator!
)
```

## metric_set() Integration Issues

### Metric Not Working in metric_set()

**Problem:**
```r
metrics <- metric_set(mae, rmse, my_custom_metric)
metrics(data, truth, estimate)
# Error or my_custom_metric not in results
```

**Causes & Solutions:**

1. **Metric not wrapped with `new_*_metric()`**

```r
# Bad
mae <- function(data, ...) {
  UseMethod("mae")
}

# Good
mae <- function(data, ...) {
  UseMethod("mae")
}
mae <- new_numeric_metric(mae, direction = "minimize")
```

2. **Wrong metric class**

```r
# Make sure class hierarchy is correct
class(mae)
# [1] "mae" "numeric_metric" "metric" "function"

# For class metrics
class(accuracy)
# [1] "accuracy" "class_metric" "metric" "function"
```

3. **Missing direction or range**

```r
mae <- new_numeric_metric(
  mae,
  direction = "minimize",  # Required
  range = c(0, Inf)        # Optional but recommended
)
```

### metric_set() Returns Wrong Estimator

**Problem:** All metrics in set show same estimator, but they shouldn't.

**Example:**
```r
metrics <- metric_set(accuracy, precision, recall)
result <- metrics(df, truth, estimate)

# All show "binary" but some should show "macro"
```

**Cause:** Metrics in a set must have compatible estimators.

**Solution:**
- For binary data: All metrics will use "binary"
- For multiclass data: Specify estimator explicitly

```r
# Multiclass with specific estimator
result <- metrics(df, truth, estimate, estimator = "macro")
```

### Mixed Metric Types in metric_set()

**Problem:**
```r
metrics <- metric_set(mae, accuracy)  # numeric + class
# Error: Can't mix metric types
```

**Cause:** You can't mix numeric, class, and probability metrics in one set.

**Solution:** Create separate metric sets:

```r
numeric_metrics <- metric_set(mae, rmse, mse)
class_metrics <- metric_set(accuracy, precision, recall)
```

## Case Weight Issues

### Case Weights Not Working

**Problem:** Weighted and unweighted results are identical.

**Diagnosis:**

```r
# Check if weights are being used
df <- data.frame(
  truth = 1:5,
  estimate = c(1.5, 2.5, 2.5, 3.5, 4.5),
  weights = c(1, 1, 1, 1, 100)  # Heavy weight on last
)

result_unweighted <- mae(df, truth, estimate)
result_weighted <- mae(df, truth, estimate, case_weights = weights)

# These should be different!
result_unweighted$.estimate == result_weighted$.estimate
```

**Solutions:**

1. **Using `yardstick_mean()` correctly**

```r
# Good - passes weights
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)
  yardstick_mean(errors, case_weights = case_weights)
}

# Bad - ignores weights
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)
  mean(errors)  # Doesn't use case_weights!
}
```

2. **Converting hardhat weights**

```r
# yardstick_mean() handles this, but if implementing manually:
if (!is.null(case_weights)) {
  if (inherits(case_weights, c("hardhat_importance_weights",
                               "hardhat_frequency_weights"))) {
    case_weights <- as.double(case_weights)
  }
  weighted.mean(x, w = case_weights)
}
```

3. **Weights column must be hardhat type**

```r
# Create proper hardhat weights
df$wt <- hardhat::importance_weights(df$weights)

# Then use in metric
mae(df, truth, estimate, case_weights = wt)
```

### Case Weights Causing Errors

**Problem:**
```r
Error: All case weights must be non-negative
```

**Cause:** Negative weights in data.

**Solution:** Validate input data has non-negative weights.

## Package Check Issues

### Check Fails: Examples Too Long

**Problem:**
```r
checking examples ... ERROR
Examples with CPU time > 2.5 times elapsed time
```

**Solution:** Use `\donttest{}` for slow examples:

```roxygen
#' @examples
#' # Quick example
#' mae(data, truth, estimate)
#'
#' \donttest{
#' # Slower example with cross-validation
#' result <- tune::fit_resamples(...)
#' }
```

### Check Fails: Tests Too Long

**Problem:** Test suite takes too long.

**Solution:** Make tests faster:
- Use smaller test datasets
- Skip slow tests on CRAN: `skip_on_cran()`
- Parallelize independent tests

### Check Fails: Snapshot Changes

**Problem:**
```r
checking tests ... ERROR
Snapshot test failed
```

**Solution:**

```r
# Review changes
testthat::snapshot_review()

# If changes are intentional, accept them
testthat::snapshot_accept()

# If unintentional, fix code and re-test
```

### Check Fails: Undefined Global Variables

**Problem:**
```r
checking R code for possible problems ... NOTE
  accuracy: no visible binding for global variable '.estimate'
```

**Cause:** Using bare column names in dplyr/rlang code.

**Solution:** Use `.data` pronoun:

```r
# Good
data |> dplyr::mutate(new_col = .data$.estimate * 2)

# Avoid
data |> dplyr::mutate(new_col = .estimate * 2)
```

## Integration Testing Issues

### Metric Doesn't Work with tune

**Problem:** Metric works alone but fails in `tune::tune_grid()`.

**Diagnosis:**

```r
# Test with tune
library(tune)
library(rsample)

# Your metric should work here
result <- tune_grid(
  model,
  recipe,
  resamples = vfold_cv(data),
  metrics = metric_set(mae, rmse, your_metric)
)
```

**Common Issues:**

1. **Metric returns wrong structure**
   - Must return tibble with `.metric`, `.estimator`, `.estimate`

2. **Metric doesn't handle grouped data**
   - Use metric summarizers, they handle groups

3. **Metric fails on resampled data**
   - Test with `rsample::vfold_cv()` data

### Metric Doesn't Work with workflows

**Problem:** Metric works with tune but not workflows.

**Solution:** Make sure metric works with model predictions:

```r
library(workflows)
library(parsnip)

wf <- workflow() |>
  add_model(linear_reg()) |>
  add_formula(mpg ~ .)

fit <- fit(wf, mtcars)
preds <- predict(fit, mtcars)

# Your metric should work with these predictions
mae(bind_cols(mtcars, preds), truth = mpg, estimate = .pred)
```

## Git and PR Issues

### Merge Conflicts

**Problem:** Your branch has conflicts with main.

**Solution:**

```bash
# Update your local main
git checkout main
git pull origin main

# Rebase your branch
git checkout your-branch
git rebase main

# Resolve conflicts in each file
# After resolving each:
git add resolved-file.R
git rebase --continue

# Force push (since rebase rewrites history)
git push --force-with-lease origin your-branch
```

### PR Build Fails

**Problem:** PR checks fail on GitHub Actions.

**Common failures:**

1. **R CMD check fails**
   - Run locally: `devtools::check()`
   - Fix all errors, warnings, notes

2. **Tests fail**
   - Run locally: `devtools::test()`
   - Fix failing tests

3. **Code coverage drops**
   - Add tests for new code
   - Aim for >90% coverage on new code

4. **Lint failures**
   - Run: `lintr::lint_package()`
   - Fix style issues

### PR Review Feedback

**Common requests:**

1. **"Add tests for edge cases"**
   - Add tests for NA handling
   - Add tests for empty data
   - Add tests for perfect predictions

2. **"Update documentation"**
   - Add `@examples`
   - Clarify parameter descriptions
   - Add `@details` section

3. **"Use existing internal helper"**
   - Reviewer points out existing function
   - Refactor to use it

4. **"Match style of existing metrics"**
   - Review similar metrics
   - Match their structure and naming

## Yardstick-Specific Issues

### Estimator Column Missing

**Problem:** Result is missing `.estimator` column.

**Solution:** Always use metric summarizers:

```r
# They automatically add .estimator
numeric_metric_summarizer(...)
class_metric_summarizer(...)
prob_metric_summarizer(...)
```

### Direction Attribute Missing

**Problem:**
```r
attr(my_metric, "direction")
# NULL
```

**Solution:** Set when creating metric:

```r
mae <- new_numeric_metric(
  mae,
  direction = "minimize"  # or "maximize" or "zero"
)
```

### Metric Class Hierarchy Wrong

**Problem:** `metric_set()` doesn't recognize your metric.

**Check class hierarchy:**

```r
class(your_metric)
# Should be: c("your_metric", "numeric_metric", "metric", "function")
#         or: c("your_metric", "class_metric", "metric", "function")
#         or: c("your_metric", "prob_metric", "metric", "function")
```

**Solution:** Use the right `new_*_metric()` function:

```r
# For numeric metrics
new_numeric_metric(fn, direction = "minimize")

# For class metrics
new_class_metric(fn, direction = "maximize")

# For probability metrics
new_prob_metric(fn, direction = "maximize")
```

## Performance Issues

### Metric is Slow

**Problem:** Metric takes too long on large datasets.

**Diagnosis:**

```r
# Profile your code
profvis::profvis({
  mae(large_data, truth, estimate)
})
```

**Common bottlenecks:**

1. **Non-vectorized operations**
   ```r
   # Slow
   for (i in seq_along(truth)) {
     errors[i] <- abs(truth[i] - estimate[i])
   }

   # Fast
   errors <- abs(truth - estimate)
   ```

2. **Unnecessary copies**
   ```r
   # Slow - creates copy
   data <- data |> dplyr::filter(!is.na(truth))

   # Fast - works with indices
   valid <- !is.na(truth)
   truth <- truth[valid]
   ```

3. **Inefficient aggregation**
   ```r
   # Use built-in functions
   mean(errors)  # Fast

   # Avoid manual calculation
   sum(errors) / length(errors)  # Slower
   ```

## Getting Help

### Check Existing Issues

Search yardstick GitHub issues for similar problems:
https://github.com/tidymodels/yardstick/issues

### Ask Tidymodels Team

For yardstick-specific questions:
- Open an issue on GitHub
- Ask in tidymodels Slack (if you have access)
- Tag maintainers in your PR

### Reference Existing Metrics

Study similar metrics in the codebase:
- Look at `R/num-mae.R` for simple numeric metrics
- Look at `R/class-accuracy.R` for class metrics
- Look at `R/prob-roc_auc.R` for probability metrics

## Next Steps

- Review [Testing Patterns (Source)](testing-patterns-source.md) for testing guidance
- Check [Best Practices (Source)](best-practices-source.md) for coding standards
- See [Extension Troubleshooting](package-extension-requirements.md#common-issues-solutions) for common R package issues
