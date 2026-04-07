---
name: add-parsnip-engine
description: Add new computational engines to existing parsnip models. Use when connecting an existing parsnip model (linear_reg, boost_tree, etc.) to a new computational backend or R package.
---

# Add Parsnip Engine

Guide for adding new engines to existing parsnip models. This skill covers registering engines (like adding "spark" to `linear_reg()`) without creating entirely new model types.

**Use this skill when:** Adding a new engine to an existing parsnip model type.

**For creating new models:** See [add-parsnip-model](../add-parsnip-model/SKILL.md) skill instead.

---

## Two Development Contexts

This skill supports **two distinct development contexts**:

### 🆕 Extension Development (Default)
**Creating a new R package** that adds engines to existing parsnip models.

- ✅ Use this for: New packages, standalone engines, CRAN submissions

- 📦 Package detection: No `parsnip` in DESCRIPTION's `Package:` field

- ⚠️ **Constraint**: Can only use exported functions (no `:::`)

- 📖 **Guide**: [Extension Development Guide](references/extension-guide.md)

### 🔧 Source Development (Advanced)
**Contributing directly to parsnip** via pull requests.

- ✅ Use this for: Contributing to tidymodels/parsnip repository

- 📦 Package detection: `Package: parsnip` in DESCRIPTION

- ✨ **Benefit**: Can use internal functions and package infrastructure

- 📖 **Guide**: [Source Development Guide](references/source-guide.md)

**This main guide shows extension development patterns.** If you're contributing to parsnip itself, see the [Source Development Guide](references/source-guide.md) for package-specific details.

---

## Getting Started

**INSTRUCTIONS FOR CLAUDE:** Run the verification script first to determine the development context:

```bash
Rscript -e 'source(Sys.glob(path.expand("~/.claude/plugins/cache/tidymodels-skills/tidymodels-dev/*/tidymodels/shared-references/scripts/verify-setup.R"))[1])'
```

**Then follow the appropriate path based on the output:**

- **Output: "All checks for source development complete."**
  → Go to [Source Development Guide](references/source-guide.md)

- **Output: "All checks for extension development complete." (no warnings)**
  → Go to [Extension Development Guide](references/extension-guide.md)

- **Output: Shows "Warning - [UUID]" messages**
  → Go to [Extension Prerequisites](references/package-extension-prerequisites.md) to resolve warnings first

---

## Overview

Adding an engine to an existing parsnip model provides:

- Connection to new computational backends (e.g., H2O, Spark, TensorFlow)

- Standardized interface with parsnip models

- Support for multiple prediction types

- Integration with tidymodels ecosystem

- Consistent API regardless of engine

**What this skill covers:**

- Planning and choosing the right interface

- Complete registration sequence

- Fit and predict method implementation

- Testing engine implementations

- Multi-mode support (regression + classification)

---

## Repository Access (Optional but Recommended)

**INSTRUCTIONS FOR CLAUDE:** Check if `repos/parsnip/` exists in the current working directory. Use this to guide development:

**If `repos/parsnip/` exists:**

- ✅ Use it as a reference throughout development

- Read source files (e.g., `repos/parsnip/R/linear_reg_data.R`) to study engine registration patterns

- Read test files (e.g., `repos/parsnip/tests/testthat/test-linear_reg.R`) for testing patterns

- Reference these files when answering complex questions or solving problems

- Look at actual code structure, validation patterns, and edge case handling

**If `repos/parsnip/` does NOT exist:**

- Suggest cloning the repository using the scripts in [Repository Access Guide](references/package-repository-access.md)

- This is **optional but strongly recommended** for high-quality development

- If the user declines, reference files using GitHub URLs:

  - Format: `https://github.com/tidymodels/parsnip/blob/main/R/[file-name].R`

  - Example: https://github.com/tidymodels/parsnip/blob/main/R/linear_reg_data.R

  - This allows users to click through to see implementations

**When to use repository references:**

- Complex implementation questions (e.g., "How does parsnip handle multi-mode engines?")

- Debugging issues (compare user's code to working implementation)

- Understanding patterns (study similar engines)

- Test design (see how parsnip tests edge cases)

- Architecture decisions (understand internal structure)

See [Repository Access Guide](references/package-repository-access.md) for setup instructions.

---

## Quick Navigation

**Development Guides:**

- [Extension Development Guide](references/extension-guide.md) - Creating new packages that add engines

- [Source Development Guide](references/source-guide.md) - Contributing PRs to parsnip itself

**Core Implementation References:**

- [Engine Implementation](references/engine-implementation.md) - Complete registration sequence, examples, patterns

- [Fit and Predict Methods](references/fit-predict-methods.md) - Implementation details for fit/predict

- [Prediction Types](references/prediction-types.md) - All 11 prediction types

- [Mode Handling](references/mode-handling.md) - Multi-mode support (regression + classification)

- [Encoding Options](references/encoding-options.md) - Interface types and data conversion

**Model-Specific Guides:**

- [Model Specification System](references/model-specification-system.md) - How parsnip models work

**Shared References (Extension Development):**

- [Extension Prerequisites](references/package-extension-prerequisites.md) - Package setup

- [Development Workflow](references/package-development-workflow.md) - Fast iteration cycle

- [Extension Requirements](references/package-extension-requirements.md) - Complete guide:

  - [Best Practices](references/package-extension-requirements.md#best-practices)

  - [Testing Patterns](references/package-extension-requirements.md#testing-requirements)

  - [Troubleshooting](references/package-extension-requirements.md#common-issues-solutions)

- [Roxygen Documentation](references/package-roxygen-documentation.md)

- [Package Imports](references/package-imports.md)

**Source Development Specific:**

- [Testing Patterns (Source)](references/testing-patterns-source.md)

- [Best Practices (Source)](references/best-practices-source.md)

- [Troubleshooting (Source)](references/troubleshooting-source.md)

---

## Prerequisites

**⚠️ IMPORTANT**: Before implementing engines, complete the extension prerequisites sequence:

👉 **[Extension Prerequisites Guide](references/package-extension-prerequisites.md)**

This guide includes critical steps like `use_claude_code()` (if available) that must run BEFORE adding dependencies. Following the complete sequence ensures proper package initialization and Claude Code integration.

After completing extension prerequisites, return here to implement your engine.

**Parsnip Fundamentals:**

Before adding an engine, understand:

- How parsnip models work - [Model Specification System](references/model-specification-system.md)

- Fit and predict patterns - [Fit and Predict Methods](references/fit-predict-methods.md)

- Available output formats - [Prediction Types](references/prediction-types.md)

---

## Implementation Overview

**INSTRUCTIONS FOR CLAUDE: Assess complexity first, then choose approach:**

### Simple Engine?

- Single mode (regression OR classification, not both)

- Formula interface OR matrix interface (pick one)

- 1-3 parameters to map

- Standard prediction type (numeric OR class/prob)

**→ Use streamlined approach:**

- Target 2 files: R/zzz.R (15-30 lines), tests/testthat/test-*.R; acceptable to reach 4-6 if needed

- NO summary docs, NO example files

- See [Extension Guide, Simple Single-Mode](references/extension-guide.md#simple-single-mode-2-files-rzzzr-teststest-r)

### Complex Engine?

- Multi-mode (regression AND classification)

- Matrix interface with encoding

- Survival/censored regression

- Custom prediction post-processing

**→ Reference detailed guides:**

- See [Mode Handling](references/mode-handling.md) for multi-mode

- See [Encoding Options](references/encoding-options.md) for matrix interfaces

- Still target 2-3 files (R/zzz.R, tests, optional README); acceptable to reach 4-6 if implementation requires it

---

**Core registration steps:**

1. **Plan** - Identify model, choose interface, decide on modes
2. **Register** - Declare engine exists with `set_model_engine()`
3. **Dependencies** - Declare packages with `set_dependency()`
4. **Arguments** - Translate main arguments with `set_model_arg()`
5. **Fit** - Register fit method with `set_fit()`
6. **Encoding** - Configure interface with `set_encoding()` (if needed)
7. **Predict** - Register prediction types with `set_pred()`
8. **Test** - Verify all interfaces and prediction types work

**File Discipline:**

- Extension: Create **2-3 files** (R/zzz.R, tests/testthat/test-*.R, optional README.md); acceptable to reach 4-6 files if implementation requires it

- Source: Modify **1-2 files** (add to R/*_data.R, add to tests/testthat/test-*.R); acceptable to reach 3-7 files if implementation requires it

- **Never create**: IMPLEMENTATION_SUMMARY.md, example_usage.R, helper files

**See [Engine Implementation Guide](references/engine-implementation.md) for complete details and examples.**

---

## Registration Process

The registration process differs slightly by context:

**Extension Development:**

- Register in `.onLoad()` function

- Use `parsnip::` prefix for all functions

- Cannot access internal helpers

- Create function that contains all registrations

**Source Development:**

- Add to existing `R/[model]_data.R` file

- No prefix needed for parsnip functions

- Can use internal helpers if needed

- Follow existing file organization patterns

See respective guides for detailed registration patterns.

---

## Testing Your Engine

**Essential tests to include:**

- Engine fits successfully

- Formula and xy interfaces work (if applicable)

- Each prediction type returns correct format

- Predictions match data dimensions

- Factor handling works correctly

- Error messages are clear

**See testing guides:**

- Extension: [Testing Patterns (Extension)](references/package-extension-requirements.md#testing-requirements)

- Source: [Testing Patterns (Source)](references/testing-patterns-source.md)

---

## When to Add an Engine

**Add an engine when:**

- Model type already exists in parsnip

- Engine provides different computational approach

- Engine offers performance benefits or unique features

- Package is well-maintained and stable

**Don't add an engine when:**

- Model type doesn't exist (see add-parsnip-model instead)

- Engine is functionally identical to existing

- Package is experimental or unmaintained

- Only cosmetic differences from existing engines

---

## Related Skills

- [add-parsnip-model](../add-parsnip-model/SKILL.md) - Create new model specifications (if model doesn't exist yet)

- [add-dials-parameter](../add-dials-parameter/SKILL.md) - Define tunable parameters for engine arguments

- [add-recipe-step](../add-recipe-step/SKILL.md) - Preprocess data before model fitting

- [add-yardstick-metric](../add-yardstick-metric/SKILL.md) - Evaluate engine predictions with custom metrics

---

## Next Steps

**For Extension Development (creating new packages):**

1. Complete [Extension Prerequisites](references/package-extension-prerequisites.md)
2. Follow [Extension Development Guide](references/extension-guide.md)
3. Implement engine using [Engine Implementation Guide](references/engine-implementation.md)
4. Test thoroughly using [Testing Patterns](references/package-extension-requirements.md#testing-requirements)
5. Consider contributing to parsnip

**For Source Development (contributing to parsnip):**

1. Clone tidymodels/parsnip repository
2. Follow [Source Development Guide](references/source-guide.md)
3. Implement engine in appropriate `R/[model]_data.R` file
4. Add comprehensive tests using [Testing Patterns (Source)](references/testing-patterns-source.md)
5. Update NEWS.md and submit PR

---

For questions or contributions, see:

- [Tidymodels GitHub](https://github.com/tidymodels/parsnip)

- [Tidymodels Community](https://community.rstudio.com/c/ml)
