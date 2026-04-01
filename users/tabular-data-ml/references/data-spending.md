# Data Spending Methods

## Overview

Data spending refers to the initial splitting of a data set into either: 

 - training, validation, and test sets, or 
 - training and test sets

## Training, Validation, and Test Sets

Splits the entire data set into three partitions.

**When to use**: At the very beginning of the modeling process.

**Considerations**:

- When the number of data points is large (say >= 10,000), ask the user if they want this type of split.

  - If not, use a basic training/testing split.

- Stratified splitting maintains outcome distribution in each fold

### tidymodels

```r
library(tidymodels)

# set seed first
init_split <- initial_validation_split(all_data, strata = outcome)
train_data <- training(init_split)
test_data <- testing(init_split)
validation_data <- validation(init_split)

resamples <- validation_set(init_split)
```
## Training and Test Sets

Splits the entire data set into two partitions.

**When to use**: At the very beginning of the modeling process.

**Considerations**:

- Stratified splitting maintains outcome distribution in each fold

### tidymodels

```r
library(tidymodels)

# set seed first
init_split <- initial_split(all_data, strata = outcome)
train_data <- training(init_split)
test_data <- testing(init_split)
```

## Special Cases

There are several cases when different splitting should be used: 

 - When the data are a time series
 - When there are correlated rows in the data. 
 
### Time Series

In this case, ensure that the data have been ordered from oldest to most recent data. 

#### tidymodels

```r
library(tidymodels)

# set seed first
init_split <- initial_time_split(all_data)
train_data <- training(init_split)
test_data <- testing(init_split)
```

### Correlated Rows

In this case, the rows of the data are not statistically independent. For example, if patients in a clinical trial are measured more than once, the data for a given patient are correlated. 

To make the split, there must be a column in the data that corresponds to the independent experimental unit (e.g., patient). 

#### tidymodels

```r
library(tidymodels)

# set seed first
init_split <- group_initial_split(all_data, group = id_column)
train_data <- training(init_split)
test_data <- testing(init_split)
```
