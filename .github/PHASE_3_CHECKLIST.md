# Phase 3 Implementation Checklist

**Goal**: Enhance skill references with specific file paths to cloned repositories, making them more useful for developers who have local clones.

## Overview

Phase 3 adds specific file path references throughout the skill documentation to bridge the gap between abstract patterns and real implementations. When users have cloned repositories locally (via Phase 1 scripts), they can navigate directly to canonical implementations.

**Guiding Principles**:
- Reference 2-4 canonical/representative examples per pattern
- Focus on simple, clear implementations (not edge cases)
- Avoid over-referencing (don't list every file)
- Use consistent path format: `R/filename.R`, `tests/testthat/test-name.R`
- Paths work for both local clones and GitHub references

## 1. Yardstick Skill Enhancement

### 1.1 Review SKILL.md for File Reference Opportunities
- [ ] Read through `tidymodels/skills/add-yardstick-metric/SKILL.md`
- [ ] Identify sections that reference "existing implementations" or "patterns"
- [ ] Add specific file paths to 2-3 canonical examples per section
- [ ] Focus on main workflow examples (not comprehensive lists)
- [ ] Verify paths exist in yardstick repository

**Example transformation:**
```markdown
# Before:
See existing numeric metric implementations for patterns.

# After:
See existing numeric metric implementations:
- `R/num-mae.R` - Simple error metric
- `R/num-rmse.R` - Root mean squared error
- `R/num-huber_loss.R` - Robust metric with tuning parameter
```

### 1.2 Update Numeric Metrics Reference
- [ ] File: `tidymodels/skills/add-yardstick-metric/references/numeric-metrics.md`
- [ ] Add 2-4 file paths to canonical implementations:
  - [ ] Simple metrics (MAE, RMSE, MSE)
  - [ ] Weighted metrics (Huber loss)
  - [ ] Complex metrics (CCC, IIC)
- [ ] Add test file references:
  - [ ] Basic test pattern example
  - [ ] Edge case handling example
- [ ] Avoid listing every numeric metric file
- [ ] Verify all paths exist in repos/yardstick/

### 1.3 Update Class Metrics Reference
- [ ] File: `tidymodels/skills/add-yardstick-metric/references/class-metrics.md`
- [ ] Add 2-4 file paths to canonical implementations:
  - [ ] Simple metrics (accuracy, precision, recall)
  - [ ] Multiclass handling examples
  - [ ] Confusion matrix based metrics
- [ ] Add test file references:
  - [ ] Binary classification tests
  - [ ] Multiclass tests
- [ ] Verify all paths exist

### 1.4 Update Probability Metrics Reference
- [ ] File: `tidymodels/skills/add-yardstick-metric/references/probability-metrics.md`
- [ ] Add 2-4 file paths to canonical implementations:
  - [ ] ROC AUC variants
  - [ ] Log loss
  - [ ] Brier score
- [ ] Add test file references
- [ ] Verify all paths exist

### 1.5 Update Other Metric Type References
- [ ] File: `references/ordered-probability-metrics.md`
  - [ ] Add 1-2 canonical examples (RPS)
- [ ] File: `references/static-survival-metrics.md`
  - [ ] Add 1-2 canonical examples (Concordance Index)
- [ ] File: `references/dynamic-survival-metrics.md`
  - [ ] Add 1-2 canonical examples (Brier Survival)
- [ ] File: `references/integrated-survival-metrics.md`
  - [ ] Add 1-2 canonical examples
- [ ] File: `references/linear-predictor-survival-metrics.md`
  - [ ] Add 1-2 canonical examples
- [ ] File: `references/quantile-metrics.md`
  - [ ] Add 1-2 canonical examples

### 1.6 Balance Reference Density
- [ ] Review all updated files for over-referencing
- [ ] Ensure focus is on representative examples, not comprehensive lists
- [ ] Verify consistency in path format across all files
- [ ] Check that references enhance rather than clutter documentation

## 2. Recipes Skill Enhancement

### 2.1 Review SKILL.md for File Reference Opportunities
- [ ] Read through `tidymodels/skills/add-recipe-step/SKILL.md`
- [ ] Identify sections that reference "existing steps" or "patterns"
- [ ] Add specific file paths to 2-3 canonical examples per section
- [ ] Focus on main workflow examples
- [ ] Verify paths exist in recipes repository

**Example transformation:**
```markdown
# Before:
Look at existing modify-in-place steps for the pattern.

# After:
Look at existing modify-in-place steps:
- `R/step_center.R` - Simple centering transformation
- `R/step_normalize.R` - Scaling with prep/bake pattern
- `R/step_log.R` - Transformation with parameter tuning
```

### 2.2 Update Modify-in-Place Steps Reference
- [ ] File: `tidymodels/skills/add-recipe-step/references/modify-in-place-steps.md`
- [ ] Add 2-4 file paths to canonical implementations:
  - [ ] Simple transformations (center, scale, normalize)
  - [ ] Parameterized transformations (log, Box-Cox)
  - [ ] Multi-column operations
- [ ] Add test file references:
  - [ ] Basic prep/bake tests
  - [ ] Edge case handling
- [ ] Verify all paths exist in repos/recipes/

### 2.3 Update Create-New-Columns Steps Reference
- [ ] File: `tidymodels/skills/add-recipe-step/references/create-new-columns-steps.md`
- [ ] Add 2-4 file paths to canonical implementations:
  - [ ] Dummy variables (step_dummy)
  - [ ] Interactions (step_interact)
  - [ ] Feature engineering examples
- [ ] Add test file references
- [ ] Verify all paths exist

### 2.4 Update Row-Operation Steps Reference
- [ ] File: `tidymodels/skills/add-recipe-step/references/row-operation-steps.md`
- [ ] Add 2-4 file paths to canonical implementations:
  - [ ] Filtering steps
  - [ ] Row removal patterns
  - [ ] Sampling operations
- [ ] Add test file references
- [ ] Verify all paths exist

### 2.5 Update Step Architecture Reference
- [ ] File: `tidymodels/skills/add-recipe-step/references/step-architecture.md`
- [ ] Add references to canonical examples showing:
  - [ ] Three-function pattern (constructor, prep, bake)
  - [ ] Step class definition
  - [ ] Required methods implementation
- [ ] Keep focus on architecture, not specific use cases
- [ ] Verify all paths exist

### 2.6 Balance Reference Density
- [ ] Review all updated files for over-referencing
- [ ] Ensure focus is on representative examples
- [ ] Verify consistency in path format across all files
- [ ] Check that references enhance documentation

## 3. Reference Format Guidelines

### 3.1 Path Format Standards
- [ ] Always use relative paths from package root:
  - ✅ `R/num-mae.R`
  - ✅ `tests/testthat/test-num-mae.R`
  - ❌ `repos/yardstick/R/num-mae.R` (too specific)
  - ❌ `/absolute/path/to/R/num-mae.R` (not portable)
- [ ] Use code formatting: `` `R/file.R` ``
- [ ] Group related references with bullet points

### 3.2 Reference Density Guidelines
- [ ] Overview sections: 1-2 references to key architectural files
- [ ] Pattern introductions: 2-4 references to canonical examples
- [ ] Detailed examples: 3-5 references to similar implementations
- [ ] Testing sections: 2-3 references to test patterns
- [ ] Avoid comprehensive lists of every possible file

### 3.3 Example Quality Standards
**Good referencing:**
```markdown
**Core numeric metric patterns:**
- Simple metrics: `R/num-mae.R`, `R/num-rmse.R`
- Weighted metrics: `R/num-huber_loss.R`
- Complex metrics: `R/num-ccc.R` (correlation-based)

**Test patterns:**
- Basic: `tests/testthat/test-num-mae.R`
- Edge cases: `tests/testthat/test-num-huber_loss.R`
```

**Bad referencing (too much):**
```markdown
❌ See: R/num-mae.R, R/num-rmse.R, R/num-mse.R, R/num-mape.R,
R/num-mpe.R, R/num-smape.R, R/num-huber_loss.R, R/num-ccc.R,
R/num-iic.R, R/num-rpd.R, R/num-rpiq.R, ...
```

## 4. Validation

### 4.1 Path Verification
- [ ] Clone yardstick repository to verify all paths exist:
  ```bash
  cd /tmp
  git clone --depth 1 https://github.com/tidymodels/yardstick.git
  ```
- [ ] Clone recipes repository to verify all paths exist:
  ```bash
  cd /tmp
  git clone --depth 1 https://github.com/tidymodels/recipes.git
  ```
- [ ] Check each referenced file path exists
- [ ] Document any paths that need updating

### 4.2 Documentation Quality Check
- [ ] References enhance understanding (not just clutter)
- [ ] Paths work for both local clones and GitHub viewing
- [ ] Examples chosen are truly representative/canonical
- [ ] Balance maintained between detail and brevity
- [ ] Consistent formatting across all files

### 4.3 User Experience Validation
- [ ] References are discoverable (not buried in text)
- [ ] Clear distinction between "see implementation" and "comprehensive list"
- [ ] File references complement, not replace, explanatory text
- [ ] Users without clones can still understand the documentation
- [ ] Users with clones have clear navigation targets

### 4.4 Integration Testing
- [ ] Test a complete skill workflow with cloned repos:
  1. [ ] Clone yardstick using Phase 1 script
  2. [ ] Invoke add-yardstick-metric skill
  3. [ ] Follow a file reference to local clone
  4. [ ] Verify path matches and file content is relevant
  5. [ ] Repeat for recipes skill
- [ ] Verify skill works equally well WITHOUT clones

## 5. Documentation Updates

### 5.1 Update Phase 3 Plan
- [ ] Mark Phase 3 tasks complete in REPOSITORY_ACCESS_PLAN.md
- [ ] Document any deviations from original plan
- [ ] Note which references proved most valuable
- [ ] Record lessons learned about reference density

### 5.2 Document Reference Strategy
- [ ] Create `shared-references/file-reference-guide.md` if needed
- [ ] Document the "2-4 canonical examples" guideline
- [ ] Provide templates for future skill authors
- [ ] Explain when to add vs. avoid file references

## 6. Refinement (Optional)

### 6.1 Gather Feedback
- [ ] Use skills with enhanced references
- [ ] Note which references are most helpful
- [ ] Identify gaps or over-referenced areas
- [ ] Document feedback for future adjustments

### 6.2 Iterate Based on Usage
- [ ] Add references to frequently asked examples
- [ ] Remove references that clutter without helping
- [ ] Update reference density guidelines based on experience
- [ ] Share learnings with future skill development

---

## Progress Tracking

**Started**: TBD
**Status**: ⏸️ **AWAITING START**

## Success Criteria

Phase 3 is complete when:
- [ ] All SKILL.md files reviewed and enhanced with file references
- [ ] All metric type reference files updated (yardstick)
- [ ] All step type reference files updated (recipes)
- [ ] All referenced paths verified to exist
- [ ] Reference density balanced (not overwhelming)
- [ ] Documentation maintains clarity with or without clones
- [ ] Skills provide clear navigation to canonical implementations

## Notes

**Reference Philosophy**: File references should act as **navigation aids** for those with clones, not as **required reading**. The documentation should remain clear and complete even if users never follow a single file reference.

**Canonical vs. Comprehensive**: We reference 2-4 **canonical examples** that best represent a pattern, not comprehensive lists of every implementation. Users can explore beyond the references if needed.

**GitHub Compatibility**: All file paths work as relative references in GitHub's file browser, so they're useful even without local clones (users can click through to GitHub).

