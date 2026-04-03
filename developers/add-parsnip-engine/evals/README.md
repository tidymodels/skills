# Evaluation Tests for add-parsnip-engine Skill

This directory contains quantitative evaluation tests for the `add-parsnip-engine` skill.

## Test Coverage

The evaluation suite includes 7 test cases covering:

### Extension Development (Evals 1-3)

- **Eval 1**: Simple formula interface engine (Spark for linear_reg)

- **Eval 2**: Matrix interface engine with encoding (Keras for linear_reg)

- **Eval 3**: Multi-mode engine (H2O for boost_tree with regression + classification)

### Source Development (Evals 4-6)

- **Eval 4**: Contributing single-mode engine to parsnip (xgboost for linear_reg)

- **Eval 5**: Contributing multi-mode engine (LightGBM for boost_tree with regression + classification)

- **Eval 6**: Contributing complex three-mode engine (ranger for random_forest with regression + classification + survival)

### Critical Behavior (Eval 7)

- **Eval 7**: Refusing to use internal functions (`parsnip:::`) and providing alternatives

## Key Patterns Tested

1. **Interface Types**

   - Formula interface (eval 1, 6)

   - Matrix interface (eval 2, 4, 5)

   - Data.frame interface (eval 3)

2. **Mode Handling**

   - Single mode (eval 1, 2, 4)

   - Dual mode - regression + classification (eval 3, 5)

   - Triple mode - regression + classification + survival (eval 6)

3. **Registration Sequence**

   - `set_model_engine()` - declare engine exists

   - `set_dependency()` - declare package dependencies

   - `set_model_arg()` - translate main arguments

   - `set_fit()` - specify fit method

   - `set_encoding()` - configure interface (matrix/xy only)

   - `set_pred()` - register prediction types

4. **Context Discrimination**

   - Extension: Uses `parsnip::` prefix, registration in `.onLoad()`

   - Source: No prefix, adds to existing `*_data.R` files

5. **Prediction Types**

   - Regression: numeric

   - Classification: class, prob

   - Survival: survival, time

6. **File Discipline**

   - Extension: 2-3 files (R file, test file, optional README)

   - Source: 1-2 files (adds to existing files)

   - No supplementary documentation files

## Grading Configuration

The `grading-config.json` file defines automated checks:

### File Count Checks

- Extension: 2-3 files

- Source: 1-2 files (modifications to existing)

### Prohibited Files

- Documentation: IMPLEMENTATION_SUMMARY.md, ENGINE_DESIGN.md, QUICKSTART.md

- Examples: example_usage.R, verification_script.R

- PR-related: PR_CHECKLIST.md, PR_DESCRIPTION.md, NEWS_entry.md

### Pattern Checks

**Extension Development:**

- Registration functions: set_model_engine(), set_dependency(), set_fit()

- .onLoad function present

- Roxygen @export for .onLoad

- set_pred() for predictions

- No internal functions (no :::)

- Complete tests with skip_if_not_installed

**Source Development:**

- Registration functions present

- Adds to existing *_data.R file

- Complete tests with proper checks

- No parsnip:: prefix (or minimal usage)

### Prefix Usage

- Extension: minimum 3 uses of `parsnip::`

- Source: maximum 3 uses of `parsnip::`

### Interface Configuration

- Must specify one of: 'formula', 'matrix', 'data.frame', or 'xy'

## Running Evaluations

### Manual Testing

Test individual cases:

```bash
# From workspace directory
claude --skill=/path/to/add-parsnip-engine "Eval 1 prompt here..."
```

### Automated Grading

Grade completed evaluation runs:

```bash
# With explicit config
python skill-development/grade-evaluations.py \
  developers/add-parsnip-engine-workspace/iteration-1 \
  --config developers/add-parsnip-engine/evals/grading-config.json

# With auto-detection
python skill-development/grade-evaluations.py \
  developers/add-parsnip-engine-workspace/iteration-1 \
  --skill add-parsnip-engine
```

## Expected Results

### Critical Metrics

- **Overall pass rate**: Target 80%+ (combined extension + source)

- **Context detection**: 100% (correctly identifies extension vs source)

- **Registration completeness**: 90%+ (all required functions present)

- **Interface specification**: 100% (interface type always specified)

- **File discipline**: 75-85% (acceptable range given complexity)

- **Critical behavior (eval 7)**: 100% (must refuse internal functions)

### Per-Context Targets

**Extension Development (evals 1-3, 7):**

- Registration in .onLoad: 100%

- parsnip:: prefix usage: 90%+

- No internal functions: 100%

- Complete tests: 85%+

**Source Development (evals 4-6):**

- Adds to existing files: 100%

- No/minimal parsnip:: prefix: 90%+

- Complete tests: 85%+

- Follows parsnip patterns: 80%+

### By Complexity

**Simple engines (evals 1, 2, 4):**

- Should achieve 90%+ pass rate

- Focus: correct registration sequence and interface

**Multi-mode engines (evals 3, 5):**

- Should achieve 80%+ pass rate

- Focus: separate registration per mode, mode-specific defaults

**Complex engines (eval 6):**

- Should achieve 70%+ pass rate (acceptable given three modes)

- Focus: all modes work, survival handling correct

**Critical behavior (eval 7):**

- Must achieve 100% on refusal

- Focus: clear explanation, working alternatives

## Iteration Strategy

### Priority 1: Registration Correctness

- All required functions present

- Correct interface specification

- Proper mode handling

- These are functional requirements

### Priority 2: Context Detection

- Extension vs source correctly identified

- Appropriate prefix usage

- Proper file organization

### Priority 3: Testing Quality

- skip_if_not_installed present

- Formula/xy equivalence tests

- Prediction format verification

- Parameter translation tests

### Priority 4: File Discipline

- Correct file count

- No prohibited files

- These are style requirements (lower priority)

## Known Limitations

1. **False Positives**: The `no_internal_functions` check may flag explanatory comments in eval 7 (critical behavior test) that discuss internal functions while correctly refusing to use them.

2. **File Count**: Source development file count depends on whether tests are added to existing files or new files created. Both patterns are acceptable.

3. **Interface Detection**: The interface check uses regex and may miss interfaces specified via variables or complex logic.

4. **Multi-Mode Complexity**: Eval 6 (three modes) is intentionally challenging and lower pass rates are expected.

## Future Enhancements

Potential additions to evaluation suite:

1. **Custom xy interface**: Test engines with non-standard argument names
2. **Submodel handling**: Test has_submodel parameter for models that support prediction at multiple tuning values
3. **Pre/post processing**: More complex transformations in prediction registration
4. **Error handling**: Test graceful failure when engine package not installed
5. **Multiple dependencies**: Test engines requiring multiple packages
6. **Engine-specific arguments**: Test set_model_arg with engine-specific parameters beyond main arguments

## Maintenance

When updating the skill:

1. Run evaluations with current skill version
2. Analyze failures and categorize issues
3. Update skill based on failure patterns
4. Re-run evaluations to verify improvements
5. Update grading config if check definitions need refinement
6. Iterate until pass rates meet targets

Target iteration time: 4-6 hours per cycle after initial setup.
