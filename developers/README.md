# Tidymodels Development Skills

Claude Code skills for extending tidymodels packages with custom functionality.
These skills guide developers through creating new metrics, preprocessing steps,
and other tidymodels extensions following package conventions and best
practices.

## Available Skills

### [add-yardstick-metric](add-yardstick-metric/SKILL.md)

Create custom performance metrics for yardstick. Supports numeric metrics
(regression), class metrics (classification), probability metrics, survival
metrics, and quantile metrics. Includes complete patterns for all metric types
with testing and documentation templates.

### [add-recipe-step](add-recipe-step/SKILL.md)

Create preprocessing steps for the recipes package. Covers modify-in-place
transformations, steps that create new columns, and row operations. Includes the
prep/bake workflow, variable selection, and case weight handling.

## Quick Start

1. **Choose your skill** based on what you want to extend
2. **Understand your development context:**

   - Creating a new package? Follow extension development guidance

   - Contributing to a tidymodels package? Follow source development guidance
3. **Follow the skill guide** for complete implementation patterns

Each skill automatically detects your development context and provides
appropriate guidance.

## Directory Structure

```
developers/
├── add-yardstick-metric/      # Custom metrics skill
│   ├── SKILL.md               # Main entry point
│   ├── references/            # Detailed metric type guides
│   └── ...
├── add-recipe-step/           # Custom preprocessing steps skill
│   ├── SKILL.md               # Main entry point
│   ├── references/            # Detailed step type guides
│   └── ...
├── shared-references/         # Common R package development guidance
├── shared-references/scripts/  # Repository cloning utilities
└── SKILL_IMPLEMENTATION_GUIDE.md  # For skill authors
```

## Key Features

- **Comprehensive coverage** of all metric and step types

- **Complete code examples** with testing patterns

- **Claude Code integration** - Optional `usethis::use_claude_code()` setup for
  tidyverse R package development patterns that complement tidymodels-specific
  guidance

- **Skill composition** - Automatically incorporates tidyverse team's general R
  patterns when available, keeping tidymodels skills focused on domain-specific
  guidance

- **Automatic repository cloning** - When building extensions, skills can clone
  tidymodels source repositories with your permission, providing direct access
  to canonical implementations for more accurate guidance

- **Platform-agnostic scripts** for enhanced development workflow

- **Extensive reference documentation** for deep dives

## Future Development

This directory will serve as the home for tidymodels-recommended development
skills. Additional skills for extending other tidymodels packages will be added
here as they are developed.

## About

These skills are designed for use with Claude Code and follow tidymodels
conventions. Each skill provides both extension development patterns (for
creating new packages) and source development patterns (for contributing to
tidymodels repositories).
