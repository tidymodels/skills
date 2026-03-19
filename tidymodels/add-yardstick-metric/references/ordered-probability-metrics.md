# Ordered Probability Metrics

Ordered probability metrics evaluate predicted probabilities for ordered factor outcomes. These metrics are specifically designed for ordinal classification where the class levels have a natural ordering.

## Overview

**Use when:**
- Truth is an **ordered factor** (e.g., `ordered(c("low", "medium", "high"))`)
- Predictions are **probabilities** for each ordered class
- The ordering of classes matters (e.g., severity ratings, performance levels)

**Key differences from regular probability metrics:**
- Uses cumulative probabilities to respect ordering
- Penalizes predictions that are "further away" in the ordering
- No averaging types (works the same for any number of classes)

**Examples:** Ranked Probability Score (RPS)

**Reference implementation:** `R/orderedprob-ranked_prob_score.R` in yardstick repository

## Pattern: Three-Function Approach

### 1. Implementation Function

```r
# Internal calculation logic
my_metric_impl <- function(truth, estimate, case_weights = NULL) {
  # truth: ordered factor
  # estimate: matrix with columns for each class level
  # case_weights: numeric vector or NULL

  # Example: calculate cumulative probabilities
  num_class <- nlevels(truth)
  inds <- hardhat::fct_encode_one_hot(truth)
  cum_ind <- cumulative_rows(inds)  # Helper for cumulative sums
  cum_estimate <- cumulative_rows(estimate)

  case_weights <- vctrs::vec_cast(case_weights, to = double())

  # Calculate metric using cumulative probabilities
  # ... implementation details ...
}

cumulative_rows <- function(x) {
  t(apply(x, 1, cumsum))
}
```

### 2. Vector Interface

```r
#' @export
my_metric_vec <- function(truth, estimate, na_rm = TRUE, case_weights = NULL, ...) {
  # Validate na_rm parameter
  check_bool(na_rm)
  abort_if_class_pred(truth)

  # Determine estimator (typically "standard" for ordered prob metrics)
  estimator <- finalize_estimator(truth, metric_class = "my_metric")

  # Validate inputs
  check_ordered_prob_metric(truth, estimate, case_weights, estimator)

  # Handle missing values
  if (na_rm) {
    result <- yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  # Call implementation
  my_metric_impl(truth, estimate, case_weights)
}
```

### 3. Data Frame Method

```r
#' My Ordered Probability Metric
#'
#' Description of what this metric measures.
#'
#' @family class probability metrics
#' @templateVar fn my_metric
#' @template return
#'
#' @param data A data frame
#' @param truth Unquoted column with true ordered classes (ordered factor)
#' @param ... Unquoted column(s) with predicted probabilities
#' @param na_rm Remove missing values (default TRUE)
#' @param case_weights Optional case weights column
#'
#' @export
my_metric <- function(data, ...) {
  UseMethod("my_metric")
}

my_metric <- new_ordered_prob_metric(
  my_metric,
  direction = "minimize",  # or "maximize"
  range = c(0, 1)  # or c(0, Inf), etc.
)

#' @export
#' @rdname my_metric
my_metric.data.frame <- function(data, truth, ..., na_rm = TRUE,
                                 case_weights = NULL) {
  ordered_prob_metric_summarizer(
    name = "my_metric",
    fn = my_metric_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    ...,
    na_rm = na_rm,
    case_weights = !!rlang::enquo(case_weights)
  )
}
```

## Complete Example: Ranked Probability Score

The ranked probability score (RPS) is a Brier score for ordinal data that uses cumulative probabilities.

```r
# R/ranked_prob_score.R

# 1. Implementation function
ranked_prob_score_impl <- function(truth, estimate, case_weights) {
  num_class <- nlevels(truth)
  inds <- hardhat::fct_encode_one_hot(truth)
  cum_ind <- cumulative_rows(inds)
  cum_estimate <- cumulative_rows(estimate)

  case_weights <- vctrs::vec_cast(case_weights, to = double())

  # RPS divides by number of classes minus one
  brier_ind(cum_ind, cum_estimate, case_weights) / (num_class - 1) * 2
}

cumulative_rows <- function(x) {
  t(apply(x, 1, cumsum))
}

# 2. Vector interface
#' @export
ranked_prob_score_vec <- function(truth, estimate, na_rm = TRUE,
                                   case_weights = NULL, ...) {
  check_bool(na_rm)
  abort_if_class_pred(truth)

  estimator <- finalize_estimator(truth, metric_class = "ranked_prob_score")
  check_ordered_prob_metric(truth, estimate, case_weights, estimator)

  if (na_rm) {
    result <- yardstick_remove_missing(truth, estimate, case_weights)
    truth <- result$truth
    estimate <- result$estimate
    case_weights <- result$case_weights
  } else if (yardstick_any_missing(truth, estimate, case_weights)) {
    return(NA_real_)
  }

  ranked_prob_score_impl(truth, estimate, case_weights)
}

# 3. Data frame method
#' @export
ranked_prob_score <- function(data, ...) {
  UseMethod("ranked_prob_score")
}

ranked_prob_score <- new_ordered_prob_metric(
  ranked_prob_score,
  direction = "minimize",
  range = c(0, 1)
)

#' @export
#' @rdname ranked_prob_score
ranked_prob_score.data.frame <- function(data, truth, ..., na_rm = TRUE,
                                         case_weights = NULL) {
  ordered_prob_metric_summarizer(
    name = "ranked_prob_score",
    fn = ranked_prob_score_vec,
    data = data,
    truth = !!enquo(truth),
    ...,
    na_rm = na_rm,
    case_weights = !!enquo(case_weights)
  )
}
```

## Key Validation Function

```r
check_ordered_prob_metric(truth, estimate, case_weights, estimator)
```

This validates:
- `truth` is an ordered factor
- `estimate` is a matrix with correct dimensions
- `case_weights` are valid (if provided)
- Estimator type is appropriate

## Input Format

### Truth

```r
# Must be an ordered factor
truth <- ordered(c("low", "medium", "high", "low"))
```

### Estimate

```r
# Matrix with probabilities for each level (columns match levels)
# Rows correspond to observations, columns to ordered levels
estimate <- matrix(
  c(0.7, 0.2, 0.1,    # First observation
    0.1, 0.6, 0.3),   # Second observation
  nrow = 2,
  byrow = TRUE
)
```

## Cumulative Probabilities

Ordered probability metrics typically use cumulative probabilities:

```r
# Original probabilities
probs <- c(0.2, 0.5, 0.3)  # P(class=1), P(class=2), P(class=3)

# Cumulative probabilities
cum_probs <- cumsum(probs)  # 0.2, 0.7, 1.0
# P(class <= 1), P(class <= 2), P(class <= 3)
```

This respects the ordering: being one class away is better than being two classes away.

## Testing

```r
# tests/testthat/test-my_metric.R

test_that("my_metric works with ordered factors", {
  df <- data.frame(
    truth = ordered(c("low", "medium", "high")),
    low = c(0.8, 0.1, 0.05),
    medium = c(0.15, 0.8, 0.15),
    high = c(0.05, 0.1, 0.8)
  )

  result <- my_metric(df, truth, low:high)

  expect_equal(result$.metric, "my_metric")
  expect_equal(result$.estimator, "standard")
  expect_true(is.numeric(result$.estimate))
})

test_that("my_metric validates ordered factor", {
  df <- data.frame(
    truth = factor(c("a", "b", "c")),  # NOT ordered
    a = c(0.8, 0.1, 0.1),
    b = c(0.1, 0.8, 0.1),
    c = c(0.1, 0.1, 0.8)
  )

  expect_error(my_metric(df, truth, a:c))
})

test_that("my_metric handles case weights", {
  df <- data.frame(
    truth = ordered(c("low", "medium", "high")),
    low = c(0.8, 0.1, 0.05),
    medium = c(0.15, 0.8, 0.15),
    high = c(0.05, 0.1, 0.8),
    weights = c(1, 2, 1)
  )

  result_weighted <- my_metric(df, truth, low:high, case_weights = weights)
  result_unweighted <- my_metric(df, truth, low:high)

  # Weighted should differ from unweighted
  expect_false(result_weighted$.estimate == result_unweighted$.estimate)
})
```

## Common Patterns

### Helper for Cumulative Rows

```r
cumulative_rows <- function(x) {
  t(apply(x, 1, cumsum))
}
```

### Converting Ordered Factor to Indicators

```r
# One-hot encoding
inds <- hardhat::fct_encode_one_hot(truth)

# Then cumulative sum
cum_ind <- cumulative_rows(inds)
```

## Key Differences from Regular Probability Metrics

| Aspect | Regular Probability | Ordered Probability |
|--------|---------------------|---------------------|
| Truth type | Factor | Ordered factor |
| Calculation | Uses raw probabilities | Uses cumulative probabilities |
| Class ordering | Not considered | Explicitly used |
| Averaging | Macro/micro/weighted | No averaging (standard only) |
| Use case | Nominal classification | Ordinal classification |

## Best Practices

1. **Always validate ordered factor**: Use `check_ordered_prob_metric()` to ensure truth is ordered
2. **Use cumulative probabilities**: This respects the ordering of classes
3. **Handle case weights consistently**: Convert to numeric with `vctrs::vec_cast()`
4. **No averaging types**: Ordered metrics work the same regardless of class count
5. **Document ordering assumptions**: Make clear that class order matters

## See Also

- [Probability Metrics](probability-metrics.md) - Regular (nominal) probability metrics
- [Metric System](metric-system.md) - Understanding metric architecture
- [Testing Patterns](../testing-patterns.md) - Comprehensive test guide
