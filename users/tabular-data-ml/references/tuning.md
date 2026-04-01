# Hyperparameter Tuning

## Overview

Hyperparameters are model settings that cannot be learned from data. Tuning searches for values that optimize out-of-sample performance.

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| Grid search | Few parameters, small grids | Exhaustive, reproducible | Exponential scaling |
| Racing | Large grids | Efficient, discards poor configs early | May miss borderline good configs |
| Bayesian optimization | Expensive models, many parameters | Smart exploration | Overhead for simple problems |

For tabular data, grid search and racing are optimized and should be the default. 

## Marking Parameters for Tuning

In tidymodels, use `tune()` as a placeholder for parameters to optimize.

### tidymodels

```r
library(tidymodels)

# Model with tunable parameters
model_spec <- rand_forest(
 mtry = tune(),
 min_n = tune(),
 trees = 500
) |>
 set_engine("ranger") |>
 set_mode("classification")

# Recipe with tunable parameters
recipe_spec <- recipe(outcome ~ ., data = train_data) |>
 step_pca(all_numeric_predictors(), num_comp = tune())
```

## Grid Search

Evaluates all combinations of parameter values in a predefined grid.

**When to use**: Almost all cases.

**Considerations**:

- Space-filling designs cover parameter space more efficiently

- Typical grid sizes: 10-50 configurations

### tidymodels

Space-filling grid (recommended):

We can make a specific grid from a parameter set object:

```r
grid <- grid_space_filling(params, size = 25)
```

However, it is best to simply provide an integer to the `grid` argument of the tuning functions (see below). 

Running the grid search:

```r
resamples <- vfold_cv(train_data, v = 10, strata = outcome)

tune_results <- tune_grid(
 wf,
 resamples = resamples,
 grid = 20,
 metrics = metric_set(roc_auc, accuracy)
)
```

## Racing Methods

Starts with all configurations, then eliminates poor performers after initial resamples. Efficient for large and/or wide grids.

**When to use**: Wide grids; want efficiency without giving up grid search's coverage.

**Considerations**:

- Requires enough resamples for statistical comparison (≥5 resamples)

- Can't use with validation sets (only one assessment—no racing possible)

- ANOVA racing is most common; simulated annealing racing also available

### tidymodels

```r
library(finetune)

# ANOVA racing - eliminates configs significantly worse than best

# Set seed first

tune_results <- tune_race_anova(
 wf,
 resamples = resamples,
 grid = 20,
 metrics = metric_set(roc_auc)
)
```

## Initial Model Suggestions

Unless the user is interested in a specific model, we suggest starting with two disparate models: 

- A regularized model that is linear in its parameters, such as linear regression, logistic regression, or multinomial regression. 

- A boosted tree that uses early stopping.

Generally, do not suggest models that are similar to ones already considered. For example, do not suggest random forest after a different tree ensemble has been evaluated. 

### Linear Models

Propose a simple model early in the process. Use a recipe that includes any existing feature engineering and also standardize the predictors after a zero-variance filter. 

#### tidymodels

For example, for a regression data set where we have observed that predictor `x1` has a nonlinear relationship with the outcome: 

```r
library(tidymodels)

# Model with tunable parameters
glmnet_spec <- linear_reg(penalty = tune(), mixture = tune()) |>
 set_engine("glmnet")

# Recipe 
spline_rec <- recipe(outcome ~ ., data = train_data) |>
 step_spline_natural(x1, deg_free = tune()) |> 
 step_dummy(all_factor_predictors()) |> 
 step_zv(all_predictors()) |> 
 step_normalize(all_predictors())
 
glmnet_wflow <- workflow(spline_rec, model_spec)
```

### Boosting

Also propose a boosting model early in the process. Make sure that the number of trees is set to a specific value and the argument `stop_iter = 5` is used. 

For example: 

```r
library(tidymodels)

# Model with tunable parameters
bst_spec <- boosted_tree(
  trees = 1000,
  learn_rate = tune(),
  mtry = tune(),
  min_n = tune(),
  stop_iter = tune()
) |> 
 set_mode("regression")

# Recipe 
indicator_rec <- recipe(outcome ~ ., data = train_data) |>
 step_dummy(all_factor_predictors(), one_hot = TRUE)
 
bst_wflow <- workflow(indicator_rec, bst_spec)
```

#### tidymodels

## Working with Tuning Results

### Viewing results

```r
# Summary of all configurations
collect_metrics(tune_results)

# Best configuration by metric
show_best(tune_results, metric = "roc_auc", n = 5)

# Single best
select_best(tune_results, metric = "roc_auc")
```

### Visualizing tuning

```r
# Performance vs parameters
autoplot(tune_results)

# Custom visualization
tune_results |>
 collect_metrics() |>
 filter(.metric == "roc_auc") |>
 ggplot(aes(x = mtry, y = mean, color = factor(min_n))) +
 geom_point() +
 geom_line()
```

### Finalizing the model

```r
# Select best parameters
best_params <- select_best(tune_results, metric = "roc_auc")

# Update workflow with best parameters
final_wf <- finalize_workflow(wf, best_params)

# Fit to full training set
final_fit <- fit(final_wf, data = train_data)
```

If the resample function was used to make the initial split, there is a simpler API: 

```r
# Select best parameters
best_params <- select_best(tune_results, metric = "roc_auc")

# Update workflow with best parameters
final_wf <- finalize_workflow(wf, best_params)

# Fit to full training set
final_fit <- last_fit(init_split, final_wf)
```

## Parameter Ranges

tidymodels provides sensible defaults via the `dials` package. Customize when needed.

```r
# View default range
mtry()

# Customize range (mtry depends on number of predictors)
params <- extract_parameter_set_dials(wf) |>
 update(mtry = mtry(range = c(2, 20)))

# Finalize data-dependent parameters
params <- params |>
 finalize(train_data)
```

## Parallel Processing

Tuning is embarrassingly parallel—each configuration can run independently.

Before proposing potentially long-running computations, like resampling or model fitting, first use `parallel::detectCores()` to determine the maximum number of cores available, then ask the user if they would like to use parallel processing and, if so, how many cores you are allowed to use. Keep using the extra cores throughout the work unless the user asks you to stop.

When computing statistics over a large number of columns, use the future package to parallelize these computations. Do not use the parallel, mirai, or foreach packages for parallel execution. 

When using tidymodels functions, such as `tune::fit_resamples()`  or `tune::tune_grid()`, ask about parallel processing and use the future package to create local workers. 

```r
library(future)
plan("multisession")

# tune_grid, tune_race_anova, etc. will use parallel processing automatically
```
