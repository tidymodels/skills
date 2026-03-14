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

```r
usethis::use_github_file(
  "edgararuiz/skills",
  "tidymodels/add-yardstick-metric/SKILL.md",
  destdir = ".claude/skills/add-yardstick-metric"
)
```

**Why is this a large skill?** This skill is ~2,350 lines because it covers three metric types (numeric, class, probability), each with different complexity levels, plus comprehensive testing patterns, edge case handling, autoplot support, and yardstick-specific internals (confusion matrices, event levels, factor ordering). It's designed as a self-contained reference guide that Claude searches rather than reads linearly—users without access to yardstick source code need complete working examples and detailed explanations of non-exported functions.

## Using Skills

Skills are automatically invoked by Claude Code when your request matches the skill's description. For example:

- "Add a new metric to yardstick for calculating mean absolute percentage error" → invokes `add-yardstick-metric`
- "Create a custom classification metric for miss rate" → invokes `add-yardstick-metric`

You can also manually reference a skill by mentioning it by name in your request.

## Focus Areas

This repository currently focuses on:

- **Yardstick metrics development**: Adding new performance metrics with proper structure, documentation, and testing
- **Tidyverse conventions**: Following established patterns for package development
- **R package workflows**: Testing, documentation, and maintenance processes

## Resources

- [Tidymodels](https://www.tidymodels.org/)
- [Yardstick package](https://yardstick.tidymodels.org/)
- [Claude Code documentation](https://github.com/anthropics/claude-code)
- [Custom performance metrics tutorial](https://www.tidymodels.org/learn/develop/metrics/)
