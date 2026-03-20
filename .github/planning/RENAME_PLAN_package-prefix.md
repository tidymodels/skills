# Rename Plan: Add "package-" Prefix to Shared References

**Date:** 2026-03-20
**Goal:** Add "package-" prefix to all shared-references files (except those already having it)
**Status:** Planning Phase

---

## Executive Summary

Add "package-" prefix to 5 shared-references files to create a consistent naming convention. This makes it clear these files are about R package development, distinguishing them from other types of shared references.

**Rationale:**
- Consistent naming convention (all shared references start with "package-")
- Clear distinction: these are R package development resources
- Future-proof: allows for non-package shared references if needed
- Already started: package-imports.md already has prefix

---

## Files to Rename

### Summary Table

| Current Name | New Name | References | Notes |
|--------------|----------|------------|-------|
| development-workflow.md | package-development-workflow.md | 31 | |
| extension-prerequisites.md | package-extension-prerequisites.md | 71 | |
| extension-requirements.md | package-extension-requirements.md | 102 | Just created! |
| package-imports.md | package-imports.md | N/A | ✅ Already has prefix |
| repository-access.md | package-repository-access.md | 11 | |
| roxygen-documentation.md | package-roxygen-documentation.md | 37 | |

**Total references to update:** ~252

---

## Detailed Impact Analysis

### 1. extension-requirements.md → package-extension-requirements.md (102 refs)

**This is the file we JUST created in the merge!** High-impact rename.

**Files affected:**
- Both SKILL.md files (yardstick, recipe)
- Both extension-guide.md files
- Both testing-patterns-source.md files
- Both troubleshooting-source.md files
- SKILL_IMPLEMENTATION_GUIDE.md
- Multiple references/ files in both skills
- Shared-references files

**Special considerations:**
- Has section anchors (#best-practices, #testing-requirements, #common-issues-solutions)
- Must preserve anchors in all updates
- Just localized to both skills

### 2. extension-prerequisites.md → package-extension-prerequisites.md (71 refs)

**Core setup file** - heavily referenced.

**Files affected:**
- SKILL.md files
- extension-guide.md files
- source-guide.md files
- Multiple shared-references files
- SKILL_IMPLEMENTATION_GUIDE.md

### 3. roxygen-documentation.md → package-roxygen-documentation.md (37 refs)

**Documentation guide** - medium impact.

**Files affected:**
- Multiple metric/step reference files
- Shared-references files
- SKILL.md files

### 4. development-workflow.md → package-development-workflow.md (31 refs)

**Workflow guide** - medium impact.

**Files affected:**
- SKILL.md files
- extension-guide.md files
- extension-requirements.md (the file we just created!)

### 5. repository-access.md → package-repository-access.md (11 refs)

**Repository cloning guide** - low impact.

**Files affected:**
- extension-prerequisites.md
- source-guide.md files
- SKILL_IMPLEMENTATION_GUIDE.md

---

## Implementation Strategy

### Pre-requisite: Permission Patterns

These scripts are already approved in `.claude/settings.local.json`:

```json
"Bash(python3:*)",
"Bash(*replace-text.py:*)",
"Bash(*rename-and-update.py:*)",
"Bash(*python3 tidymodels/dev-scripts/replace-text.py*)",
"Bash(./dev-scripts/verify-references.py)",
"Bash(bash tidymodels/dev-scripts/localize-shared-files.sh)"
```

This means Claude can run these commands without prompting, making the rename process smooth and automated.

### Approach: Use rename-and-update.py Script

We have a script specifically designed for this: `tidymodels/dev-scripts/rename-and-update.py`

**Advantages:**
- Automatically updates all markdown references
- Shows dry-run preview
- Updates all files in one operation per rename
- Handles both simple references and anchor links
- Already has permission patterns approved

**Process for each file:**
```bash
# 1. Dry run to see what would change
python3 tidymodels/dev-scripts/rename-and-update.py \
  old-name.md new-name.md --dry-run

# 2. Review output

# 3. Execute rename
python3 tidymodels/dev-scripts/rename-and-update.py \
  old-name.md new-name.md

# 4. Verify with verify-references.py
python3 tidymodels/dev-scripts/verify-references.py
```

### Order of Operations

Rename in this order (low impact → high impact):

1. **repository-access.md** (11 refs) - Simplest
2. **development-workflow.md** (31 refs)
3. **roxygen-documentation.md** (37 refs)
4. **extension-prerequisites.md** (71 refs)
5. **extension-requirements.md** (102 refs) - Most complex, do last

**Rationale:** Start with low-impact files to test the process, end with the most complex.

---

## Detailed Steps

### Step 1: Baseline Verification

```bash
# Verify current state has 0 errors
python3 tidymodels/dev-scripts/verify-references.py
```

Expected: 0 errors (we just finished the merge successfully)

### Step 2: Rename Files (One at a Time)

**Note:** All these commands use approved permission patterns from `.claude/settings.local.json` and will run without prompting.

**For EACH file in order:**

```bash
cd tidymodels

# Example for repository-access.md
python3 dev-scripts/rename-and-update.py \
  shared-references/repository-access.md \
  shared-references/package-repository-access.md \
  --dry-run

# Review output carefully

# If looks good, execute
python3 dev-scripts/rename-and-update.py \
  shared-references/repository-access.md \
  shared-references/package-repository-access.md

# Verify after EACH rename
python3 dev-scripts/verify-references.py
```

**IMPORTANT:** Verify after each rename before proceeding to next file.

### Step 3: Update Localized Copies

After all renames complete:

```bash
# Localize new filenames to skills
bash tidymodels/dev-scripts/localize-shared-files.sh
```

### Step 4: Fix Localized References

The localized files in `references/` will have broken links to old names in shared-references. Fix these:

**Option A: Re-run rename-and-update for localized files**
```bash
# For each skill's references/ folder
python3 dev-scripts/rename-and-update.py \
  add-yardstick-metric/references/OLD-NAME.md \
  add-yardstick-metric/references/package-NEW-NAME.md
```

**Option B: Use replace-text.py to update references**
```bash
# Update old references to new names in localized files
# (May be cleaner than re-renaming)
```

### Step 5: Final Verification

```bash
# Must show 0 errors
python3 tidymodels/dev-scripts/verify-references.py

# Check file counts
ls tidymodels/shared-references/*.md | wc -l  # Should be 6
ls tidymodels/add-yardstick-metric/references/package-*.md | wc -l  # Should be 6
ls tidymodels/add-recipe-step/references/package-*.md | wc -l  # Should be 6
```

### Step 6: Update Documentation

Update SKILL_IMPLEMENTATION_GUIDE.md:
- File structure diagram
- References to shared files
- Update "Last Updated" date to 2026-03-20

---

## Special Considerations

### Section Anchors

`extension-requirements.md` has section anchors that must be preserved:
- `#best-practices`
- `#testing-requirements`
- `#common-issues-solutions`

When renaming to `package-extension-requirements.md`, verify all anchor references work:
```
package-extension-requirements.md#best-practices
package-extension-requirements.md#testing-requirements
package-extension-requirements.md#common-issues-solutions
```

### Localization Script Compatibility

Verify `localize-shared-files.sh` works with new names:
```bash
# Script copies shared-references/*.md to each skill's references/
# Should automatically pick up renamed files
```

### SKILL.md Navigation Sections

Both SKILL.md files have "Shared References" sections listing these files. Update the display names for clarity:
```markdown
**Shared References:**
- [Extension Prerequisites](references/package-extension-prerequisites.md)
- [Extension Requirements](references/package-extension-requirements.md)
- [Development Workflow](references/package-development-workflow.md)
- [Roxygen Documentation](references/package-roxygen-documentation.md)
- [Package Imports](references/package-imports.md)
- [Repository Access](references/package-repository-access.md)
```

---

## Risks and Mitigations

### Risk 1: Anchor Link Breakage

**Risk:** Section anchors in extension-requirements.md might break

**Mitigation:**
- Verify anchor links explicitly after rename
- Test by clicking links in key files (SKILL.md, extension-guide.md)

### Risk 2: Script Doesn't Handle All References

**Risk:** rename-and-update.py might miss some references

**Mitigation:**
- Run verify-references.py after EACH rename
- Fix any errors before proceeding
- Use replace-text.py for manual fixes if needed

### Risk 3: Localized Files Out of Sync

**Risk:** Localized files might not update properly

**Mitigation:**
- Run localize-shared-files.sh after all renames
- Verify localized files exist with new names
- Check diff between shared and localized versions

### Risk 4: JUST Finished Major Merge

**Risk:** We JUST completed a complex merge. Doing another major rename immediately is risky.

**Mitigation:**
- This is just renaming (simpler than merge)
- Have script designed for this (rename-and-update.py)
- Verify after each step
- Can easily rollback individual renames if needed

---

## Testing Strategy

### After Each Rename

```bash
# 1. Verify references
python3 tidymodels/dev-scripts/verify-references.py

# 2. Spot check key files
grep "old-name.md" tidymodels/ -r --include="*.md"  # Should find nothing

# 3. Verify new name exists
ls -l tidymodels/shared-references/package-*.md
```

### After All Renames

```bash
# 1. Comprehensive verification
python3 tidymodels/dev-scripts/verify-references.py

# 2. Check all shared files have prefix
ls tidymodels/shared-references/*.md | grep -v "^package-" | wc -l  # Should be 0

# 3. Check localized copies
diff tidymodels/shared-references/package-extension-requirements.md \
     tidymodels/add-yardstick-metric/references/package-extension-requirements.md

# 4. Test key navigation paths manually
# - Open add-yardstick-metric/SKILL.md
# - Click through to shared references
# - Verify links work
```

---

## Rollback Plan

If issues arise:

### For Individual File Rollback

```bash
# Undo specific rename
python3 tidymodels/dev-scripts/rename-and-update.py \
  shared-references/package-new-name.md \
  shared-references/old-name.md

# Verify
python3 tidymodels/dev-scripts/verify-references.py
```

### For Complete Rollback

```bash
# Revert all changes from git
git checkout tidymodels/shared-references/
git checkout tidymodels/add-yardstick-metric/
git checkout tidymodels/add-recipe-step/
git checkout tidymodels/SKILL_IMPLEMENTATION_GUIDE.md

# Re-run localization to restore
bash tidymodels/dev-scripts/localize-shared-files.sh
```

---

## Success Criteria

✅ **All 5 files renamed** with package- prefix
✅ **verify-references.py reports 0 errors**
✅ **All shared-references files** have package- prefix
✅ **Localized copies created** via localize-shared-files.sh
✅ **Localized copies match** shared versions (verified with diff)
✅ **Section anchors work** in package-extension-requirements.md
✅ **SKILL_IMPLEMENTATION_GUIDE.md updated** with new names
✅ **Scripts used** for all renames (rename-and-update.py)

---

## Timeline Estimate

**Per file rename:**
- Dry run: 1 minute
- Review: 2 minutes
- Execute: 1 minute
- Verify: 1 minute
- **Total per file:** ~5 minutes

**Total for 5 files:** ~25 minutes

**Additional tasks:**
- Baseline verification: 2 minutes
- Localization: 2 minutes
- Fix localized references: 10 minutes
- Final verification: 5 minutes
- Update SKILL_IMPLEMENTATION_GUIDE.md: 5 minutes

**Total estimated time:** 45-50 minutes

---

## Decision Points

**Before proceeding, decide:**

1. **Timing:** Do this now or wait?
   - Pro (now): Fresh off merge, scripts tested, momentum
   - Con (now): Two major operations back-to-back, potential fatigue
   - Pro (wait): Let merge settle, test in practice first
   - Con (wait): More references will be added over time

2. **Scope:** Rename all 5 files or phase it?
   - All at once: Consistent, done quickly, one verification cycle
   - Phased: Lower risk, can test process on low-impact files first

3. **Alternative:** Keep current names?
   - Current state is functional
   - package-imports.md is the odd one out
   - Could rename package-imports.md to imports.md instead (inverse)

**Recommendation:** Proceed with all 5 files in one session (45-50 min total). The scripts are designed for this, and we've just validated the process works well with the merge.

---

## Open Questions

1. Should package-imports.md stay as-is or rename to imports.md?
   - Current plan: Keep package- prefix, add it to others
   - Alternative: Remove from package-imports.md
   [er] Keep as is

2. Should we update display names in SKILL.md to show "Package" prefix?
   - Example: "Package Extension Prerequisites" vs "Extension Prerequisites"
   - Or keep display names short, rely on filenames for clarity
   [er] Not necessary, this is mainly to make it easier for a human to know what's being synced from shared-references

3. Should verify-setup.R script be renamed to package-verify-setup.R?
   - Currently in shared-scripts/, not shared-references/
   - Out of scope for this rename, but worth considering
  [er] No, scripts are isolated in their own folder, so they're easy to identify 
---

## Notes

- This rename adds clarity to the file organization
- All files remain in shared-references/ directory
- No content changes, only filename changes
- Scripts automate the heavy lifting
- We have proven rollback process

---

**Status:** Ready for approval to proceed

**Next Step:** Get approval, then execute Step 1 (Baseline Verification)
