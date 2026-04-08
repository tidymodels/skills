# Correlation Reduction

## Overview

Highly correlated predictors can cause problems:

- Unstable coefficient estimates in linear models

- Inflated variance in predictions

- Redundant information consuming model capacity

Two main strategies: **remove** correlated predictors or **extract** new
features that combine them.

## Correlation Filters

Removes predictors that are highly correlated with others, keeping the one with
highest mean absolute correlation to remaining predictors.

**When to use**: Want interpretable features; correlation is the main concern.

**Considerations**:

- Threshold typically 0.7-0.9

- Only addresses pairwise linear correlation

- Which predictor is kept can be somewhat arbitrary

### tidymodels

```r
library(recipes)

recipe(outcome ~ ., data = train) |>
  step_corr(all_numeric_predictors(), threshold = 0.9)
```

Tunable threshold:

```r
recipe(outcome ~ ., data = train) |>
  step_corr(all_numeric_predictors(), threshold = tune())
```

## Principal Component Analysis (PCA)

Transforms correlated predictors into uncorrelated principal components.
Components are ordered by variance explained.

**When to use**: Many correlated predictors; willing to sacrifice
interpretability for dimensionality reduction.

**Considerations**:

- Requires centering and scaling first

- Must decide how many components to retain

- Components are linear combinations—not directly interpretable

- Works well for neural networks, regularized regression

### tidymodels

Keep components explaining 95% of variance:

```r
recipe(outcome ~ ., data = train) |>
  step_normalize(all_numeric_predictors()) |>
  step_pca(all_numeric_predictors(), threshold = 0.95)
```

Keep fixed number of components:

```r
recipe(outcome ~ ., data = train) |>
  step_normalize(all_numeric_predictors()) |>
  step_pca(all_numeric_predictors(), num_comp = 5)
```

Tunable number of components:

```r
recipe(outcome ~ ., data = train) |>
  step_normalize(all_numeric_predictors()) |>
  step_pca(all_numeric_predictors(), num_comp = tune())
```

## Linear Combinations

Detects and removes predictors that are exact linear combinations of others.
This is a stronger condition than correlation.

**When to use**: Dummy variables from hierarchical categories; derived features
that sum to a constant.

### tidymodels

```r
recipe(outcome ~ ., data = train) |>
  step_lincomb(all_numeric_predictors())
```

## Typical Recipe Order

When combining correlation reduction with other steps:

```r
recipe(outcome ~ ., data = train) |>
  # 1. Handle categoricals
  step_novel(all_factor_predictors()) |>
  step_dummy(all_factor_predictors()) |>
  # 2. Remove zero-variance 
  step_zv(all_predictors()) |>
  # 3. Handle missing data
  step_impute_knn(all_numeric_predictors()) |>
  # 4. Normalize before PCA
  step_normalize(all_numeric_predictors()) |>
  # 5. Then reduce correlation

  step_pca(all_numeric_predictors(), threshold = 0.95)
```

Or with correlation filter instead of PCA:

```r
recipe(outcome ~ ., data = train) |>
  step_novel(all_factor_predictors()) |>
  step_dummy(all_factor_predictors()) |>
  step_zv(all_predictors()) |>
  step_impute_knn(all_numeric_predictors()) |>
  step_corr(all_numeric_predictors(), threshold = 0.9) |>
  step_normalize(all_numeric_predictors())
```
