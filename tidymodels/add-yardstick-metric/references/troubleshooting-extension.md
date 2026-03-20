# Troubleshooting Extension Package Development

**Context:** This guide is for **extension development** - creating new packages that extend tidymodels packages.

**Key focus:** Package setup, namespace issues, dependency management, and common errors with external functions.

For source development (contributing to tidymodels packages directly), see the package-specific source guides.

---

Common issues and solutions when developing tidymodels extension packages.

## Build and Check Issues

### "Non-standard files/directories found"

**Symptom:**
```
* checking top-level files ... NOTE
Non-standard files/directories found at top level:
  '.claude' '.here' 'example.R'
```

**Cause:** Hidden files or example files not excluded from package build

**Solution:** Set up `.Rbuildignore`:

```r
# Add common exclusions to .Rbuildignore
writeLines(c(
  "^\\.here$",
  "^\\.claude$",
  "^example.*\\.R$",
  "^.*\\.Rproj$",
  "^\\.Rproj\\.user$"
), ".Rbuildignore", useBytes = TRUE)
```

Or manually edit `.Rbuildignore` to include these patterns.

See [extension-prerequisites.md](extension-prerequisites.md) for details.

### "No visible global function definition"

**Symptom:**
```
checking R code for possible problems ... NOTE
  your_function: no visible global function definition for 'weighted.mean'
  Undefined global functions or variables:
    weighted.mean
```

**Cause:** Using function from base/stats without importing

**Solution:** Add package-level documentation file:

Create `R/{packagename}-package.R`:
```r
#' @keywords internal
#' @importFrom stats weighted.mean
"_PACKAGE"

## usethis namespace: start
## usethis namespace: end
NULL
```

Then run `devtools::document()`.

See [package-imports.md](package-imports.md) for details.

### "No visible binding for global variable"

**Symptom:**
```
checking R code for possible problems ... NOTE
  your_function: no visible binding for global variable 'column_name'
```

**Cause:** Using NSE variables (common with dplyr/ggplot2) without declaring them

**Solution:** Use `.data` pronoun or declare globals:

**Option 1: Use .data pronoun (preferred)**
```r
dplyr::mutate(data, new_col = .data$column_name * 2)
```

**Option 2: Declare global variables**
```r
# In R/{packagename}-package.R
utils::globalVariables(c("column_name", "another_column"))
```

## Function and Object Errors

### "Could not find function"

**Symptom:**
```
Error: could not find function "your_function"
```

**Cause:** Function exists in R code but not loaded

**Solution:**

1. Make sure function has `@export` tag
2. Run `devtools::document()` to update NAMESPACE
3. Run `devtools::load_all()` to load package

### "Object not found in namespace"

**Symptom:**
```
Error: 'your_function' is not an exported object from 'namespace:yourpackage'
```

**Cause:** Missing `@export` in roxygen or namespace not updated

**Solution:**
```r
# Add @export to your roxygen block
#' @export
your_function <- function() { ... }

# Update namespace
devtools::document()

# Load updated package
devtools::load_all()
```

### "Cannot find function 'yardstick_mean'"

**Symptom:**
```
Error: could not find function "yardstick_mean"
```

**Cause:** Using internal yardstick function that's not exported

**Solution:** Use base R alternatives:

```r
# Instead of yardstick_mean() - NOT EXPORTED
if (is.null(case_weights)) {
  mean(values)
} else {
  weighted.mean(values, w = as.double(case_weights))
}
```

See yardstick skill for list of internal vs exported functions.

### "Object is not exported by 'namespace:package'"

**Symptom:**
```
Error: 'internal_function' is not exported by 'namespace:yardstick'
```

**Cause:** Trying to import internal function

**Solution:** Don't use internal functions. Find exported alternatives or implement yourself.

**If you must use internal (not recommended for production):**
```r
# Use ::: (not recommended)
yardstick:::internal_function()
```

## Testing Errors

### Tests fail with "object 'data_altman' not found"

**Symptom:**
```
Error: object 'data_altman' not found
```

**Cause:** Using yardstick internal test data

**Solution:** Create simple test data inline:

```r
# Don't rely on internal helpers
# data <- data_altman()  # NOT EXPORTED

# Create your own test data
test_data <- data.frame(
  truth = c(1, 2, 3, 4, 5),
  estimate = c(1.1, 2.2, 2.9, 4.1, 4.8)
)
```

See [testing-patterns.md](testing-patterns.md) for test data patterns.

### "Could not find function in tests"

**Symptom:**
```
Error in test: could not find function "your_function"
```

**Cause:** Package not loaded before running tests

**Solution:**
```r
# Load package before testing
devtools::load_all()
devtools::test()
```

### Tests pass locally but fail in check()

**Symptom:** Tests work with `devtools::test()` but fail with `devtools::check()`

**Cause:** Test relies on local environment

**Solution:** Make tests self-contained:
- Don't assume specific working directory
- Don't rely on installed packages not in DESCRIPTION
- Don't use external files without checking they exist

## Documentation Errors

### "Cannot find template 'return'"

**Symptom:**
```
Error: Cannot find template 'return'
```

**Cause:** Using `@template return` which doesn't exist in your package

**Solution:** Use explicit `@return` documentation:

```r
# Don't use @template
#' @template return  # Won't work

# Use explicit documentation
#' @return A tibble with columns `.metric`, `.estimator`, and `.estimate`
```

### "Link to unknown function"

**Symptom:**
```
Warning: Link to unknown function 'some_function'
```

**Cause:** Documentation references function that doesn't exist or isn't imported

**Solution:**
- Check spelling
- Make sure function is exported
- Link to correct package: `[package::function()]`

## Method and S3 Errors

### "No applicable method"

**Symptom:**
```
Error: no applicable method for 'metric_name' applied to an object of class "data.frame"
```

**Cause:** Calling `UseMethod()` after `new_*_metric()` or data.frame method not defined

**Solution:** Correct order:

```r
# Correct order
metric_name <- function(data, ...) {
  UseMethod("metric_name")  # First
}

metric_name <- new_numeric_metric(  # Second
  metric_name,
  direction = "minimize",
  range = c(0, Inf)
)

#' @export
#' @rdname metric_name
metric_name.data.frame <- function(data, truth, estimate, ...) {  # Third
  # Implementation
}
```

## Custom Parameter Issues

### "Can't find custom parameter in _vec function"

**Symptom:**
```
Error in metric_vec: argument "threshold" is missing, with no default
```

**Cause:** Custom parameters not passed through `fn_options`

**Solution:** Pass custom parameters via `fn_options`:

```r
#' @export
metric_name.data.frame <- function(data, truth, estimate, threshold = 0.5, ...) {
  numeric_metric_summarizer(
    name = "metric_name",
    fn = metric_name_vec,
    data = data,
    truth = !!rlang::enquo(truth),
    estimate = !!rlang::enquo(estimate),
    fn_options = list(threshold = threshold)  # Pass custom parameter here
  )
}
```

## Dependency Issues

### "Package 'xxx' not available"

**Symptom:**
```
Error: package 'xxx' is not available for this version of R
```

**Cause:** Package not installed or wrong version

**Solution:**
```r
# Install missing package
install.packages("xxx")

# Or add to DESCRIPTION
usethis::use_package("xxx")
```

### "Namespace dependencies not required"

**Symptom:**
```
checking package dependencies ... NOTE
Namespace dependencies not required: 'xxx' 'yyy'
```

**Cause:** Packages imported in NAMESPACE but not used

**Solution:** Remove unused imports from package-level doc, then `devtools::document()`

### "All declared Imports should be used"

**Symptom:**
```
checking dependencies in R code ... NOTE
Package in 'Imports' field not imported from: 'xxx'
```

**Cause:** Package in DESCRIPTION but not used in code

**Solution:** Remove from DESCRIPTION or add proper `@importFrom` declaration

## Performance Issues

### Slow test runs

**Problem:** Tests take too long during development

**Solution:**
```r
# Run only one test file
devtools::test_active_file()

# Run only tests matching a pattern
devtools::test(filter = "your_function")

# Skip slow tests during development
test_that("slow integration test", {
  skip_if_not(interactive(), "Slow test - run manually")

  # Expensive test here
})
```

### Slow check()

**Problem:** `devtools::check()` takes too long

**Reminder:** Don't run `check()` during development!

Use the fast iteration cycle instead:
```r
devtools::document()  # Fast
devtools::load_all()  # Fast
devtools::test()      # Fast (seconds to minutes)
```

Only run `check()` once at the very end.

See [development-workflow.md](development-workflow.md) for details.

## Memory Issues

### "Cannot allocate vector of size"

**Problem:** Running out of memory

**Solution:**
- Don't store entire datasets in objects
- Store only necessary parameters/statistics
- Consider sparse matrices for appropriate data
- Process data in chunks if necessary

## Git and Workflow Issues

### Pre-commit hook fails

**Problem:** Commit fails due to hook

**Solution:** Fix the underlying issue, don't skip hooks:

```r
# DON'T skip hooks
git commit --no-verify  # Bad practice

# DO fix the issue
# - Fix linting errors
# - Fix test failures
# - Then commit normally
```

### Accidentally committed sensitive files

**Problem:** Committed .env or credentials

**Solution:**
1. Remove from git history (complex, search online)
2. Add to .gitignore
3. Rotate compromised credentials immediately

**Prevention:** Set up .gitignore properly from the start

## Getting Help

### Built-in help

```r
# View function documentation
?your_function

# View package documentation
help(package = "yourpackage")

# Search documentation
??search_term
```

### Package debugging

```r
# View function source
your_function

# Debug function
debug(your_function)
your_function(test_data)  # Will pause at start

# Add breakpoint
browser()  # Add this line in function code
```

### External resources

- [R Packages book](https://r-pkgs.org/) - Comprehensive guide
- [Tidymodels developer guide](https://www.tidymodels.org/learn/develop/)
- Package documentation (yardstick, recipes, etc.)
- Stack Overflow with tag `[r]`
- RStudio Community

### When to ask for help

After you've:
1. Read relevant documentation
2. Searched for similar issues
3. Created a minimal reproducible example
4. Tried suggested solutions

### Creating a reproducible example

```r
# Install reprex package
install.packages("reprex")

# Copy your code to clipboard
# Then run:
reprex::reprex()

# Paste the output when asking for help
```

## Quick Reference: Common Commands

```r
# Setup and documentation
devtools::document()      # Update docs and NAMESPACE
devtools::load_all()      # Load package
devtools::test()          # Run tests
devtools::check()         # Full R CMD check (end only)

# Debugging
debug(function_name)      # Step through function
browser()                 # Add breakpoint in code
traceback()              # Show error call stack

# Package management
usethis::use_package("pkg")                # Add dependency
usethis::use_package("pkg", "Suggests")   # Add optional dependency
usethis::use_testthat()                   # Set up testing

# Viewing
?function_name           # Help for function
package_name::          # See package contents (RStudio)
```

## Next Steps

- Review development workflow: [development-workflow.md](development-workflow.md)
- Complete extension prerequisites: [extension-prerequisites.md](extension-prerequisites.md)
- Follow best practices: [best-practices.md](best-practices.md)
- Learn testing patterns: [testing-patterns.md](testing-patterns.md)
