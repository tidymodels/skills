# Merge Plan: extension-requirements.md

**Date:** 2026-03-20
**Goal:** Consolidate three extension development files into a single comprehensive guide
**Status:** Planning Phase
**Note:** This is Phase 1 of a larger documentation consolidation project

---

## Executive Summary

Merge `best-practices-extension.md`, `testing-patterns-extension.md`, and `troubleshooting-extension.md` into a unified `extension-requirements.md` document that provides complete, organized guidance for extension developers.

**Rationale:**
- Reduce navigation friction (one document vs. three separate files)
- Eliminate content duplication across files
- Create logical flow from best practices → testing → troubleshooting
- Maintain single source of truth principle
- Easier for Claude to consume all context at once

---

## Current State Analysis

### Files to Merge

1. **best-practices-extension.md**
   - Location: `shared-references/best-practices-extension.md`
   - Purpose: Code style, conventions, and development guidelines
   - Estimated size: ~200-300 lines

2. **testing-patterns-extension.md**
   - Location: `shared-references/testing-patterns-extension.md`
   - Purpose: Testing strategies, test structure, and patterns
   - Estimated size: ~300-400 lines

3. **troubleshooting-extension.md**
   - Location: `shared-references/troubleshooting-extension.md`
   - Purpose: Common issues, error messages, and solutions
   - Estimated size: ~200-300 lines

**Combined estimated size:** ~700-1000 lines (well within readable limits)

### Current References to These Files

Files that link to the three documents:
- `SKILL.md` files (add-yardstick-metric, add-recipe-step)
- `extension-guide.md` files
- Other reference documents
- SKILL_IMPLEMENTATION_GUIDE.md

---

## Proposed Structure: extension-requirements.md

### Document Organization

```markdown
# Extension Development Requirements

Complete guide for developing R package extensions to tidymodels packages.

---

## Table of Contents

1. [Best Practices](#best-practices)
   - Code Style
   - Package Structure
   - Function Design
   - Documentation Standards
   - Error Handling

2. [Testing Requirements](#testing-requirements)
   - Required Test Categories
   - Test Structure
   - Test Helpers
   - Coverage Standards
   - Testing Workflow

3. [Common Issues & Solutions](#common-issues-solutions)
   - Package Setup Issues
   - Testing Issues
   - Documentation Issues
   - Dependency Issues
   - R CMD check Issues

4. [Quick Reference](#quick-reference)
   - Checklist: Before First Commit
   - Checklist: Before Release

---

## Best Practices

[Content from best-practices-extension.md]

### Code Style
[Section content...]

### Package Structure
[Section content...]

[... continue with all sections ...]

---

## Testing Requirements

[Content from testing-patterns-extension.md]

### Required Test Categories
[Section content...]

### Test Structure
[Section content...]

[... continue with all sections ...]

---

## Common Issues & Solutions

[Content from troubleshooting-extension.md]

### Package Setup Issues

#### Issue: "Package not found"
**Problem:** [description]
**Solution:** [fix]
**Example:**
```r
[code]
```

[... continue with all issues ...]

---

## Quick Reference

### Checklist: Before First Commit
- [ ] All functions documented with roxygen2
- [ ] Tests written for all exported functions
- [ ] `devtools::document()` runs without errors
- [ ] `devtools::load_all()` loads successfully
- [ ] `devtools::test()` passes all tests

### Checklist: Before Release
- [ ] `devtools::check()` passes with no errors, warnings, or notes
- [ ] All examples run successfully
- [ ] NEWS.md updated
- [ ] Version bumped in DESCRIPTION
- [ ] README up to date
```

---

## Content Integration Strategy

### Section 1: Best Practices

**Source:** `best-practices-extension.md`

**Content to include:**
- Code style guidelines (base pipe, for-loops, etc.)
- Function naming conventions
- Package structure recommendations
- Documentation standards
- Error handling patterns (cli::cli_abort)
- Exported vs internal functions
- DESCRIPTION file requirements

**Content to exclude:**
- Anything specific to source development
- Redundant setup instructions (belongs in extension-prerequisites.md)

### Section 2: Testing Requirements

**Source:** `testing-patterns-extension.md`

**Content to include:**
- Required test categories (basic functionality, edge cases, errors, warnings)
- Test file organization and naming
- Test structure and patterns
- Test helper creation
- Coverage expectations
- Integration with devtools workflow
- Snapshot testing (if applicable)

**Content to exclude:**
- Source-specific test helpers
- Internal test data (that's for source development)

### Section 3: Common Issues & Solutions

**Source:** `troubleshooting-extension.md`

**Content to include:**
- Package setup errors
- Testing failures
- Documentation generation issues
- Dependency problems
- R CMD check errors/warnings/notes
- Common user mistakes
- Debugging strategies

**Content to organize by:**
- Error message or symptom
- Clear problem statement
- Step-by-step solution
- Code examples where helpful

### Section 4: Quick Reference

**New content to create:**
- Pre-commit checklist
- Pre-release checklist
- Quick command reference
- Common patterns at a glance

---

## Migration Strategy

### Phase 1: Create New Document

1. **Read all three source files** to understand full content
2. **Create extension-requirements.md** in `shared-references/`
3. **Merge content** following proposed structure
4. **Add Table of Contents** with anchor links
5. **Add cross-references** between sections
6. **Review for duplication** and consolidate

### Phase 2: Update References

**Note:** Use `replace-text.py` (not `rename-and-update.py`) because we're merging files, not renaming them.

1. **Use replace-text.py** to update all file references systematically:
   ```bash
   # Pattern: Update old filename to new filename with section anchor
   # Process each file that references the old documents

   # Example for a single file:
   python3 tidymodels/dev-scripts/replace-text.py \
     add-yardstick-metric/SKILL.md \
     "best-practices-extension.md" \
     "extension-requirements.md#best-practices" \
     --dry-run

   # Review output, then apply without --dry-run
   ```

2. **Follow the batch replacement patterns** documented in "Recommended Workflow" section below

3. **Run verify-references.py** after each batch to catch any issues early:
   ```bash
   python3 tidymodels/dev-scripts/verify-references.py
   ```

4. **Update SKILL.md navigation sections** in both skills using replace-text.py

### Phase 3: Cleanup

1. **Delete old files** from `shared-references/`:
   - `best-practices-extension.md`
   - `testing-patterns-extension.md`
   - `troubleshooting-extension.md`

2. **Delete old localized files** from each skill's `references/` folder:
   - `add-yardstick-metric/references/best-practices-extension.md`
   - `add-yardstick-metric/references/testing-patterns-extension.md`
   - `add-yardstick-metric/references/troubleshooting-extension.md`
   - `add-recipe-step/references/best-practices-extension.md`
   - `add-recipe-step/references/testing-patterns-extension.md`
   - `add-recipe-step/references/troubleshooting-extension.md`

3. **Run localize-shared-files.sh** to copy new `extension-requirements.md` to skills
   ```bash
   ./tidymodels/dev-scripts/localize-shared-files.sh
   ```

4. **Verify** no broken links remain

### Phase 4: Documentation Updates

1. **Update SKILL_IMPLEMENTATION_GUIDE.md**:
   - Remove references to three separate files
   - Document new single-file approach
   - Update file structure examples

---

## Tools and Methodology

### Script-First Approach

**IMPORTANT:** Always use the provided scripts instead of manual commands when applicable:
- ✅ Use `verify-references.py` instead of manually checking links
- ✅ Use `replace-text.py` instead of manual `sed` or text editor find/replace
- ✅ Use `rename-and-update.py` instead of `mv` + manual link updates
- ❌ Do NOT use manual approaches (`ls`, `mv`, `sed`, `grep -r`) for tasks covered by scripts
- ❌ Do NOT manually edit links when scripts can handle updates automatically

Scripts provide safety (dry-run modes), consistency, and comprehensive updates across all files.

### Available Maintenance Scripts

All scripts located in `tidymodels/dev-scripts/`:

1. **verify-references.py**
   - Validates all markdown links and anchors
   - Checks for broken file references
   - Identifies missing anchor targets
   - Run before and after migration to ensure no broken links

   ```bash
   python3 tidymodels/dev-scripts/verify-references.py
   ```

2. **replace-text.py**
   - Performs exact text replacements in files
   - Useful for updating link text or fixing specific references
   - Dry-run mode available for safety

   ```bash
   # Dry run to preview changes
   python3 tidymodels/dev-scripts/replace-text.py <file> "old text" "new text" --dry-run

   # Apply changes
   python3 tidymodels/dev-scripts/replace-text.py <file> "old text" "new text"
   ```

3. **rename-and-update.py**
   - Renames files and updates all references automatically
   - Handles markdown links in all files
   - Dry-run mode available

   ```bash
   # See what would change
   python3 tidymodels/dev-scripts/rename-and-update.py old-file.md new-file.md --dry-run

   # Execute rename and updates
   python3 tidymodels/dev-scripts/rename-and-update.py old-file.md new-file.md
   ```

### Recommended Workflow

**Step 1: Baseline verification**
```bash
# Check current state - should show 0 errors
python3 tidymodels/dev-scripts/verify-references.py
```

**Step 2: Create and populate new file**
- Manually create `extension-requirements.md`
- Merge content from three source files
- Add table of contents with proper anchors

**Step 3: Update references with targeted replacements**
```bash
# Update each old filename to new filename
# Example pattern for each file:
python3 tidymodels/dev-scripts/replace-text.py \
  add-yardstick-metric/references/some-file.md \
  "best-practices-extension.md" \
  "extension-requirements.md#best-practices"

# Batch process multiple files if needed
for file in add-yardstick-metric/references/*.md; do
  python3 tidymodels/dev-scripts/replace-text.py "$file" \
    "testing-patterns-extension.md" \
    "extension-requirements.md#testing-requirements"
done
```

**Step 4: Verify after updates**
```bash
# Should still show 0 errors
python3 tidymodels/dev-scripts/verify-references.py
```

### Lessons from Recent Link Fix (2026-03-20)

Successfully fixed 63 broken references using this methodology:

1. **Discovery**: `verify-references.py` identified all broken links
2. **Pattern recognition**: Grouped similar issues by error type
3. **Batch fixes**: Used `replace-text.py` to fix common patterns across files
4. **Validation**: Re-ran verification to confirm all fixes
5. **Documentation**: Updated NEWS.md with changes

**Key insights:**
- Run verification before starting to establish baseline
- Group similar link patterns for efficient batch processing
- Use `--dry-run` flags to preview changes before applying
- Verify after each major batch of changes
- Fix section anchors last (after confirming file references work)

**Common patterns to fix during this merge:**
```bash
# Pattern 1: Basic filename change
"best-practices-extension.md" → "extension-requirements.md#best-practices"
"testing-patterns-extension.md" → "extension-requirements.md#testing-requirements"
"troubleshooting-extension.md" → "extension-requirements.md#common-issues-solutions"

# Pattern 2: Section-specific references
"[Best Practices](best-practices-extension.md#code-style)"
  → "[Best Practices](extension-requirements.md#code-style)"

# Pattern 3: Cross-references from other files
"../best-practices-extension.md" → "../extension-requirements.md#best-practices"
```

---

## Impact Assessment

### Files Affected

**Directly modified:**
- `shared-references/extension-requirements.md` (new)
- `add-yardstick-metric/SKILL.md`
- `add-yardstick-metric/extension-guide.md`
- `add-yardstick-metric/references/extension-requirements.md` (via localization)
- `add-recipe-step/SKILL.md`
- `add-recipe-step/extension-guide.md`
- `add-recipe-step/references/extension-requirements.md` (via localization)
- `SKILL_IMPLEMENTATION_GUIDE.md`

**Deleted:**
- `shared-references/best-practices-extension.md`
- `shared-references/testing-patterns-extension.md`
- `shared-references/troubleshooting-extension.md`
- `add-yardstick-metric/references/best-practices-extension.md`
- `add-yardstick-metric/references/testing-patterns-extension.md`
- `add-yardstick-metric/references/troubleshooting-extension.md`
- `add-recipe-step/references/best-practices-extension.md`
- `add-recipe-step/references/testing-patterns-extension.md`
- `add-recipe-step/references/troubleshooting-extension.md`

### Benefits

✅ **Single source for all extension development guidance**
✅ **Reduced navigation overhead** (one file vs three)
✅ **Better context** for Claude (loads all requirements at once)
✅ **Easier to maintain** (one file to update)
✅ **Clearer progression** (practices → testing → troubleshooting)
✅ **Reduced duplication** between files
✅ **More cohesive documentation** experience

### Risks

⚠️ **Large file size** - Might approach or exceed 1000 lines
   - Mitigation: Use clear section headers, table of contents
   - Still well within readable limits for both humans and Claude

⚠️ **Link breakage** - Many existing links will need updating
   - Mitigation: Use rename-and-update.py script + manual review
   - Test all links after migration

⚠️ **Context switch for maintainers** - Different structure to learn
   - Mitigation: Clear documentation in SKILL_IMPLEMENTATION_GUIDE.md
   - Logical organization makes navigation easier

---

## Implementation Steps

### Step 1: Preparation
- [ ] Read all three source files completely
- [ ] Identify duplicate content across files
- [ ] Note all cross-references between files
- [ ] Create detailed content outline

### Step 2: Content Creation
- [ ] Create `extension-requirements.md` with full structure
- [ ] Merge best practices content (Section 1)
- [ ] Merge testing patterns content (Section 2)
- [ ] Merge troubleshooting content (Section 3)
- [ ] Create quick reference section (Section 4)
- [ ] Add table of contents with anchor links
- [ ] Review for flow and coherence
- [ ] Eliminate any duplication

### Step 3: Reference Updates
- [ ] Use replace-text.py to update references (NOT rename-and-update.py - we're merging, not renaming)
- [ ] Process each old filename with appropriate section anchors
- [ ] Run verify-references.py after each batch of changes
- [ ] Update SKILL.md quick navigation sections using replace-text.py
- [ ] Update extension-guide.md references using replace-text.py
- [ ] Final verification: run verify-references.py to confirm 0 errors

### Step 4: Cleanup
- [ ] Delete three old files from shared-references/
- [ ] Delete six old localized files from skill references/ folders
- [ ] Run localize-shared-files.sh
- [ ] Verify localized copies in skills

### Step 5: Documentation
- [ ] Update SKILL_IMPLEMENTATION_GUIDE.md
- [ ] Review all changes one final time

### Step 6: Validation
- [ ] Run verify-references.py to validate all links (must show 0 errors)
- [ ] Manually review key navigation sections in SKILL.md files
- [ ] Verify section anchors work correctly in extension-requirements.md
- [ ] Ensure localization script works correctly
- [ ] Check file sizes are reasonable

---

## Success Criteria

✅ **Single comprehensive file** exists with all extension development guidance
✅ **No broken links** - verify-references.py reports 0 errors
✅ **Clear structure** with logical flow between sections
✅ **Table of contents** allows quick navigation
✅ **All references updated** using replace-text.py (not manual edits)
✅ **Old files deleted** from both shared-references/ and all skill references/ folders
✅ **Documentation updated** in SKILL_IMPLEMENTATION_GUIDE.md
✅ **File size** remains under 1500 lines for readability
✅ **Cross-references** between sections work correctly
✅ **Scripts used** for all applicable operations (no manual mv/sed/grep)

---

## Timeline Estimate

- **Step 1 (Preparation):** 15 minutes - Read and analyze files
- **Step 2 (Content Creation):** 30-45 minutes - Merge and organize content
- **Step 3 (Reference Updates):** 15-20 minutes - Run scripts and manual fixes
- **Step 4 (Cleanup):** 10 minutes - Delete old files and localize
- **Step 5 (Documentation):** 10 minutes - Update SKILL_IMPLEMENTATION_GUIDE.md
- **Step 6 (Validation):** 15 minutes - Test and verify

**Total estimated time:** 95-115 minutes (~1.5-2 hours)

---

## Open Questions

1. Should we add a "Development Workflow" section or keep that separate?
   - **Decision:** Keep separate in development-workflow.md (already exists)

2. Should quick reference be at the beginning or end?
   - **Decision:** At the end (summary after reading full content)

3. How deep should troubleshooting examples be?
   - **Decision:** Full code examples for common issues, brief solutions for rare ones

4. Should we include package-specific patterns here?
   - **Decision:** No, this is universal extension guidance only

---

## Rollback Plan

If issues arise:

1. **Revert changes** by restoring three original files from git history
2. **Re-run rename-and-update.py** in reverse to fix links
3. **Re-run localize-shared-files.sh** to restore localized copies
4. **Document lessons learned** for next attempt

---

## Next Steps

**After approval of this plan:**

1. Begin Step 1: Read all three source files
2. Create detailed content outline
3. Begin content creation in extension-requirements.md
4. Proceed through implementation steps
5. Validate and deploy

**Approval needed from:** Repository maintainer
**Expected start date:** After plan review
