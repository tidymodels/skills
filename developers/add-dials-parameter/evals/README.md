# Add Dials Parameter - Evaluation Tests

This directory contains evaluation tests for the `add-dials-parameter` skill.

## Test Coverage

The evaluation set includes 7 test cases covering both quantitative and
qualitative parameter types, with emphasis on extension development (4 tests
including critical behavior) and source development (3 tests).

### Extension Development Tests (Evals 1-3, 7)

Creating new packages that define custom tuning parameters.

#### Simple Quantitative Parameter

1. **Max Tree Depth** (Eval 1): Random forest extension - simple integer
   parameter with fixed range

   - Tests: basic quantitative parameter, integer type, fixed range, no
     transformation, dials:: prefix

   - Complexity: Simple

   - Context: Extension development for 'foresttuner' package

#### Qualitative Parameter

2. **Embedding Dimension** (Eval 2): Text modeling - categorical parameter with
   dimension labels

   - Tests: qualitative parameter, character type, discrete values, default
     value, companion values vector, dials:: prefix

   - Complexity: Simple

   - Context: Extension development for 'embeddingtuner' package

#### Data-Dependent Parameter with Custom Finalize

3. **Number of Genes** (Eval 3): Genomics feature selection - data-dependent
   with custom finalization logic

   - Tests: data-dependent parameter, unknown() bounds, custom finalize
     function, range_get/range_set, dials:: prefix

   - Complexity: Moderate

   - Context: Extension development for 'genomicselector' package

#### Critical Behavior - Refusing Internal Functions (NEW)

7. **Precision Threshold with Invalid Request** (Eval 7): User attempts to use
   internal function (dials:::check_type())

   - Tests: CRITICAL BEHAVIOR - refuses internal function usage, explains
     constraint, provides alternative, maintains dials:: prefix

   - Complexity: Simple (but tests non-negotiable constraint)

   - Context: Extension development for 'advancedtuning' package

   - **Expected behavior**: REFUSE dials::: usage and provide working
     alternative

### Source Development Tests (Evals 4-6)

Contributing parameters directly to the dials package via PRs.

#### Transformed Quantitative Parameter

4. **Dropout Rate** (Eval 4): Neural network dropout - probability parameter
   with logit transformation

   - Tests: logit transformation, inclusive/exclusive bounds, internal patterns
     (no prefix), PR conventions

   - Complexity: Moderate

   - Context: Contributing PR to tidymodels/dials

#### Data-Dependent Parameter with Built-in Finalize

5. **Number of Latent Factors** (Eval 5): Collaborative filtering - uses
   built-in finalization helper

   - Tests: data-dependent parameter, unknown() bounds, built-in finalize
     function (get_n_frac_range), internal patterns

   - Complexity: Moderate

   - Context: Contributing PR to tidymodels/dials

#### Qualitative Parameter with Companion Vector

6. **Optimizer Selection** (Eval 6): Neural network optimizer - categorical with
   values vector

   - Tests: qualitative parameter, companion values vector, @rdname pattern,
     internal patterns, PR conventions

   - Complexity: Simple

   - Context: Contributing PR to tidymodels/dials

## Test Design Principles

### Realistic User Prompts

Each test uses realistic, detailed prompts that include:

- User context and domain (random forests, text modeling, genomics, neural
  networks, etc.)

- Specific technical requirements

- Package names and clear statement of development context

- Mix of formal and casual language

- References to existing dials parameters as examples

### Coverage Strategy

- **Parameter types**:

  - Quantitative: simple (1), transformed (4), data-dependent with custom
    finalize (3), data-dependent with built-in finalize (5)

  - Qualitative: simple (2), with companion vector (6)

- **Complexity**: Mix of simple to moderate complexity

- **Core features**: Transformations, finalization, unknown() bounds, range
  specifications, inclusive/exclusive bounds, companion values vectors

- **Development contexts**:

  - Extension development (3 tests): Creating new packages with dials:: prefix

  - Source development (3 tests): Contributing PRs to dials with internal
    function access

### Expected Outputs

Each test specifies comprehensive expected output including:

- Complete parameter constructor function

- Proper use of new_quant_param() or new_qual_param()

- For data-dependent parameters: finalize function implementation

- For qualitative parameters: companion values vector

- **For extension tests (1-3)**: dials:: prefix throughout, self-contained
  implementations

- **For source tests (4-6)**: Direct use of internal functions (no prefix),
  @inheritParams usage, package conventions, PR-ready code

- Comprehensive tests (extension: own test data; source: internal test helpers)

- Roxygen documentation with proper inheritance and examples

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

- [ ] Complete parameter constructor function

- [ ] Proper use of new_quant_param() or new_qual_param()

- [ ] All required parameters specified (type, range/values, inclusive, trans,
      label, finalize)

- [ ] For data-dependent: finalize function with correct signature and logic

- [ ] For qualitative: companion values vector when appropriate

### Dials Conventions

**For extension tests (1-3):**

- [ ] Uses dials:: prefix for all functions

- [ ] Self-contained implementations (no internal function access)

- [ ] Creates own test data

- [ ] Proper parameter structure with all required fields

**For source tests (4-6):**

- [ ] Uses internal functions directly (no prefix)

- [ ] Follows package file naming conventions (R/param\_\*.R)

- [ ] Uses @inheritParams for documentation

- [ ] Uses internal test helpers if available

- [ ] Includes PR-relevant considerations (file placement, consistency)

**Common to both:**

- [ ] Proper use of type specification (double/integer/character)

- [ ] Correct range or values specification

- [ ] Appropriate transformation (scales::transform_log10(), etc.)

- [ ] Proper finalization setup (NULL, built-in function, or custom function)

### Parameter Type Patterns

**Quantitative parameters:**

- [ ] type = "double" or "integer"

- [ ] range parameter with two-element vector

- [ ] inclusive parameter specifying bound inclusivity

- [ ] trans parameter for transformations (NULL if none)

- [ ] finalize parameter (NULL, built-in, or custom function)

**Qualitative parameters:**

- [ ] type = "character" (or "logical" for binary)

- [ ] values parameter with discrete options

- [ ] optional default parameter

- [ ] companion values\_\* vector exported separately

### Finalization (Data-Dependent Parameters)

- [ ] Upper bound set to unknown()

- [ ] finalize parameter references function

- [ ] Custom finalize function signature: function(object, x)

- [ ] Uses range_get() and range_set() correctly

- [ ] Computes appropriate upper bound from data

- [ ] Returns updated parameter object

### Testing

- [ ] Parameter creation tests

- [ ] Range/values validation tests

- [ ] Grid integration tests (grid_regular, grid_random)

- [ ] Value utilities tests (value_seq, value_sample)

- [ ] For data-dependent: finalization tests

- [ ] For transformed: transformation tests

- [ ] Edge cases and error handling

### Documentation

- [ ] Roxygen tags (@param, @details, @examples, @export)

- [ ] Clear description of parameter purpose

- [ ] Examples showing usage

- [ ] For source: @inheritParams usage

- [ ] For qualitative: @rdname for companion vector

## Notes

- **Tests 1-3, 7** focus on extension development (creating new packages)

- **Tests 4-6** focus on source development (contributing to dials)

- **Test 7** is a critical behavior test: verifies skill refuses internal
  function usage

- Tests cover both quantitative and qualitative parameters

- Mix of simple parameters and complex data-dependent parameters

- Tests focus on dials-specific patterns, not general R package development

- Each test represents a realistic use case from different domains

- Prompts vary in formality and detail to reflect real user interactions

- The split between contexts tests the skill's ability to detect and adapt to
  both scenarios

- Critical behavior test (7) ensures non-negotiable constraints are enforced
