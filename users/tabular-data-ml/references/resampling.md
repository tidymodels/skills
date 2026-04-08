# Resampling Methods

## Overview

Resampling estimates model performance using out-of-sample predictions without
touching the test set. The choice depends on dataset size and computational
budget.

| Method         | Best For               | Pros                          | Cons                      |
| -------------- | ---------------------- | ----------------------------- | ------------------------- |
| V-fold CV      | Small to medium data   | Low variance, uses all data   | Computationally expensive |
| Validation set | Large data (≥10K rows) | Fast, simple                  | Higher variance           |
| Repeated CV    | Final model assessment | Lower variance than single CV | Very expensive            |

## V-Fold Cross-Validation

Splits training data into V folds; iteratively holds out each fold for
validation while training on the rest.

**When to use**: Default choice for small to medium datasets.

**Considerations**:

- V=10 is standard; V=5 for very small data or expensive models

- Stratified CV maintains outcome distribution in each fold

- Each observation appears in exactly one held-out fold

### tidymodels

```r
library(tidymodels)

# Set seed immediately before creating folds for reproducibility
set.seed(2954)

# Basic 10-fold CV
resamples <- vfold_cv(train_data, v = 10)

# Stratified by outcome (classification)
resamples <- vfold_cv(train_data, v = 10, strata = outcome)

# Stratified by outcome (regression - uses quartiles internally)
resamples <- vfold_cv(train_data, v = 10, strata = outcome)
```

## Repeated Cross-Validation

Runs V-fold CV multiple times with different random splits, then averages
results.

**When to use**: Final model assessment when variance reduction matters;
comparing close models.

**Considerations**:

- 5-fold repeated 5 times or 10-fold repeated 3 times are common

- Multiplies computation time by the number of repeats

### tidymodels

```r
# Set seed immediately before creating folds for reproducibility
set.seed(8173)

# 10-fold CV repeated 5 times
resamples <- vfold_cv(train_data, v = 10, repeats = 5, strata = outcome)
```

## Validation Set

tidymodels treats validation sets like a single resample of the data.

See the instructions in [data-spending.md](data-spending.md) for making the
initial three-way split.

### tidymodels

```r
library(tidymodels)

# Set seed immediately before splitting for reproducibility
set.seed(6401)
init_split <- initial_validation_split(all_data, strata = outcome)
train_data <- training(init_split)
test_data <- testing(init_split)
validation_data <- validation(init_split)

# Create resampling object for tuning
resamples <- validation_set(init_split)
```

## Time Series: Rolling Origin

For time-dependent data, uses expanding or sliding windows that respect temporal
order.

**When to use**: Time series or temporal data where random splits would cause
data leakage.

**Considerations**:

- Never use future data to predict the past

- `initial` sets minimum training size; `assess` sets forecast horizon

- requires the data to have a column that has a date or date-time class.

### tidymodels

```r
# Rolling origin with expanding window
resamples <-  
  sliding_period(
    train_data,
    index = date_column,
    period = "week",  # use an appropriate unit of time
    lookback = Inf,
    complete = TRUE,
    assess_stop = 2,  # use an appropriate size for data
    step = 2          # use an appropriate size for data
  )
```

## Grouped Data

When observations are not independent (e.g., multiple measurements per subject),
keep groups together.

**When to use**: Repeated measures, clustered data, longitudinal studies.

### tidymodels

```r
# Set seed immediately before creating folds for reproducibility
set.seed(9528)

# Keep all observations from the same group together
resamples <- group_vfold_cv(train_data, group = id_column, v = 10)
```
