# Roxygen Documentation

Guide to documenting R functions using roxygen2 comments.

## Basic Structure

Roxygen comments start with `#'` and appear directly above the function:

```r
#' Short title (one line)
#'
#' Longer description paragraph that explains what the function does
#' in more detail. Can span multiple lines.
#'
#' @param parameter_name Description of parameter
#' @return Description of what the function returns
#' @export
#' @examples
#' # Example code
#' result <- your_function(data)
your_function <- function(parameter_name) {
  # Function body
}
```

## Essential Tags

### @param - Parameter documentation

```r
#' @param data A data frame containing the columns specified by other arguments.
#' @param truth The column identifier for the true results. This should be an
#'   unquoted column name.
#' @param estimate The column identifier for the predicted results. This should
#'   be an unquoted column name.
#' @param na_rm A logical value indicating whether NA values should be stripped
#'   before the computation proceeds. Default is `TRUE`.
#' @param ... Not currently used.
```

**Guidelines:**

- Start with the type (e.g., "A data frame", "A logical value", "A string")

- Explain what it contains or controls

- Note default values if not obvious

- For `...`, state if it's used or not

### @return - Return value documentation

```r
#' @return
#' A tibble with columns `.metric`, `.estimator`, and `.estimate` and 1 row of
#' values.
#'
#' For grouped data frames, the number of rows returned will be the same as the
#' number of groups.
#'
#' For `metric_name_vec()`, a single numeric value (or `NA`).
```

**Guidelines:**

- Describe the structure returned

- Note special behavior (grouped data, NA handling)

- Be specific about column names and types

### @export - Make function available to users

```r
#' @export
your_function <- function() { ... }
```

**When to export:**

- User-facing functions (metrics, steps, utilities)

- S3 methods that users might call

**When NOT to export:**

- Internal helpers

- Implementation functions (`*_impl`, `*_new`)

- Functions users shouldn't call directly

### @examples - Usage examples

```r
#' @examples
#' # Create sample data
#' df <- data.frame(
#'   truth = c(1, 2, 3, 4, 5),
#'   estimate = c(1.1, 2.2, 2.9, 4.1, 5.2)
#' )
#'
#' # Basic usage
#' metric_name(df, truth, estimate)
#'
#' # With case weights
#' df$weights <- c(1, 2, 1, 2, 1)
#' metric_name(df, truth, estimate, case_weights = weights)
```

**For examples requiring optional packages:**
```r
#' @examplesIf rlang::is_installed("modeldata")
#' data(biomass, package = "modeldata")
#' recipe(HHV ~ ., data = biomass) |>
#'   step_yourname(carbon, hydrogen)
```

**Guidelines:**

- Show common use cases

- Include comments explaining what's happening

- Keep examples simple and self-contained

- Use `@examplesIf` for optional dependencies

## Optional but Useful Tags

### @family - Group related functions

```r
#' @family numeric metrics
#' @family class metrics
#' @family preprocessing steps
```

Creates "See Also" links to other functions in the same family.

### @details - Extended explanation

```r
#' @details
#' This metric measures [explanation]. It is particularly useful for
#' [use case].
#'
#' The formula is:
#'
#' \deqn{formula here}
#'
#' When [condition], the metric will [behavior].
```

### @section - Custom sections

```r
#' @section Multiclass:
#'
#' For multiclass problems, this metric uses [explanation of estimator types]:
#' - `macro`: Average per-class metrics equally
#' - `micro`: Aggregate contributions and compute metric
#' - `macro_weighted`: Average per-class metrics weighted by class frequency
```

### @author - Attribution

```r
#' @author Your Name <your.email@example.com>
```

Useful for indicating who created or maintains the function.

### @references - Citations

```r
#' @references
#' Smith, J. (2020). "Metric Name." Journal of Statistics, 12(3), 456-789.
#'
#' https://en.wikipedia.org/wiki/Metric_Name
```

## Complete Templates

### Numeric/Regression Metric

```r
#' Mean Squared Error
#'
#' Calculate the mean squared error between truth and estimate.
#'
#' @family numeric metrics
#'
#' @param data A data frame containing the columns specified by `truth` and
#'   `estimate`.
#' @param truth The column identifier for the true results (numeric). This
#'   should be an unquoted column name.
#' @param estimate The column identifier for the predicted results (numeric).
#'   This should be an unquoted column name.
#' @param na_rm A logical value indicating whether NA values should be stripped
#'   before the computation proceeds. Default is `TRUE`.
#' @param case_weights The optional column identifier for case weights. This
#'   should be an unquoted column name. Default is `NULL`.
#' @param ... Not currently used.
#'
#' @return
#' A tibble with columns `.metric`, `.estimator`, and `.estimate` and 1 row of
#' values.
#'
#' For grouped data frames, the number of rows returned will be the same as the
#' number of groups.
#'
#' For `mse_vec()`, a single numeric value (or `NA`).
#'
#' @details
#' `mse()` is a metric that should be minimized. The output ranges from 0 to
#' Inf, with 0 indicating perfect predictions.
#'
#' The formula for MSE is:
#'
#' \deqn{\frac{1}{n} \sum_{i=1}^{n} (truth_i - estimate_i)^2}
#'
#' @examples
#' # Create sample data
#' df <- data.frame(
#'   truth = c(1, 2, 3, 4, 5),
#'   estimate = c(1.1, 2.2, 2.9, 4.1, 5.2)
#' )
#'
#' # Basic usage
#' mse(df, truth, estimate)
#'
#' # Vector interface
#' mse_vec(df$truth, df$estimate)
#'
#' @export
mse <- function(data, ...) {
  UseMethod("mse")
}
```

### Class/Classification Metric

```r
#' Accuracy
#'
#' Calculate the accuracy of predictions, the proportion of correct predictions.
#'
#' @family class metrics
#'
#' @param data A data frame containing the columns specified by `truth` and
#'   `estimate`.
#' @param truth The column identifier for the true class results (factor). This
#'   should be an unquoted column name.
#' @param estimate The column identifier for the predicted class results
#'   (factor). This should be an unquoted column name.
#' @param estimator One of "binary", "macro", "macro_weighted", or "micro" to
#'   specify the type of averaging to be done. Default is `NULL` which
#'   automatically selects based on the number of classes.
#' @param na_rm A logical value indicating whether NA values should be stripped
#'   before the computation proceeds. Default is `TRUE`.
#' @param case_weights The optional column identifier for case weights. This
#'   should be an unquoted column name. Default is `NULL`.
#' @param event_level A string either "first" or "second" to specify which level
#'   of truth to consider as the "event". Default is "first".
#' @param ... Not currently used.
#'
#' @return
#' A tibble with columns `.metric`, `.estimator`, and `.estimate` and 1 row of
#' values.
#'
#' For grouped data frames, the number of rows returned will be the same as the
#' number of groups.
#'
#' For `accuracy_vec()`, a single numeric value (or `NA`).
#'
#' @section Multiclass:
#'
#' Accuracy extends naturally to multiclass scenarios. The estimator type is
#' automatically set to "multiclass" when there are more than 2 classes.
#'
#' @details
#' `accuracy()` is a metric that should be maximized. The output ranges from 0
#' to 1, with 1 indicating perfect predictions.
#'
#' The formula for binary classification is:
#'
#' \deqn{\frac{TP + TN}{TP + TN + FP + FN}}
#'
#' @examples
#' # Binary classification
#' df <- data.frame(
#'   truth = factor(c("yes", "yes", "no", "no")),
#'   estimate = factor(c("yes", "no", "yes", "no"))
#' )
#'
#' accuracy(df, truth, estimate)
#'
#' # Multiclass
#' df_multi <- data.frame(
#'   truth = factor(c("A", "B", "C", "A", "B", "C")),
#'   estimate = factor(c("A", "B", "A", "A", "C", "C"))
#' )
#'
#' accuracy(df_multi, truth, estimate)
#'
#' @export
accuracy <- function(data, ...) {
  UseMethod("accuracy")
}
```

### Recipe Step

```r
#' Center Numeric Variables
#'
#' `step_center()` creates a *specification* of a recipe step that will
#' normalize numeric data to have a mean of zero.
#'
#' @inheritParams step_center
#' @param recipe A recipe object. The step will be added to the sequence of
#'   operations for this recipe.
#' @param ... One or more selector functions to choose variables for this step.
#'   See [recipes::selections()] for more details.
#' @param role Not used by this step since no new variables are created.
#' @param trained A logical to indicate if the quantities for preprocessing have
#'   been estimated.
#' @param means A named numeric vector of means. This is `NULL` until computed by
#'   [prep()].
#' @param na_rm A logical value indicating whether NA values should be removed
#'   when computing means.
#' @param columns A character vector of column names that will be populated
#'   (eventually) by the [terms] argument. This is `NULL` until computed by
#'   [prep()].
#' @param skip A logical. Should the step be skipped when the recipe is baked by
#'   [bake()]? While all operations are baked when [prep()] is run, some
#'   operations may not be able to be conducted on new data. Care should be
#'   taken when using `skip = TRUE` as it may affect the computations for
#'   subsequent operations.
#' @param id A character string that is unique to this step to identify it.
#'
#' @return An updated version of `recipe` with the new step added to the
#'   sequence of any existing operations.
#'
#' @family normalization steps
#' @export
#'
#' @details
#'
#' Centering data means that the mean of the data is subtracted from each value,
#' resulting in a transformed variable with a mean of zero.
#'
#' The step estimates the means from the data used in the `training` argument
#' of [prep()]. [bake()] then applies the centering to new data sets using
#' these means.
#'
#' # Tidying
#'
#' When you [`tidy()`][recipes::tidy.recipe()] this step, a tibble is returned with
#' columns `terms`, `value`, and `id`:
#'
#' \describe{
#'   \item{terms}{character, the selectors or variables selected}
#'   \item{value}{numeric, the mean of the variable}
#'   \item{id}{character, id of this step}
#' }
#'
#' # Case weights
#'
#' This step performs an unsupervised operation that can utilize case weights.
#' As a result, case weights are used with frequency weights as well as
#' importance weights. For more information, see the documentation in
#' [recipes::case_weights] and the examples on `tidymodels.org`.
#'
#' @examplesIf rlang::is_installed("modeldata")
#' data(biomass, package = "modeldata")
#'
#' biomass_tr <- biomass[biomass$dataset == "Training", ]
#' biomass_te <- biomass[biomass$dataset == "Testing", ]
#'
#' rec <- recipe(
#'   HHV ~ carbon + hydrogen + oxygen + nitrogen + sulfur,
#'   data = biomass_tr
#' )
#'
#' # Center carbon and hydrogen
#' step_centered <- rec |>
#'   step_center(carbon, hydrogen)
#'
#' step_centered
#'
#' # Train the step
#' step_trained <- prep(step_centered, training = biomass_tr)
#'
#' # Apply to test data
#' transformed_te <- bake(step_trained, biomass_te)
#'
#' # Check means are zero
#' mean(transformed_te$carbon)
#' mean(transformed_te$hydrogen)
#'
#' # View learned parameters
#' tidy(step_trained, number = 1)
step_center <- function(
  recipe,
  ...,
  role = NA,
  trained = FALSE,
  means = NULL,
  na_rm = TRUE,
  columns = NULL,
  skip = FALSE,
  id = recipes::rand_id("center")
) {
  # Implementation...
}
```

## Special Formatting

### LaTeX equations

```r
#' \deqn{formula}  # Display equation (centered, separate line)
#' \eqn{inline}    # Inline equation (within text)
```

Examples:
```r
#' \deqn{\frac{1}{n} \sum_{i=1}^{n} (x_i - \bar{x})^2}
#' \eqn{x_i} represents the i-th observation
```

### Code formatting

```r
#' `function_name()` - inline code
#' [package::function()] - link to function
#' \code{code} - alternative inline code
```

### Lists

```r
#' Bullet list:
#' - Item 1
#' - Item 2
#'
#' Numbered list:
#' 1. First
#' 2. Second
```

### Sections

```r
#' @section Title:
#'
#' Content in this section.
```

## Common Mistakes

### Missing parameter documentation

```r
# Bad: undocumented parameter
#' @export
my_function <- function(x, y) { ... }

# Good: all parameters documented
#' @param x Description
#' @param y Description
#' @export
my_function <- function(x, y) { ... }
```

### Inconsistent parameter names

```r
# Bad: documentation doesn't match function signature
#' @param data Data frame
my_function <- function(df) { ... }  # Parameter is 'df', not 'data'

# Good: names match
#' @param df Data frame
my_function <- function(df) { ... }
```

### Using @template without templates

```r
# Bad: @template won't work in user packages
#' @template return-metric

# Good: Write out the documentation
#' @return A tibble with columns `.metric`, `.estimator`, and `.estimate`
```

### Missing @export

If users should call your function, it needs `@export`:

```r
#' @export  # Don't forget this!
user_facing_function <- function() { ... }
```

## Generating Documentation

After writing roxygen comments:

```r
# Generate documentation and update NAMESPACE
devtools::document()
```

This creates:

- `man/*.Rd` files (documentation)

- Updates `NAMESPACE` with exports and imports

## Previewing Documentation

```r
# After documenting
devtools::document()
devtools::load_all()

# View in help
?your_function
```

## Next Steps

- Learn about package imports: [package-imports.md](package-imports.md)

- Follow best practices: [package-best-practices.md](package-best-practices.md)

- Set up testing: [package-testing-patterns.md](package-testing-patterns.md)
