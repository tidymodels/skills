# Model Evaluation

## Overview

Evaluation measures how well the model predicts unseen data. Always use out-of-sample predictions—from cross-validation during development, from the test set for final assessment.

## Classification Metrics

### Threshold-Independent Metrics

These evaluate the full range of predicted probabilities without choosing a classification threshold.

**ROC-AUC**: Area under the ROC curve. Measures ability to rank positive cases higher than negative cases. Range: 0.5 (random) to 1.0 (perfect).

**PR-AUC**: Area under the precision-recall curve. Better than ROC-AUC for imbalanced data where the positive class is rare.

**Brier Score**: Mean squared error of probability predictions. Measures calibration. Range: 0 (perfect) to 1 (worst). Lower is better.

### tidymodels

```r
library(tidymodels)

# From predictions dataframe with columns: .pred_class, .pred_positive, truth
metrics <- metric_set(roc_auc, pr_auc, brier_class)
predictions |> metrics(truth = outcome, .pred_positive, estimate = .pred_class)

# Individual metrics
predictions |> roc_auc(truth = outcome, .pred_positive)
predictions |> pr_auc(truth = outcome, .pred_positive)
predictions |> brier_class(truth = outcome, .pred_positive)
```

### Threshold-Dependent Metrics

Require choosing a probability threshold (default: 0.5) to convert probabilities to class predictions.

**Accuracy**: Proportion of correct predictions. Can be misleading with imbalanced classes.

**Sensitivity (Recall)**: True positive rate. Of actual positives, how many did we catch?

**Specificity**: True negative rate. Of actual negatives, how many did we correctly identify?

**Precision (PPV)**: Of predicted positives, how many are actually positive?

**F1 Score**: Harmonic mean of precision and recall. Balances both concerns.

### tidymodels

```r
# Confusion matrix
predictions |> conf_mat(truth = outcome, estimate = .pred_class)

# Multiple metrics
class_metrics <- metric_set(accuracy, sensitivity, specificity, precision, f_meas)
predictions |> class_metrics(truth = outcome, estimate = .pred_class)
```

### Multiclass Classification

For more than two classes, metrics are computed per-class and aggregated.

```r
# Macro-averaging (unweighted mean across classes)
predictions |> accuracy(truth = outcome, estimate = .pred_class)
predictions |> roc_auc(truth = outcome, .pred_class_A, .pred_class_B, .pred_class_C)

# Specify estimator explicitly
predictions |> sensitivity(truth = outcome, estimate = .pred_class, estimator = "macro")
predictions |> sensitivity(truth = outcome, estimate = .pred_class, estimator = "micro")
```

## Regression Metrics

**RMSE**: Root mean squared error. In outcome units. Penalizes large errors heavily.

**MAE**: Mean absolute error. In outcome units. Less sensitive to outliers than RMSE.

**R²**: Coefficient of determination. Proportion of variance explained. Does not measure prediction accuracy—use with RMSE/MAE.

**MAPE**: Mean absolute percentage error. Scale-independent but undefined when true values are zero.

### tidymodels

```r
# From predictions dataframe with columns: .pred, truth
reg_metrics <- metric_set(rmse, mae, rsq)
predictions |> reg_metrics(truth = outcome, estimate = .pred)

# Individual metrics
predictions |> rmse(truth = outcome, estimate = .pred)
predictions |> mae(truth = outcome, estimate = .pred)
predictions |> rsq(truth = outcome, estimate = .pred)
```

## Evaluation Visualizations

### Classification: ROC Curve

Shows tradeoff between sensitivity and specificity across all thresholds.

```r
# Generate ROC curve data
roc_data <- predictions |> roc_curve(truth = outcome, .pred_positive)

# Plot
autoplot(roc_data)

# Custom plot
roc_data |>
 ggplot(aes(x = 1 - specificity, y = sensitivity)) +
 geom_path() +
 geom_abline(linetype = "dashed") +
 coord_equal()
```

### Classification: Precision-Recall Curve

Shows tradeoff between precision and recall. Preferred for imbalanced data.

```r
pr_data <- predictions |> pr_curve(truth = outcome, .pred_positive)
autoplot(pr_data)
```

### Classification: Calibration Curve

Shows whether predicted probabilities match observed frequencies. Well-calibrated models follow the diagonal.

```r
library(probably)

# Calibration plot
predictions |>
 cal_plot_breaks(truth = outcome, .pred_positive, num_breaks = 10)

# Calibration with more refinement
predictions |>
 cal_plot_windowed(truth = outcome, .pred_positive, step_size = 0.03)
```

### Classification: Confusion Matrix

```r
predictions |>
 conf_mat(truth = outcome, estimate = .pred_class) |>
 autoplot(type = "heatmap")

# Mosaic plot
predictions |>
 conf_mat(truth = outcome, estimate = .pred_class) |>
 autoplot(type = "mosaic")
```

### Regression: Observed vs Predicted

Points should fall along the diagonal for good predictions.

```r
predictions |>
 ggplot(aes(x = outcome, y = .pred)) +
 geom_point(alpha = 0.5) +
 geom_abline(color = "red", linetype = "dashed") +
 coord_obs_pred() +
 labs(x = "Observed", y = "Predicted")
```

### Regression: Residual Plots

Residuals should be randomly scattered around zero with constant variance.

```r
predictions |>
 mutate(residual = outcome - .pred) |>
 ggplot(aes(x = .pred, y = residual)) +
 geom_point(alpha = 0.5) +
 geom_hline(yintercept = 0, color = "red", linetype = "dashed") +
 labs(x = "Predicted", y = "Residual")
```

Residual distribution:

```r
predictions |>
 mutate(residual = outcome - .pred) |>
 ggplot(aes(x = residual)) +
 geom_histogram(bins = 30)
```

## Comparing Models

### Resampling Comparison

Compare models using the same resamples for valid statistical comparison.

```r
# Fit multiple models to same resamples
results_rf <- fit_resamples(wf_rf, resamples = folds)
results_xgb <- fit_resamples(wf_xgb, resamples = folds)
results_glm <- fit_resamples(wf_glm, resamples = folds)

# Combine for comparison
all_results <- bind_rows(
 collect_metrics(results_rf) |> mutate(model = "random_forest"),
 collect_metrics(results_xgb) |> mutate(model = "xgboost"),
 collect_metrics(results_glm) |> mutate(model = "logistic")
)

# Visualize
all_results |>
 filter(.metric == "roc_auc") |>
 ggplot(aes(x = model, y = mean)) +
 geom_point() +
 geom_errorbar(aes(ymin = mean - std_err, ymax = mean + std_err), width = 0.2)
```

### Using workflow_set

```r
library(workflowsets)

# Create workflow set
wf_set <- workflow_set(
 preproc = list(basic = recipe_basic, normalized = recipe_normalized),
 models = list(rf = model_rf, xgb = model_xgb)
)

# Fit all workflows to same resamples
wf_results <- wf_set |>
 workflow_map("fit_resamples", resamples = folds)

# Rank by metric
rank_results(wf_results, rank_metric = "roc_auc")

# Plot comparison
autoplot(wf_results, metric = "roc_auc")
```

## Collecting Predictions from Resamples

```r
# Save predictions during resampling
results <- fit_resamples(
 wf,
 resamples = folds,
 control = control_resamples(save_pred = TRUE)
)

# Get all out-of-sample predictions
predictions <- collect_predictions(results, summarize = TRUE)

# Now use for evaluation visualizations
predictions |> roc_curve(truth = outcome, .pred_positive) |> autoplot()
```
