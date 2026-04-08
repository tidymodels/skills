# Understanding Recipe Step Architecture

Before implementing a recipe step, understand the recipe step architecture and
workflow.

> **Note for Source Development:** If you're contributing directly to the
> recipes package, you can use internal helper functions like
> `recipes_eval_select()`, `check_type()`, and `get_case_weights()` without the
> `recipes::` prefix. See the [Source Development Guide](source-guide.md) for
> details.

**Reference implementations showing complete architecture:**

- Simple steps: `R/center.R`, `R/scale.R` (modify-in-place pattern)

- Complex steps: `R/dummy.R`, `R/pca.R` (create-new-columns pattern)

- Row operations: `R/filter.R`, `R/sample.R` (skip behavior)

## The Three-Function Pattern

Every recipe step consists of three functions:

### 1. Step constructor (e.g., `step_center()`)

User-facing function that:

- Captures user arguments

- Uses `enquos(...)` to capture variable selections

- Returns recipe with step added via `add_step()`

```r
step_center <- function(recipe, ..., role = NA, trained = FALSE,
                        means = NULL, na_rm = TRUE, skip = FALSE,
                        id = rand_id("center")) {
  add_step(
    recipe,
    step_center_new(
      terms = enquos(...),
      role = role,
      trained = trained,
      means = means,
      na_rm = na_rm,
      skip = skip,
      id = id
    )
  )
}
```

### 2. Step initialization (e.g., `step_center_new()`)

Internal constructor that:

- Is a minimal function with no defaults

- Calls `step(subclass = "name", ...)` to create S3 object

```r
step_center_new <- function(terms, role, trained, means, na_rm, skip, id) {
  step(
    subclass = "center",
    terms = terms,
    role = role,
    trained = trained,
    means = means,
    na_rm = na_rm,
    skip = skip,
    id = id
  )
}
```

### 3. S3 methods

Required methods for every step:

- **`prep.step_*()`** - Estimates parameters from training data

- **`bake.step_*()`** - Applies transformation to new data

- **`print.step_*()`** - Displays step in recipe summary

- **`tidy.step_*()`** - Returns step information as tibble

## The prep/bake Workflow

### prep() - Training phase

Prep resolves variable selections and learns parameters from training data:

```r
prep.step_center <- function(x, training, info = NULL, ...) {
  # 1. Resolve variable selections to actual column names
  col_names <- recipes_eval_select(x$terms, training, info)

  # 2. Validate column types
  check_type(training[, col_names], types = c("double", "integer"))

  # 3. Compute statistics/parameters from training data
  means <- colMeans(training[, col_names], na.rm = x$na_rm)

  # 4. Store learned parameters in step object
  # 5. Return updated step with trained = TRUE
  step_center_new(
    terms = x$terms,
    role = x$role,
    trained = TRUE,
    means = means,
    na_rm = x$na_rm,
    skip = x$skip,
    id = x$id
  )
}
```

**prep() responsibilities:**

- Resolve variable selections (e.g., `all_numeric()` → actual column names)

- Validate column types

- Compute statistics/parameters from training data

- Store learned parameters in step object

- Return updated step with `trained = TRUE`

### bake() - Application phase

Bake applies the transformation using stored parameters:

```r
bake.step_center <- function(object, new_data, ...) {
  # 1. Get column names from trained step
  col_names <- names(object$means)

  # 2. Validate required columns exist in new data
  check_new_data(col_names, object, new_data)

  # 3. Apply transformation using stored parameters
  for (col in col_names) {
    new_data[[col]] <- new_data[[col]] - object$means[[col]]
  }

  # 4. Return modified data
  new_data
}
```

**bake() responsibilities:**

- Takes trained step and new data

- Validates required columns exist

- Applies transformation using stored parameters

- Returns transformed data

### Example workflow

```r
# 1. Define recipe with step
rec <- recipe(mpg ~ ., data = mtcars) |>
  step_center(all_numeric_predictors())

# At this point, step knows to center all numeric predictors
# but hasn't calculated what those means are yet

# 2. prep() trains the step (calculates means from training data)
trained_rec <- prep(rec, training = mtcars)

# Now the step knows the mean of each column

# 3. bake() applies the step (subtracts those means from new data)
new_data <- bake(trained_rec, new_data = test_data)

# New data has been centered using the training means
```

## Step Type Decision Tree

Choose the appropriate template based on what your step does:

### Type 1: Modify-in-Place Steps

**Use when:** Your step transforms existing columns without creating new ones

**Characteristics:**

- `role = NA` (preserves existing roles)

- No `keep_original_cols` parameter

- Returns tibble with same columns (but modified values)

- Examples: `step_center`, `step_scale`, `step_normalize`, `step_log`

**Template:** See [modify-in-place-steps.md](modify-in-place-steps.md)

### Type 2: Create-New-Columns Steps

**Use when:** Your step creates new columns from existing ones

**Characteristics:**

- `role = "predictor"` (default, assigns role to new columns)

- Includes `keep_original_cols` parameter (default `FALSE`)

- Uses `remove_original_cols()` in bake()

- May need `.recipes_estimate_sparsity()` if creating sparse columns

- Examples: `step_dummy`, `step_pca`, `step_interact`, `step_poly`

**Template:** See [create-new-columns-steps.md](create-new-columns-steps.md)

### Type 3: Row-Operation Steps

**Use when:** Your step filters or removes rows

**Characteristics:**

- Default `skip = TRUE` (usually not applied during bake on new data)

- Affects number of rows returned

- Often used for training data only

- Examples: `step_filter`, `step_sample`, `step_naomit`, `step_slice`

**Template:** See [row-operation-steps.md](row-operation-steps.md)

## Key Concepts

### Variable Selection

Steps use tidyselect to let users specify columns:

```r
# By name
step_center(disp, hp)

# By type
step_center(all_numeric())

# By role
step_center(all_predictors())

# Combinations
step_center(all_numeric_predictors())
```

The `prep()` method resolves these selections to actual column names.

### Roles

Columns in recipes have roles:

- `"predictor"` - Used as features

- `"outcome"` - Used as target variable

- `NA` - No specific role

Steps can:

- Preserve roles (`role = NA`)

- Assign roles to new columns (`role = "predictor"`)

- Filter by role (`all_predictors()`)

### Training vs Application

**Training (prep):**

- Learn parameters from training data

- Store parameters in step object

- Happens once

**Application (bake):**

- Apply stored parameters to new data

- Can be called multiple times

- Uses parameters from prep, doesn't relearn

## Case Weights

**INSTRUCTIONS FOR CLAUDE:** Include case weight handling based on operation
type.

### Include Case Weights IF Step Computes Statistics:

**Required when prep() aggregates across rows:**

- ✅ Mean, median, mode

- ✅ Quantiles, percentiles, quartiles (e.g., 5th, 95th percentile)

- ✅ IQR (interquartile range)

- ✅ Variance, standard deviation

- ✅ Min/Max for scaling/normalization

- ✅ PCA/dimension reduction (uses covariance matrix)

- ✅ Any formula that aggregates across rows

**Why:** These operations produce different results with weighted vs unweighted
data.

**Examples that NEED case weights:**

- step_center() - computes means

- step_normalize() - computes min/max or mean/sd

- step_winsorize() - computes percentiles

- step_bin() - computes quantiles for binning

- step_flag_outliers() - computes Q1, Q3, IQR

- step_range() - computes min/max for scaling

- step_pca() - uses covariance matrix

### Skip Case Weights IF Step Only Does Per-Row Operations:

**Not required when operation is per-row:**

- ❌ Character counting: nchar()

- ❌ NA detection: is.na()

- ❌ Simple comparisons: x < threshold

- ❌ Type conversions: as.character()

- ❌ String manipulation

- ❌ Math operations on individual values: log(), sqrt(), exp()

- ❌ Creating indicators from existing data

- ❌ Polynomial expansion

- ❌ Row filtering without statistics

**Why:** These operations are per-row; weights don't change the result.

**Examples that DON'T need case weights:**

- step_filter_missing() - counts NAs per row

- step_filter_short_text() - counts characters per row

- step_log() - applies log() to each value

- step_dummy() - creates indicators from factors

- step_interact() - multiplies existing columns

- step_poly() - polynomial expansion

### Detection Rule:

Ask: "Does prep() compute a statistic by aggregating across multiple rows?"

- **YES** → Include case weights

- **NO** → Skip case weights entirely

## Common Patterns

### Storing parameters

Store only what's needed:

```r
# Good: store only the means
means <- colMeans(training[, col_names])

# Bad: store entire training data
training_data <- training  # Don't do this!
```

### For-loops over purrr

Use for-loops for better error messages:

```r
# Preferred
for (col in col_names) {
  new_data[[col]] <- transform(new_data[[col]])
}

# Avoid
new_data <- map(col_names, \(col) transform(new_data[[col]]))
```

### Validation early

Validate in prep(), trust in bake():

```r
# prep() validates
check_type(training[, col_names], types = c("double", "integer"))

# bake() trusts and applies
new_data[[col]] <- new_data[[col]] - means[[col]]
```

## Next Steps

- Implement modify-in-place steps:
  [modify-in-place-steps.md](modify-in-place-steps.md)

- Implement create-new-columns steps:
  [create-new-columns-steps.md](create-new-columns-steps.md)

- Implement row-operation steps:
  [row-operation-steps.md](row-operation-steps.md)

- Learn helper functions: [helper-functions.md](helper-functions.md)

- Add optional methods: [optional-methods.md](optional-methods.md)
