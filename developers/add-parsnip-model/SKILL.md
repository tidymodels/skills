# Add Parsnip Model

Create entirely new model specifications for the parsnip package. This skill covers creating new model types (like `linear_reg()`, `boost_tree()`) with their constructors, registration, and engine implementations.

**Use this skill when:** Creating a fundamentally new model type for parsnip.

**For adding engines to existing models:** See [add-parsnip-engine](../add-parsnip-engine/SKILL.md) skill instead.

---

## Prerequisites

Before creating a new parsnip model, ensure you have:

**R Package Development:**

- [Extension Prerequisites](references/package-extension-prerequisites.md) - Required for extension packages

- [Development Workflow](references/package-development-workflow.md) - Fast iteration practices

**Parsnip Architecture:**

- [Model Specification System](references/model-specification-system.md) - Core parsnip concepts

- [Fit and Predict Methods](references/fit-predict-methods.md) - Implementation fundamentals

---

## Creating a New Model

### Assess Model Complexity First

Before diving into implementation, determine the complexity of your model:

**Simple Model:**
- Single mode (regression OR classification, not both)
- 1-2 engines
- Few main arguments (1-3)
- Standard prediction types only

→ Follow streamlined approach: Focus on getting the basics right, avoid over-engineering

**Complex Model:**
- Multiple modes (regression AND classification)
- 3+ engines
- Many main arguments
- Custom prediction types or special encoding

→ Reference detailed guides for multi-mode handling, encoding options, and advanced patterns

**Target files regardless of complexity:**
- Extension development: 2-3 files (constructor, tests, optional README)
- Source development: 2-4 files (constructor, data file, tests, optional engine docs)

### 1. Design the Model Specification

**Start here:** [Model Constructor Design](references/model-constructors.md)

Decide on:

- Model name and function (e.g., `sparse_reg()`)

- Which modes to support (regression, classification, both?)

- Main arguments (standardized across engines)

- Default engine

This step defines the user-facing API.

### 2. Understand the Registration System

**Review:** [Model Specification System](references/model-specification-system.md)

Learn how parsnip's registration system works:

- Model environment and storage

- Engine registration database

- Mode handling

- Argument translation

### 3. Implement the Registration Sequence

**Follow:** [Registration Sequence](references/registration-sequence.md)

Complete registration in the correct order:
1. `set_new_model()` - Declare model exists
2. `set_model_mode()` - Declare supported modes
3. `set_model_engine()` - Register each engine
4. `set_dependency()` - Package requirements
5. `set_model_arg()` - Argument translation
6. `set_fit()` - Fitting method
7. `set_encoding()` - Data conversion (if needed)
8. `set_pred()` - Each prediction type

### 4. Design Main Arguments

**Plan carefully:** [Argument Design](references/argument-design.md)

Create standardized arguments that:

- Work across multiple engines

- Map to engine-specific parameters

- Integrate with tune package

- Follow tidymodels conventions

### 5. Implement Fit and Predict

**Core implementation:** [Fit and Predict Methods](references/fit-predict-methods.md)

For each engine:

- Choose interface type (formula, matrix, xy)

- Implement data conversion

- Register fit method

- Register each prediction type with proper column naming

### 6. Handle Prediction Types

**Standardize output:** [Prediction Types](references/prediction-types.md)

Implement appropriate prediction types for each mode:

- Regression: `numeric`, `conf_int`, `pred_int`

- Classification: `class`, `prob`

- Survival: `time`, `survival`, `hazard`, `linear_pred`

- Quantile: `quantile`

### 7. Configure Mode Handling

**If multi-mode:** [Mode Handling](references/mode-handling.md)

For models supporting multiple modes:

- Register each mode separately

- Set mode-specific defaults

- Implement mode-specific prediction types

- Handle mode validation

### 8. Handle Encoding Options

**For matrix/xy interfaces:** [Encoding Options](references/encoding-options.md)

Configure how formulas are converted:

- Choose interface type

- Set indicator coding (traditional vs one-hot)

- Handle intercept

- Configure factor encoding

---

## Testing Your Model

**Essential tests:**

- Model constructor creates correct object

- Setting engine works

- Setting mode works (if multi-mode)

- Formula and xy interfaces equivalent

- Each prediction type returns correct format

- Factor handling works correctly

- Error messages are clear

**Test each engine separately:**
```r
test_that("lm engine works", {
  skip_if_not_installed("lm_package")

  spec <- my_model() |> set_engine("lm")
  fit <- fit(spec, y ~ x, data = data)
  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, data)
  expect_named(preds, ".pred")
})
```

---

## Contributing to Parsnip Source

**For PRs to tidymodels/parsnip:**

Additional resources for source development:

- [Best Practices (Source)](references/best-practices-source.md) - Parsnip-specific patterns

- [Troubleshooting (Source)](references/troubleshooting-source.md) - Common issues

- [Testing Patterns (Source)](references/testing-patterns-source.md) - Comprehensive tests

**Key differences from extensions:**

- Can use internal functions (`:::`)

- Follow parsnip file organization (`R/[model].R`, `R/[model]_data.R`)

- Add to parsnip documentation

- More comprehensive testing required

- Consider existing parsnip conventions

---

## Example: Creating `sparse_reg()`

**Hypothetical new model for sparse regression:**

> **Note:** This example shows extension development patterns. For source development, omit `parsnip::` prefixes and use internal functions as shown in [source-guide.md](references/source-guide.md).

1. **Constructor** (`R/sparse_reg.R`):
```r
sparse_reg <- function(mode = "regression",
                       penalty = NULL,
                       sparsity_threshold = NULL,
                       engine = "glmnet") {

  args <- list(
    penalty = rlang::enquo(penalty),
    sparsity_threshold = rlang::enquo(sparsity_threshold)
  )

  parsnip::new_model_spec(
    "sparse_reg",
    args = args,
    eng_args = NULL,
    mode = mode,
    user_specified_mode = FALSE,
    method = NULL,
    engine = engine,
    user_specified_engine = !missing(engine)
  )
}
```

2. **Registration** (in `.onLoad()` or package setup):
```r
# Declare model
parsnip::set_new_model("sparse_reg")
parsnip::set_model_mode("sparse_reg", "regression")

# Register glmnet engine
parsnip::set_model_engine("sparse_reg", "regression", "glmnet")
parsnip::set_dependency("sparse_reg", "glmnet", "glmnet", "regression")

# Translate arguments
parsnip::set_model_arg(
  model = "sparse_reg",
  eng = "glmnet",
  parsnip = "penalty",
  original = "lambda",
  func = list(pkg = "dials", fun = "penalty"),
  has_submodel = TRUE
)

# Fit method
parsnip::set_fit(
  model = "sparse_reg",
  eng = "glmnet",
  mode = "regression",
  value = list(
    interface = "matrix",
    protect = c("x", "y"),
    func = c(pkg = "glmnet", fun = "glmnet"),
    defaults = list(family = "gaussian")
  )
)

# Predictions
parsnip::set_pred(
  model = "sparse_reg",
  eng = "glmnet",
  mode = "regression",
  type = "numeric",
  value = list(
    pre = NULL,
    post = NULL,
    func = c(fun = "predict"),
    args = list(
      object = rlang::expr(object$fit),
      newx = rlang::expr(as.matrix(new_data)),
      type = "response"
    )
  )
)
```

3. **Testing**:
```r
test_that("sparse_reg constructor works", {
  spec <- sparse_reg()
  expect_s3_class(spec, "sparse_reg")
  expect_equal(spec$mode, "regression")
  expect_equal(spec$engine, "glmnet")
})

test_that("sparse_reg fits and predicts", {
  skip_if_not_installed("glmnet")

  spec <- sparse_reg(penalty = 0.1) |> set_engine("glmnet")
  fit <- fit(spec, mpg ~ ., data = mtcars)

  expect_s3_class(fit, "model_fit")

  preds <- predict(fit, mtcars[1:5, ])
  expect_s3_class(preds, "tbl_df")
  expect_named(preds, ".pred")
  expect_equal(nrow(preds), 5)
})
```

---

## Common Pitfalls

**Prioritize correctness over structure.** Focus on getting the implementation right before worrying about file organization.

**Code correctness issues (fix first):**
1. **Incorrect column names** - Follow `.pred` naming conventions strictly (`.pred`, `.pred_class`, `.pred_lower`)
2. **Wrong interface type** - Match engine's expected input format (formula vs matrix vs xy)
3. **Inconsistent argument naming** - Use tidymodels standards (`penalty`, `mixture`), not engine names
4. **Missing prediction post-processing** - Ensure output format matches parsnip conventions

**Implementation completeness (fix second):**
5. **Incomplete registration** - Must complete full sequence for each engine (`set_new_model` → `set_model_mode` → `set_model_engine` → `set_dependency` → `set_model_arg` → `set_fit` → `set_pred`)
6. **Missing mode registration** - Must register modes explicitly with `set_model_mode()`
7. **No argument translation** - Main arguments must map to engine arguments via `set_model_arg()`
8. **Insufficient testing** - Test all modes, engines, prediction types, and both fit() and fit_xy()

**Structural concerns (address last):**
9. **Too many files** - Keep to 2-3 files for extensions, 2-4 for source (see File Discipline section)

---

## When to Create a New Model

**INSTRUCTIONS FOR CLAUDE:**

Before implementing, verify this is truly a NEW model type. If the user requests:
- A different computational engine for an existing model (e.g., "add xgboost to boost_tree")
  → **Stop.** Politely explain this should use the [add-parsnip-engine](../add-parsnip-engine/SKILL.md) skill instead
- A minor variation that could be an engine-specific argument
  → **Stop.** Suggest using engine-specific arguments rather than creating a new model
- Something that duplicates an existing parsnip model
  → **Stop.** Point them to the existing model

Only proceed with implementation if it's genuinely a new model type that doesn't exist in parsnip.

**Create a new model when:**

- The algorithm is fundamentally different from existing models

- It serves a distinct use case

- It has unique prediction types

- It fills a gap in parsnip's model coverage

**Don't create a new model when:**

- It's just a different engine for an existing model type
  → Use [add-parsnip-engine](../add-parsnip-engine/SKILL.md) instead

- It's a minor variation of an existing model
  → Consider engine-specific arguments instead

**Examples:**

- ✓ `survival_reg()` - New outcome type (censored data)

- ✓ `naive_bayes()` - Distinct algorithm family

- ✗ Random forest with different package → Add engine to `rand_forest()`

- ✗ Linear regression with different penalty → Add engine to `linear_reg()`

---

## File Discipline

Keep implementations focused and avoid creating unnecessary files.

**Target file counts:**

Extension development:
- `R/[model_name].R` - Model constructor
- `tests/testthat/test-[model_name].R` - Tests
- `README.md` - Only if needed for package users
- **Total: 2-3 files**

Source development:
- `R/[model_name].R` - Model constructor
- `R/[model_name]_data.R` - Engine registrations
- `tests/testthat/test-[model_name].R` - Tests
- `man/rmd/[model_name]_[engine].Rmd` - Engine docs (optional)
- **Total: 2-4 files**

**Do not create:**
- Implementation notes or summaries (IMPLEMENTATION_NOTES.md, IMPLEMENTATION_SUMMARY.md)
- Usage example files (example_usage.R, examples.R)
- Separate documentation files (DOCUMENTATION.md, USAGE.md)
- Development guide files (DEVELOPMENT.md, GUIDE.md)
- Testing guide files (TESTING.md, TEST_GUIDE.md)
- Changelog files (CHANGELOG.md, NEWS.md unless source development)
- Configuration files (CONFIG.md, SETUP.md)
- Workflow files (WORKFLOW.md, PROCESS.md)
- Debug or log files (DEBUG.md, LOG.md)
- Status or progress files (STATUS.md, PROGRESS.md)
- TODO or task files (TODO.md, TASKS.md)
- Multiple README variants (README_DEV.md, README_TECHNICAL.md)

**Instead:**
- Put usage examples in roxygen `@examples` tags
- Put implementation notes in roxygen `@details` tags
- Put development notes in comments within code
- Document design decisions in commit messages
- Use vignettes for comprehensive usage guides (if creating a package)

---

## Related Skills

- [add-parsnip-engine](../add-parsnip-engine/SKILL.md) - Add computational engines to your new model

- [add-dials-parameter](../add-dials-parameter/SKILL.md) - Define tunable parameters for model arguments

- [add-recipe-step](../add-recipe-step/SKILL.md) - Preprocess data before model fitting

- [add-yardstick-metric](../add-yardstick-metric/SKILL.md) - Evaluate model predictions with custom metrics

## Next Steps

After creating your model:

1. **Test thoroughly** - Both extension and source tests
2. **Document** - Add examples and usage guidance
3. **Share** - Consider contributing to parsnip
4. **Maintain** - Keep up with engine package updates

For questions or contributions, see:

- [Tidymodels GitHub](https://github.com/tidymodels/parsnip)

- [Tidymodels Community](https://community.rstudio.com/c/ml)
