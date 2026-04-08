# Missing Data Imputation

## Overview

Imputation estimates missing values from observed data. Required for models that
cannot handle `NA` values (most models except some tree implementations).

**Key principle**: Imputation must be performed within the resampling process.
Compute imputation parameters (means, medians, model coefficients) from training
data only.

## Simple Imputation

Replaces missing values with a single summary statistic.

**Mean/Median imputation**: Fast and simple. Median is more robust to outliers.

**Mode imputation**: For categorical variables, replace with most frequent
level.

**Considerations**:

- Distorts distributions and underestimates variance

- Appropriate when missingness is low (<5%) and mechanism is MCAR

### tidymodels

Numeric predictors with median:

```r
library(recipes)

recipe(outcome ~ ., data = train) |>
  step_impute_median(all_numeric_predictors())
```

Numeric predictors with mean:

```r
recipe(outcome ~ ., data = train) |>
  step_impute_mean(all_numeric_predictors())
```

Categorical predictors with mode:

```r
recipe(outcome ~ ., data = train) |>
  step_impute_mode(all_factor_predictors())
```

## K-Nearest Neighbors Imputation

Imputes missing values using the mean (numeric) or mode (categorical) of the K
nearest neighbors based on non-missing predictors.

**When to use**: When relationships between predictors matter; missingness may
be MAR.

**Considerations**:

- Computationally more expensive than simple imputation

- Requires scaling predictors for distance calculation

- Typical K values: 5-10

### tidymodels

```r
recipe(outcome ~ ., data = train) |>
  step_impute_knn(all_predictors(), neighbors = 5)
```

## Bagged Tree Imputation

Uses bagged decision trees to predict missing values from other predictors.

**When to use**: When relationships between predictors are complex or nonlinear;
can handle mixed predictor types.

**Considerations**:

- More computationally expensive than KNN

- Often produces better imputations for complex data

### tidymodels

```r
recipe(outcome ~ ., data = train) |>
  step_impute_bag(all_predictors())
```

## Linear Model Imputation

Predicts missing values using a linear model (or logistic for binary).

**When to use**: When linear relationships exist between predictors.

### tidymodels

```r
recipe(outcome ~ ., data = train) |>
  step_impute_linear(predictor_with_missing, 
                     impute_with = imp_vars(predictor1, predictor2))
```

## Missing Value Indicators

Creates binary indicator columns flagging which values were originally missing.
Can help if missingness itself is informative.

**When to use**: When the pattern of missingness may predict the outcome.

### tidymodels

```r
recipe(outcome ~ ., data = train) |>
  step_indicate_na(all_predictors()) |>
  step_impute_median(all_numeric_predictors()) |>
  step_impute_mode(all_factor_predictors())
```

## Recommended Order

When combining imputation with other steps:

```r
recipe(outcome ~ ., data = train) |>
  # 1. Handle novel levels first (before any encoding)
  step_novel(all_factor_predictors()) |>
  # 2. Impute missing values
  step_impute_knn(all_predictors()) |>
  # 3. Then proceed with other transformations
  step_dummy(all_factor_predictors()) |>
  step_normalize(all_numeric_predictors())
```
