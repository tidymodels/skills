# Claude Code Skills for Tidymodels

A curated collection of [Claude Code skills](https://code.claude.com/docs/en/skills) for the Tidymodels ecosystem, organized by audience.

## Structure

This repository contains two categories of skills:

### Developer Skills (`developers/`)

Skills for **creating and extending** Tidymodels packages:
- Building custom yardstick metrics
- Creating recipes preprocessing steps
- Contributing to Tidymodels packages

**Browse Developer Skills**: [developers/README.md](developers/README.md)

### User Skills (`users/`)

Skills for **using** Tidymodels in data analysis and modeling:
- *(Coming soon - to be added by content team)*

**Browse User Skills**: [users/README.md](users/README.md)

## Installation

Install skills through the Claude Code marketplace:

```bash
# Add the marketplace
/plugin marketplace add tidymodels/skills

# Install developer skills
/plugin install tidymodels-developers@tidymodels-skills

# Install user skills (when available)
/plugin install tidymodels-users@tidymodels-skills
```

## Audience Guide

**Choose Developer Skills if you are:**
- Creating a new R package that extends Tidymodels
- Contributing code to Tidymodels core packages
- Building custom metrics, models, or preprocessing steps

**Choose User Skills if you are:**
- Analyzing data with Tidymodels
- Building predictive models
- Learning Tidymodels workflows

## Resources

- [Tidymodels](https://www.tidymodels.org/)
- [Yardstick package](https://yardstick.tidymodels.org/)
- [Recipes package](https://recipes.tidymodels.org/)
- [Claude Code documentation](https://github.com/anthropics/claude-code)
