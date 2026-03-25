# Skill Development Tools

Meta-level tooling for maintaining and building skills in this repository.

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
./build-verify.py ../users/  # When user skills exist
```

**When to use**:
- Before committing changes
- After updating shared references
- After modifying skill structure

### rename-and-update.py
**Purpose**: Rename files and update all references across a directory tree.

**What it does**:
- Recursively searches for files to rename
- Updates all text references in .md, .py, .sh, .yml, .yaml, .json files
- Handles markdown links, file paths, and shell paths

**Usage**:
```bash
./rename-and-update.py "old-name" "new-name" --dry-run  # Preview
./rename-and-update.py "old-name" "new-name"            # Apply
```

**When to use**:
- Renaming skills or directories
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
- `build-verify.py` is mandatory before committing
- These tools can be used for both `developers/` and `users/` skills
