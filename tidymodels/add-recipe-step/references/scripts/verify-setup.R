# Tidymodels Development - Pre-Flight Verification Script
#
# This script checks setup state and warns about missing components
# before development starts.
#
# Usage: source("path/to/skills-personal/tidymodels/shared-scripts/verify-setup.R")

# Check if cli package is available for prettier output
use_cli <- requireNamespace("cli", quietly = TRUE)

# Initialize results structure
results <- list(
  context = NULL,
  package_type = NULL,
  checks = list(
    structure = list(passed = TRUE, warnings = character(0)),
    claude_code = list(passed = TRUE, warnings = character(0)),
    repository = list(passed = TRUE, warnings = character(0)),
    dependencies = list(passed = TRUE, warnings = character(0))
  ),
  all_passed = TRUE,
  warning_count = 0
)

# Helper function to add warning
add_warning <- function(check_name, warning_msg) {
  results$checks[[check_name]]$passed <<- FALSE
  results$checks[[check_name]]$warnings <<- c(
    results$checks[[check_name]]$warnings,
    warning_msg
  )
  results$all_passed <<- FALSE
  results$warning_count <<- results$warning_count + 1
}

# Helper function to print section header
print_header <- function(text) {
  if (use_cli) {
    cli::cli_h2(text)
  } else {
    cat("\n", text, ":\n", sep = "")
  }
}

# Helper function to print check result
print_check <- function(passed, msg) {
  if (use_cli) {
    if (passed) {
      cli::cli_alert_success(msg)
    } else {
      cli::cli_alert_danger(paste("WARNING:", msg))
    }
  } else {
    symbol <- if (passed) "\u2713" else "\u2717"
    cat("  ", symbol, " ", msg, "\n", sep = "")
  }
}

# Helper function to print info
print_info <- function(msg) {
  if (use_cli) {
    cli::cli_alert_info(msg)
  } else {
    cat("  \u2139 ", msg, "\n", sep = "")
  }
}

# Helper function to print action
print_action <- function(msg) {
  cat("    \u2192 ", msg, "\n", sep = "")
}

# Print banner
cat("\n")
cat("========================================\n")
cat("Tidymodels Development - Pre-Flight Check\n")
cat("========================================\n")

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
      context_label <- paste0("Source Development (", package_name, ")")
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
      context_label <- paste0("Extension Development (", results$package_type, ")")
    }
  } else {
    results$context <- "unknown"
    results$package_type <- "unknown"
    context_label <- "Unknown (DESCRIPTION malformed)"
  }
} else {
  # No DESCRIPTION file
  results$context <- "unknown"
  results$package_type <- "unknown"
  context_label <- "Unknown (no DESCRIPTION)"
}

cat("\nContext: ", context_label, "\n", sep = "")

# ============================================================================
# 2. Check Package Structure
# ============================================================================

print_header("Package Structure")

# Check DESCRIPTION
if (desc_exists) {
  print_check(TRUE, "DESCRIPTION found")

  # Only check other structure if package exists
  # Check R/ directory
  if (dir.exists("R")) {
    print_check(TRUE, "R/ directory exists")
  } else {
    print_check(FALSE, "R/ directory not found")
    print_action("Run: dir.create(\"R\")")
    print_action("Review and follow instructions in ../shared-references/r-package-setup.md")
    add_warning("structure", "R/ directory not found")
  }

  # Check tests/testthat/ directory
  if (dir.exists("tests/testthat")) {
    print_check(TRUE, "tests/testthat/ directory exists")
  } else {
    print_check(FALSE, "tests/testthat/ not found")
    print_action("Run: usethis::use_testthat()")
    print_action("Review and follow instructions in ../shared-references/r-package-setup.md")
    add_warning("structure", "tests/testthat/ not found")
  }
} else {
  print_check(FALSE, "DESCRIPTION not found")
  print_action("Run: usethis::create_package(\".\", open = FALSE)")
  print_action("This will create DESCRIPTION and R/ directory")
  print_action("Review and follow instructions in ../shared-references/r-package-setup.md")
  add_warning("structure", "DESCRIPTION not found")
  print_info("Skipping R/ and tests/ checks - create package first")
}

# ============================================================================
# 3. Check Claude Code Integration
# ============================================================================

print_header("Claude Code Integration")

# Check usethis version
usethis_available <- requireNamespace("usethis", quietly = TRUE)

if (usethis_available) {
  usethis_version <- packageVersion("usethis")
  required_version <- package_version("3.2.1.9000")

  if (usethis_version >= required_version) {
    print_check(TRUE, paste0("usethis ", usethis_version, "+ installed"))

    # Check for .claude/CLAUDE.md
    if (file.exists(".claude/CLAUDE.md")) {
      print_check(TRUE, ".claude/CLAUDE.md found")
    } else {
      print_check(FALSE, ".claude/CLAUDE.md not found")
      print_action("Run: usethis::use_claude_code()")
      print_action("IMPORTANT: Must run BEFORE adding other dependencies")
      print_action("This enables Claude to read tidyverse development patterns")
      print_action("Review and follow instructions in ../shared-references/r-package-setup.md")
      add_warning("claude_code", ".claude/CLAUDE.md not found")
    }
  } else {
    print_info(paste0("usethis ", usethis_version, " (Claude Code requires 3.2.1.9000+)"))
    # Not a warning - just informational
  }
} else {
  print_info("usethis not installed (Claude Code requires usethis 3.2.1.9000+)")
  # Not a warning - just informational
}

# ============================================================================
# 4. Check Repository Access (Extension Development Only)
# ============================================================================

print_header("Repository Access")

if (results$context == "source") {
  print_info("Not applicable (source development)")
} else if (results$context == "extension") {
  # Check repos/ directory
  repos_exists <- dir.exists("repos")
  if (repos_exists) {
    print_check(TRUE, "repos/ directory exists")
  } else {
    print_check(FALSE, "repos/ directory not found")
  }

  # Check for specific repo
  if (results$package_type %in% c("recipes", "yardstick")) {
    repo_path <- file.path("repos", results$package_type)
    if (dir.exists(repo_path)) {
      print_check(TRUE, paste0(repo_path, "/ found"))
    } else {
      print_check(FALSE, paste0(repo_path, "/ not found"))
      print_action("Reference implementations are critical for development")
      print_action("Follow instructions in ../shared-references/repository-access.md")
      print_action(paste0("Run: ./path/to/clone-tidymodels-repos.sh ", results$package_type))
      add_warning("repository", paste0(repo_path, "/ not found"))
    }
  } else {
    print_info("Cannot determine package type from Imports (recipes or yardstick)")
    print_action("Add recipes or yardstick to Imports in DESCRIPTION")
  }
} else {
  print_info("Context unknown - cannot check repository access")
}

# ============================================================================
# 5. Check Dependencies (Extension Development Only)
# ============================================================================

print_header("Dependencies")

if (results$context == "source") {
  print_info("Not checked (source development)")
} else if (results$context == "extension") {
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

  # Define required packages
  if (results$package_type == "recipes") {
    required_pkgs <- c("recipes", "rlang", "tibble", "vctrs", "cli")
  } else if (results$package_type == "yardstick") {
    required_pkgs <- c("yardstick", "rlang", "cli")
  } else {
    required_pkgs <- character(0)
    print_info("Cannot determine required packages (unknown package type)")
  }

  # Check each required package
  if (length(required_pkgs) > 0) {
    any_missing <- FALSE
    for (pkg in required_pkgs) {
      if (grepl(pkg, imports_text)) {
        print_check(TRUE, paste0(pkg, " in Imports"))
      } else {
        print_check(FALSE, paste0(pkg, " not in Imports"))
        print_action(paste0("Run: usethis::use_package(\"", pkg, "\")"))
        any_missing <- TRUE
        add_warning("dependencies", paste0(pkg, " not in Imports"))
      }
    }

    if (any_missing) {
      print_action("Review and follow instructions in ../shared-references/r-package-setup.md")
    }
  }
} else {
  print_info("Context unknown - cannot check dependencies")
}

# ============================================================================
# 6. Print Summary
# ============================================================================

cat("\n")
cat("========================================\n")

if (results$all_passed) {
  if (use_cli) {
    cli::cli_alert_success("All checks passed!")
  } else {
    cat("\u2713 All checks passed!\n")
  }
  cat("\n")
  if (use_cli) {
    cli::cli_alert_success("You can now proceed with development")
  } else {
    cat("\u2713 You can now proceed with development\n")
  }
} else {
  cat("Summary: ", results$warning_count, " warning",
      if (results$warning_count != 1) "s" else "", " found\n", sep = "")
  cat("\n")
  if (use_cli) {
    cli::cli_alert_warning("REQUIRED: After addressing deficiencies, re-run this script")
  } else {
    cat("\u26A0 REQUIRED: After addressing deficiencies, re-run this script\n")
  }
  cat("\nTo re-run:\n")
  cat("  Rscript -e 'source(\"~/.claude/plugins/cache/tidymodels-skills/tidymodels-dev/*/tidymodels/shared-scripts/verify-setup.R\")'\n")
}

cat("========================================\n\n")
