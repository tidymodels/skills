---
name: tidymodels
description: Build machine learning models using tidymodels for tabular data using proper data spending, resampling, and validation practices. Covers train/test splitting, cross-validation, feature engineering, model tuning, and evaluation. Use when building predictive models, comparing algorithms, or when users mention machine learning, model training, or prediction tasks.
---

# Tabular Data Machine Learning

This skill guides the process of developing predictive models for tabular data with proper validation practices.

## Data Spending Strategy

Always partition data into:

- **Training set**: Used for all feature engineering, feature selection, and model development

- **Test set**: Reserved for final model evaluation only—requires explicit user permission before use

A common split is 75% training / 25% testing. Use stratified sampling:

- Classification: stratify by outcome class

- Regression: create temporary quartile groups and stratify by those

See [references/data-spending.md](references/data-spending.md) for specific instructions for data splitting.

### Test Set Rules

- **NEVER** predict on test data during model development

- **NEVER** calculate test set metrics without explicit user permission

- **NEVER** use test data to compare models or tune hyperparameters

- **DO** ask: *"If you have completed model development, may I evaluate the final model on the test set?"*

- **DO** wait for explicit confirmation before proceeding

**Self-check**: If you're writing `predict(..., test_data)` without prior user permission, STOP—you're making an error.

**Exception**: Basic verification after splitting (e.g., `nrow(test_data)`, `glimpse(test_data)`) to confirm the split worked.

## Empirical Validation

Always use out-of-sample predictions to measure performance:

- **Large datasets (≥10,000 rows)**: Use a single validation set

- **Small to medium datasets**: Use 10-fold cross-validation or appropriate resampling

See [references/resampling.md](references/resampling.md) for resampling methods and implementation.

### Validation Rules

- **NEVER** directly predict on training data to measure performance

- **DO** develop and compare models using only CV or validation set results

- **DO** select final model(s) based on out-of-sample performance

## Performance Metrics

See [references/evaluation.md](references/evaluation.md) for specific instructions for computing performance metrics.

### Classification

Ask the user whether they prioritize:

- **Class separation**: Use ROC-AUC or PR-AUC

- **Calibrated probabilities**: Use Brier score

Default set: ROC-AUC, Brier score, and accuracy.

### Regression

- **RMSE**: Primary accuracy metric (sensitive to outliers)

- **MAE**: Accuracy metric less sensitive to outliers

- **R²**: Measures variance explained (supplement to RMSE/MAE, not a replacement)

Default set: RMSE and R².

## Model Optimization

The modeling process is iterative. Three main levers for improvement:

1. **Feature engineering**: Modify predictors so the model does less work
2. **Model selection**: Choose appropriate algorithm for data characteristics
3. **Hyperparameter tuning**: Optimize parameters that can't be estimated from data

All steps must be validated using out-of-sample data.

### Optimization Rules

- **NEVER** use data outside the training set to determine feature engineering steps

- **NEVER** engineer features, then evaluate directly on training data

- **DO** treat feature engineering and model training as a single process

- **DO** use CV or validation set to measure combined feature engineering + model performance

- **DO** use CV or validation set to select best tuning parameters

## Feature Engineering

See [references/feature-engineering.md](references/feature-engineering.md) for:

- Common feature engineering techniques

- Model-specific requirements (mandatory vs. helpful transformations)

## Model Tuning

- Use parameter ranges provided by the modeling framework

- Use space-filling designs for grid search when available

- Use racing methods for efficiency (except with validation sets)

- Visualize tuning results to show performance vs. parameter relationships

It is a good idea to propose two models to the user: 

 - a regularized linear (or logistic) model such as `glmnet`
 - a boosted tree with an early stopping argument to halt after 5 poor iterations.

See [references/tuning.md](references/tuning.md) for details on tuning methods and implementation.


## Model Evaluation

See [references/tuning.md](references/tuning.md) for details on tuning methods and implementation.

**Without tuning**: Resample the model or use a validation set. Report out-of-sample metrics.

**With tuning**: Select metric to optimize, identify optimal tuning parameters.

For the best model, present:

- Numeric metric results

- Appropriate visualizations (see below)

### Evaluation Visualizations

**Classification**:

- ROC or PR curves

- Calibration curves

**Regression**:

- Observed vs. predicted plots

- Residual plots

See [references/evaluation.md](references/evaluation.md) for metrics, visualizations, and implementation.

## Final Model

Once the user selects a final model, fit it on the entire training set.

## Test Set Evaluation

After receiving user permission, evaluate on the test set with:

- Numeric metrics

- Same visualizations as model evaluation (ROC/PR curves, calibration, observed vs. predicted, residuals)
