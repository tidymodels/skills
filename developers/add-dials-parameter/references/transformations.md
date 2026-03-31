# Transformations

**Using scale transformations with quantitative parameters**

This guide covers how to use transformations to improve grid coverage and parameter sampling for quantitative parameters that span multiple orders of magnitude.

---

## Why Transformations Are Useful

Transformations change the scale on which parameter values are sampled, improving grid coverage and search efficiency.

### The Problem: Linear Sampling Across Orders of Magnitude

Consider a penalty parameter that can range from 0.0000000001 to 1:

```r
# WITHOUT transformation (linear scale)
penalty <- function(range = c(0.0000000001, 1)) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = NULL,  # No transformation
    label = c(penalty = "Penalty Amount")
  )
}

# Generate regular grid with 5 levels
grid <- dials::grid_regular(penalty(), levels = 5)
grid$penalty
#> [1] 0.0000000001  0.2500000000  0.5000000000  0.7500000000  1.0000000000

# Problem: Only one value explores small penalties!
# Most grid points are bunched near 1
```

### The Solution: Log-Scale Sampling

With log transformation, equal steps in transformed space give uniform exploration:

```r
# WITH transformation (log10 scale)
penalty <- function(range = c(-10, 0), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,  # In log10 space: -10 to 0
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(penalty = "Penalty Amount")
  )
}

# Generate regular grid with 5 levels
grid <- dials::grid_regular(penalty(), levels = 5)
grid$penalty
#> [1] 1e-10  1e-07  1e-04  1e-01  1e+00
#> Equal spacing on log scale! Each step multiplies by 1000

# Benefit: Even exploration across all orders of magnitude
```

### Key Benefits

1. **Uniform exploration**: Equal spacing in transformed space ensures even coverage across scales
2. **Meaningful steps**: For parameters like penalties, relative changes matter more than absolute changes
3. **Better grid coverage**: Grid points distributed where they matter most
4. **Improved tuning**: More efficient parameter space exploration

### When to Use Transformations

**Use transformations when**:

- Parameter spans multiple orders of magnitude
- Relative changes are more meaningful than absolute changes
- Equal steps in transformed space make scientific sense
- Literature commonly discusses parameter on that scale

**Common use cases**:

- Regularization parameters (penalties, costs)
- Learning rates and decay factors
- Small probability parameters
- Parameters with exponential relationships

**Don't use transformations when**:

- Parameter has narrow range (e.g., 0 to 1)
- Absolute changes are meaningful (e.g., number of neighbors from 1 to 15)
- Linear scale is natural for the domain

---

## Available Transformations from scales Package

The scales package provides several transformation functions for use with dials parameters.

### transform_log10()

**Base-10 logarithm transformation**

Most common transformation for parameters spanning orders of magnitude.

```r
# Extension pattern
penalty <- function(range = c(-10, 0), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,        # In log10 space
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(penalty = "Amount of Regularization")
  )
}

# Range: -10 to 0 in log10 space
# Actual values: 10^-10 to 10^0 = 0.0000000001 to 1
```

**When to use**:
- Penalties, costs, regularization amounts
- Parameters spanning 2+ orders of magnitude
- When powers of 10 are natural units

### transform_log()

**Natural logarithm transformation**

Similar to log10 but uses base e (2.71828...).

```r
# Extension pattern
decay_rate <- function(range = c(-10, 0), trans = scales::transform_log()) {
  dials::new_quant_param(
    type = "double",
    range = range,        # In log (natural) space
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(decay_rate = "Exponential Decay Rate")
  )
}

# Range: -10 to 0 in natural log space
# Actual values: exp(-10) to exp(0) = 0.0000454 to 1
```

**When to use**:
- Parameters with natural exponential relationships
- When literature uses natural log
- Continuous decay processes

### transform_log2()

**Base-2 logarithm transformation**

Useful when doubling/halving is natural.

```r
# Extension pattern
buffer_size <- function(range = c(4, 12), trans = scales::transform_log2()) {
  dials::new_quant_param(
    type = "integer",
    range = range,        # In log2 space
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(buffer_size = "Buffer Size")
  )
}

# Range: 4 to 12 in log2 space
# Actual values: 2^4 to 2^12 = 16 to 4096
```

**When to use**:
- Computer science parameters (buffer sizes, cache sizes)
- When powers of 2 are natural (binary systems)
- When doubling/halving is meaningful

### transform_log1p()

**log(1 + x) transformation**

Handles values near zero without issues.

```r
# Extension pattern
small_penalty <- function(range = c(0, 2), trans = scales::transform_log1p()) {
  dials::new_quant_param(
    type = "double",
    range = range,        # In log1p space
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(small_penalty = "Small Penalty Amount")
  )
}

# Handles x = 0 gracefully: log1p(0) = 0
```

**When to use**:
- Parameters that include or are near zero
- Avoid log(0) = -Inf issues
- Count data that might be zero

### transform_reciprocal()

**1/x transformation**

Inverts the scale.

```r
# Extension pattern
time_scale <- function(range = c(0.01, 1), trans = scales::transform_reciprocal()) {
  dials::new_quant_param(
    type = "double",
    range = range,        # In reciprocal space
    inclusive = c(FALSE, TRUE),
    trans = trans,
    label = c(time_scale = "Time Scale Parameter")
  )
}

# Actual values: 1/0.01 to 1/1 = 100 to 1
```

**When to use**:
- Inverse relationships (frequency ↔ period)
- Rate parameters
- When 1/x is more natural than x

### transform_sqrt()

**Square root transformation**

Moderate transformation for more modest ranges.

```r
# Extension pattern
variance_param <- function(range = c(1, 100), trans = scales::transform_sqrt()) {
  dials::new_quant_param(
    type = "double",
    range = range,        # In sqrt space
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(variance_param = "Variance Parameter")
  )
}

# Actual values: 1^2 to 10^2 = 1 to 100
```

**When to use**:
- Variance parameters (standard deviation ↔ variance)
- Parameters with quadratic relationships
- Moderate range compression

---

## How Transformations Affect Parameters

### Range Specification

**Critical**: When `trans` is provided, `range` must be in **transformed space**.

```r
# Log10 transformation example
penalty <- function(range = c(-10, 0), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,  # TRANSFORMED space: -10 to 0
    ...
  )
}

# Actual penalty values: 10^-10 to 10^0 = 0.0000000001 to 1
```

**Common mistake**:

```r
# WRONG: Specifying actual values with transformation
penalty <- function(range = c(0.0000000001, 1),  # ❌ Actual values
                    trans = scales::transform_log10()) {
  ...
}

# CORRECT: Specifying transformed values
penalty <- function(range = c(-10, 0),  # ✅ log10 values
                    trans = scales::transform_log10()) {
  ...
}
```

### Grid Generation

Transformations ensure even spacing in transformed space:

```r
penalty_param <- penalty()

# Regular grid: evenly spaced in log10 space
grid <- dials::grid_regular(penalty_param, levels = 5)
grid$penalty
#> [1] 1e-10  1e-07  1e-04  1e-01  1e+00
#> Each step multiplies by 1000 (10^2.5)

# Random grid: uniform sampling in log10 space
set.seed(123)
grid <- dials::grid_random(penalty_param, size = 5)
grid$penalty
#> [1] 0.0002042  0.1303287  0.0000001  0.5241482  0.9399407
#> Spread across all orders of magnitude
```

### Value Sampling

**`value_sample()`**: Uniform random sampling in transformed space

```r
penalty_param <- penalty()

set.seed(123)
samples <- dials::value_sample(penalty_param, n = 10)
samples
#>  [1] 1.970e-10 3.182e-03 6.727e-09 5.095e-01 2.042e-04
#>  [6] 1.303e-01 5.609e-07 1.000e-10 5.241e-01 9.399e-01

# Even distribution across log scale
log10(samples)
#>  [1] -9.705 -2.497 -8.172 -0.293 -3.690
#>  [6] -0.885 -6.251 -10.000 -0.281 -0.027
# Roughly uniform from -10 to 0
```

**`value_seq()`**: Regular sequence in transformed space

```r
penalty_param <- penalty()

seq_vals <- dials::value_seq(penalty_param, n = 5)
seq_vals
#> [1] 1e-10  1e-07  1e-04  1e-01  1e+00

# Regular spacing on log scale
log10(seq_vals)
#> [1] -10.0  -7.5  -5.0  -2.5   0.0
# Evenly spaced: steps of 2.5
```

---

## Examples

### Example 1: Penalty with Log10 Transformation

Regularization penalty spanning many orders of magnitude:

```r
# Extension pattern
penalty <- function(range = c(-10, 0), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(penalty = "Amount of Regularization"),
    finalize = NULL
  )
}

# Source pattern (no scales:: prefix needed)
penalty <- function(range = c(-10, 0), trans = transform_log10()) {
  new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(penalty = "Amount of Regularization"),
    finalize = NULL
  )
}

# Usage
penalty()
#> Amount of Regularization (quantitative)
#> Transformer: log-10
#> Range (transformed scale): [-10, 0]

# Grid covers all orders of magnitude evenly
grid <- dials::grid_regular(penalty(), levels = 11)
grid$penalty
#>  [1] 1e-10 1e-09 1e-08 1e-07 1e-06 1e-05 1e-04 1e-03 1e-02 1e-01 1e+00
```

### Example 2: Learning Rate with Log10 Transformation

Learning rate for gradient descent:

```r
# Extension pattern
learn_rate <- function(range = c(-5, -1), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(learn_rate = "Learning Rate"),
    finalize = NULL
  )
}

# Usage
learn_rate()
#> Learning Rate (quantitative)
#> Transformer: log-10
#> Range (transformed scale): [-5, -1]

# Actual range: 10^-5 to 10^-1 = 0.00001 to 0.1
grid <- dials::grid_regular(learn_rate(), levels = 5)
grid$learn_rate
#> [1] 0.00001 0.00010 0.00100 0.01000 0.10000

# Even spacing on log scale allows efficient search
```

### Example 3: Cost Parameter with Log Transformation

SVM cost parameter:

```r
# Extension pattern
cost <- function(range = c(-10, 5), trans = scales::transform_log()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(cost = "Cost"),
    finalize = NULL
  )
}

# Usage
cost()
#> Cost (quantitative)
#> Transformer: log-e
#> Range (transformed scale): [-10, 5]

# Actual range: exp(-10) to exp(5) = 0.0000454 to 148.4
grid <- dials::grid_regular(cost(), levels = 4)
grid$cost
#> [1] 4.540e-05 1.832e-02 7.389e+00 2.981e+02
```

### Example 4: Comparing With and Without Transformation

Side-by-side comparison:

```r
# WITHOUT transformation
no_trans <- function(range = c(0.0000001, 1), trans = NULL) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(no_trans = "No Transformation")
  )
}

# WITH transformation
with_trans <- function(range = c(-7, 0), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(with_trans = "With Transformation")
  )
}

# Compare grid coverage
grid_no_trans <- dials::grid_regular(no_trans(), levels = 5)
grid_with_trans <- dials::grid_regular(with_trans(), levels = 5)

grid_no_trans$no_trans
#> [1] 0.0000001 0.2500001 0.5000000 0.7500000 1.0000000
#> Poor coverage: Only 1 value explores small penalties!

grid_with_trans$with_trans
#> [1] 1e-07 1e-05 1e-03 1e-01 1e+00
#> Excellent coverage: Even exploration across all scales!
```

---

## Creating Custom Transformations

For specialized cases, you can create custom transformations with `scales::new_transform()`.

### Custom Transformation Structure

```r
my_transform <- scales::new_transform(
  name = "my_transform",
  transform = function(x) { ... },    # Forward transformation
  inverse = function(x) { ... },      # Inverse transformation
  breaks = scales::extended_breaks(), # Optional: axis breaks
  domain = c(-Inf, Inf)              # Valid domain
)
```

### Example: Custom Power Transformation

```r
# Extension pattern
transform_cube <- scales::new_transform(
  name = "cube",
  transform = function(x) x^3,
  inverse = function(x) x^(1/3),
  domain = c(-Inf, Inf)
)

my_param <- function(range = c(1, 10), trans = transform_cube) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_param = "My Parameter")
  )
}

# Range: 1 to 10 in cube space
# Actual values: 1^3 to 10^3 = 1 to 1000
```

### Example: Custom Bounded Transformation

Logit transformation for probabilities:

```r
# Extension pattern
transform_logit <- scales::new_transform(
  name = "logit",
  transform = function(x) log(x / (1 - x)),
  inverse = function(x) exp(x) / (1 + exp(x)),
  domain = c(0, 1)
)

probability_param <- function(range = c(-3, 3), trans = transform_logit) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(probability_param = "Probability Parameter")
  )
}

# Range: -3 to 3 in logit space
# Actual values: inverse_logit(-3) to inverse_logit(3)
#              = 0.047 to 0.953
```

---

## Extension vs Source Patterns

### Extension Development

**Use `scales::` prefix for transformations**:

```r
penalty <- function(range = c(-10, 0), trans = scales::transform_log10()) {
  dials::new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(penalty = "Amount of Regularization"),
    finalize = NULL
  )
}

# Custom transformation
my_trans <- scales::new_transform(
  name = "my_trans",
  transform = function(x) x^2,
  inverse = function(x) sqrt(x)
)
```

### Source Development

**Transformation functions available directly**:

```r
penalty <- function(range = c(-10, 0), trans = transform_log10()) {
  new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(penalty = "Amount of Regularization"),
    finalize = NULL
  )
}

# Note: scales transformations still need scales:: prefix
my_trans <- scales::new_transform(...)
```

---

## Best Practices

1. **Match transformation to domain**: Use log for exponential relationships, sqrt for quadratic

2. **Specify range in transformed space**: Always remember `range` is in transformed units

3. **Document the transformation**: Explain in `@details` what the actual value range is

4. **Test grid coverage**: Verify that grid points span the intended range

5. **Use standard transformations**: Prefer built-in scales transformations over custom when possible

6. **Consider user expectations**: If users think in actual units, document the conversion clearly

---

## Next Steps

### Learn More

- **Quantitative parameters**: [Quantitative Parameters Guide](quantitative-parameters.md)
- **Data-dependent ranges**: [Data-Dependent Parameters Guide](data-dependent-parameters.md)
- **Grid integration**: [Grid Integration Guide](grid-integration.md)

### Implementation Guides

- **Extension development**: [Extension Development Guide](extension-guide.md)
- **Source development**: [Source Development Guide](source-guide.md)

---

**Last Updated:** 2026-03-31
