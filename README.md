# Claude Skills for Tidymodels Development

A curated collection of [Claude Code skills](https://code.claude.com/docs/en/skills) for developing and maintaining tidymodels ecosystem packages, with a current focus on building extension packages. These skills package expertise, workflows, and best practices into reusable capabilities that Claude can automatically invoke.

## Skills Inventory

### add-yardstick-metric

Comprehensive guide for creating new yardstick performance metrics (numeric, class, probability). Includes:

- Templates for implementation functions, vector functions, and data frame methods
- Roxygen documentation templates
- Comprehensive testing patterns
- Optional autoplot support for visualization (curve metrics and confusion matrices)
- Weighted calculations and `NA` handling
- Multiclass support with different averaging strategies
- Common pitfalls and troubleshooting guidance

**Why is this a large skill?** This skill is ~2,350 lines because it covers three metric types (numeric, class, probability), each with different complexity levels, plus comprehensive testing patterns, edge case handling, autoplot support, and yardstick-specific internals (confusion matrices, event levels, factor ordering). It's designed as a self-contained reference guide that Claude searches rather than reads linearly—users without access to yardstick source code need complete working examples and detailed explanations of non-exported functions.

### add-recipe-step

Comprehensive guide for creating new preprocessing steps for the recipes package. Includes:

- Complete templates for three step types (modify-in-place, create-new-columns, row-operations)
- Decision tree to help choose the appropriate step type
- Full implementation of the three-function architecture (constructor, initialization, S3 methods)
- Complete prep/bake workflow patterns
- Variable selection with `enquos()` and `recipes_eval_select()`
- Case weights handling for both frequency and importance weights
- Roxygen documentation templates with recipes-specific `@template` tags
- Comprehensive testing guide with all 6 required infrastructure tests
- Optional methods for tunable parameters, sparse data, and package dependencies
- Helper functions reference table

**Why is this a large skill?** This skill is ~1,700 lines because it provides three distinct templates for different step types, each requiring five S3 methods with complete implementations. Like add-yardstick-metric, it's fully self-contained with working code examples since users need complete templates they can copy and adapt without access to the recipes source code. The skill includes extensive testing patterns, best practices, and a comprehensive checklist to ensure steps integrate properly with the recipes ecosystem.

## Installation

### Via Claude Code Marketplace

The easiest way to install these skills is through the Claude Code marketplace:

```bash
# Add the marketplace
/plugin marketplace add edgararuiz/skills

# Install the tidymodels development plugin
/plugin install tidymodels-dev@tidymodels-skills
```

**Note:** The repository must be public for GitHub-based installation. For local development, you can add the marketplace using the local path:

```bash
/plugin marketplace add /Users/edgar/Projects/skills-personal
/plugin install tidymodels-dev@tidymodels-skills
```

## Using Skills

Skills are automatically invoked by Claude Code when your request matches the skill's description. For example:

- "Add a new metric to yardstick for calculating mean absolute percentage error" → invokes `add-yardstick-metric`
- "Create a custom classification metric for miss rate" → invokes `add-yardstick-metric`
- "Create a recipe step for winsorizing numeric variables" → invokes `add-recipe-step`
- "Build a preprocessing step that creates polynomial features" → invokes `add-recipe-step`

You can also manually reference a skill by mentioning it by name in your request.

## Focus Areas

This repository currently focuses on:

- **Yardstick metrics development**: Adding new performance metrics with proper structure, documentation, and testing
- **Recipes preprocessing steps**: Creating custom preprocessing steps that integrate with the recipes pipeline
- **Tidyverse conventions**: Following established patterns for package development
- **R package workflows**: Testing, documentation, and maintenance processes

## Resources

- [Tidymodels](https://www.tidymodels.org/)
- [Yardstick package](https://yardstick.tidymodels.org/)
- [Recipes package](https://recipes.tidymodels.org/)
- [Claude Code documentation](https://github.com/anthropics/claude-code)
- [Custom performance metrics tutorial](https://www.tidymodels.org/learn/develop/metrics/)
- [Custom recipe steps tutorial](https://www.tidymodels.org/learn/develop/recipes/)
