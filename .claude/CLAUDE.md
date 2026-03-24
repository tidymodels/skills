# Skills Personal - Claude Code Skills Repository

Personal repository for Claude Code skills, with a focus on tidymodels development patterns.

## Repository Structure

```
skills-personal/
├── tidymodels/                           # Tidymodels development skills
│   ├── SKILL_IMPLEMENTATION_GUIDE.md    # How to create new tidymodels skills
│   ├── add-yardstick-metric/            # Creating custom metrics
│   ├── add-recipe-step/                 # Creating preprocessing steps
│   └── shared-references/               # Universal R package patterns
├── repos/                                # Cloned tidymodels repositories
│   ├── yardstick/
│   ├── recipes/
│   └── ...
└── .claude/                              # Claude Code configuration
```

## Working in This Repository

### Before Committing Changes

**⚠️ CRITICAL**: Before committing any changes to tidymodels skills, run:

```bash
cd tidymodels
./dev-scripts/build-verify.py
```

This script:
1. **Builds**: Copies shared files to each skill's references folder
2. **Verifies**: Checks all markdown links and file references

Fix any errors before committing. This ensures all skills stay in sync and all links work correctly.

### Creating New Tidymodels Skills

When creating a new tidymodels skill (e.g., add-parsnip-model):

**Follow the [Skill Implementation Guide](../tidymodels/SKILL_IMPLEMENTATION_GUIDE.md)**

This comprehensive guide covers:
- File structure and organization
- Extension vs Source development patterns
- Avoiding code duplication
- Claude Code behavioral patterns
- Testing and validation
- Time estimates: 14-22 hours for a complete skill

### Project Conventions

- **No code duplication**: Each piece of content exists in exactly one place
- **SKILL.md files**: Navigation only, link to references for actual content
- **Shared references**: Universal patterns in `shared-references/`, skill-specific in `references/`
- **Extension-first**: Main examples use extension patterns with `package::` prefix

### Repository Access

The `repos/` directory contains cloned tidymodels repositories for reference. These are optional but recommended for creating high-quality skills.

## Quick Links

**Implementation:**
- [Skill Implementation Guide](../tidymodels/SKILL_IMPLEMENTATION_GUIDE.md) - Creating new skills

**Example Skills:**
- [add-yardstick-metric](../tidymodels/add-yardstick-metric/SKILL.md) - Creating custom metrics
- [add-recipe-step](../tidymodels/add-recipe-step/SKILL.md) - Creating preprocessing steps

**Shared Resources:**
- [Extension Prerequisites](../tidymodels/shared-references/extension-prerequisites.md) - R package setup
- [Development Workflow](../tidymodels/shared-references/development-workflow.md) - Fast iteration cycle
- [Testing Patterns](../tidymodels/shared-references/testing-patterns-extension.md) - Extension testing

## Development Philosophy

This repository follows the principles outlined in the Skill Implementation Guide:

1. **Single source of truth** - No duplicate content across files
2. **Dual context support** - Extension development (creating new packages) and Source development (contributing PRs)
3. **Complete examples** - Show full working code, not fragments
4. **Clear constraints** - Extension developers cannot use internal functions (`:::`)
5. **Autonomous execution** - Claude Code runs commands directly when possible

---

**Last Updated:** 2026-03-20
