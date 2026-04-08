# Creating Class Metrics

Class metrics are more complex than numeric metrics due to multiclass support
and the need to handle different averaging strategies.

## Overview

Class metrics are used for classification problems where predictions and truth
are categorical (factor) variables. Examples include:

- Accuracy

- Precision / Recall / Sensitivity / Specificity

- F1 Score / F-measure

- Matthews Correlation Coefficient (MCC)

**Canonical implementations in yardstick:**

- Simple binary metrics: `R/class-accuracy.R`, `R/class-precision.R`,
  `R/class-recall.R`

- F-measure family: `R/class-f_meas.R` (combines precision and recall)

- Balanced metrics: `R/class-bal_accuracy.R` (handles class imbalance)

- Complex metrics: `R/class-mcc.R` (Matthews Correlation Coefficient)

**Test patterns:**

- Binary classification: `tests/testthat/test-class-accuracy.R`

- Multiclass averaging: `tests/testthat/test-class-f_meas.R`

## Implementation Steps

### Step 1: Binary implementation

Start with the binary case - this is the foundation.

**Reference implementations:**

- Simple confusion matrix metrics: `R/class-accuracy.R`, `R/class-precision.R`

- Metrics with event_level handling: `R/class-recall.R`, `R/class-f_meas.R`

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

**Key points:**

- Take confusion matrix and event_level as inputs

- Use `event_level` to determine which class is "positive"

- Extract TP, FP, FN, TN from the matrix

- Return single numeric value

### Step 2: Multiclass implementation (optional)

If your metric extends to multiclass.

**Reference implementations with averaging:**

- Macro/micro averaging: `R/class-precision.R`, `R/class-recall.R`

- Balanced accuracy: `R/class-bal_accuracy.R` (handles imbalanced classes)

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

> **Source Development:** When contributing to yardstick itself, you can use
> `finalize_estimator_internal()` to handle estimator selection and validation.
> This internal helper manages binary, macro, micro, and macro_weighted
> estimators automatically. See [Best Practices
> (Source)](best-practices-source.md). \`\`\`

**Estimator types:**

- **macro**: Calculate per-class, average with equal weights

- **macro_weighted**: Calculate per-class, average weighted by class frequency

- **micro**: Aggregate first, then calculate (treats all observations equally)

### Step 3: Estimator implementation

Combine binary and multiclass with weighting:

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

**Pattern:**

- Binary: use binary implementation

- Multiclass: calculate per-class, then apply weighting strategy

- Main impl function creates confusion matrix once, passes to estimator function

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

**Required elements:**

- Validate `na_rm` parameter

- Use `abort_if_class_pred()` and `as_factor_from_class_pred()` for class_pred
  handling

- Call `finalize_estimator()` to determine appropriate estimator

- Use `check_class_metric()` for validation

- Handle NAs with `yardstick_remove_missing()`

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

**Key points:**

- Use `new_class_metric()` instead of `new_numeric_metric()`

- Use `class_metric_summarizer()` instead of `numeric_metric_summarizer()`

- Include `estimator` and `event_level` parameters

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

## Factor Level Ordering

Factor levels critically affect how classification metrics are calculated.
Understanding this helps avoid confusion and errors.

### How factor levels determine the confusion matrix

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

### Binary classification: which level is "positive"?

For binary metrics, the "positive" class depends on **both** factor order and
`event_level`:

```r
# With levels = c("yes", "no") and event_level = "first"
# "yes" is treated as the positive class

# With levels = c("yes", "no") and event_level = "second"
# "no" is treated as the positive class

# With levels = c("no", "yes") and event_level = "first"
# "no" is treated as the positive class
```

### Multiclass: affects per-class calculations

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

### Unused levels after filtering

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

**Best practice in your tests:** Create factors with only the levels you need:

```r
# Good: explicit levels matching the data
truth <- factor(c("A", "A", "B", "B"), levels = c("A", "B"))

# Avoid: extra levels that aren't used
truth <- factor(c("A", "A", "B", "B"), levels = c("A", "B", "C"))
```

### Ensuring consistent levels

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

## Event Level Mechanics

For binary classification, `event_level` specifies which factor level is the
"positive" class: `"first"` (default) or `"second"`.

### Why it matters

Asymmetric metrics (sensitivity, specificity, precision, recall) depend on which
class is "positive". Changing `event_level` swaps their meaning. Symmetric
metrics (accuracy, MCC) are unaffected.

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

**Best practice:** Order factor levels so the positive class is first, then use
default `event_level = "first"`.

### Implementation pattern

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

**For symmetric metrics:** Include `event_level` parameter for consistency but
don't use it.

**For asymmetric metrics:** Always include `event_level`, use it to determine
positive class, and document its effect.

### Testing event_level

```r
test_that("metric respects event_level parameter", {
  truth <- factor(c("yes", "yes", "no", "no"), levels = c("yes", "no"))
  estimate <- factor(c("yes", "no", "yes", "no"), levels = c("yes", "no"))

  result_first <- metric_vec(truth, estimate, event_level = "first")
  result_second <- metric_vec(truth, estimate, event_level = "second")

  expect_false(result_first == result_second)  # Should differ for asymmetric metrics
})
```

### Common mistakes

- Assuming alphabetical factor order (levels are explicit, not alphabetical)

- Not using `event_level` in asymmetric metric calculations

- Poor documentation of what `event_level` does

## Multiclass Averaging Strategies

### Macro averaging

Calculate metric for each class, average with equal weights:

```r
# Per-class precision: [0.8, 0.6, 0.9]
# Macro average: (0.8 + 0.6 + 0.9) / 3 = 0.77
```

**Use when:** All classes are equally important regardless of frequency.

### Macro-weighted averaging

Calculate metric for each class, weight by class frequency:

```r
# Per-class precision: [0.8, 0.6, 0.9]
# Class frequencies: [100, 50, 150]
# Weighted: (0.8*100 + 0.6*50 + 0.9*150) / 300 = 0.82
```

**Use when:** More frequent classes should have more influence on overall
metric.

### Micro averaging

Aggregate contributions across all classes, then calculate:

```r
# Sum all TP, FP, FN across classes
# Then calculate metric from aggregated values
```

**Use when:** Every prediction matters equally, regardless of class.

## Testing Class Metrics

See
[package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements)
for comprehensive testing guide.

### Key tests for class metrics

```r
test_that("binary calculations are correct", {
  truth <- factor(c("yes", "yes", "no", "no"), levels = c("yes", "no"))
  estimate <- factor(c("yes", "no", "yes", "no"), levels = c("yes", "no"))

  # TP=1, FP=1, TN=1, FN=1
  result <- your_metric_vec(truth, estimate)

  expect_equal(result, expected_value)
})

test_that("multiclass calculations are correct", {
  truth <- factor(c("A", "A", "B", "B", "C", "C"))
  estimate <- factor(c("A", "B", "B", "C", "C", "A"))

  # Test each estimator type
  expect_equal(
    your_metric_vec(truth, estimate, estimator = "macro"),
    expected_macro
  )
  expect_equal(
    your_metric_vec(truth, estimate, estimator = "macro_weighted"),
    expected_weighted
  )
  expect_equal(
    your_metric_vec(truth, estimate, estimator = "micro"),
    expected_micro
  )
})

test_that("event_level works correctly", {
  truth <- factor(c("yes", "yes", "no", "no"), levels = c("yes", "no"))
  estimate <- factor(c("yes", "no", "yes", "no"), levels = c("yes", "no"))

  first <- your_metric_vec(truth, estimate, event_level = "first")
  second <- your_metric_vec(truth, estimate, event_level = "second")

  # Should differ for asymmetric metrics
  expect_false(first == second)
})
```

## File Naming

- **Source file**: `R/class-accuracy.R` (or `R/class-your-metric.R`)

- **Test file**: `tests/testthat/test-class-accuracy.R`

Use `class-` prefix to indicate classification metrics.

## Next Steps

- Understand confusion matrices: [confusion-matrix.md](confusion-matrix.md)

- Handle case weights: [case-weights.md](case-weights.md)

- Document your metric:
  [package-roxygen-documentation.md](package-roxygen-documentation.md)

- Write tests:
  [package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements)
