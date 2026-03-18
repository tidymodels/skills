# Phase 1 Assessment: Source Package Development Support

**Date:** 2026-03-18
**Status:** Assessment Complete
**Next Phase:** Planning (Phase 2)

## Executive Summary

The current `add-yardstick-metric` and `add-recipe-step` skills are well-structured for **extension development** (creating new packages). Converting them to support **source package development** (contributing to yardstick/recipes directly) requires **moderate changes** focused on three areas:

1. **Guidance on internal functions** (currently avoided, but needed for source development)
2. **Documentation standards** (needs to match existing package style exactly)
3. **Testing patterns** (needs to align with package-specific conventions)

**Key Finding:** Most reference files can remain largely unchanged due to their thematic organization. The main changes are in the primary SKILL.md files and testing guidance.

---

## Current State Analysis

### add-yardstick-metric Skill

**Current Focus:** Creating metrics in external packages that extend yardstick

**Structure:**
```
tidymodels/skills/add-yardstick-metric/
├── SKILL.md (686 lines)
├── references/
│   ├── metric-system.md
│   ├── numeric-metrics.md
│   ├── class-metrics.md
│   ├── probability-metrics.md
│   ├── ordered-probability-metrics.md
│   ├── static-survival-metrics.md
│   ├── dynamic-survival-metrics.md
│   ├── integrated-survival-metrics.md
│   ├── linear-predictor-survival-metrics.md
│   ├── quantile-metrics.md
│   ├── confusion-matrix.md
│   ├── case-weights.md
│   ├── autoplot.md
│   ├── metric-set.md
│   └── groupwise-metrics.md
└── Shared references (8 files)
```

**Key Characteristics:**
- Emphasizes avoiding internal functions
- Shows package setup with `usethis::create_package()`
- Examples use clean, self-contained implementations
- Testing uses simple, constructed test data
- Documentation follows roxygen2 standards

### add-recipe-step Skill

**Current Focus:** Creating steps in external packages that extend recipes

**Structure:**
```
tidymodels/skills/add-recipe-step/
├── SKILL.md (666 lines)
├── references/
│   ├── step-architecture.md
│   ├── modify-in-place-steps.md
│   ├── create-new-columns-steps.md
│   ├── row-operation-steps.md
│   ├── optional-methods.md
│   └── helper-functions.md
└── Shared references (8 files)
```

**Key Characteristics:**
- Emphasizes avoiding internal functions
- Shows the three-function pattern clearly
- Examples use recipes exported helpers only
- Testing uses standard datasets (mtcars, iris)
- Documentation follows recipes conventions

---

## What Needs to Change

### 1. Internal Function Usage

**Current Approach:** Explicitly avoid internal functions
- SKILL.md states to use only exported functions
- Examples show alternatives to internal helpers
- Testing avoids package internals

**Required Changes for Source Development:**
- ✅ **Acknowledge internal functions exist and when to use them**
- ✅ **Show examples accessing internals with :::**
- ✅ **Explain when internals are appropriate vs. creating new helpers**
- ✅ **Warn about stability (internals can change)**

**Example Change Needed:**
```r
# Extension development (current)
if (is.null(case_weights)) {
  mean(values)
} else {
  weighted.mean(values, w = as.double(case_weights))
}

# Source development (new)
# Can use internal helpers when they exist
yardstick:::yardstick_mean(values, case_weights = case_weights)
```

**Impact Level:** 🟡 MODERATE
- Main SKILL.md: Add new section "Working with Internal Functions"
- Reference files: Minimal changes (most are thematic)
- Testing guide: Add section on testing with internals

### 2. Documentation Standards

**Current Approach:** General roxygen2 guidance suitable for any package

**Required Changes for Source Development:**
- ✅ **Must match existing package documentation exactly**
- ✅ **Specific template requirements** (e.g., yardstick uses `@templateVar`, `@template`)
- ✅ **Package-specific roxygen tags and conventions**
- ✅ **Consistent @family tags with existing metrics/steps**
- ✅ **More extensive @examples sections**

**Impact Level:** 🟡 MODERATE
- Main SKILL.md: Update documentation section
- roxygen-documentation.md: Add source-specific patterns
- Examples need to reference existing package patterns more

### 3. Testing Patterns

**Current Approach:**
- Create simple test data from scratch
- Explicitly avoid internal test helpers
- Basic testthat patterns

**Required Changes for Source Development:**
- ✅ **CAN use internal test helpers** (they're part of the package)
- ✅ **Must match existing test file structure**
- ✅ **Need snapshot testing where package uses it**
- ✅ **More extensive edge case coverage to match package standards**

**Example Change:**
```r
# Extension development (current)
test_data <- data.frame(
  truth = c(1, 2, 3, 4, 5),
  estimate = c(1.1, 2.2, 2.9, 4.1, 4.8)
)

# Source development (new) - CAN use internal helpers
test_data <- yardstick:::data_altman()  # OK when developing yardstick itself
```

**Impact Level:** 🟡 MODERATE
- testing-patterns.md: Add section distinguishing extension vs. source testing
- Main SKILL.md: Update testing examples

### 4. Package Setup Section

**Current Approach:**
- Shows full package initialization with `usethis::create_package()`
- Focuses on creating new packages
- Emphasizes package structure

**Required Changes for Source Development:**
- ✅ **Clone existing repository instead**
- ✅ **Navigate to correct directory (R/, tests/, man/)**
- ✅ **Understand existing package architecture**
- ✅ **Work within existing structure, not create new**
- ✅ **Branch strategy for PRs**

**Impact Level:** 🟢 MINOR
- Main SKILL.md: Replace "Prerequisites" section
- repository-access.md: Already exists and covers this

### 5. Development Workflow

**Current Approach:**
- Standard devtools workflow
- Focus on iterative development
- Run check() before publishing

**Required Changes for Source Development:**
- ✅ **Add git workflow** (branch, commit, PR process)
- ✅ **Run package-specific checks** (some packages have custom checks)
- ✅ **Integration testing with rest of package**
- ✅ **Code review expectations**

**Impact Level:** 🟢 MINOR
- development-workflow.md: Add git/PR workflow section
- Main SKILL.md: Reference PR process

---

## Reference Files Assessment

### Reference Files Requiring Changes

#### MINIMAL CHANGES (thematic content remains valid):
- ✅ **metric-system.md** - Architecture is the same
- ✅ **numeric-metrics.md** - Pattern is the same
- ✅ **class-metrics.md** - Pattern is the same
- ✅ **probability-metrics.md** - Pattern is the same
- ✅ **All other metric type references** - Patterns unchanged
- ✅ **step-architecture.md** - Core architecture unchanged
- ✅ **modify-in-place-steps.md** - Pattern unchanged
- ✅ **create-new-columns-steps.md** - Pattern unchanged
- ✅ **row-operation-steps.md** - Pattern unchanged

**Changes Needed:** Minor notes about when internals are used in source

#### MODERATE CHANGES:
- 🟡 **testing-patterns.md** - Add source vs. extension distinction
- 🟡 **best-practices.md** - Add notes about internal function usage
- 🟡 **troubleshooting.md** - Update import/namespace guidance

#### NO CHANGES NEEDED:
- ✅ **r-package-setup.md** - Still useful for understanding package structure
- ✅ **development-workflow.md** - Core workflow same (minor additions)
- ✅ **package-imports.md** - Same namespace principles apply
- ✅ **roxygen-documentation.md** - Core principles same (examples need updating)
- ✅ **repository-access.md** - Already exists and handles cloning

---

## Shared Scripts Assessment

**Current Scripts:**
```
tidymodels/skills/shared-scripts/
├── README.md
├── clone-tidymodels-repos.sh
├── clone-tidymodels-repos.ps1
└── clone-tidymodels-repos.py
```

**Assessment:** ✅ NO CHANGES NEEDED
- Scripts already support cloning source repositories
- Work for both extension and source development
- Well-documented and cross-platform

---

## Quantitative Impact Assessment

### add-yardstick-metric Skill

| Component | Lines | Change Level | Estimated New Lines |
|-----------|-------|--------------|---------------------|
| SKILL.md | 686 | 🟡 MODERATE | ~800 (+114) |
| references/*.md (14 files) | ~3500 | 🟢 MINOR | ~3650 (+150) |
| shared-references/*.md (8 files) | ~2000 | 🟡 MODERATE | ~2200 (+200) |
| **Total** | **~6186** | | **~6650 (+464, ~7.5%)** |

**Primary Changes:**
1. New section in SKILL.md: "Source vs. Extension Development" (~100 lines)
2. Updated testing guidance (~50 lines)
3. Internal function usage examples (~50 lines)
4. Documentation pattern updates (~50 lines)
5. Minor additions across reference files (~214 lines)

### add-recipe-step Skill

| Component | Lines | Change Level | Estimated New Lines |
|-----------|-------|--------------|---------------------|
| SKILL.md | 666 | 🟡 MODERATE | ~780 (+114) |
| references/*.md (6 files) | ~1800 | 🟢 MINOR | ~1900 (+100) |
| shared-references/*.md (8 files) | ~2000 | 🟡 MODERATE | ~2200 (+200) |
| **Total** | **~4466** | | **~4880 (+414, ~9.3%)** |

**Primary Changes:** Similar to yardstick metric skill

---

## Architecture Decision: Three-Skill Split

### Proposed Structure

```
tidymodels/skills/
├── add-yardstick-metric/          # Main skill (chooses variant)
│   ├── SKILL.md                    # Decision point + common guidance
│   └── references/                 # Thematic references (mostly unchanged)
│
├── add-yardstick-metric-extension/ # Extension development variant
│   ├── SKILL.md                    # Extension-specific guidance
│   └── examples/                   # Extension examples
│
├── add-yardstick-metric-source/   # Source development variant
│   ├── SKILL.md                    # Source-specific guidance
│   └── examples/                   # Source examples
│
├── add-recipe-step/               # Main skill (chooses variant)
│   ├── SKILL.md                    # Decision point + common guidance
│   └── references/                 # Thematic references (mostly unchanged)
│
├── add-recipe-step-extension/     # Extension development variant
│   ├── SKILL.md                    # Extension-specific guidance
│   └── examples/                   # Extension examples
│
├── add-recipe-step-source/        # Source development variant
│   ├── SKILL.md                    # Source-specific guidance
│   └── examples/                   # Source examples
│
└── shared-references/             # Common to all (minor updates)
    └── *.md
```

### Alternative: Two-Skill Structure

```
tidymodels/skills/
├── add-yardstick-metric/          # Combined skill with sections
│   ├── SKILL.md                    # Has both extension and source guidance
│   ├── references/
│   ├── extension-guide.md          # Extension-specific deep dive
│   └── source-guide.md             # Source-specific deep dive
│
└── add-recipe-step/               # Combined skill with sections
    ├── SKILL.md
    ├── references/
    ├── extension-guide.md
    └── source-guide.md
```

### Recommendation: **Two-Skill Structure**

**Rationale:**
1. ✅ **Simpler to maintain** - Less duplication
2. ✅ **Most content is common** - Patterns are the same, just context differs
3. ✅ **Clear decision point** - User makes choice early in SKILL.md
4. ✅ **Shared references work naturally** - No need to duplicate
5. ✅ **Easier navigation** - Don't have to switch between skills

**Implementation:**
```markdown
# Add Yardstick Metric

## Choose Your Development Path

**Are you:**
- 🔹 **Creating a new package** that extends yardstick? → Follow Extension Development
- 🔹 **Contributing to yardstick itself** via PR? → Follow Source Development

[Rest of skill is common, with sections marked "Extension Development" or "Source Development" where they differ]
```

---

## Risk Assessment

### LOW RISK ✅
- **Thematic reference files remain valid** - Core patterns don't change
- **Shared scripts work for both** - No changes needed
- **Architecture is the same** - Just different context

### MEDIUM RISK 🟡
- **Testing guidance needs clarity** - Must clearly distinguish when to use internals
- **Documentation examples** - Need to show package-specific patterns
- **User confusion** - Need clear decision point early

### MITIGATION STRATEGIES
1. ✅ **Clear decision tree at start** - Help users choose right path
2. ✅ **Explicit callouts** - Mark sections as extension vs. source specific
3. ✅ **Examples for both** - Show same metric/step in both contexts
4. ✅ **Troubleshooting section** - Address common confusion points

---

## Timeline Estimate

### Phase 2: Planning (Next)
- **Duration:** 2-3 hours
- **Deliverables:**
  - Detailed plan document
  - Implementation checklist
  - Example migration (one metric, one step)

### Implementation: Yardstick Skill
- **Duration:** 4-6 hours
- **Tasks:**
  - Update SKILL.md with decision point
  - Add source development guidance
  - Update testing-patterns.md
  - Update best-practices.md
  - Create extension-guide.md
  - Create source-guide.md
  - Test with example metric

### Implementation: Recipe Skill
- **Duration:** 4-6 hours
- **Tasks:** Same as yardstick skill
- **Note:** Can reuse patterns from yardstick implementation

### Total Estimated Time: 10-15 hours

---

## Recommendations

### Immediate Next Steps (Phase 2)

1. ✅ **Create detailed plan document** with:
   - Exact sections to modify in each file
   - Decision tree for choosing development path
   - Example implementations (one metric, one step) in both contexts
   - Testing strategy

2. ✅ **Create implementation checklist** for tracking progress

3. ✅ **Start with yardstick skill** (recipes can follow same pattern)

### Key Success Criteria

- ✅ Clear distinction between extension and source development
- ✅ Users can easily choose the right path
- ✅ Reference files remain useful for both contexts
- ✅ Examples show both approaches where they differ
- ✅ Testing guidance is clear about when internals are appropriate

### Open Questions for Phase 2

1. Should we show side-by-side comparisons of extension vs. source code?
2. How detailed should git/PR workflow guidance be?
3. Should we create template PRs for contributions?
4. Do we need package-specific guides (yardstick has different conventions than recipes)?

---

## Conclusion

**Assessment Result:** ✅ FEASIBLE with MODERATE effort

The skills are well-structured with thematic references that largely transcend the extension vs. source distinction. The main changes are:

1. **Adding context** about when to use internal functions
2. **Updating testing guidance** to distinguish extension vs. source patterns
3. **Providing clear decision points** for users to choose their path
4. **Adding git/PR workflow** for source contributions

**Most reference files (80%) can remain unchanged** because they describe patterns that work in both contexts. The architecture, metric types, step types, and core concepts are identical whether developing in an extension package or contributing to the source.

**Confidence Level:** HIGH - The proposed two-skill structure with decision points is the right approach and can be implemented within the estimated timeline.

## Edgar's feedback

We should go with the "Two-Skill Structure" for sure

### Implementation thoughts

You have:
```markdown
# Add Yardstick Metric

## Choose Your Development Path

**Are you:**
- 🔹 **Creating a new package** that extends yardstick? → Follow Extension Development
- 🔹 **Contributing to yardstick itself** via PR? → Follow Source Development

[Rest of skill is common, with sections marked "Extension Development" or "Source Development" where they differ]
```

I would say to follow this logic: 
1. Check to see if it's already in a folder that contains the source code of the package ('yardstick' or 'recipes'), and if it does, to automatically assume that this is an internal function
2. If on a different package, assume extension
3. If in a non-package project (the folder has content already but is not a package), assume extension
4. Empty folder, ask


### "MODERATE CHANGES" thoughts
You have this:
- 🟡 **testing-patterns.md** - Add source vs. extension distinction
- 🟡 **best-practices.md** - Add notes about internal function usage
- 🟡 **troubleshooting.md** - Update import/namespace guidance

Can we just split them in two files, one for extensions and one for internal? In this case we would end up with 6 files, but each one will be clear on intent

### Open Questions for Phase 2

1. Should we show side-by-side comparisons of extension vs. source code? [er] Do not think so, the process should be pretty seamless for the end-user
2. How detailed should git/PR workflow guidance be? [er] I would say minimal, that is low priority. I think Tidymodels developers will be the ones mostly using this new feature, so no git guidance will be necessary
3. Should we create template PRs for contributions? [er] Not at this time
4. Do we need package-specific guides (yardstick has different conventions than recipes)? [er] Absolutely, each package will have nuanced requirements 

