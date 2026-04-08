# Tidymodels User Skills

User-facing Claude Code skills for working with tidymodels packages in data
analysis and machine learning.

## Available Skills

### tidymodels - Tabular Data Machine Learning

Build predictive models for tabular data with proper validation practices. This
skill guides you through:

- **Data Spending**: Train/test splitting with strict test set protection rules

- **Empirical Validation**: Cross-validation and resampling strategies

- **Performance Metrics**: Classification (ROC-AUC, Brier score) and regression
  (RMSE, R²)

- **Model Optimization**: Feature engineering, model selection, and
  hyperparameter tuning

- **Model Evaluation**: Visualization and final test set evaluation

**Key principle**: All development happens on training data using out-of-sample
validation. Test set evaluation only occurs with explicit user permission.

See [tabular-data-ml/SKILL.md](tabular-data-ml/SKILL.md) for the complete skill
or [tabular-data-ml/references/](tabular-data-ml/references/) for detailed
implementation guides.

## Structure

- `tabular-data-ml/` - Tabular data machine learning skill

  - `SKILL.md` - Main skill entry point

  - `references/` - Implementation guides for:

    - Data splitting and spending

    - Resampling methods

    - Feature engineering techniques

    - Model tuning strategies

    - Evaluation metrics and visualizations

- `shared-references/` - Future shared reference materials

## Difference from Developer Skills

- **Developer skills** (`../developers/`): Creating tidymodels extensions
  (packages, metrics, steps)

- **User skills** (this directory): Using tidymodels for analysis and modeling

## Guidelines for Adding Skills

Follow the structure established in developer skills:

- Each skill folder (e.g., `tabular-data-ml/`) contains the skill

- Each skill should have a `SKILL.md` entry point

- Reference materials go in the skill's `references/` folder

- Common references go in `shared-references/`

- Use the build-verify script pattern for validation
