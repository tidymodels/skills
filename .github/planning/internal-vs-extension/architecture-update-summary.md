# Architecture Update Summary

**Date:** 2026-03-18
**Update:** Improved file structure based on feedback

## Key Change

**Original Plan:** Split shared-references files into both extension and source versions (6 total files in shared-references)

**Updated Plan:**
- Extension files stay in shared-references (universal guidance)
- Source files go in each skill directory (package-specific guidance)

## Rationale

✅ **Extension guidance is universal** - Same patterns whether extending yardstick or recipes
✅ **Source guidance is package-specific** - Yardstick and recipes have different internals, conventions, testing styles
✅ **Cleaner organization** - Package-specific files live with the package skill
✅ **Easier maintenance** - Update yardstick-specific patterns in yardstick skill directory

---

## Updated File Structure

```
tidymodels/skills/
├── add-yardstick-metric/
│   ├── SKILL.md
│   ├── extension-guide.md (NEW)
│   ├── source-guide.md (NEW)
│   ├── testing-patterns-source.md (NEW - yardstick-specific)
│   ├── best-practices-source.md (NEW - yardstick-specific)
│   ├── troubleshooting-source.md (NEW - yardstick-specific)
│   └── references/ (existing)
│
├── add-recipe-step/
│   ├── SKILL.md
│   ├── extension-guide.md (NEW)
│   ├── source-guide.md (NEW)
│   ├── testing-patterns-source.md (NEW - recipes-specific)
│   ├── best-practices-source.md (NEW - recipes-specific)
│   ├── troubleshooting-source.md (NEW - recipes-specific)
│   └── references/ (existing)
│
└── shared-references/
    ├── testing-patterns-extension.md (RENAME from testing-patterns.md)
    ├── best-practices-extension.md (RENAME from best-practices.md)
    ├── troubleshooting-extension.md (RENAME from troubleshooting.md)
    ├── r-package-setup.md (unchanged)
    ├── development-workflow.md (minor updates)
    ├── roxygen-documentation.md (unchanged)
    ├── package-imports.md (unchanged)
    └── repository-access.md (unchanged)
```

---

## Files to Create

**Total: 10 new files**

### Yardstick Skill (6 files)
1. `add-yardstick-metric/extension-guide.md` - Extension development guide
2. `add-yardstick-metric/source-guide.md` - Source development guide
3. `add-yardstick-metric/testing-patterns-source.md` - Yardstick testing patterns
4. `add-yardstick-metric/best-practices-source.md` - Yardstick best practices
5. `add-yardstick-metric/troubleshooting-source.md` - Yardstick troubleshooting

### Recipes Skill (6 files)
6. `add-recipe-step/extension-guide.md` - Extension development guide
7. `add-recipe-step/source-guide.md` - Source development guide
8. `add-recipe-step/testing-patterns-source.md` - Recipes testing patterns
9. `add-recipe-step/best-practices-source.md` - Recipes best practices
10. `add-recipe-step/troubleshooting-source.md` - Recipes troubleshooting

---

## Files to Rename

**Total: 3 renames in shared-references/**

1. `testing-patterns.md` → `testing-patterns-extension.md`
2. `best-practices.md` → `best-practices-extension.md`
3. `troubleshooting.md` → `troubleshooting-extension.md`

---

## Files to Modify

**Total: 2 main files + cross-references**

1. `add-yardstick-metric/SKILL.md` - Add auto-detection, link to guides
2. `add-recipe-step/SKILL.md` - Add auto-detection, link to guides
3. `shared-references/development-workflow.md` - Add minimal git guidance
4. Update cross-references in other shared-references files

---

## Updated Stages

### Stage 1: Rename Extension Reference Files (15 minutes)
- Rename 3 files in shared-references with -extension suffix
- Update cross-references

### Stage 2: Create Package-Specific Source Files (4-5 hours)
- Create 3 source files for yardstick (testing, best-practices, troubleshooting)
- Create 3 source files for recipes (testing, best-practices, troubleshooting)
- Package-specific nuances captured in each

### Stage 3: Create Extension/Source Guides (4-5 hours)
- Create 2 guides for yardstick (extension, source)
- Create 2 guides for recipes (extension, source)

### Stage 4: Update Main SKILL.md Files (3-4 hours)
- Add auto-detection to both skills
- Link to appropriate guides

### Stage 5: Update Shared References (1-2 hours)
- Add git workflow guidance
- Update cross-references

### Stage 6: Minor Updates to Existing References (1-2 hours)
- Add minimal notes about internals where relevant

---

## Benefits of New Structure

### 1. Clear Separation of Concerns
- **Extension guidance**: Universal, in shared-references
- **Source guidance**: Package-specific, in skill directories

### 2. No Duplication
- Extension developers use same files regardless of package
- Source developers get package-specific guidance

### 3. Easier Navigation
- Extension: shared-references/[topic]-extension.md
- Source (yardstick): add-yardstick-metric/[topic]-source.md
- Source (recipes): add-recipe-step/[topic]-source.md

### 4. Package Expertise Captured
- Yardstick internals documented with yardstick skill
- Recipes internals documented with recipes skill
- Each can evolve independently

### 5. Maintenance Simplicity
- Update yardstick patterns → change yardstick files only
- Update recipes patterns → change recipes files only
- Update universal patterns → change shared-references only

---

## Cross-Reference Patterns

### Extension Development
```markdown
# In extension-guide.md
→ See [Testing Patterns](../shared-references/testing-patterns-extension.md)
→ See [Best Practices](../shared-references/best-practices-extension.md)
→ See [Troubleshooting](../shared-references/troubleshooting-extension.md)
```

### Source Development (Yardstick)
```markdown
# In add-yardstick-metric/source-guide.md
→ See [Testing Patterns](testing-patterns-source.md)
→ See [Best Practices](best-practices-source.md)
→ See [Troubleshooting](troubleshooting-source.md)
```

### Source Development (Recipes)
```markdown
# In add-recipe-step/source-guide.md
→ See [Testing Patterns](testing-patterns-source.md)
→ See [Best Practices](best-practices-source.md)
→ See [Troubleshooting](troubleshooting-source.md)
```

---

## Implementation Priority

1. **Stage 1** (15 min) - Quick wins, enables rest of work
2. **Stage 2** (4-5 hrs) - Critical for capturing package nuances
3. **Stage 3** (4-5 hrs) - Main user-facing guides
4. **Stage 4** (3-4 hrs) - Auto-detection and navigation
5. **Stage 5** (1-2 hrs) - Polish and references
6. **Stage 6** (1-2 hrs) - Minor enhancements

**Total Time: Still 10-15 hours**

---

## Updated Documents

All planning documents have been updated to reflect this new structure:

- [x] phase2-plan.md - Updated file structure, stages, timeline
- [x] phase2-checklist.md - Updated all checklists and stage numbers
- [x] phase2-examples.md - No changes needed (examples still valid)

---

## Next Steps

Ready to proceed with implementation following the updated plan!
