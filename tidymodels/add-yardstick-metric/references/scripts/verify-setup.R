# Tidymodels Development - Pre-Flight Verification Script
#
# This script checks setup state and warns about missing components
# before development starts.
#
# Usage: source("path/to/skills-personal/tidymodels/shared-scripts/verify-setup.R")

# Initialize results structure
results <- list(
  context = NULL,
  package_type = NULL,
  warnings = character(0),
  all_passed = TRUE
)

# UUID constants for warnings
UUID_NO_DESCRIPTION <- "e7f4c89a-1234"
UUID_NO_R_DIR <- "b3d9e6f2-5678"
UUID_NO_TESTS <- "a1c5d8f3-9012"
UUID_NO_CLAUDE_MD <- "f9b2e4d7-3456"
UUID_NO_REPOS <- "c8a7f1b5-7890"
UUID_MISSING_YARDSTICK <- "d4e8b9c2-1111"
UUID_MISSING_RECIPES <- "d4e8b9c2-2222"
UUID_MISSING_RLANG <- "d4e8b9c2-3333"
UUID_MISSING_CLI <- "d4e8b9c2-4444"
UUID_MISSING_TIBBLE <- "d4e8b9c2-5555"
UUID_MISSING_VCTRS <- "d4e8b9c2-6666"

# Helper function to add warning
add_warning <- function(uuid) {
  results$warnings <<- c(results$warnings, uuid)
  results$all_passed <<- FALSE
}

# ============================================================================
# 1. Check if we're in a package directory and detect context
# ============================================================================

desc_exists <- file.exists("DESCRIPTION")
desc_lines <- character(0)

if (desc_exists) {
  # Read DESCRIPTION
  desc_lines <- readLines("DESCRIPTION", warn = FALSE)
  desc_content <- paste(desc_lines, collapse = "\n")

  # Detect context (Extension vs Source Development)
  package_line <- grep("^Package:", desc_lines, value = TRUE)
  if (length(package_line) > 0) {
    package_name <- sub("^Package:\\s*", "", package_line[1])
    package_name <- trimws(package_name)

    if (package_name %in% c("recipes", "yardstick")) {
      results$context <- "source"
      results$package_type <- package_name
    } else {
      results$context <- "extension"
      # Detect package type from Imports
      imports_line <- grep("^Imports:", desc_lines, value = TRUE)
      if (length(imports_line) > 0) {
        if (grepl("recipes", imports_line[1])) {
          results$package_type <- "recipes"
        } else if (grepl("yardstick", imports_line[1])) {
          results$package_type <- "yardstick"
        } else {
          results$package_type <- "unknown"
        }
      } else {
        results$package_type <- "unknown"
      }
    }
  } else {
    results$context <- "unknown"
    results$package_type <- "unknown"
  }
} else {
  # No DESCRIPTION file
  results$context <- "unknown"
  results$package_type <- "unknown"
}

# ============================================================================
# 2. Run checks (only for extension development)
# ============================================================================

# Skip all checks for source development
if (results$context != "source") {

  # Check DESCRIPTION
  if (!desc_exists) {
    add_warning(UUID_NO_DESCRIPTION)
  }

  # Check R/ directory (always check, even if DESCRIPTION missing)
  if (!dir.exists("R")) {
    add_warning(UUID_NO_R_DIR)
  }

  # Check tests/testthat/ directory (always check)
  if (!dir.exists("tests/testthat")) {
    add_warning(UUID_NO_TESTS)
  }

  # Check for .claude/CLAUDE.md (always check)
  if (!file.exists(".claude/CLAUDE.md")) {
    add_warning(UUID_NO_CLAUDE_MD)
  }

  # Check Repository Access (always check unless source development)
  # Check for repos even if package_type is unknown
  has_repos <- FALSE
  if (results$package_type %in% c("recipes", "yardstick")) {
    # Check for specific repo
    repo_path <- file.path("repos", results$package_type)
    has_repos <- dir.exists(repo_path)
  } else {
    # Unknown package type - check if ANY tidymodels repos exist
    has_repos <- dir.exists("repos/yardstick") || dir.exists("repos/recipes")
  }

  if (!has_repos) {
    add_warning(UUID_NO_REPOS)
  }

  # Check Dependencies (only if DESCRIPTION exists and package type is known)
  if (desc_exists && results$package_type %in% c("recipes", "yardstick")) {
    # Get Imports field
    imports_start <- grep("^Imports:", desc_lines)
    if (length(imports_start) > 0) {
      # Find the extent of Imports (until next field or end)
      next_field <- grep("^[A-Z]", desc_lines)
      next_field <- next_field[next_field > imports_start[1]]
      if (length(next_field) > 0) {
        imports_end <- next_field[1] - 1
      } else {
        imports_end <- length(desc_lines)
      }
      imports_text <- paste(desc_lines[imports_start[1]:imports_end], collapse = " ")
      imports_text <- tolower(imports_text)
    } else {
      imports_text <- ""
    }

    # Check required packages based on package type
    if (results$package_type == "yardstick") {
      if (!grepl("yardstick", imports_text)) add_warning(UUID_MISSING_YARDSTICK)
      if (!grepl("rlang", imports_text)) add_warning(UUID_MISSING_RLANG)
      if (!grepl("cli", imports_text)) add_warning(UUID_MISSING_CLI)
    } else if (results$package_type == "recipes") {
      if (!grepl("recipes", imports_text)) add_warning(UUID_MISSING_RECIPES)
      if (!grepl("rlang", imports_text)) add_warning(UUID_MISSING_RLANG)
      if (!grepl("cli", imports_text)) add_warning(UUID_MISSING_CLI)
      if (!grepl("tibble", imports_text)) add_warning(UUID_MISSING_TIBBLE)
      if (!grepl("vctrs", imports_text)) add_warning(UUID_MISSING_VCTRS)
    }
  }
}

# ============================================================================
# 6. Print Summary
# ============================================================================

# Default to "extension" for unknown contexts
context_name <- if (results$context == "source") "source" else "extension"

if (!results$all_passed) {
  # Warnings found - output UUIDs only
  for (uuid in results$warnings) {
    cat("Warning -", uuid, "\n")
  }
  cat("See package-extension-prerequisites.md to resolve these warnings.\n")
}
# Always show completion message
cat("All checks for", context_name, "development complete.\n")
