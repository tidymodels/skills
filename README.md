# Claude Code Skills for Tidymodels

Official [Claude Code skills](https://docs.anthropic.com/en/docs/build-with-claude/claude-for-sheets-and-code) for the Tidymodels ecosystem, organized by audience.

[![Documentation](https://img.shields.io/badge/docs-tidymodels--skills-blue)](https://tidymodels.github.io/skills/)
[![Plugin Version](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/tidymodels/skills/main/.claude-plugin/marketplace.json&query=$.metadata.version&label=plugin&color=blue)](https://github.com/tidymodels/skills/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Quick Start

1. **Browse the documentation**: Visit [tidymodels.github.io/skills](https://tidymodels.github.io/skills/) for complete guides and examples

2. **Install through Claude Code marketplace**:
   ```bash
   # Add the marketplace
   /plugin marketplace add tidymodels/skills

   # Install developer skills
   /plugin install tidymodels-developers@tidymodels-skills

   # Install user skills (when available)
   /plugin install tidymodels-users@tidymodels-skills
   ```

3. **Start using skills**: Activate skills in Claude Code to get AI assistance for Tidymodels development

## Available Skills

This repository contains two categories of skills:

### 👨‍💻 Developer Skills

Skills for **creating and extending** Tidymodels packages:
- Building custom yardstick metrics
- Creating recipes preprocessing steps
- Contributing to Tidymodels packages

**Documentation**: [tidymodels.github.io/skills/developers](https://tidymodels.github.io/skills/developers)
**Browse**: [developers/README.md](developers/README.md)

### 👥 User Skills

Skills for **using** Tidymodels in data analysis and modeling:
- Tabular data machine learning workflows
- Time series forecasting with modeltime
- Model training, tuning, and evaluation
- Feature engineering with recipes

**Documentation**: [tidymodels.github.io/skills/users](https://tidymodels.github.io/skills/users)
**Browse**: [users/README.md](users/README.md)

## Audience Guide

**Choose Developer Skills if you are:**
- Creating a new R package that extends Tidymodels
- Contributing code to Tidymodels core packages
- Building custom metrics, models, or preprocessing steps

**Choose User Skills if you are:**
- Analyzing data with Tidymodels
- Building predictive models
- Learning Tidymodels workflows

## Documentation

Full documentation is available at [tidymodels.github.io/skills](https://tidymodels.github.io/skills/), including:
- Getting started guides
- Comprehensive skill references
- Code examples and patterns
- Best practices

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting issues
- Suggesting new skills
- Contributing code
- Improving documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Resources

- [Tidymodels](https://www.tidymodels.org/) - Official Tidymodels website
- [Yardstick](https://yardstick.tidymodels.org/) - Model performance metrics
- [Recipes](https://recipes.tidymodels.org/) - Preprocessing tools
- [Claude Code](https://docs.anthropic.com/en/docs/build-with-claude/claude-for-sheets-and-code) - AI-powered coding assistant
- [Tidymodels Community](https://github.com/tidymodels) - GitHub organization

---

**Maintained by the Tidymodels team** | [Report an issue](https://github.com/tidymodels/skills/issues)
