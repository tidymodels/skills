# Tidymodels Skills - Claude Code Skills Repository

Official repository for Claude Code skills for the Tidymodels ecosystem, organized by audience.

## Repository Structure

```
skills/
├── skill-development/              # Meta-level tooling for skill maintenance
│   ├── build-verify.py            # Orchestrates all steps below
│   ├── build-skills.py            # Copies shared files into each skill's references/
│   ├── add-blank-lines.py         # Formats markdown (blank lines before bullets)
│   ├── verify-references.py       # Checks all markdown links and file references
│   ├── verify-docs.py             # Confirms each skill has a matching .qmd in docs/
│   ├── rename-and-update.py       # Bulk renaming and updating all references
│   ├── replace-text.py            # Surgical text replacement
│   ├── SKILL_IMPLEMENTATION_GUIDE.md
│   └── README.md                  # Tool documentation
├── developers/                     # Developer-facing skills
│   ├── add-yardstick-metric/      # Creating custom metrics
│   ├── add-recipe-step/           # Creating preprocessing steps
│   ├── add-parsnip-engine/        # Adding engines to existing parsnip models
│   ├── add-parsnip-model/         # Creating new parsnip model types
│   ├── add-dials-parameter/       # Creating dials tuning parameters
│   ├── shared-references/         # R package patterns copied to ALL developer skills
│   ├── shared-references-parsnip/ # Patterns copied to parsnip skills only
│   ├── README.md
│   └── NEWS.md
├── users/                          # User-facing skills
│   └── tabular-data-ml/           # ML with tabular data using tidymodels
├── docs/                           # Quarto documentation site
│   ├── developers/                # Mirrors developers/ skill structure as .qmd files
│   ├── users/                     # Mirrors users/ skill structure as .qmd files
│   └── ...                        # Site config (_quarto.yml), assets, styles
├── repos/                          # Cloned Tidymodels repos for reference (not committed;
│                                   # only present when actively developing a skill)
└── .claude/                        # Claude Code configuration
```

### Shared References

Two shared directories exist under `developers/` — both are source files that
`build-skills.py` copies into each skill's `references/` folder during the build
step. **Never edit files in a skill's `references/` folder directly if they
originated from a shared directory — edit the source instead.**

- `shared-references/` — copied to **all** developer skills (universal R package
  patterns: testing, roxygen, prerequisites, etc.)
- `shared-references-parsnip/` — copied to parsnip skills only (`add-parsnip-engine`,
  `add-parsnip-model`); contains parsnip-specific patterns like prediction types,
  mode handling, engine implementation

To check whether a file in `references/` is a shared copy, run:

```bash
find developers/shared-references developers/shared-references-parsnip -name "<filename>"
```

## Audience-Specific Skills

### Developer Skills (`developers/`)
For creating Tidymodels extensions and contributing to packages:
- Building custom yardstick metrics
- Creating recipes preprocessing steps
- Package development workflows

### User Skills (`users/`)
For using Tidymodels in data analysis and modeling:
- Building ML pipelines for tabular data (`tabular-data-ml`)

## Working in This Repository

### Pre-Approved Commands

**⚠️ IMPORTANT**: This repository has a curated list of pre-approved commands in `.claude/settings.local.json`.

**When working in this repository, prefer using pre-approved commands:**
- All scripts in `skill-development/` are pre-approved and should be used for their intended purposes
- Common safe commands: `cd`, `ls`, `cat`, `grep`, `find`, `git clone`, `Rscript`, `quarto render`, `wc`
- Pre-approved Python execution: `python3 skill-development/*.py`

**Commands intentionally NOT pre-approved:**
- `mv` - Use `skill-development/rename-and-update.py` instead
- `sed`, `awk` - Use `skill-development/replace-text.py` instead
- `rm -rf` - Discuss with user before destructive operations

**Why this matters:**
- Pre-approved commands execute without user prompts, enabling faster workflows
- The exclusion list prevents accidental breaking changes (e.g., moving files without updating references)
- Using repository scripts ensures consistency and prevents broken references

### Before Committing Changes

**⚠️ CRITICAL**: Before committing any changes to skills, run:

```bash
# From project root - runs both developers/ and users/ by default
./skill-development/build-verify.py

# Or run for a specific directory
./skill-development/build-verify.py developers/
./skill-development/build-verify.py users/
```

This script:
1. **Builds**: Copies shared files to each skill's references folder
2. **Formats**: Adds blank lines before bullets in markdown files
3. **Panache**: Formats markdown files with panache (skips if not installed)
4. **Verifies**: Checks all markdown links and file references
5. **Docs**: Confirms each skill has a corresponding `.qmd` file in `docs/`, and that each `.md` file in the skill's `references/` folder has a matching `.qmd` in `docs/*/references/`

The script automatically skips workspace directories (any directory containing `-workspace` in the name).

Fix any errors before committing. This ensures all skills stay in sync, all links work correctly, and documentation is complete.

### Skill Maintenance Scripts

**⚠️ IMPORTANT**: For skill maintenance tasks, ALWAYS use the scripts in `skill-development/`:

- **Verification**: Use `build-verify.py` to verify all markdown links and file references
- **File Renaming**: Use `rename-and-update.py` for bulk renaming and updating all references
- **Text Replacement**: Use `replace-text.py` for surgical text replacement in specific files

**⚠️ CRITICAL - Do NOT use raw terminal commands for file operations:**

- **DON'T** use `mv` to rename files - Use `rename-and-update.py` instead
- **DON'T** use `sed`, `awk`, or text editors for bulk replacements - Use `replace-text.py` instead
- **DON'T** manually update references after moving files - `rename-and-update.py` does this automatically

**Why this matters:**
- `rename-and-update.py` automatically updates ALL references across the entire repository (markdown links, file paths, shell scripts, etc.)
- `replace-text.py` shows context and validates changes before applying them
- Raw `mv` commands break links and require manual reference hunting
- These scripts prevent broken references from reaching the repository

**Reference**: See [skill-development/README.md](../skill-development/README.md) for detailed documentation on what each script does, when to use it, and usage examples.

These scripts ensure consistency across the repository and catch broken references automatically. Do not manually rename files or perform bulk text replacements without using these tools.

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
- **Prefer pre-approved commands**: Use commands from `.claude/settings.local.json` when possible - these execute without prompts and are specifically chosen to prevent breaking changes
- **Use repository scripts for file operations**: NEVER use `mv`, `sed`, or `awk` directly - always use `rename-and-update.py` or `replace-text.py` to ensure all references are updated
- **Capitalize "Tidymodels"**: When used as a noun (the project, ecosystem, community, or brand), always capitalize as "Tidymodels". Keep lowercase only for: R package names (`tidymodels packages`), URLs (`tidymodels.org`), repository paths (`tidymodels/skills`), and code identifiers (`tidymodels-users`, `@tidymodels-skills`)

### Repository Access

The `repos/` directory contains cloned Tidymodels repositories for reference. These are optional but recommended for creating high-quality skills.

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

**Last Updated:** 2026-04-08
