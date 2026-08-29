# Time Series Models

Complete guide to available models in the modeltime ecosystem and when to use
them.

## Model Selection Strategy

**No single model is best for all time series.** The optimal approach depends
on:

- Data characteristics (trend, seasonality, noise)

- Forecast horizon (short-term vs long-term)

- Available predictors (univariate vs multivariate)

- Interpretability requirements

**Recommended approach:**

1. **Start with a baseline ensemble** of classical methods
2. **Add ML models** if you have external predictors or complex patterns
3. **Compare using backtesting**, not the test set
4. **Consider ensembles** to combine strengths of multiple models

## Available Models

| Function          | Method             | Engine               | Best For                          |
| ----------------- | ------------------ | -------------------- | --------------------------------- |
| `arima_reg()`     | ARIMA              | `auto_arima`         | Trend, short-term seasonality     |
| `arima_boost()`   | ARIMA + XGBoost    | `auto_arima_xgboost` | ARIMA + external predictors       |
| `exp_smoothing()` | ETS                | `ets`                | Strong seasonal patterns          |
| `prophet_reg()`   | Prophet            | `prophet`            | Multiple seasonality, holidays    |
| `prophet_boost()` | Prophet + XGBoost  | `prophet_xgboost`    | Prophet + external predictors     |
| `linear_reg()`    | Linear/Elastic Net | `lm`, `glmnet`       | Simple trends with predictors     |
| `mars()`          | MARS               | `earth`              | Non-linear relationships          |
| `boost_tree()`    | XGBoost            | `xgboost`            | Complex patterns, many predictors |
| `rand_forest()`   | Random Forest      | `ranger`             | Non-linear patterns               |

## Classical Time Series Models

These models work directly with date variables and don't require feature
engineering.

### ARIMA (`arima_reg()`)

**When to use:**

- Univariate time series with trend

- Short to medium forecast horizons

- Stationary or easily made stationary data

**Strengths:**

- Automatic model selection with `auto_arima`

- Handles trend and short-term seasonality

- Well-understood statistical properties

- Fast to fit

**Limitations:**

- Struggles with long seasonal periods

- Cannot incorporate external predictors (use `arima_boost()` instead)

**Example:**

```r
arima_fit <- arima_reg() |>
  set_engine("auto_arima") |>
  fit(value ~ date, data = train_data)
```

### Exponential Smoothing (`exp_smoothing()`)

**When to use:**

- Strong seasonal patterns

- Data without complex non-linear trends

- When you need prediction intervals

**Strengths:**

- Excellent for seasonal data

- Automatically selects best ETS model

- Robust to outliers

- Fast to fit

**Limitations:**

- Cannot incorporate external predictors

- May struggle with irregular patterns

**Example:**

```r
ets_fit <- exp_smoothing() |>
  set_engine("ets") |>
  fit(value ~ date, data = train_data)
```

**Note:** ETS often excels on seasonal data and is a strong baseline.

### Prophet (`prophet_reg()`)

**When to use:**

- Multiple seasonal patterns (daily, weekly, yearly)

- Data with holidays or special events

- Missing data or outliers

- Business data with human-scale seasonality

**Strengths:**

- Handles multiple seasonality automatically

- Robust to missing data and outliers

- Holiday effects built-in

- Works well with minimal tuning

**Limitations:**

- Can be slower than ARIMA/ETS

- May overfit on small datasets

- Less interpretable than ARIMA/ETS

**Example:**

```r
prophet_fit <- prophet_reg() |>
  set_engine("prophet") |>
  fit(value ~ date, data = train_data)
```

## Hybrid Models

Combine classical time series models with machine learning.

### ARIMA + XGBoost (`arima_boost()`)

ARIMA for the temporal pattern + XGBoost for external predictors.

**When to use:**

- You have external predictors

- Temporal patterns + additional signals

**Example:**

```r
# Requires external predictors in formula
arima_boost_fit <- arima_boost() |>
  set_engine("auto_arima_xgboost") |>
  fit(value ~ date + predictor1 + predictor2, data = train_data)
```

### Prophet + XGBoost (`prophet_boost()`)

Prophet for seasonality/trend + XGBoost for external predictors.

**When to use:**

- Multiple seasonality + external predictors

- Complex patterns with additional signals

**Example:**

```r
prophet_boost_fit <- prophet_boost() |>
  set_engine("prophet_xgboost") |>
  fit(value ~ date + predictor1 + predictor2, data = train_data)
```

## Machine Learning Models

These require feature engineering from dates. See
[feature-engineering.md](feature-engineering.md) for details.

### Linear Regression / Elastic Net

**When to use:**

- Simple linear trends

- Need interpretable coefficients

- Many correlated predictors (use elastic net)

**Requires:** Date features via recipes

**Example:**

```r
rec <- recipe(value ~ date, data = train_data) |>
  step_holiday(date) |>
  step_date(date, features = c("dow", "month", "year")) |>
  step_mutate(date = as.numeric(date))

lm_fit <- workflow(rec, linear_reg()) |>
  fit(train_data)
```

### XGBoost (`boost_tree()`)

**When to use:**

- Complex non-linear patterns

- Many external predictors

- Interactions between predictors

- When you need high accuracy

**Strengths:**

- Handles non-linear relationships

- Automatic interaction detection

- Often produces best accuracy

**Limitations:**

- Requires careful feature engineering

- Less interpretable

- Can overfit without proper tuning

**Requires:** Date features via recipes (often `step_timeseries_signature()`)

**Example:**

```r
rec <- recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>
  step_rm(matches("(.iso$)|(.xts$)")) |>
  step_dummy(all_nominal())

xgb_fit <- workflow(rec, boost_tree() |> set_engine("xgboost")) |>
  fit(train_data)
```

### Random Forest (`rand_forest()`)

**When to use:**

- Non-linear patterns

- Want more interpretability than XGBoost

- Less prone to overfitting than XGBoost

**Requires:** Date features via recipes

**Example:**

```r
rec <- recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>
  step_rm(matches("(.iso$)|(.xts$)")) |>
  step_dummy(all_nominal())

rf_fit <- workflow(rec, rand_forest() |> set_engine("ranger")) |>
  fit(train_data)
```

## Baseline Model Recommendations

**For most time series, start with this baseline ensemble:**

1. **ARIMA** (`arima_reg()`) - Handles trend and short-term seasonality
2. **ETS** (`exp_smoothing()`) - Excellent for seasonal data
3. **Prophet** (`prophet_reg()`) - Robust to outliers and missing data

These three models:

- Cover different modeling approaches

- Don't require feature engineering

- Are fast to fit

- Often produce competitive results

**Then add ML models if:**

- You have external predictors

- Baseline ensemble is insufficient

- Data has complex patterns

- You need to model interactions

## Model Selection Process

1. **Fit baseline models** (ARIMA, ETS, Prophet)
2. **Evaluate using backtesting** (not test set) - see
   [resampling.md](resampling.md)
3. **Add ML models** if needed (XGBoost, Random Forest)
4. **Compare performance** on resampling metrics (RMSE, MAE)
5. **Consider ensembles** - see [ensembles.md](ensembles.md)
6. **Select final model(s)** based on backtesting performance
7. **Evaluate on test set** (with user permission) for final validation

## Comparison Tips

**Use backtesting metrics to compare:**

- **RMSE**: Primary metric for forecast accuracy (sensitive to large errors)

- **MAE**: Less sensitive to outliers

- **MAPE**: Percentage error (avoid if data has zeros)

**Consider:**

- **Forecast horizon**: Some models better for short vs long-term

- **Computational cost**: Classical models are faster than ML

- **Interpretability**: Classical models more interpretable

- **Ensemble potential**: Different model types often ensemble well

## Date Handling Summary

**Modeltime models** (ARIMA, ETS, Prophet):

- Accept `value ~ date` directly

- Handle temporal patterns automatically

- No feature engineering required

**Parsnip models** (linear, XGBoost, RF):

- Need date converted to features

- Use recipes with `step_timeseries_signature()`, `step_date()`, etc.

- More flexible but require more setup

See [feature-engineering.md](feature-engineering.md) for complete guide to date
feature engineering.
