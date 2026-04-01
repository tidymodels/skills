# Tidymodels Skills - News

- **Build-Verify Script Enhancements** (2026-03-24)

  - Added comment stripping (HTML comments in markdown, `#` comments in scripts) and improved relative path validation with resolved path display in error messages

- **Build and Verification Consolidation** (2026-03-24)

  - Merged `localize-shared-files.sh` and `verify-references.py` into single `build-verify.py`

  - Single command: `./dev-scripts/build-verify.py` handles both:
    - Copies shared-references files to each skill's references folder
    - Verifies all markdown links, anchors, and file references

  - Python-based for better cross-platform consistency

  - **CRITICAL**: Must be run before committing any skill changes

  - Documentation updated (CLAUDE.md and SKILL_IMPLEMENTATION_GUIDE.md) to emphasize pre-commit requirement

  - Catches broken links and out-of-sync files before they reach repository

  - Extensible foundation for future build/verification steps

- **Repository Structure Standardization** (2026-03-20)

  - **Scripts Reorganization**: Moved `shared-scripts/` to `shared-references/scripts/`
    - Creates consistency between source and localized structures
    - Scripts now live under references/, matching skill folder patterns
    - Reduces top-level directory complexity
    - Updated `localize-shared-files.sh` to copy from new location
    - All script paths in documentation updated automatically via `replace-text.py`

  - **Package Prefix Standardization**: Added "package-" prefix to shared reference filenames
    - Renamed 5 core shared references:
      - `development-workflow.md` → `package-development-workflow.md`
      - `extension-prerequisites.md` → `package-extension-prerequisites.md`
      - `extension-requirements.md` → `package-extension-requirements.md`
      - `repository-access.md` → `package-repository-access.md`
      - `roxygen-documentation.md` → `package-roxygen-documentation.md`
    - Consistent naming: all shared references now use "package-" prefix
    - Clear distinction: these are R package development resources
    - All 252+ references updated automatically via `rename-and-update.py`
    - Section anchors preserved across renames

  - **Benefits**:
    - Clearer file organization and semantic grouping
    - Single source structure mirrors localized structure
    - Future-proof for adding non-package shared references
    - Easier to identify R package development resources at a glance

- **Development Scripts Reorganization & Link Verification** (2026-03-20)

  - Added new maintenance scripts in `dev-scripts/` subfolder:
    - `verify-references.py` - Validates all markdown links and anchors
    - `replace-text.py` - Performs exact text replacements in files
    - `rename-and-update.py` - Renames files and updates all references

  - Scripts moved from root to `tidymodels/dev-scripts/` for better organization

  - Fixed all broken internal references (63 links corrected across documentation)

- **UUID-Based Warning System in verify-setup.R** (2026-03-20)

  - **CRITICAL ANTI-PATTERN FIX**: Replaced verbose error messages with UUID-only warnings

  - **Why UUIDs?** Combat Claude's propensity to start developing instead of reading documentation

  - Previous verbose warnings gave Claude enough context to attempt fixes without reading full prerequisites

  - Claude would see "Run: usethis::create_package()" and execute immediately, bypassing complete setup sequence

  - **New behavior**: verify-setup.R outputs only cryptic UUIDs (e.g., "Warning - e0f0c00a-0000")

  - Forces Claude to look up each UUID in package-extension-prerequisites.md for resolution details

  - Ensures Claude reads complete setup instructions before attempting any fixes

  - **Behavioral changes**:
    - All checks run independently (no early exits)
    - Always shows "All checks for [context] development complete." regardless of warnings
    - Source development skips all checks (avoids confusion with usethis dev version requirements)
    - Repos check now runs in empty directories (was previously skipped due to "unknown" context)

  - **Output format**: Clean, minimal, no blank lines between messages

  - **Path robustness**: Updated SKILL.md files to use `Sys.glob(path.expand(...))` for wildcard expansion

  - Single source of truth: UUID resolution details live only in package-extension-prerequisites.md

  - Result: Claude cannot skip documentation reading; must follow complete setup sequence

  - Propagated to both add-yardstick-metric and add-recipe-step skills

- **package-extension-prerequisites.md: Fixed Claude Code Execution Instructions** (2026-03-19)

  - **CRITICAL FIX**: Updated package-extension-prerequisites.md to clarify Claude Code SHOULD run R commands directly

  - Removed misleading guidance stating "you cannot run R commands directly"

  - All setup steps now explicitly instruct Claude to run `Rscript -e` commands via Bash tool

  - Changed from "Ask user to run..." to "Run this command via Bash tool..."

  - Added verification steps using Read/Bash tools for immediate feedback

  - **Root cause findings**:
    - Claude was refusing to read reference files from top-level folders during skill execution
    - Documentation falsely implied Claude couldn't execute R commands autonomously
    - Previous guidance led Claude to unnecessarily delegate all R commands to users
    - Short checklists in SKILL.md were being treated as "good enough" instead of reading full references
    - "Optional" labels were effectively disregarded by Claude, executing marked-optional steps anyway

  - **Architectural changes to prevent premature execution**:
    - Centralized `use_claude_code()` and repo cloning instructions exclusively in package-extension-prerequisites.md
    - Removed these details from SKILL.md and extension-guide.md to prevent Claude from executing before reading full reference
    - High-level documents now contain only "see package-extension-prerequisites.md" to force proper reference reading
    - Removed misleading "optional" monikers that Claude consistently ignored

  - Steps updated: package creation, Claude Code integration, dependencies, testing, and configurations

  - Result: Claude now runs full setup autonomously, verifying each step before proceeding

  - Propagated changes to both add-yardstick-metric and add-recipe-step skill references

- **Architecture: Single Source of Truth & Code Duplication Remediation** (2026-03-19)

  - **BREAKING**: Removed all code blocks from SKILL.md files to eliminate duplication

  - SKILL.md is now purely navigational (overview + links to references)

  - Removed duplicated extension prerequisites code from extension-guide.md files (both recipe and yardstick)

  - Setup code now exists only in package-extension-prerequisites.md (single source of truth)

  - Removed duplicate MAE implementation from add-yardstick-metric SKILL.md

  - Complete MAE example now lives only in numeric-metrics.md reference

  - Prevents users from following incomplete/stale setup instructions

  - Prevents inconsistency where users follow abbreviated "Quick setup" and miss critical steps

  - Documented as #1 anti-pattern in SKILL_IMPLEMENTATION_GUIDE.md

  - Makes skills maintainable: one place to update, no synchronization needed

  - Part of systematic review to eliminate all code duplication across tidymodels skills

- **Claude Code Integration** (2026-03-19)

  - Added support for `usethis::use_claude_code()` in extension setup workflow

  - Claude uses `AskUserQuestion` to prompt users to read `.claude/CLAUDE.md` after setup

  - Seamless integration: Claude reads CLAUDE.md and incorporates tidyverse patterns automatically

  - Skill composition: tidymodels-dev skills combine with tidy-* skills for complete R package guidance

  - Graceful fallback: skills work perfectly without usethis dev version

  - Clear instructions in package-extension-prerequisites.md, extension guides, and SKILL_IMPLEMENTATION_GUIDE.md

- **Extension vs Source Development Architecture** (2026-03-18)

  - Skills now support two distinct development contexts

  - Extension development: Creating new packages using only exported functions

  - Source development: Contributing to tidymodels repos with access to internal functions

  - Automatic context detection based on DESCRIPTION file

  - Dedicated guidance for each context to avoid overwhelming developers

- **Repository Access Enhancement** (2026-03-17)

  - Optional repository cloning for direct access to canonical implementations

  - Platform-agnostic scripts (bash, PowerShell, Python) for one-command cloning

  - File path references added to skill documentation

  - Entirely optional—skills work with built-in references if preferred
