# Ensemble Methods for Time Series

Complete guide to combining multiple models for improved forecasting performance.

## Why Ensembles?

**Ensemble methods combine predictions from multiple models** to produce a single, often more accurate forecast.

**Benefits:**

- **Improved accuracy** - Often outperform individual models
- **Reduced variance** - Less sensitive to quirks of single models
- **Robustness** - Hedge against model-specific failures
- **Capture different patterns** - Different models excel at different aspects

**When ensembles help most:**

- Individual models have similar performance
- Models capture different patterns (e.g., ARIMA + XGBoost)
- High-stakes forecasts where accuracy matters
- When no single model clearly dominates

**When ensembles may not help:**

- One model far outperforms all others (just use that model)
- All models are similar types (e.g., all tree-based)
- Very limited data

## Ensemble Strategy

**Recommended approach:**

1. **Fit multiple diverse models** (classical + ML)
2. **Evaluate each on backtesting** - see [resampling.md](resampling.md)
3. **Create ensemble from top performers**
4. **Evaluate ensemble on backtesting** (not test set)
5. **Compare to individual models**
6. **Select best approach** (ensemble or individual)

**Key principle:** Ensembles are not automatic improvements. Always evaluate using resampling before deciding to use an ensemble.

## Available Ensemble Methods

### Mean Ensemble

**Averages predictions** from all models equally.

```r
library(modeltime.ensemble)

ensemble_fit <- calibration_tbl |>
  ensemble_average(type = "mean")
```

**When to use:**

- Models have similar accuracy
- Simplest approach
- Good default choice

**Pros:**

- Simple and interpretable
- Reduces variance
- Fast

**Cons:**

- Gives equal weight to all models (even weaker ones)
- May not be optimal if models vary in quality

### Median Ensemble

**Takes median prediction** across models.

```r
ensemble_fit <- calibration_tbl |>
  ensemble_average(type = "median")
```

**When to use:**

- Concerned about outlier predictions
- Want more robust ensemble
- Some models occasionally produce extreme forecasts

**Pros:**

- Robust to outliers
- Reduces impact of poor individual predictions

**Cons:**

- Less common than mean
- May be less smooth

### Weighted Ensemble

**Weights models by performance** on backtesting or test data.

```r
# Requires loading weights from previous evaluation
ensemble_fit <- calibration_tbl |>
  ensemble_weighted(loadings = model_weights)
```

**When to use:**

- Models have different accuracy levels
- Want to favor better performers
- Have reliable performance estimates

**Note:** More complex setup - requires computing and storing weights.

## Ensemble Workflow

### Step 1: Fit Individual Models

```r
# Fit diverse models
models_tbl <- modeltime_table(
  arima_fit,     # Classical: trend
  ets_fit,       # Classical: seasonality
  prophet_fit,   # Classical: robust
  xgb_fit        # ML: complex patterns
)
```

**Diversity is key:** Include models that capture different aspects of the data.

### Step 2: Evaluate with Backtesting

```r
library(modeltime.resample)

set.seed(5847)
resamples <- time_series_cv(
  data = train_data,
  initial = "2 years",
  assess = "6 months",
  skip = "3 months",
  slice_limit = 4
)

# Evaluate individual models
resample_results <- models_tbl |>
  modeltime_fit_resamples(resamples = resamples) |>
  modeltime_resample_accuracy(summary_fns = list(mean = mean, sd = sd))

resample_results
```

**Look for:**

- Models with good mean performance
- Low standard deviation (consistent)
- Complementary strengths

### Step 3: Create Ensemble

**If using test set** (after getting user permission):

```r
# Calibrate on test set
calibration_tbl <- models_tbl |>
  modeltime_calibrate(new_data = test_data)

# Create ensemble
ensemble_fit <- calibration_tbl |>
  ensemble_average(type = "mean")
```

**If not using test set yet:**

Create ensemble on training data for initial evaluation:

```r
# Use last resample as calibration
# (This is less ideal but allows ensemble evaluation before test set)
calibration_tbl <- models_tbl |>
  modeltime_calibrate(new_data = train_data)

ensemble_fit <- calibration_tbl |>
  ensemble_average(type = "mean")
```

### Step 4: Evaluate Ensemble

**Evaluate ensemble using backtesting:**

```r
# Add ensemble to model table
ensemble_tbl <- modeltime_table(ensemble_fit)

# Evaluate on same resamples
ensemble_results <- ensemble_tbl |>
  modeltime_fit_resamples(resamples = resamples) |>
  modeltime_resample_accuracy(summary_fns = list(mean = mean, sd = sd))

ensemble_results
```

**Important:** Evaluate ensemble using resampling, not test set. Only use test set with explicit user permission.

### Step 5: Compare

```r
# Combine results
bind_rows(
  resample_results,
  ensemble_results
) |>
  arrange(mean_rmse)
```

**Decision:**

- If ensemble has lowest RMSE → Use ensemble
- If individual model dominates → Use that model
- If tie → Consider ensemble for robustness

## Example: Complete Ensemble Workflow

```r
# 1. Fit diverse models
arima_fit <- arima_reg() |> set_engine("auto_arima") |>
  fit(value ~ date, data = train_data)

ets_fit <- exp_smoothing() |> set_engine("ets") |>
  fit(value ~ date, data = train_data)

prophet_fit <- prophet_reg() |> set_engine("prophet") |>
  fit(value ~ date, data = train_data)

xgb_fit <- workflow(signature_rec, boost_tree() |> set_engine("xgboost")) |>
  fit(train_data)

models_tbl <- modeltime_table(arima_fit, ets_fit, prophet_fit, xgb_fit)

# 2. Set up resampling
set.seed(5847)
resamples <- time_series_cv(
  data = train_data,
  initial = "2 years",
  assess = "6 months",
  skip = "3 months",
  slice_limit = 4
)

# 3. Evaluate individual models
individual_results <- models_tbl |>
  modeltime_fit_resamples(resamples = resamples) |>
  modeltime_resample_accuracy(summary_fns = list(mean = mean, sd = sd))

individual_results

# 4. Create ensemble (using training data for calibration)
calibration_tbl <- models_tbl |>
  modeltime_calibrate(new_data = train_data)

ensemble_fit <- calibration_tbl |>
  ensemble_average(type = "mean")

# 5. Evaluate ensemble
ensemble_results <- modeltime_table(ensemble_fit) |>
  modeltime_fit_resamples(resamples = resamples) |>
  modeltime_resample_accuracy(summary_fns = list(mean = mean, sd = sd))

# 6. Compare
bind_rows(individual_results, ensemble_results) |>
  arrange(mean_rmse)

# 7. Select best approach based on backtesting results
```

## Selecting Models for Ensemble

**Include models that:**

- Have reasonable performance (within ~10% of best)
- Use different algorithms (ARIMA, tree-based, neural net)
- Capture different patterns
- Show consistent performance (low SD)

**Exclude models that:**

- Perform much worse than others
- Are redundant (e.g., two ARIMA variants)
- Show high variance
- Have correlated predictions with other models

**Example good ensemble:**

- ARIMA (trend)
- ETS (seasonality)
- XGBoost (complex patterns + external predictors)

**Example poor ensemble:**

- ARIMA
- Auto ARIMA with different settings
- Another ARIMA variant
- (Too similar - won't gain from diversity)

## Ensemble Rules

- **Evaluate ensemble using RESAMPLING** (not test set)
- **Compare to individual models** before deciding
- **Don't assume ensembles always help** - validate the improvement
- **Only evaluate on test set** with explicit user permission

## Advanced: Model Stacking

Stacking uses a meta-model to learn optimal weights:

```r
# Requires modeltime.ensemble
ensemble_fit <- calibration_tbl |>
  ensemble_model_spec(
    model_spec = linear_reg() |> set_engine("lm"),
    control = control_grid(save_pred = TRUE)
  )
```

**When to use:**

- Have enough data for meta-model training
- Want to optimize model weights
- Individual models have very different performance

**Caution:** More complex, requires careful validation to avoid overfitting.

## Interpretability Considerations

**Ensembles reduce interpretability:**

- Harder to explain "why" a forecast was made
- Multiple models contribute
- Weights may not be intuitive

**Trade-off:**

- Gain: Improved accuracy
- Loss: Explainability

**Recommendation:** If interpretability is critical, favor individual models (especially classical ones). If accuracy is paramount, ensembles often help.

## Common Questions

**Q: Should I always use ensembles?**

A: No. Only when they improve performance on backtesting compared to individual models.

**Q: How many models should I include?**

A: 3-5 diverse models is typical. Too few = limited benefit, too many = diminishing returns and complexity.

**Q: Can I ensemble only ML models, or only classical models?**

A: You can, but **diverse ensembles work best**. Combining classical + ML often outperforms single-type ensembles.

**Q: Should I evaluate the ensemble on the test set?**

A: Only after user permission, and only if the ensemble performed well on backtesting. Don't use the test set to decide whether to ensemble—use resampling for that.

**Q: What if the ensemble is worse than the best individual model?**

A: Use the best individual model. Ensembles don't always help.

## Summary

Ensemble best practices:

1. **Fit diverse models** - Different algorithms, different strengths
2. **Evaluate each on backtesting** - Understand individual performance
3. **Create ensemble and evaluate on backtesting** - Not test set
4. **Compare to individuals** - Only use ensemble if it improves performance
5. **Mean ensemble** is a good default
6. **Validate improvement** - Don't assume ensembles always help

Ensembles frequently outperform individual models, but always validate through resampling before committing to an ensemble approach.
