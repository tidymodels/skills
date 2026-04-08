# Numeric Predictor Transformations

## Centering and Scaling (Standardization)

Centers predictors to mean zero and scales to unit variance. Essential for
models that use distance metrics or dot products.

**When to use**: KNN, SVM, neural networks, regularized regression (lasso,
ridge, elastic net), PCA.

**Considerations**:

- Compute mean and SD from training data only; apply same values to test data

- Not needed for tree-based models

### tidymodels

```r
library(recipes)

recipe(outcome ~ ., data = train) |>
  step_normalize(all_numeric_predictors())
```

For min-max scaling to [0, 1] range:

```r
recipe(outcome ~ ., data = train) |>
  step_range(all_numeric_predictors())
```

## Symmetric Transformations

Transforms skewed predictors to approximate symmetry. Can improve performance
for models sensitive to outliers or that assume normality.

**When to use**: Numeric predictors with heavy skew; particularly helpful for
linear models and neural networks.

**Options**:

- **Yeo-Johnson**: Handles zero and negative values

- **Box-Cox**: Requires strictly positive values

- **orderNorm**: Transforms to approximate normality via rank ordering

### tidymodels

Yeo-Johnson (recommended default):

```r
recipe(outcome ~ ., data = train) |>
  step_YeoJohnson(all_numeric_predictors())
```

Box-Cox (positive values only):

```r
recipe(outcome ~ ., data = train) |>
  step_BoxCox(all_numeric_predictors())
```

orderNorm (from bestNormalize):

```r
recipe(outcome ~ ., data = train) |>
  step_orderNorm(all_numeric_predictors())
```

## Natural Splines

Creates basis functions to model nonlinear relationships between a predictor and
outcome. Allows linear models to capture curvature.

**When to use**: Suspected nonlinear relationship between a numeric predictor
and outcome; using a linear model.

**Considerations**:

- Degrees of freedom (df) controls flexibility; higher df = more wiggly

- Start with df = 3-5 and tune if needed

- Not needed for tree-based models or GAMs (they handle nonlinearity internally)

### tidymodels

```r
recipe(outcome ~ ., data = train) |>
  step_ns(predictor_name, deg_free = 4)
```

Tunable degrees of freedom:

```r
recipe(outcome ~ ., data = train) |>
  step_ns(predictor_name, deg_free = tune())
```

## Interaction Terms

Creates products of predictors to model joint effects. Use when the effect of
one predictor depends on another.

**When to use**: Domain knowledge suggests interaction; exploratory analysis
shows effect modification.

**Considerations**:

- Can dramatically increase feature count

- Tree-based models capture interactions automatically

- For linear models, specify interactions based on domain knowledge

### tidymodels

Specific interactions:

```r
recipe(outcome ~ ., data = train) |>
  step_interact(terms = ~ var1:var2)
```

All pairwise interactions among selected predictors:

```r
recipe(outcome ~ ., data = train) |>
  step_interact(terms = ~ all_numeric_predictors():all_numeric_predictors())
```

## Zero-Variance and Near-Zero-Variance Removal

Removes predictors with single unique value (zero variance) or very few unique
values relative to sample size.

**When to use**: Always include zero-variance removal; near-zero-variance is
optional but often helpful.

### tidymodels

Zero-variance only:

```r
recipe(outcome ~ ., data = train) |>
  step_zv(all_predictors())
```

Near-zero-variance (also catches problematic predictors):

```r
recipe(outcome ~ ., data = train) |>
  step_nzv(all_predictors())
```
