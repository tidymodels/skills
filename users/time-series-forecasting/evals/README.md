# Time Series Forecasting - Evaluation Tests

This directory contains evaluation tests for the `time-series-forecasting` skill.

## Test Coverage

*Coming soon: Evaluation tests will be added during skill development.*

## Test Design Principles

Tests should cover:

- Train/test splitting for time series (initial_time_split)
- Resampling strategies (time_series_cv with proper backtesting)
- Test set protection (explicit permission before evaluation)
- Model comparison (ARIMA, ETS, Prophet, ML models)
- Feature engineering for time series (timeseries_signature, Fourier terms)
- Ensemble methods
- Reproducibility (seed setting)
- Refitting on full data before forecasting

## Running Evaluations

These tests are designed for use with the skill-creator evaluation workflow.

## Key Evaluation Criteria

For each test, evaluate:

### Time Series Best Practices

- [ ] Seeds set before initial_time_split, time_series_cv, or other random operations
- [ ] Proper temporal train/test split using initial_time_split()
- [ ] Time series resampling (time_series_cv) instead of random cross-validation
- [ ] Test set protected until explicit user permission
- [ ] Refit on full data before final forecasting

### Model Development

- [ ] Comparison of multiple approaches (classical and ML)
- [ ] Proper modeltime workflow
- [ ] Feature engineering appropriate for model type (date derivatives for ML models)
- [ ] Ensemble methods when appropriate

### Evaluation and Reporting

- [ ] Appropriate metrics (RMSE, MAE, etc.)
- [ ] Visualization of forecasts with confidence intervals
- [ ] Clear reporting of model performance

### Critical Behaviors

- [ ] **Never evaluates on test set without explicit permission**
- [ ] **Always sets seeds before random operations**
- [ ] Uses resampling (backtesting) for model comparison, not test set
