# Claude Code Skills for Tidymodels

A curated collection of [Claude Code skills](https://code.claude.com/docs/en/skills) for the tidymodels ecosystem, organized by audience.

## Structure

This repository contains two categories of skills:

### Developer Skills (`developers/`)

Skills for **creating and extending** tidymodels packages:
- Building custom yardstick metrics
- Creating recipes preprocessing steps
- Contributing to tidymodels packages

**Browse Developer Skills**: [developers/README.md](developers/README.md)

### User Skills (`users/`)

Skills for **using** tidymodels in data analysis and modeling:
- *(Coming soon - to be added by content team)*

**Browse User Skills**: [users/README.md](users/README.md)

## Installation

Install skills through the Claude Code marketplace:

```bash
# Add the marketplace
/plugin marketplace add edgararuiz/skills

# Install developer skills
/plugin install tidymodels-developers@tidymodels-skills

# Install user skills (when available)
/plugin install tidymodels-users@tidymodels-skills
```

## Audience Guide

**Choose Developer Skills if you are:**
- Creating a new R package that extends tidymodels
- Contributing code to tidymodels core packages
- Building custom metrics, models, or preprocessing steps

**Choose User Skills if you are:**
- Analyzing data with tidymodels
- Building predictive models
- Learning tidymodels workflows

## Resources

- [Tidymodels](https://www.tidymodels.org/)
- [Yardstick package](https://yardstick.tidymodels.org/)
- [Recipes package](https://recipes.tidymodels.org/)
- [Claude Code documentation](https://github.com/anthropics/claude-code)
