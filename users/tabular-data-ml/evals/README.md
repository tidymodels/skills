# Tabular Data ML - Evaluation Tests

This directory contains evaluation tests for the `tabular-data-ml` skill.

## Test Coverage

The evaluation set includes 5 test cases covering key machine learning workflows
and best practices:

### Core Supervised Learning (2 tests)

1. **Customer Churn Classification** (Eval 1): Telecom churn prediction with
   7000 rows

   - Tests: Binary classification, train/test split, cross-validation, model
     comparison (glmnet + boosted tree), feature engineering, ROC-AUC/Brier
     metrics, test set protection, seed setting

   - Complexity: Moderate

2. **House Price Regression** (Eval 2): Real estate price prediction with 1500
   homes

   - Tests: Regression workflow, handling skewed predictors, high-cardinality
     categoricals (25 neighborhoods), normalization for linear models, glmnet +
     boosted tree comparison, RMSE/R² evaluation, observed vs predicted plots,
     parallel processing inquiry, seed setting

   - Complexity: Moderate

### Data Spending and Validation (1 test)

3. **Test Set Evaluation Request** (Eval 3): User asks to evaluate on test set
   mid-development

   - Tests: Refusing premature test set evaluation, explaining test set
     protection, asking for confirmation that model development is complete

   - Complexity: Critical behavior check

   - **Expected behavior**: REFUSE and explain why

### Special Data Structures (1 test)

4. **Time Series Forecasting** (Eval 4): Monthly sales prediction with 4 years
   of data

   - Tests: Temporal structure awareness, rolling origin cross-validation
     (sliding_period), initial_time_split, rejecting random CV for time series,
     explaining temporal ordering importance, seed setting

   - Complexity: Moderate

### Complex Workflows (1 test)

5. **Hospital Readmission Prediction** (Eval 5): Patient readmission with 850
   rows

   - Tests: Missing data imputation, high-cardinality categoricals (diagnosis
     codes), workflow_set for model comparison, parallel processing setup with
     future package, proper model selection from CV results, asking permission
     before test evaluation, seed setting

   - Complexity: Advanced

## Test Design Principles

### Realistic User Prompts

Each test uses realistic, conversational prompts that include:

- Natural language with casual phrasing ("hey so i have...", "ok I split my
  data...")

- Real-world domains (telecom, real estate, healthcare, sales)

- Specific file paths and column names

- Dataset size information

- Business context and goals

- Mix of technical and non-technical language

### Coverage Strategy

- **Problem types**: Classification (binary) and regression

- **Data structures**: Standard tabular, time series

- **Best practices**: Train/test splitting, cross-validation strategy, test set
  protection, seed setting

- **Feature engineering**: Missing data, skewed predictors, high-cardinality
  categoricals, normalization

- **Model comparison**: Multiple algorithms (glmnet, boosted tree), workflow_set

- **Performance**: Parallel processing setup

- **Critical behavior**: Refusing premature test set evaluation

### Expected Outputs

Each test specifies comprehensive expected behavior including:

- Proper data spending (initial_split, appropriate resampling)

- Seed setting before all random operations

- Feature engineering appropriate to model type

- Model comparison with 2+ algorithms

- Appropriate evaluation metrics (classification: ROC-AUC, Brier; regression:
  RMSE, R²)

- Visualizations (ROC curves, observed vs predicted, residuals)

- Test set protection (asking permission before final evaluation)

- Time series awareness (rolling origin for temporal data)

- Parallel processing setup when mentioned

- Complete tidymodels workflow (recipe → workflow → fit → evaluate)

## Running Evaluations

These tests are designed for use with the skill-creator evaluation workflow:

1. **Spawn test runs**: Each eval spawned as independent subagent with the skill
2. **Grade outputs**: Check workflow correctness, tidymodels best practices,
   completeness
3. **Review results**: Human review via evaluation viewer

## Key Evaluation Criteria

For each test, evaluate:

### Tidymodels Best Practices

- [ ] Seeds set before initial_split, vfold_cv, or other random operations

- [ ] Proper train/test split using initial_split()

- [ ] Appropriate resampling strategy (vfold_cv for standard data,
      sliding_period for time series)

- [ ] Test set protected until explicit user permission

- [ ] Complete workflow: recipe → workflow → fit → tune/evaluate

### Data Handling

- [ ] Missing data addressed (imputation or explicit handling)

- [ ] Appropriate feature engineering for data types (normalization, dummy
      encoding, etc.)

- [ ] High-cardinality categoricals handled (embedding, filtering, or
      appropriate strategy)

- [ ] Skewed predictors transformed when needed for linear models

### Model Development

- [ ] Comparison of 2+ algorithms (typically glmnet and xgboost)

- [ ] Proper use of workflow objects

- [ ] Hyperparameter tuning or sensible defaults

- [ ] Model selection based on cross-validation performance

### Evaluation and Reporting

- [ ] Appropriate metrics (classification: ROC-AUC, accuracy, Brier; regression:
      RMSE, R², MAE)

- [ ] Visualizations (ROC curves, confusion matrices, observed vs predicted,
      residuals)

- [ ] Clear reporting of model performance

- [ ] Residual diagnostics for regression

### Special Considerations

- [ ] Time series: Uses rolling origin validation, explains temporal structure
      importance

- [ ] Parallel processing: Sets up future package when user has multiple cores

- [ ] Test set protection: Refuses premature evaluation, explains why test set
      matters

### Critical Behaviors

- [ ] **Never evaluates on test set without explicit permission**

- [ ] **Always sets seeds before random operations**

- [ ] Asks clarifying questions when needed

- [ ] Explains key concepts (why cross-validation, why test set protection,
      etc.)

## Notes

- All tests focus on tidymodels ecosystem and best practices

- Tests represent realistic data science scenarios across multiple domains

- Prompts intentionally vary in formality and completeness to reflect real user
  interactions

- Eval 3 specifically tests the skill's ability to refuse inappropriate actions

- Seed setting is a critical requirement across all applicable tests to ensure
  reproducibility
