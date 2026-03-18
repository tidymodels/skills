# Quantile Metrics

Quantile metrics evaluate quantile predictions (probabilistic forecasts represented as quantiles) against observed numeric values. These metrics assess the quality of uncertainty quantification.

## Overview

**Use when:**
- Truth is **numeric** (observed values)
- Predictions are **quantile predictions** (`hardhat::quantile_pred` objects)
- You want to evaluate probabilistic forecasts represented as quantiles

**Key characteristics:**
- Works with quantile-based distributional predictions
- Handles missing quantiles (implicit or explicit)
- Supports imputation of missing quantiles
- Returns `.estimator = "standard"`

**Examples:** Weighted Interval Score (WIS), Pinball Loss

**Reference implementation:** `R/quant-weighted_interval_score.R` in yardstick repository

## Pattern: Three-Function Approach

### 1. Implementation Function

```r
# Internal calculation logic
my_metric_impl <- function(truth, estimate, quantile_levels, rowwise_na_rm = TRUE) {
  # truth: numeric vector
  # estimate: matrix of quantile predictions (rows = obs, cols = quantiles)
  # quantile_levels: vector of probability levels
  # rowwise_na_rm: whether to drop NAs within each row

  # Calculate metric for each observation
  res <- mapply(
    FUN = function(.x, .y) {
      my_metric_one_quantile(.x, quantile_levels, .y, rowwise_na_rm)
    },
    vctrs::vec_chop(estimate),
    truth
  )

  as.vector(res, "double")
}

# Helper: Calculate metric for one observation
my_metric_one_quantile <- function(values, quantile_levels, truth, na_rm) {
  # values: vector of quantile predictions for one observation
  # quantile_levels: corresponding probability levels
  # truth: single observed value
  # na_rm: whether to remove NAs

  # Calculate metric (e.g., pinball loss, interval score)
  # ...
}
```

### 2. Vector Interface

```r
#' @export
my_metric_vec <- function(truth, estimate, quantile_levels = NULL, na_rm = FALSE,
                          quantile_estimate_nas = c("impute", "drop", "propagate"),
                          case_weights = NULL, ...) {
  # Validate na_rm parameter
  check_bool(na_rm)

  # Validate inputs
  check_quantile_metric(truth, estimate, case_weights)

  # Get quantile levels from estimate
  estimate_quantile_levels <- hardhat::extract_quantile_levels(estimate)
  quantile_estimate_nas <- rlang::arg_match(quantile_estimate_nas)

  # Handle quantile_levels parameter
  if (!is.null(quantile_levels)) {
    hardhat::check_quantile_levels(quantile_levels)
    all_levels_estimated <- all(quantile_levels %in% estimate_quantile_levels)

    if (quantile_estimate_nas == "drop" && !all_levels_estimated) {
      cli::cli_abort(
        "When `quantile_levels` is not a subset of those available in `estimate`,
        `quantile_estimate_nas` may not be `'drop'`."
      )
    }
    if (!all_levels_estimated && (quantile_estimate_nas == "propagate")) {
      return(NA_real_)
    }
  }

  quantile_levels <- quantile_levels %||% estimate_quantile_levels

  # Handle missing quantiles
  if (quantile_estimate_nas %in% c("drop", "propagate")) {
    levels_estimated <- estimate_quantile_levels %in% quantile_levels
    estimate <- as.matrix(estimate)[, levels_estimated, drop = FALSE]
  } else {
    estimate <- as.matrix(hardhat::impute_quantiles(estimate, quantile_levels))
  }

  # Calculate metric per observation
  vec_metric <- my_metric_impl(
    truth = truth,
    estimate = estimate,
    quantile_levels = quantile_levels,
    rowwise_na_rm = (quantile_estimate_nas == "drop")
  )

  # Handle overall missing values
  if (na_rm) {
    result <- yardstick_remove_missing(truth, vec_metric, case_weights)
    truth <- result$truth
    vec_metric <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick_any_missing(truth, vec_metric, case_weights)) {
    return(NA_real_)
  }

  # Average across observations
  yardstick_mean(vec_metric, case_weights = case_weights)
}
```

### 3. Data Frame Method

```r
#' My Quantile Metric
#'
#' Description of what this metric measures.
#'
#' @family quantile metrics
#' @templateVar fn my_metric
#' @template return
#'
#' @param data A data frame
#' @param truth Unquoted column with true numeric values
#' @param estimate Unquoted column with quantile predictions
#' @param quantile_levels Optional specific quantile levels to evaluate
#' @param na_rm Remove missing values (default FALSE)
#' @param quantile_estimate_nas How to handle missing quantiles ("impute", "drop", "propagate")
#' @param case_weights Optional case weights column
#' @param ... Not currently used
#'
#' @export
my_metric <- function(data, ...) {
  UseMethod("my_metric")
}

my_metric <- new_quantile_metric(
  my_metric,
  direction = "minimize",  # or "maximize"
  range = c(0, Inf)  # or other appropriate range
)

#' @export
#' @rdname my_metric
my_metric.data.frame <- function(data, truth, estimate, quantile_levels = NULL,
                                 na_rm = TRUE, quantile_estimate_nas = c("impute", "drop", "propagate"),
                                 case_weights = NULL, ...) {
  quantile_metric_summarizer(
    name = "my_metric",
    fn = my_metric_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights),
    fn_options = list(
      quantile_levels = quantile_levels,
      quantile_estimate_nas = quantile_estimate_nas
    )
  )
}
```

## Complete Example: Weighted Interval Score

The weighted interval score (WIS) is a quantile-based approximation of the continuous ranked probability score (CRPS).

```r
# R/weighted_interval_score.R

# 1. Helper: Calculate WIS for one observation
wis_one_quantile <- function(values, quantile_levels, truth, na_rm) {
  # Pinball loss for each quantile
  res <- pmax(
    quantile_levels * (truth - values),
    (1 - quantile_levels) * (values - truth)
  )

  2 * mean(res, na.rm = na_rm)
}

# 2. Implementation function
wis_impl <- function(truth, estimate, quantile_levels, rowwise_na_rm = TRUE) {
  res <- mapply(
    FUN = function(.x, .y) {
      wis_one_quantile(.x, quantile_levels, .y, rowwise_na_rm)
    },
    vctrs::vec_chop(estimate),
    truth
  )

  as.vector(res, "double")
}

# 3. Vector interface
#' @export
weighted_interval_score_vec <- function(truth, estimate, quantile_levels = NULL,
                                        na_rm = FALSE,
                                        quantile_estimate_nas = c("impute", "drop", "propagate"),
                                        case_weights = NULL, ...) {
  check_bool(na_rm)
  check_quantile_metric(truth, estimate, case_weights)

  estimate_quantile_levels <- hardhat::extract_quantile_levels(estimate)
  quantile_estimate_nas <- rlang::arg_match(quantile_estimate_nas)

  if (!is.null(quantile_levels)) {
    hardhat::check_quantile_levels(quantile_levels)
    all_levels_estimated <- all(quantile_levels %in% estimate_quantile_levels)

    if (quantile_estimate_nas == "drop" && !all_levels_estimated) {
      cli::cli_abort(
        "When `quantile_levels` is not a subset of those available in `estimate`,
        `quantile_estimate_nas` may not be `'drop'`."
      )
    }
    if (!all_levels_estimated && (quantile_estimate_nas == "propagate")) {
      return(NA_real_)
    }
  }

  quantile_levels <- quantile_levels %||% estimate_quantile_levels

  if (quantile_estimate_nas %in% c("drop", "propagate")) {
    levels_estimated <- estimate_quantile_levels %in% quantile_levels
    estimate <- as.matrix(estimate)[, levels_estimated, drop = FALSE]
  } else {
    estimate <- as.matrix(hardhat::impute_quantiles(estimate, quantile_levels))
  }

  vec_wis <- wis_impl(
    truth = truth,
    estimate = estimate,
    quantile_levels = quantile_levels,
    rowwise_na_rm = (quantile_estimate_nas == "drop")
  )

  if (na_rm) {
    result <- yardstick_remove_missing(truth, vec_wis, case_weights)
    truth <- result$truth
    vec_wis <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick_any_missing(truth, vec_wis, case_weights)) {
    return(NA_real_)
  }

  yardstick_mean(vec_wis, case_weights = case_weights)
}

# 4. Data frame method
#' @export
weighted_interval_score <- function(data, ...) {
  UseMethod("weighted_interval_score")
}

weighted_interval_score <- new_quantile_metric(
  weighted_interval_score,
  direction = "minimize",
  range = c(0, Inf)
)

#' @export
#' @rdname weighted_interval_score
weighted_interval_score.data.frame <- function(data, truth, estimate,
                                               quantile_levels = NULL, na_rm = TRUE,
                                               quantile_estimate_nas = c("impute", "drop", "propagate"),
                                               case_weights = NULL, ...) {
  quantile_metric_summarizer(
    name = "weighted_interval_score",
    fn = weighted_interval_score_vec,
    data = data,
    truth = !!enquo(truth),
    estimate = !!enquo(estimate),
    na_rm = na_rm,
    case_weights = !!enquo(case_weights),
    fn_options = list(
      quantile_levels = quantile_levels,
      quantile_estimate_nas = quantile_estimate_nas
    )
  )
}
```

## Key Validation Function

```r
check_quantile_metric(truth, estimate, case_weights)
```

This validates:
- `truth` is a numeric vector
- `estimate` is a `hardhat::quantile_pred` object
- Lengths match
- `case_weights` are valid (if provided)

## Input Format

### Truth: Numeric Vector

```r
# Observed values
truth <- c(3.3, 7.1, 5.5, 2.8)
```

### Estimate: Quantile Predictions

```r
library(hardhat)

# Create quantile predictions
quantile_levels <- c(0.1, 0.25, 0.5, 0.75, 0.9)

# Predictions for first observation
pred1 <- c(2.0, 2.5, 3.0, 3.5, 4.0)

# Predictions for second observation
pred2 <- c(6.0, 6.5, 7.0, 7.5, 8.0)

# Combine into quantile_pred object
preds <- quantile_pred(
  rbind(pred1, pred2),
  quantile_levels
)
```

## Understanding Quantile Predictions

Quantile predictions represent uncertainty:

```r
# Example: 90% prediction interval
# 0.05 quantile: lower bound
# 0.95 quantile: upper bound

quantile_pred(
  matrix(c(1.5, 5.5), nrow = 1),  # Predictions
  c(0.05, 0.95)                    # Quantile levels
)
# Predicts value will be between 1.5 and 5.5 with 90% probability
```

## Handling Missing Quantiles

Three strategies for missing quantile values:

### 1. Impute (`quantile_estimate_nas = "impute"`)

```r
# Impute missing quantiles using linear interpolation
estimate <- hardhat::impute_quantiles(estimate, desired_quantiles)
```

Use when:
- You need specific quantile levels that weren't predicted
- Interpolation is reasonable for your data

### 2. Drop (`quantile_estimate_nas = "drop"`)

```r
# Remove NAs within each observation
# Only works if quantile_levels is subset of available levels
```

Use when:
- Some quantiles are explicitly NA
- You want to average over available quantiles only

### 3. Propagate (`quantile_estimate_nas = "propagate"`)

```r
# Any missing quantile → entire observation gets NA score
# If na_rm = TRUE, that observation is excluded
```

Use when:
- Missing quantiles indicate prediction failure
- You want to be conservative

## Testing

```r
# tests/testthat/test-weighted_interval_score.R

test_that("weighted_interval_score works correctly", {
  library(hardhat)

  quantile_levels <- c(0.2, 0.4, 0.6, 0.8)
  pred1 <- 1:4
  pred2 <- 8:11
  preds <- quantile_pred(rbind(pred1, pred2), quantile_levels)
  truth <- c(3.3, 7.1)

  result_vec <- weighted_interval_score_vec(truth, preds)
  expect_true(is.numeric(result_vec))
  expect_true(result_vec >= 0)

  # Data frame interface
  df <- data.frame(truth = truth)
  df$preds <- preds

  result_df <- weighted_interval_score(df, truth, preds)
  expect_equal(result_df$.metric, "weighted_interval_score")
  expect_equal(result_df$.estimate, result_vec)
})

test_that("weighted_interval_score handles missing quantiles", {
  library(hardhat)

  preds_na <- quantile_pred(
    rbind(c(1, 2, NA, 4), c(5, 6, 7, 8)),
    c(0.2, 0.4, 0.6, 0.8)
  )
  truth <- c(2.5, 6.5)

  # Impute by default
  result_impute <- weighted_interval_score_vec(truth, preds_na)
  expect_false(is.na(result_impute))

  # Propagate NAs
  result_propagate <- weighted_interval_score_vec(
    truth, preds_na,
    quantile_estimate_nas = "propagate"
  )
  expect_true(is.na(result_propagate))

  # Drop NAs (only works for subset)
  result_drop <- weighted_interval_score_vec(
    truth, preds_na,
    quantile_levels = c(0.2, 0.4, 0.8),
    quantile_estimate_nas = "drop"
  )
  expect_false(is.na(result_drop))
})

test_that("weighted_interval_score with specific quantile_levels", {
  library(hardhat)

  preds <- quantile_pred(
    rbind(1:5, 6:10),
    c(0.1, 0.25, 0.5, 0.75, 0.9)
  )
  truth <- c(3.0, 7.5)

  # Request different quantile levels
  result <- weighted_interval_score_vec(
    truth, preds,
    quantile_levels = c(0.25, 0.5, 0.75)
  )
  expect_true(is.numeric(result))
})

test_that("weighted_interval_score works with case weights", {
  library(hardhat)

  preds <- quantile_pred(rbind(1:4, 8:11), c(0.2, 0.4, 0.6, 0.8))
  truth <- c(3.3, 7.1)
  weights <- c(1, 2)

  df <- data.frame(truth = truth, weights = weights)
  df$preds <- preds

  result <- weighted_interval_score(df, truth, preds, case_weights = weights)
  expect_true(is.numeric(result$.estimate))
})
```

## Common Patterns

### Creating Quantile Predictions

```r
library(hardhat)

# Matrix: rows = observations, columns = quantiles
pred_matrix <- matrix(
  c(1, 2, 3, 4, 5,    # Observation 1
    6, 7, 8, 9, 10),  # Observation 2
  nrow = 2,
  byrow = TRUE
)

quantile_levels <- c(0.1, 0.25, 0.5, 0.75, 0.9)

preds <- quantile_pred(pred_matrix, quantile_levels)
```

### Extracting Quantile Levels

```r
# Get quantile levels from predictions
levels <- hardhat::extract_quantile_levels(estimate)
```

### Averaging with Case Weights

```r
# Use yardstick helper (internal but used in vec function)
yardstick_mean(vec_metric, case_weights = case_weights)
```

### Per-Observation Calculations

```r
# Process each observation separately
res <- mapply(
  FUN = function(.x, .y) {
    calculate_for_one(.x, .y)
  },
  vctrs::vec_chop(estimate),  # Split estimate by rows
  truth                        # Truth values
)

as.vector(res, "double")
```

## Key Differences from Other Metric Types

| Aspect | Quantile | Numeric | Probability |
|--------|----------|---------|-------------|
| Truth type | Numeric | Numeric | Factor |
| Estimate type | quantile_pred | Numeric | Probabilities |
| Purpose | Uncertainty quantification | Point prediction | Classification |
| Output | Distributional accuracy | Point accuracy | Class accuracy |

## Statistical Background

### Pinball Loss (Quantile Loss)

For quantile level τ and prediction q:
```
L(y, q, τ) = (τ - 1) * (y - q)  if y < q
L(y, q, τ) = τ * (y - q)        if y ≥ q
```

Or equivalently:
```
L(y, q, τ) = max(τ * (y - q), (1 - τ) * (q - y))
```

### Weighted Interval Score

WIS is essentially the average pinball loss across quantiles:
```
WIS = 2 * mean(pinball_losses)
```

The factor of 2 scales it to match interval-based scoring.

## Best Practices

1. **Use appropriate quantile levels**: Include median (0.5) and symmetric intervals (e.g., 0.1/0.9, 0.25/0.75)
2. **Handle missing quantiles carefully**: Choose strategy based on your use case
3. **Validate quantile_pred objects**: Use `check_quantile_metric()`
4. **Document quantile strategy**: Explain how missing quantiles are handled
5. **Consider calibration**: Quantiles should be calibrated (e.g., 90% interval contains 90% of values)
6. **Use fn_options**: Pass extra parameters via `fn_options` in summarizer
7. **Test edge cases**: Missing quantiles, single quantile, all NAs

## Common Metrics

- **Weighted Interval Score (WIS)**: Quantile-based CRPS approximation
- **Pinball Loss**: Loss for single quantile level
- **Interval Score**: Score for single prediction interval
- **Quantile Coverage**: Proportion of observations within intervals

## Dependencies

Quantile metrics require the hardhat package:

```r
# In DESCRIPTION
Imports:
    hardhat,
    vctrs,
    rlang

# In R/package.R
#' @importFrom hardhat quantile_pred extract_quantile_levels impute_quantiles
```

## See Also

- [Numeric Metrics](numeric-metrics.md) - Point prediction metrics
- [Metric System](metric-system.md) - Understanding metric architecture
- [Testing Patterns](../../shared-references/testing-patterns.md) - Comprehensive test guide
