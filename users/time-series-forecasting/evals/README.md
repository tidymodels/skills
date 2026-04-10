# Time Series Forecasting - Evaluation Tests

This directory contains evaluation tests for the `time-series-forecasting` skill.

## Test Coverage

**8 comprehensive evaluation scenarios covering:**

1. **Basic Forecasting Workflow** - Complete workflow with baseline ensemble (ARIMA, ETS, Prophet)
2. **ML Models with Feature Engineering** - XGBoost/RF with external predictors and date features
3. **Test Set Protection** - Refusing evaluation without explicit permission
4. **Parallel Processing** - Proper interaction pattern for computationally intensive work
5. **Cross-Validation** - Proper time_series_cv parameters and interpretation
6. **Ensemble Methods** - Validating ensembles before recommending them
7. **Temporal Ordering** - Warning against random CV and explaining data leakage
8. **Hyperparameter Tuning** - Tuning ML models with proper time series resampling

## Critical Behaviors Tested

### Test Set Protection (Eval #3)

- **Refuses** to evaluate on test set without explicit user permission
- **Explains** why test set is for final validation only
- **Offers** backtesting results as alternative for model comparison

### Temporal Ordering (Eval #7)

- **Warns** against random cross-validation for time series
- **Explains** data leakage: training on future to predict past
- **Recommends** time_series_cv with proper temporal splits

### Reproducibility (All Evals)

- **Sets seeds** before initial_time_split, time_series_cv, tune_grid
- **Avoids common values** (1, 123, 42, 999, 2024, etc.)
- **Uses random integers** between 1000-10000

### Feature Engineering (Eval #2)

- **Requires** step_timeseries_signature for ML models (XGBoost, Random Forest)
- **Not needed** for classical models (ARIMA, ETS, Prophet)
- **Explains** why different model types have different requirements

### Parallel Processing (Evals #4, #5, #8)

- **Detects** available cores with parallel::detectCores()
- **Asks user** in conversation (not just code comment)
- **Recommends** leaving 1-2 cores free
- **Uses** future package only (not parallel, mirai, foreach)

### Ensemble Methods (Eval #6)

- **Evaluates** ensemble performance before recommending
- **Validates** on same resamples as individual models
- **Acknowledges** that ensembles may not always improve
- **Explains** benefit of model diversity

### Backtesting as Primary Tool (Evals #1, #3, #5)

- **Emphasizes** time_series_cv for model comparison
- **Not test set** for model selection
- **Explains** why backtesting gives realistic performance estimates

## Running Evaluations

Use with the skill-creator evaluation workflow:

```r
# From Claude Code with skill-creator skill
/evals run users/time-series-forecasting
```

Or manually run individual scenarios:

```r
/evals run users/time-series-forecasting --id 3  # Test set protection
/evals run users/time-series-forecasting --id 7  # Temporal ordering
```

## Evaluation Structure

Each eval in `evals.json` contains:

- **id**: Unique identifier
- **prompt**: Realistic user request
- **expected_output**: Detailed description of correct behavior
- **files**: Required data files (currently none - prompts reference hypothetical files)
- **assertions**: Automated checks for critical behaviors

## Assertions Explained

### "No common seed values used"

Verifies that `set.seed()` calls avoid overused values:
- ❌ Bad: 1, 123, 42, 111, 222, 333, 999, 2024, 2025, 2026
- ✅ Good: Random integers between 1000-10000 (e.g., 3847, 7291, 5628)

### "Seeds set before random operations"

Checks that `set.seed()` is called immediately before:
- `initial_time_split()`
- `time_series_cv()`
- `tune_grid()`

### "Test set not used for model comparison"

Ensures model comparison uses `modeltime_resample_accuracy()` on time_series_cv results, NOT `modeltime_accuracy()` on test set without permission.

### "Feature engineering for ML models only"

Validates that:
- ML models (XGBoost, Random Forest) use recipes with `step_timeseries_signature()`
- Classical models (ARIMA, ETS, Prophet) use `value ~ date` directly

## Success Criteria

For each evaluation, the skill should:

### Correctness ✓

- Use proper temporal train/test splits
- Apply time series cross-validation (not random CV)
- Protect test set until final validation
- Set seeds for reproducibility

### Clarity ✓

- Explain why temporal ordering matters
- Justify model selection based on backtesting
- Describe when feature engineering is needed
- Communicate parallel processing recommendations

### Best Practices ✓

- Start with baseline ensemble (ARIMA, ETS, Prophet)
- Compare models on resampling, not test set
- Validate ensembles before recommending
- Ask for permission before test set evaluation

## Common Failure Modes to Test

1. **Using random CV** instead of time_series_cv → Eval #7
2. **Evaluating on test set** without permission → Eval #3
3. **No feature engineering** for ML models → Eval #2
4. **Not setting seeds** before random operations → All evals
5. **Using common seed values** (123, 42, etc.) → All evals
6. **Recommending ensemble** without validation → Eval #6
7. **No parallel processing** interaction → Evals #4, #5, #8
8. **Using test set** for model comparison → Evals #1, #3, #5

---

**Last Updated:** 2026-04-10

**Status:** 8 comprehensive evaluations ready for testing
