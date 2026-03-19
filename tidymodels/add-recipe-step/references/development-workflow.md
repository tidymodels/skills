# Development Workflow

This guide covers the efficient development workflow for R package development.

## The Fast Iteration Cycle

**IMPORTANT:** Follow this workflow to develop efficiently.

### During Development (Fast Iteration Cycle)

Run these commands repeatedly while developing:

1. **`devtools::document()`** - Generate documentation from roxygen2 comments
   - Updates `man/` directory
   - Updates `NAMESPACE` with exports and imports
   - Takes seconds to run

2. **`devtools::load_all()`** - Load your package into memory
   - Equivalent to library(yourpackage) but uses development version
   - Loads all functions, even unexported ones
   - Takes seconds to run

3. **`devtools::test()`** - Run all tests
   - Runs testthat test suite
   - Takes seconds to minutes depending on test count
   - For single file: `devtools::test_active_file('R/yourfile.R')`

**This cycle is fast (seconds) and gives you immediate feedback.**

### Why This Works

```r
# Typical workflow:
devtools::document()   # Update docs and namespace
devtools::load_all()   # Load updated code
devtools::test()       # Verify it works

# Test your function interactively
your_function(test_data)

# Find issue, fix code, repeat
```

This tight feedback loop lets you:
- Catch errors immediately
- Test interactively
- Iterate quickly on design

## Final Validation (Run Once at End)

4. **`devtools::check()`** - Full R CMD check

**WARNING:** Do NOT run `check()` during iteration.

### Why avoid check() during development?

- Takes 1-2 minutes (sometimes longer)
- Runs many validations unnecessary during development
- Interrupts your flow
- Everything it checks is validated by the fast cycle

### When to run check()

**Only run check() once at the very end:**
- Before submitting to CRAN
- Before creating a release
- Before final code review
- After all development is complete

`check()` validates:
- Package structure
- Documentation completeness
- Code quality
- Examples run correctly
- Tests pass
- No NOTEs or WARNINGs

## Interactive Development

### Testing individual functions

```r
# Load your package
devtools::load_all()

# Test your function
result <- your_function(mtcars, mpg, hp)
result

# Check intermediate values
debug(your_function)
your_function(mtcars, mpg, hp)
```

### Using browser() for debugging

```r
your_function <- function(data, ...) {
  # Add browser() where you want to pause
  browser()

  # Rest of function
}

# Run function - it will pause at browser()
your_function(test_data)
```

## Common Workflow Patterns

### Pattern 1: New Function Development

```r
# 1. Write function in R/your-file.R
# 2. Add roxygen documentation
# 3. Document and load
devtools::document()
devtools::load_all()

# 4. Test interactively
your_function(test_data)

# 5. Write formal tests in tests/testthat/test-your-file.R
# 6. Run tests
devtools::test()

# 7. Fix issues, go to step 3
```

### Pattern 2: Fixing a Bug

```r
# 1. Write a failing test that demonstrates the bug
# 2. Run tests to confirm failure
devtools::test()

# 3. Fix the code
# 4. Document and load
devtools::document()
devtools::load_all()

# 5. Verify test now passes
devtools::test()
```

### Pattern 3: Updating Documentation

```r
# 1. Update roxygen comments in R code
# 2. Regenerate documentation
devtools::document()

# 3. Preview documentation
?your_function

# 4. Repeat until satisfied
```

## Keyboard Shortcuts (RStudio)

Speed up your workflow with keyboard shortcuts:

- `Cmd/Ctrl + Shift + D` - `devtools::document()`
- `Cmd/Ctrl + Shift + L` - `devtools::load_all()`
- `Cmd/Ctrl + Shift + T` - `devtools::test()`
- `Cmd/Ctrl + Shift + E` - `devtools::check()`

## Best Practices

### DO:
- Run the fast cycle (document, load, test) frequently
- Test interactively in console
- Write tests as you develop
- Fix issues immediately when found
- Use `browser()` for complex debugging

### DON'T:
- Run `check()` during development (only at end)
- Skip writing tests "for later" (write them now)
- Ignore warnings from `document()` or `test()`
- Make many changes before testing
- Commit broken code to git

## Troubleshooting

### "could not find function"

**Problem:** Function exists in R code but not loaded

**Solution:** Run `devtools::load_all()`

### "object not found in namespace"

**Problem:** Missing `@export` in roxygen or namespace not updated

**Solution:**
```r
# Add @export to your roxygen block
devtools::document()  # Update namespace
devtools::load_all()  # Load updated package
```

### Tests fail but function works interactively

**Problem:** Test environment differs from interactive environment

**Solution:**
- Check test data setup
- Verify all required packages loaded in tests
- Use `devtools::load_all()` before interactive testing

### "no visible binding for global variable"

**Problem:** Using NSE without proper imports

**Solution:** See [package-imports.md](package-imports.md) for proper namespace usage

## Performance Tips

### Speed up test runs

```r
# Run only one test file
devtools::test_active_file()

# Run only tests matching a pattern
devtools::test(filter = "your_function")
```

### Skip slow tests during development

```r
test_that("slow integration test", {
  skip_if_not(interactive(), "Slow test - run manually")

  # Expensive test here
})
```

### Use testthat snapshots for complex output

```r
test_that("complex output matches", {
  expect_snapshot(your_function(data))
})
```

## Git Workflow (Source Development)

If you're contributing to tidymodels packages (recipes, yardstick, etc.), you'll also need basic git workflow.

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/tidymodels/recipes.git
cd recipes

# Create a feature branch
git checkout -b feature/add-step-name
```

### During Development

```r
# Your fast iteration cycle (unchanged)
devtools::document()
devtools::load_all()
devtools::test()
```

### Committing Changes

```bash
# Check what changed
git status
git diff

# Add your changes
git add R/step_name.R tests/testthat/test-step_name.R

# Commit with descriptive message
git commit -m "Add step_name() for [brief description]"

# Push to your fork
git push origin feature/add-step-name
```

### Before Submitting PR

1. Run full check: `devtools::check()`
2. Update `NEWS.md` with your changes
3. Ensure all tests pass
4. Push final commits

### Common Git Commands

```bash
# See current branch
git branch

# Switch branches
git checkout main

# Update from upstream
git pull origin main

# View commit history
git log --oneline
```

**Note:** This is a minimal git guide. For complete git documentation, see the official Git documentation or GitHub guides.

---

## Next Steps

- Learn testing patterns: [testing-patterns-extension.md](testing-patterns-extension.md)
- Set up proper documentation: [roxygen-documentation.md](roxygen-documentation.md)
- Follow best practices: [best-practices-extension.md](best-practices-extension.md)
