# Working with Confusion Matrices

Understanding how to work with confusion matrices is essential for implementing classification metrics in yardstick.

> **Note for Source Development:** If you're contributing directly to the yardstick package, you can use internal confusion matrix utilities. See the [Source Development Guide](source-guide.md) for details.

## Overview

Confusion matrices are the foundation for classification metrics. The `yardstick_table()` function creates weighted confusion matrices that all classification metrics use.

**Implementation:**
- Confusion matrix creation: `R/table.R` (implements `yardstick_table()`)
- Matrix extraction: Used by all class metrics in `R/class-*.R`

**Usage examples in metrics:**
- Binary metrics: `R/class-accuracy.R`, `R/class-precision.R` (extract TP/FP/TN/FN)
- Multiclass metrics: `R/class-f_meas.R` (per-class calculations)
- Balanced metrics: `R/class-bal_accuracy.R` (uses diagonals and marginals)

**Test patterns:**
- Table creation tests: `tests/testthat/test-table.R`
- Weight handling: `tests/testthat/test-class-accuracy.R` (validates weighted confusion matrices)

## Creating Confusion Matrices

Use `yardstick_table()` to create weighted confusion matrices:

```r
xtab <- yardstick::yardstick_table(truth, estimate, case_weights = case_weights)
```

## What yardstick_table Returns

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

## How Case Weights are Incorporated

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

## Accessing Elements Correctly

**Critical:** Use character names, not integer indices:

```r
# Good: use level names
tp <- xtab["yes", "yes"]
fp <- xtab["no", "yes"]

# Bad: numeric indices can be confusing
tp <- xtab[1, 1]  # Which level is row 1?
```

### Pattern for binary metrics

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
- Format: `xtab[truth_value, predicted_value]`

## Confusion Matrix for Multiclass

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

### Extracting per-class metrics

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

### Efficient multiclass patterns

Use vectorized operations:

```r
# Good: matrix operations
tp <- diag(xtab)
fp <- colSums(xtab) - tp
fn <- rowSums(xtab) - tp

# Calculate per-class precision
precision <- tp / (tp + fp)

# Calculate per-class recall
recall <- tp / (tp + fn)
```

## Common Mistakes with Table Indexing

### Mistake 1: Row/column confusion

```r
# Correct understanding:
tp <- xtab[event, event]  # actual event, predicted event

# Wrong interpretation:
# Thinking columns are truth - THEY ARE NOT
# Rows = actual truth, Columns = predictions
```

Remember: `xtab[truth_value, predicted_value]`

### Mistake 2: Assuming numeric indices

```r
# Fragile: depends on factor level order
tp <- xtab[1, 1]
fp <- xtab[2, 1]

# Robust: uses level names
tp <- xtab[event, event]
fp <- xtab[control, event]
```

### Mistake 3: Not handling zero counts

```r
# When a cell is zero, it's still numeric
fp <- xtab[control, event]  # Could be 0

# Don't need special handling for zeros
sensitivity <- tp / (tp + fn)  # Works even if fn = 0 (gives Inf or NaN)
```

Zero counts are valid and operations handle them correctly (may result in `Inf` or `NaN` which is expected).

## Factor Level Ordering and the Table

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

## Multiclass Averaging

Three types of averaging for multiclass metrics:

### Macro averaging

Unweighted average across classes (equal weight for each class):

```r
# Calculate per-class metric
per_class_precision <- tp / (tp + fp)

# Macro average: equal weight
wt <- rep(1, n_classes)
macro_precision <- weighted.mean(per_class_precision, wt)
# Or simply: mean(per_class_precision)
```

### Macro-weighted averaging

Weighted by class frequency in truth:

```r
# Calculate per-class metric
per_class_precision <- tp / (tp + fp)

# Macro-weighted: weight by class frequency
class_counts <- colSums(xtab)  # or rowSums, they should be equal for balanced data
macro_weighted_precision <- weighted.mean(per_class_precision, class_counts)
```

### Micro averaging

Pool all classes, calculate once:

```r
# Aggregate first
total_tp <- sum(tp)
total_fp <- sum(fp)

# Then calculate
micro_precision <- total_tp / (total_tp + total_fp)
```

## Performance Tips

### Cache confusion matrix calculations

Don't recalculate the confusion matrix multiple times:

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

### Use matrix operations

```r
# Good: vectorized operations
tp <- diag(xtab)
fp <- colSums(xtab) - tp
fn <- rowSums(xtab) - tp

# Avoid: looping
tp <- numeric(n_classes)
for (i in seq_len(n_classes)) {
  tp[i] <- xtab[i, i]
}
```

## Testing with Confusion Matrices

When testing, create simple, explicit test data:

```r
test_that("confusion matrix indexing works correctly", {
  truth <- factor(c("yes", "yes", "no", "no"), levels = c("yes", "no"))
  estimate <- factor(c("yes", "no", "yes", "no"), levels = c("yes", "no"))

  xtab <- yardstick_table(truth, estimate)

  # Verify structure
  expect_equal(xtab["yes", "yes"], 1)  # TP
  expect_equal(xtab["no", "yes"], 1)   # FP
  expect_equal(xtab["yes", "no"], 1)   # FN
  expect_equal(xtab["no", "no"], 1)    # TN
})
```

## Next Steps

- Implement class metrics: [class-metrics.md](class-metrics.md)
- Handle case weights: [case-weights.md](case-weights.md)
- Understand the metric system: [metric-system.md](metric-system.md)
