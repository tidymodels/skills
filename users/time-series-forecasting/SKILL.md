---
name: time-series-forecasting
description: Forecasts time series data using the modeltime ecosystem in R. Supports ARIMA, ETS, Prophet, XGBoost, and ensemble methods. Use when users need to forecast, predict future values, or model time-dependent data with tidymodels workflows.
author: Based off documentation files created by Matt Dancho
---

# Time Series Forecasting with Modeltime

## Core Packages

```r
library(tidymodels)
library(modeltime)
library(timetk)
library(tidyverse)
```

Optional extensions: `modeltime.ensemble`, `modeltime.resample`, `modeltime.gluonts`, `modeltime.h2o`

## 6-Step Workflow

### 1. Train-Test Split

Always partition data into:

- **Training set**: Used for all feature engineering, feature selection, and model development
- **Test set**: Reserved for final evaluation only—maximum 1-2 uses with explicit user permission

Ask the user how much data should be used in the test set before proceeding. 

Using modeltime: 

```r
init_split <- initial_time_split(data, prop = 0.9)
train_data <- training(init_split)
test_data <- testing(init_split)
```

### Test Set Discipline

**The test set may be used AT MOST TWICE in the entire analysis:**

1. **First use (optional)**: Evaluate 2-3 final candidate models to select the best one
2. **Second use (optional)**: Report final performance metrics for the selected model

**After using the test set, you MUST NOT return to model development.**

---

#### What You MUST Do

**Before ANY test set use:**
1. Complete all model development using training data + resampling
2. Ask for explicit permission using the prompts below
3. Track usage count (1 of 2, or 2 of 2)

**Permission prompt templates:**

*Before first use:*
> "I've completed model development using backtesting on the training data. [Summarize top 2-3 models with resampling performance]. May I evaluate these on the test set to select the final model? (**Test set use 1 of 2**)"

*Before second use:*
> "May I evaluate the final [model name] on the test set to report performance metrics? (**Test set use 2 of 2—final use**)"

---

#### What You MUST NEVER Do

- ❌ Predict on test data during model development
- ❌ Use test data without explicit user permission
- ❌ Use test data to compare models (use resampling instead)
- ❌ Use test data to tune hyperparameters (use resampling instead)
- ❌ Touch the test set more than twice
- ❌ Return to model development after using the test set

---

#### Self-Checks

**Before writing `test_data` in any code:**
- [ ] Have I completed all model development?
- [ ] Have I asked for user permission?
- [ ] How many times have I used the test set? (Must be < 2)
- [ ] If I'm tempted to use it a 3rd time → STOP and explain to user that test set is exhausted

**Exception:** Basic verification after splitting (e.g., `nrow(test_data)`, `glimpse(test_data)`) is allowed.

---

#### Key Principle

**Use resampling/backtesting on training data for ALL model comparisons.** The test set is only for final validation of your best model(s), not for iterative development.

### 2. Create & Fit Models

**Modeltime models** (date in formula):

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

**Parsnip models** (use date derivatives, not raw date):

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

### 3. Create Modeltime Table

```r
models_tbl <- modeltime_table(
  arima_fit,
  ets_fit,
  prophet_fit,
  lm_fit,
  xgb_fit
)
```

### 4 Resampling / Backtesting

- **NEVER** use data outside the training set to determine feature engineering steps
- **NEVER** engineer features, then evaluate directly on training data
- **DO** treat feature engineering and model training as a single process
- **DO** use resampling to measure combined feature engineering + model performance
- **DO** use resampling to select best tuning parameters
- **DO** ask the users how much data to use to assess the model and suggest the same size as the test set.

**Important:** Resampling is your PRIMARY tool for comparing models—not the test set. Use backtesting to compare algorithms, evaluate tuning parameters, and choose feature engineering approaches. Only use the test set for final validation after making all decisions.

```r
library(modeltime.resample)

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

### 5. Tuning

Offer to tune the hyperparameters of complex models (e.g., xgboost). 

Use a space-filling grid, preferably by passing an integer to the `grid` argument. If not, you must use `grid_space_filling()` to create the grid. 

#### Parallel Processing

Before proposing potentially long-running computations, like resampling or model fitting, first use `parallel::detectCores()` to determine the maximum number of cores available, then ask the user if they would like to use parallel processing and, if so, how many cores you are allowed to use. Keep using the extra cores throughout the work unless the user asks you to stop.

When computing statistics over a large number of columns, use the future package to parallelize these computations. Do not use the parallel, mirai, or foreach packages for parallel execution. 

When using tidymodels functions, such as `tune::tune_grid()`, ask about parallel processing and use the future package to create local workers. 

### 6. Test Set Evaluation (Optional)

**Before proceeding:** Review the Test Set Discipline rules in Section 1. You must ask for explicit permission using the prompt templates provided, tracking whether this is use 1 of 2 or 2 of 2.

```r
# Only after getting explicit permission and announcing which use (1 of 2 or 2 of 2):
calibration_tbl <- models_tbl |>
  modeltime_calibrate(new_data = test_data)
```

### 7. Report Performance (Optional)

```r
# Accuracy metrics (on test set if calibrated, or on resamples)
calibration_tbl |> modeltime_accuracy()

# Visualize forecasts
calibration_tbl |>
  modeltime_forecast(new_data = test_data, actual_data = data) |>
  plot_modeltime_forecast()
```

**Remember:** After using the test set, do not return to model development.

### 8. Refit & Forecast

```r
# Refit to full data, then forecast future
calibration_tbl |>
  modeltime_refit(data = data) |>
  modeltime_forecast(h = "12 months", actual_data = data) |>
  plot_modeltime_forecast()
```

## Available Models

| Function | Method | Engine |
|----------|--------|--------|
| `arima_reg()` | ARIMA | `auto_arima` |
| `arima_boost()` | ARIMA + XGBoost | `auto_arima_xgboost` |
| `exp_smoothing()` | ETS | `ets` |
| `prophet_reg()` | Prophet | `prophet` |
| `prophet_boost()` | Prophet + XGBoost | `prophet_xgboost` |
| `linear_reg()` | Linear/Elastic Net | `lm`, `glmnet` |
| `mars()` | MARS | `earth` |
| `boost_tree()` | XGBoost | `xgboost` |
| `rand_forest()` | Random Forest | `ranger` |

## Feature Engineering

Use `timetk` with recipes:

```r
recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>         
  step_fourier(date, K = 3, period = 12) |>  
  step_rm(matches("(.iso$)|(.xts$)")) |>     
  step_normalize(matches("(index.num$)|(_year$)")) |>
  step_dummy(all_nominal())
```

## Ensembles

```r
library(modeltime.ensemble)

# Average ensemble
ensemble_fit <- calibration_tbl |>
  ensemble_average(type = "mean")

# Evaluate ensemble using RESAMPLING (not test set)
modeltime_table(ensemble_fit) |>
  modeltime_fit_resamples(resamples = resamples) |>
  modeltime_resample_accuracy()

# Only evaluate on test set if you have user permission and haven't exceeded 2 uses
```

## Key Guidance

- **Date handling**: Modeltime models accept `value ~ date`. Parsnip models need date converted to numeric/factors via recipes.
- **Refitting**: Always `modeltime_refit()` on full data before forecasting future periods.
- **Confidence intervals**: Generated from calibration residuals; require calibration step.
- **Model selection**: No single best model—compare multiple approaches. ETS often excels on seasonal data; ensembles frequently outperform individuals.
