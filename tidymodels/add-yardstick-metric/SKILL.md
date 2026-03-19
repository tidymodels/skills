---
name: add-yardstick-metric
description: Guide for creating new yardstick metrics. Use when a developer needs to extend yardstick with a custom performance metric, including numeric, class, probability, ordered probability, survival (static, dynamic, integrated, linear predictor), and quantile metrics.
---

# Add Yardstick Metric

Guide for developing new metrics that extend the yardstick package. This skill provides best practices, code templates, and testing patterns for creating custom performance metrics.

---

## 🛑 CLAUDE: RUN VERIFICATION FIRST

**Before implementing ANY metrics, run this verification script from the user's package directory:**

```bash
cd /path/to/user/package
Rscript -e 'source("~/.claude/plugins/cache/tidymodels-skills/tidymodels-dev/<commit>/tidymodels/shared-scripts/verify-setup.R")'
```

**How to find the script path:**
- This skill is loaded from the plugin cache at `~/.claude/plugins/cache/tidymodels-skills/tidymodels-dev/<commit-hash>/tidymodels/`
- The verify-setup.R script is at `../shared-scripts/verify-setup.R` relative to this SKILL.md
- Use the absolute plugin cache path shown above, replacing `<commit>` with the actual commit hash from where this skill was loaded

**What the script checks:**
- Package structure (DESCRIPTION, R/, tests/testthat/)
- Claude Code integration (usethis version, .claude/CLAUDE.md)
- Repository access (repos/yardstick/)
- Dependencies (yardstick, rlang, cli)

**If there are ANY warnings:**
1. Guide the user through fixing them using suggested commands
2. Do NOT proceed with implementation until all checks pass
3. Critical blockers require user action first

**When to run:** After initial package setup, BEFORE implementing any metrics.

---

## Two Development Contexts

This skill supports **two distinct development contexts**:

### 🆕 Extension Development (Default)
**Creating a new R package** that extends yardstick with custom metrics.

- ✅ Use this for: New packages, standalone metrics, CRAN submissions
- 📦 Package detection: No `yardstick` in DESCRIPTION's `Package:` field
- ⚠️ **Constraint**: Can only use exported functions (no `:::`)
- 📖 **Guide**: [Extension Development Guide](references/extension-guide.md)

### 🔧 Source Development (Advanced)
**Contributing directly to yardstick** via pull requests.

- ✅ Use this for: Contributing to tidymodels/yardstick repository
- 📦 Package detection: `Package: yardstick` in DESCRIPTION
- ✨ **Benefit**: Can use internal functions and package infrastructure
- 📖 **Guide**: [Source Development Guide](references/source-guide.md)

**This main guide shows extension development patterns.** If you're contributing to yardstick itself, see the [Source Development Guide](references/source-guide.md) for package-specific details.

---

## Quick Start

**Choose your context:**

- **Creating a new package?** → Follow this guide, then see [Extension Development Guide](references/extension-guide.md)
- **Contributing to yardstick?** → Clone repository, then see [Source Development Guide](references/source-guide.md)

**Not sure which?** If you're in the `tidymodels/yardstick` repository, use source development. Otherwise, use extension development.

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

## Repository Access

Clone the yardstick source repository for reference implementations and examples.

**Benefits:**
- See actual metric implementations
- Reference real test patterns
- Search through source code
- Understand package architecture

**Setup:**

Run from your R package directory:

```bash
# macOS/Linux/WSL
~/.claude/plugins/cache/tidymodels-skills/tidymodels-dev/*/tidymodels/shared-scripts/clone-tidymodels-repos.sh yardstick

# Windows (PowerShell)
~\.claude\plugins\cache\tidymodels-skills\tidymodels-dev\*\tidymodels\shared-scripts\clone-tidymodels-repos.ps1 yardstick

# Any platform (Python)
python3 ~/.claude/plugins/cache/tidymodels-skills/tidymodels-dev/*/tidymodels/shared-scripts/clone-tidymodels-repos.py yardstick
```

**Note:** The `*` wildcard matches the commit hash. The shell will expand it to the actual path.

**For complete instructions**, see: [Repository Access Setup](../shared-references/repository-access.md)

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
- [R Package Setup](../shared-references/r-package-setup.md) - Package initialization and structure
- [Development Workflow](../shared-references/development-workflow.md) - Fast iteration cycle
- [Testing Patterns (Extension)](../shared-references/testing-patterns-extension.md) - Extension testing guide
- [Roxygen Documentation](../shared-references/roxygen-documentation.md) - Documentation templates
- [Package Imports](../shared-references/package-imports.md) - Managing dependencies
- [Best Practices (Extension)](../shared-references/best-practices-extension.md) - Extension code style
- [Troubleshooting (Extension)](../shared-references/troubleshooting-extension.md) - Extension issues

**Source Development Specific:**
- [Testing Patterns (Source)](references/testing-patterns-source.md) - Using internal test helpers
- [Best Practices (Source)](references/best-practices-source.md) - Using internal functions
- [Troubleshooting (Source)](references/troubleshooting-source.md) - Source-specific issues

## Development Workflow

See [Development Workflow](../shared-references/development-workflow.md) for complete details.

**Fast iteration cycle (run repeatedly):**

1. `devtools::document()` - Generate documentation
2. `devtools::load_all()` - Load your package
3. `devtools::test()` - Run tests

**Final validation (run once at end):**

4. `devtools::check()` - Full R CMD check

**WARNING:** Do NOT run `check()` during iteration. It takes 1-2 minutes and is unnecessary until you're done.

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

See [Roxygen Documentation](../shared-references/roxygen-documentation.md) for complete templates.

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

See [Testing Patterns (Extension)](../shared-references/testing-patterns-extension.md) for comprehensive guide.

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

```r
# Check and convert hardhat weights
if (!is.null(case_weights)) {
  if (inherits(case_weights, c("hardhat_importance_weights",
                               "hardhat_frequency_weights"))) {
    case_weights <- as.double(case_weights)
  }
}

# Use in calculations
if (is.null(case_weights)) {
  mean(values)
} else {
  weighted.mean(values, w = case_weights)
}
```

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

See [Package Imports](../shared-references/package-imports.md) for complete guide.

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

See [Best Practices (Extension)](../shared-references/best-practices-extension.md) for complete guide.

**Key principles:**
- Use base pipe `|>` not magrittr pipe `%>%`
- Prefer for-loops over `purrr::map()` for better error messages
- Use `cli::cli_abort()` for error messages
- Keep functions focused on single responsibility
- Validate early (in `_vec`), trust data in `_impl`

## Troubleshooting

See [Troubleshooting (Extension)](../shared-references/troubleshooting-extension.md) for complete guide.

**Common issues:**
- "No visible global function definition" → Add to package imports
- "Object not found" in tests → Use `devtools::load_all()` before testing
- NA handling bugs → Check both `na_rm = TRUE` and `FALSE` cases
- Case weights not working → Convert hardhat weights to numeric

## Next Steps

**For Extension Development (creating new packages):**

1. **Choose your context:** [Extension Development Guide](references/extension-guide.md)
2. **Understand the system:** Read [Metric System](references/metric-system.md)
3. **Choose metric type:**
   - Regression: [Numeric](references/numeric-metrics.md)
   - Classification: [Class](references/class-metrics.md), [Probability](references/probability-metrics.md), [Ordered Probability](references/ordered-probability-metrics.md)
   - Survival: [Static](references/static-survival-metrics.md), [Dynamic](references/dynamic-survival-metrics.md), [Integrated](references/integrated-survival-metrics.md), [Linear Predictor](references/linear-predictor-survival-metrics.md)
   - Quantile: [Quantile](references/quantile-metrics.md)
4. **Follow the template:** Use complete examples from reference files
5. **Test thoroughly:** See [Testing Patterns (Extension)](../shared-references/testing-patterns-extension.md)
6. **Document completely:** See [Roxygen Documentation](../shared-references/roxygen-documentation.md)
7. **Run final check:** `devtools::check()` before publishing

**For Source Development (contributing to yardstick):**

1. **Start here:** [Source Development Guide](references/source-guide.md)
2. **Clone repository:** See [Repository Access](../shared-references/repository-access.md)
3. **Study existing metrics:** Browse `R/num-*.R`, `R/class-*.R`, etc.
4. **Follow package conventions:** File naming, internal functions, templates
5. **Test with internal helpers:** See [Testing Patterns (Source)](references/testing-patterns-source.md)
6. **Submit PR:** See [Source Development Guide](references/source-guide.md) for PR process
