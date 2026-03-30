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
- Copies files from `shared-references/` to each skill's `references/` folder
- Verifies all markdown links resolve correctly
- Checks that referenced files exist

**Usage**:
```bash
./build-verify.py ../developers/
./build-verify.py ../users/
```

**When to use**:
- Before committing changes
- After updating shared references
- After modifying skill structure

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

### rename-and-update.py
**Purpose**: Rename files and update all references across the entire repository.

**What it does**:
- Recursively searches the entire repository for files to rename
- Updates all text references in .md, .py, .sh, .yml, .yaml, .json files
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
