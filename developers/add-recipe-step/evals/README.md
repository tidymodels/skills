# Add Recipe Step - Evaluation Tests

This directory contains evaluation tests for the `add-recipe-step` skill.

## Test Coverage

The evaluation set includes 6 test cases covering the three main recipe step patterns, split evenly between extension development (3 tests) and source development (3 tests).

### Extension Development Tests (Evals 1-3)
Creating new packages that extend recipes.

#### Modify-in-Place Steps

1. **Winsorize** (Eval 1): Clinical trial analysis - caps extreme values at percentiles

   - Tests: percentile calculation, case weights, in-place modification, recipes:: prefix usage

   - Complexity: Moderate

   - Context: Extension development for 'recipeextras' package

#### Create-New-Columns Steps

2. **Binning** (Eval 2): Manufacturing sensor data - discretizes continuous variables into categories

   - Tests: quantile-based binning, keep_original_cols, role assignment, new column naming, recipes:: prefix

   - Complexity: Moderate

   - Context: Extension development for 'factoryrecipes' package

#### Row-Operation Steps

3. **Filter Missing** (Eval 3): Healthcare data cleaning - removes rows with too much missing data

   - Tests: row filtering, skip parameter, threshold behavior, column selection, recipes:: prefix

   - Complexity: Simple

   - Context: Extension development for 'datacleaning' package

### Source Development Tests (Evals 4-6)
Contributing directly to the recipes package via PRs.

#### Modify-in-Place Steps

4. **Custom Range Scaling** (Eval 4): Scales to custom min/max ranges (similar to normalize)

   - Tests: linear transformation, weighted statistics, internal function usage (no prefix), PR conventions

   - Complexity: Moderate

   - Context: Contributing PR to tidymodels/recipes

#### Create-New-Columns Steps

5. **Flag Outliers** (Eval 5): Creates binary indicators for outliers using IQR method

   - Tests: IQR method, indicator variables, keep_original_cols, internal helpers, test patterns

   - Complexity: Moderate

   - Context: Contributing PR to tidymodels/recipes

#### Row-Operation Steps

6. **Filter Short Text** (Eval 6): Removes rows with short text responses

   - Tests: character counting, skip parameter, text validation, file placement, internal patterns

   - Complexity: Simple

   - Context: Contributing PR to tidymodels/recipes

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

- **Development contexts**:

  - Extension development (3 tests): Creating new packages with recipes:: prefix

  - Source development (3 tests): Contributing PRs to recipes with internal function access

### Expected Outputs
Each test specifies comprehensive expected output including:

- Complete three-function pattern (constructor, _new, prep/bake methods)

- All required S3 methods (print, tidy)

- Proper use of recipes helpers (recipes_eval_select, check_type, etc.)

- **For extension tests (1-3)**: recipes:: prefix throughout, self-contained implementations

- **For source tests (4-6)**: Direct use of internal functions (no prefix), package conventions, PR-ready code

- Comprehensive tests (extension: own test data; source: internal test helpers)

- Roxygen documentation (extension: self-contained; source: uses @inheritParams and templates)

## Running Evaluations

These tests are designed for use with the skill-creator evaluation workflow:

1. **Spawn test runs**: Each eval spawned as independent subagent with the skill
2. **Grade outputs**: Check implementation completeness, correctness, patterns
3. **Review results**: Human review via evaluation viewer

## Key Evaluation Criteria

For each test, evaluate:

### Context Detection

- [ ] Correctly identifies whether user is doing extension or source development

- [ ] Adapts guidance appropriately based on context

- [ ] Provides context-appropriate code patterns

### Implementation Completeness

- [ ] Three-function pattern (constructor, _new, S3 methods)

- [ ] All required methods (prep, bake, print, tidy)

- [ ] Proper parameter handling

- [ ] Error checking and validation

### Recipes Conventions

**For extension tests (1-3):**

- [ ] Uses recipes:: prefix for all functions

- [ ] Self-contained implementations (no internal function access)

- [ ] Creates own test data

**For source tests (4-6):**

- [ ] Uses internal functions directly (no prefix)

- [ ] Follows package file naming conventions

- [ ] Uses internal test helpers and data

- [ ] Includes PR-relevant considerations (file placement, consistency with existing steps)

**Common to both:**

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

- **Tests 1-3** focus on extension development (creating new packages)

- **Tests 4-6** focus on source development (contributing to recipes)

- Tests focus on recipes-specific patterns, not general R package development

- Each test represents a realistic use case from different domains

- Prompts vary in formality and detail to reflect real user interactions

- The split between contexts tests the skill's ability to detect and adapt to both scenarios
