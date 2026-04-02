# Package Imports and Namespace Management

Guide to properly importing functions from other packages and managing your package's namespace.

## The NAMESPACE File

The `NAMESPACE` file controls:

- Which functions your package exports (makes available to users)

- Which functions your package imports from other packages

**Important:** Never edit `NAMESPACE` directly. Let roxygen2 generate it via `devtools::document()`.

## Package-Level Documentation

Create a package-level documentation file to declare imports.

### Create R/{packagename}-package.R

```r
#' @keywords internal
#' @importFrom stats weighted.mean
"_PACKAGE"

## usethis namespace: start
## usethis namespace: end
NULL
```

Replace `{packagename}` with your actual package name (e.g., `R/mymetrics-package.R`).

### What this does

- `@keywords internal` - Marks as internal documentation

- `@importFrom stats weighted.mean` - Imports `weighted.mean` from stats

- `"_PACKAGE"` - Roxygen directive for package-level docs

- `## usethis namespace:` - Markers for usethis to add content

## Common Import Patterns

### Importing specific functions

```r
#' @keywords internal
#' @importFrom stats weighted.mean median sd
#' @importFrom utils head tail
"_PACKAGE"
```

### Importing entire packages (use sparingly)

```r
#' @keywords internal
#' @import rlang
"_PACKAGE"
```

**Warning:** `@import` imports everything from a package. Use `@importFrom` instead to import only what you need.

## When to Add Imports

### R CMD check warnings

If you see warnings like:

```
checking R code for possible problems ... NOTE
  your_function: no visible global function definition for 'weighted.mean'
  Undefined global functions or variables:
    weighted.mean
```

**Solution:** Add import to package-level doc:

```r
#' @importFrom stats weighted.mean
```

### Common packages that need imports

**From `stats`:**
```r
#' @importFrom stats weighted.mean median sd var quantile
```

**From `utils`:**
```r
#' @importFrom utils head tail str
```

**From `grDevices`:**
```r
#' @importFrom grDevices rainbow
```

## Dependencies in DESCRIPTION

Imports in `NAMESPACE` must match dependencies in `DESCRIPTION`.

### Add package dependencies

```r
# For packages you import from
usethis::use_package("rlang")
usethis::use_package("cli")
usethis::use_package("yardstick")

# For optional dependencies (examples, vignettes)
usethis::use_package("ggplot2", type = "Suggests")
usethis::use_package("modeldata", type = "Suggests")
```

This updates `DESCRIPTION`:

```
Imports:
  rlang,
  cli,
  yardstick
Suggests:
  ggplot2,
  modeldata
```

## Calling Functions from Other Packages

### Option 1: Use :: notation (recommended for occasional use)

```r
# Don't need to import, just use ::
result <- dplyr::filter(data, condition)
```

**When to use:**

- Functions used infrequently

- Clarity about where function comes from

- Avoiding namespace conflicts

### Option 2: Import and use directly (recommended for frequent use)

```r
# In R/{packagename}-package.R
#' @importFrom dplyr filter mutate

# In your function code
result <- filter(data, condition) |>
  mutate(new_col = old_col * 2)
```

**When to use:**

- Functions used frequently

- Cleaner, more readable code

- Functions are core to your package

## Special Cases

### Non-standard evaluation (NSE) with tidy eval

For rlang functions:

```r
#' @keywords internal
#' @importFrom rlang :=  !! !!! enquo enquos sym syms
"_PACKAGE"
```

### S3 method registration

If you create S3 methods for other packages' generics:

```r
#' @export
#' @method autoplot your_class
autoplot.your_class <- function(object, ...) {
  # Implementation
}
```

Or use `@export` on the method:

```r
#' @export
autoplot.your_class <- function(object, ...) {
  # Implementation
}
```

### Importing entire packages (last resort)

Only use `@import` for packages designed for it (like rlang):

```r
#' @keywords internal
#' @import rlang
"_PACKAGE"
```

**Avoid `@import` for most packages** - import specific functions instead.

## Workflow

1. **Add dependency to DESCRIPTION:**
   ```r
   usethis::use_package("dplyr")
   ```

2. **Add import to package-level doc:**
   ```r
   #' @importFrom dplyr filter mutate
   ```

3. **Update documentation:**
   ```r
   devtools::document()
   ```

4. **Use function in your code:**
   ```r
   result <- filter(data, condition)
   ```

## Common Issues

### "could not find function"

**Problem:** Function not imported or package not in DESCRIPTION

**Solution:**
1. Add package to DESCRIPTION: `usethis::use_package("package_name")`
2. Add import or use `::` notation
3. Run `devtools::document()`

### "no visible global function definition"

**Problem:** Function used but not imported

**Solution:** Add `@importFrom` to package-level doc

### "no visible binding for global variable"

**Problem:** NSE variables not declared (common with dplyr/ggplot2)

**Solution:** Either:

- Use `.data$column` pronoun: `mutate(.data$new_col = value)`

- Or add `utils::globalVariables()` to package-level doc:
  ```r
  utils::globalVariables(c("column_name", "another_column"))
  ```

### "object is not exported by 'namespace:package'"

**Problem:** Trying to import internal function

**Solution:** Use `:::` (not recommended for production) or find an exported alternative

## Best Practices

### DO:

- Use `@importFrom` to import specific functions

- Add all packages to DESCRIPTION first

- Run `devtools::document()` after changes

- Use `::` for infrequently-used functions

### DON'T:

- Edit NAMESPACE directly

- Use `@import` for most packages

- Import internal functions with `:::`

- Forget to add packages to DESCRIPTION

## Example Package-Level Doc

```r
#' @keywords internal
#' @importFrom stats weighted.mean median sd
#' @importFrom rlang := !! enquo enquos
#' @importFrom cli cli_abort cli_warn
"_PACKAGE"

## usethis namespace: start
## usethis namespace: end
NULL
```

## Checking Your Imports

Run R CMD check to verify:

```r
devtools::check()
```

Look for:

- "no visible global function definition" - add import

- "Namespace dependencies not required" - remove import

- "All declared Imports should be used" - remove unused package

## Next Steps

- Write roxygen documentation: [package-roxygen-documentation.md](package-roxygen-documentation.md)

- Follow best practices: [package-best-practices.md](package-best-practices.md)

- Set up testing: [package-testing-patterns.md](package-testing-patterns.md)
