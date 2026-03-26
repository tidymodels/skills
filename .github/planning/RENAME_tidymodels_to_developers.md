# Rename Plan: tidymodels/ → developers/

## Context

The repository needs to rename `tidymodels/` directory to `developers/` to better reflect the broader scope beyond tidymodels-specific development. This operation must:

1. Update ~150+ references across the codebase
2. Use existing rename scripts wherever possible to automate updates
3. Reduce README.md to a stub (no links, to be expanded later)
4. Verify all links work after the rename

## Scope Analysis

Based on comprehensive codebase exploration, `tidymodels/` is referenced in:

- **13 markdown files** (docs, planning, skill references)
- **2 config files** (marketplace.json, settings.local.json)
- **1 .gitignore file**
- **6 Python scripts** (including localized copies)
- **6 shell scripts** (including localized copies)
- **1 GitHub workflow** (28+ references)
- **~150+ total references**

## Available Tools

### Primary: rename-and-update.py
Location: `tidymodels/dev-scripts/rename-and-update.py`

**Capabilities:**
- Text replacement across all searchable files (.md, .py, .sh, .yml, .yaml, .json)
- Smart pattern matching for markdown links, file paths, shell paths
- Dry-run mode for safety
- **Scope limitation**: Only operates within `tidymodels/` directory

**Usage:**
```bash
cd tidymodels/dev-scripts
./rename-and-update.py "tidymodels" "developers" --dry-run    # Preview
./rename-and-update.py "tidymodels" "developers"               # Apply
```

### Secondary: build-verify.py
Location: `tidymodels/dev-scripts/build-verify.py` (soon `developers/dev-scripts/build-verify.py`)

**Capabilities:**
- Copies shared files to each skill's references/ folder
- Verifies all markdown links and file references
- Critical for post-rename validation

**Usage:**
```bash
cd developers
./dev-scripts/build-verify.py
```

## Implementation Plan

### Phase 1: Pre-Rename Verification
```bash
# Verify current state is clean
cd tidymodels
./dev-scripts/build-verify.py

# Document any existing issues
```

### Phase 2: Update Internal References Using Script
**Use rename-and-update.py for all text within tidymodels/**

```bash
# Preview changes
cd tidymodels/dev-scripts
./rename-and-update.py "tidymodels" "developers" --dry-run

# Apply changes
./rename-and-update.py "tidymodels" "developers"
```

This will update:
- All script docstrings and comments
- Internal markdown references
- Python/shell script path references
- Any other text within the tidymodels/ directory

**Files affected by script:**
- `dev-scripts/build-verify.py` (docstrings, comments)
- `dev-scripts/rename-and-update.py` (docstrings, comments)
- `shared-references/scripts/*.py` (comments, help text)
- `shared-references/scripts/*.sh` (comments)
- `shared-references/scripts/README.md`
- All SKILL.md files if they reference "tidymodels" in text
- Any references within skill documentation

### Phase 3: Rename Directory

Rename the directory from `tidymodels/` to `developers/`

### Phase 4: Update External References Manually

**Must update manually (outside developers/ directory scope):**

#### 4.1 Core Documentation
- `.claude/CLAUDE.md` - 7 references
  - Lines 42, 66, 69-70, 73-75
  - Update all `tidymodels/` → `developers/`

- `README.md` - Replace entire content with stub:
  ```markdown
  # Claude Code Skills - Personal Repository

  Personal repository for Claude Code skills and development tools.

  ## Status

  This repository is under active development.
  ```

#### 4.2 Configuration Files
- `.claude-plugin/marketplace.json`
  - Update plugin name: `tidymodels-skills` → `developers-skills`
  - Update descriptions mentioning tidymodels
  - Update paths: `./tidymodels/` → `./developers/`
  - Lines 2, 7, 12-13, 17-18

- `.claude/settings.local.json`
  - Update 70+ bash command allowlist entries
  - Find/replace all: `tidymodels/` → `developers/`
  - Lines 7-28, 41-77

- `.gitignore`
  - Update ignored paths: `tidymodels/` → `developers/`
  - Lines 12-14

#### 4.3 GitHub Workflows
- `.github/workflows/test-clone-scripts.yml`
  - Update all path references: `tidymodels/` → `developers/`
  - 28+ references across multiple lines
  - Use careful find/replace to update all instances

#### 4.4 Planning Documents (Optional - Historical Context)
Files in `.github/planning/` that reference tidymodels/:
- `MERGE_PLAN_extension-requirements.md`
- `MERGE_CHECKLIST_extension-requirements.md`
- `MOVE_PLAN_scripts-folder.md`
- `cloning-repos/REPOSITORY_ACCESS_PLAN.md`

**Decision:** Update these for consistency, or leave as historical reference?
**Recommendation:** Update them for clarity, using find/replace: `tidymodels/` → `developers/`

#### 4.5 GitHub Workflows Documentation
- `.github/workflows/README.md`
  - Lines 170-171
  - Update: `tidymodels/` → `developers/`

### Phase 5: Rebuild and Verify

```bash
# Run build-verify to rebuild localized files
cd developers
./dev-scripts/build-verify.py
```

This will:
1. Copy updated shared-references/ files to each skill's references/
2. Verify all markdown links work
3. Report any broken links or missing files

### Phase 6: Final Verification

```bash
# Verify no "tidymodels/" strings remain (except in appropriate contexts)
grep -r "tidymodels/" --include="*.md" --include="*.json" --include="*.py" --include="*.yml" .

# Expected remaining references:
# - repos/tidymodels/* (actual package repos)
# - References to "tidymodels ecosystem" in documentation (contextual, not paths)
# - GitHub URLs to tidymodels org
```

## Execution Checklist

- [ ] Phase 1: Run current build-verify.py (verify clean state)
- [ ] Phase 2: Run rename-and-update.py with --dry-run
- [ ] Phase 2: Run rename-and-update.py (apply changes)
- [ ] Phase 3: Rename directory to developers/
- [ ] Phase 4.1: Update .claude/CLAUDE.md
- [ ] Phase 4.1: Replace README.md with stub
- [ ] Phase 4.2: Update .claude-plugin/marketplace.json
- [ ] Phase 4.2: Update .claude/settings.local.json
- [ ] Phase 4.2: Update .gitignore
- [ ] Phase 4.3: Update .github/workflows/test-clone-scripts.yml
- [ ] Phase 4.4: Update .github/planning/*.md files
- [ ] Phase 4.5: Update .github/workflows/README.md
- [ ] Phase 5: Run developers/dev-scripts/build-verify.py
- [ ] Phase 5: Fix any reported broken links
- [ ] Phase 6: Verify with grep (check for remaining "tidymodels/" refs)

## Critical Notes

1. **Use rename-and-update.py first** - This handles all internal references automatically
2. **build-verify.py is mandatory** - Catches broken links after changes
3. **Scope awareness** - rename-and-update.py only works within its directory; external files need manual updates
4. **Dry-run everything** - Both scripts support preview modes

## Risk Mitigation

- Dry-run mode shows changes before applying
- build-verify.py validates all links
- Scripts tested and used in production
- Incremental commits between phases allow rollback

## Expected Outcome

After completion:
- Directory renamed: `developers/`
- All ~150+ references updated consistently
- README.md reduced to stub
- All links verified and working
- Ready for future expansion with non-tidymodels skills
