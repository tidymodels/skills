# Changelog

All notable changes to the tidymodels-skills plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The version number tracked here matches `version` in
[.claude-plugin/plugin.json](.claude-plugin/plugin.json) and `metadata.version`
in [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json).

## [0.5.0] - 2026-06-24

### Added

- Plugin manifest (`.claude-plugin/plugin.json`) for the `tidymodels-skills` plugin.
- Grading configuration for the `add-recipe-step` skill evals.

### Changed

- Updated parsnip skills (`add-parsnip-model`, `add-parsnip-engine`) for parsnip 1.5.0.
- Updated quantile guidance to reflect the latest version of parsnip.
- Updated recipes skill script references to match the latest CRAN release.
- Updated yardstick skill file references after script renaming in its latest release.
- Updated dials skill references for the consolidated grid source files
  (`R/grids.R`, `R/space_filling.R`, `R/extract.R`) and refreshed the
  `values_weight_func` example (`cos`/`inv`, now 9 values).
- Refreshed roxygen2 documentation.
- Reorganized the repository structure.
- Improved the evaluation script and updated eval R paths and configs.
- Added guards to prevent unintended `git commit` usage.

### Fixed

- Fixed a roxygen issue in the parsnip grader.
- Replaced dead documentation links with nearest live matches.

[0.5.0]: https://github.com/tidymodels/skills/releases/tag/v0.5.0
