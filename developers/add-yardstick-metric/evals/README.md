# Evaluations for add-yardstick-metric Skill

This directory contains quantitative evaluation test cases for the `add-yardstick-metric` skill.

## Overview

These evaluations measure the skill's effectiveness across different scenarios:

- **Extension development** (creating new packages that extend yardstick)
- **Source development** (contributing PRs to yardstick itself)
- **Different metric types** (numeric, class, probability)
- **Critical behaviors** (file discipline, refusing to use internal functions)

## Test Cases

### Eval 1: Simple Numeric Metric (Extension Dev)
- **Metric:** Weighted Absolute Percentage Error (WAPE)
- **Context:** Extension development for retail forecasting package
- **Tests:** Three-function pattern, case weights, NA handling, extension patterns (yardstick:: prefix)

### Eval 2: Class Metric with Multiclass (Extension Dev)
- **Metric:** Positive Likelihood Ratio (PLR)
- **Context:** Extension development for medical diagnostics
- **Tests:** Confusion matrix usage, event_level parameter, multiclass averaging, case weights

### Eval 3: Probability Metric (Extension Dev)
- **Metric:** Calibration Slope
- **Context:** Extension development for probabilistic forecasting
- **Tests:** Probability validation, logistic regression, calibration assessment, case weights

### Eval 4: Robust Numeric Metric (Source Dev PR)
- **Metric:** Median Absolute Error (MedAE)
- **Context:** Contributing to yardstick itself
- **Tests:** Internal helpers (yardstick_median), file naming (R/num-*.R), no supplementary files, source patterns

### Eval 5: Binary Classification Metric (Source Dev PR)
- **Metric:** Balanced Accuracy
- **Context:** Contributing to yardstick for imbalanced datasets
- **Tests:** Binary + multiclass patterns, internal test data, confusion matrix, event_level

### Eval 6: Complex Probability Metric (Source Dev PR)
- **Metric:** Expected Calibration Error (ECE)
- **Context:** Contributing advanced calibration metric
- **Tests:** Binning logic, probability validation, edge cases, file naming (R/prob-*.R)

### Eval 7: Critical Behavior Test (Extension Dev)
- **Scenario:** User attempts to use internal functions (yardstick:::)
- **Expected:** Skill explicitly refuses and provides alternatives
- **Tests:** Constraint enforcement, alternative suggestions, working implementation without :::

## Evaluation Structure

Each test case in `evals.json` contains:

```json
{
  "id": 1,
  "prompt": "Realistic user request describing metric and context",
  "expected_output": "Detailed description of what should be produced",
  "files": [],
  "expectations": [
    "Testable assertion about file creation",
    "Testable assertion about code patterns",
    "..."
  ]
}
```

## Assertion Categories

Each test case now includes explicit assertions across 5 categories:

### 1. File Discipline (Priority 1)
Tests that ONLY the required files are created (no supplementary docs).

### 2. Code Structure (High Priority)
Tests that all functions are present with correct signatures, patterns, and prefixes.

### 3. Functional Correctness (High Priority)
Tests that metrics calculate correctly, formulas are right, and edge cases handled.

### 4. Test Quality (High Priority)
Tests that test suites actually verify correctness with known values, not just run.

### 5. Integration & Documentation (Medium Priority)
Tests that metrics work with yardstick infrastructure and docs are complete.

## Key Assertions

These evaluations specifically test:

### File Discipline (Priority 1)
- ✅ Creates EXACTLY 2-3 files for extension dev (R file, test file, optional README)
- ✅ Creates EXACTLY 2 files for source dev (R file, test file)
- ❌ Does NOT create supplementary documentation files
- ❌ No IMPLEMENTATION_SUMMARY.md, QUICKSTART.md, example_usage.R, etc.

### Code Patterns (High Priority)
- ✅ Uses yardstick:: prefix consistently (extension dev)
- ✅ No yardstick:: prefix (source dev)
- ✅ Three-function pattern for most metrics (_impl, _vec, .data.frame)
- ✅ Proper use of yardstick infrastructure (new_*_metric, check_*_metric, yardstick_remove_missing)

### Testing Coverage (High Priority)
- ✅ Correctness tests (metric calculates correctly)
- ✅ NA handling tests (na_rm = TRUE and FALSE)
- ✅ Input validation tests (wrong types, mismatched lengths)
- ✅ Case weights tests (weighted differs from unweighted)
- ✅ Edge cases (zeros, negatives, perfect prediction, all wrong)

### Documentation (Medium Priority)
- ✅ Roxygen documentation with @family, @export, @examples
- ✅ Extension dev: @inheritParams, @param, @details
- ✅ Source dev: @inheritParams, @template, @templateVar

### Critical Behaviors (Critical)
- ✅ Refuses to use internal functions (:::) in extension dev
- ✅ Explains constraints and provides alternatives
- ✅ Suggests source development when internal functions needed

## Running Evaluations

To run these evaluations, use the skill-creator skill:

```
Use the skill-creator skill to:
1. Load the add-yardstick-metric skill
2. Run test cases from evals.json
3. Generate benchmark results
4. Review outputs in the eval viewer
```

The evaluation workflow:
1. Spawn subagents for each test case (with skill and without/baseline)
2. Grade outputs against expectations
3. Aggregate results into benchmark.json
4. Analyze patterns and failures
5. Iterate on skill improvements

## Success Metrics

Based on lessons learned from add-dials-parameter evaluations:

### Target Pass Rates (After File Discipline Updates)
- **Extension development:** ≥90% file discipline compliance
- **Source development:** ≥80% file discipline compliance
- **Overall file discipline:** ≥85% pass rate
- **Code patterns:** ≥90% correctness
- **Testing coverage:** ≥85% completeness
- **Critical behaviors:** 100% (must refuse internal functions)

### File Count Targets
- Extension dev: 2-3 files (R + test + optional README)
- Source dev: 2 files (R + test)
- Supplementary files: 0 (zero tolerance)

### Time and Token Trade-offs
- Skills typically use +18-67% more tokens than baseline
- This is acceptable trade-off for quality improvement
- Focus on correctness, not token efficiency
- Consistency is more valuable than speed

## Benchmark Structure

After running evaluations, benchmark.json will contain:

```json
{
  "skill_name": "add-yardstick-metric",
  "configurations": [
    {
      "name": "with_skill",
      "pass_rate": {"mean": 0.857, "std": 0.141, "min": 0.5, "max": 1.0},
      "time": {"mean": 45.2, "std": 12.3},
      "tokens": {"mean": 15234, "std": 3421}
    },
    {
      "name": "baseline",
      "pass_rate": {"mean": 0.285, "std": 0.213, "min": 0.0, "max": 0.67},
      "time": {"mean": 38.1, "std": 15.2},
      "tokens": {"mean": 12841, "std": 4123}
    }
  ],
  "deltas": {
    "pass_rate": "+57.2 pp",
    "time": "+18.6%",
    "tokens": "+18.6%"
  }
}
```

## Iteration Process

1. **Iteration 1:** Run all tests with current skill
2. **Review:** Analyze failures, identify patterns
3. **Improve:** Update skill based on failure modes
4. **Iteration 2:** Rerun with improvements
5. **Compare:** Measure improvement over baseline and previous iteration
6. **Repeat:** Until target metrics achieved (typically 2-3 iterations)

## Test Case Design Principles

From lessons learned (SKILL_IMPLEMENTATION_GUIDE.md):

1. **Realistic prompts:** Use actual user language, not abstract descriptions
2. **Clear contexts:** Specify extension vs source development explicitly
3. **Concrete details:** Include package names, file paths, specific values
4. **Edge cases:** Test boundary conditions and common mistakes
5. **Critical behaviors:** Include refusal tests for non-negotiable constraints
6. **Coverage balance:** 50/50 split between extension and source development
7. **Metric variety:** Cover numeric, class, and probability metrics

## Analyzing Results

### Key Questions After Running Evaluations

1. **File Discipline:**
   - How many supplementary files were created?
   - Which evals violated file limits?
   - What types of files are being created incorrectly?

2. **Code Patterns:**
   - Is yardstick:: prefix used correctly in extension dev?
   - Are internal functions avoided in extension dev?
   - Is three-function pattern implemented correctly?

3. **Testing Coverage:**
   - Are all 5 test categories covered (correctness, NA, validation, case weights, edge cases)?
   - Do tests actually verify the metric works?
   - Are edge cases handled properly?

4. **Critical Behaviors:**
   - Does eval-7 correctly refuse to use internal functions?
   - Are alternatives provided when internal functions requested?
   - Is source development suggested as option?

### Common Failure Patterns

Based on add-dials-parameter experience:

- **File discipline failures:** Most common (0% → 85% with improvements)
- **Context confusion:** Mixing extension and source patterns
- **Testing gaps:** Missing NA handling or case weights tests
- **Documentation shortcuts:** Incomplete roxygen or missing examples
- **Internal function usage:** Accidentally using ::: in extension dev

## Next Steps After Evaluation

1. **Identify top 3 failure modes** from results
2. **Update skill** to address specific failures
3. **Rerun affected tests** to verify improvements
4. **Measure delta** from previous iteration
5. **Continue until** target metrics achieved (85%+ overall)

---

**Created:** 2026-04-03
**Based on:** Lessons learned from add-dials-parameter and add-recipe-step evaluations
**Expected improvement:** 50-85 percentage point improvement over baseline
