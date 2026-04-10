---
name: time-series-forecasting
description: Forecasts time series data using the modeltime ecosystem in R.
  Supports ARIMA, ETS, Prophet, XGBoost, and ensemble methods. Use when users
  need to forecast, predict future values, or model time-dependent data with
  tidymodels workflows.
---

# Time Series Forecasting with Modeltime

This skill guides the process of forecasting time series data using the
modeltime ecosystem in R.

## Overview

Time series forecasting requires special handling to respect temporal ordering
and prevent data leakage. This skill provides:

- **Proper data splitting** for time series (temporal train/test)

- **Backtesting** with time series cross-validation (not random CV)

- **Model variety** from classical (ARIMA, ETS, Prophet) to ML (XGBoost, Random
  Forest)

- **Feature engineering** for date variables

- **Ensemble methods** to combine model strengths

- **Test set protection** to ensure valid evaluation

## Core Packages

```r
library(tidymodels)
library(modeltime)
library(timetk)
library(tidyverse)
```

Optional extensions: `modeltime.ensemble`, `modeltime.resample`,
`modeltime.gluonts`, `modeltime.h2o`

## Quick Start

### Basic Workflow

1. **Split data** using `initial_time_split()` (temporal split)
2. **Fit multiple models** (ARIMA, ETS, Prophet, XGBoost)
3. **Create modeltime table** to organize models
4. **Backtest with `time_series_cv()`** - never use random CV
5. **Compare models** using backtesting metrics (not test set)
6. **Optionally tune** hyperparameters for ML models
7. **Evaluate on test set** (with user permission) for final validation
8. **Refit on full data** and forecast future periods

See [references/workflow.md](references/workflow.md) for the complete 8-step
workflow.

### Model Selection

**Start with a baseline ensemble:**

- ARIMA (`arima_reg()`) - Trend and seasonality

- ETS (`exp_smoothing()`) - Strong for seasonal data

- Prophet (`prophet_reg()`) - Robust, handles holidays

**Add ML models if needed:**

- XGBoost (`boost_tree()`) - Complex patterns, external predictors

- Random Forest (`rand_forest()`) - Non-linear patterns

See [references/models.md](references/models.md) for detailed model guidance and
selection strategy.

## Critical Principles

### 1. Reproducibility

**Always set a random seed before any operation that involves randomness:**

- **Before data splitting** - Set seed immediately before `initial_time_split()`

- **Before resampling** - Set seed immediately before `time_series_cv()`

- **Before tuning** - Set seed before `tune_grid()` or other tuning functions

**Good seed practices:**

- Use a random integer between 1000 and 10000 (e.g., 3847, 7291, 5628)

- Avoid common values like 123, 42, 111, 999

- Document your seed choice in comments

### 2. Test Set Protection

**The test set is reserved for final validation only.**

- **NEVER** predict on test data during model development

- **NEVER** use test data to compare models (use backtesting instead)

- **NEVER** use test data to tune hyperparameters (use resampling instead)

- **DO** ask for explicit permission: *"I've completed model development using
  backtesting. May I evaluate the final model on the test set?"*

- **DO** wait for user confirmation before proceeding

**Self-check**: If you're writing `modeltime_calibrate(new_data = test_data)`
without prior user permission, STOP—you're making an error.

**Exception**: Basic verification after splitting (e.g., `nrow(test_data)`) to
confirm the split worked.

### 3. Temporal Ordering

**Never use random cross-validation for time series.**

Random CV shuffles data, which:

- Violates temporal ordering

- Creates data leakage (trains on future, tests on past)

- Produces optimistically biased estimates

**Always use `time_series_cv()`** which:

- Respects temporal ordering

- Trains only on past data

- Tests on future data (realistic scenario)

See [references/resampling.md](references/resampling.md) for complete details.

## Reference Documentation

**Core Concepts:**

- [Complete Workflow](references/workflow.md) - 8-step process from split to
  forecast

- [Available Models](references/models.md) - When to use ARIMA, ETS, Prophet,
  XGBoost, etc.

- [Time Series Resampling](references/resampling.md) - Backtesting with
  `time_series_cv()`

**Advanced Topics:**

- [Feature Engineering](references/feature-engineering.md) - Creating date
  features for ML models

- [Hyperparameter Tuning](references/tuning.md) - Tuning XGBoost, Random Forest,
  etc.

- [Ensemble Methods](references/ensembles.md) - Combining models for better
  performance

## Parallel Processing

Before starting computationally intensive work (resampling, tuning, model
fitting):

1. **Detect available cores**: `parallel::detectCores()`
2. **Ask the user in the conversation** - Don't just add a comment in code

**Example interaction:**

> **You:** I'm about to run time series cross-validation with 4 slices. I can
> use parallel processing to speed this up significantly.
>
> I see you have 8 cores available. Would you like me to use parallel
> processing? If so, how many cores should I use? (I'd recommend using 6-7 to
> leave 1-2 cores free for other processes)

**If user says yes:**

```r
library(future)
plan("multisession", workers = 6)  # or whatever they specified
```

**If user says no:** Proceed sequentially (no future setup)

**Continue using** the same parallel configuration throughout unless the user
asks to stop.

**Important:** Only use the `future` package for parallel processing. Do not use
`parallel`, `mirai`, or `foreach`.

See [references/tuning.md](references/tuning.md) for complete parallel
processing guidance.

## Key Guidance

**Date handling:**

- Modeltime models (ARIMA, ETS, Prophet) accept `value ~ date` directly

- Parsnip models (XGBoost, RF, Linear) need date features via recipes

- See [references/feature-engineering.md](references/feature-engineering.md)

**Model comparison:**

- Use backtesting (resampling) to compare models, NOT the test set

- RMSE is the primary metric (penalizes large errors)

- Consider ensembles when multiple models perform well

- See [references/ensembles.md](references/ensembles.md)

**Refitting:**

- Always `modeltime_refit()` on full data before forecasting future periods

- This uses all available information for the final forecast

**Confidence intervals:**

- Generated from calibration residuals

- Require the calibration step (`modeltime_calibrate()`)

## Example: Quick Forecast

```r
# Set seed for reproducibility
set.seed(5847)

# 1. Split data (temporal split)
splits <- initial_time_split(data, prop = 0.9)
train_data <- training(splits)
test_data <- testing(splits)

# 2. Fit baseline models
arima_fit <- arima_reg() |> set_engine("auto_arima") |>
  fit(value ~ date, data = train_data)

ets_fit <- exp_smoothing() |> set_engine("ets") |>
  fit(value ~ date, data = train_data)

prophet_fit <- prophet_reg() |> set_engine("prophet") |>
  fit(value ~ date, data = train_data)

# 3. Create modeltime table
models_tbl <- modeltime_table(arima_fit, ets_fit, prophet_fit)

# 4. Backtest with time series CV
set.seed(5847)
resamples <- time_series_cv(
  train_data,
  initial = "2 years",
  assess = "6 months",
  skip = "3 months",
  slice_limit = 4
)

models_tbl |>
  modeltime_fit_resamples(resamples) |>
  modeltime_resample_accuracy()

# 5. [After user permission] Evaluate on test set
calibration_tbl <- models_tbl |>
  modeltime_calibrate(test_data)

calibration_tbl |> modeltime_accuracy()

# 6. Refit on full data and forecast
calibration_tbl |>
  modeltime_refit(data) |>
  modeltime_forecast(h = "12 months", actual_data = data) |>
  plot_modeltime_forecast()
```

## Getting Started

New to time series forecasting? Start with these steps:

1. Read [references/workflow.md](references/workflow.md) for the complete
   process
2. Review [references/models.md](references/models.md) to understand model
   options
3. Study [references/resampling.md](references/resampling.md) to learn why
   temporal ordering matters
4. Refer to other references as needed for advanced topics

The references provide detailed guidance, examples, and best practices for each
component of the forecasting workflow.
