# Skills Personal - Claude Code Skills Repository

Personal repository for Claude Code skills for the tidymodels ecosystem, organized by audience.

## Repository Structure

```
skills-personal/
├── skill-development/              # Meta-level tooling for skill maintenance
│   ├── build-verify.py            # Build and verify skills
│   ├── rename-and-update.py       # Bulk renaming and updates
│   ├── replace-text.py            # Surgical text replacement
│   ├── SKILL_IMPLEMENTATION_GUIDE.md
│   └── README.md                  # Tool documentation
├── developers/                     # Developer-facing skills
│   ├── add-yardstick-metric/      # Creating custom metrics
│   ├── add-recipe-step/           # Creating preprocessing steps
│   ├── shared-references/         # Universal R package patterns
│   ├── README.md
│   └── NEWS.md
├── users/                          # User-facing skills (future)
│   ├── shared-references/         # User skill references
│   └── README.md
├── repos/                          # Cloned tidymodels repositories
│   ├── yardstick/
│   ├── recipes/
│   └── ...
└── .claude/                        # Claude Code configuration
```

## Audience-Specific Skills

### Developer Skills (`developers/`)
For creating tidymodels extensions and contributing to packages:
- Building custom yardstick metrics
- Creating recipes preprocessing steps
- Package development workflows

### User Skills (`users/`)
For using tidymodels in data analysis and modeling:
- *(Coming soon - to be added by content team)*

## Working in This Repository

### Before Committing Changes

**⚠️ CRITICAL**: Before committing any changes to skills, run:

```bash
cd skill-development
./build-verify.py ../developers/
```

This script:
1. **Builds**: Copies shared files to each skill's references folder
2. **Verifies**: Checks all markdown links and file references

Fix any errors before committing. This ensures all skills stay in sync and all links work correctly.

### Creating New Developer Skills

When creating a new developer skill (e.g., add-parsnip-model):

**Follow the [Skill Implementation Guide](../skill-development/SKILL_IMPLEMENTATION_GUIDE.md)**

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
- [Skill Implementation Guide](../skill-development/SKILL_IMPLEMENTATION_GUIDE.md) - Creating new skills

**Example Skills:**
- [add-yardstick-metric](../developers/add-yardstick-metric/SKILL.md) - Creating custom metrics
- [add-recipe-step](../developers/add-recipe-step/SKILL.md) - Creating preprocessing steps

**Shared Resources:**
- [Extension Prerequisites](../developers/shared-references/extension-prerequisites.md) - R package setup
- [Development Workflow](../developers/shared-references/development-workflow.md) - Fast iteration cycle
- [Testing Patterns](../developers/shared-references/testing-patterns-extension.md) - Extension testing

## Development Philosophy

This repository follows the principles outlined in the Skill Implementation Guide:

1. **Single source of truth** - No duplicate content across files
2. **Dual context support** - Extension development (creating new packages) and Source development (contributing PRs)
3. **Complete examples** - Show full working code, not fragments
4. **Clear constraints** - Extension developers cannot use internal functions (`:::`)
5. **Autonomous execution** - Claude Code runs commands directly when possible

---

**Last Updated:** 2026-03-25
