# Creating Probability Metrics

Probability metrics evaluate predicted probabilities rather than hard
classifications. These metrics are used when your model outputs probability
estimates for each class.

> **Note for Source Development:** If contributing to yardstick, you can use
> internal validation and helper functions. See the [Source Development
> Guide](source-guide.md) for yardstick-specific patterns.

## Overview

Probability metrics work with continuous probability values rather than discrete
class predictions. Examples include:

- ROC AUC (Area Under the Receiver Operating Characteristic Curve)

- PR AUC (Area Under the Precision-Recall Curve)

- Brier Score

- Log Loss / Cross-Entropy

- Calibration metrics

**Canonical implementations in yardstick:**

- ROC-based metrics: `R/prob-roc_auc.R` (binary and multiclass)

- Precision-Recall: `R/prob-pr_auc.R`, `R/prob-average_precision.R`

- Probability scoring: `R/prob-brier_class.R`, `R/prob-mn_log_loss.R`
  (multinomial log loss)

**Test patterns:**

- Binary probability metrics: `tests/testthat/test-prob-roc_auc.R`

- Multiclass metrics: `tests/testthat/test-prob-mn_log_loss.R`

## Key Differences from Class Metrics

**Probability metrics:**

- Accept probability columns (`.pred_class1`, `.pred_class2`, etc.)

- Work with continuous [0, 1] probability values

- Often more informative than hard classifications

- Can assess model calibration

**Class metrics:**

- Accept factor predictions

- Work with discrete class labels

- Simpler to interpret

- Only assess discrimination

## Understanding Probability Column Structure

### Binary classification

```r
# Data has predicted probabilities for each class
df <- tibble(
  truth = factor(c("yes", "no", "yes", "no")),
  .pred_yes = c(0.9, 0.2, 0.7, 0.3),
  .pred_no = c(0.1, 0.8, 0.3, 0.7)
)
```

### Multiclass

```r
df <- tibble(
  truth = factor(c("A", "B", "C")),
  .pred_A = c(0.7, 0.1, 0.1),
  .pred_B = c(0.2, 0.8, 0.2),
  .pred_C = c(0.1, 0.1, 0.7)
)
```

**Column naming convention:** `.pred_{level}` where `{level}` matches the factor
level.

## Implementation Steps

### Step 1: Implementation function for binary case

**Reference implementations:**

- Simple probability metrics: `R/prob-brier_class.R` (Brier score)

- Curve-based metrics: `R/prob-roc_auc.R` (requires threshold calculations)

- Log-based metrics: `R/prob-mn_log_loss.R` (multinomial log loss)

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

**Key points:**

- Accept `truth` (factor), `prob_estimate` (numeric), and `event_level`

- Convert truth to binary 0/1

- Calculate metric using probability values

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

## Handling Multiple Probability Columns

For multiclass probability metrics, the `estimate` parameter can refer to
multiple columns:

```r
# User specifies probability columns with dplyr selection
roc_auc(data, truth, c(.pred_A, .pred_B, .pred_C))

# Or using tidyselect helpers
roc_auc(data, truth, starts_with(".pred_"))
```

The `prob_metric_summarizer()` handles extracting the appropriate probability
columns based on the truth factor levels.

**Your implementation receives:**

- `truth`: factor vector

- `estimate`: matrix or data frame of probabilities (for multiclass) OR numeric
  vector (for binary)

For binary metrics:

```r
# estimate is just the probability for the event level
# prob_metric_summarizer handles this for you
```

For multiclass metrics:

```r
# estimate is a matrix with columns for each class
# You need to handle the full probability distribution
```

## Multiclass Probability Metrics

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

## Estimator Behavior Differences

**For class metrics:** estimator usually defaults based on number of levels

- 2 levels → "binary"

- 3+ levels → "macro"

**For probability metrics:** estimator might behave differently

- Some metrics only support binary (like `pr_auc`)

- Some support one-vs-all multiclass (like `roc_auc`)

- Document clearly what estimators your metric supports

## Common Probability Metric Patterns

### Log loss / Cross-entropy

```r
# Binary log loss
-mean(ifelse(truth_binary == 1,
             log(prob_estimate),
             log(1 - prob_estimate)))
```

### Brier score

```r
mean((prob_estimate - truth_binary)^2)
```

### Calibration metrics

- Compare predicted probabilities to observed frequencies

- Bin predictions and calculate bias within bins

## Testing Probability Metrics

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

## Validation Considerations

### Probabilities should sum to 1

For multiclass:

- Sum across all `.pred_*` columns should be 1

- `check_prob_metric()` validates this

For binary:

- `.pred_yes + .pred_no = 1`

- May only provide one column (the other is implied)

### Probabilities should be in [0, 1]

- Values outside this range are invalid

- `check_prob_metric()` validates this

### Column names must match levels

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

## When to Use Probability vs Class Metrics

### Use probability metrics when:

- You want to assess model calibration

- You need to compare models at different thresholds

- Probability values themselves are important

- You want more nuanced performance assessment

### Use class metrics when:

- You have a fixed decision threshold

- You need simple, interpretable metrics

- Your application requires discrete predictions

- Stakeholders think in terms of correct/incorrect

## File Naming

- **Source file**: `R/prob-brier.R` (or `R/prob-your-metric.R`)

- **Test file**: `tests/testthat/test-prob-brier.R`

Use `prob-` prefix to indicate probability metrics.

## Next Steps

- Understand class metrics: [class-metrics.md](class-metrics.md)

- Document your metric:
  [package-roxygen-documentation.md](package-roxygen-documentation.md)

- Write tests:
  [package-extension-requirements.md#testing-requirements](package-extension-requirements.md#testing-requirements)
