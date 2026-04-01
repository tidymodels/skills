# Skill Development Tools

Meta-level tooling for maintaining and building skills in this repository.

**Note**: All commands in this document should be run from the `skill-development/` directory:
```bash
cd skill-development
./build-verify.py ../developers/
```

Alternatively, from the project root:
```bash
skill-development/build-verify.py developers/
```

## Tools

### build-verify.py
**Purpose**: Build and verify skills to ensure all references and links work correctly.

**What it does**:
- **BUILD**: Copies files from `shared-references/` to each skill's `references/` folder
- **VERIFY**: Verifies all markdown links resolve correctly and referenced files exist
- **DOCS**: Confirms that each skill has a corresponding `.qmd` file in `docs/`, and that each `.md` file in the skill's `references/` folder has a matching `.qmd` in `docs/*/references/`

**Usage**:
```bash
./build-verify.py ../developers/
./build-verify.py ../users/
```

**When to use**:
- Before committing changes
- After updating shared references
- After modifying skill structure
- After adding or renaming skills

### create-docs-wrappers.py
**Purpose**: Generate thin wrapper .qmd files in docs/ that include source .md files.

**What it does**:
- Recursively walks through skill references/ directories
- Creates 1-line wrapper .qmd files with correct include paths
- Handles arbitrary nesting depth (calculates correct ../ count)
- Skips scripts/ subdirectories
- Validates source files exist

**Usage**:
```bash
./create-docs-wrappers.py --skill users/tabular-data-ml --dry-run  # Preview
./create-docs-wrappers.py --skill users/tabular-data-ml            # Apply
./create-docs-wrappers.py --all                                    # All skills
./create-docs-wrappers.py --skill developers/add-yardstick-metric --force  # Overwrite
```

**When to use**:
- After adding a new skill to the repository
- After adding new reference files to a skill
- When restructuring docs/ folder
- After running build-verify.py (which copies shared references)

**Example wrapper output**:
- Flat reference: `{{< include ../../../../users/tabular-data-ml/references/data-spending.md >}}`
- Nested reference: `{{< include ../../../../../users/tabular-data-ml/references/feature-engineering/categorical.md >}}`

### count-skill-tokens.py
**Purpose**: Count lines and estimate tokens for a Claude Code skill directory.

**What it does**:
- Analyzes SKILL.md and all references/**/*.md files
- Counts lines and tokens using cl100k_base encoding
- Checks skill description length against metadata token limit (100 tokens)
- Flags SKILL.md if it exceeds limits (5000 tokens or 500 lines)
- Outputs a formatted Markdown summary table

**Usage**:
```bash
./count-skill-tokens.py <skill-directory>
./count-skill-tokens.py ../developers/add-yardstick-metric
```

**When to use**:
- Checking if a skill fits within Claude Code token limits
- Identifying which files contribute most to token count
- Validating skill size before deployment

### add-blank-lines.py
**Purpose**: Add blank lines before bullet points in markdown files for readability.

**What it does**:
- Scans markdown files for bullet points (lines starting with `-` or `  -`)
- Adds blank lines before bullets that don't already have them
- Improves markdown readability when rendered
- Preserves existing formatting and spacing

**Usage**:
```bash
./add-blank-lines.py <markdown-file>
./add-blank-lines.py ../developers/add-parsnip-model/SKILL.md
./add-blank-lines.py ../.github/planning/add-parsnip-model-plan.md
```

**When to use**:
- After creating or editing planning documents
- When markdown lists appear cramped when rendered
- Before committing documentation files
- To ensure consistent formatting across markdown files

### rename-and-update.py
**Purpose**: Rename files and update all references across the entire repository.

**What it does**:
- Recursively searches the entire repository for files to rename
- Updates all text references in .md, .R, .sh, .ps1, .py, .yml, .yaml, .json files
- Handles markdown links, file paths, and shell paths
- Works in all directories: `developers/`, `users/`, `docs/`, etc.

**Usage**:
```bash
./rename-and-update.py "old-name" "new-name" --dry-run  # Preview
./rename-and-update.py "old-name" "new-name"            # Apply

# Examples
./rename-and-update.py docs/users/old-file.qmd docs/users/new-file.qmd
./rename-and-update.py developers/old-skill/ developers/new-skill/
```

**When to use**:
- Renaming skills or directories
- Renaming files in docs/, users/, or developers/
- Bulk text replacement across multiple files
- Refactoring file organization

### replace-text.py
**Purpose**: Perform surgical text replacement in a single file.

**What it does**:
- Exact string replacement in a specific file
- Shows context of changes before applying
- Preserves file encoding and permissions

**Usage**:
```bash
./replace-text.py <file> "old text" "new text" --dry-run  # Preview
./replace-text.py <file> "old text" "new text"            # Apply
```

**When to use**:
- Updating configuration files
- Fixing specific references in external files
- Precise edits outside skill directories

## Documentation

### SKILL_IMPLEMENTATION_GUIDE.md
Comprehensive guide for creating new skills in this repository. Covers:
- File structure and organization
- Avoiding code duplication
- Testing and validation
- Best practices

**Audience**: Developers creating new skills for this repository (not tidymodels developers)

## Workflow

Typical workflow when making structural changes:

1. **Plan**: Document the changes needed
2. **Update internal references**: Use `rename-and-update.py` for bulk updates
3. **Update external references**: Use `replace-text.py` for specific files
4. **Verify**: Run `build-verify.py` to catch broken links
5. **Test**: Ensure skills load and function correctly
6. **Commit**: Document changes clearly

## Notes

- These tools operate on the repository structure, not on tidymodels code
- Always use `--dry-run` first to preview changes
- `build-verify.py` is mandatory before committing skills in `developers/` or `users/`
- `rename-and-update.py` and `replace-text.py` work repository-wide (all folders)
