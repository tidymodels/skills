# Time Series Feature Engineering

Complete guide to engineering features from date variables for machine learning models.

## When Feature Engineering is Needed

### Modeltime Models: No Feature Engineering Required

Classical time series models accept date variables directly:

```r
# ARIMA, ETS, Prophet - use date directly
arima_fit <- arima_reg() |>
  set_engine("auto_arima") |>
  fit(value ~ date, data = train_data)
```

**No feature engineering needed for:**

- `arima_reg()`
- `exp_smoothing()`
- `prophet_reg()`
- `arima_boost()` (but external predictors can be included)
- `prophet_boost()` (but external predictors can be included)

### Parsnip Models: Feature Engineering Required

Machine learning models cannot use raw dates and need derived features:

```r
# XGBoost, Random Forest, Linear - need date features
rec <- recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>  # Create date features
  step_rm(matches("(.iso$)|(.xts$)")) |>
  step_dummy(all_nominal())

xgb_fit <- workflow(rec, boost_tree()) |>
  fit(train_data)
```

**Feature engineering required for:**

- `linear_reg()`
- `boost_tree()`
- `rand_forest()`
- `mars()`
- Any parsnip model

## Feature Engineering Approaches

### Approach 1: Simple Date Features

**Best for:** Linear models, interpretable models, limited data

```r
recipe(value ~ date, data = train_data) |>
  step_holiday(date) |>  # US holidays (0/1 indicators)
  step_date(date, features = c("dow", "month", "year")) |>  # Day of week, month, year
  step_mutate(date = as.numeric(date))  # Linear time trend
```

**Creates:**

- `date_dow` - Day of week (factor: Mon-Sun)
- `date_month` - Month (factor: Jan-Dec)
- `date_year` - Year (numeric)
- Holiday indicators (numeric: 0/1)
- Linear time trend (numeric)

**When to use:**

- Linear regression
- Simple patterns
- Need interpretability
- Limited training data

### Approach 2: Time Series Signature

**Best for:** Tree-based models (XGBoost, Random Forest), complex patterns

```r
recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>  # Create many date features
  step_rm(matches("(.iso$)|(.xts$)")) |>  # Remove unhelpful features
  step_dummy(all_nominal())  # Convert factors to dummies
```

**Creates 20+ features including:**

- `date_index.num` - Numeric index
- `date_year`
- `date_month` - Month number
- `date_month.lbl` - Month label (factor)
- `date_day`
- `date_wday` - Weekday number
- `date_wday.lbl` - Weekday label (factor)
- `date_hour`, `date_minute`, `date_second` (if timestamp)
- `date_week`, `date_quarter`
- Many more...

**Why remove `.iso` and `.xts` features?**

- These are redundant representations
- Can cause issues with some models
- Standard practice to remove them

**When to use:**

- XGBoost, Random Forest
- Complex seasonal patterns
- Many observations (handles many features)
- Don't need interpretability

### Approach 3: Fourier Terms

**Best for:** Modeling seasonality with smooth periodic functions

```r
recipe(value ~ date, data = train_data) |>
  step_fourier(date, K = 3, period = 12) |>  # 3 sine/cosine pairs for monthly seasonality
  step_date(date, features = c("year")) |>
  step_mutate(date = as.numeric(date))
```

**Parameters:**

- `K` - Number of sine/cosine pairs (higher = more flexible)
- `period` - Length of seasonal cycle (12 for monthly data with yearly seasonality)

**Creates:** `K * 2` features (sine and cosine pairs)

**When to use:**

- Strong seasonal patterns
- Linear or regularized models
- Want smooth seasonal effects
- Limited data (fewer features than time series signature)

### Approach 4: Combined Features

**Best for:** Complex patterns with multiple seasonal periods

```r
recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>  # Comprehensive date features
  step_fourier(date, K = 3, period = 12) |>  # Yearly seasonality
  step_rm(matches("(.iso$)|(.xts$)")) |>  # Remove redundant features
  step_normalize(matches("(index.num$)|(_year$)")) |>  # Scale numeric features
  step_dummy(all_nominal())  # Convert factors to dummies
```

**When to use:**

- Very complex patterns
- Tree-based models (handle many features well)
- Plenty of training data
- Want maximum flexibility

## Feature Preprocessing Steps

### Normalization

```r
step_normalize(matches("(index.num$)|(_year$)"))
```

**When to use:**

- Linear models (required)
- Elastic net (required)
- Neural networks (required)
- **Not needed** for tree-based models (XGBoost, Random Forest)

**Why?** Linear models are sensitive to feature scales. Normalization puts all features on the same scale.

### Dummy Encoding

```r
step_dummy(all_nominal())
```

**When to use:**

- All parsnip models (required for factors)
- Converts factors (day of week, month names) to numeric dummies

**Why?** Most ML models require numeric inputs.

### Removing Redundant Features

```r
step_rm(matches("(.iso$)|(.xts$)"))
```

**When to use:**

- After `step_timeseries_signature()`
- Removes ISO week and xts-specific features that are redundant

## Recommendations by Model Type

### Linear Regression / Elastic Net

```r
recipe(value ~ date, data = train_data) |>
  step_holiday(date) |>
  step_date(date, features = c("dow", "month", "year")) |>
  step_fourier(date, K = 3, period = 12) |>  # If seasonal
  step_normalize(all_numeric_predictors()) |>  # Required
  step_dummy(all_nominal())
```

**Why:**

- Few interpretable features
- Fourier for smooth seasonality
- Normalization required for linear models

### XGBoost

```r
recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>
  step_rm(matches("(.iso$)|(.xts$)")) |>
  step_dummy(all_nominal())
```

**Why:**

- Handles many features well
- No normalization needed
- Automatically finds interactions

### Random Forest

```r
recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>
  step_rm(matches("(.iso$)|(.xts$)")) |>
  step_dummy(all_nominal())
```

**Why:**

- Same as XGBoost
- Handles many features
- No normalization needed

## External Predictors

If you have external predictors (temperature, promotions, etc.):

```r
recipe(value ~ date + temp + promo, data = train_data) |>
  step_timeseries_signature(date) |>
  step_rm(matches("(.iso$)|(.xts$)")) |>
  # Handle external predictors
  step_normalize(all_of(c("temp"))) |>  # If numeric
  step_dummy(all_of(c("promo"))) |>  # If factor
  step_dummy(all_nominal())  # Any remaining factors
```

**Important:** External predictors must be available for the entire forecast horizon.

## Feature Engineering Rules

- **NEVER** use data outside the training set to determine feature engineering steps
- **NEVER** engineer features, then evaluate directly on training data
- **DO** treat feature engineering and model training as a single process (use workflows)
- **DO** use resampling to measure combined feature engineering + model performance

## Common Patterns

### Daily Data with Weekly Seasonality

```r
recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>
  step_fourier(date, K = 3, period = 7) |>  # Weekly pattern
  step_rm(matches("(.iso$)|(.xts$)")) |>
  step_dummy(all_nominal())
```

### Monthly Data with Yearly Seasonality

```r
recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>
  step_fourier(date, K = 3, period = 12) |>  # Yearly pattern
  step_rm(matches("(.iso$)|(.xts$)")) |>
  step_dummy(all_nominal())
```

### Hourly Data with Daily and Weekly Patterns

```r
recipe(value ~ date, data = train_data) |>
  step_timeseries_signature(date) |>
  step_fourier(date, K = 3, period = 24) |>   # Daily pattern
  step_fourier(date, K = 2, period = 24*7) |> # Weekly pattern
  step_rm(matches("(.iso$)|(.xts$)")) |>
  step_dummy(all_nominal())
```

## Summary

**Key decisions:**

1. **Does your model need features?**
   - Classical models (ARIMA, ETS, Prophet): No
   - ML models (XGBoost, RF, Linear): Yes

2. **Which approach?**
   - Simple patterns or linear models: `step_date()` + `step_fourier()`
   - Complex patterns or tree models: `step_timeseries_signature()`

3. **Preprocessing?**
   - Linear models: Normalize
   - Tree models: No normalization needed
   - All models: `step_dummy()` for factors

4. **Always use workflows** to bundle recipe + model for proper evaluation
