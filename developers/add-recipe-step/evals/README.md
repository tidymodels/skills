# Add Recipe Step - Evaluation Tests

This directory contains evaluation tests for the `add-recipe-step` skill.

## Test Coverage

The evaluation set includes 6 test cases covering the three main recipe step patterns:

### Modify-in-Place Steps (2 tests)
Steps that transform existing columns without creating new ones.

1. **Winsorize** (Eval 1): Clinical trial analysis - caps extreme values at percentiles

   - Tests: percentile calculation, case weights, in-place modification

   - Complexity: Moderate

2. **Custom Range Scaling** (Eval 4): Environmental modeling - scales to custom min/max ranges

   - Tests: linear transformation, weighted statistics, parameter handling

   - Complexity: Moderate

### Create-New-Columns Steps (3 tests)
Steps that generate new columns from existing ones.

3. **Binning** (Eval 2): Manufacturing sensor data - discretizes continuous variables into categories

   - Tests: quantile-based binning, keep_original_cols, role assignment, new column naming

   - Complexity: Moderate

4. **Flag Outliers** (Eval 5): Fraud detection - creates binary indicators for outliers

   - Tests: IQR method, indicator variables, keep_original_cols, parameterized threshold

   - Complexity: Moderate

### Row-Operation Steps (2 tests)
Steps that filter or remove rows from data.

5. **Filter Missing** (Eval 3): Healthcare data cleaning - removes rows with too much missing data

   - Tests: row filtering, skip parameter, threshold behavior, column selection

   - Complexity: Simple

6. **Filter Short Text** (Eval 6): Text analysis - removes rows with short text responses

   - Tests: character counting, skip parameter, text column validation

   - Complexity: Simple

## Test Design Principles

### Realistic User Prompts
Each test uses realistic, detailed prompts that include:

- User context and domain (clinical trials, manufacturing, healthcare, etc.)

- Specific technical requirements

- Package names and file paths

- Mix of formal and casual language

- Clear statement of development context (extension development)

### Coverage Strategy

- **Step types**: All three main patterns (modify-in-place, create-new-columns, row-operations)

- **Complexity**: Mix of simple to moderate complexity

- **Core features**: Variable selection, case weights, role assignment, keep_original_cols, skip parameter

- **Development context**: All tests focus on extension development (creating new packages)

### Expected Outputs
Each test specifies comprehensive expected output including:

- Complete three-function pattern (constructor, _new, prep/bake methods)

- All required S3 methods (print, tidy)

- Proper use of recipes helpers (recipes_eval_select, check_type, etc.)

- Extension pattern with recipes:: prefix throughout

- Comprehensive tests

- Roxygen documentation

## Running Evaluations

These tests are designed for use with the skill-creator evaluation workflow:

1. **Spawn test runs**: Each eval spawned as independent subagent with the skill
2. **Grade outputs**: Check implementation completeness, correctness, patterns
3. **Review results**: Human review via evaluation viewer

## Key Evaluation Criteria

For each test, evaluate:

### Implementation Completeness

- [ ] Three-function pattern (constructor, _new, S3 methods)

- [ ] All required methods (prep, bake, print, tidy)

- [ ] Proper parameter handling

- [ ] Error checking and validation

### Recipes Conventions

- [ ] Uses recipes:: prefix for all functions (extension pattern)

- [ ] Proper use of recipes_eval_select() in prep

- [ ] Appropriate use of check_type(), check_new_data()

- [ ] Correct handling of trained flag

### Step Type Patterns

- [ ] Modify-in-place: role = NA, no keep_original_cols

- [ ] Create-new-columns: role = "predictor", keep_original_cols parameter

- [ ] Row-operations: skip = TRUE default

### Testing

- [ ] Correctness tests (step works as intended)

- [ ] Edge cases (NA handling, empty data, etc.)

- [ ] Infrastructure (works in recipe pipeline)

- [ ] Feature-specific (case weights, skip, keep_original_cols, etc.)

### Documentation

- [ ] Roxygen tags (@param, @return, @export)

- [ ] Clear description and details

- [ ] Working examples

- [ ] Proper inheritance (@inheritParams)

## Notes

- All tests assume extension development context (not contributing to recipes itself)

- Tests focus on recipes-specific patterns, not general R package development

- Each test represents a realistic use case from different domains

- Prompts vary in formality and detail to reflect real user interactions
