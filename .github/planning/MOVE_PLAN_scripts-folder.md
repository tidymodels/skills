# Move Plan: shared-scripts → shared-references/scripts

**Date:** 2026-03-20
**Goal:** Reorganize scripts location to match the structure used in skill references/ folders
**Status:** Planning Phase

---

## Executive Summary

Move `tidymodels/shared-scripts/` to `tidymodels/shared-references/scripts/` to create consistency between the source structure and the localized structure in each skill's `references/` folder.

**Rationale:**
- Match the pattern already established in skills (scripts live under references/)
- Reduce path complexity (one less top-level directory)
- Logical grouping: scripts are reference materials just like markdown docs
- Consistency: skills have `references/scripts/`, so shared should have `shared-references/scripts/`

---

## Current State Analysis

### Current Directory Structure

```
tidymodels/
├── shared-scripts/              # Current location
│   ├── clone-tidymodels-repos.ps1
│   ├── clone-tidymodels-repos.py
│   ├── clone-tidymodels-repos.sh
│   ├── README.md
│   └── verify-setup.R
├── shared-references/           # Target parent directory
│   ├── package-*.md files
│   └── (no scripts/ folder yet)
└── dev-scripts/                 # Stays separate (maintenance tools)
    ├── localize-shared-files.sh
    ├── rename-and-update.py
    ├── replace-text.py
    └── verify-references.py
```

### After Localization (Current Behavior)

The `localize-shared-files.sh` script currently copies:
```
tidymodels/add-yardstick-metric/references/
├── scripts/                     # Created during localization
│   ├── clone-tidymodels-repos.ps1
│   ├── clone-tidymodels-repos.py
│   ├── clone-tidymodels-repos.sh
│   ├── README.md
│   └── verify-setup.R
└── [markdown files from shared-references/]
```

### Files That Reference shared-scripts

Need to find and update references:
- `tidymodels/shared-references/package-repository-access.md` (likely main reference)
- Any SKILL.md files that mention the scripts
- The localize-shared-files.sh script itself
- Possibly README files or documentation
- GitHub workflows (if any)

---

## Proposed Structure

### New Directory Layout

```
tidymodels/
├── shared-references/
│   ├── scripts/                 # NEW LOCATION
│   │   ├── clone-tidymodels-repos.ps1
│   │   ├── clone-tidymodels-repos.py
│   │   ├── clone-tidymodels-repos.sh
│   │   ├── README.md
│   │   └── verify-setup.R
│   └── package-*.md files
└── dev-scripts/                 # Unchanged (maintenance tools)
    └── [development scripts]
```

### Updated Localization Behavior

After update, localization will mirror the source structure:
```
tidymodels/add-yardstick-metric/references/
├── scripts/                     # Same structure as source
│   ├── clone-tidymodels-repos.ps1
│   ├── clone-tidymodels-repos.py
│   ├── clone-tidymodels-repos.sh
│   ├── README.md
│   └── verify-setup.R
└── [markdown files]
```

---

## Migration Strategy

### Phase 1: Pre-Flight Checks

1. **Run baseline verification**
   ```bash
   python3 tidymodels/dev-scripts/verify-references.py
   ```

2. **Find all references to shared-scripts**
   ```bash
   grep -r "shared-scripts" tidymodels/ --include=*.md --include=*.sh
   ```

3. **Document current references** for update plan

### Phase 2: Move Files

1. **Create target directory**
   ```bash
   mkdir -p tidymodels/shared-references/scripts
   ```

2. **Move all files**
   ```bash
   mv tidymodels/shared-scripts/* tidymodels/shared-references/scripts/
   ```

3. **Remove empty directory**
   ```bash
   rmdir tidymodels/shared-scripts
   ```

### Phase 3: Update References

**IMPORTANT: Use `replace-text.py` from dev-scripts instead of manual sed/find-replace**

The dev-scripts provide:
- Safety with `--dry-run` mode
- Consistency across updates
- Already pre-authorized in settings.local.json

#### Script References to Update

1. **Update localize-shared-files.sh**
   - Location: `tidymodels/dev-scripts/localize-shared-files.sh`
   - Change: Update path from `shared-scripts/` to `shared-references/scripts/`
   - Tool: Direct edit (it's a script file, not markdown)

2. **Update markdown documentation**
   ```bash
   # Pattern 1: Path references in markdown links
   python3 tidymodels/dev-scripts/replace-text.py \
     tidymodels/shared-references/package-repository-access.md \
     "tidymodels/shared-scripts/" \
     "tidymodels/shared-references/scripts/" \
     --dry-run

   # Review, then apply
   python3 tidymodels/dev-scripts/replace-text.py \
     tidymodels/shared-references/package-repository-access.md \
     "tidymodels/shared-scripts/" \
     "tidymodels/shared-references/scripts/"
   ```

3. **Update script README if it references its own path**
   ```bash
   python3 tidymodels/dev-scripts/replace-text.py \
     tidymodels/shared-references/scripts/README.md \
     "./tidymodels/shared-scripts/" \
     "./tidymodels/shared-references/scripts/" \
     --dry-run
   ```

4. **Update any skill files that reference the path**
   ```bash
   # If add-yardstick-metric/SKILL.md references shared-scripts
   python3 tidymodels/dev-scripts/replace-text.py \
     tidymodels/add-yardstick-metric/SKILL.md \
     "shared-scripts" \
     "shared-references/scripts" \
     --dry-run
   ```

### Phase 4: Update Localization Script

**Edit: tidymodels/dev-scripts/localize-shared-files.sh**

Current logic:
```bash
# Copy shared-scripts to references/scripts/
echo "  Copying shared-scripts/* → $SCRIPTS_DIR/"
cp -v shared-scripts/* "$SCRIPTS_DIR/"
```

Updated logic:
```bash
# Copy shared-references/scripts to references/scripts/
echo "  Copying shared-references/scripts/* → $SCRIPTS_DIR/"
cp -v shared-references/scripts/* "$SCRIPTS_DIR/"
```

### Phase 5: Re-Localize and Verify

1. **Run updated localization script**
   ```bash
   bash tidymodels/dev-scripts/localize-shared-files.sh
   ```

2. **Verify files copied correctly**
   ```bash
   ls -la tidymodels/add-yardstick-metric/references/scripts/
   ls -la tidymodels/add-recipe-step/references/scripts/
   ```

3. **Run reference verification**
   ```bash
   python3 tidymodels/dev-scripts/verify-references.py
   ```

4. **Check git status**
   ```bash
   git status
   ```

---

## Tools and Methodology

### Script-First Approach

**CRITICAL: Always use dev-scripts tools instead of manual commands**

✅ **DO USE:**
- `python3 tidymodels/dev-scripts/replace-text.py` for updating text references
- `python3 tidymodels/dev-scripts/verify-references.py` for checking links
- `bash tidymodels/dev-scripts/localize-shared-files.sh` for localization
- `mv` for moving files (when necessary)

❌ **DO NOT USE:**
- `sed` or `awk` for text replacement (use `replace-text.py` instead)
- `grep -r` then manual edits (use `replace-text.py` for batch updates)
- Manual file copying (use `localize-shared-files.sh` instead)

### Why Use Scripts Over Manual Commands?

1. **Safety**: Scripts have `--dry-run` modes to preview changes
2. **Consistency**: Same operation produces same results every time
3. **Pre-authorization**: Scripts are already approved in settings.local.json
4. **Auditability**: Script output shows exactly what changed
5. **Efficiency**: Batch operations handle multiple files at once

### Pre-Authorized Commands

From `.claude/settings.local.json`, these commands are already approved:

```json
"Bash(python3:*)",                   // Run Python scripts
"Bash(chmod:*)",                     // Make scripts executable
"Bash(ls:*)",                        // List files
"Bash(find:*)",                      // Find files
"Bash(./dev-scripts/verify-references.py)",
"Bash(./dev-scripts/replace-text.py)",
"Bash(./dev-scripts/localize-shared-files.sh)",
"Bash(bash tidymodels/dev-scripts/localize-shared-files.sh)",
"Bash(grep -r:*)"                    // Search in files
```

### Commands That May Need Pre-Authorization

If the plan requires any of these patterns, request pre-authorization:

```json
"Bash(mkdir -p tidymodels/shared-references/scripts)",
"Bash(rmdir tidymodels/shared-scripts)",
"Bash(mv tidymodels/shared-scripts/* tidymodels/shared-references/scripts/)"
```

---

## Reference Update Patterns

### Common Path Patterns to Replace

1. **Absolute path references**
   ```
   OLD: ./tidymodels/shared-scripts/clone-tidymodels-repos.sh
   NEW: ./tidymodels/shared-references/scripts/clone-tidymodels-repos.sh
   ```

2. **Relative path from skill directory**
   ```
   OLD: ../shared-scripts/verify-setup.R
   NEW: ../shared-references/scripts/verify-setup.R
   ```

3. **Path in documentation**
   ```
   OLD: See scripts in `shared-scripts/`
   NEW: See scripts in `shared-references/scripts/`
   ```

4. **Command examples in README**
   ```
   OLD: ./tidymodels/shared-scripts/clone-tidymodels-repos.sh yardstick
   NEW: ./tidymodels/shared-references/scripts/clone-tidymodels-repos.sh yardstick
   ```

### Batch Update Strategy

```bash
# Step 1: Update shared-references documentation
for file in tidymodels/shared-references/*.md; do
  python3 tidymodels/dev-scripts/replace-text.py "$file" \
    "shared-scripts" \
    "shared-references/scripts" \
    --dry-run
done

# Review output, then run without --dry-run

# Step 2: Update scripts README
python3 tidymodels/dev-scripts/replace-text.py \
  tidymodels/shared-references/scripts/README.md \
  "./tidymodels/shared-scripts/" \
  "./tidymodels/shared-references/scripts/"

# Step 3: Update skill documentation
for skill in add-yardstick-metric add-recipe-step; do
  for file in tidymodels/$skill/*.md; do
    python3 tidymodels/dev-scripts/replace-text.py "$file" \
      "shared-scripts" \
      "shared-references/scripts" \
      --dry-run
  done
done
```

---

## Impact Assessment

### Files Directly Modified

**Moved:**
- `tidymodels/shared-scripts/` → `tidymodels/shared-references/scripts/`
  - All 5 files (3 scripts, 1 README, 1 R script)

**Updated:**
- `tidymodels/dev-scripts/localize-shared-files.sh` (path update)
- `tidymodels/shared-references/package-repository-access.md` (likely)
- `tidymodels/shared-references/scripts/README.md` (if self-referential)
- Possibly skill SKILL.md files if they mention the path

**Re-localized (via script):**
- `tidymodels/add-yardstick-metric/references/scripts/` (all 5 files)
- `tidymodels/add-recipe-step/references/scripts/` (all 5 files)

### Files Verified (No Changes Expected)

- `tidymodels/dev-scripts/*` (maintenance scripts, separate concern)

### Benefits

✅ **Consistent structure** - Source mirrors localized layout
✅ **Logical grouping** - Scripts are reference materials
✅ **Simpler paths** - One less top-level folder
✅ **Clear separation** - dev-scripts vs reference scripts
✅ **Better organization** - All reference materials under one parent

### Risks

⚠️ **Broken references** - Documentation may reference old path
   - Mitigation: Use replace-text.py + verify-references.py

⚠️ **Script execution paths** - Users' shell history or scripts may break
   - Mitigation: Update README with migration note

⚠️ **Cached paths** - Users with cloned repos may have old paths
   - Mitigation: Document in README or release notes

---

## Implementation Steps

### Step 1: Preparation
- [ ] Run `verify-references.py` to establish baseline
- [ ] Search for all references to `shared-scripts`
- [ ] Document what needs updating

### Step 2: Move Files
- [ ] Create target directory: `mkdir -p tidymodels/shared-references/scripts`
- [ ] Move files: `mv tidymodels/shared-scripts/* tidymodels/shared-references/scripts/`
- [ ] Remove empty directory: `rmdir tidymodels/shared-scripts`
- [ ] Verify move: `ls -la tidymodels/shared-references/scripts/`

### Step 3: Update localize-shared-files.sh
- [ ] Edit `tidymodels/dev-scripts/localize-shared-files.sh`
- [ ] Change `shared-scripts/*` to `shared-references/scripts/*`
- [ ] Save and verify syntax

### Step 4: Update References
- [ ] Update `package-repository-access.md` using replace-text.py
- [ ] Update `scripts/README.md` using replace-text.py
- [ ] Update any skill documentation using replace-text.py
- [ ] Run replace-text.py with --dry-run first, then apply

### Step 5: Re-Localize
- [ ] Run: `bash tidymodels/dev-scripts/localize-shared-files.sh`
- [ ] Verify scripts copied to both skills: `ls -la tidymodels/*/references/scripts/`
- [ ] Check file contents match source

### Step 6: Validation
- [ ] Run: `python3 tidymodels/dev-scripts/verify-references.py` (must show 0 errors)
- [ ] Test a script path manually to ensure it works
- [ ] Verify all files moved successfully: `ls -la tidymodels/shared-references/scripts/`
- [ ] Confirm old directory removed: `ls tidymodels/shared-scripts` should fail

---

## Success Criteria

✅ **All files moved** to `tidymodels/shared-references/scripts/`
✅ **No broken references** - verify-references.py reports 0 errors
✅ **Localization works** - scripts copy correctly to skills
✅ **Scripts executable** - permissions preserved through move
✅ **Documentation updated** - all references point to new location
✅ **Tools used correctly** - replace-text.py used for updates (not sed/awk)

---

## Timeline Estimate

- **Step 1 (Preparation):** 10 minutes - Baseline and search
- **Step 2 (Move Files):** 5 minutes - Move commands
- **Step 3 (Update Script):** 5 minutes - Edit localize-shared-files.sh
- **Step 4 (Update References):** 15 minutes - Run replace-text.py on files
- **Step 5 (Re-Localize):** 5 minutes - Run localization script
- **Step 6 (Validation):** 10 minutes - Verify and test

**Total estimated time:** 50 minutes

---

## Rollback Plan

If issues arise:

1. **Move files back**: `mv tidymodels/shared-references/scripts/* tidymodels/shared-scripts/`
2. **Recreate directory if needed**: `mkdir -p tidymodels/shared-scripts`
3. **Restore localize-shared-files.sh** to original version
4. **Re-run localization**: `bash tidymodels/dev-scripts/localize-shared-files.sh`
5. **Verify references**: `python3 tidymodels/dev-scripts/verify-references.py`
6. **Document lessons learned**

---

## Next Steps

**After approval of this plan:**

1. Confirm all necessary commands are pre-authorized
2. Add any needed wildcards to settings.local.json
3. Begin Step 1: Preparation and baseline
4. Execute steps 2-6 sequentially
5. Validate completion

**Approval needed from:** Repository maintainer
**Expected start date:** After plan review and settings update

---

## Notes

- This is a relatively straightforward move operation
- Main risk is broken references, mitigated by verify-references.py
- Using git mv preserves history, making this safe to revert
- Scripts in dev-scripts/ are separate and should not be affected
- The localized copies in skills will be regenerated correctly
