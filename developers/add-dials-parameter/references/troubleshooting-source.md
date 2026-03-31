# Troubleshooting (Source Development)

**Common issues and solutions for dials source development**

This guide covers troubleshooting specific to contributing parameters to the dials package.

---

## Common Parameter Issues

### Issue 1: Range Must Have Length 2

**Error**:

```
Error: The range must have length 2
```

**Cause**: Range provided as single value or vector of wrong length

**Solution**: Provide two-element vector

```r
# Wrong
my_param <- function(range = 0) { ... }
my_param <- function(range = c(0, 0.5, 1)) { ... }

# Correct
my_param <- function(range = c(0, 1)) { ... }
```

---

### Issue 2: Lower Bound Must Be Less Than Upper Bound

**Error**:

```
Error: The range for 'param' is invalid: lower bound (1) must be less than upper bound (0)
```

**Cause**: Range specified backwards

**Solution**: Swap values

```r
# Wrong
my_param(range = c(1, 0))

# Correct
my_param(range = c(0, 1))
```

---

### Issue 3: Type Mismatch Between type and values

**Error**:

```
Error: The values for 'param' must be character
```

**Cause**: Qualitative parameter has `type = "character"` but `values` are numeric or wrong type

**Solution**: Ensure type matches values

```r
# Wrong
activation <- function(values = c(1, 2, 3)) {
  new_qual_param(
    type = "character",  # Type says character
    values = values,     # But values are numeric
    ...
  )
}

# Correct
activation <- function(values = values_activation) {
  new_qual_param(
    type = "character",
    values = values,  # Character vector
    ...
  )
}

values_activation <- c("relu", "sigmoid", "tanh")
```

---

### Issue 4: Grid Values Look Wrong with Transformation

**Problem**: Generated grid values don't match expected range

**Cause**: Range specified in actual units but transformation expects transformed units

**Example**:

```r
# Wrong: Range in actual units with transformation
penalty <- function(range = c(0.0000000001, 1), trans = transform_log10()) {
  # This will be interpreted as 10^0.0000000001 to 10^1 = 1.00... to 10
  # NOT 0.0000000001 to 1
}

grid <- grid_regular(penalty(), levels = 5)
grid$penalty
#> [1] 1.000000 1.778279 3.162278 5.623413 10.000000
#> Wrong! These are way too large

# Correct: Range in transformed (log10) units
penalty <- function(range = c(-10, 0), trans = transform_log10()) {
  # Range in log10 space: -10 to 0
  # Actual values: 10^-10 to 10^0
}

grid <- grid_regular(penalty(), levels = 5)
grid$penalty
#> [1] 1e-10 1e-07 1e-04 1e-01 1e+00
#> Correct!
```

**Solution**: Always specify range in **transformed space** when using transformations

---

### Issue 5: Parameter Won't Finalize

**Error**:

```
Error: Can't finalize parameter with no finalize function
```

**Cause**: Parameter has `unknown()` but no `finalize` function

**Solution**: Provide finalize function

```r
# Wrong
mtry <- function(range = c(1L, unknown()), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = NULL  # Missing finalize!
  )
}

# Correct
mtry <- function(range = c(1L, unknown()), trans = NULL) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),
    trans = trans,
    label = c(mtry = "# Randomly Selected Predictors"),
    finalize = get_p  # Finalize function provided
  )
}
```

---

### Issue 6: Can't Generate Grid with Unknown Bound

**Error**:

```
Error: Can't generate grid when range includes unknown values
```

**Cause**: Trying to generate grid before finalizing parameter

**Solution**: Finalize parameter with data first

```r
# Wrong
param <- mtry()
grid <- grid_regular(param, levels = 5)
#> Error: Can't generate grid...

# Correct
param <- mtry()
finalized <- finalize(param, train_data)
grid <- grid_regular(finalized, levels = 5)
```

---

### Issue 7: Integer Range Produces No Valid Values

**Problem**: Integer parameter with exclusive bounds produces no or very few valid values

**Example**:

```r
my_param <- function(range = c(1L, 3L)) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(FALSE, FALSE),  # Both excluded
    ...
  )
}

# Only value 2 is valid!
# If grid needs 5 levels, error or duplicate values
```

**Solution**: Use inclusive bounds or wider range for integer parameters

```r
# Option 1: Use inclusive bounds
my_param <- function(range = c(1L, 3L)) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(TRUE, TRUE),  # Include endpoints
    ...
  )
}
# Valid values: 1, 2, 3

# Option 2: Wider range
my_param <- function(range = c(1L, 20L)) {
  new_quant_param(
    type = "integer",
    range = range,
    inclusive = c(FALSE, FALSE),
    ...
  )
}
# Valid values: 2, 3, 4, ..., 19 (plenty of values)
```

---

### Issue 8: Snapshot Mismatch

**Error** (during tests):

```
Error: Snapshot mismatch
! Snapshot error messages don't match
```

**Cause**: Error message changed, or snapshot needs to be created/updated

**Solution**: Review changes and accept snapshots

```r
# Run tests to see differences
devtools::test()

# If changes are intentional, accept snapshots
testthat::snapshot_accept()

# Run tests again to confirm
devtools::test()
```

---

## PR-Specific Issues

### Issue 9: Documentation Check Failures

**Error**:

```
checking Rd cross-references ... WARNING
Missing link or links in documentation object 'my_parameter.Rd':
  'some_function()'
```

**Cause**: Documentation references function that doesn't exist or isn't linked correctly

**Solution**: Fix roxygen cross-references

```r
# Wrong
#' @seealso some_function()

# Correct (use square brackets for links)
#' @seealso [some_function()]

# Or if from another package
#' @seealso [other_package::some_function()]
```

---

### Issue 10: NEWS.md Format

**Issue**: PR check fails due to NEWS.md format

**Correct format**:

```markdown
## Development

* New parameter `my_parameter()` for controlling feature selection (#123).
* Fixed bug in `other_function()` (#124).

## dials 1.2.0

* Previous release notes...
```

**Guidelines**:

- Add entry under "Development" section
- Use backticks for code
- Include PR number in parentheses
- Keep entries concise
- Use present tense

---

### Issue 11: Alphabetical Ordering in test-params.R

**Issue**: Tests not in alphabetical order

**Cause**: New parameter test added in wrong location

**Solution**: Place test in alphabetical order

```r
# test-params.R

# ... earlier parameters ...

test_that("mixture range validation", {
  # Tests for mixture
})

# Add new parameter here (between mixture and penalty)
test_that("my_parameter range validation", {
  # Tests for my_parameter
})

test_that("penalty range validation", {
  # Tests for penalty
})

# ... later parameters ...
```

---

### Issue 12: devtools::check() Failures

**Common check failures**:

**1. Undocumented exports**:

```
checking for missing documentation entries ... WARNING
Undocumented code objects:
  'my_parameter'
```

**Solution**: Add roxygen documentation with `@export`

```r
#' My parameter
#'
#' Description...
#'
#' @export
my_parameter <- function(...) { ... }
```

**2. Examples fail**:

```
checking examples ... ERROR
Error in my_parameter() : object 'values_my_parameter' not found
```

**Solution**: Ensure companion vector is exported

```r
#' @rdname my_parameter
#' @export
values_my_parameter <- c("option1", "option2")
```

**3. Namespace conflicts**:

```
checking package namespace information ... WARNING
Object 'my_function' is imported from 'pkg' but is not used
```

**Solution**: Remove unused imports from NAMESPACE (regenerate with `devtools::document()`)

---

## Universal Issues

These issues also apply to extension development. See [Common Issues & Solutions](package-extension-requirements.md#common-issues-solutions) for details.

### Issue: could not find function

**Error**:

```
Error: could not find function "my_parameter"
```

**Solution**:

```r
devtools::load_all()  # Reload package
```

---

### Issue: object not found in namespace

**Error**:

```
Error: object 'my_parameter' is not exported by 'namespace:dials'
```

**Solution**: Add `@export` to function documentation

```r
#' @export
my_parameter <- function(...) { ... }
```

Then regenerate documentation:

```r
devtools::document()
```

---

### Issue: Test failures

**Problem**: Tests pass locally but fail in CI

**Common causes**:

1. **Missing set.seed()**: Random tests need seeds

```r
# Add seed before random operations
test_that("random grid works", {
  set.seed(123)  # Add this
  grid <- grid_random(param, size = 10)
  ...
})
```

2. **Platform-specific paths**: Use `testthat::test_path()`

```r
# Wrong
file.path("tests", "testthat", "fixtures", "data.csv")

# Correct
testthat::test_path("fixtures", "data.csv")
```

3. **Floating point precision**: Use `expect_equal()` with tolerance

```r
# Wrong
expect_equal(result, 0.123456789)

# Correct
expect_equal(result, 0.123456789, tolerance = 1e-7)
```

---

## Debugging Strategies

### Strategy 1: Interactive Debugging

Load package and test functions interactively:

```r
devtools::load_all()

# Test parameter creation
param <- my_parameter()
param

# Test finalization
finalized <- finalize(param, mtcars[, -1])
finalized

# Test grid generation
grid <- grid_regular(finalized, levels = 5)
grid
```

### Strategy 2: Check Parameter Structure

Inspect parameter object:

```r
param <- my_parameter()

# Check class
class(param)

# Check structure
str(param)

# Check specific properties
param$type
param$range
param$inclusive
param$trans
param$finalize
```

### Strategy 3: Test Finalization Step-by-Step

For data-dependent parameters:

```r
param <- my_parameter()

# Before finalization
print(param$range)

# Finalize
test_data <- mtcars[, -1]
finalized <- finalize(param, test_data)

# After finalization
print(finalized$range)

# Check bounds are sensible
stopifnot(finalized$range$lower <= finalized$range$upper)
stopifnot(!inherits(finalized$range$upper, "unknown"))
```

### Strategy 4: Test Transformation

For transformed parameters:

```r
param <- penalty()

# Generate grid
grid <- grid_regular(param, levels = 5)

# Check transformed values
print(grid$penalty)

# Check log10 spacing
log_vals <- log10(grid$penalty)
print(log_vals)

# Should be evenly spaced
diffs <- diff(log_vals)
print(diffs)
```

### Strategy 5: Isolate Test Failures

Run individual tests:

```r
# Run specific test file
testthat::test_file("tests/testthat/test-params.R")

# Run specific test
testthat::test_file(
  "tests/testthat/test-params.R",
  filter = "my_parameter"
)

# Run with reporter for more detail
testthat::test_file(
  "tests/testthat/test-params.R",
  reporter = "progress"
)
```

---

## Getting Help

### Before Asking for Help

1. **Check existing parameters**: Look at similar parameters in `R/param_*.R`
2. **Read error messages carefully**: Often point to exact issue
3. **Test interactively**: Use `devtools::load_all()` and test functions
4. **Check documentation**: Review roxygen and parameter properties
5. **Run devtools::check()**: See all issues at once

### Where to Ask

1. **GitHub Issues**: [tidymodels/dials issues](https://github.com/tidymodels/dials/issues)
2. **GitHub Discussions**: [tidymodels discussions](https://github.com/tidymodels/tidymodels/discussions)
3. **RStudio Community**: [Tidymodels category](https://community.rstudio.com/c/ml/15)

### What to Include

When asking for help, include:

1. **Minimal reproducible example**:

```r
library(dials)

# Parameter definition
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

# Problem
param <- my_param()
grid <- grid_regular(param, levels = 5)
# Error: ...
```

2. **Error message** (full text)
3. **What you've tried**
4. **Expected vs actual behavior**
5. **Session info**: `sessionInfo()` or `devtools::session_info()`

---

## Quick Reference

### Most Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Range error | Wrong length or order | Two-element vector, lower < upper |
| Type mismatch | values type ≠ type arg | Match types |
| Grid values wrong | Range in actual units with trans | Range in transformed units |
| Won't finalize | No finalize function | Add finalize = get_p or custom |
| Can't generate grid | Unknown not finalized | finalize(param, data) first |
| Snapshot mismatch | Error message changed | testthat::snapshot_accept() |

### Quick Fixes

```r
# Reload package
devtools::load_all()

# Regenerate docs
devtools::document()

# Run tests
devtools::test()

# Accept snapshots
testthat::snapshot_accept()

# Full check
devtools::check()

# Spell check
devtools::spell_check()
```

---

## Checklist for Debugging

When encountering an issue:

- [ ] Read error message completely
- [ ] Check parameter structure with `str(param)`
- [ ] Test interactively with `devtools::load_all()`
- [ ] Review similar existing parameters
- [ ] Check roxygen documentation is complete
- [ ] Verify tests are in correct file
- [ ] Run `devtools::check()` for all issues
- [ ] Search GitHub issues for similar problems
- [ ] Create minimal reproducible example
- [ ] Ask for help with complete information

---

## Next Steps

### Learn More

- **Best practices**: [Best Practices (Source)](best-practices-source.md)
- **Testing**: [Testing Patterns (Source)](testing-patterns-source.md)
- **Source guide**: [Source Development Guide](source-guide.md)

### External Resources

- [dials GitHub Issues](https://github.com/tidymodels/dials/issues)
- [R Packages Book - Debugging](https://r-pkgs.org/code.html#debugging)
- [Tidymodels Community](https://community.rstudio.com/c/ml/15)

---

**Last Updated:** 2026-03-31
