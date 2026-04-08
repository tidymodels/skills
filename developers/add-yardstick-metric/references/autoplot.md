# Autoplot Support for Metrics

**Note:** Autoplot is optional functionality. Only implement if your metric
produces multi-dimensional data that benefits from visualization.

> **Note for Source Development:** If you're contributing directly to the
> yardstick package, see existing autoplot implementations for patterns. See the
> [Source Development Guide](source-guide.md) for details.

## Overview

Autoplot provides visualization methods for metrics that produce
multi-dimensional results like curves or confusion matrices.

**Implementation examples:**

- Curve visualization: `R/prob-roc_curve.R` (ROC curve autoplot),
  `R/prob-pr_curve.R` (PR curve autoplot)

- Confusion matrix: `R/class-conf_mat.R` (heatmap and mosaic plot autoplots)

- Calibration plots: `R/prob-cal_plot_breaks.R` (calibration curve
  visualization)

- Gain/lift curves: `R/prob-gain_curve.R`, `R/prob-lift_curve.R`

**Common patterns:**

- Curve metrics: Line plots with threshold information

- Matrix metrics: Heatmaps showing confusion patterns

- Calibration: Scatter/line plots of predicted vs observed

- Multi-group: Faceted plots for different groups/resamples

**Test patterns:**

- Autoplot tests: `tests/testthat/test-prob-roc_curve.R` (includes autoplot
  validation)

- ggplot2 dependency: Tests check for graceful failure when ggplot2 not
  available

## When to Implement Autoplot

### Autoplot is appropriate for:

- **Confusion matrices**: Binary or multiclass classification results (heatmaps,
  mosaic plots)

- **Curve metrics**: ROC curves, PR curves, gain/lift curves

- **Calibration plots**: Predicted vs observed probabilities

- **Multi-threshold metrics**: Metrics calculated across threshold values

### Skip autoplot for:

- Simple scalar metrics (accuracy, MSE, etc.)

- Metrics without natural visual representation

- Metrics where visualization adds little value

## Dependencies

Add to your DESCRIPTION:

```r
usethis::use_package("ggplot2", type = "Suggests")
usethis::use_package("rlang", type = "Suggests")
```

Autoplot is optional, so ggplot2 goes in `Suggests`, not `Imports`.

## S3 Method Registration

Register the autoplot method in your package-level documentation:

```r
# In R/{packagename}-package.R
#' @importFrom ggplot2 autoplot
#' @export
ggplot2::autoplot
```

This re-exports the generic so users can call `autoplot()` directly.

## Implementation Pattern

### For curve metrics (ROC, PR, etc.)

```r
#' @export
autoplot.roc_curve <- function(object, ...) {
  # Check ggplot2 is available
  rlang::check_installed("ggplot2")

  # object is a data frame with curve data
  # Typically has columns like: .threshold, sensitivity, specificity

  ggplot2::ggplot(object, ggplot2::aes(x = 1 - specificity, y = sensitivity)) +
    ggplot2::geom_line() +
    ggplot2::geom_abline(slope = 1, intercept = 0, linetype = "dashed") +
    ggplot2::labs(
      title = "ROC Curve",
      x = "1 - Specificity (False Positive Rate)",
      y = "Sensitivity (True Positive Rate)"
    ) +
    ggplot2::coord_equal() +
    ggplot2::theme_minimal()
}
```

**Key points:**

- Check ggplot2 is installed with `rlang::check_installed()`

- Return a ggplot object

- Use descriptive labels and titles

- Consider appropriate themes and scales

### For confusion matrices

```r
#' @export
autoplot.conf_mat <- function(object, type = "heatmap", ...) {
  rlang::check_installed("ggplot2")

  type <- rlang::arg_match(type, c("heatmap", "mosaic"))

  if (type == "heatmap") {
    autoplot_conf_mat_heatmap(object, ...)
  } else {
    autoplot_conf_mat_mosaic(object, ...)
  }
}

autoplot_conf_mat_heatmap <- function(object, ...) {
  # Convert confusion matrix to long format for ggplot
  mat <- as.data.frame.table(object$table)
  names(mat) <- c("Truth", "Prediction", "Count")

  ggplot2::ggplot(mat, ggplot2::aes(x = Prediction, y = Truth, fill = Count)) +
    ggplot2::geom_tile() +
    ggplot2::geom_text(ggplot2::aes(label = Count)) +
    ggplot2::scale_fill_gradient(low = "white", high = "steelblue") +
    ggplot2::labs(
      title = "Confusion Matrix",
      x = "Predicted Class",
      y = "True Class"
    ) +
    ggplot2::theme_minimal() +
    ggplot2::coord_equal()
}
```

## Handling the `...` Parameter

The `...` parameter in `autoplot()` methods should be passed to ggplot2
functions when appropriate:

```r
#' @export
autoplot.your_metric <- function(object, ...) {
  # Extract parameters meant for your function
  type <- list(...)$type %||% "default"

  # Pass remaining parameters to ggplot if needed
  # Or ignore ... if not used

  ggplot2::ggplot(object, ...) +  # ... passed to ggplot if relevant
    # ... rest of plot
}
```

**Common uses of `...`:**

- `type` parameter to control plot type

- Aesthetic parameters to pass to ggplot layers

- Theme parameters

## Handling the `type` Parameter

For metrics with multiple visualization options:

```r
#' @param type Type of plot. Options are "heatmap" (default) or "mosaic".
#' @export
autoplot.conf_mat <- function(object, type = "heatmap", ...) {
  rlang::check_installed("ggplot2")

  type <- rlang::arg_match(type, c("heatmap", "mosaic"))

  switch(type,
    "heatmap" = plot_heatmap(object, ...),
    "mosaic" = plot_mosaic(object, ...)
  )
}
```

## Data Structure Requirements

Your metric should return a data frame or object with data suitable for
plotting:

```r
# For curve metrics
roc_curve.data.frame <- function(data, truth, estimate, ...) {
  # Calculate sensitivity and specificity at various thresholds
  results <- tibble(
    .threshold = thresholds,
    sensitivity = sens_values,
    specificity = spec_values
  )

  # Add class so autoplot.roc_curve is called
  class(results) <- c("roc_curve", class(results))

  results
}
```

## Testing Autoplot

```r
test_that("autoplot method works", {
  skip_if_not_installed("ggplot2")

  # Create test data
  df <- data.frame(
    truth = factor(c("yes", "no", "yes", "no")),
    .pred_yes = c(0.9, 0.2, 0.7, 0.3)
  )

  curve_data <- roc_curve(df, truth, .pred_yes)

  # Test that autoplot produces a ggplot
  p <- autoplot(curve_data)
  expect_s3_class(p, "ggplot")
})

test_that("autoplot handles type parameter", {
  skip_if_not_installed("ggplot2")

  cm <- conf_mat(test_data, truth, estimate)

  p_heat <- autoplot(cm, type = "heatmap")
  p_mosaic <- autoplot(cm, type = "mosaic")

  expect_s3_class(p_heat, "ggplot")
  expect_s3_class(p_mosaic, "ggplot")
})
```

## Documentation

Document the autoplot method:

```r
#' @rdname your_metric
#' @param object A `your_metric` object from `your_metric()`.
#' @param type Type of plot. Options are "default", "alternative".
#' @param ... Not currently used.
#' @export
autoplot.your_metric <- function(object, type = "default", ...) {
  # Implementation
}
```

## When to Skip Autoplot

Don't implement autoplot if:

- Your metric returns a single scalar value

- Visualization doesn't add insight

- The metric is simple and self-explanatory

- Your time is better spent on core functionality

**Focus on correctness first, visualization second.**

## Users Can Extend Plots

Users can always customize autoplot output:

```r
# Your basic autoplot
autoplot(roc_data)

# Users can extend it
autoplot(roc_data) +
  geom_point() +
  theme_bw() +
  labs(title = "My Custom Title")
```

Provide a good default, let users customize.

## Example: Complete ROC Curve Autoplot

```r
#' @export
autoplot.roc_curve <- function(object, ...) {
  # Check ggplot2 is available
  rlang::check_installed("ggplot2")

  # Validate object has required columns
  required <- c(".threshold", "sensitivity", "specificity")
  if (!all(required %in% names(object))) {
    cli::cli_abort("Object must have {.val {required}} columns.")
  }

  ggplot2::ggplot(object) +
    ggplot2::aes(x = 1 - specificity, y = sensitivity) +
    ggplot2::geom_line(linewidth = 1) +
    ggplot2::geom_abline(
      slope = 1,
      intercept = 0,
      linetype = "dashed",
      color = "gray50"
    ) +
    ggplot2::labs(
      title = "ROC Curve",
      x = "False Positive Rate (1 - Specificity)",
      y = "True Positive Rate (Sensitivity)"
    ) +
    ggplot2::coord_equal() +
    ggplot2::theme_minimal() +
    ggplot2::theme(
      plot.title = ggplot2::element_text(hjust = 0.5)
    )
}
```

## Best Practices

- **Check package availability**: Always use `rlang::check_installed("ggplot2")`

- **Return ggplot objects**: Don't print, return the object

- **Use sensible defaults**: Good labels, appropriate scales

- **Document parameters**: Especially `type` if supported

- **Test with skip**: `skip_if_not_installed("ggplot2")`

- **Keep it simple**: Don't over-complicate visualizations

## Next Steps

- Implement core metric functionality first

- Add autoplot only if it adds value

- Test thoroughly

- Document clearly

- Consider user customization needs

For most metrics, autoplot is optional. Focus on correctness and completeness of
the metric calculation first.
