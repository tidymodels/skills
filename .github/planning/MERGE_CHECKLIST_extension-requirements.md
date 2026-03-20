# Merge Checklist: extension-requirements.md

**Date Started:** ___________
**Date Completed:** ___________
**Related Plan:** MERGE_PLAN_extension-requirements.md

---

## Pre-Flight Checks

- [ ] Read MERGE_PLAN_extension-requirements.md completely
- [ ] Understand script-first approach (use scripts, not manual commands)
- [ ] Verify all scripts are in `tidymodels/dev-scripts/`
- [ ] Run baseline verification:
  ```bash
  python3 tidymodels/dev-scripts/verify-references.py
  ```
  Expected: 0 errors before starting

---

## Step 1: Preparation (15 min)

- [ ] Read `shared-references/best-practices-extension.md` completely
- [ ] Read `shared-references/testing-patterns-extension.md` completely
- [ ] Read `shared-references/troubleshooting-extension.md` completely
- [ ] Identify duplicate content across the three files
- [ ] Note all cross-references between files
- [ ] Create detailed content outline for merged document

---

## Step 2: Content Creation (30-45 min)

- [ ] Create `shared-references/extension-requirements.md` with structure:
  - [ ] Header and introduction
  - [ ] Table of contents with anchor links
  - [ ] Section 1: Best Practices (from best-practices-extension.md)
  - [ ] Section 2: Testing Requirements (from testing-patterns-extension.md)
  - [ ] Section 3: Common Issues & Solutions (from troubleshooting-extension.md)
  - [ ] Section 4: Quick Reference (new content - checklists)
- [ ] Review merged content for flow and coherence
- [ ] Eliminate any duplicate content
- [ ] Verify all section anchors match planned references

---

## Step 3: Reference Updates (15-20 min)

### 3.1: Update Links to extension-requirements.md

Use `replace-text.py` for all updates. Process files systematically:

**For add-yardstick-metric:**
- [ ] Update SKILL.md:
  ```bash
  python3 tidymodels/dev-scripts/replace-text.py add-yardstick-metric/SKILL.md \
    "best-practices-extension.md" "extension-requirements.md#best-practices" --dry-run
  # Review, then run without --dry-run
  ```
- [ ] Update extension-guide.md (repeat pattern for testing/troubleshooting)
- [ ] Update other references/ files as needed

**For add-recipe-step:**
- [ ] Update SKILL.md
- [ ] Update extension-guide.md
- [ ] Update other references/ files as needed

**For shared references:**
- [ ] Update SKILL_IMPLEMENTATION_GUIDE.md
- [ ] Update any other files referencing the three old files

### 3.2: Verify After Each Batch
- [ ] Run after yardstick updates:
  ```bash
  python3 tidymodels/dev-scripts/verify-references.py
  ```
- [ ] Run after recipe updates:
  ```bash
  python3 tidymodels/dev-scripts/verify-references.py
  ```
- [ ] Run after shared-references updates:
  ```bash
  python3 tidymodels/dev-scripts/verify-references.py
  ```

---

## Step 4: Cleanup (10 min)

### 4.1: Delete Old Files from shared-references/
- [ ] Delete `shared-references/best-practices-extension.md`
- [ ] Delete `shared-references/testing-patterns-extension.md`
- [ ] Delete `shared-references/troubleshooting-extension.md`

### 4.2: Delete Old Localized Files
- [ ] Delete `add-yardstick-metric/references/best-practices-extension.md`
- [ ] Delete `add-yardstick-metric/references/testing-patterns-extension.md`
- [ ] Delete `add-yardstick-metric/references/troubleshooting-extension.md`
- [ ] Delete `add-recipe-step/references/best-practices-extension.md`
- [ ] Delete `add-recipe-step/references/testing-patterns-extension.md`
- [ ] Delete `add-recipe-step/references/troubleshooting-extension.md`

### 4.3: Localize New File
- [ ] Run localization script:
  ```bash
  ./tidymodels/dev-scripts/localize-shared-files.sh
  ```
- [ ] Verify `add-yardstick-metric/references/extension-requirements.md` created
- [ ] Verify `add-recipe-step/references/extension-requirements.md` created

---

## Step 5: Documentation Updates (10 min)

- [ ] Update SKILL_IMPLEMENTATION_GUIDE.md:
  - [ ] Remove references to three separate files
  - [ ] Document new single-file approach
  - [ ] Update file structure examples
  - [ ] Update shared-references section

---

## Step 6: Final Validation (15 min)

- [ ] Run final verification (MUST show 0 errors):
  ```bash
  python3 tidymodels/dev-scripts/verify-references.py
  ```
- [ ] Manually review key sections in both SKILL.md files
- [ ] Verify table of contents links work in extension-requirements.md
- [ ] Test a few section anchors manually (e.g., `#best-practices`, `#testing-requirements`)
- [ ] Check file size of extension-requirements.md (should be under 1500 lines)
- [ ] Verify localized copies match shared version

---

## Success Criteria Verification

- [ ] ✅ Single comprehensive extension-requirements.md exists
- [ ] ✅ verify-references.py reports 0 errors
- [ ] ✅ Clear structure with logical flow
- [ ] ✅ Table of contents with working anchor links
- [ ] ✅ All references updated using replace-text.py (not manual edits)
- [ ] ✅ All 9 old files deleted (3 from shared, 6 from skill references)
- [ ] ✅ SKILL_IMPLEMENTATION_GUIDE.md updated
- [ ] ✅ File size under 1500 lines
- [ ] ✅ Scripts used for all applicable operations (no manual mv/sed/grep)
- [ ] ✅ Localized copies created via localize-shared-files.sh

---

## Post-Completion

- [ ] Mark completion date at top of checklist
- [ ] Document any deviations from plan in MERGE_PLAN_extension-requirements.md
- [ ] Note lessons learned for future merges
- [ ] (Later) Add entry to NEWS.md as part of larger documentation update

---

## Rollback (if needed)

If issues arise:
- [ ] Revert to previous commit
- [ ] Restore three original files from git history
- [ ] Re-run localize-shared-files.sh
- [ ] Document what went wrong
- [ ] Update plan before retry

---

**Notes:**

[Space for notes during execution]
