---
name: add-yardstick-metric
description: Guide for creating new yardstick metrics. Use when a developer needs to extend yardstick with a custom performance metric, including numeric, class, or probability metrics.
---

# Add Yardstick Metric

Guide for developing new metrics that extend the yardstick package. This skill provides best practices, code templates, and testing patterns for creating custom performance metrics.

## Overview

Creating a custom yardstick metric provides:
- Standardization with existing metrics
- Automatic error handling for types and lengths
- Support for multiclass implementations
- NA handling
- Grouped data frame support
- Integration with `metric_set()`
- Optional autoplot support for visualization (curves and confusion matrices)

## Understanding the Metric System

Before creating metrics, understanding how yardstick's metric system works helps you build metrics that integrate properly with the ecosystem.

### What `new_*_metric()` does

When you wrap your metric function with `new_numeric_metric()`, `new_class_metric()`, or `new_prob_metric()`, it:

1. **Sets attributes** that describe your metric:
   - `direction`: "minimize", "maximize", or "zero" (what's optimal?)
   - `range`: `c(min, max)` (possible values the metric can take)

2. **Creates a class hierarchy**:
   ```r
   # Example for accuracy
   class(accuracy)
   # [1] "accuracy" "class_metric" "metric" "function"
   ```

3. **Enables ecosystem integration**:
   - `metric_set()` knows how to combine your metric with others
   - The metric can be identified and validated
   - Automatic method dispatch works correctly

### Why this matters

**For `metric_set()` composition:**
```r
metrics <- metric_set(accuracy, precision, recall)
```

The metric class hierarchy allows `metric_set()` to:
- Verify all metrics are compatible
- Group results by `.estimator` appropriately
- Apply metrics to data correctly

**For direction and range:**
```r
# These attributes help users understand the metric
attr(accuracy, "direction")  # "maximize"
attr(accuracy, "range")       # c(0, 1)
```

Tools can use this to:
- Know if higher is better or worse
- Validate metric values are in expected range
- Create appropriate visualizations

### The `.estimator` column

Every metric returns a tibble with a `.estimator` column:

**For numeric metrics:**
```r
# Always "standard"
mae(df, truth, estimate)
# .metric .estimator .estimate
# mae     standard   0.5
```

**For class metrics:**
```r
# Depends on number of classes
accuracy(df_binary, truth, estimate)
# .metric  .estimator .estimate
# accuracy binary     0.75

accuracy(df_multiclass, truth, estimate)
# .metric  .estimator .estimate
# accuracy multiclass 0.68
```

**The estimator value comes from `finalize_estimator()`:**
- Binary classification → "binary"
- Multiclass with 3+ levels → "macro", "micro", or "macro_weighted"
- Numeric/regression → "standard"

**Why it matters:** When you use `metric_set()`, results are grouped by `.estimator`:
```r
metrics <- metric_set(accuracy, precision, recall)
metrics(df, truth, estimate)
# All three metrics share the same .estimator value
```

### Class naming conventions

Your metric's primary class should match the function name:
```r
mse <- new_numeric_metric(mse, direction = "minimize", range = c(0, Inf))
class(mse)
# [1] "mse" "numeric_metric" "metric" "function"
```

This enables S3 dispatch for methods like `autoplot.mse()`.

## Prerequisites

### Check and initialize project structure

**CRITICAL: Do this FIRST before attempting to create metrics**

```r
# Check if this is a new package or existing package
if (!file.exists("DESCRIPTION")) {
  # New package - create full structure
  usethis::create_package(".", open = FALSE)
  usethis::use_mit_license()  # or use_gpl3_license()
  usethis::use_package("yardstick")
  usethis::use_package("rlang")
  usethis::use_package("cli")
  usethis::use_testthat()
} else {
  # Existing package - ensure dependencies are present
  usethis::use_package("yardstick")
  usethis::use_package("rlang")
  usethis::use_package("cli")

  # Add testthat if not present
  if (!dir.exists("tests/testthat")) {
    usethis::use_testthat()
  }
}
```

## Metric types

Yardstick supports several metric types:
- **Numeric metrics**: For regression (e.g., MAE, RMSE, MSE)
- **Class metrics**: For classification (e.g., accuracy, precision, recall)
- **Probability metrics**: For class probabilities (e.g., ROC AUC, log loss)
- **Survival metrics**: For survival analysis
- **Quantile metrics**: For quantile predictions

## Design Considerations

Before implementing a new metric, consider whether you actually need to create one.

### When to create a new metric

**Create a new metric when:**
- It measures a genuinely different aspect of model performance
- It's commonly used in your domain and not available in yardstick
- It has a well-defined formula or calculation method
- You'll use it repeatedly across multiple projects

**Don't create a new metric if:**
- It's just a transformation of an existing metric (use `metric_tweak()` instead)
- It can be composed from existing metrics
- It's a one-off calculation for a specific analysis
- It's too domain-specific for general use

### Using `metric_tweak()` for variations

For simple variations of existing metrics, use `metric_tweak()`:

```r
# Create a variant of F-measure with beta = 2
f2_meas <- metric_tweak("f2_meas", f_meas, beta = 2)

# Use it like any other metric
f2_meas(df, truth, estimate)
metric_set(accuracy, f2_meas)
```

This is much simpler than creating a full new metric.

### Naming conventions

**Follow yardstick patterns:**
- Use lowercase with underscores: `mean_squared_error` → `mse`
- Avoid camelCase or PascalCase
- Be consistent with existing naming

**Abbreviations vs full names:**
- Well-known abbreviations: `rmse`, `mae`, `auc` (widely recognized)
- Full names for clarity: `accuracy`, `precision`, `recall` (already short)
- When in doubt, use the full name

**Avoid conflicts:**
```r
# Bad: too generic
error()  # Conflicts with base::error
metric()  # Too vague

# Good: specific and descriptive
prediction_error()
classification_metric()
```

**Examples of good names:**
- `miss_rate` (clear, descriptive)
- `huber_loss` (named after the technique)
- `roc_auc` (standard abbreviation)

### Parameter design

**What should be arguments:**
```r
# Hyperparameters that affect calculation
huber_loss(data, truth, estimate, delta = 1.0)

# Configuration that changes behavior
f_meas(data, truth, estimate, beta = 1)

# Thresholds or cutoffs
classification_cost(data, truth, estimate, costs = c(1, 2))
```

**What should NOT be arguments:**
- Constants that are part of the metric definition
- Values that would break the metric's meaning
- Options that should be separate metrics

**Keep parameters minimal:**
```r
# Good: focused parameters
mse(data, truth, estimate, na_rm = TRUE, case_weights = NULL)

# Bad: too many options
mse(data, truth, estimate, na_rm = TRUE, case_weights = NULL,
    sqrt = FALSE, relative = FALSE, log_scale = FALSE)
# These should be separate metrics: rmse(), relative_mse(), log_mse()
```

Users can always wrap your metric if they need variations:
```r
my_custom_mse <- function(data, truth, estimate) {
  result <- mse(data, truth, estimate)
  result$.estimate <- sqrt(result$.estimate)
  result
}
```

### Single responsibility principle

**Each metric should do one thing well:**

```r
# Good: accuracy measures one thing
accuracy(data, truth, estimate)

# Bad: don't combine multiple metrics
accuracy_and_precision()  # Should be two separate metrics
combined_scores()         # Use metric_set() instead
```

**Compose with `metric_set()` instead:**
```r
# Let users compose metrics
metrics <- metric_set(accuracy, precision, recall, f_meas)
metrics(data, truth, estimate)
```

### Scope and reusability

**Design for general use:**
- Avoid hard-coded domain-specific values
- Make assumptions explicit in documentation
- Allow customization through parameters when appropriate

**Example:**
```r
# Bad: too specific
credit_risk_score(data, truth, estimate)  # Hard-codes credit risk logic

# Good: general with parameters
classification_cost(data, truth, estimate, costs = c(fp = 2, fn = 5))
# Users can set costs for their domain
```

## CRITICAL: Exported vs Internal Functions

Many yardstick helper functions are INTERNAL and not exported. Using them will cause runtime errors.

### ❌ Don't Use (Internal/Not Exported)
- `yardstick_mean()` - NOT EXPORTED
- `get_weights()` - NOT EXPORTED
- `metric_range()` - NOT EXPORTED
- `metric_optimal()` - NOT EXPORTED
- `metric_direction()` - NOT EXPORTED
- `data_altman()` - NOT EXPORTED (test helper)
- `data_three_class()` - NOT EXPORTED (test helper)

### ✅ Use Instead

**For weighted calculations:**
```r
# Instead of yardstick_mean(), use base R weighted.mean()
if (is.null(case_weights)) {
  mean(values)
} else {
  # Handle hardhat weights (convert to numeric)
  wts <- if (inherits(case_weights, "hardhat_importance_weights") ||
             inherits(case_weights, "hardhat_frequency_weights")) {
    as.double(case_weights)
  } else {
    case_weights
  }
  weighted.mean(values, w = wts)
}
```

**EXPORTED yardstick functions you CAN safely use:**
- `check_numeric_metric()` ✓
- `check_class_metric()` ✓
- `check_prob_metric()` ✓
- `yardstick_remove_missing()` ✓
- `yardstick_any_missing()` ✓
- `yardstick_table()` ✓
- `finalize_estimator()` ✓
- `validate_estimator()` ✓
- `abort_if_class_pred()` ✓
- `as_factor_from_class_pred()` ✓
- `numeric_metric_summarizer()` ✓
- `class_metric_summarizer()` ✓
- `prob_metric_summarizer()` ✓
- `new_numeric_metric()` ✓
- `new_class_metric()` ✓
- `new_prob_metric()` ✓

## Creating a numeric metric

Numeric metrics are the simplest to implement. They measure continuous predictions against continuous truth values.

### Step 1: Define the implementation function

Create the core calculation function. Use the `_impl` suffix:

```r
# Example: Mean Squared Error
mse_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- (truth - estimate) ^ 2

  if (is.null(case_weights)) {
    mean(errors)
  } else {
    # Handle hardhat weights
    wts <- if (inherits(case_weights, "hardhat_importance_weights") ||
               inherits(case_weights, "hardhat_frequency_weights")) {
      as.double(case_weights)
    } else {
      case_weights
    }
    weighted.mean(errors, w = wts)
  }
}
```

**Key patterns:**
- Take `truth`, `estimate`, and optionally `case_weights`
- Return a single numeric value
- Use `weighted.mean()` for weighted calculations
- Handle hardhat weight classes by converting to numeric

### Step 2: Create the vector function

```r
mse_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Validate na_rm
  if (!is.logical(na_rm) || length(na_rm) != 1) {
    cli::cli_abort("{.arg na_rm} must be a single logical value.")
  }

  # Validate inputs
  yardstick::check_numeric_metric(truth, estimate, case_weights)

  # Handle NA values
  if (na_rm) {
    result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  mse_impl(truth, estimate, case_weights)
}
```

**Required elements:**
- Validate `na_rm` parameter explicitly
- Use `check_numeric_metric()` for validation
- Handle NA values consistently using `yardstick_remove_missing()`
- Return `NA_real_` if `na_rm = FALSE` and NAs present

### Step 3: Create the data frame method

```r
mse <- function(data, ...) {
  UseMethod("mse")
}

mse <- yardstick::new_numeric_metric(
  mse,
  direction = "minimize",  # or "maximize" or "zero"
  range = c(0, Inf)
)

#' @export
#' @rdname mse
mse.data.frame <- function(data, truth, estimate, na_rm = TRUE,
                           case_weights = NULL, ...) {
  yardstick::numeric_metric_summarizer(
    name = "mse",
    fn = mse_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights)
  )
}
```

**Key patterns:**
- Use `new_numeric_metric()` to create the metric function
- Set `direction` to "minimize", "maximize", or "zero"
- Specify `range` as `c(min, max)` (use `Inf` or `-Inf` for unbounded)
- Use `rlang::enquo()` and `!!` for NSE support
- Export the data frame method with `@export`

## Creating a class metric

Class metrics are more complex due to multiclass support.

### Step 1: Binary implementation

```r
# Example: Miss Rate (False Negative Rate)
miss_rate_binary <- function(data, event_level) {
  # data is a confusion matrix (table)
  col <- if (identical(event_level, "first")) {
    colnames(data)[[1]]
  } else {
    colnames(data)[[2]]
  }
  col2 <- setdiff(colnames(data), col)

  tp <- data[col, col]
  fn <- data[col2, col]

  fn / (fn + tp)
}
```

### Step 2: Multiclass implementation (optional)

```r
miss_rate_multiclass <- function(data, estimator) {
  # Calculate per-class values
  tp <- diag(data)
  tpfn <- colSums(data)
  fn <- tpfn - tp

  # For micro averaging, sum first
  if (estimator == "micro") {
    tp <- sum(tp)
    fn <- sum(fn)
  }

  # Return vector of per-class values (or single value for micro)
  fn / (fn + tp)
}
```

### Step 3: Estimator implementation

```r
miss_rate_estimator_impl <- function(data, estimator, event_level) {
  if (estimator == "binary") {
    miss_rate_binary(data, event_level)
  } else {
    # Calculate per-class metrics
    res <- miss_rate_multiclass(data, estimator)

    # Get weights based on class frequencies
    class_counts <- colSums(data)
    wt <- switch(estimator,
      "macro" = rep(1, length(res)),  # Equal weights
      "macro_weighted" = class_counts,  # Weighted by frequency
      "micro" = rep(1, length(res))  # Already aggregated
    )

    weighted.mean(res, wt)
  }
}

miss_rate_impl <- function(truth, estimate, estimator, event_level, case_weights) {
  xtab <- yardstick::yardstick_table(truth, estimate, case_weights = case_weights)
  miss_rate_estimator_impl(xtab, estimator, event_level)
}
```

### Step 4: Vector function

```r
miss_rate_vec <- function(truth, estimate, estimator = NULL, na_rm = TRUE,
                          case_weights = NULL, event_level = "first", ...) {
  # Validate na_rm
  if (!is.logical(na_rm) || length(na_rm) != 1) {
    cli::cli_abort("{.arg na_rm} must be a single logical value.")
  }

  yardstick::abort_if_class_pred(truth)
  estimate <- yardstick::as_factor_from_class_pred(estimate)

  estimator <- yardstick::finalize_estimator(
    truth,
    estimator,
    metric_class = "miss_rate"
  )

  yardstick::check_class_metric(truth, estimate, case_weights, estimator)

  if (na_rm) {
    result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  miss_rate_impl(truth, estimate, estimator, event_level, case_weights)
}
```

### Step 5: Data frame method

```r
miss_rate <- function(data, ...) {
  UseMethod("miss_rate")
}

miss_rate <- yardstick::new_class_metric(
  miss_rate,
  direction = "minimize",
  range = c(0, 1)
)

#' @export
#' @rdname miss_rate
miss_rate.data.frame <- function(data, truth, estimate, estimator = NULL,
                                 na_rm = TRUE, case_weights = NULL,
                                 event_level = "first", ...) {
  yardstick::class_metric_summarizer(
    name = "miss_rate",
    fn = miss_rate_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    estimator = estimator,
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights),
    event_level = event_level
  )
}
```

### Step 6: Restrict estimator (optional)

If your metric only supports binary classification:

```r
finalize_estimator_internal.miss_rate <- function(metric_dispatcher, x,
                                                   estimator, call) {
  yardstick::validate_estimator(estimator, estimator_override = "binary")

  if (!is.null(estimator)) {
    return(estimator)
  }

  lvls <- levels(x)
  if (length(lvls) > 2) {
    cli::cli_abort(
      "A multiclass {.arg truth} input was provided, but only {.code binary} is supported."
    )
  }

  "binary"
}
```

### Factor level ordering

Factor levels critically affect how classification metrics are calculated. Understanding this helps avoid confusion and errors.

#### How factor levels determine the confusion matrix

The confusion matrix rows and columns follow the order of factor levels:

```r
truth <- factor(c("yes", "no", "yes", "no"), levels = c("yes", "no"))
estimate <- factor(c("yes", "yes", "no", "no"), levels = c("yes", "no"))

yardstick::yardstick_table(truth, estimate)
#         estimate
# truth    yes no
#   yes      1  1
#   no       1  1
```

**The order matches the levels:**
- First level ("yes") = first row and column
- Second level ("no") = second row and column

#### Binary classification: which level is "positive"?

For binary metrics, the "positive" class depends on **both** factor order and `event_level`:

```r
# With levels = c("yes", "no") and event_level = "first"
# "yes" is treated as the positive class

# With levels = c("yes", "no") and event_level = "second"
# "no" is treated as the positive class

# With levels = c("no", "yes") and event_level = "first"
# "no" is treated as the positive class
```

See the next section on event level mechanics for details.

#### Multiclass: affects per-class calculations

For multiclass metrics, factor level order determines:
- Which class corresponds to which row/column in the confusion matrix
- The order of per-class metric calculations
- How averaging is applied

```r
# Three classes with different orderings
truth1 <- factor(x, levels = c("A", "B", "C"))
truth2 <- factor(x, levels = c("C", "B", "A"))

# Confusion matrices will have different row/column orders
# But final averaged metrics should be the same (if using macro averaging)
```

#### Unused levels after filtering

**Critical issue:** Factors retain levels even after filtering:

```r
original <- factor(c("A", "A", "B", "B", "C", "C"), levels = c("A", "B", "C"))
filtered <- original[1:4]  # Only A and B remain

levels(filtered)
# [1] "A" "B" "C"  # C is still a level!

# This affects confusion matrix dimensions
yardstick::yardstick_table(filtered, filtered)
#   A B C
# A 2 0 0
# B 0 2 0
# C 0 0 0  # Empty row/column for unused level
```

**Best practice in your tests:**
Create factors with only the levels you need:

```r
# Good: explicit levels matching the data
truth <- factor(c("A", "A", "B", "B"), levels = c("A", "B"))

# Avoid: extra levels that aren't used
truth <- factor(c("A", "A", "B", "B"), levels = c("A", "B", "C"))
```

**Note:** Most yardstick metrics handle unused levels correctly, but it can affect confusion matrix interpretation and some edge cases.

#### Ensuring consistent levels

When creating test data, always specify levels explicitly:

```r
# Good: explicit, consistent levels
truth <- factor(c("pos", "pos", "neg", "neg"), levels = c("pos", "neg"))
estimate <- factor(c("pos", "neg", "pos", "neg"), levels = c("pos", "neg"))

# Bad: implicit levels (order depends on data)
truth <- factor(c("pos", "pos", "neg", "neg"))      # Levels: "neg", "pos" (alphabetical!)
estimate <- factor(c("pos", "neg", "pos", "neg"))  # Same

# Very bad: inconsistent levels
truth <- factor(c("pos", "neg"), levels = c("pos", "neg"))
estimate <- factor(c("pos", "neg"), levels = c("neg", "pos"))  # Different order!
```

### Event level mechanics

For binary classification, `event_level` specifies which factor level is the "positive" class: `"first"` (default) or `"second"`.

#### Why it matters

Asymmetric metrics (sensitivity, specificity, precision, recall) depend on which class is "positive". Changing `event_level` swaps their meaning. Symmetric metrics (accuracy, MCC) are unaffected.

**Example:**
```r
truth <- factor(c("disease", "disease", "healthy", "healthy"),
                levels = c("disease", "healthy"))
estimate <- factor(c("disease", "healthy", "healthy", "healthy"),
                   levels = c("disease", "healthy"))

# event_level = "first" → "disease" is positive
# sensitivity = 0.5 (1 of 2 diseases detected)
# specificity = 1.0 (2 of 2 healthy identified)

# event_level = "second" → "healthy" is positive
# sensitivity = 1.0 (swapped with specificity above)
# specificity = 0.5 (swapped with sensitivity above)
```

**Best practice:** Order factor levels so the positive class is first, then use default `event_level = "first"`.

#### Implementation pattern

```r
your_metric_vec <- function(truth, estimate, ..., event_level = "first") {
  # Determine which level is the event
  event <- if (identical(event_level, "first")) {
    levels(truth)[1]
  } else {
    levels(truth)[2]
  }
  control <- setdiff(levels(truth), event)

  # Index confusion matrix with event/control
  xtab <- yardstick_table(truth, estimate, case_weights)
  tp <- xtab[event, event]
  fp <- xtab[control, event]
  fn <- xtab[event, control]
  tn <- xtab[control, control]
  # ... use tp, fp, fn, tn in calculation
}
```

**For symmetric metrics:** Include `event_level` parameter for consistency but don't use it.

**For asymmetric metrics:** Always include `event_level`, use it to determine positive class, and document its effect.

#### Testing

```r
test_that("metric respects event_level parameter", {
  truth <- factor(c("yes", "yes", "no", "no"), levels = c("yes", "no"))
  estimate <- factor(c("yes", "no", "yes", "no"), levels = c("yes", "no"))

  result_first <- metric_vec(truth, estimate, event_level = "first")
  result_second <- metric_vec(truth, estimate, event_level = "second")

  expect_false(result_first == result_second)  # Should differ for asymmetric metrics
})
```

#### Common mistakes

- Assuming alphabetical factor order (levels are explicit, not alphabetical)
- Not using `event_level` in asymmetric metric calculations
- Poor documentation of what `event_level` does

## Creating a probability metric

Probability metrics evaluate predicted probabilities rather than hard classifications. These metrics are used when your model outputs probability estimates for each class.

### Key differences from class metrics

**Probability metrics:**
- Accept probability columns (`.pred_class1`, `.pred_class2`, etc.)
- Work with continuous [0, 1] probability values
- Often more informative than hard classifications
- Examples: `roc_auc`, `pr_auc`, `mn_log_loss`, `brier_class`

**Class metrics:**
- Accept factor predictions
- Work with discrete class labels
- Simpler to interpret
- Examples: `accuracy`, `precision`, `recall`

### Understanding probability column structure

For binary classification:
```r
# Data has predicted probabilities for each class
df <- tibble(
  truth = factor(c("yes", "no", "yes", "no")),
  .pred_yes = c(0.9, 0.2, 0.7, 0.3),
  .pred_no = c(0.1, 0.8, 0.3, 0.7)
)
```

For multiclass:
```r
df <- tibble(
  truth = factor(c("A", "B", "C")),
  .pred_A = c(0.7, 0.1, 0.1),
  .pred_B = c(0.2, 0.8, 0.2),
  .pred_C = c(0.1, 0.1, 0.7)
)
```

**Column naming convention:** `.pred_{level}` where `{level}` matches the factor level.

### Step 1: Implementation function for binary case

```r
# Example: Brier Score (Mean Squared Error for probabilities)
brier_class_binary <- function(truth, prob_estimate, event_level) {
  # Determine which probability column to use
  event <- if (identical(event_level, "first")) {
    levels(truth)[1]
  } else {
    levels(truth)[2]
  }

  # Convert truth to 0/1 (1 = event occurred)
  truth_binary <- as.integer(truth == event)

  # Calculate squared errors
  mean((prob_estimate - truth_binary)^2)
}
```

### Step 2: Vector function

```r
brier_class_vec <- function(truth, estimate, estimator = NULL, na_rm = TRUE,
                            case_weights = NULL, event_level = "first", ...) {
  # Validate na_rm
  if (!is.logical(na_rm) || length(na_rm) != 1) {
    cli::cli_abort("{.arg na_rm} must be a single logical value.")
  }

  # Check for class_pred (shouldn't be used with probability metrics)
  yardstick::abort_if_class_pred(truth)

  # Finalize estimator
  estimator <- yardstick::finalize_estimator(
    truth,
    estimator,
    metric_class = "brier_class"
  )

  # Validate inputs - note: using check_prob_metric for probability validation
  yardstick::check_prob_metric(truth, estimate, case_weights, estimator)

  # Handle NAs
  if (na_rm) {
    result <- yardstick::yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick::yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  brier_class_binary(truth, estimate, event_level)
}
```

**Key differences for probability metrics:**
- Use `check_prob_metric()` instead of `check_class_metric()`
- `estimate` is a numeric vector of probabilities, not a factor
- Still need `event_level` to know which probability to use

### Step 3: Data frame method

```r
brier_class <- function(data, ...) {
  UseMethod("brier_class")
}

brier_class <- yardstick::new_prob_metric(
  brier_class,
  direction = "minimize",
  range = c(0, 1)
)

#' @export
#' @rdname brier_class
brier_class.data.frame <- function(data, truth, estimate, estimator = NULL,
                                   na_rm = TRUE, case_weights = NULL,
                                   event_level = "first", ...) {
  yardstick::prob_metric_summarizer(
    name = "brier_class",
    fn = brier_class_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    estimator = estimator,
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights),
    event_level = event_level
  )
}
```

**Key differences:**
- Use `new_prob_metric()` instead of `new_class_metric()`
- Use `prob_metric_summarizer()` instead of `class_metric_summarizer()`

### Handling multiple probability columns

For multiclass probability metrics, the `estimate` parameter can refer to multiple columns:

```r
# User specifies probability columns with dplyr selection
roc_auc(data, truth, c(.pred_A, .pred_B, .pred_C))

# Or using tidyselect helpers
roc_auc(data, truth, starts_with(".pred_"))
```

The `prob_metric_summarizer()` handles extracting the appropriate probability columns based on the truth factor levels.

**Your implementation receives:**
- `truth`: factor vector
- `estimate`: matrix or data frame of probabilities (for multiclass) OR numeric vector (for binary)

For binary metrics, extract the relevant probability:
```r
# estimate is just the probability for the event level
# prob_metric_summarizer handles this for you
```

For multiclass metrics, you'll receive all probability columns:
```r
# estimate is a matrix with columns for each class
# You need to handle the full probability distribution
```

### Multiclass probability metrics

For multiclass (one-vs-all) probability metrics:

```r
brier_class_multiclass <- function(truth, prob_matrix, estimator) {
  # prob_matrix has one column per class
  # Create one-hot encoded truth matrix
  truth_matrix <- model.matrix(~ truth - 1)

  # Calculate Brier score for each class
  per_class <- colMeans((prob_matrix - truth_matrix)^2)

  if (estimator == "micro") {
    # Average all predictions together
    mean(per_class)
  } else {
    # Return per-class scores for macro averaging
    per_class
  }
}
```

Then in your vector function:
```r
if (estimator == "binary") {
  brier_class_binary(truth, estimate, event_level)
} else {
  # estimate is now a matrix for multiclass
  per_class <- brier_class_multiclass(truth, estimate, estimator)

  # Handle averaging
  if (estimator == "macro") {
    mean(per_class)
  } else if (estimator == "macro_weighted") {
    # Weight by class frequency
    class_freq <- table(truth)
    weighted.mean(per_class, class_freq)
  } else {
    # micro already averaged in multiclass function
    per_class
  }
}
```

### Differences in estimator behavior

**For class metrics:** estimator usually defaults based on number of levels
- 2 levels → "binary"
- 3+ levels → "macro"

**For probability metrics:** estimator might behave differently
- Some metrics only support binary (like `pr_auc`)
- Some support one-vs-all multiclass (like `roc_auc`)
- Document clearly what estimators your metric supports

### Common probability metric patterns

**Log loss / Cross-entropy:**
```r
# Binary log loss
-mean(ifelse(truth_binary == 1,
             log(prob_estimate),
             log(1 - prob_estimate)))
```

**Brier score (shown above):**
```r
mean((prob_estimate - truth_binary)^2)
```

**Calibration metrics:**
- Compare predicted probabilities to observed frequencies
- Bin predictions and calculate bias within bins

### Testing probability metrics

```r
test_that("probability metric calculation is correct", {
  df <- data.frame(
    truth = factor(c("yes", "yes", "no", "no"), levels = c("yes", "no")),
    .pred_yes = c(0.9, 0.7, 0.3, 0.1),
    .pred_no = c(0.1, 0.3, 0.7, 0.9)
  )

  # Test with the probability for "yes"
  result <- brier_class_vec(df$truth, df$.pred_yes)

  # Manual calculation:
  # truth binary: 1, 1, 0, 0
  # predictions: 0.9, 0.7, 0.3, 0.1
  # errors: (0.9-1)^2, (0.7-1)^2, (0.3-0)^2, (0.1-0)^2
  #       = 0.01, 0.09, 0.09, 0.01
  # mean = 0.05
  expect_equal(result, 0.05)
})

test_that("probability metric works with data frame interface", {
  df <- data.frame(
    truth = factor(c("yes", "no", "yes", "no"), levels = c("yes", "no")),
    .pred_yes = c(0.9, 0.2, 0.7, 0.3)
  )

  result <- brier_class(df, truth, .pred_yes)

  expect_s3_class(result, "tbl_df")
  expect_equal(result$.metric, "brier_class")
  expect_equal(result$.estimator, "binary")
})
```

### Validation considerations

**Probabilities should sum to 1** (for multiclass):
- For binary, `.pred_yes + .pred_no = 1`
- For multiclass, sum across all `.pred_*` columns should be 1
- `check_prob_metric()` validates this

**Probabilities should be in [0, 1]:**
- Values outside this range are invalid
- `check_prob_metric()` validates this

**Column names must match levels:**
```r
# Good: column names match factor levels
truth = factor(c("A", "B")),
.pred_A = c(0.7, 0.3),
.pred_B = c(0.3, 0.7)

# Bad: mismatched names
truth = factor(c("A", "B")),
.pred_class1 = c(0.7, 0.3),  # Doesn't match "A"
.pred_class2 = c(0.3, 0.7)   # Doesn't match "B"
```

## Documentation

### Roxygen template for numeric metrics

**Do NOT use `@template` tags - they won't exist in your package**

```r
#' Metric Name
#'
#' Brief description of what this metric measures.
#'
#' @family numeric metrics
#'
#' @param data A data frame containing the columns specified by `truth` and
#'   `estimate`.
#' @param truth The column identifier for the true results (numeric). This
#'   should be an unquoted column name.
#' @param estimate The column identifier for the predicted results (numeric).
#'   This should be an unquoted column name.
#' @param na_rm A logical value indicating whether NA values should be stripped
#'   before the computation proceeds. Default is `TRUE`.
#' @param case_weights The optional column identifier for case weights. This
#'   should be an unquoted column name. Default is `NULL`.
#' @param ... Not currently used.
#'
#' @return
#' A tibble with columns `.metric`, `.estimator`, and `.estimate` and 1 row of
#' values.
#'
#' For grouped data frames, the number of rows returned will be the same as the
#' number of groups.
#'
#' For `metric_name_vec()`, a single numeric value (or `NA`).
#'
#' @details
#' [metric_name()] is a metric that should be [maximized/minimized].
#' The output ranges from [min] to [max], with [optimal_value] indicating
#' perfect predictions.
#'
#' The formula for [metric name] is:
#'
#' \deqn{formula here}
#'
#' @author Your Name
#'
#' @examples
#' # Create sample data
#' df <- data.frame(
#'   truth = c(1, 2, 3, 4, 5),
#'   estimate = c(1.1, 2.2, 2.9, 4.1, 5.2)
#' )
#'
#' # Basic usage
#' metric_name(df, truth, estimate)
#'
#' @export
```

### Roxygen template for class metrics

```r
#' Metric Name
#'
#' Brief description of what this metric measures.
#'
#' @family class metrics
#'
#' @param data A data frame containing the columns specified by `truth` and
#'   `estimate`.
#' @param truth The column identifier for the true class results (factor). This
#'   should be an unquoted column name.
#' @param estimate The column identifier for the predicted class results
#'   (factor). This should be an unquoted column name.
#' @param estimator One of "binary", "macro", "macro_weighted", or "micro" to
#'   specify the type of averaging to be done. Default is `NULL` which
#'   automatically selects based on the number of classes.
#' @param na_rm A logical value indicating whether NA values should be stripped
#'   before the computation proceeds. Default is `TRUE`.
#' @param case_weights The optional column identifier for case weights. This
#'   should be an unquoted column name. Default is `NULL`.
#' @param event_level A string either "first" or "second" to specify which level
#'   of truth to consider as the "event". Default is "first".
#' @param ... Not currently used.
#'
#' @return
#' A tibble with columns `.metric`, `.estimator`, and `.estimate` and 1 row of
#' values.
#'
#' For grouped data frames, the number of rows returned will be the same as the
#' number of groups.
#'
#' For `metric_name_vec()`, a single numeric value (or `NA`).
#'
#' @section Multiclass:
#'
#' Explanation of multiclass behavior and estimator types.
#'
#' @details
#' [metric_name()] is a metric that should be [maximized/minimized].
#' The output ranges from [min] to [max].
#'
#' The formula for binary classification is:
#'
#' \deqn{formula here}
#'
#' @examples
#' # Binary classification
#' df <- data.frame(
#'   truth = factor(c("yes", "yes", "no", "no")),
#'   estimate = factor(c("yes", "no", "yes", "no"))
#' )
#'
#' metric_name(df, truth, estimate)
#'
#' @export
```

## Autoplot Support (Optional)

Autoplot provides automatic visualization for metrics that return structured, multi-dimensional data. This section guides you through implementing autoplot support when appropriate.

### When to implement autoplot

**Autoplot is appropriate for:**
- **Confusion matrices**: Binary or multiclass classification results that can be shown as heatmaps or mosaic plots
- **Curve metrics**: Metrics that trace a curve (ROC, PR, gain, lift) across thresholds or other continuous values
- **Grouped/stratified metrics**: When the metric naturally produces multiple facetable results
- **Other structured outputs**: Any metric returning data that tells a visual story

**NOT appropriate for:**
- **Single-value summary metrics**: accuracy, RMSE, F1 score, MAE, etc. - these return a single number with nothing to plot

**Decision guide**: If your metric returns a tibble with multiple rows or a special object (like a confusion matrix), consider autoplot. If it returns a single value, skip it.

### Data structure requirements

Before implementing autoplot, ensure your metric returns properly structured data.

**For curve metrics**, your metric must return a tibble with:
```r
# Standard structure for curve metrics
tibble::tibble(
  .threshold = ...,     # Or other identifier column
  sensitivity = ...,    # Value column 1
  specificity = ...,    # Value column 2 (optional)
  # Additional columns as needed
)
```

**For confusion matrices**, your metric must return:
```r
# An object of class "conf_mat"
# Typically created via yardstick::conf_mat()
```

The returned object MUST have a class attribute that autoplot can dispatch on.

### Dependencies and imports

**Add ggplot2 to your package:**
```r
usethis::use_package("ggplot2")
```

**In your NAMESPACE** (via roxygen2):
- Add `#' @export` to your autoplot method
- The autoplot generic comes from ggplot2, so you don't need to import it separately
- Use `ggplot2::` prefix for all ggplot2 functions to avoid import issues

### S3 method registration

Autoplot uses S3 dispatch based on the class of your metric's return value.

**Method naming pattern:**
```r
autoplot.your_metric_class <- function(object, ...) {
  # Implementation
}
```

**How the class is determined:**
```r
# When you create your metric output, set the class
result <- tibble::tibble(...)
class(result) <- c("roc_curve", "data.frame")  # Example for ROC curve

# Then autoplot will dispatch to:
autoplot.roc_curve <- function(object, ...) { ... }
```

**For confusion matrices**, the class is already set by `yardstick::conf_mat()`.

### Complete implementation template: Curve metric

```r
#' Plot an ROC curve
#'
#' @param object A data frame from [roc_curve()].
#' @param ... Additional arguments passed to [ggplot2::geom_line()]. Common
#'   options include color, size, linetype, and alpha.
#'
#' @return A ggplot object.
#'
#' @export
autoplot.roc_curve <- function(object, ...) {
  ggplot2::ggplot(object, ggplot2::aes(x = 1 - specificity, y = sensitivity)) +
    ggplot2::geom_line(...) +
    ggplot2::geom_abline(lty = 2, color = "grey50") +
    ggplot2::coord_equal() +
    ggplot2::labs(
      x = "1 - Specificity",
      y = "Sensitivity",
      title = "ROC Curve"
    ) +
    ggplot2::theme_minimal()
}
```

### Complete implementation template: Confusion matrix with type

```r
#' Plot a confusion matrix
#'
#' @param object A `conf_mat` object from [conf_mat()].
#' @param type Type of plot. Options: "heatmap" (default) or "mosaic".
#' @param ... Not currently used.
#'
#' @return A ggplot object.
#'
#' @export
autoplot.conf_mat <- function(object, type = "heatmap", ...) {
  type <- rlang::arg_match(type, c("heatmap", "mosaic"))

  # Convert confusion matrix to data frame for plotting
  df <- as.data.frame(object$table)

  if (type == "heatmap") {
    ggplot2::ggplot(df, ggplot2::aes(x = Prediction, y = Truth, fill = Freq)) +
      ggplot2::geom_tile() +
      ggplot2::geom_text(ggplot2::aes(label = Freq), color = "white", size = 8) +
      ggplot2::scale_fill_gradient(low = "grey90", high = "grey20") +
      ggplot2::theme_minimal() +
      ggplot2::labs(title = "Confusion Matrix")
  } else {
    # Mosaic plot implementation
    ggplot2::ggplot(df, ggplot2::aes(x = Prediction, y = Freq, fill = Truth)) +
      ggplot2::geom_col(position = "fill") +
      ggplot2::theme_minimal() +
      ggplot2::labs(
        title = "Confusion Matrix (Mosaic)",
        y = "Proportion"
      )
  }
}
```

### Handling the `...` parameter

The `...` parameter allows users to customize plot aesthetics without adding many explicit parameters.

**Common patterns:**

```r
# Pass ... to geom layer for aesthetic customization
autoplot.your_curve <- function(object, ...) {
  ggplot2::ggplot(object, ggplot2::aes(x = x, y = y)) +
    ggplot2::geom_line(...)  # User can set color, size, linetype, alpha, etc.
}

# Or pass to labs for title customization
autoplot.your_curve <- function(object, ...) {
  p <- ggplot2::ggplot(object, ggplot2::aes(x = x, y = y)) +
    ggplot2::geom_line()

  p + ggplot2::labs(...)  # User can set title, subtitle, caption, etc.
}
```

**Document what `...` does:**
```r
#' @param ... Additional arguments passed to [ggplot2::geom_line()]. Common
#'   options include color, size, linetype, and alpha.
```

**Test that common arguments work:**
```r
test_that("autoplot accepts ggplot2 aesthetics", {
  result <- your_curve_metric(df, truth, estimate)

  # Should not error with common aesthetics
  expect_no_error(autoplot(result, color = "red", size = 2))
  expect_no_error(autoplot(result, linetype = "dashed", alpha = 0.7))
})
```

### Handling the `type` parameter

Use `type` when there are genuinely different ways to visualize the same data (not just minor variations).

**Implementation pattern:**
```r
autoplot.conf_mat <- function(object, type = "heatmap", ...) {
  # Validate the type argument
  type <- rlang::arg_match(type, c("heatmap", "mosaic"))

  # Branch based on type
  if (type == "heatmap") {
    # Heatmap implementation
  } else if (type == "mosaic") {
    # Mosaic implementation
  }
}
```

**When to use type:**
- ✅ Fundamentally different plot styles (heatmap vs mosaic, line vs step)
- ✅ Different data representations (raw vs normalized)
- ❌ Minor aesthetic changes (use `...` instead)
- ❌ Color schemes (use `...` with scale functions)

**Testing type parameter:**
```r
test_that("autoplot type parameter works", {
  result <- conf_mat(df, truth, estimate)

  # Each type should work
  expect_no_error(autoplot(result, type = "heatmap"))
  expect_no_error(autoplot(result, type = "mosaic"))

  # Invalid type should error
  expect_error(autoplot(result, type = "invalid"))
})
```

### Custom parameters

For metric-specific customization, add dedicated parameters.

**Example with boolean flag:**
```r
#' @param show_diagonal Should the diagonal reference line be shown?
#'   Default is TRUE.
autoplot.roc_curve <- function(object, show_diagonal = TRUE, ...) {
  check_bool(show_diagonal)  # Validate with standalone checker

  p <- ggplot2::ggplot(object, ggplot2::aes(x = 1 - specificity, y = sensitivity)) +
    ggplot2::geom_line(...)

  if (show_diagonal) {
    p <- p + ggplot2::geom_abline(lty = 2, color = "grey50")
  }

  p
}
```

**Example with numeric parameter:**
```r
#' @param alpha Transparency level for confidence bands. Default is 0.3.
autoplot.survival_curve <- function(object, alpha = 0.3, ...) {
  check_number_decimal(alpha, min = 0, max = 1)

  # Use alpha in ribbon layer
  ggplot2::ggplot(object) +
    ggplot2::geom_ribbon(ggplot2::aes(ymin = lower, ymax = upper), alpha = alpha)
}
```

### Testing autoplot

**Basic structure test:**
```r
test_that("autoplot returns ggplot object", {
  result <- your_curve_metric(df, truth, estimate)
  p <- autoplot(result)

  expect_s3_class(p, "gg")
  expect_s3_class(p, "ggplot")
})

test_that("autoplot works with metric output", {
  result <- your_metric(df, truth, estimate)

  # Should not error
  expect_no_error(autoplot(result))
})
```

**Test customization:**
```r
test_that("autoplot respects custom parameters", {
  result <- your_curve_metric(df, truth, estimate)

  # Test with reference line off
  p1 <- autoplot(result, show_diagonal = FALSE)
  expect_s3_class(p1, "ggplot")

  # Test with reference line on
  p2 <- autoplot(result, show_diagonal = TRUE)
  expect_s3_class(p2, "ggplot")
})
```

**Note on visual testing**: Without snapshot testing infrastructure, focus on testing that the function runs without error and returns the correct object type. Visual inspection during development is sufficient.

### When to skip autoplot

**Skip autoplot if:**
- Your metric returns a single numeric value (the vast majority of metrics)
- You're unsure how to visualize it meaningfully
- The metric is for internal use only
- You want to iterate on the metric first, add autoplot later

**Autoplot is completely optional**. Your metric works perfectly fine without it. Users can always create their own plots using the data your metric returns.

### The metric-autoplot relationship

**Understand the flow:**

1. **Metric function returns data** with a specific class:
```r
your_curve_metric <- function(data, truth, estimate) {
  # ... calculation ...

  result <- tibble::tibble(
    threshold = thresholds,
    sensitivity = sens_values,
    specificity = spec_values
  )

  class(result) <- c("your_curve_metric", class(result))
  result
}
```

2. **Autoplot dispatches on that class**:
```r
# When user calls:
autoplot(result)

# R looks for:
autoplot.your_curve_metric(result)
```

3. **Your autoplot method receives the data and plots it**:
```r
autoplot.your_curve_metric <- function(object, ...) {
  ggplot2::ggplot(object, ggplot2::aes(x = threshold, y = sensitivity)) +
    ggplot2::geom_line(...)
}
```

### Critical warnings

**Don't try these:**
- ❌ **Don't look for yardstick plotting helpers** - they may not exist or aren't exported
- ❌ **Don't assume autoplot is automatic** - you must explicitly implement it
- ❌ **Don't try to reuse yardstick's internal plotting code** - build your own with ggplot2
- ❌ **Don't forget `#' @export`** - the method won't be available without it
- ❌ **Don't add autoplot to single-value metrics** - only for curves and matrices
- ❌ **Don't overcomplicate** - a simple line plot is often sufficient

### Users can extend plots

Document that users can modify the returned plot:

```r
#' @return A ggplot object that can be further customized using ggplot2.
#'
#' @examples
#' # Create and customize the plot
#' p <- autoplot(result)
#' p +
#'   ggplot2::theme_minimal() +
#'   ggplot2::labs(title = "My Custom Title")
```

This allows users to add themes, modify scales, add annotations, etc., without requiring you to expose every possible customization as a parameter.

## Testing

### Create your own test data

**Do NOT rely on yardstick internal test helpers like `data_altman()` or `data_three_class()`**

```r
# Simple test data patterns for numeric metrics
test_that("Calculations are correct", {
  df <- data.frame(
    truth = c(1, 2, 3, 4, 5),
    estimate = c(1.1, 2.2, 2.9, 4.1, 4.8)
  )

  # Calculate expected value by hand
  expected <- ...  # manual calculation

  expect_equal(
    metric_name_vec(df$truth, df$estimate),
    expected
  )
})

# Binary classification test data
test_that("Binary calculations are correct", {
  df <- data.frame(
    truth = factor(c("yes", "yes", "no", "no"), levels = c("yes", "no")),
    estimate = factor(c("yes", "no", "yes", "no"), levels = c("yes", "no"))
  )

  # TP=1, FP=1, TN=1, FN=1
  # Calculate expected value from formula
  expect_equal(
    metric_name_vec(df$truth, df$estimate),
    expected_value
  )
})

# Multiclass test data
test_that("Multiclass calculations are correct", {
  df <- data.frame(
    truth = factor(c("A", "A", "B", "B", "C", "C")),
    estimate = factor(c("A", "B", "B", "C", "C", "A"))
  )

  # 2 correct (A-A, B-B), 4 incorrect
  # Calculate per-class and averaged metrics
  expect_equal(
    metric_name_vec(df$truth, df$estimate),
    expected_value
  )
})
```

### Standard test suite template

```r
test_that("Perfect predictions give optimal value", {
  truth <- c(10, 20, 30, 40, 50)
  estimate <- c(10, 20, 30, 40, 50)

  expect_equal(
    metric_name_vec(truth, estimate),
    optimal_value  # 0 for minimize, 1 for maximize, etc.
  )
})

test_that("Case weights calculations are correct", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.5, 2.5, 3.5),
    case_weights = c(1, 2, 1)
  )

  # Calculate weighted expectation by hand
  # errors = (0.5, 0.5, 0.5)
  # weighted = (1*0.5 + 2*0.5 + 1*0.5) / (1+2+1) = 2/4 = 0.5
  expect_equal(
    metric_name_vec(df$truth, df$estimate, case_weights = df$case_weights),
    expected_weighted_value
  )
})

test_that("Works with hardhat case weights", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.5, 2.5, 3.5)
  )

  imp_wgt <- hardhat::importance_weights(c(1, 2, 1))
  freq_wgt <- hardhat::frequency_weights(c(1, 2, 1))

  expect_no_error(
    metric_name_vec(df$truth, df$estimate, case_weights = imp_wgt)
  )

  expect_no_error(
    metric_name_vec(df$truth, df$estimate, case_weights = freq_wgt)
  )
})

test_that("na_rm argument works", {
  expect_error(
    metric_name_vec(c(1, 2), c(1, 2), na_rm = "yes"),
    "must be a single logical value"
  )
})

test_that("NA handling with na_rm = TRUE", {
  truth <- c(1, 2, NA, 4)
  estimate <- c(1.1, NA, 3.1, 4.1)

  # Only use non-NA pairs: (1, 1.1) and (4, 4.1)
  expect_equal(
    metric_name_vec(truth, estimate, na_rm = TRUE),
    expected_value_from_complete_pairs
  )
})

test_that("NA handling with na_rm = FALSE", {
  truth <- c(1, 2, NA)
  estimate <- c(1, 2, 3)

  expect_equal(
    metric_name_vec(truth, estimate, na_rm = FALSE),
    NA_real_
  )
})

test_that("Data frame method works", {
  df <- data.frame(
    truth = c(1, 2, 3),
    estimate = c(1.1, 2.2, 3.3)
  )

  result <- metric_name(df, truth, estimate)

  expect_s3_class(result, "tbl_df")
  expect_equal(result$.metric, "metric_name")
  expect_equal(result$.estimator, "standard")
  expect_equal(nrow(result), 1)
})

test_that("Metric has correct attributes", {
  expect_equal(attr(metric_name, "direction"), "maximize")  # or "minimize"
  expect_equal(attr(metric_name, "range"), c(min_value, max_value))
})

test_that("Works with metric_set", {
  df <- data.frame(
    truth = c(1, 2, 3, 4, 5),
    estimate = c(1.1, 2.2, 2.9, 4.1, 5.2)
  )

  metrics <- yardstick::metric_set(metric_name, yardstick::rmse)

  result <- metrics(df, truth, estimate)

  expect_s3_class(result, "tbl_df")
  expect_equal(nrow(result), 2)
  expect_true("metric_name" %in% result$.metric)
  expect_true("rmse" %in% result$.metric)
})

test_that("Works with grouped data", {
  df <- data.frame(
    group = rep(c("A", "B"), each = 3),
    truth = c(1, 2, 3, 4, 5, 6),
    estimate = c(1.1, 2.1, 3.1, 4.1, 5.1, 6.1)
  )

  result <- df |>
    dplyr::group_by(group) |>
    metric_name(truth, estimate)

  expect_equal(nrow(result), 2)
  expect_equal(result$group, c("A", "B"))
})
```

### Real-world edge cases

Test edge cases explicitly to avoid surprises in production:

**Empty data frames:**
```r
test_that("handles empty data frames", {
  df <- data.frame(truth = numeric(0), estimate = numeric(0))
  result <- metric_name(df, truth, estimate)
  expect_s3_class(result, "tbl_df")
  # .estimate will be NA or NaN (mean(numeric(0)) = NaN, sum(numeric(0)) = 0)
})
```

**All-`NA` values:**
```r
test_that("handles all-NA values", {
  result <- metric_name_vec(c(NA, NA), c(1, 2), na_rm = TRUE)
  expect_true(is.na(result) || is.nan(result))  # Empty after removing NAs
})
```

**Additional edge cases to test:**
- **Single observation**: May be undefined for variance-based metrics
- **Factors with unused levels**: Confusion matrix includes empty rows/columns
- **Zero case weights**: `weighted.mean()` with all-zero weights returns `NaN`
- **Perfect predictions**: All correct (should give optimal value, not error)
- **Perfect anti-predictions**: All incorrect (should give worst value)
- **Single-class predictions**: Model only predicts one class (some metrics become undefined)
- **Extreme numeric values**: Very large (`1e10`) or small (`1e-10`) values shouldn't overflow/underflow

### Integration testing

Ensure your metric works within the yardstick ecosystem:

**metric_set() compatibility:**
```r
test_that("works in metric_set with other metrics", {
  df <- data.frame(truth = 1:5, estimate = c(1.1, 2.2, 2.9, 4.1, 5.2))

  metrics <- yardstick::metric_set(metric_name, yardstick::rmse, yardstick::mae)
  result <- metrics(df, truth, estimate)

  expect_equal(nrow(result), 3)
  expect_true("metric_name" %in% result$.metric)
  expect_true(all(result$.estimator == "standard"))
})
```

**All estimator types (classification):**
```r
test_that("works with all estimator types", {
  df <- data.frame(
    truth = factor(c("A", "A", "B", "B", "C", "C")),
    estimate = factor(c("A", "B", "B", "C", "C", "A"))
  )

  expect_equal(metric_name(df, truth, estimate)$.estimator, "macro")  # Default
  expect_equal(metric_name(df, truth, estimate, estimator = "macro_weighted")$.estimator, "macro_weighted")
  expect_equal(metric_name(df, truth, estimate, estimator = "micro")$.estimator, "micro")
})
```

**Grouped data:**
```r
test_that("respects dplyr groups", {
  df <- data.frame(
    group = rep(c("A", "B"), each = 3),
    truth = 1:6,
    estimate = c(1.1, 2.1, 3.1, 4.1, 5.1, 6.1)
  )

  result <- df |> dplyr::group_by(group) |> metric_name(truth, estimate)
  expect_equal(nrow(result), 2)  # One row per group
})
```

**Other integration patterns to test:** Case weights with grouping, multiple grouping variables, typical tidymodels workflows with multiple metrics.

## File naming conventions

- **Source files**: `R/[type]-[name].R`
  - Examples: `R/num-mae.R`, `R/class-accuracy.R`, `R/prob-roc_auc.R`
- **Test files**: `tests/testthat/test-[type]-[name].R`
  - Examples: `test-num-mae.R`, `test-class-accuracy.R`
- Use prefixes: `num-`, `class-`, `prob-`, `surv-`, etc.

## Common patterns

### Confusion matrix metrics

Use `yardstick_table()` to create weighted confusion matrices:

```r
xtab <- yardstick::yardstick_table(truth, estimate, case_weights = case_weights)
```

#### What yardstick_table returns

`yardstick_table()` returns a base R `table` object (which is technically an array):

```r
xtab <- yardstick_table(truth, estimate)
class(xtab)
# [1] "table"

# It's a 2D array with dimnames
dimnames(xtab)
# $truth
# [1] "yes" "no"
#
# $estimate
# [1] "yes" "no"
```

**Structure:**
- Rows represent actual truth values
- Columns represent predicted estimate values
- Cell values are counts (or weighted counts if case_weights provided)

#### How case_weights are incorporated

When you provide `case_weights`, they're summed within each cell:

```r
truth <- factor(c("A", "A", "B", "B"))
estimate <- factor(c("A", "B", "A", "B"))
weights <- c(1, 2, 3, 4)

xtab <- yardstick_table(truth, estimate, case_weights = weights)
#      estimate
# truth A B
#   A   1 2  # Weights for correct/incorrect "A" predictions
#   B   3 4  # Weights for incorrect/correct "B" predictions
```

Without weights, these would just be counts (1, 1, 1, 1).

#### Accessing elements correctly

**Critical:** Use character names, not integer indices:

```r
# Good: use level names
tp <- xtab["yes", "yes"]
fp <- xtab["no", "yes"]

# Bad: numeric indices can be confusing
tp <- xtab[1, 1]  # Which level is row 1?
```

**Pattern for any metric:**
```r
# Determine event and control levels
event <- if (identical(event_level, "first")) {
  levels(truth)[1]
} else {
  levels(truth)[2]
}
control <- setdiff(levels(truth), event)

# Access using names
tp <- xtab[event, event]      # True positives: actual event, predicted event
fp <- xtab[control, event]    # False positives: actual control, predicted event
fn <- xtab[event, control]    # False negatives: actual event, predicted control
tn <- xtab[control, control]  # True negatives: actual control, predicted control
```

**Remember:**
- First index (row) = actual truth
- Second index (column) = prediction

#### Confusion matrix for multiclass

For multiclass, the table is larger:

```r
truth <- factor(c("A", "A", "B", "B", "C", "C"))
estimate <- factor(c("A", "B", "A", "C", "C", "A"))

xtab <- yardstick_table(truth, estimate)
#      estimate
# truth A B C
#   A   1 1 0
#   B   1 0 1
#   C   1 0 1
```

**Extracting per-class metrics:**
```r
# True positives: diagonal elements
tp <- diag(xtab)
# [1] 1 0 1  (for A, B, C respectively)

# Total actual per class: row sums
actual_per_class <- rowSums(xtab)
# [1] 2 2 2

# Total predicted per class: column sums
predicted_per_class <- colSums(xtab)
# [1] 3 1 2

# False positives for each class: column sum minus diagonal
fp <- colSums(xtab) - diag(xtab)
# [1] 2 1 1

# False negatives for each class: row sum minus diagonal
fn <- rowSums(xtab) - diag(xtab)
# [1] 1 2 1
```

#### Common mistakes with table indexing

**Mistake 1: Row/column confusion**
```r
# Wrong: thinking columns are truth
tp <- xtab[event, event]  # This is CORRECT

# Wrong interpretation: "predicted event" as rows
tp <- xtab[event, event]  # Actually: "actual event" as rows
```

Remember: `xtab[truth_value, predicted_value]`

**Mistake 2: Assuming numeric indices**
```r
# Fragile: depends on factor level order
tp <- xtab[1, 1]
fp <- xtab[2, 1]

# Robust: uses level names
tp <- xtab[event, event]
fp <- xtab[control, event]
```

**Mistake 3: Not handling zero counts**
```r
# When a cell is zero, it's still numeric
fp <- xtab[control, event]  # Could be 0

# Don't need special handling for zeros
sensitivity <- tp / (tp + fn)  # Works even if fn = 0 (gives Inf or NaN)
```

#### Factor level ordering and the table

The table rows and columns follow factor level order:

```r
truth <- factor(c("B", "A"), levels = c("A", "B"))
estimate <- factor(c("B", "A"), levels = c("A", "B"))

xtab <- yardstick_table(truth, estimate)
#      estimate
# truth A B
#   A   1 0
#   B   0 1

# Levels order matches table order:
rownames(xtab)  # "A", "B"
colnames(xtab)  # "A", "B"
```

This is why it's important to specify factor levels explicitly in tests.

### Multiclass averaging

Three types:
- **macro**: Unweighted average across classes (equal weight for each class)
- **macro_weighted**: Weighted by class frequency in truth
- **micro**: Pool all classes, calculate once

Calculate weights manually:
```r
# For macro
wt <- rep(1, n_classes)

# For macro_weighted
class_counts <- colSums(confusion_matrix)
wt <- class_counts

# Then use weighted.mean()
weighted.mean(per_class_values, wt)
```

### Case weights

Always include `case_weights = NULL` parameter. Handle hardhat weights:

```r
if (is.null(case_weights)) {
  mean(values)
} else {
  # Convert hardhat weights to numeric
  wts <- if (inherits(case_weights, "hardhat_importance_weights") ||
             inherits(case_weights, "hardhat_frequency_weights")) {
    as.double(case_weights)
  } else {
    case_weights
  }
  weighted.mean(values, w = wts)
}
```

## Step-by-step workflow

1. ✅ **Initialize/verify package structure** (run prerequisite code first)
2. ✅ **Create implementation function** `metric_impl()` with core logic
3. ✅ **Create vector function** `metric_vec()` with validation and NA handling
4. ✅ **Create generic and data frame method** with proper NSE (`enquo`, `!!`)
5. ✅ **Add comprehensive documentation** (use templates above, no external templates)
6. ✅ **Create tests** (use simple inline test data, not yardstick internals)
7. ✅ **Add autoplot support (optional)** - only if metric returns curves or confusion matrices
8. ✅ **Run and verify:**

```bash
# From command line
Rscript -e "devtools::document()"  # Generate documentation
Rscript -e "devtools::load_all()"  # Load package
Rscript -e "devtools::test()"      # Run tests
```

## Common pitfalls to avoid

1. ❌ Using internal yardstick functions that aren't exported (`yardstick_mean`, `get_weights`, etc.)
2. ❌ Referencing `@template` tags that don't exist in your package
3. ❌ Using `metric_range()`, `metric_optimal()`, `metric_direction()` in docs (not exported)
4. ❌ Assuming yardstick test helpers like `data_altman()` are available
5. ❌ Forgetting to handle hardhat weight classes (convert with `as.double()`)
6. ❌ Not validating inputs with `check_*_metric()` functions
7. ❌ Not validating `na_rm` parameter explicitly
8. ❌ Creating package in wrong directory or forgetting to check DESCRIPTION exists
9. ❌ Using `UseMethod()` after calling `new_*_metric()` (do it before)
10. ❌ Forgetting to export the data frame method with `@export`
11. ❌ Adding autoplot to single-value metrics (only for curves/matrices)
12. ❌ Forgetting to add ggplot2 as a dependency when implementing autoplot
13. ❌ Not using `ggplot2::` prefix for ggplot2 functions in autoplot methods
14. ❌ Trying to reuse yardstick's internal plotting code (build your own with ggplot2)

## Pre-flight checklist

Before creating a metric, verify:
- [ ] DESCRIPTION file exists (if not, run package initialization)
- [ ] yardstick, rlang, cli are in Imports section
- [ ] testthat is configured (tests/testthat/ directory exists)
- [ ] R/ directory exists
- [ ] You know which type of metric (numeric/class/prob)
- [ ] You have the formula/calculation method clearly defined
- [ ] You understand how to handle the specific metric type's requirements
- [ ] You've decided if autoplot is appropriate (curves/matrices only)

## Troubleshooting

### "Cannot find function 'yardstick_mean'"
- **Cause**: Using internal function that's not exported
- **Fix**: Use `weighted.mean()` from base R instead

### "Cannot find template 'return'"
- **Cause**: Using `@template return` which doesn't exist in your package
- **Fix**: Use explicit `@return` documentation from templates above

### "metric_range is not an exported object"
- **Cause**: Using internal function in roxygen dynamic code
- **Fix**: Write static documentation, don't use `metric_range()`, etc.

### "No applicable method for metric_name"
- **Cause**: Calling `UseMethod()` after `new_*_metric()`
- **Fix**: Call `UseMethod()` first, then `new_*_metric()`, then define `.data.frame` method

### Tests fail with "object 'data_altman' not found"
- **Cause**: Using yardstick internal test data
- **Fix**: Create simple test data inline (see Testing section)

## Best practices

### Code style
- Use base pipe `|>` not `%>%`
- Use `\() ...` for single-line anonymous functions
- Use `function() {...}` for multi-line functions
- Keep tests minimal with few comments

### Documentation
- Wrap roxygen at 80 characters
- Use US English and sentence case
- Reference formulas and academic sources when available
- Include practical examples
- Don't use dynamic roxygen code with non-exported functions

### Performance

Writing efficient metric code ensures your metrics work well with large datasets and in repeated evaluations (like cross-validation).

#### Vectorization over loops

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
- Comparisons: `==`, `!=`, `>`, `<`
- Logical: `&`, `|`, `!`
- Math: `abs()`, `sqrt()`, `log()`, `exp()`
- Aggregations: `sum()`, `mean()`, `max()`, `min()`

#### Use matrix operations for multiclass

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
actual_totals <- rowSums(confusion_matrix)

# Avoid
class_totals <- apply(confusion_matrix, 2, sum)  # Slower
```

#### Cache confusion matrix calculations

**Don't recalculate the same thing:**

```r
# Good: calculate once, reuse
miss_rate_impl <- function(truth, estimate, estimator, event_level, case_weights) {
  # Calculate confusion matrix once
  xtab <- yardstick::yardstick_table(truth, estimate, case_weights = case_weights)

  # Use it multiple times
  miss_rate_estimator_impl(xtab, estimator, event_level)
}

# Bad: calculate multiple times
miss_rate_impl <- function(truth, estimate, estimator, event_level, case_weights) {
  # Calculating table in each helper call
  binary_result <- miss_rate_binary(truth, estimate, event_level, case_weights)
  # ...
}
```

#### Apply weighting once, at the end

**For multiclass averaging, weight the final results:**

```r
# Good: calculate per-class, then weight
per_class_values <- compute_per_class_metric(confusion_matrix)

weights <- if (estimator == "macro") {
  rep(1, length(per_class_values))
} else {
  colSums(confusion_matrix)  # Frequency weighting
}

weighted.mean(per_class_values, weights)

# Bad: applying weights multiple times in intermediate steps
# (More complex, harder to reason about, potentially buggy)
```

#### Avoid repeated validations

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

#### Pre-compute constant values

**Calculate invariants outside loops or repeated operations:**

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

#### Avoid unnecessary data copies

**Use views/references when possible:**

```r
# Good: work with vectors directly
mean((truth - estimate)^2)

# Avoid: creating intermediate data frames unnecessarily
df_temp <- data.frame(truth = truth, estimate = estimate)
mean((df_temp$truth - df_temp$estimate)^2)
```

#### Handle case weights efficiently

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

#### Profile before optimizing

**Focus optimization where it matters:**

1. Start with clear, correct code
2. Profile with `profvis::profvis()` if performance is an issue
3. Optimize the actual bottlenecks
4. Don't prematurely optimize

```r
# Profile your metric
profvis::profvis({
  for (i in 1:100) {
    metric_name_vec(truth, estimate)
  }
})
```

Most metrics are fast enough without optimization. Focus on correctness first.

#### When performance doesn't matter

**Don't optimize unnecessarily:**
- Metrics are typically called once or a few times per model evaluation
- The metric calculation is usually fast compared to model fitting
- Readability and correctness are more important than micro-optimizations

**Do optimize when:**
- Your metric will be called thousands of times (hyperparameter tuning, cross-validation)
- You're working with very large datasets (millions of observations)
- Profiling shows your metric is the bottleneck

### Error messages
- Use `cli::cli_abort()` for errors
- Use `cli::cli_warn()` for warnings
- Include argument names in braces: `{.arg truth}`
- Include code in braces: `{.code binary}`

## References

- [Custom performance metrics tutorial](https://www.tidymodels.org/learn/develop/metrics/)
- [Yardstick reference](https://yardstick.tidymodels.org/reference/)
- [Multiclass metrics vignette](https://yardstick.tidymodels.org/articles/multiclass.html)
- Source examples: look at yardstick source on GitHub (but remember many helpers are internal)
