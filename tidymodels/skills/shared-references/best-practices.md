# Best Practices for R Package Development

Guide to writing high-quality R code for tidymodels packages.

## Code Style

### Use base pipe

```r
# Good
recipe(mpg ~ ., data = mtcars) |>
  step_center(all_numeric_predictors())

# Avoid
recipe(mpg ~ ., data = mtcars) %>%
  step_center(all_numeric_predictors())
```

The base pipe `|>` is faster, built-in, and the tidymodels standard.

### Anonymous functions

```r
# Single line: use backslash notation
map(x, \(i) i + 1)

# Multi-line: use function()
map(x, function(i) {
  result <- complex_computation(i)
  result + 1
})
```

### For-loops over map()

```r
# Preferred (better error messages)
for (col in columns) {
  new_data[[col]] <- transform(new_data[[col]])
}

# Avoid (harder to debug)
new_data <- map(columns, \(col) transform(new_data[[col]]))
```

**Why prefer for-loops:**
- Better error messages (shows which iteration failed)
- More familiar to most R users
- Easier to debug with `browser()`
- Consistent with tidymodels style

### Minimal comments

```r
# Good: code is self-documenting
means <- colMeans(data)
centered <- sweep(data, 2, means, "-")

# Avoid: over-commenting obvious code
# Calculate column means
means <- colMeans(data)
# Subtract means from each column
centered <- sweep(data, 2, means, "-")
```

Write clear code that doesn't need comments. Add comments only for:
- Complex algorithms
- Non-obvious optimization tricks
- Warnings about edge cases

## Error Messages

### Use cli functions

```r
# Good: cli provides better formatting
if (invalid) {
  cli::cli_abort("{.arg param} must be positive, not {.val {param}}.")
}

if (risky) {
  cli::cli_warn("Column{?s} {.var {col_names}} returned Inf or NaN.")
}

# Avoid: base R error functions
stop("param must be positive")
warning("columns returned Inf or NaN")
```

### cli formatting syntax

```r
# Argument names
cli::cli_abort("{.arg your_param} must be numeric.")

# Code/function names
cli::cli_abort("Use {.code binary} estimator for two classes.")

# Values
cli::cli_abort("Expected 3 columns, got {.val {ncol(data)}}.")

# Variable names
cli::cli_warn("Column{?s} {.var {col_names}} has/have missing values.")

# Pluralization
cli::cli_abort("Found {length(x)} error{?s}.")  # Handles 1 vs many
```

### Error message guidelines

- Be specific about what's wrong
- Tell users what they can do to fix it
- Include actual values when helpful
- Use proper English grammar

```r
# Good
cli::cli_abort(
  "{.arg threshold} must be between 0 and 1, not {.val {threshold}}."
)

# Avoid
stop("Invalid threshold")
```

## Documentation Standards

### Be explicit

```r
#' @param threshold Threshold value for classification. Must be a numeric
#'   value between 0 and 1. Default is 0.5.
```

**Include:**
- Type (numeric, logical, character, factor)
- Valid range or options
- Default value
- Effect on function behavior

### US English

- Use American spelling: "normalize" not "normalise"
- Use sentence case: "Calculate the mean" not "calculate the mean"
- Be consistent throughout

### Wrap roxygen at 80 characters

```r
#' This is a long line that should be wrapped to ensure it doesn't exceed the
#' 80-character limit for better readability in various text editors.
```

### Include practical examples

```r
#' @examples
#' # Basic usage
#' metric_name(data, truth, estimate)
#'
#' # With grouped data
#' data |>
#'   dplyr::group_by(fold) |>
#'   metric_name(truth, estimate)
```

Show realistic use cases, not just minimal examples.

### Don't use dynamic roxygen code

```r
# Bad: calling non-exported functions
#' @return Range: `r metric_range()`  # metric_range() not exported

# Good: static documentation
#' @return Range: 0 to 1
```

## Performance

### Vectorization over loops

**Always prefer vectorized operations:**

```r
# Good: vectorized
errors <- truth - estimate
squared_errors <- errors^2
mean(squared_errors)

# Bad: loop
total <- 0
for (i in seq_along(truth)) {
  total <- total + (truth[i] - estimate[i])^2
}
total / length(truth)
```

**Vectorized functions:**
- Arithmetic: `+`, `-`, `*`, `/`, `^`
- Comparisons: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Logical: `&`, `|`, `!`
- Math: `abs()`, `sqrt()`, `log()`, `exp()`, `sin()`, `cos()`
- Aggregations: `sum()`, `mean()`, `max()`, `min()`, `median()`

### Use matrix operations

**Efficient per-class calculations:**

```r
# Good: matrix operations
confusion_matrix <- yardstick_table(truth, estimate)
tp <- diag(confusion_matrix)
fp <- colSums(confusion_matrix) - tp
fn <- rowSums(confusion_matrix) - tp

# Bad: looping over classes
tp <- numeric(n_classes)
for (i in seq_len(n_classes)) {
  tp[i] <- confusion_matrix[i, i]
}
```

**Use `colSums()` and `rowSums()`:**
```r
# Good
class_totals <- colSums(confusion_matrix)

# Avoid
class_totals <- apply(confusion_matrix, 2, sum)  # Slower
```

### Avoid repeated computations in prep()

```r
# Good: compute once in prep()
prep.step_yourname <- function(x, training, ...) {
  means <- colMeans(training[col_names])  # Computed once
  # Store in step object for use in bake()
}

# Bad: compute in bake() each time
bake.step_yourname <- function(object, new_data, ...) {
  means <- colMeans(new_data[col_names])  # Computed every time!
}
```

### Cache confusion matrix calculations

**Don't recalculate the same thing:**

```r
# Good: calculate once, reuse
metric_impl <- function(truth, estimate, estimator, event_level, case_weights) {
  # Calculate confusion matrix once
  xtab <- yardstick::yardstick_table(truth, estimate, case_weights = case_weights)

  # Use it multiple times
  metric_estimator_impl(xtab, estimator, event_level)
}

# Bad: calculate multiple times
metric_impl <- function(truth, estimate, estimator, event_level, case_weights) {
  # Calculating in each helper call
  binary_result <- metric_binary(truth, estimate, event_level, case_weights)
  # Confusion matrix calculated again inside metric_binary
}
```

### Avoid repeated validations

**Validate once at entry point, trust internally:**

```r
# Good: validate in vec function
metric_vec <- function(truth, estimate, ...) {
  check_numeric_metric(truth, estimate, case_weights)  # Validate once

  metric_impl(truth, estimate, ...)  # Trust the data
}

metric_impl <- function(truth, estimate, ...) {
  # No validation needed - data already validated
  mean((truth - estimate)^2)
}

# Bad: validating multiple times
metric_impl <- function(truth, estimate, ...) {
  check_numeric_metric(truth, estimate, case_weights)  # Redundant!
  mean((truth - estimate)^2)
}
```

### Pre-compute constant values

**Calculate invariants outside loops:**

```r
# Good: compute levels once
levels_list <- levels(truth)
n_levels <- length(levels_list)

for (i in seq_len(n_levels)) {
  # Use pre-computed values
}

# Bad: recomputing each iteration
for (i in seq_len(length(levels(truth)))) {
  levels_list <- levels(truth)  # Redundant!
}
```

### Avoid unnecessary data copies

**Use views/references when possible:**

```r
# Good: work with vectors directly
mean((truth - estimate)^2)

# Avoid: creating intermediate data frames unnecessarily
df_temp <- data.frame(truth = truth, estimate = estimate)
mean((df_temp$truth - df_temp$estimate)^2)
```

### Handle case weights efficiently

**Convert hardhat weights once:**

```r
# Good: convert once at the start
if (!is.null(case_weights)) {
  if (inherits(case_weights, c("hardhat_importance_weights",
                               "hardhat_frequency_weights"))) {
    case_weights <- as.double(case_weights)
  }
  # Now use case_weights multiple times
}

# Bad: converting repeatedly
if (!is.null(case_weights)) {
  result1 <- weighted.mean(x, as.double(case_weights))
  result2 <- weighted.mean(y, as.double(case_weights))  # Converting again!
}
```

### Profile before optimizing

**Focus optimization where it matters:**

1. Start with clear, correct code
2. Profile with `profvis::profvis()` if performance is an issue
3. Optimize the actual bottlenecks
4. Don't prematurely optimize

```r
# Profile your code
profvis::profvis({
  for (i in 1:100) {
    your_function(data)
  }
})
```

### When performance doesn't matter

**Don't optimize unnecessarily:**
- Functions typically called once or few times per evaluation
- Calculation is usually fast compared to model fitting
- Readability and correctness are more important

**Do optimize when:**
- Function called thousands of times (tuning, cross-validation)
- Working with very large datasets (millions of observations)
- Profiling shows the function is the bottleneck

## Code Validation

### Validate early

```r
step_yourname <- function(recipe, ..., your_param = 1) {
  # Validate parameters early
  if (!is.numeric(your_param) || your_param <= 0) {
    cli::cli_abort("{.arg your_param} must be a positive number.")
  }

  # ... rest of function
}

prep.step_yourname <- function(x, training, ...) {
  # Validate data early
  col_names <- recipes_eval_select(x$terms, training, info)
  check_type(training[, col_names], types = c("double", "integer"))

  # ... rest of function
}
```

### Give actionable error messages

```r
# Good: tells user what to do
cli::cli_abort(
  "Columns {.var {bad_cols}} must be numeric.
  Convert to numeric with {.code as.numeric()}."
)

# Avoid: vague errors
stop("Invalid columns")
```

## Memory Management

### Don't store entire datasets

```r
# Good: store only necessary parameters
prep.step_center <- function(x, training, ...) {
  means <- colMeans(training[col_names])  # Just means, not data
  # Return step with means stored
}

# Bad: storing entire training set
prep.step_center <- function(x, training, ...) {
  # Return step with training data stored (memory leak!)
}
```

### Consider memory usage for large data

- Store statistics/parameters, not raw data
- Use sparse matrices when appropriate
- Consider memory-mapped files for very large data

## Testing

### Write tests as you develop

Don't defer testing "for later" - write tests alongside code:

```r
# Development cycle:
# 1. Write function
# 2. Write test
# 3. Run test with devtools::test()
# 4. Fix issues
# 5. Repeat
```

### Test edge cases explicitly

Don't assume functions handle edge cases - test them:

- Empty data frames
- All-NA values
- Single observation
- Perfect predictions
- Extreme numeric values

See [testing-patterns.md](testing-patterns.md) for comprehensive testing guide.

## Code Formatting

After writing code, format it:

```r
# Format current package
air::air_format(".")
```

Or use RStudio: Code → Reformat Code (Cmd/Ctrl + Shift + A)

## Version Control

### Commit messages

```r
# Good: descriptive commits
"Add support for multiclass metrics"
"Fix NA handling in case weights"
"Update documentation examples"

# Avoid: vague commits
"Fix bug"
"Update code"
"Changes"
```

### Commit frequency

- Commit after each logical unit of work
- Commit working, tested code
- Don't commit broken code (except on branches)

## Summary Checklist

Before considering your code complete:

- [ ] Code follows tidymodels style (base pipe, for-loops, etc.)
- [ ] Error messages use cli and are actionable
- [ ] Documentation is complete with examples
- [ ] All functions have tests
- [ ] Tests pass with `devtools::test()`
- [ ] R CMD check passes with `devtools::check()`
- [ ] Code is formatted
- [ ] Performance is adequate for use case
- [ ] No unnecessary optimizations that hurt readability

## Next Steps

- Review testing patterns: [testing-patterns.md](testing-patterns.md)
- Learn documentation: [roxygen-documentation.md](roxygen-documentation.md)
- Set up package: [r-package-setup.md](r-package-setup.md)
- Follow workflow: [development-workflow.md](development-workflow.md)
