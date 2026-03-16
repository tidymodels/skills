# Claude Skills for Tidymodels Development

A curated collection of [Claude Code skills](https://code.claude.com/docs/en/skills) for developing and maintaining tidymodels ecosystem packages, with a current focus on building extension packages. These skills package expertise, workflows, and best practices into reusable capabilities that Claude can automatically invoke.

## Skills Inventory

| Skill | Description |
|-------|-------------|
| [add-yardstick-metric](tidymodels/skills/add-yardstick-metric/SKILL.md) | Create new yardstick performance metrics (numeric, class, probability) with templates for implementation functions, testing patterns, and optional visualization support |
| [add-recipe-step](tidymodels/skills/add-recipe-step/SKILL.md) | Build preprocessing steps for the recipes package with templates for modify-in-place, create-new-columns, and row-operation steps |

## Installation

Install these skills through the Claude Code marketplace:

```bash
# Add the marketplace
/plugin marketplace add edgararuiz/skills

# Install the tidymodels development plugin
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
