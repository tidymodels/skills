# Best Practices (Source Development)

**dials-specific best practices for contributing to tidymodels/dials**

This guide covers conventions, patterns, and best practices specific to source development in the dials package.

---

## File Naming Conventions

### Parameter Files

**Pattern**: `R/param_[name].R`

```
R/
├── param_penalty.R
├── param_mixture.R
├── param_mtry.R
├── param_learn_rate.R
├── param_activation.R
└── param_num_comp.R
```

**Rules**:

- Use lowercase with underscores

- One parameter per file (usually)

- Related parameters may share a file (e.g., `activation()` and `activation_2()`)

**Examples**:

```r
# Good
R/param_learn_rate.R      # For learn_rate()
R/param_num_trees.R       # For num_trees()
R/param_weight_func.R     # For weight_func()

# Avoid
R/learn_rate.R            # Missing param_ prefix
R/param-learn-rate.R      # Hyphens instead of underscores
R/learning_rate.R         # Different from function name
```

### Test Files

**Shared test files** (most common):

```
tests/testthat/
├── test-params.R          # Range tests for all parameters
├── test-constructors.R    # Constructor validation
├── test-finalize.R        # Finalization tests
└── test-grids.R          # Grid generation tests
```

**Individual test files** (rare, for complex parameters):

```
tests/testthat/
└── test-special-param.R  # Only if parameter needs many unique tests
```

---

## Function Naming

### Match the Concept

Choose function names that clearly describe what the parameter controls:

**Good examples**:

```r
learn_rate()        # Learning rate (not learning_rate)
num_trees()         # Number of trees
mtry()              # Randomly selected predictors
deg_free()          # Degrees of freedom
weight_func()       # Weight function
```

**Guidelines**:

- Use underscores for multi-word names

- Abbreviate when commonly understood (`mtry`, `deg_free`)

- Match terminology used in literature and practice

- Keep concise but clear

### Avoid Redundancy

```r
# Good
penalty()           # Amount of regularization
mixture()           # Proportion of Lasso penalty

# Avoid
penalty_amount()    # Redundant "amount"
mixture_proportion() # Redundant "proportion"
```

### Parameter Variants

When you need multiple related parameters:

```r
activation()        # Primary activation function
activation_2()      # Second layer activation

mtry()              # Standard mtry
mtry_prop()         # mtry as proportion
```

---

## Range Specification

### Always in Transformed Units

When `trans` is provided, specify `range` in transformed space:

```r
# Correct: range in log10 space
penalty <- function(range = c(-10, 0), trans = transform_log10()) {
  new_quant_param(
    type = "double",
    range = range,  # -10 to 0 in log10 space
    ...
  )
}
# Actual values: 10^-10 to 10^0

# Wrong: mixing actual and transformed
penalty <- function(range = c(0.0000000001, 1), trans = transform_log10()) {
  # This would be interpreted as 10^0.0000000001 to 10^1 = 1.0000... to 10
}
```

### Use unknown() for Data-Dependent Bounds

When bounds depend on dataset characteristics:

```r
# Correct: upper bound unknown
mtry <- function(range = c(1L, unknown()), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = get_p
  )
}

# Avoid: guessing upper bound
mtry <- function(range = c(1L, 1000L), trans = NULL) {
  # What if dataset has 2000 predictors?
}
```

### Use Inclusive Endpoints by Default

Most parameters should include both endpoints:

```r
# Default (most common)
inclusive = c(TRUE, TRUE)

# Only use exclusive when necessary
inclusive = c(FALSE, FALSE)  # E.g., probabilities strictly between 0 and 1
```

---

## Label Formatting

### Pattern: "{Noun} {Descriptor}"

```r
label = c(penalty = "Amount of Regularization")
label = c(learn_rate = "Learning Rate")
label = c(mtry = "# Randomly Selected Predictors")
label = c(num_comp = "# Principal Components")
label = c(activation = "Activation Function")
```

**Guidelines**:

- Use title case

- Start with noun or count (#)

- Be concise but descriptive

- Avoid articles ("the", "a")

- Use # for counts

- Match parameter semantics

**Examples**:

```r
# Good
c(penalty = "Amount of Regularization")
c(trees = "# Trees")
c(threshold = "Classification Threshold")
c(weight_func = "Distance Weighting Function")

# Avoid
c(penalty = "The penalty parameter")      # Has article
c(trees = "Number of trees in forest")    # Too verbose
c(threshold = "threshold")                 # Not title case
c(weight_func = "distance weight func")    # Inconsistent case
```

---

## Documentation Patterns

### Use @inheritParams

Inherit common parameter documentation from constructors:

```r
#' My parameter
#'
#' Description of what this parameter controls.
#'
#' @inheritParams new_quant_param
#' @param range A two-element vector with the lower and upper bounds.
#'
#' @export
my_param <- function(range = c(0, 1), trans = NULL) {
  new_quant_param(
    type = "double",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_param = "My Parameter"),
    finalize = NULL
  )
}
```

Common inherited parameters:

- `trans`: Transformation object

- `label`: Display name

- `finalize`: Finalization function

### Use @seealso for Related Parameters

Link to related parameters:

```r
#' @seealso [penalty()], [mixture()]
#' @seealso [learn_rate()], [momentum()]
#' @seealso [activation()], [activation_2()]
```

### Use @details for Important Information

Explain transformation units, finalization logic, or usage context:

```r
#' @details
#' This parameter uses a log10 transformation, so the range is specified
#' in log10 units. The default range of c(-10, 0) represents actual penalty
#' values from 10^-10 to 1.
#'
#' @details
#' The upper bound is set to `unknown()` and must be finalized with training
#' data using `finalize()`. The finalization function sets the upper bound to
#' the number of predictors in the dataset.
```

### Use @examples with Practical Usage

Show how to use the parameter:

```r
#' @examples
#' penalty()
#' penalty(range = c(-5, 0))
#'
#' # Generate grid
#' grid_regular(penalty(), levels = 5)
#'
#' # Sample values
#' set.seed(123)
#' value_sample(penalty(), n = 5)
#'
#' # Use in model specification
#' linear_reg(penalty = tune()) %>%
#'   set_engine("glmnet")
```

---

## Creating Companion values_* Vectors

### Always Create for Qualitative Parameters

**Convention**: Create separate `values_[param_name]` vector:

```r
#' Activation function
#'
#' The activation function for neural networks.
#'
#' @param values A character vector of possible activation functions.
#'
#' @examples
#' values_activation
#' activation()
#' activation(values = c("relu", "sigmoid"))
#'
#' @export
activation <- function(values = values_activation) {
  new_qual_param(
    type = "character",
    values = values,
    label = c(activation = "Activation Function")
  )
}

#' @rdname activation
#' @export
values_activation <- c(
  "relu", "sigmoid", "tanh", "softmax",
  "elu", "selu", "softplus", "softsign"
)
```

### Link with @rdname

Use `@rdname` to document vector and function together:

```r
#' @rdname parameter_name
#' @export
values_parameter_name <- c("option1", "option2", "option3")
```

### Export Both

Both the parameter function and values vector should be exported:

```r
#' @export
activation <- function(values = values_activation) { ... }

#' @rdname activation
#' @export
values_activation <- c(...)
```

---

## When to Create Parameter Variants

### Create Variants When

**Different scales or units**:

```r
mtry()           # Integer count
mtry_prop()      # Proportion of predictors
```

**Different contexts or layers**:

```r
activation()     # Hidden layer activation
activation_2()   # Output layer activation
```

**Different calculation methods**:

```r
sample_size()    # Absolute count
sample_prop()    # Proportion of observations
```

### Don't Create Variants When

**Just different ranges**: Let users customize the range

```r
# Don't create
penalty_small()  # range c(-5, 0)
penalty_large()  # range c(-10, 5)

# Instead, let users specify
penalty(range = c(-5, 0))
penalty(range = c(-10, 5))
```

**Transformation is the only difference**: Let users customize

```r
# Don't create
cost_log()       # With transformation
cost_linear()    # Without transformation

# Instead, let users specify
cost(trans = transform_log())
cost(trans = NULL)
```

---

## Universal Best Practices

These best practices apply to all R package development in Tidymodels:

### Use Base Pipe |>

**Do**: Use base pipe `|>`

```r
finalized <- param |>
  finalize(train_data) |>
  update(penalty = penalty(range = c(-5, -1)))
```

**Don't**: Use magrittr pipe `%>%`

```r
# Avoid
finalized <- param %>%
  finalize(train_data) %>%
  update(penalty = penalty(range = c(-5, -1)))
```

### Prefer for-loops Over purrr::map()

**Do**: Use for-loops for iteration

```r
results <- vector("list", length(params))
for (i in seq_along(params)) {
  results[[i]] <- process_param(params[[i]])
}
```

**Don't**: Use purrr functional programming

```r
# Avoid
results <- purrr::map(params, process_param)
```

### Use cli::cli_abort() for Errors

**Do**: Use cli for error messages

```r
if (invalid_condition) {
  cli::cli_abort(
    "The range for {.arg param_name} is invalid.",
    "i" = "Lower bound must be less than upper bound."
  )
}
```

**Don't**: Use base stop()

```r
# Avoid
stop("The range is invalid")
```

### Follow Tidyverse Style Guide

- Use snake_case for functions and variables

- Use 2-space indentation

- Limit line length to 80 characters

- Use meaningful variable names

See [Tidyverse Style Guide](https://style.tidyverse.org/) for complete guidelines.

---

## Parameter-Specific Best Practices

### Choose Appropriate Defaults

**Wide ranges** are better (users can narrow):

```r
# Good: Wide default range
penalty <- function(range = c(-10, 0), trans = transform_log10()) {
  # Covers 10^-10 to 1
}

# Avoid: Too narrow
penalty <- function(range = c(-3, -1), trans = transform_log10()) {
  # Only 10^-3 to 10^-1, might miss optimal values
}
```

**Match literature and practice**:

```r
# Good: Matches common usage
learn_rate <- function(range = c(-5, -1), trans = transform_log10()) {
  # 10^-5 to 10^-1 is typical for learning rates
}
```

### Document Range Units Clearly

When using transformations, explain range units:

```r
#' @param range A two-element vector with the lower and upper bounds
#'   (in log10 units). Default c(-10, 0) represents values from 10^-10 to 1.
```

### Use Integer Type for Counts

```r
# Correct
num_trees <- function(range = c(1L, 2000L), trans = NULL) {
  new_quant_param(
    type = "integer",  # Correct for counts
    ...
  )
}

# Incorrect
num_trees <- function(range = c(1, 2000), trans = NULL) {
  new_quant_param(
    type = "double",  # Wrong for counts
    ...
  )
}
```

### Test with Real Data

When creating finalization functions, test with realistic data:

```r
get_custom_bound <- function(object, x) {
  # Calculate bound based on data properties
  p <- ncol(x)
  n <- nrow(x)

  # Use domain knowledge
  upper <- min(100, floor(sqrt(n) * p))

  # Update range
  bounds <- range_get(object)
  bounds$upper <- upper
  range_set(object, bounds)
}
```

---

## PR Best Practices

### Before Submitting

1. **Run all checks**: `devtools::check()`
2. **Run spell check**: `devtools::spell_check()`
3. **Update NEWS.md**: Add entry for new parameter
4. **Accept snapshots**: `testthat::snapshot_accept()`
5. **Run tests**: Ensure all tests pass

### NEWS.md Format

Add entry under "Development" section:

```markdown
## Development

* New parameter `my_parameter()` for controlling [feature] (#PR_NUMBER).
```

### Commit Messages

Follow conventional commit style:

```
feat: add my_parameter() for [use case]

This parameter controls [what] and is used for [when].
The upper bound is finalized using [method].
```

### PR Description

Include:

- What parameter was added

- Why it's needed

- Example usage

- Related issues

---

## Common Patterns Reference

### Simple Integer Parameter

```r
num_neighbors <- function(range = c(1L, 15L), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(num_neighbors = "# Nearest Neighbors"),
    finalize = NULL
  )
}
```

### Log-Transformed Parameter

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
```

### Data-Dependent Parameter

```r
mtry <- function(range = c(1L, unknown()), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = get_p
  )
}
```

### Custom Finalization

```r
my_param <- function(range = c(1L, unknown()), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(my_param = "My Parameter"),
    finalize = get_my_bound
  )
}

get_my_bound <- function(object, x) {
  upper <- calculate_from_data(x)
  bounds <- range_get(object)
  bounds$upper <- upper
  range_set(object, bounds)
}
```

### Qualitative Parameter

```r
activation <- function(values = values_activation) {
  new_qual_param(
    type = "character",
    values = values,
    label = c(activation = "Activation Function")
  )
}

#' @rdname activation
#' @export
values_activation <- c("relu", "sigmoid", "tanh", "softmax")
```

---

## Checklist for New Parameter

Before submitting PR:

**Code**:

- [ ] File named `R/param_[name].R`

- [ ] Function name matches convention

- [ ] Uses appropriate constructor

- [ ] Range in correct units (transformed if applicable)

- [ ] Includes `@export` tag

- [ ] No `dials::` prefix (source development)

**Documentation**:

- [ ] Uses `@inheritParams` for common arguments

- [ ] Includes `@details` explaining usage

- [ ] Includes `@examples` with practical usage

- [ ] Uses `@seealso` for related parameters

- [ ] Label follows "{Noun} {Descriptor}" pattern

- [ ] Companion `values_*` vector for qualitative (with `@rdname`)

**Testing**:

- [ ] Tests in `test-params.R`

- [ ] Invalid argument tests in `test-constructors.R`

- [ ] Finalization tests if applicable

- [ ] Grid integration tests

- [ ] All tests pass: `devtools::test()`

**Package Checks**:

- [ ] `devtools::check()` passes

- [ ] `devtools::spell_check()` passes

- [ ] NEWS.md updated

- [ ] Snapshots accepted

**Git**:

- [ ] Descriptive commit messages

- [ ] Branch named clearly

- [ ] PR description complete

---

## Next Steps

### Learn More

- **Testing**: [Testing Patterns (Source)](testing-patterns-source.md)

- **Troubleshooting**: [Troubleshooting (Source)](troubleshooting-source.md)

- **Source guide**: [Source Development Guide](source-guide.md)

### External Resources

- [Tidyverse Style Guide](https://style.tidyverse.org/)

- [R Packages Book](https://r-pkgs.org/)

- [roxygen2 Documentation](https://roxygen2.r-lib.org/)

---

**Last Updated:** 2026-03-31
