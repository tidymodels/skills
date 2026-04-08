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
**Purpose**: Orchestrate all build and verification steps in sequence.

**What it does**:
- **BUILD**: Calls `build-skills.py` to copy files from `shared-references/` to each skill's `references/` folder
- **FORMAT**: Calls `add-blank-lines.py` to add blank lines before bullet points in all markdown files
- **VERIFY**: Calls `verify-references.py` to check all markdown links resolve correctly
- **DOCS**: Calls `verify-docs.py` to confirm `.qmd` files exist for all skills

**Usage**:
```bash
./build-verify.py                # Runs against both developers/ and users/ (default)
./build-verify.py ../developers/ # Single directory
./build-verify.py ../users/
```

**When to use**:
- Before committing changes (mandatory)
- After updating shared references
- After modifying skill structure
- After adding or renaming skills

**Output format**:
- Each step displays a visible 60-character header (e.g., `================ VERIFY: Checking References ===============`)
- No blank lines between steps for compact, easy-to-scan output
- Workspace directories (containing `-workspace`) are automatically skipped

**Note**: This is a thin orchestrator. Each step can be run independently using the discrete scripts below.

---

### build-skills.py
**Purpose**: Localize shared files to each skill's references folder.

**What it does**:
- Copies files from `shared-references/` to each skill's `references/` folder
- Copies files from `shared-references-parsnip/` for skills with "parsnip" in the name
- Copies scripts from `shared-references/scripts/` to each skill
- Skips directories containing `-workspace` in the name

**Usage**:
```bash
./build-skills.py ../developers/
./build-skills.py ../users/
./build-skills.py ../developers/ --verbose  # Show skipped workspace folders
```

**When to use**:
- When you only need to update shared references without verification
- Testing build process independently
- Debugging build issues

---

### verify-references.py
**Purpose**: Verify all references in markdown files and scripts.

**What it does**:
- Verifies all markdown links resolve correctly
- Checks that referenced files exist
- Validates anchors within markdown files
- Checks file path references in script files
- Skips directories containing `-workspace` in the name

**Usage**:
```bash
./verify-references.py ../developers/
./verify-references.py ../users/
./verify-references.py ../developers/ --verbose  # Show skipped workspace folders
```

**When to use**:
- After modifying markdown links
- When debugging broken references
- Testing reference validation independently

---

### verify-docs.py
**Purpose**: Verify that skills have corresponding .qmd files in docs/.

**What it does**:
- Confirms each skill has a corresponding `.qmd` file in `docs/`
- Verifies each `.md` file in skill's `references/` has a matching `.qmd` in `docs/*/references/`
- Skips directories containing `-workspace` in the name

**Usage**:
```bash
./verify-docs.py ../developers/
./verify-docs.py ../users/
./verify-docs.py ../developers/ --verbose  # Show skipped workspace folders
```

**When to use**:
- After adding new skills
- After adding new reference files
- When debugging documentation structure

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

### grade-evaluations.py
**Purpose**: Grade skill evaluation outputs against configuration-based checks.

**What it does**:
- Reads grading configuration from JSON file (checks to perform per eval)
- Scans workspace/iteration-N/eval-M-name/outputs/ directories
- Runs checks: file counts, prohibited files, pattern matching, prefix usage
- Generates grading.json for each eval with pass/fail + evidence
- Creates summary report with overall pass rate

**Usage**:
```bash
# With explicit config
./grade-evaluations.py <workspace_path> --config <config_json>
./grade-evaluations.py ../developers/add-yardstick-metric-workspace/iteration-1 \
    --config ../developers/add-yardstick-metric/evals/grading-config.json

# With auto-detection (looks for ../developers/<skill>/evals/grading-config.json)
./grade-evaluations.py ../developers/add-yardstick-metric-workspace/iteration-1 \
    --skill add-yardstick-metric

# Custom output location
./grade-evaluations.py <workspace_path> --config <config_json> \
    --output /path/to/custom-summary.json
```

**Configuration format**:
- Define checks by context (extension vs source development)
- File count checks (exact, range, max)
- Prohibited files list (patterns to reject)
- Required files (patterns that must exist)
- Pattern checks (regex patterns in code)
- Prefix usage checks (e.g., yardstick::, recipes::)

**When to use**:
- After running skill evaluation tests
- To assess file discipline compliance
- To verify code patterns and structure
- To measure skill effectiveness quantitatively
- To compare iterations and track improvements

**Output**:
- Individual `grading.json` per eval directory
- Summary `grading-summary.json` in workspace root
- Console output with pass rates and failed checks

### add-blank-lines.py
**Purpose**: Add blank lines before bullet points in markdown files for readability.

**What it does**:
- Scans markdown files for bullet points (lines starting with `-` or `  -`)
- Adds blank lines before bullets that don't already have them
- Improves markdown readability when rendered
- Preserves existing formatting and spacing
- **Supports recursive directory processing** - processes all `.md` files in a directory tree
- Skips directories containing `-workspace` in the name

**Usage**:
```bash
# Single file
./add-blank-lines.py <markdown-file>
./add-blank-lines.py ../developers/add-parsnip-model/SKILL.md

# Recursive directory processing (all .md files)
./add-blank-lines.py <directory>
./add-blank-lines.py ../developers/
./add-blank-lines.py ../developers/shared-references/

# Show skipped workspace/hidden directories
./add-blank-lines.py ../developers/ --verbose
```

**When to use**:
- After creating or editing planning documents
- When markdown lists appear cramped when rendered
- Before committing documentation files
- To ensure consistent formatting across markdown files
- Bulk processing of all markdown files in a directory tree

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

### Full Workflow (Before Committing)
1. **Plan**: Document the changes needed
2. **Update internal references**: Use `rename-and-update.py` for bulk updates
3. **Update external references**: Use `replace-text.py` for specific files
4. **Verify**: Run `build-verify.py` to catch broken links (mandatory before committing)
5. **Test**: Ensure skills load and function correctly
6. **Commit**: Document changes clearly

### Running Components Independently
When working on specific aspects, you can run discrete scripts:

- **Just building**: `./build-skills.py ../developers/`
- **Just formatting**: `./add-blank-lines.py ../developers/`
- **Just verifying references**: `./verify-references.py ../developers/`
- **Just verifying docs**: `./verify-docs.py ../developers/`
- **Full pipeline**: `./build-verify.py ../developers/` (runs all of the above)

## Notes

- These tools operate on the repository structure, not on tidymodels code
- Always use `--dry-run` first to preview changes (for rename/replace scripts)
- `build-verify.py` is mandatory before committing skills in `developers/` or `users/`
- `build-verify.py` is a thin orchestrator that calls discrete scripts - each step can be run independently
- `rename-and-update.py` and `replace-text.py` work repository-wide (all folders)
- Discrete scripts (`build-skills.py`, `verify-references.py`, `verify-docs.py`, `add-blank-lines.py`) can be used individually for focused tasks
- All scripts automatically skip directories containing `-workspace` (e.g., `add-yardstick-metric-workspace`, `my-workspace-old`)
- Use `--verbose` flag with build/verify scripts to see which workspace directories are being skipped
- `build-verify.py` runs against both `developers/` and `users/` when no directory is specified
