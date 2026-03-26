# Categorical Predictor Encoding

## Dummy Variables (Indicator Encoding)

Converts a categorical variable with K levels into K-1 binary columns (one level becomes the reference). Required for models that cannot handle factors directly (linear models, neural networks, SVMs, KNN).

**When to use**: Most models except tree-based methods, Cubist, and Naive Bayes.

**Considerations**:
- Reference level choice affects coefficient interpretation but not predictions
- High-cardinality variables create many columns—consider target encoding instead

### tidymodels

```r
library(recipes)

recipe(outcome ~ ., data = train) |>
  step_dummy(all_factor_predictors())
```

To use one-hot encoding (K columns instead of K-1):

```r
recipe(outcome ~ ., data = train) |>
  step_dummy(all_factor_predictors(), one_hot = TRUE)
```

## Target Encoding (Effect Encoding)

Replaces categorical levels with a numeric value based on the outcome. Useful for high-cardinality categoricals where dummy encoding creates too many columns.

**When to use**: Categorical predictors with many levels (e.g., ZIP codes, product IDs).

**Considerations**:
- Risk of data leakage if not done within resampling
- Smoothing/regularization helps with rare levels
- For classification, encodes the probability of the positive class; for regression, encodes the mean outcome

### tidymodels

Mixed-effects target encoding (recommended—provides regularization):

```r
library(recipes)
library(embed)

recipe(outcome ~ ., data = train) |>
  step_lencode_mixed(high_cardinality_var, outcome = vars(outcome))
```

Simple target encoding (less regularization):

```r
recipe(outcome ~ ., data = train) |>
  step_lencode_glm(high_cardinality_var, outcome = vars(outcome))
```

## Novel Levels

New categorical levels in test/production data that weren't in training can cause errors. Handle by assigning novel levels to "other" or the most common level.

### tidymodels

```r
recipe(outcome ~ ., data = train) |>
  step_novel(all_factor_predictors()) |>
  step_dummy(all_factor_predictors())
```

## Infrequent Levels

Levels that appear rarely may not provide reliable signal and can cause issues in resampling. Pool them into an "other" category.

### tidymodels

Pool levels appearing in fewer than 5% of rows:

```r
recipe(outcome ~ ., data = train) |>
  step_other(all_factor_predictors(), threshold = 0.05) |>
  step_dummy(all_factor_predictors())
```

Allow tuning of the pooling threshold:

```r
recipe(outcome ~ ., data = train) |>
  step_other(all_factor_predictors(), threshold = tune()) |>
  step_dummy(all_factor_predictors())
```
