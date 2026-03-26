# Restructure Plan: Developer and User Skills Split

## Context

Transform the repository from single-audience (developer skills only) to dual-audience (developer and user skills) for tidymodels. This is a significant architectural change that requires careful coordination.

**Current State:**
```
tidymodels/
├── add-yardstick-metric/
├── add-recipe-step/
├── shared-references/
├── dev-scripts/
├── SKILL_IMPLEMENTATION_GUIDE.md
├── README.md
└── NEWS.md
```

**Target State:**
```
skill-development/           (meta-level tooling for skill maintenance)
├── build-verify.py
├── rename-and-update.py
├── replace-text.py
└── SKILL_IMPLEMENTATION_GUIDE.md

developers/
├── add-yardstick-metric/
├── add-recipe-step/
├── shared-references/
├── README.md
└── NEWS.md

users/
├── shared-references/       (empty, ready for future content)
├── README.md                (explains this is for user skills)
└── .gitkeep
```

## Key Decisions

1. **Audience Split**: Root-level split into `developers/` and `users/`
2. **Scope**: Tidymodels-only (no multi-framework support)
3. **Structure**: Flattened (no `tidymodels/` subdirectory)
4. **References**: Separate `shared-references/` for each audience
5. **Meta-level Tooling**: `skill-development/` at root for build scripts and guides (applies to both audiences)
6. **Automation**: Use `replace-text.py` for surgical updates to external files

## Available Tools

### Primary Tools

#### 1. rename-and-update.py
- **Location**: `tidymodels/dev-scripts/rename-and-update.py` → `skill-development/rename-and-update.py`
- **Scope**: Recursive updates across all files in a directory tree
- **Use case**: Bulk internal updates (Phase 2)
- **Usage**: `./rename-and-update.py "tidymodels" "developers" --dry-run`

#### 2. replace-text.py
- **Location**: `tidymodels/dev-scripts/replace-text.py` → `skill-development/replace-text.py`
- **Scope**: Surgical replacement in a single specific file
- **Use case**: External file updates outside developers/ (Phase 4)
- **Usage**: `./replace-text.py <file> "old" "new" --dry-run`

#### 3. build-verify.py
- **Location**: `tidymodels/dev-scripts/build-verify.py` → `skill-development/build-verify.py`
- **Scope**: Rebuilds localized files and verifies markdown links
- **Use case**: Post-restructure verification (Phase 6)
- **Usage**: `./build-verify.py developers/`

## Implementation Plan

### Phase 1: Pre-Restructure Verification

```bash
cd tidymodels
./dev-scripts/build-verify.py
```

**Expected outcome**: Clean bill of health, or documented existing issues

---

### Phase 2: Update Internal References (Script-Based)

```bash
cd tidymodels/dev-scripts
./rename-and-update.py "tidymodels" "developers" --dry-run  # Preview
./rename-and-update.py "tidymodels" "developers"            # Apply
```

**Updates automatically:**
- Script docstrings and comments
- Internal markdown references
- Python/shell script references
- Any text within the tidymodels/ directory

**Files affected:**
- `dev-scripts/*.py` (all scripts)
- `shared-references/scripts/*.py` and `*.sh`
- `shared-references/scripts/README.md`
- All SKILL.md files (if they mention "tidymodels" in text)
- SKILL_IMPLEMENTATION_GUIDE.md
- README.md, NEWS.md

---

### Phase 3: Create New Directory Structure

#### 3.1 Create skill-development/ Directory
```bash
cd /Users/edgar/Projects/skills-personal
mkdir skill-development

# Move scripts from tidymodels/dev-scripts/ to skill-development/
# Move SKILL_IMPLEMENTATION_GUIDE.md to skill-development/
```

**Files to move:**
- `tidymodels/dev-scripts/build-verify.py` → `skill-development/build-verify.py`
- `tidymodels/dev-scripts/rename-and-update.py` → `skill-development/rename-and-update.py`
- `tidymodels/dev-scripts/replace-text.py` → `skill-development/replace-text.py`
- `tidymodels/SKILL_IMPLEMENTATION_GUIDE.md` → `skill-development/SKILL_IMPLEMENTATION_GUIDE.md`

**Note**: Delete the now-empty `tidymodels/dev-scripts/` directory

#### 3.2 Create skill-development/README.md

Create a README explaining the purpose of each tool and document:

```markdown
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
```

#### 3.3 Rename Main Directory
```bash
# Rename tidymodels/ to developers/
```

#### 3.4 Create users/ Directory
```bash
mkdir -p users/shared-references
```

#### 3.5 Create users/README.md
Create a README explaining this directory is for future user-facing skills:

```markdown
# Tidymodels User Skills

User-facing Claude Code skills for working with tidymodels packages.

## Status

This directory is ready for user skills to be added by the content team.

## Structure

- `shared-references/` - Reference materials shared across user skills
- Individual skill directories will be added here

## Difference from Developer Skills

- **Developer skills** (`../developers/`): For creating packages, adding metrics, building steps
- **User skills** (this directory): For using tidymodels packages in analysis and modeling

## Guidelines

When adding user skills, follow the structure established in developer skills:
- Each skill should have a `SKILL.md` entry point
- Reference materials go in the skill's `references/` folder
- Common references go in `shared-references/`
- Use the build-verify script pattern for validation
```

---

### Phase 4: Update External References (Automated with replace-text.py)

#### 4.1 Update .claude/CLAUDE.md

**Use replace-text.py for automated updates:**

```bash
cd skill-development

# Update path references (7 locations)
./replace-text.py ../.claude/CLAUDE.md "../tidymodels/" "../developers/" --dry-run
./replace-text.py ../.claude/CLAUDE.md "../tidymodels/" "../developers/"

# Update references to SKILL_IMPLEMENTATION_GUIDE.md location
./replace-text.py ../.claude/CLAUDE.md "../developers/SKILL_IMPLEMENTATION_GUIDE.md" "../skill-development/SKILL_IMPLEMENTATION_GUIDE.md" --dry-run
./replace-text.py ../.claude/CLAUDE.md "../developers/SKILL_IMPLEMENTATION_GUIDE.md" "../skill-development/SKILL_IMPLEMENTATION_GUIDE.md"
```

**Manual addition needed**: Add documentation for the new dual-audience structure and skill-development/ directory

#### 4.2 Update .claude-plugin/marketplace.json

**Use replace-text.py for path updates:**

```bash
cd skill-development

# Update skill paths
./replace-text.py ../.claude-plugin/marketplace.json "./tidymodels/" "./developers/" --dry-run
./replace-text.py ../.claude-plugin/marketplace.json "./tidymodels/" "./developers/"

# Update plugin name
./replace-text.py ../.claude-plugin/marketplace.json '"tidymodels-dev"' '"tidymodels-developers"' --dry-run
./replace-text.py ../.claude-plugin/marketplace.json '"tidymodels-dev"' '"tidymodels-developers"'
```

**Manual addition needed**: Add second plugin entry for `tidymodels-users` with empty skills array:

```json
{
  "name": "tidymodels-users",
  "publisher": "edgararuiz",
  "version": "0.1.0",
  "description": "Claude Code skills for using tidymodels packages",
  "skills": []
}
```

**Note**: Using standard semantic versioning. The `0.x.x` major version signals pre-release/unstable. Increment to `0.2.0`, `0.3.0` for iterations, then `1.0.0` when ready for production. 

#### 4.3 Update .claude/settings.local.json

**Use replace-text.py for automated updates:**

```bash
cd skill-development

# Update 70+ bash command allowlist entries
./replace-text.py ../.claude/settings.local.json "tidymodels/dev-scripts/" "skill-development/" --dry-run
./replace-text.py ../.claude/settings.local.json "tidymodels/dev-scripts/" "skill-development/"

./replace-text.py ../.claude/settings.local.json "tidymodels/shared-references/" "developers/shared-references/" --dry-run
./replace-text.py ../.claude/settings.local.json "tidymodels/shared-references/" "developers/shared-references/"

./replace-text.py ../.claude/settings.local.json "tidymodels/" "developers/" --dry-run
./replace-text.py ../.claude/settings.local.json "tidymodels/" "developers/"
```

#### 4.4 Update .gitignore

**Use replace-text.py for automated updates:**

```bash
cd skill-development

# Update existing entries
./replace-text.py ../.gitignore "tidymodels/" "developers/" --dry-run
./replace-text.py ../.gitignore "tidymodels/" "developers/"
```

#### 4.5 Update .github/workflows/test-clone-scripts.yml

**Use replace-text.py for automated updates:**

```bash
cd skill-development

# Update script paths (28+ references)
./replace-text.py ../.github/workflows/test-clone-scripts.yml "tidymodels/shared-references/scripts/" "developers/shared-references/scripts/" --dry-run
./replace-text.py ../.github/workflows/test-clone-scripts.yml "tidymodels/shared-references/scripts/" "developers/shared-references/scripts/"
```

#### 4.6 Update .github/workflows/README.md

**Use replace-text.py for automated updates:**

```bash
cd skill-development

# Update path references
./replace-text.py ../.github/workflows/README.md "../tidymodels/" "../developers/" --dry-run
./replace-text.py ../.github/workflows/README.md "../tidymodels/" "../developers/"
```

---

### Phase 5: Update Root README.md

**Current**: Stub placeholder

**Target**: Comprehensive explanation of the repository structure

```markdown
# Claude Code Skills for Tidymodels

A curated collection of [Claude Code skills](https://code.claude.com/docs/en/skills) for the tidymodels ecosystem, organized by audience.

## Structure

This repository contains two categories of skills:

### Developer Skills (`developers/`)

Skills for **creating and extending** tidymodels packages:
- Building custom yardstick metrics
- Creating recipes preprocessing steps
- Contributing to tidymodels packages

**Browse Developer Skills**: [developers/README.md](developers/README.md)

### User Skills (`users/`)

Skills for **using** tidymodels in data analysis and modeling:
- *(Coming soon - to be added by content team)*

**Browse User Skills**: [users/README.md](users/README.md)

## Installation

Install skills through the Claude Code marketplace:

```bash
# Add the marketplace
/plugin marketplace add edgararuiz/skills

# Install developer skills
/plugin install tidymodels-developers@tidymodels-skills

# Install user skills (when available)
/plugin install tidymodels-users@tidymodels-skills
```

## Audience Guide

**Choose Developer Skills if you are:**
- Creating a new R package that extends tidymodels
- Contributing code to tidymodels core packages
- Building custom metrics, models, or preprocessing steps

**Choose User Skills if you are:**
- Analyzing data with tidymodels
- Building predictive models
- Learning tidymodels workflows

## Resources

- [Tidymodels](https://www.tidymodels.org/)
- [Yardstick package](https://yardstick.tidymodels.org/)
- [Recipes package](https://recipes.tidymodels.org/)
- [Claude Code documentation](https://github.com/anthropics/claude-code)
```

---

### Phase 6: Rebuild and Verify

```bash
cd skill-development
./build-verify.py ../developers/
```

**Expected outcome**:
- All shared files copied to skill references/
- All markdown links verified
- No broken links reported

**Note**: build-verify.py now takes a directory path argument since it's no longer inside the developers/ directory

---

### Phase 7: Final Verification

```bash
# Check for remaining "tidymodels/" references
grep -r "tidymodels/" \
  --include="*.md" \
  --include="*.json" \
  --include="*.py" \
  --include="*.yml" \
  --include="*.sh" \
  --exclude-dir=repos \
  .

# Expected remaining references:
# - repos/tidymodels/* (actual package repositories - OK)
# - GitHub URLs like "github.com/tidymodels/yardstick" (OK)
# - References to "tidymodels ecosystem" in documentation (contextual - OK)
# - Old planning documents (historical reference - OK)
```

---

## Execution Checklist

- [ ] **Phase 1**: Run build-verify.py (verify clean state)
- [ ] **Phase 2**: Run rename-and-update.py with --dry-run
- [ ] **Phase 2**: Run rename-and-update.py (apply changes)
- [ ] **Phase 3.1**: Create skill-development/ directory
- [ ] **Phase 3.1**: Move dev-scripts/*.py to skill-development/
- [ ] **Phase 3.1**: Move SKILL_IMPLEMENTATION_GUIDE.md to skill-development/
- [ ] **Phase 3.2**: Create skill-development/README.md
- [ ] **Phase 3.3**: Rename tidymodels/ to developers/
- [ ] **Phase 3.4**: Create users/shared-references/
- [ ] **Phase 3.5**: Create users/README.md
- [ ] **Phase 4.1**: Update .claude/CLAUDE.md (replace-text.py + manual)
- [ ] **Phase 4.2**: Update .claude-plugin/marketplace.json (replace-text.py + manual)
- [ ] **Phase 4.3**: Update .claude/settings.local.json (replace-text.py)
- [ ] **Phase 4.4**: Update .gitignore (replace-text.py)
- [ ] **Phase 4.5**: Update .github/workflows/test-clone-scripts.yml (replace-text.py)
- [ ] **Phase 4.6**: Update .github/workflows/README.md (replace-text.py)
- [ ] **Phase 5**: Update root README.md (manual rewrite)
- [ ] **Phase 6**: Run skill-development/build-verify.py ../developers/
- [ ] **Phase 7**: Verify no stray "tidymodels/" references

---

## Critical Considerations

### 1. Marketplace Plugin Split
The marketplace.json now defines TWO plugins from the same repository. This is valid and intentional:
- `tidymodels-developers`: For package developers
- `tidymodels-users`: For analysis users (empty skills array initially)

### 2. Shared References Independence
`developers/shared-references/` and `users/shared-references/` are completely independent:
- No cross-references between them
- Different content for different audiences
- Users' content will be added by another developer later

### 3. skill-development/ Location
Build and maintenance scripts are now at root level in `skill-development/` because:
- They're meta-level tooling that applies to the repository itself, not to tidymodels development
- Both developers/ and users/ directories may eventually use these tools
- Clean separation of concerns: skill content vs skill tooling

### 4. SKILL_IMPLEMENTATION_GUIDE.md
This guide moves to `skill-development/` because:
- It's about creating skills for this repository, not about tidymodels development
- Meta-level documentation belongs with meta-level tooling
- Users will have different skill creation guidelines when their skills are added

### 5. Backward Compatibility
After this restructuring:
- All old paths become invalid
- This is a breaking change for any external references
- Increment version numbers in marketplace.json

---

## Testing Strategy

After restructuring:

1. **Build verification**: `cd developers && ./dev-scripts/build-verify.py`
2. **Link checking**: All internal links should resolve correctly
3. **Plugin loading**: Test loading both plugins in Claude Code
4. **Skill invocation**: Test that existing developer skills still trigger correctly
5. **Path references**: No broken references in any markdown or config files

---

## Rollback Plan

If issues arise:
- All changes are in version control
- Can revert to previous commit before restructuring
- Incremental commits between phases enable partial rollback

---

## Post-Restructure Tasks

After this restructuring is complete:

1. **Update marketplace listing**: If published, update marketplace description
2. **Documentation review**: Ensure all docs reflect new structure
3. **Version tags**: Consider tagging this as a major version (v1.0.0?)
4. **Notify collaborators**: Alert the developer who will add user skills about the new structure

---

## Expected Outcome

After completion:
- ✅ Clean dual-audience structure
- ✅ Developers/ contains all current skills
- ✅ Users/ ready for future content
- ✅ All references updated consistently
- ✅ All links verified and working
- ✅ Two plugins available in marketplace
- ✅ Clear documentation of structure and purpose
- ✅ No breaking existing functionality
