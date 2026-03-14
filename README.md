# Claude Skills for Tidymodels Development

A curated collection of Claude Code skills for developing and maintaining tidymodels ecosystem packages, with a current focus on building extension packages. These skills package expertise, workflows, and best practices into reusable capabilities that Claude can automatically invoke.

## What are Claude Skills?

Claude skills are autonomous capabilities that Claude Code can invoke automatically based on your request. Each skill consists of a `SKILL.md` file containing structured instructions that guide Claude through complex workflows, from adding new metrics to yardstick to properly deprecating functions following tidyverse conventions.

Skills help by:
- Encoding domain expertise and institutional knowledge
- Ensuring consistent processes are followed
- Making complex tasks accessible and repeatable
- Providing step-by-step guidance with verification checklists

## Skills Inventory

### add-yardstick-metric

Comprehensive guide for creating new yardstick performance metrics (numeric, class, probability). Includes templates for implementation functions, vector functions, data frame methods, documentation, and comprehensive testing patterns. Covers weighted calculations, NA handling, multiclass support, and common pitfalls.

```r
usethis::use_github_file(
  "edgararuiz/skills",
  "tidymodels/add-yardstick-metric/SKILL.md",
  destdir = ".claude/skills/add-yardstick-metric"
)
```

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
