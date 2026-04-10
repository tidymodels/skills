# Time Series Resampling

Complete guide to time series cross-validation and backtesting with modeltime.

## Why Time Series Resampling is Different

**Never use random cross-validation for time series data.** Random CV shuffles observations, which:

- **Violates temporal ordering** - Training on future, testing on past
- **Creates data leakage** - Model sees future values during training
- **Produces optimistically biased estimates** - Performance looks better than it actually is

**Always use time series cross-validation (`time_series_cv`)** which:

- **Respects temporal ordering** - Always trains on past, tests on future
- **Simulates realistic forecasting** - Tests how model would perform in production
- **Expands training window** - Mirrors how models are used (retraining as new data arrives)
- **Prevents data leakage** - No information from the future leaks into training

## The Backtesting Process

Time series cross-validation creates multiple train/test splits that respect temporal ordering:

```
Split 1:  [--------Training--------][--Test--]
Split 2:  [---------Training---------][--Test--]
Split 3:  [----------Training----------][--Test--]
Split 4:  [-----------Training-----------][--Test--]
```

Each split:

1. **Trains on historical data** up to a certain point
2. **Tests on future data** immediately following
3. **Expands the training window** for the next split

This mimics real-world forecasting where you periodically retrain and forecast ahead.

## Key Principle

**Resampling is your PRIMARY tool for comparing models—not the test set.**

Use backtesting to:

- Compare different algorithms
- Evaluate hyperparameter choices
- Select feature engineering approaches
- Choose between classical and ML models
- Decide on ensemble strategies

Only use the test set for final validation after making all decisions.

## Implementation with `time_series_cv()`

```r
library(modeltime.resample)

# Set seed before resampling for reproducibility
set.seed(5847)

resamples <- time_series_cv(
  data = train_data,
  initial = "2 years",
  assess = "6 months",
  skip = "3 months",
  slice_limit = 4
)
```

### Parameters Explained

- **`initial`**: How much data to use for the first training set
  - Should be large enough to capture patterns
  - Common values: "1 year", "2 years", "80% of training data"

- **`assess`**: How far ahead to forecast in each test set
  - Should match your forecast horizon
  - Common values: "3 months", "6 months", "1 year"
  - **Ask the user**: "How far ahead do you need to forecast?"

- **`skip`**: How much time to skip between slices
  - Controls how many slices you get
  - Smaller skip = more slices = longer computation
  - Common values: "1 month", "3 months", "6 months"

- **`slice_limit`**: Maximum number of slices to create
  - Limits computation time
  - Common values: 4-6 slices
  - More slices = better estimates but slower

### Choosing Parameter Values

**Ask the user about forecast horizon:**

> "How far ahead do you need to forecast? This will help me set up the resampling strategy."

**Then suggest values based on their answer:**

- If they need 6-month forecasts → `assess = "6 months"`
- If they have 4+ years of data → `initial = "2 years"`
- For moderate computation → `skip = "3 months"`, `slice_limit = 4`

**Suggest using the same `assess` size as the test set** to ensure consistent evaluation.

## Evaluating Models with Resampling

```r
# Fit models on each resample
models_tbl |>
  modeltime_fit_resamples(resamples = resamples) |>
  modeltime_resample_accuracy(summary_fns = list(mean = mean, sd = sd))
```

This produces:

- **Mean performance** across all slices (primary metric for comparison)
- **Standard deviation** (indicates stability/consistency)
- **Metrics**: RMSE, MAE, MAPE, etc.

### Interpreting Results

**Compare models on mean RMSE/MAE:**

- Lower is better
- RMSE penalizes large errors more than MAE
- Use RMSE as primary metric unless outliers are a concern

**Check standard deviation:**

- Lower SD = more consistent performance
- High SD = model performance varies by time period
- Prefer models with both good mean and low SD

**Example results:**

```
# A tibble: 5 × 4
  .model_id .type       mean_rmse    sd_rmse
      <int> <chr>           <dbl>      <dbl>
1         1 ARIMA           125.       15.2   # Consistent
2         2 ETS             118.       12.8   # Best + consistent
3         3 Prophet         132.       28.4   # Good but variable
4         4 Linear          145.       18.6
5         5 XGBoost         121.       14.1   # Good + consistent
```

Here, ETS has the lowest mean RMSE and low SD, making it a strong candidate.

## Resampling Rules

- **NEVER** use data outside the training set to determine feature engineering steps
- **NEVER** engineer features, then evaluate directly on training data without resampling
- **DO** treat feature engineering and model training as a single process
- **DO** use resampling to measure combined feature engineering + model performance
- **DO** use resampling to select best tuning parameters
- **DO** ask the user how much data to use to assess the model and suggest the same size as the test set

## Resampling vs Test Set

| Purpose | Use Resampling | Use Test Set |
|---------|---------------|--------------|
| Compare models | ✅ Yes | ❌ No |
| Tune hyperparameters | ✅ Yes | ❌ No |
| Select features | ✅ Yes | ❌ No |
| Choose ensemble strategy | ✅ Yes | ❌ No |
| Final validation | ❌ No | ✅ Yes (with permission) |

**Key principle:** Make ALL modeling decisions using resampling. Use the test set only once for final validation.

## Advanced: Visualizing Resampling Splits

```r
# Visualize the resampling plan
resamples |>
  tk_time_series_cv_plan() |>
  plot_time_series_cv_plan(date, value)
```

This shows:

- How the training window expands
- Where test sets fall
- Helps verify the resampling strategy makes sense

## Common Questions

**Q: Why not just use the test set to compare models?**

A: Each test set use reduces its validity. Resampling gives you multiple out-of-sample evaluations without touching the test set.

**Q: How many slices should I use?**

A: 4-6 is typical. More slices give better estimates but take longer. Balance precision with computation time.

**Q: Should `assess` match my forecast horizon?**

A: Yes, ideally. If you need 6-month forecasts in production, use `assess = "6 months"` to evaluate that horizon.

**Q: Can I use random CV if I have external time-independent predictors?**

A: No. Even with external predictors, the temporal structure of the target variable must be respected. Always use time series CV.

## Summary

Time series resampling:

1. **Respects temporal ordering** - No data leakage
2. **Simulates realistic forecasting** - Trains on past, tests on future
3. **Primary tool for model comparison** - Not the test set
4. **Provides multiple evaluations** - Mean and SD of performance
5. **Requires thoughtful parameter choices** - Based on forecast horizon and data size

Use `time_series_cv()` for all model comparisons, and reserve the test set for final validation with user permission.
