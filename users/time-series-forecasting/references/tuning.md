# Hyperparameter Tuning for Time Series

Complete guide to tuning hyperparameters for time series forecasting models.

## When to Tune

**Offer to tune hyperparameters for complex models:**

- XGBoost (`boost_tree()`)
- Random Forest (`rand_forest()`)
- Elastic Net (`linear_reg()` with `glmnet` engine)
- MARS (`mars()`)

**Generally don't need tuning:**

- ARIMA (`arima_reg()`) - Uses `auto_arima` which selects parameters automatically
- ETS (`exp_smoothing()`) - Automatically selects best model
- Prophet (`prophet_reg()`) - Works well with defaults

## Tuning Workflow

### Step 1: Define Model with Tuning Parameters

```r
xgb_spec <- boost_tree(
  trees = tune(),
  tree_depth = tune(),
  learn_rate = tune(),
  min_n = tune()
) |>
  set_engine("xgboost") |>
  set_mode("regression")
```

### Step 2: Create Workflow

```r
xgb_wf <- workflow() |>
  add_recipe(signature_rec) |>
  add_model(xgb_spec)
```

### Step 3: Create Tuning Grid

**Use space-filling designs** for better coverage of parameter space.

```r
# Preferred: Pass integer for automatic space-filling grid
xgb_grid <- 20  # Creates 20 parameter combinations

# Alternative: Explicit space-filling grid
xgb_grid <- grid_space_filling(
  trees = trees(),
  tree_depth = tree_depth(),
  learn_rate = learn_rate(),
  min_n = min_n(),
  size = 20
)
```

### Step 4: Set Up Resampling

```r
# Set seed for reproducibility
set.seed(5847)

resamples <- time_series_cv(
  data = train_data,
  initial = "2 years",
  assess = "6 months",
  skip = "3 months",
  slice_limit = 4
)
```

### Step 5: Check Parallel Processing

Before running potentially long computations, ask about parallel processing.

**Detect available cores:**

```r
parallel::detectCores()
```

**Ask the user in the conversation:**

> "I'm about to run hyperparameter tuning with time series cross-validation. This could take a while. I see you have 8 cores available. Would you like me to use parallel processing to speed this up? If so, how many cores should I use? (I'd recommend using 6-7 to leave 1-2 cores free for other processes)"

**If user says yes:**

```r
library(future)
plan("multisession", workers = 6)  # or whatever they specified
```

**If user says no or doesn't respond:**

```r
# Proceed with sequential processing (no future setup)
```

**Continue using the same parallel configuration** throughout unless the user asks to stop.

### Step 6: Tune

```r
# Set seed before tuning for reproducibility
set.seed(5847)

xgb_tuned <- tune_grid(
  xgb_wf,
  resamples = resamples,
  grid = xgb_grid,
  metrics = metric_set(rmse, mae),
  control = control_grid(save_pred = TRUE)
)
```

### Step 7: Evaluate Results

```r
# View best results
show_best(xgb_tuned, metric = "rmse", n = 5)

# Visualize tuning results
autoplot(xgb_tuned)
```

### Step 8: Select Best Parameters

```r
best_params <- select_best(xgb_tuned, metric = "rmse")

# Finalize workflow with best parameters
final_wf <- finalize_workflow(xgb_wf, best_params)

# Fit on full training data
final_fit <- fit(final_wf, train_data)
```

## Parallel Processing

### When to Ask About Parallel Processing

**Ask before:**

- Hyperparameter tuning
- Time series cross-validation with many slices
- Fitting many models
- Any computation that might take >2-3 minutes

### Interaction Pattern

**Don't just add a comment in code** - have an actual conversation with the user.

**Example interaction:**

> **You:** I'm about to run 10-fold cross-validation with hyperparameter tuning. I can use parallel processing to speed this up significantly.
>
> I see you have 8 cores available. Would you like me to use parallel processing? If so, how many cores should I use? (I'd recommend using 6-7 to leave 1-2 cores free for other processes)

**User might respond:**

- "Yes, use 6 cores"
- "No, just run it normally"
- "I'm not sure - what's the difference?"

**If user is unsure:**

> **You:** Here's the trade-off:
>
> - **With parallel processing (6 cores)**: ~5-10 minutes
> - **Without (sequential)**: ~30-45 minutes
>
> Your choice won't affect the results, just the speed.

### Using the Future Package

**Do not use:**

- `parallel` package
- `mirai` package
- `foreach` package

**Do use:**

- `future` package only

```r
library(future)
plan("multisession", workers = 6)

# Now tune_grid() will automatically use parallel processing
```

**Important:** Once parallel processing is set up, continue using it throughout unless the user asks to stop.

## Tuning Parameters by Model

### XGBoost

```r
boost_tree(
  trees = tune(),          # Number of trees (typical: 100-2000)
  tree_depth = tune(),     # Max tree depth (typical: 3-10)
  learn_rate = tune(),     # Learning rate (typical: 0.001-0.3)
  min_n = tune()           # Minimum observations per node (typical: 2-40)
) |>
  set_engine("xgboost") |>
  set_mode("regression")
```

**Grid size:** 20-30 combinations

### Random Forest

```r
rand_forest(
  trees = tune(),     # Number of trees (typical: 500-2000)
  mtry = tune(),      # Number of predictors per split
  min_n = tune()      # Minimum observations per node
) |>
  set_engine("ranger") |>
  set_mode("regression")
```

**Grid size:** 15-25 combinations

### Elastic Net

```r
linear_reg(
  penalty = tune(),    # L1/L2 penalty (typical: 10^-10 to 1)
  mixture = tune()     # Mix of L1 and L2 (0 = ridge, 1 = lasso)
) |>
  set_engine("glmnet")
```

**Grid size:** 10-20 combinations

## Tuning Best Practices

### Grid Size

- **Small datasets (<1000 rows)**: 10-15 combinations
- **Medium datasets (1000-10000 rows)**: 15-25 combinations
- **Large datasets (>10000 rows)**: 25-50 combinations

**Balance:** More combinations = better optimization but longer computation

### Resampling for Tuning

Use the same resampling strategy as model evaluation:

```r
resamples <- time_series_cv(
  data = train_data,
  initial = "2 years",
  assess = "6 months",
  skip = "3 months",
  slice_limit = 4
)
```

**Never use random CV** for time series tuning - always use `time_series_cv()`.

### Metrics

```r
metrics = metric_set(rmse, mae)
```

- **RMSE**: Primary metric (penalizes large errors)
- **MAE**: Secondary metric (less sensitive to outliers)

Select best parameters based on RMSE unless outliers are a major concern.

### Reproducibility

**Always set seed before tuning:**

```r
set.seed(5847)
tune_grid(...)
```

This ensures reproducible results.

## Visualizing Tuning Results

```r
# Overall performance
autoplot(xgb_tuned)

# By specific parameter
autoplot(xgb_tuned, metric = "rmse")

# Numeric summary
show_best(xgb_tuned, metric = "rmse", n = 10)
```

**Look for:**

- Clear optimal region (tuning worked)
- Flat region (parameter doesn't matter much)
- Continuously improving (need to expand search space)

## Complete Tuning Example

```r
# 1. Create model spec with tuning parameters
xgb_spec <- boost_tree(
  trees = tune(),
  tree_depth = tune(),
  learn_rate = tune(),
  min_n = tune()
) |>
  set_engine("xgboost") |>
  set_mode("regression")

# 2. Create workflow
xgb_wf <- workflow() |>
  add_recipe(signature_rec) |>
  add_model(xgb_spec)

# 3. Set up resampling
set.seed(5847)
resamples <- time_series_cv(
  data = train_data,
  initial = "2 years",
  assess = "6 months",
  skip = "3 months",
  slice_limit = 4
)

# 4. Ask about parallel processing
cores <- parallel::detectCores()
# [Have conversation with user about using parallel processing]

# 5. Set up parallel processing (if user agrees)
library(future)
plan("multisession", workers = 6)

# 6. Tune with space-filling grid
set.seed(5847)
xgb_tuned <- tune_grid(
  xgb_wf,
  resamples = resamples,
  grid = 20,  # Space-filling grid with 20 combinations
  metrics = metric_set(rmse, mae),
  control = control_grid(save_pred = TRUE)
)

# 7. Evaluate results
show_best(xgb_tuned, metric = "rmse", n = 5)
autoplot(xgb_tuned)

# 8. Finalize workflow
best_params <- select_best(xgb_tuned, metric = "rmse")
final_wf <- finalize_workflow(xgb_wf, best_params)

# 9. Fit on full training data
final_fit <- fit(final_wf, train_data)
```

## When Tuning Isn't Worth It

**Skip tuning if:**

- Classical models (ARIMA, ETS, Prophet) - use defaults
- Very small datasets (<200 observations)
- Tight time constraints
- Baseline models already perform well

**Focus tuning effort on:**

- ML models (XGBoost, RF, Elastic Net)
- When baseline performance is insufficient
- When you have computational resources
- Production models that will be used repeatedly

## Summary

Key principles:

1. **Use space-filling grids** - Better parameter space coverage
2. **Set seeds** - For reproducible tuning
3. **Use time series CV** - Not random CV
4. **Ask about parallel processing** - Before long computations
5. **Visualize results** - To understand parameter effects
6. **Tune selectively** - Focus on ML models, skip classical models

Tuning can significantly improve model performance, but requires computational resources and careful setup.
