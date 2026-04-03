---
name: add-yardstick-metric
description: Guide for creating new yardstick metrics. Use when a developer needs to extend yardstick with a custom performance metric, including numeric, class, probability, ordered probability, survival (static, dynamic, integrated, linear predictor), and quantile metrics.
---

# Add Yardstick Metric

Guide for developing new metrics that extend the yardstick package. This skill provides best practices, code templates, and testing patterns for creating custom performance metrics.

---

## Two Development Contexts

This skill supports **two distinct development contexts**:

### 🆕 Extension Development (Default)
**Creating a new R package** that extends yardstick with custom metrics.

- ✅ Use this for: New packages, standalone metrics, CRAN submissions

- ⚠️ **Constraint**: Can only use exported functions (no `:::`)

### 🔧 Source Development (Advanced)
**Contributing directly to yardstick** via pull requests.

- ✅ Use this for: Contributing to tidymodels/yardstick repository

- ✨ **Benefit**: Can use internal functions and package infrastructure

---

## Getting Started

**INSTRUCTIONS FOR CLAUDE:** Run the verification script first to determine the development context:

```bash
Rscript -e 'source(Sys.glob(path.expand("~/.claude/plugins/cache/tidymodels-skills/tidymodels-dev/*/tidymodels/shared-references/scripts/verify-setup.R"))[1])'
```

**Then follow the appropriate path based on the output:**

- **Output: "All checks for source development complete."**
  → Go to [Source Development Guide](references/source-guide.md)

- **Output: "All checks for extension development complete." (no warnings)**
  → Go to [Extension Development Guide](references/extension-guide.md)

- **Output: Shows "Warning - [UUID]" messages**
  → Go to [Extension Prerequisites](references/package-extension-prerequisites.md) to resolve warnings first

---

## Overview

Creating a custom yardstick metric provides:

- Standardization with existing metrics

- Automatic error handling for types and lengths

- Support for multiclass implementations

- NA handling

- Grouped data frame support

- Integration with `metric_set()`

- Optional autoplot support for visualization (curves and confusion matrices)

## Repository Access (Optional but Recommended)

**INSTRUCTIONS FOR CLAUDE:** Check if `repos/yardstick/` exists in the current working directory. Use this to guide development:

**If `repos/yardstick/` exists:**

- ✅ Use it as a reference throughout development

- Read source files (e.g., `repos/yardstick/R/prob-brier_class.R`) to study implementation patterns

- Read test files (e.g., `repos/yardstick/tests/testthat/test-prob-roc_auc.R`) for testing patterns

- Reference these files when answering complex questions or solving problems

- Look at actual code structure, validation patterns, and edge case handling

**If `repos/yardstick/` does NOT exist:**

- Suggest cloning the repository using the scripts in [Repository Access Guide](references/package-repository-access.md)

- This is **optional but strongly recommended** for high-quality development

- If the user declines, reference files using GitHub URLs:

  - Format: `https://github.com/tidymodels/yardstick/blob/main/R/[file-name].R`

  - Example: https://github.com/tidymodels/yardstick/blob/main/R/prob-brier_class.R

  - This allows users to click through to see implementations

**When to use repository references:**

- Complex implementation questions (e.g., "How does yardstick handle multiclass averaging?")

- Debugging issues (compare user's code to working implementation)

- Understanding patterns (study similar metrics)

- Test design (see how yardstick tests edge cases)

- Architecture decisions (understand internal structure)

See [Repository Access Guide](references/package-repository-access.md) for setup instructions.

## Quick Navigation

**Development Guides:**

- [Extension Development Guide](references/extension-guide.md) - Creating new packages that extend yardstick

- [Source Development Guide](references/source-guide.md) - Contributing PRs to yardstick itself

**Reference Files:**

- [Metric System Architecture](references/metric-system.md) - How new_*_metric() works, .estimator column, design considerations

- [Combining Metrics](references/metric-set.md) - Using metric_set() to combine multiple metrics

- [Groupwise Metrics](references/groupwise-metrics.md) - Creating disparity/fairness metrics

- [Numeric Metrics](references/numeric-metrics.md) - Regression metrics (MAE, RMSE, MSE)

- [Class Metrics](references/class-metrics.md) - Classification metrics (accuracy, precision, recall)

- [Probability Metrics](references/probability-metrics.md) - Probability-based metrics (ROC AUC, log loss)

- [Ordered Probability Metrics](references/ordered-probability-metrics.md) - Ordinal classification metrics (Ranked Probability Score)

- [Static Survival Metrics](references/static-survival-metrics.md) - Overall survival metrics (Concordance Index)

- [Dynamic Survival Metrics](references/dynamic-survival-metrics.md) - Time-dependent survival metrics (Brier Survival)

- [Integrated Survival Metrics](references/integrated-survival-metrics.md) - Integrated survival metrics (Integrated Brier)

- [Linear Predictor Survival Metrics](references/linear-predictor-survival-metrics.md) - Linear predictor metrics (Royston's D)

- [Quantile Metrics](references/quantile-metrics.md) - Quantile prediction metrics (Weighted Interval Score)

- [Confusion Matrix](references/confusion-matrix.md) - Working with yardstick_table()

- [Case Weights](references/case-weights.md) - Handling weighted observations

- [Autoplot Support](references/autoplot.md) - Optional visualization (curves, confusion matrices)

**Shared References (Extension Development):**

- [Extension Prerequisites](references/package-extension-prerequisites.md) - Extension prerequisites

- [Development Workflow](references/package-development-workflow.md) - Fast iteration cycle

- [Testing Patterns (Extension)](references/package-extension-requirements.md#testing-requirements) - Extension testing guide

- [Roxygen Documentation](references/package-roxygen-documentation.md) - Documentation templates

- [Package Imports](references/package-imports.md) - Managing dependencies

- [Best Practices (Extension)](references/package-extension-requirements.md#best-practices) - Extension code style

- [Troubleshooting (Extension)](references/package-extension-requirements.md#common-issues-solutions) - Extension issues

**Source Development Specific:**

- [Testing Patterns (Source)](references/testing-patterns-source.md) - Using internal test helpers

- [Best Practices (Source)](references/best-practices-source.md) - Using internal functions

- [Troubleshooting (Source)](references/troubleshooting-source.md) - Source-specific issues

## Development Workflow

See [Development Workflow](references/package-development-workflow.md) for complete details.

**Fast iteration cycle (run repeatedly):**

1. `devtools::document()` - Generate documentation
2. `devtools::load_all()` - Load your package
3. `devtools::test()` - Run tests

**Final validation (run once at end):**

4. `devtools::check()` - Full R CMD check

**WARNING:** Do NOT run `check()` during iteration. It takes 1-2 minutes and is unnecessary until you're done.

---

## Critical: Tidymodels Code Standards

**These requirements ensure your code aligns with tidymodels patterns and passes review.**

### Source Development (PRs to yardstick)

When contributing to yardstick itself, you MUST:

**1. Use internal helpers** - Don't reimplement what exists:
```r
# ✅ CORRECT - Use internal helper
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)
  yardstick_mean(errors, case_weights = case_weights)  # Use this
}

# ❌ WRONG - Reimplementing what already exists
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)
  if (is.null(case_weights)) {
    mean(errors)
  } else {
    weighted.mean(errors, w = as.double(case_weights))
  }
}
```

Common internal helpers: `yardstick_mean()`, `finalize_estimator_internal()`, `check_*_metric()`, `yardstick_remove_missing()`, `yardstick_any_missing()`

**2. NO package prefix** - Functions are in the same package:
```r
# ✅ CORRECT - No prefix
yardstick_mean(errors, case_weights = case_weights)
check_numeric_metric(truth, estimate, case_weights)

# ❌ WRONG - Don't prefix your own package
yardstick::yardstick_mean(errors, case_weights = case_weights)
yardstick::check_numeric_metric(truth, estimate, case_weights)
```

**3. Include @examples** - Required for all exported functions:
```r
#' @examples
#' # Basic usage
#' mae(solubility_test, solubility, prediction)
#'
#' # With case weights
#' library(dplyr)
#' solubility_test %>%
#'   mutate(weight = 1:nrow(.)) %>%
#'   mae(solubility, prediction, case_weights = weight)
```

### Extension Development (new packages)

When creating packages that extend yardstick, you MUST:

**1. ALWAYS use package prefix** - Explicitly namespace all yardstick functions:
```r
# ✅ CORRECT - Always prefix
yardstick::check_numeric_metric(truth, estimate, case_weights)
yardstick::new_numeric_metric(wape, direction = "minimize")
yardstick::numeric_metric_summarizer(...)

# ❌ WRONG - Missing prefix (will fail R CMD check without imports)
check_numeric_metric(truth, estimate, case_weights)
new_numeric_metric(wape, direction = "minimize")
```

**2. NEVER use internal functions** - Cannot access `:::`:
```r
# ❌ FORBIDDEN - Extension developers cannot use :::
yardstick:::yardstick_mean(errors, case_weights)
yardstick:::finalize_estimator_internal(estimator, ...)

# ✅ CORRECT - Implement manually or use exported functions
if (!is.null(case_weights)) {
  case_weights <- as.double(case_weights)
  weighted.mean(errors, w = case_weights)
} else {
  mean(errors)
}
```

**3. Include @examples** - Required for usability:
```r
#' @examples
#' library(modeldata)
#' data(solubility_test)
#'
#' # Calculate WAPE
#' wape(solubility_test, solubility, prediction)
```

### Both Contexts: Case Weights Handling

ALWAYS convert hardhat weight objects to numeric. This is **required in all _impl functions** that accept case weights:

**Extension development example:**
```r
wape_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  # REQUIRED: Convert hardhat weight objects to numeric
  if (!is.null(case_weights)) {
    if (inherits(case_weights, c("hardhat_importance_weights",
                                 "hardhat_frequency_weights"))) {
      case_weights <- as.double(case_weights)  # ← CRITICAL
    }
    weighted.mean(errors, w = case_weights)
  } else {
    mean(errors)
  }
}
```

**Source development example:**
```r
mae_impl <- function(truth, estimate, case_weights = NULL) {
  errors <- abs(truth - estimate)

  # REQUIRED: Convert hardhat weight objects to numeric
  if (!is.null(case_weights)) {
    if (inherits(case_weights, c("hardhat_importance_weights",
                                 "hardhat_frequency_weights"))) {
      case_weights <- as.double(case_weights)  # ← CRITICAL
    }
  }

  # Then use internal helper
  yardstick_mean(errors, case_weights = case_weights)
}
```

**Why this matters:** Hardhat weights are S3 objects, not plain numerics. Without conversion, arithmetic operations and functions like `weighted.mean()` will fail. This conversion is **mandatory** in every _impl function that handles case weights.

---

## Choosing Your Metric Type

```
┌─────────────────────────────────────────────────────────────┐
│ What type of data do you have?                              │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┬───────────────────┐
        │                   │                   │                   │
        ▼                   ▼                   ▼                   ▼
   Regression        Classification    Survival Analysis    Quantile Forecasting
        │                   │                   │                   │
        ▼                   ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   NUMERIC   │     │ CLASS-BASED │     │  SURVIVAL   │     │  QUANTILE   │
│   METRICS   │     │   METRICS   │     │   METRICS   │     │   METRICS   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
        │                   │                   │                   │
        │                   ├───────────────────┤                   │
        │                   │                   │                   │
        │                   ▼                   ▼                   │
        │            ┌─────────────┐     ┌─────────────┐           │
        │            │   Classes   │     │Probabilities│           │
        │            └─────────────┘     └─────────────┘           │
        │                   │                   │                   │
        │                   ├───────────────────┤                   │
        │                   │                   │                   │
        │                   ▼                   ▼                   │
        │            ┌─────────────┐     ┌─────────────┐           │
        │            │Unordered?   │     │Unordered?   │           │
        │            │  CLASS      │     │ PROBABILITY │           │
        │            └─────────────┘     └─────────────┘           │
        │                   │                   │                   │
        │                   ▼                   ▼                   │
        │            ┌─────────────┐     ┌─────────────┐           │
        │            │Ordered?     │     │Ordered?     │           │
        │            │ORDERED PROB │     │ORDERED PROB │           │
        │            └─────────────┘     └─────────────┘           │
        │                                                            │
        │            ┌───────────────────┬───────────────┬─────────┤
        │            │                   │               │         │
        ▼            ▼                   ▼               ▼         ▼
  Examples:     Examples:          Examples:      Examples:  Examples:

  - MAE         - Accuracy         - ROC AUC      - Concordance - WIS

  - RMSE        - Precision        - Log Loss     - Brier       - Pinball

  - R²          - F1 Score         - PR AUC       - Royston's D - Coverage
                - Ranked Prob Score

  Survival Metrics Breakdown:

  - STATIC: Single overall value (e.g., Concordance)

  - DYNAMIC: Value per time point (e.g., Time-dependent Brier)

  - INTEGRATED: Averaged across time (e.g., Integrated Brier)

  - LINEAR PRED: From Cox models (e.g., Royston's D)
```

**Decision guide:**

- **Numeric metric**: Truth and predictions are continuous numbers → [Numeric Metrics](references/numeric-metrics.md)

- **Class metric**: Truth and predictions are unordered factor classes → [Class Metrics](references/class-metrics.md)

- **Probability metric**: Truth is unordered factor, predictions are probabilities → [Probability Metrics](references/probability-metrics.md)

- **Ordered probability metric**: Truth is ordered factor, predictions are probabilities → [Ordered Probability Metrics](references/ordered-probability-metrics.md)

- **Static survival metric**: Truth is Surv object, single numeric prediction → [Static Survival Metrics](references/static-survival-metrics.md)

- **Dynamic survival metric**: Truth is Surv object, time-dependent predictions → [Dynamic Survival Metrics](references/dynamic-survival-metrics.md)

- **Integrated survival metric**: Truth is Surv object, integrated across time → [Integrated Survival Metrics](references/integrated-survival-metrics.md)

- **Linear predictor survival metric**: Truth is Surv object, linear predictor from Cox model → [Linear Predictor Survival Metrics](references/linear-predictor-survival-metrics.md)

- **Quantile metric**: Truth is numeric, predictions are quantiles → [Quantile Metrics](references/quantile-metrics.md)

## Complete Example: Numeric Metric (MAE)

For a complete, step-by-step implementation of a numeric metric (MAE), see the comprehensive example with all required components in:

👉 **[Numeric Metrics Reference](references/numeric-metrics.md)**

This reference includes:

- Implementation function (`mae_impl`) with case weights handling

- Vector interface (`mae_vec`) with validation and NA handling

- Data frame method with `new_numeric_metric()` wrapper

- Complete test suite covering correctness, NA handling, input validation, and case weights

- Working examples you can adapt for your own metrics

**Quick preview of the pattern:**

- `_impl()` function: Core calculation logic

- `_vec()` function: Validation and NA handling

- `.data.frame()` method: Integration with yardstick system

See also [Extension Development Guide](references/extension-guide.md) for the complete implementation walkthrough.

## Implementation Guide by Metric Type

### Numeric Metrics

**Use for:** Regression metrics where truth and predictions are continuous numbers.

**Pattern:** Three-function approach (_impl, _vec, data.frame method)

**Complete guide:** [Numeric Metrics](references/numeric-metrics.md)

**Key points:**

- Always use `check_numeric_metric()` for validation

- Handle case weights with `weighted.mean()`

- Use `yardstick_remove_missing()` for NA handling

- Return `.estimator = "standard"`

**Examples:** MAE, RMSE, MSE, Huber Loss, R-squared

**Reference implementations:**

- Simple metrics: `R/num-mae.R`, `R/num-rmse.R`, `R/num-mse.R`

- Parameterized metrics: `R/num-huber_loss.R` (has delta parameter)

- Complex metrics: `R/num-ccc.R` (correlation-based)

### Class Metrics

**Use for:** Classification metrics where truth and predictions are factor classes.

**Pattern:** Uses confusion matrix from `yardstick_table()`

**Complete guide:** [Class Metrics](references/class-metrics.md)

**Key points:**

- Use `yardstick_table()` to create weighted confusion matrix

- Implement separate `_binary` and `_estimator_impl` functions

- Handle factor level ordering with `event_level` parameter

- Support multiclass with macro, micro, macro_weighted averaging

**Examples:** Accuracy, Precision, Recall, F1, Specificity

**Reference implementations:**

- Simple metrics: `R/class-accuracy.R`, `R/class-precision.R`, `R/class-recall.R`

- Combined metrics: `R/class-f_meas.R` (F1 score)

- Balanced metrics: `R/class-bal_accuracy.R` (handles class imbalance)

### Probability Metrics

**Use for:** Metrics that evaluate predicted probabilities against true classes.

**Pattern:** Similar to class metrics but uses probability columns

**Complete guide:** [Probability Metrics](references/probability-metrics.md)

**Key points:**

- Truth is factor, estimate is probabilities

- Convert factor to binary for binary metrics

- Handle multiple probability columns for multiclass

- Use `check_prob_metric()` for validation

**Examples:** ROC AUC, Log Loss, Brier Score, PR AUC

**Reference implementations:**

- Curve-based: `R/prob-roc_auc.R`, `R/prob-pr_auc.R`

- Scoring rules: `R/prob-brier_class.R`, `R/prob-mn_log_loss.R`

### Ordered Probability Metrics

**Use for:** Ordinal classification metrics where class ordering matters.

**Pattern:** Three-function approach with cumulative probabilities

**Complete guide:** [Ordered Probability Metrics](references/ordered-probability-metrics.md)

**Key points:**

- Truth must be ordered factor

- Uses cumulative probabilities to respect ordering

- Use `check_ordered_prob_metric()` for validation

- No averaging types (works same for any number of classes)

**Examples:** Ranked Probability Score (RPS)

### Static Survival Metrics

**Use for:** Overall survival metrics with single numeric predictions.

**Pattern:** Three-function approach with Surv objects

**Complete guide:** [Static Survival Metrics](references/static-survival-metrics.md)

**Key points:**

- Truth is Surv object from survival package

- Estimate is single numeric per observation

- Handles right-censoring with comparable pairs

- Use `check_static_survival_metric()` for validation

**Examples:** Concordance Index (C-index)

### Dynamic Survival Metrics

**Use for:** Time-dependent survival metrics at specific evaluation times.

**Pattern:** Three-function approach with list-column predictions

**Complete guide:** [Dynamic Survival Metrics](references/dynamic-survival-metrics.md)

**Key points:**

- Truth is Surv object

- Estimate is list-column of data.frames with `.eval_time`, `.pred_survival`, `.weight_censored`

- Returns multiple rows (one per eval_time)

- Uses inverse probability of censoring weights (IPCW)

**Examples:** Time-dependent Brier Score, Time-dependent ROC AUC

### Integrated Survival Metrics

**Use for:** Overall survival metrics integrated across evaluation times.

**Pattern:** Two-function approach (calls dynamic metric, then integrates)

**Complete guide:** [Integrated Survival Metrics](references/integrated-survival-metrics.md)

**Key points:**

- Same input format as dynamic survival metrics

- Integrates across time using trapezoidal rule

- Normalizes by max evaluation time

- Requires at least 2 evaluation times

**Examples:** Integrated Brier Score, Integrated ROC AUC

### Linear Predictor Survival Metrics

**Use for:** Metrics for linear predictors from Cox models.

**Pattern:** Three-function approach with transformations

**Complete guide:** [Linear Predictor Survival Metrics](references/linear-predictor-survival-metrics.md)

**Key points:**

- Truth is Surv object

- Estimate is linear predictor values (unbounded)

- Often uses transformations (e.g., normal scores)

- Use `check_linear_pred_survival_metric()` for validation

**Examples:** Royston's D statistic, R²_D

### Quantile Metrics

**Use for:** Quantile prediction metrics for uncertainty quantification.

**Pattern:** Three-function approach with quantile_pred objects

**Complete guide:** [Quantile Metrics](references/quantile-metrics.md)

**Key points:**

- Truth is numeric

- Estimate is `hardhat::quantile_pred` object

- Handles missing quantiles (impute, drop, or propagate)

- Uses `fn_options` for additional parameters

**Examples:** Weighted Interval Score (WIS), Pinball Loss

## Documentation

See [Roxygen Documentation](references/package-roxygen-documentation.md) for complete templates.

**Required roxygen tags:**
```r
#' @family [metric category] metrics
#' @export
#' @inheritParams [similar_metric]
#' @param data A data frame
#' @param truth Unquoted column with true values
#' @param estimate Unquoted column with predictions
#' @param na_rm Remove missing values (default TRUE)
#' @param case_weights Optional case weights column
#' @return A tibble with .metric, .estimator, .estimate columns
```

## Testing

See [Testing Patterns (Extension)](references/package-extension-requirements.md#testing-requirements) for comprehensive guide.

**Required test categories:**
1. **Correctness**: Metric calculates correctly
2. **NA handling**: Both `na_rm = TRUE` and `FALSE`
3. **Input validation**: Wrong types, mismatched lengths
4. **Case weights**: Weighted and unweighted differ
5. **Edge cases**: All correct, all wrong, empty data

## Common Patterns

### Using the confusion matrix

See [Confusion Matrix](references/confusion-matrix.md) for complete guide.

```r
# Get confusion matrix
xtab <- yardstick::yardstick_table(truth, estimate, case_weights)

# Extract values (for binary classification)
tp <- xtab[2, 2]  # True positives: truth = second, pred = second
tn <- xtab[1, 1]  # True negatives: truth = first, pred = first
fp <- xtab[1, 2]  # False positives: truth = first, pred = second
fn <- xtab[2, 1]  # False negatives: truth = second, pred = first
```

### Handling case weights

See [Case Weights](references/case-weights.md) for complete guide.

**IMPORTANT: Always convert hardhat weights to numeric using `as.double()`**

```r
# Extension development pattern (no internal functions):
# ALWAYS include this conversion pattern in your _impl function
if (!is.null(case_weights)) {
  # Convert hardhat weight objects to numeric vector
  # This is REQUIRED - hardhat weights are S3 objects, not plain numerics
  if (inherits(case_weights, c("hardhat_importance_weights",
                               "hardhat_frequency_weights"))) {
    case_weights <- as.double(case_weights)  # ← CRITICAL: Must convert to double
  }
}

# Use in calculations
if (is.null(case_weights)) {
  mean(values)
} else {
  weighted.mean(values, w = case_weights)  # Now safe to use with base R functions
}
```

**Why `as.double()` is required:**
- hardhat weight objects are S3 classes, not plain numeric vectors
- Base R functions like `weighted.mean()` expect numeric vectors
- Without conversion, you'll get errors like "non-numeric argument"
- Source development can use `yardstick_mean()` which handles this internally
- Extension development must do the conversion manually

### Multiclass averaging

See [Class Metrics](references/class-metrics.md) for complete guide.

**Macro averaging:** Average of per-class metrics (treats all classes equally)
**Micro averaging:** Pool all observations, calculate once (treats all observations equally)
**Macro-weighted averaging:** Weighted average by class prevalence

## Advanced Topics

### Combining Metrics with metric_set()

Once you've created your metric, you can combine it with other metrics using `metric_set()`:

```r
my_metrics <- metric_set(mae, rmse, my_custom_metric)
my_metrics(data, truth = y, estimate = y_pred)
```

**Key benefits:**

- Calculate multiple metrics at once

- More efficient (shared calculations)

- Integrates with tune package

- Works with grouped data

See [Combining Metrics](references/metric-set.md) for complete guide.

### Creating Groupwise Metrics

Groupwise metrics measure disparity in metric values across groups (useful for fairness):

```r
accuracy_diff <- new_groupwise_metric(
  fn = accuracy,
  name = "accuracy_diff",
  aggregate = function(x) diff(range(x$.estimate))
)

accuracy_diff_by_group <- accuracy_diff(group_column)
accuracy_diff_by_group(data, truth, estimate)
```

**Use cases:**

- Fairness analysis across demographic groups

- Performance consistency across segments

- Disparity quantification

See [Groupwise Metrics](references/groupwise-metrics.md) for complete guide.

## Package-Specific Patterns (Source Development)

If you're contributing to yardstick itself, you have access to internal functions and conventions not available in extension development.

### File Naming Conventions

Yardstick uses strict naming patterns:

- Numeric: `R/num-[name].R` → `R/num-mae.R`

- Class: `R/class-[name].R` → `R/class-accuracy.R`

- Probability: `R/prob-[name].R` → `R/prob-roc_auc.R`

- Tests: `tests/testthat/test-num-mae.R`

### Internal Functions Available

When developing yardstick itself, you can use:

- `yardstick_mean()` - Weighted mean with case weight handling

- `finalize_estimator_internal()` - Estimator selection for multiclass

- `check_numeric_metric()`, `check_class_metric()`, `check_prob_metric()` - Validation

- Test helpers: `data_altman()`, `data_three_class()`, `data_hpc_cv1()`

### Documentation Templates

Yardstick uses templates in `man-roxygen/`:
```r
#' @templateVar fn mae
#' @template return
#' @template event_first
```

### Snapshot Testing

Yardstick uses `testthat::expect_snapshot()` extensively:
```r
test_that("mae returns correct structure", {
  expect_snapshot(mae(df, truth, estimate))
})
```

**Complete source development guide:** [Source Development Guide](references/source-guide.md)

---

## Package Integration

### Package-level documentation

See [Package Imports](references/package-imports.md) for complete guide.

Create `R/{packagename}-package.R`:

```r
#' @keywords internal
"_PACKAGE"

#' @importFrom rlang .data := !! enquo enquos
#' @importFrom yardstick new_numeric_metric new_class_metric new_prob_metric
NULL
```

### Exports

All metrics must be exported:
```r
#' @export
mae <- function(data, ...) {
  UseMethod("mae")
}
```

## Best Practices

See [Best Practices (Extension)](references/package-extension-requirements.md#best-practices) for complete guide.

**Key principles:**

- Use base pipe `|>` not magrittr pipe `%>%`

- Prefer for-loops over `purrr::map()` for better error messages

- Use `cli::cli_abort()` for error messages

- Keep functions focused on single responsibility

- Validate early (in `_vec`), trust data in `_impl`

## Troubleshooting

See [Troubleshooting (Extension)](references/package-extension-requirements.md#common-issues-solutions) for complete guide.

**Common issues:**

- "No visible global function definition" → Add to package imports

- "Object not found" in tests → Use `devtools::load_all()` before testing

- NA handling bugs → Check both `na_rm = TRUE` and `FALSE` cases

- Case weights not working → Convert hardhat weights to numeric

---

## File Creation Guidelines

**Extension development (creating new package):**
- R/[metric_name].R (with complete roxygen docs and examples)
- tests/testthat/test-[metric_name].R (comprehensive tests)
- README.md (ONLY if package has no README - check first!)

Typically creates 2 files (3 if README needed).

**Source development (PR to yardstick):**
- R/[type]-[metric_name].R (e.g., R/num-mae.R, R/class-accuracy.R)
- tests/testthat/test-[type]-[metric_name].R

Creates exactly 2 files.

**❌ AVOID creating these files:**
- README.md or README.txt (for PRs - yardstick already has one)
- NEWS_entry.md (mention in conversation - maintainer adds to NEWS.md)
- IMPLEMENTATION_SUMMARY.md, IMPLEMENTATION_NOTES.md, IMPLEMENTATION_NOTES.txt
- QUICKSTART.md, QUICK_REFERENCE.md, INTEGRATION_GUIDE.md
- example_usage.R, USAGE_EXAMPLE.R (examples go in roxygen @examples)
- PR_CHECKLIST.md, PR_DESCRIPTION.md, PR_SUMMARY.md
- INDEX.md, FILE_GUIDE.md, SUMMARY.md, SUMMARY.txt, OVERVIEW.md
- metric_examples.R, test_examples.R
- METRIC_DESIGN.md, VALIDATION_APPROACH.md
- pkgdown_update.txt, pkgdown_addition.yml
- WORKFLOW_COMMANDS.sh, setup.sh
- verification_script.R, check_metric.R
- ANY other .md, .txt, .yml, .sh files beyond the 2-3 core files

**Where everything goes:**
- Examples → roxygen @examples in R file
- Implementation notes → roxygen @details in R file
- Metric design rationale → roxygen @details in R file
- PR description → conversation with user
- NEWS entry → conversation (maintainer adds it)
- Usage guide → README.md (extension dev only) or roxygen examples

---

## Related Skills

- [add-recipe-step](../add-recipe-step/SKILL.md) - Recipe steps may generate outputs that need custom metrics

- [add-dials-parameter](../add-dials-parameter/SKILL.md) - Custom metrics may require custom tuning parameters for hyperparameter optimization

- [add-parsnip-model](../add-parsnip-model/SKILL.md) - Metrics evaluate predictions from model specifications

- [add-parsnip-engine](../add-parsnip-engine/SKILL.md) - Metrics evaluate predictions from model engines

## Next Steps

**For Extension Development (creating new packages):**

1. **Extension prerequisites:** [Extension Prerequisites](references/package-extension-prerequisites.md) - START HERE

**For Source Development (contributing to yardstick):**

1. **Start here:** [Source Development Guide](references/source-guide.md)
2. **Clone repository:** See [Repository Access](references/package-repository-access.md)
3. **Study existing metrics:** Browse `R/num-*.R`, `R/class-*.R`, etc.
4. **Follow package conventions:** File naming, internal functions, templates
5. **Test with internal helpers:** See [Testing Patterns (Source)](references/testing-patterns-source.md)
6. **Submit PR:** See [Source Development Guide](references/source-guide.md) for PR process
