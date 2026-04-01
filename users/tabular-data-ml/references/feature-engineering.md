# Feature Engineering Reference

## Common Techniques

| Technique | When to Use |
|-----------|-------------|
| Zero-variance removal | Always check for predictors with single unique value |
| Dummy variables | Convert categorical predictors to binary 0/1 indicators |
| Target encoding | Categorical predictors with many levels → single numeric column |
| Centering & scaling | Models using distance metrics or dot products |
| Symmetric transformations | Skewed numeric predictors (Yeo-Johnson or orderNorm) |
| Imputation | Missing predictor values—estimate from other columns |
| Correlation reduction | Feature extraction (e.g., PCA) or unsupervised correlation filter |
| Spline terms | Nonlinear relationships between single predictors and outcome |
| Interaction terms | Joint effects of two or more predictors |

## Detailed Implementation

For methodology and code examples:

- [Categorical predictors](feature-engineering/categorical.md): dummy variables, target encoding

- [Numeric predictors](feature-engineering/numeric.md): scaling, transformations, splines

- [Missing data](feature-engineering/missing-data.md): imputation strategies

- [Correlation reduction](feature-engineering/correlation.md): PCA, filters

## Model-Specific Requirements

### Linear Models

**Ordinary linear/logistic/multinomial regression**:

- Mandatory: indicator variables, zero-variance removal, complete data

- Helpful: interaction terms, spline terms, reducing correlation, symmetric distributions

**Regularized linear/logistic/multinomial regression**:

- Mandatory: indicator variables, zero-variance removal, standardized scale, complete data

- Helpful: interaction terms, spline terms, reducing correlation, symmetric distributions

### Distance-Based Models

**K-nearest neighbors**:

- Mandatory: indicator variables, zero-variance removal, standardized scale, complete data

- Helpful: symmetric distributions

**Support Vector Machines**:

- Mandatory: indicator variables, zero-variance removal, standardized scale, complete data

- Helpful: symmetric distributions

### Additive and Spline Models

**Generalized Additive Models**:

- Mandatory: indicator variables, zero-variance removal, complete data

- Helpful: symmetric distributions

**Multivariate Adaptive Regression Splines (MARS)**:

- Mandatory: indicator variables, complete data

- Helpful: symmetric distributions

### Probabilistic Models

**Naive Bayes**:

- Mandatory: zero-variance removal

- Helpful: none

### Neural Networks

**Neural networks**:

- Mandatory: indicator variables, zero-variance removal, reducing correlation, standardized scale, complete data

- Helpful: symmetric distributions

### Tree-Based Models

**Single tree models**:

- Mandatory: none

- Helpful: none

**Tree ensemble models (random forest, boosting)**:

- Mandatory: complete data (for most implementations)

### Rule-Based Models

**RuleFit**:

- Mandatory: indicator variables, zero-variance removal, standardized scale, complete data

- Helpful: none

**Cubist**:

- Mandatory: none

- Helpful: none
