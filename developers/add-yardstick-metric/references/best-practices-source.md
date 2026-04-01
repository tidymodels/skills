# Best Practices for Yardstick Source Development

**Context:** This guide is for **source development** - contributing to the yardstick package directly.

**Key principle:** ✅ **You CAN use internal functions** - you're developing the package, so internals are available.

For extension development (creating new packages), see [Best Practices (Extension)](package-extension-requirements.md#best-practices).

---

## Using Internal Functions in Yardstick

### When to Use Internal Functions

✅ **Use internal functions when:**

- Shared logic exists between multiple metrics

- Complex calculations are already implemented

- Consistency with existing metrics is needed

- Avoiding code duplication

❌ **Don't use internal functions when:**

- Simple logic can be written inline

- The internal function doesn't quite fit your needs

- It would make code less readable

### Finding Existing Internal Functions

```r
# List all objects in yardstick (including internals)
ls("package:yardstick", all.names = TRUE)

# Search for specific internal functions
apropos("yardstick_", where = TRUE)

# View internal function source
yardstick:::yardstick_mean

# Search in package directory
# grep -r "yardstick_" R/
```

### Common Internal Helpers

#### `yardstick_mean()` - Weighted Mean

Use for calculating weighted or unweighted means:

```r
# In your implementation function
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  # Use internal helper
  yardstick_mean(errors, case_weights = case_weights)
}
```

**Why use it:**

- Handles case weights consistently

- Converts hardhat weights automatically

- Matches behavior of other metrics

#### `finalize_estimator_internal()` - Estimator Selection

Use for multiclass metrics with estimator variants:

```r
# In your data frame method
accuracy.data.frame <- function(data, truth, estimate,
                                estimator = NULL, na_rm = TRUE,
                                case_weights = NULL, ...) {
  estimator <- finalize_estimator_internal(
    estimator,
    metric_class = "accuracy",
    call = rlang::caller_env()
  )

  # Rest of implementation
  # ...
}
```

**What it does:**

- Auto-detects binary vs multiclass

- Validates estimator parameter

- Provides consistent error messages

#### `yardstick_remove_missing()` - NA Handling

Use for consistent NA removal:

```r
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
```

#### `yardstick_any_missing()` - Check for NAs

```r
if (yardstick_any_missing(truth, estimate, case_weights)) {
  return(NA_real_)
}
```

#### Validation Functions

```r
# For numeric metrics
check_numeric_metric(truth, estimate, case_weights)

# For class metrics
check_class_metric(truth, estimate, case_weights)

# For probability metrics
check_prob_metric(truth, estimate, case_weights)
```

These provide consistent validation and error messages.

## File Naming Conventions

Yardstick organizes code by metric type:

### Source File Names

- **Numeric metrics**: `R/num-[name].R`

  - Examples: `num-mae.R`, `num-rmse.R`, `num-huber_loss.R`

- **Class metrics**: `R/class-[name].R`

  - Examples: `class-accuracy.R`, `class-precision.R`, `class-recall.R`

- **Probability metrics**: `R/prob-[name].R`

  - Examples: `prob-roc_auc.R`, `prob-mn_log_loss.R`, `prob-brier_class.R`

- **Survival metrics**: `R/surv-[name].R`

  - Examples: `surv-concordance_survival.R`, `surv-brier_survival.R`

- **Quantile metrics**: `R/quant-[name].R`

  - Examples: `quant-weighted_interval_score.R`

### Test File Names Match Source

- `R/num-mae.R` → `tests/testthat/test-num-mae.R`

- `R/class-accuracy.R` → `tests/testthat/test-class-accuracy.R`

## Documentation Patterns

Yardstick uses templates extensively for consistent documentation.

### Using `@template`

Templates are defined in `man-roxygen/` directory:

```r
#' Mean Absolute Error
#'
#' @family numeric metrics
#' @family accuracy metrics
#' @templateVar fn mae
#' @template return
#' @template event_first
#'
#' @inheritParams rmse
#'
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}
```

### Common Templates

**`@template return`** - Standard return value documentation
**`@template event_first`** - Event level documentation for class metrics
**`@template multiclass`** - Multiclass metric documentation

### Using `@templateVar`

Define template variables before using templates:

```r
#' @templateVar fn mae
#' @templateVar metric_fn mae
#' @template return
```

### Inheriting Parameters

Use `@inheritParams` to avoid duplicating parameter documentation:

```r
#' @inheritParams rmse
#' @param delta The delta parameter for Huber loss
```

This inherits `truth`, `estimate`, `na_rm`, `case_weights`, etc. from `rmse`.

## Code Style Specific to Yardstick

### Function Organization

Each metric should have three functions:

```r
# 1. Generic (always exported)
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}

# 2. Data frame method (exported)
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

# 3. Vector method (exported)
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

# 4. Implementation (NOT exported - internal)
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)
  yardstick_mean(errors, case_weights = case_weights)
}
```

### Creating the Metric

Wrap the generic with `new_*_metric()`:

```r
mae <- new_numeric_metric(mae, direction = "minimize")

# For class metrics
accuracy <- new_class_metric(accuracy, direction = "maximize")

# For probability metrics
roc_auc <- new_prob_metric(roc_auc, direction = "maximize")
```

### Use Metric Summarizers

Don't implement the data frame method from scratch. Use the appropriate summarizer:

```r
# For numeric metrics
numeric_metric_summarizer(name = "mae", fn = mae_vec, ...)

# For class metrics
class_metric_summarizer(name = "accuracy", fn = accuracy_vec, ...)

# For probability metrics
prob_metric_summarizer(name = "roc_auc", fn = roc_auc_vec, ...)
```

These handle:

- NSE (non-standard evaluation)

- Grouped data frames

- Case weights

- Error handling

## Creating New Internal Helpers

### When to Create Internal Helpers

Create a new internal helper when:

- Logic is shared by 2+ metrics

- Complex calculation that's hard to understand inline

- Abstraction improves code clarity

### Naming Convention

Internal helpers are NOT exported and typically:

- Start with `yardstick_` for utility functions

- Have descriptive names (e.g., `yardstick_mean`, `yardstick_table`)

- Are documented with roxygen but use `@keywords internal`

### Example Internal Helper

```r
#' Calculate weighted mean
#'
#' Internal helper for calculating weighted or unweighted means.
#'
#' @param x Numeric vector
#' @param case_weights Optional case weights
#'
#' @return Numeric scalar
#' @keywords internal
#' @noRd
yardstick_mean <- function(x, case_weights = NULL) {
  if (is.null(case_weights)) {
    mean(x)
  } else {
    # Convert hardhat weights
    if (inherits(case_weights, c("hardhat_importance_weights",
                                 "hardhat_frequency_weights"))) {
      case_weights <- as.double(case_weights)
    }
    weighted.mean(x, w = case_weights)
  }
}
```

### Don't Export Internal Helpers

Internal helpers should:

- Have `@keywords internal`

- Use `@noRd` to skip documentation generation

- NOT have `@export`

## Error Messages

### Use cli Functions

Yardstick uses cli for error messages:

```r
if (invalid_input) {
  cli::cli_abort(
    "{.arg estimator} must be one of {.val binary}, {.val macro}, or {.val micro}, not {.val {estimator}}.",
    call = call
  )
}
```

### Pass `call` for Better Error Context

```r
accuracy.data.frame <- function(data, truth, estimate,
                                estimator = NULL, ...,
                                call = rlang::caller_env()) {
  # Use call in error messages
  if (is_bad) {
    cli::cli_abort("Error message", call = call)
  }
}
```

### Consistent Error Message Style

Follow existing patterns in yardstick:

```r
# Good
cli::cli_abort("{.arg truth} must be a factor, not {.cls {class(truth)}}.")

# Good
cli::cli_abort("Found {length(extra)} unexpected column{?s}: {.var {extra}}.")

# Avoid
stop("truth must be a factor")
```

## Multiclass Metrics

### Supporting Multiple Estimators

For multiclass metrics, support macro, micro, and macro_weighted:

```r
accuracy.data.frame <- function(data, truth, estimate,
                                estimator = NULL, na_rm = TRUE,
                                case_weights = NULL, ...,
                                call = rlang::caller_env()) {
  # Finalize estimator
  estimator <- finalize_estimator_internal(
    estimator,
    metric_class = "accuracy",
    call = call
  )

  class_metric_summarizer(
    name = "accuracy",
    fn = accuracy_vec,
    data = data,
    truth = !!enquo(truth),
    estimate = !!enquo(estimate),
    estimator = estimator,
    na_rm = na_rm,
    case_weights = !!enquo(case_weights),
    call = call
  )
}
```

### Implement Binary and Estimator Variants

```r
# Binary implementation
accuracy_binary <- function(truth, estimate, case_weights) {
  # Implementation for 2-class case
}

# Multiclass implementation
accuracy_estimator_impl <- function(truth, estimate, estimator, case_weights) {
  if (estimator == "macro") {
    # Per-class average
  } else if (estimator == "micro") {
    # Pool all observations
  } else if (estimator == "macro_weighted") {
    # Weighted by prevalence
  }
}
```

## Working with Confusion Matrices

For class metrics based on confusion matrices:

```r
# Create confusion matrix with weights
xtab <- yardstick_table(truth, estimate, case_weights)

# Extract values (for binary)
tp <- xtab[2, 2]  # True positives
tn <- xtab[1, 1]  # True negatives
fp <- xtab[1, 2]  # False positives
fn <- xtab[2, 1]  # False negatives

# Calculate metric
(tp + tn) / (tp + tn + fp + fn)
```

## Consistency with Existing Metrics

### Study Similar Metrics

Before implementing, study similar existing metrics:

- For numeric metrics: Look at `R/num-mae.R`, `R/num-rmse.R`

- For class metrics: Look at `R/class-accuracy.R`, `R/class-precision.R`

- For probability metrics: Look at `R/prob-roc_auc.R`

### Match Parameter Names and Order

Keep parameter names and order consistent:

```r
# Standard order for numeric metrics
metric_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...)

# Standard order for class metrics
metric_vec <- function(truth, estimate, estimator = NULL, na_rm = TRUE,
                      case_weights = NULL, event_level = "first", ...)

# Standard order for probability metrics
metric_vec <- function(truth, estimate, estimator = NULL, na_rm = TRUE,
                      case_weights = NULL, event_level = "first", ...)
```

### Use Standard Return Format

All metrics return a tibble with:

- `.metric`: Character, metric name

- `.estimator`: Character, estimator type

- `.estimate`: Numeric, metric value

```r
tibble::tibble(
  .metric = "mae",
  .estimator = "standard",
  .estimate = 0.5
)
```

## Performance Considerations

### Vectorization

Prefer vectorized operations:

```r
# Good
errors <- abs(truth - estimate)
mean(errors)

# Avoid
sum(abs(truth - estimate)) / length(truth)
```

### Avoid Unnecessary Copies

```r
# Good - modify in place
if (na_rm) {
  result <- yardstick_remove_missing(truth, estimate, case_weights)
  truth <- result$truth
  estimate <- result$estimate
  case_weights <- result$case_weights
}

# Avoid - creates unnecessary copies
if (na_rm) {
  indices <- !is.na(truth) & !is.na(estimate)
  truth <- truth[indices]
  estimate <- estimate[indices]
  if (!is.null(case_weights)) {
    case_weights <- case_weights[indices]
  }
}
```

## Next Steps

- Review [Testing Patterns (Source)](testing-patterns-source.md) for testing guidance

- Check [Troubleshooting (Source)](troubleshooting-source.md) for common issues

- Study existing metrics in the yardstick repository

- Follow the [Extension Guide](package-extension-requirements.md#best-practices) for code style basics
