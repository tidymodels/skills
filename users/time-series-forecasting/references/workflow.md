# Time Series Forecasting Workflow

Complete 8-step workflow for forecasting time series data with modeltime.

## Overview

This workflow guides you through the complete process of time series
forecasting, from data splitting to final predictions. Each step builds on the
previous one, and all model development happens on the training data using
resampling—the test set is reserved for final validation only.

## Step 1: Train-Test Split

Always partition data into:

- **Training set**: Used for all feature engineering, feature selection, and
  model development

- **Test set**: Reserved for final model evaluation only—requires explicit user
  permission before use

Ask the user how much data should be used in the test set before proceeding.

### Implementation

```r
# Set seed before splitting for reproducibility
set.seed(5847)
init_split <- initial_time_split(data, prop = 0.9)
train_data <- training(init_split)
test_data <- testing(init_split)
```

### Test Set Rules

- **NEVER** predict on test data during model development

- **NEVER** calculate test set metrics without explicit user permission

- **NEVER** use test data to compare models (use backtesting instead)

- **NEVER** use test data to tune hyperparameters (use resampling instead)

- **DO** ask: *"I've completed model development using backtesting on the
  training data. [Summarize top models with resampling performance]. May I
  evaluate the final model on the test set?"*

- **DO** wait for explicit confirmation before proceeding

**Self-check**: If you're writing `predict(..., test_data)` or
`modeltime_calibrate(new_data = test_data)` without prior user permission,
STOP—you're making an error.

**Exception**: Basic verification after splitting (e.g., `nrow(test_data)`,
`glimpse(test_data)`) to confirm the split worked.

**Key Principle**: Use resampling/backtesting on training data for ALL model
comparisons. The test set is only for final validation of your best model, not
for iterative development.

## Step 2: Create & Fit Models

See [models.md](models.md) for detailed information on available models and when
to use them.

### Modeltime Models

Modeltime models can use the date variable directly in the formula:

```r
# ARIMA
arima_fit <- arima_reg() |>
  set_engine("auto_arima") |>
  fit(value ~ date, data = train_data)

# Exponential Smoothing
ets_fit <- exp_smoothing() |>
  set_engine("ets") |>
  fit(value ~ date, data = train_data)

# Prophet
prophet_fit <- prophet_reg() |>
  set_engine("prophet") |>
  fit(value ~ date, data = train_data)
```

### Parsnip Models

Parsnip models require date derivatives, not raw dates. See
[feature-engineering.md](feature-engineering.md) for details.

```r
# Linear regression with simple date features
simple_rec <- recipe(value ~ date, data = train_data) |>
  step_holiday(date) |>
  step_date(date, features = c("dow", "month", "year")) |>
  step_mutate(date = as.numeric(date))

lm_fit <- workflow(simple_rec, linear_reg()) |>
  fit(train_data)

# XGBoost via workflow with recipe
signature_rec <- recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>
  step_rm(matches("(.iso$)|(.xts$)")) |>
  step_dummy(all_nominal())

xgb_fit <- workflow() |>
  add_recipe(signature_rec) |>
  add_model(boost_tree() |> set_engine("xgboost")) |>
  fit(train_data)
```

## Step 3: Create Modeltime Table

Combine all fitted models into a modeltime table for easy comparison:

```r
models_tbl <- modeltime_table(
  arima_fit,
  ets_fit,
  prophet_fit,
  lm_fit,
  xgb_fit
)
```

The modeltime table provides a unified interface for resampling, calibration,
and forecasting across different model types.

## Step 4: Resampling / Backtesting

See [resampling.md](resampling.md) for complete details on time series
cross-validation.

**Important:** Resampling is your PRIMARY tool for comparing models—not the test
set. Use backtesting to compare algorithms, evaluate tuning parameters, and
choose feature engineering approaches. Only use the test set for final
validation after making all decisions.

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

models_tbl |>
  modeltime_fit_resamples(resamples = resamples) |>
  modeltime_resample_accuracy(summary_fns = list(mean = mean, sd = sd))
```

## Step 5: Tuning (Optional)

See [tuning.md](tuning.md) for details on hyperparameter tuning.

Offer to tune the hyperparameters of complex models (e.g., XGBoost).

**Remember to set a seed before tuning for reproducibility:**

```r
set.seed(5847)
# Then proceed with tune_grid() or other tuning functions
```

## Step 6: Test Set Evaluation (Optional)

**Before proceeding:** Review the Test Set Rules in Step 1. You must ask for
explicit permission before using the test set.

```r
# Only after getting explicit user permission:
calibration_tbl <- models_tbl |>
  modeltime_calibrate(new_data = test_data)
```

## Step 7: Report Performance (Optional)

```r
# Accuracy metrics (on test set if calibrated, or on resamples)
calibration_tbl |> modeltime_accuracy()

# Visualize forecasts
calibration_tbl |>
  modeltime_forecast(new_data = test_data, actual_data = data) |>
  plot_modeltime_forecast()
```

**Remember:** After using the test set, do not return to model development.

## Step 8: Refit & Forecast

Always refit on the full dataset before producing final forecasts:

```r
# Refit to full data, then forecast future
calibration_tbl |>
  modeltime_refit(data = data) |>
  modeltime_forecast(h = "12 months", actual_data = data) |>
  plot_modeltime_forecast()
```

**Why refit?**

- Uses all available data for the final model

- Produces the most accurate future forecasts

- Standard practice in time series forecasting

## Summary

The workflow emphasizes:

1. **Proper data spending** - Test set reserved for final validation
2. **Reproducibility** - Seeds set before all random operations
3. **Model comparison via resampling** - Not test set
4. **Multiple model approaches** - Classical and ML methods
5. **Refitting on full data** - Before final forecasting

See the related reference files for detailed guidance on each component.
