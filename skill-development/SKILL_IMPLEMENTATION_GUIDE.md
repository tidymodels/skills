# Tidymodels Skill Implementation Guide

**Purpose:** Guide for creating new skills in the tidymodels skill system (e.g., add-parsnip-model, add-dials-parameter).

**Last Updated:** 2026-04-03

---

## Overview

This guide documents the current architecture and patterns for tidymodels skills, based on the completed `add-yardstick-metric` and `add-recipe-step` skills.

### Current Skills

- **add-yardstick-metric** - Creating custom performance metrics
- **add-recipe-step** - Creating preprocessing steps for recipes
- **add-dials-parameter** - Creating custom tuning parameters
- *(Future: add-parsnip-model, etc.)*

---

## Core Architecture: Extension vs Source Development

### The Dual Context Pattern

Every tidymodels skill supports **two distinct development contexts**:

1. **Extension Development** (Default)
   - Creating **new R packages** that extend tidymodels
   - Cannot use internal functions (only exported functions with `package::` prefix)
   - For CRAN submissions, standalone packages, independent work
   - Package detection: No tidymodels package name in DESCRIPTION's `Package:` field

2. **Source Development** (Advanced)
   - Contributing **directly to tidymodels repositories** via PRs
   - Can use internal functions without prefix
   - Has access to internal helpers, test data, documentation templates
   - Package detection: tidymodels package name in DESCRIPTION's `Package:` field

### Why This Split Matters

**Extension developers** (90% of users):
- Must use only exported functions
- Need self-contained implementations
- Require complete examples showing all code
- Face stricter constraints but get portability

**Source developers** (10% - contributors):
- Can leverage internal infrastructure
- Follow package-specific conventions
- Have access to internal test helpers
- Need to match existing code style exactly

---

## File Structure

### Complete Skill Directory Structure

```
developers/
├── add-[package]-[feature]/          # E.g., add-yardstick-metric
│   ├── SKILL.md                      # Main entry point (REQUIRED)
│   ├── extension-guide.md            # Extension development guide
│   ├── source-guide.md               # Source development guide
│   ├── testing-patterns-source.md    # Package-specific testing
│   ├── best-practices-source.md      # Package-specific practices
│   ├── troubleshooting-source.md     # Package-specific troubleshooting
│   └── references/                   # Detailed reference docs
│       ├── [topic1].md
│       ├── [topic2].md
│       └── ...
│
└── shared-references/                # Universal cross-skill resources
    ├── package-extension-requirements.md     # All-in-one: best practices, testing, troubleshooting
    ├── package-extension-prerequisites.md
    ├── package-development-workflow.md
    ├── package-roxygen-documentation.md
    ├── package-imports.md
    └── package-repository-access.md
```

### Shared Scripts (Optional)

```
developers/shared-references/scripts/
├── README.md
├── clone-tidymodels-repos.sh    # Bash script
├── clone-tidymodels-repos.ps1   # PowerShell script
└── clone-tidymodels-repos.py    # Python script
```

---

## Core Principle: Avoid Code Duplication

**The #1 rule for skill architecture: Each piece of content should exist in exactly ONE place.**

### Why This Matters

Code duplication causes:
- **Inconsistency**: Different versions of the same instructions get out of sync
- **User confusion**: Users follow incomplete/outdated version
- **Maintenance burden**: Must update multiple places when things change
- **Trust erosion**: Users discover conflicting information
- **Premature execution**: Claude Code sees abbreviated instructions in SKILL.md and executes before reading full reference
- **Incomplete context**: Short checklists treated as "good enough", causing Claude to skip critical details in references
- **Behavioral issues**: Claude refuses to read reference files from top-level folders when partial info exists elsewhere

### How to Maintain Single Source of Truth

**SKILL.md:**
- ❌ No code blocks (no "Quick setup", no examples)
- ✅ Overview + navigation links only
- ✅ Links to references for all actual content

**extension-guide.md / source-guide.md:**
- ❌ No setup code (link to package-extension-prerequisites.md)
- ❌ No testing patterns (link to testing-patterns-*.md)
- ✅ Step-by-step implementation specific to the feature
- ✅ Links to references for universal patterns

**references/*.md:**
- ✅ Deep-dive content on specific topics
- ✅ Complete, self-contained examples
- ✅ Links to shared-references for universal patterns

**shared-references/*.md:**
- ✅ Universal patterns that apply to all R packages
- ✅ Content used by multiple skills
- ✅ The canonical source for general R package development

### When You're Tempted to Duplicate

**❌ "But users need a quick reference in SKILL.md!"**
→ ✅ Add a prominent link with clear description instead

**❌ "But this example would help here too!"**
→ ✅ Link to the reference that has the example

**❌ "But I need to show just this one setup step!"**
→ ✅ Link to the full setup guide, users need the complete sequence anyway

**❌ "But users should see use_claude_code() mentioned here!"**
→ ✅ Say "See package-extension-prerequisites.md" only—never show the actual command in SKILL.md
→ **Why:** Claude sees the command and executes it before reading full context

**❌ "But I'll mark it 'optional' so Claude knows it's not required!"**
→ ✅ Remove "optional" labels—Claude ignores them and executes anyway
→ **Why:** Real-world evidence shows Claude consistently disregards "optional" markers

**The test:** If you're pasting code from one file to another, STOP. Create or link to a reference instead.

---

## Claude Code Behavioral Patterns

### Key Findings from Real-World Usage

When designing skills, account for these observed Claude Code behaviors:

#### 1. Refuses to Read Top-Level References When Partial Info Exists
**Behavior:** When Claude sees abbreviated setup instructions or short checklists in SKILL.md or extension-guide.md, it may refuse to read the full reference file (e.g., package-extension-prerequisites.md) even when explicitly instructed to do so.

**Solution:**
- Remove ALL setup code from SKILL.md and extension-guide.md
- Only include "See [Extension Prerequisites](../shared-references/package-extension-prerequisites.md)" links
- Never provide partial/abbreviated setup instructions anywhere except package-extension-prerequisites.md

#### 2. Treats Short Checklists as "Good Enough"
**Behavior:** Claude may see a short checklist in a high-level document and consider it sufficient guidance, skipping detailed reference documentation.

**Solution:**
- Make SKILL.md purely navigational (overview + links only)
- No code blocks, no checklists, no abbreviated instructions
- All actual content lives in dedicated reference files

#### 3. Ignores "Optional" Labels
**Behavior:** Marking steps as "optional" or "recommended" has little effect—Claude tends to execute them regardless.

**Solution:**
- Only mark steps as "optional" if they truly don't matter
- For important-but-flexible steps, use "STRONGLY RECOMMENDED" instead
- Be explicit about consequences of skipping (e.g., "reduces development quality")

#### 4. Executes Setup Commands Prematurely
**Behavior:** If Claude sees specific commands (like `use_claude_code()` or repo cloning scripts) in SKILL.md or guides, it may execute them before reading full context from package-extension-prerequisites.md, missing critical ordering dependencies.

**Solution:**
- Centralize ALL setup commands exclusively in package-extension-prerequisites.md
- High-level documents should only reference the setup guide, never show commands
- Prevents Claude from executing out-of-order or without proper context

#### 5. Better at Running Commands Than Guiding Users
**Behavior:** Claude Code can run R commands directly via `Rscript -e` using the Bash tool, and should do so autonomously rather than asking users to run them.

**Solution:**
- Write "INSTRUCTIONS FOR CLAUDE: Run this via Bash tool" instead of "Show the user this command"
- Claude should execute, verify, and proceed—not hand off to user
- Improves user experience by reducing context switching

### Design Implications

These behavioral patterns inform our architectural decisions:

1. **Single source of truth** - Not just for maintenance, but to prevent Claude from fragmenting its attention
2. **Centralized setup** - Prevents premature execution and ensures proper sequencing
3. **Clear labels** - "Optional" is meaningless; be explicit about importance and consequences
4. **Autonomous execution** - Claude Code should run commands directly when possible, not delegate to user
5. **Minimal high-level docs** - SKILL.md and guides should be thin navigation layers, not content repositories

---

## File-by-File Implementation Guide

### 1. SKILL.md (Main Entry Point)

**Purpose:** User-facing entry point that introduces the skill and provides navigation.

**Required Sections:**

```markdown
---
name: add-[package]-[feature]
description: [One-line description for Claude Code skill selector]
---

# Add [Package] [Feature]

[Brief introduction paragraph]

## Two Development Contexts

This skill supports **two distinct development contexts**:

### 🆕 Extension Development (Default)
**Creating a new R package** that extends [package] with custom [features].

- ✅ Use this for: New packages, standalone [features], CRAN submissions
- 📦 Package detection: No `[package]` in DESCRIPTION's `Package:` field
- ⚠️ **Constraint**: Can only use exported functions (no `:::`)
- 📖 **Guide**: [Extension Development Guide](extension-guide.md)

### 🔧 Source Development (Advanced)
**Contributing directly to [package]** via pull requests.

- ✅ Use this for: Contributing to tidymodels/[package] repository
- 📦 Package detection: `Package: [package]` in DESCRIPTION
- ✨ **Benefit**: Can use internal functions and package infrastructure
- 📖 **Guide**: [Source Development Guide](source-guide.md)

**This main guide shows extension development patterns.** If you're contributing to [package] itself, see the [Source Development Guide](source-guide.md) for package-specific details.

---

## Quick Start

**Choose your context:**

- **Creating a new package?** → Follow this guide, then see [Extension Development Guide](extension-guide.md)
- **Contributing to [package]?** → Clone repository, then see [Source Development Guide](source-guide.md)

**Not sure which?** If you're in the `tidymodels/[package]` repository, use source development. Otherwise, use extension development.

---

## Overview

[What this skill provides...]

## Repository Access (Optional but Recommended)

**INSTRUCTIONS FOR CLAUDE:** Check if `repos/[package]/` exists in the current working directory. Use this to guide development:

**If `repos/[package]/` exists:**
- ✅ Use it as a reference throughout development
- Read source files (e.g., `repos/[package]/R/[example-file].R`) to study implementation patterns
- Read test files (e.g., `repos/[package]/tests/testthat/test-[example-file].R`) for testing patterns
- Reference these files when answering complex questions or solving problems
- Look at actual code structure, validation patterns, and edge case handling

**If `repos/[package]/` does NOT exist:**
- Suggest cloning the repository using the scripts in [Repository Access Guide](references/package-repository-access.md)
- This is **optional but strongly recommended** for high-quality development
- If the user declines, reference files using GitHub URLs:
  - Format: `https://github.com/tidymodels/[package]/blob/main/R/[file-name].R`
  - Example: https://github.com/tidymodels/[package]/blob/main/R/[example-file].R
  - This allows users to click through to see implementations

**When to use repository references:**
- Complex implementation questions (e.g., "How does [package] handle [specific pattern]?")
- Debugging issues (compare user's code to working implementation)
- Understanding patterns (study similar [features])
- Test design (see how [package] tests edge cases)
- Architecture decisions (understand internal structure)

See [Repository Access Guide](references/package-repository-access.md) for setup instructions.

## Quick Navigation

**Development Guides:**
- [Extension Development Guide](extension-guide.md) - Creating new packages that extend [package]
- [Source Development Guide](source-guide.md) - Contributing PRs to [package] itself

**Reference Files:**
- [List all reference/*.md files with descriptions]

**Shared References (Extension Development):**
- [Extension Prerequisites](../shared-references/package-extension-prerequisites.md)
- [Development Workflow](../shared-references/package-development-workflow.md)
- [Extension Requirements](../shared-references/package-extension-requirements.md) - Complete guide:
  - [Best Practices](../shared-references/package-extension-requirements.md#best-practices)
  - [Testing Patterns](../shared-references/package-extension-requirements.md#testing-requirements)
  - [Troubleshooting](../shared-references/package-extension-requirements.md#common-issues-solutions)
- [Roxygen Documentation](../shared-references/package-roxygen-documentation.md)
- [Package Imports](../shared-references/package-imports.md)

**Source Development Specific:**
- [Testing Patterns (Source)](testing-patterns-source.md)
- [Best Practices (Source)](best-practices-source.md)
- [Troubleshooting (Source)](troubleshooting-source.md)

## Prerequisites

**⚠️ IMPORTANT**: Before implementing [features], complete the extension prerequisites sequence:

👉 **[Extension Prerequisites Guide](../shared-references/package-extension-prerequisites.md)**

This guide includes critical steps like `use_claude_code()` (if available) that must run BEFORE adding dependencies. Following the complete sequence ensures proper package initialization and Claude Code integration.

After completing extension prerequisites, return here to implement your [feature].

## Development Workflow

[Link to shared-references/package-development-workflow.md - do NOT duplicate code here]

## Complete Example: [Primary Use Case]

[Full working example using EXTENSION patterns (with package:: prefix)]

### 1. [Component 1]
[Code example]

### 2. [Component 2]
[Code example]

[... continue with all required components]

## [Additional Sections]

[Feature-specific content organized logically]

## Package-Specific Patterns (Source Development)

If you're contributing to [package] itself, you have access to internal functions and conventions not available in extension development.

[Brief overview of source-specific patterns - link to source-guide.md for details]

---

## Next Steps

**For Extension Development (creating new packages):**

1. **Choose your context:** [Extension Development Guide](extension-guide.md)
2. [Additional steps...]

**For Source Development (contributing to [package]):**

1. **Start here:** [Source Development Guide](source-guide.md)
2. [Additional steps...]
```

**Key Principles:**
- Start with frontmatter for Claude Code skill registration
- Clearly distinguish extension vs source from the beginning
- Include Repository Access section with instructions for Claude to check `repos/[package]/`
- Provide complete examples using extension patterns (most users)
- Link extensively to other documents
- Keep main content focused on extension development
- Reference source guide for package-specific patterns
- **NEVER duplicate code across SKILL.md and reference files** - SKILL.md should only link to references, not repeat their content
- Prerequisites section should link to package-extension-prerequisites.md, NOT include abbreviated setup code
- Single source of truth: all setup instructions live in shared-references/package-extension-prerequisites.md

**Repository Access Pattern:**
- **Always include** a "Repository Access" section in SKILL.md after "Overview"
- Instructs Claude to check for `repos/[package]/` directory
- If present: Use local files as reference for complex questions
- If absent: Suggest cloning OR provide GitHub URLs as fallback
- This enables Claude to read actual implementations when available
- Benefits: Better code quality, real-world examples, edge case handling

---

### 2. extension-guide.md

**Purpose:** Step-by-step guide for creating new packages that extend tidymodels.

**Required Sections:**

```markdown
# Extension Development Guide: [Package] [Feature]

Complete guide for creating new packages that extend [package] with custom [features].

---

## When to Use This Guide

✅ **Use this guide if you are:**
- Creating a **new R package** that adds custom [features]
- Building on [package]'s foundation without modifying [package] itself
- Publishing [features] to CRAN or sharing privately
- Want to avoid tight coupling with [package] internals

❌ **Don't use this guide if you are:**
- Contributing a PR directly to the [package] package → Use [Source Development Guide](source-guide.md)
- Working inside the [package] repository → Use [Source Development Guide](source-guide.md)

---

## Prerequisites

### Quick Package Setup

See [Extension Prerequisites](../shared-references/package-extension-prerequisites.md) for complete details.

[Standard setup code block]

---

## Key Constraints for Extension Development

### ❌ Never Use Internal Functions

**Critical:** You CANNOT use functions accessed with `:::`.

[Examples of what NOT to do and alternatives]

### ✅ Only Use Exported Functions

Safe to use:
- `[package]::[function1]()`
- `[package]::[function2]()`
[List all key exported functions]

### ✅ Self-Contained Implementations

You must implement all logic yourself:

[Example of self-contained implementation]

---

## Step-by-Step Implementation

### Step 1: [First Major Step]
[Detailed guidance with code examples]

### Step 2: [Second Major Step]
[Detailed guidance with code examples]

[... continue with all steps]

---

## Complete Examples

### [Example 1]
[Full working example]

### [Example 2]
[Full working example]

---

## Common Patterns

[Common code patterns with examples]

---

## Development Workflow

See [Development Workflow](../shared-references/package-development-workflow.md) for complete details.

**Fast iteration cycle (run repeatedly):**
1. `devtools::document()` - Generate documentation
2. `devtools::load_all()` - Load your package
3. `devtools::test()` - Run tests

**Final validation (run once at end):**
4. `devtools::check()` - Full R CMD check

---

## Package Integration

[How to integrate into R package structure]

---

## Testing

See [Testing Patterns (Extension)](../shared-references/package-extension-requirements.md#testing-requirements) for comprehensive guide.

**Required test categories:**
[List essential test types]

---

## Best Practices

See [Best Practices (Extension)](../shared-references/package-extension-requirements.md#best-practices) for complete guide.

**Key principles:**
[List critical principles]

---

## Troubleshooting

See [Troubleshooting (Extension)](../shared-references/package-extension-requirements.md#common-issues-solutions) for complete guide.

**Common issues:**
[List common problems and solutions]

---

## Reference Documentation

### [Package] Types
- [Link to relevant references]

### Core Concepts
- [Link to core concept references]

### Shared References
- [Link to shared references]

---

## Next Steps

1. **Complete extension prerequisites** following [Extension Prerequisites](../shared-references/package-extension-prerequisites.md)
2. [Additional steps...]

---

## Getting Help

- Check [Troubleshooting Guide](../shared-references/package-extension-requirements.md#common-issues-solutions)
- Review existing examples in reference documentation
- Study the main [[package] SKILL.md](SKILL.md) for more details
- Search GitHub issues: https://github.com/tidymodels/[package]/issues
```

**Key Principles:**
- Focus exclusively on extension development
- Emphasize the "never use :::" constraint repeatedly
- Provide self-contained code examples
- Link to shared references extensively
- Show complete implementations, not fragments

---

### 3. source-guide.md

**Purpose:** Guide for contributing directly to the tidymodels package repository.

**Required Sections:**

```markdown
# Source Development Guide: Contributing to [Package]

Complete guide for contributing new [features] to the [package] package itself.

---

## When to Use This Guide

✅ **Use this guide if you are:**
- Contributing a PR directly to the [package] package
- Working inside the [package] repository
- Adding [features] that should be part of [package] core
- Modifying existing [package] [features]

❌ **Don't use this guide if you are:**
- Creating a new package that extends [package] → Use [Extension Development Guide](extension-guide.md)
- Building standalone [features] → Use [Extension Development Guide](extension-guide.md)

---

## Prerequisites

### Clone the [Package] Repository

```bash
# Clone from GitHub
git clone https://github.com/tidymodels/[package].git
cd [package]

# Create a feature branch
git checkout -b feature/add-[feature]-name
```

See [Repository Access](../shared-references/package-repository-access.md) for more details.

### Install Development Dependencies

```r
# Install [package] with all dependencies
devtools::install_dev_deps()

# Load the package for development
devtools::load_all()
```

---

## Understanding [Package]'s Architecture

### Package Organization

[Directory structure of the package]

### File Naming Conventions

**Source files must follow strict naming:**
[List naming conventions]

**Test files must match:**
[List test naming conventions]

---

## Working with Internal Functions

### ✅ You CAN Use Internal Functions

When developing [package] itself, internal functions are available:

[Examples of using internal functions]

### Common Internal Helpers

#### [Internal Helper 1]
[Description and example]

#### [Internal Helper 2]
[Description and example]

### Finding Internal Functions

[How to discover available internal functions]

See [Best Practices (Source)](best-practices-source.md) for complete guide to internal functions.

---

## Step-by-Step Implementation

[Detailed implementation steps specific to source development]

---

## Documentation Patterns

[Package-specific documentation patterns, templates, etc.]

---

## Using Internal Test Data

### Available Test Helpers

[List and describe internal test helpers]

See [Testing Patterns (Source)](testing-patterns-source.md) for complete list.

---

## Snapshot Testing

[How the package uses snapshot testing]

---

## Consistency with Existing [Features]

### Study Similar [Features]

Before implementing:
[What to study]

### Match Function Structure

[Expected structure pattern]

---

## Creating New Internal Helpers

### When to Create

[Guidelines for creating helpers]

### Naming and Documentation

[How to document internal helpers]

---

## Error Messages

[Package-specific error message patterns]

---

## PR Submission

### Before Submitting

[Checklist before PR]

### Creating the PR

[How to create and describe PR]

### Review Process

[What to expect in review]

See [Troubleshooting (Source)](troubleshooting-source.md) for common review feedback.

---

## Reference Documentation

### Source Development
- [Testing Patterns (Source)](testing-patterns-source.md)
- [Best Practices (Source)](best-practices-source.md)
- [Troubleshooting (Source)](troubleshooting-source.md)

[Additional reference links]

---

## Next Steps

1. **Clone [package] repository**
2. **Create feature branch**
3. **Implement your [feature]** following this guide
4. **Test thoroughly** using internal test data
5. **Run `devtools::check()`**
6. **Submit PR** to tidymodels/[package]

---

## Getting Help

- Check [Troubleshooting (Source)](troubleshooting-source.md)
- Study existing [features] in the repository
- Review [Best Practices (Source)](best-practices-source.md)
- Open an issue on GitHub for questions
- Tag maintainers in your PR
```

**Key Principles:**
- Focus exclusively on source development
- Emphasize access to internal functions
- Describe package-specific conventions
- Include git/PR workflow
- Link to source-specific reference docs

---

### 4. testing-patterns-source.md

**Purpose:** Package-specific testing patterns for source development.

**Content Structure:**

```markdown
# Testing Patterns: [Package] Source Development

This guide covers testing patterns when **developing [package] itself** (contributing PRs to the tidymodels/[package] repository).

**For extension development**, see: [Testing Patterns (Extension)](../shared-references/package-extension-requirements.md#testing-requirements)

---

## When to Use This Guide

✅ **Use this guide if:**
- You're in the `tidymodels/[package]` repository
- `DESCRIPTION` has `Package: [package]`
- You're contributing via PR

❌ **For extension development:**
- Use [Testing Patterns (Extension)](../shared-references/package-extension-requirements.md#testing-requirements)

---

## Key Differences from Extension Testing

| Aspect | Source Development | Extension Development |
|--------|-------------------|----------------------|
| Test data | Use internal helpers | Create own data |
| Test files | `tests/testthat/test-[prefix]-*.R` | `tests/testthat/test-*.R` |
| Snapshots | Extensive use | Optional |
| Internal functions | Can test directly | Cannot access |

---

## Internal Test Helpers

[List all internal test data helpers with examples]

---

## Test File Organization

[Package-specific test file naming and organization]

---

## Snapshot Testing

[How to use snapshot testing in this package]

---

## Testing Internal Functions

[How to test internal helper functions]

---

## Common Test Patterns

[Package-specific test patterns with examples]

---

## Required Test Coverage

[What tests are required for this package]

---

## Running Tests

[How to run tests during development]

---

## Examples

### Example 1: [Test Type 1]
[Complete test example]

### Example 2: [Test Type 2]
[Complete test example]

---

## Troubleshooting

[Common testing issues specific to source development]

---

## Cross-References

- [Best Practices (Source)](best-practices-source.md)
- [Troubleshooting (Source)](troubleshooting-source.md)
- [Testing Patterns (Extension)](../shared-references/package-extension-requirements.md#testing-requirements) - For universal patterns
```

**Key Principles:**
- Focus on package-specific testing
- Show use of internal test helpers
- Explain snapshot testing
- Provide complete examples
- Link to extension guide for universal patterns

---

### 5. best-practices-source.md

**Purpose:** Package-specific best practices and conventions for source development.

**Content Structure:**

```markdown
# Best Practices: [Package] Source Development

Best practices when **developing [package] itself** (contributing to tidymodels/[package]).

**For extension development**, see: [Best Practices (Extension)](../shared-references/package-extension-requirements.md#best-practices)

---

## When to Use This Guide

[Same context discrimination as other source files]

---

## Key Differences from Extension Development

| Aspect | Source Development | Extension Development |
|--------|-------------------|----------------------|
| Function access | Direct (no prefix) | Must use `package::` |
| Internal helpers | Can use freely | Must reimplement |
| File naming | Strict conventions | Flexible |
| Documentation | Uses templates | Self-contained |

---

## File Organization

[Package-specific file organization rules]

---

## Internal Function Usage

[When and how to use internal functions]

---

## Code Style

[Package-specific code style requirements]

---

## Documentation Patterns

[Package-specific documentation templates and patterns]

---

## Function Structure

[Expected function structure for this package]

---

## Error Messages

[Package-specific error message patterns]

---

## Creating Internal Helpers

[When and how to create new internal functions]

---

## Examples

### Example 1: [Pattern 1]
[Complete example]

### Example 2: [Pattern 2]
[Complete example]

---

## Universal Best Practices

See [Best Practices (Extension)](../shared-references/package-extension-requirements.md#best-practices) for practices that apply to both contexts:
- Using base pipe `|>` not `%>%`
- Prefer for-loops over `purrr::map()`
- Using `cli::cli_abort()` for errors
- [Other universal practices]

---

## Cross-References

- [Testing Patterns (Source)](testing-patterns-source.md)
- [Troubleshooting (Source)](troubleshooting-source.md)
- [Best Practices (Extension)](../shared-references/package-extension-requirements.md#best-practices)
```

---

### 6. troubleshooting-source.md

**Purpose:** Package-specific troubleshooting for source development.

**Content Structure:**

```markdown
# Troubleshooting: [Package] Source Development

Troubleshooting guide for **developing [package] itself** (contributing to tidymodels/[package]).

**For extension development**, see: [Troubleshooting (Extension)](../shared-references/package-extension-requirements.md#common-issues-solutions)

---

## When to Use This Guide

[Same context discrimination as other source files]

---

## Package-Specific Issues

### Issue 1: [Specific Problem]
**Problem:** [Description]
**Solution:** [How to fix]
**Example:**
```r
[Code example]
```

[Continue with all package-specific issues]

---

## Git and PR Issues

[Issues specific to PR workflow]

---

## Internal Function Issues

[Problems with internal function usage]

---

## Test Issues

[Testing problems specific to source development]

---

## Universal Issues

See [Troubleshooting (Extension)](../shared-references/package-extension-requirements.md#common-issues-solutions) for issues that apply to both contexts:
- "could not find function" → Run `devtools::load_all()`
- "object not found in namespace" → Add `@export`, run `devtools::document()`
- [Other universal issues]

---

## Getting Help

- Review [Best Practices (Source)](best-practices-source.md)
- Study existing [features] in the repository
- Check GitHub issues
- Ask in PR review

---

## Cross-References

- [Testing Patterns (Source)](testing-patterns-source.md)
- [Best Practices (Source)](best-practices-source.md)
- [Troubleshooting (Extension)](../shared-references/package-extension-requirements.md#common-issues-solutions)
```

---

### 7. references/*.md

**Purpose:** Deep-dive reference documentation on specific topics.

**Naming Pattern:** `[topic-name].md` (e.g., `metric-system.md`, `step-architecture.md`)

**Content Structure:**

```markdown
# [Topic Name]

[Comprehensive documentation on a specific topic]

> **Note for Source Development:** If you're contributing directly to the [package] package, you can use [internal features X, Y, Z]. See the [Source Development Guide](../source-guide.md) for details.

---

## Overview

[Topic introduction]

## [Section 1]

[Detailed content]

## [Section 2]

[Detailed content]

## Complete Examples

### Example 1: [Use Case 1]
[Full working example using EXTENSION patterns]

### Example 2: [Use Case 2]
[Full working example using EXTENSION patterns]

---

## Cross-References

- [Related reference doc 1]
- [Related reference doc 2]
- [Extension Guide](../extension-guide.md)
- [Source Guide](../source-guide.md)
```

**Key Principles:**
- Focus on one specific topic in depth
- Provide complete, self-contained examples
- Use extension patterns (package:: prefix) in examples
- Note when source development has alternatives
- Cross-reference related docs

---

### 8. Referencing Repository Files

**Purpose:** Skills can reference specific source files and test files from cloned tidymodels repositories to provide concrete implementation examples.

**Why This Matters:**

When developers have the corresponding tidymodels package cloned in `repos/` (e.g., `repos/yardstick/`, `repos/recipes/`), Claude can:
- Read actual implementation code for real-world examples
- Study test patterns from existing test files
- Understand internal architecture and conventions
- Provide more accurate, specific guidance

**Repository Access Setup:**

Skills should encourage developers to clone repositories via the shared reference:
- See [Repository Access](../shared-references/package-repository-access.md) for setup instructions
- This is **optional but strongly recommended** for creating high-quality skills
- Scripts are provided to clone repos into `repos/` directory

**How to Reference Repository Files:**

In your reference files, add references to specific implementation files using relative paths from the repository root:

**Example from `probability-metrics.md`:**

```markdown
**Canonical implementations in yardstick:**
- ROC-based metrics: `R/prob-roc_auc.R` (binary and multiclass)
- Precision-Recall: `R/prob-pr_auc.R`, `R/prob-average_precision.R`
- Probability scoring: `R/prob-brier_class.R` (Brier score), `R/prob-mn_log_loss.R` (multinomial log loss)

**Test patterns:**
- Binary probability metrics: `tests/testthat/test-prob-roc_auc.R`
- Multiclass metrics: `tests/testthat/test-prob-mn_log_loss.R`
```

**Example from `linear-predictor-survival-metrics.md`:**

```markdown
**Reference implementation:** `R/surv-royston.R` in yardstick repository
```

**When to Add Repository References:**

Add repository file references when:
1. **Introducing a category of features** (e.g., "Probability Metrics") - list canonical examples
2. **Showing implementation patterns** - point to similar implementations in the package
3. **Discussing test patterns** - reference test files that demonstrate edge cases
4. **Explaining architecture** - cite internal helper files or infrastructure

**Format Conventions:**

```markdown
**Source files:**
- Use format: `R/[file-name].R` (relative to repository root)
- Example: `R/prob-brier_class.R` (Brier score)
- Add brief description in parentheses

**Test files:**
- Use format: `tests/testthat/test-[file-name].R`
- Example: `tests/testthat/test-prob-mn_log_loss.R`
- Describe what test patterns it demonstrates

**Section placement:**
- Add near the top of reference files under "Overview" or in an "Examples" section
- Use headers like "Canonical implementations in [package]:", "Reference implementation:", or "Test patterns:"
```

**Example Pattern - Numeric Metrics:**

```markdown
## Overview

Numeric metrics evaluate continuous predictions against continuous truth values.

**Reference implementations in yardstick:**
- Simple metrics: `R/num-mae.R`, `R/num-rmse.R`, `R/num-mse.R`
- Parameterized metrics: `R/num-huber_loss.R` (has delta parameter)
- Complex metrics: `R/num-ccc.R` (correlation-based)

**Test patterns:**
- Basic tests: `tests/testthat/test-num-mae.R`
- Parameterized tests: `tests/testthat/test-num-huber_loss.R`
```

**Example Pattern - Recipe Steps:**

```markdown
## Overview

Recipe steps transform data during preprocessing.

**Reference implementations in recipes:**
- Modify-in-place: `R/center.R`, `R/normalize.R`
- Create new columns: `R/step_dummy.R`, `R/step_interact.R`
- Remove columns: `R/step_rm.R`, `R/step_zv.R`

**Test patterns:**
- Modification steps: `tests/testthat/test-step_center.R`
- Creation steps: `tests/testthat/test-step_dummy.R`
```

**Benefits for Claude Code:**

When repository files are referenced and the repos are cloned:
1. **Claude can read the actual implementation** using the Read tool
2. **Provides concrete examples** beyond generic patterns
3. **Shows real-world edge cases** and validation
4. **Reveals internal architecture** and conventions
5. **Improves accuracy** of generated code

**Integration with package-repository-access.md:**

The shared reference `package-repository-access.md` provides:
- Scripts to clone repositories (bash, PowerShell, Python)
- Setup instructions for `repos/` directory
- Troubleshooting for git installation and network issues
- Examples of how to use cloned repositories

Your skill should link to this file in SKILL.md and in the Prerequisites sections of guides.

**Implementation Checklist for New Skill:**

When creating a new skill:
- [ ] Identify 3-5 canonical implementation files in the source package
- [ ] Add references to these files in relevant reference/*.md files
- [ ] Add references to key test files that demonstrate patterns
- [ ] Ensure `package-repository-access.md` is linked in SKILL.md
- [ ] If adding a new package, update clone scripts (see Phase 5 checklist)

---

## Shared References (Universal)

These files live in `shared-references/` and apply to ALL skills:

### package-extension-requirements.md#testing-requirements
Universal testing patterns for extension developers (creating new packages).

### package-extension-requirements.md#best-practices
Universal best practices for extension developers.

### package-extension-requirements.md#common-issues-solutions
Universal troubleshooting for extension developers.

### package-extension-prerequisites.md
How to initialize an R package structure (used by all skills).

### package-development-workflow.md
The fast iteration cycle: document → load → test → check.

### package-roxygen-documentation.md
How to write roxygen2 documentation.

### package-imports.md
Managing package dependencies and imports.

### package-repository-access.md
How to clone tidymodels repositories (optional but recommended).

**Key Principle:** These files should never mention package-specific details. They provide universal guidance applicable across all tidymodels skills.

---

### ⚠️ IMPORTANT: Updating Shared Files

**When updating shared content, ONLY edit the source files in `shared-*` folders:**

**Shared reference files** (in `shared-references/`):
- `package-extension-requirements.md#best-practices`
- `package-development-workflow.md`
- `package-imports.md`
- `package-extension-prerequisites.md`
- `package-repository-access.md`
- `package-roxygen-documentation.md`
- `package-extension-requirements.md#testing-requirements`
- `package-extension-requirements.md#common-issues-solutions`

**Shared script files** (in `shared-references/scripts/`):
- `clone-tidymodels-repos.sh`
- `clone-tidymodels-repos.ps1`
- `clone-tidymodels-repos.py`
- `verify-setup.R`
- `README.md`

**❌ Do NOT edit these files in their copied locations:**
- `add-yardstick-metric/references/[shared reference files]`
- `add-yardstick-metric/references/scripts/[shared script files]`
- `add-recipe-step/references/[shared reference files]`
- `add-recipe-step/references/scripts/[shared script files]`

**✅ After editing any shared file, run:**
```bash
# From project root - runs both developers/ and users/ by default
./skill-development/build-verify.py

# Or specify a specific directory
./skill-development/build-verify.py developers/
./skill-development/build-verify.py users/
```

This script:
1. Copies the updated files from `shared-references/` and `shared-references/scripts/` to each skill's `references/` folder
2. Verifies all markdown links and file references are valid
3. Automatically skips workspace directories (those containing `-workspace`)

**Workflow:**
```
Edit shared-references/package-extension-prerequisites.md
    ↓
Run ./skill-development/build-verify.py
    ↓
Changes copied to all skills' references/ folders + verification runs
```

---

## Writing Style Guidelines

### Markdown Conventions

1. **Headers:**
   - Use `#` for main title
   - Use `##` for major sections
   - Use `###` for subsections
   - Use `####` sparingly for sub-subsections

2. **Code Blocks:**
   - Always specify language: ` ```r `, ` ```bash `
   - Include comments to explain non-obvious code
   - Show complete, runnable examples

3. **Lists:**
   - Use `-` for unordered lists
   - Use `1.` for ordered lists
   - Maintain consistent indentation

4. **Emphasis:**
   - Use `**bold**` for critical information
   - Use `*italic*` for emphasis
   - Use `**Critical:**`, `**Warning:**`, `**Note:**` for callouts

5. **Links:**
   - Use relative links: `[Text](../shared-references/file.md)`
   - Link section anchors: `[Text](file.md#section-name)`

6. **Tables:**
   - Use markdown tables for comparisons
   - Keep cells concise
   - Use `|` alignment when helpful

### Voice and Tone

- **Active voice:** "You create" not "A metric is created"
- **Direct:** "Use `function()`" not "One might use `function()`"
- **Encouraging:** "This lets you..." not "This prevents you from..."
- **Clear constraints:** Be explicit about what's not allowed

### Code Example Standards

1. **Complete, not fragments:**
   ```r
   # ✅ GOOD - Complete example
   mae_impl <- function(truth, estimate, case_weights = NULL) {
     errors <- abs(truth - estimate)
     if (is.null(case_weights)) {
       mean(errors)
     } else {
       weighted.mean(errors, w = case_weights)
     }
   }
   ```

2. **Show required vs optional:**
   - Comment which parameters are required
   - Show defaults explicitly
   - Demonstrate common variations

3. **Extension pattern by default:**
   - Use `package::function()` prefix in main examples
   - Note source alternatives in callout boxes
   - Keep extension examples self-contained

---

## Cross-Reference Patterns

### Within a Skill

```markdown
See [Source Development Guide](source-guide.md) for details.
See [Metric System](references/metric-system.md) for complete guide.
```

### To Shared References

```markdown
See [Extension Prerequisites](../shared-references/package-extension-prerequisites.md) for complete details.
See [Development Workflow](../shared-references/package-development-workflow.md) for the fast iteration cycle.
```

### To Other Skills

```markdown
See the [add-recipe-step skill](../add-recipe-step/SKILL.md) for preprocessing patterns.
```

### Bidirectional Cross-References

When you add a new skill, update related skills:
- Add link from related skill's SKILL.md to new skill
- Cross-reference in shared-references where appropriate

---

## Testing Your New Skill

### Before Considering It Complete

1. **File Checklist:**
   - [ ] SKILL.md with frontmatter
   - [ ] extension-guide.md
   - [ ] source-guide.md
   - [ ] testing-patterns-source.md
   - [ ] best-practices-source.md
   - [ ] troubleshooting-source.md
   - [ ] At least 3-5 references/*.md files
   - [ ] All files have proper cross-references

2. **Content Checklist:**
   - [ ] Clear extension vs source discrimination throughout
   - [ ] Complete examples (not code fragments)
   - [ ] Extension examples use `package::` prefix
   - [ ] Source examples show internal function usage
   - [ ] All cross-references work (no broken links)
   - [ ] Consistent voice and tone
   - [ ] No package-specific details in shared-references

3. **Quality Checklist:**
   - [ ] Examples are tested and work
   - [ ] Code follows tidymodels style
   - [ ] Documentation is clear and concise
   - [ ] Navigation is intuitive
   - [ ] Covers both happy path and edge cases
   - [ ] **Run `./skill-development/build-verify.py` with no errors**

### Manual Testing

1. **Read as extension developer:**
   - Can you follow SKILL.md → extension-guide.md flow?
   - Are examples self-contained?
   - Is the `:::` constraint clear?

2. **Read as source developer:**
   - Can you follow SKILL.md → source-guide.md flow?
   - Are internal functions documented?
   - Is PR workflow clear?

3. **Check cross-references:**
   - Click every link to verify it works
   - Ensure bidirectional references make sense
   - Verify shared-references links are correct

---

## Common Pitfalls to Avoid

### ❌ Don't:
1. **DUPLICATE CODE BETWEEN SKILL.md AND REFERENCES** - This is the #1 anti-pattern
   - ❌ NEVER include setup code blocks in SKILL.md (e.g., "Quick setup")
   - ❌ NEVER include abbreviated versions of reference content
   - ❌ NEVER include short checklists that Claude might treat as "good enough"
   - ✅ ALWAYS link to the full reference (e.g., package-extension-prerequisites.md)
   - **Why:** Creates inconsistency, users follow incomplete instructions, maintenance nightmare
   - **Example of the problem:** User follows "Quick setup" in SKILL.md, misses `use_claude_code()` from package-extension-prerequisites.md
   - **Real-world finding:** Claude was refusing to read reference files from top-level folders, treating short checklists as sufficient guidance instead of reading the full package-extension-prerequisites.md reference
2. **Include detailed setup instructions in high-level documents (SKILL.md, extension-guide.md)**
   - ❌ NEVER include `use_claude_code()` or repo cloning details in SKILL.md or guides
   - ❌ NEVER create short checklists that Claude might execute prematurely
   - ✅ ALWAYS centralize these instructions exclusively in package-extension-prerequisites.md
   - **Why:** Claude may execute setup steps before reading full reference documentation
   - **Real-world finding:** Claude would see short checklist in SKILL.md and execute it before reading package-extension-prerequisites.md, missing critical context and order dependencies
3. **Use "Optional" labels for steps that should actually be completed**
   - ❌ NEVER mark steps as "optional" if they're important
   - ✅ Be clear about what is truly optional vs. strongly recommended
   - **Why:** Claude consistently disregards "optional" labels and executes those steps anyway
   - **Real-world finding:** "Optional" monikers were effectively meaningless—Claude would do the work regardless
4. **Mix extension and source patterns in examples** - Choose one context per example
5. **Assume `:::` access in extension examples** - Always use exported functions
6. **Put package-specific content in shared-references** - Keep universal
7. **Show code fragments without context** - Provide complete examples
8. **Forget to update cross-references** - Keep links bidirectional
9. **Skip the context discrimination section** - Always clarify extension vs source
10. **Use generic error messages** - Be specific to the context
11. **Leave broken links** - Test all cross-references
12. **Commit changes without running build-verify.py** - Always build and verify before committing
   - ❌ NEVER commit skill changes without running `./skill-development/build-verify.py` first
   - ✅ ALWAYS run build-verify.py to ensure shared files are synced and links work
   - **Why:** Keeps all skills in sync, prevents broken links from reaching repository
   - **How:** Run `./skill-development/build-verify.py` from project root before every commit (runs both developers/ and users/ by default)

### ✅ Do:
1. **Use references as single source of truth** - SKILL.md links, references contain content
2. **Make SKILL.md purely navigational** - Overview + links, no duplicated code blocks
3. **Include Repository Access section in SKILL.md** - Instructs Claude to check `repos/[package]/` and use as reference
4. **Link to package-extension-prerequisites.md for ALL setup instructions** - Never abbreviate or duplicate
5. **Centralize setup commands exclusively in package-extension-prerequisites.md** - Prevents premature execution
6. **Write "INSTRUCTIONS FOR CLAUDE" for autonomous execution** - Claude should run commands via Bash tool
7. **Avoid "optional" labels that Claude ignores** - Be explicit about importance and consequences
8. **Force reference reading** - Only show "See [reference]" links, never partial content
9. **Start with SKILL.md structure from existing skills** - Copy, then adapt
10. **Test all code examples** - They should run as shown
11. **Link generously** - Help users navigate
12. **Be explicit about constraints** - Extension development has limits
13. **Provide both extension and source examples** - When patterns differ significantly
14. **Update related skills** - Add cross-references when appropriate
15. **Follow naming conventions** - Consistent with existing skills
16. **Include troubleshooting** - Anticipate common problems
17. **Run build-verify.py before committing** - Ensures files are synced and verified
   - Run `./skill-development/build-verify.py` after any skill changes (runs both developers/ and users/ by default)
   - Fix all errors before committing
   - This is CRITICAL for maintaining quality

---

## Implementation Checklist for New Skill

When creating a new skill (e.g., `add-parsnip-model`):

### Phase 1: Planning (1-2 hours)
- [ ] Identify target package (e.g., parsnip)
- [ ] Determine primary feature (e.g., adding model specifications)
- [ ] List 3-5 key reference topics
- [ ] Review existing package for patterns
- [ ] Identify internal functions (for source guide)

### Phase 2: Core Structure (3-4 hours)
- [ ] Create skill directory: `developers/add-[package]-[feature]/`
- [ ] Write SKILL.md from template
- [ ] Include "Repository Access" section in SKILL.md (after "Overview", before "Quick Navigation")
- [ ] Create extension-guide.md
- [ ] Create source-guide.md
- [ ] Add references/ directory

### Phase 3: Reference Documentation (4-6 hours)
- [ ] Write 3-5 reference/*.md files
- [ ] Ensure each has complete examples
- [ ] Test all code examples
- [ ] Add cross-references between references

### Phase 4: Source-Specific Guides (3-4 hours)
- [ ] Write testing-patterns-source.md
- [ ] Write best-practices-source.md
- [ ] Write troubleshooting-source.md
- [ ] Document internal functions
- [ ] Add test data helpers

### Phase 5: Cross-References (1-2 hours)

**⚠️ CRITICAL: If Your Skill References a New Repository**

If your skill guides users to clone a tidymodels repository that's not currently in the clone scripts (e.g., you're creating add-dials-parameter and dials isn't in the scripts yet):

**BEFORE running build-verify.py, add the repository to ALL clone scripts in `shared-references/scripts/`:**

1. **Clone scripts** - Add repository URL and update usage messages:
   - `clone-tidymodels-repos.sh` (Bash) - Update REPOS array and usage examples
   - `clone-tidymodels-repos.ps1` (PowerShell) - Update $Repos hashtable and usage examples
   - `clone-tidymodels-repos.py` (Python) - Update REPOS dict and usage examples

2. **verify-setup.R** - Add package detection:
   - Add package name to source detection check
   - Add package detection in Imports section
   - Add package to repos existence check
   - Add UUID constants for missing dependencies
   - Add package-specific dependency validation

3. **README.md** - Update documentation:
   - Update description to mention new package
   - Add examples in Quick Start sections
   - Update disk space requirements
   - Update directory structure example

4. **Test workflow** (optional but recommended):
   - Update `.github/workflows/test-clone-scripts.yml` to verify new package in "all" tests

**Why this matters:** build-verify.py copies `shared-references/scripts/*` to each skill's `references/scripts/`. If you run it before adding your new repository to the scripts, the copied scripts won't support your repository.

---

**⚠️ CRITICAL: Run `./skill-development/build-verify.py ../developers/` AFTER updating scripts**

This script copies shared reference files (package-extension-prerequisites.md, etc.) to each skill's references/ folder. You must reference these as **local files** not `../shared-references/`.

**Correct link patterns:**
- In SKILL.md: `[Extension Prerequisites](references/package-extension-prerequisites.md)`
- In references/*.md: `[Extension Prerequisites](package-extension-prerequisites.md)`

**NOT:**
- ❌ `../shared-references/package-extension-prerequisites.md`
- ❌ `../../shared-references/package-extension-prerequisites.md`

**Tasks:**
- [ ] **If new repository:** Update all clone scripts and verify-setup.R FIRST (see above)
- [ ] Run `./skill-development/build-verify.py ../developers/`
- [ ] Fix any shared reference links to use local paths
- [ ] Link all files within skill
- [ ] Update related skills (add cross-references)
- [ ] Verify all links work

### Phase 6: Review and Polish (2-3 hours)
- [ ] Read through as extension developer
- [ ] Read through as source developer
- [ ] Test all code examples
- [ ] Check for consistency
- [ ] Proofread for clarity
- [ ] **Run `./skill-development/build-verify.py` again and fix all errors**

### Phase 7: Update Website, Landing Pages, and Plugin (1-2 hours)

**Create .qmd wrappers:**
- [ ] Create `docs/developers/your-skill.qmd` (3 lines: logo + include)
- [ ] Create .qmd wrappers for skill-specific references in `docs/developers/references/`
- [ ] Update `docs/_quarto.yml` sidebar with skill section

**Update landing pages:**
- [ ] Add skill to `docs/developers/index.qmd` with logo and description
- [ ] Add skill to `docs/getting-started.qmd` in developer skills list
- [ ] Verify logo exists in `docs/assets/logos/`
- [ ] Check capitalization consistency across all files (e.g., "Add Dials Parameter" not "Add dials Parameter")

**Update marketplace plugin:**
- [ ] Add skill path to `.claude-plugin/marketplace.json` in `tidymodels-developers` skills array
- [ ] Update plugin description to mention new skill
- [ ] Bump version (MINOR version for new skill: 0.2.0 → 0.3.0)

**Verify:**
- [ ] Run `./skill-development/build-verify.py` - should report SUCCESS
- [ ] Test with `cd docs && quarto render` (optional but recommended)

**Total Time Estimate: 16-25 hours**

---

## Example: Planned Structure for add-parsnip-model

If we were to create an `add-parsnip-model` skill:

```
developers/add-parsnip-model/
├── SKILL.md                        # Entry point
├── extension-guide.md              # Creating new model packages
├── source-guide.md                 # Contributing to parsnip
├── testing-patterns-source.md      # Parsnip test patterns
├── best-practices-source.md        # Parsnip code conventions
├── troubleshooting-source.md       # Parsnip-specific issues
└── references/
    ├── model-specification.md      # set_model_engine(), set_dependency()
    ├── fit-predict-pattern.md      # fit.model_spec(), predict.model_fit()
    ├── engine-registration.md      # set_model_arg(), set_encoding()
    ├── parameter-translation.md    # Translating args to engine
    └── prediction-types.md         # numeric, class, prob, etc.
```

Key topics for parsnip:
- Model specification creation
- Engine registration
- Fit/predict pattern
- Parameter translation
- Multiple prediction types
- Engine-specific details

---

## Questions to Answer for Each New Skill

When planning a new skill, answer these questions:

1. **What is the target package?** (e.g., yardstick, recipes, parsnip, dials)

2. **What is the primary feature being extended?** (e.g., metrics, steps, models, parameters)

3. **What are the 3-5 most important concepts users need to understand?** (These become references/*.md)

4. **What internal functions exist in the package?** (Document in source guide)

5. **What test helpers are available?** (Document in testing-patterns-source.md)

6. **What are the package-specific naming conventions?** (Document in best-practices-source.md)

7. **What are the most common errors?** (Document in troubleshooting-source.md)

8. **What is a complete, minimal example?** (Show in SKILL.md and extension-guide.md)

9. **What makes this different from extension development?** (Explain in source-guide.md)

10. **What should users read next?** (Plan cross-references)

---

## Maintenance

### When to Update Skills

- **Package releases:** When tidymodels packages release new features
- **API changes:** When exported functions change
- **New patterns:** When best practices evolve
- **User feedback:** When users report confusion

### Updating Existing Skills

1. Update the relevant file(s)
2. Update cross-references if structure changed
3. Test code examples still work
4. Update "Last Updated" date in planning docs

### Version Information

Skills don't have version numbers themselves, but:
- Date stamps in planning docs track evolution
- Git history shows changes over time
- Skills reflect current state of tidymodels packages

---

## Skill Composition: Integration with usethis Claude Code Setup

### Overview

When users run `usethis::use_claude_code()` (available in usethis 3.2.1.9000+), it creates:
- `.claude/CLAUDE.md` - R package development instructions
- `.claude/settings.json` - Recommended permissions
- `.claude/skills/tidy-argument-checking/` - Patterns for validating function arguments
- `.claude/skills/tidy-deprecate-function/` - Best practices for deprecating functions

Tidymodels-dev skills can automatically incorporate these tidyverse patterns when they're present.

### Detection Pattern

Skills should check for the presence of usethis-created skills:

```markdown
# In your skill's guidance (e.g., extension-guide.md)

## Argument Validation

When implementing your [metric/step/model], validate arguments appropriately.

**Note:** If you set up Claude Code using `usethis::use_claude_code()`, the `tidy-argument-checking`
skill provides comprehensive patterns for argument validation. Those patterns apply to general R package
development and complement the tidymodels-specific guidance here.

[Your tidymodels-specific argument validation patterns...]
```

### When to Reference Tidy Skills

**Do reference tidy-* skills for:**
- General R package practices (argument checking, deprecation)
- Code style and conventions
- Error message patterns
- Testing strategies that apply to all R packages

**Don't duplicate tidy-* skills for:**
- Domain-specific patterns (metric implementation, recipe prep/bake)
- Package-specific APIs (yardstick classes, recipes infrastructure)
- Tidymodels ecosystem conventions

### Implementation Approach

**In SKILL.md or extension-guide.md:**
```markdown
## Prerequisites

### Setup Claude Code (Recommended)

If using Claude Code for development, see [Extension Prerequisites](../shared-references/package-extension-prerequisites.md)
for instructions on running `usethis::use_claude_code()`.

This provides access to tidyverse team's general R package development patterns which complement
the tidymodels-specific guidance in this skill.
```

**When discussing general R topics:**
```markdown
## Error Handling

[Your tidymodels-specific error handling patterns]

**For general argument validation patterns**, see the `tidy-argument-checking` skill if you
ran `usethis::use_claude_code()`.
```

### Reading Tidy Skills at Runtime

When a tidymodels-dev skill is invoked, Claude Code should:

1. **Check for `.claude/CLAUDE.md`** - If it exists, read it first to understand the project's R package development context
2. **Detect `.claude/skills/tidy-*` directories** - Look for tidyverse team skills
3. **Read relevant tidy skills** when they apply to the current task
4. **Incorporate patterns** for general R package development
5. **Keep tidymodels-dev skills focused** on domain-specific guidance

**Automatic Detection Pattern:**

When a skill is invoked:
```markdown
# Skill should check and read if present
- If .claude/CLAUDE.md exists → Read it for general R package development context
- If .claude/skills/tidy-argument-checking/ exists → Available for argument validation guidance
- If .claude/skills/tidy-deprecate-function/ exists → Available for deprecation guidance
```

**Example scenario:**
- User asks: "How should I validate arguments in my yardstick metric?"
- **First:** Check if `.claude/CLAUDE.md` exists and read it for general R context
- **Tidymodels skill provides:** Metric-specific validation (truth/estimate columns, case weights, etc.)
- **Tidy skill provides:** General R argument checking patterns (type checking, NULL handling, etc.)
- **Result:** Complete guidance combining both domain-specific and general best practices

### Benefits of This Approach

1. **Avoid duplication**: General R patterns stay in tidy-* skills
2. **Stay focused**: Tidymodels skills focus on package-specific guidance
3. **Consistency**: Users get tidyverse patterns across all their R development
4. **Maintainability**: Updates to tidy-* skills benefit all users automatically

### Skill Invocation Best Practices

When a tidymodels-dev skill guides a user through extension prerequisites that includes `use_claude_code()`:

**After `use_claude_code()` runs:**

1. **Use `AskUserQuestion` to prompt the user:**
   ```
   Question: "The extension prerequisites created `.claude/CLAUDE.md` with R package development
              instructions. Should I read this file now to incorporate tidyverse
              development patterns?"

   Options:
   - "Yes, read CLAUDE.md now (Recommended)"
   - "Skip for now"
   ```

2. **If user chooses "Yes":**
   - Read `.claude/CLAUDE.md` using the Read tool
   - Incorporate tidyverse patterns (testing, documentation, code style, etc.)
   - Continue with tidymodels-specific guidance

3. **If user chooses "Skip":**
   - Continue with tidymodels-specific guidance only
   - Tidymodels skills still provide complete, working guidance

4. **Proceed with domain-specific implementation:**
   - Focus on tidymodels patterns (metrics, recipe steps, etc.)
   - Apply any general R practices learned from CLAUDE.md

**Example workflow:**
```
User runs setup code with use_claude_code()
→ Claude uses AskUserQuestion: "Should I read CLAUDE.md?"
→ User: "Yes, read CLAUDE.md now"
→ Claude reads .claude/CLAUDE.md
→ Claude learns: use base pipe |>, air format ., expect_snapshot(), etc.
→ Claude proceeds with yardstick metric implementation using those patterns
```

### Fallback Behavior

If tidy-* skills are not present:
- Tidymodels-dev skills still provide complete, working guidance
- No functionality is lost
- Users just don't get the additional general R package patterns

### Documentation in package-extension-prerequisites.md

The `package-extension-prerequisites.md` file now includes a section on `use_claude_code()`:
- Explains what it creates
- Shows version check pattern
- Lists benefits including skill composition
- Makes it clear it's optional but recommended

---

## Lessons Learned from Skill Evaluations

This section documents key insights from quantitative evaluations of existing skills, based on benchmarks of `add-recipe-step`, `add-dials-parameter` (developer skills), and `tabular-data-ml` (user skill).

**Last Updated:** 2026-04-02 (added add-dials-parameter findings)

### Performance Trade-offs are Expected and Acceptable

**Finding:** Skills consistently use more tokens than baseline but deliver higher quality.

**Evidence:**
- `add-recipe-step` iteration-2: +18.9% tokens, but 20% faster execution and 33% fewer files
- `tabular-data-ml` iteration-1: +18k tokens per eval (+67%), but 56.4 percentage point improvement in pass rate (37.4% → 93.8%)

**Implication for Skill Design:**
- ✅ **Prioritize quality over token efficiency**
- ✅ Design for comprehensive, correct outputs rather than minimal token usage
- ✅ The token cost is justified by improved correctness, consistency, and completeness
- ⚠️ But avoid unnecessary verbosity - aim for concise, complete guidance

### Context Detection Works When Designed Properly

**Finding:** Skills can reliably detect development contexts with 100% accuracy.

**Evidence:**
- `add-recipe-step`: 6/6 tests correctly identified extension vs source development
- Prompt signals like "for my package" vs "I'm in the tidymodels/recipes repo" were sufficient

**Implication for Skill Design:**
- ✅ **Design clear context discrimination early**
- ✅ Use prompt signals (package names, repository mentions, PR language)
- ✅ Provide different guidance based on context (recipes:: prefix vs internal functions)
- ✅ Test both contexts in evaluations to verify accuracy

### Critical Behaviors Must Be Enforced

**Finding:** Skills can teach non-negotiable best practices that baseline behavior violates.

**Evidence:**
- `tabular-data-ml` test set protection: 100% compliance with skill vs 0% without
- Eval 3 specifically tested refusing premature test set evaluation
- With skill: Explicitly refused and explained why
- Without skill: Immediately provided code that compromises evaluation validity

**Implication for Skill Design:**
- ✅ **Identify critical "must do" and "must not do" behaviors**
- ✅ Build refusal patterns into skills when appropriate (e.g., "I cannot evaluate on test set yet")
- ✅ Include explanations for why certain practices matter
- ✅ Test these critical behaviors explicitly in evaluations

### File Discipline Should Be De-Prioritized Relative to Code Quality

**Finding:** File discipline is common but LESS CRITICAL than code correctness. Over-emphasis can backfire and confuse models.

**Evidence from add-yardstick-metric iterations:**
- **Iteration-1 (baseline):** 29% file discipline pass rate, created 39 total files
  - Models created documentation files (IMPLEMENTATION_SUMMARY.md, example_usage.R)
  - But code quality was reasonable with tidymodels standards
- **Iteration-2 (with heavy visual emphasis):** 14% file discipline pass rate, created 57 total files (-15pp REGRESSION)
  - Added dramatic visual warnings: "🛑 STOP! STOP! STOP! 🛑", "COUNT YOUR FILES BEFORE SAVING"
  - Added concrete examples: "File 1, File 2, STOP"
  - **Result:** WORSE behavior - more documentation files, Eval 7 completely broke (created test docs instead of implementation)
  - Heavy emphasis confused the model and degraded code quality
- **Iteration-3 (de-prioritized file discipline):** 84.4% overall pass rate, created 17 total files (dramatic improvement)
  - **Removed** visual emphasis, concrete examples, "COUNT YOUR FILES" language
  - **Moved** file discipline section to END of skill
  - **Kept** simple, concise guidance about what files to create
  - **Prioritized** code standards (use internal helpers, include @examples, prefix usage)
  - **Result:** File discipline AND code quality both improved

**Evidence from add-dials-parameter:**
- Similar pattern: Strong visual warnings helped (0% → 71%)
- But incremental improvement plateaued (71% → 85%)
- Remaining failures were edge cases, not lack of emphasis

**Critical Lesson: Visual Emphasis Can Backfire**

The add-yardstick-metric iteration-2 regression demonstrates that **over-emphasizing file discipline can harm code quality:**
- Models may focus on "not creating files" rather than "creating correct implementations"
- Dramatic warnings can confuse rather than clarify
- Examples showing "wrong" patterns may be interpreted as instructions
- Critical behavior tests may break completely when file discipline dominates guidance

**What Works (Simple Approach):**

1. **Simple, Concise Guidance** (Most Effective for Code-Focused Skills)
   ```
   Extension development: R/[name].R, tests/testthat/test-[name].R, README.md (if needed)
   Source development: R/[name].R, tests/testthat/test-[name].R
   ```
   - No visual drama, just clear statement
   - Placed at END of skill, not beginning
   - Let code standards take priority

2. **Explicit Prohibited File Lists** (Still Useful)
   - List 15-20 specific files that should NOT be created
   - No dramatic emphasis, just factual list
   - Group by category (documentation, examples, changelogs)

3. **Content Mapping Tables** (Helpful)
   ```
   | Content Type | ❌ Wrong | ✅ Correct |
   | Examples | example_usage.R | roxygen @examples |
   | Notes | IMPLEMENTATION_NOTES.txt | roxygen @details |
   ```
   - Shows where content belongs without drama

**What Doesn't Work or Backfires:**
- ❌ Heavy visual impact (separators, emojis, ALL CAPS) - can confuse models
- ❌ "COUNT YOUR FILES" or "File 1, File 2, STOP" language - creates rigidity that breaks understanding
- ❌ Concrete examples of wrong patterns - may be interpreted as instructions
- ❌ Placing file discipline at START of skill - prioritizes wrong concern
- ❌ Pre-flight checklists for file discipline - forces model to think about files before understanding task

**Context Matters:**
- **Skills focused on code correctness** (yardstick, recipes): De-prioritize file discipline
  - Code standards are more important than file counts
  - Models need to focus on correct implementations first
  - Simple guidance at end of skill is sufficient
- **Skills focused on project structure** (dials): Moderate emphasis acceptable
  - File creation is more central to the task
  - Visual warnings may help if not overdone

**Implication for Skill Design:**
- ✅ **Prioritize code correctness over file discipline**
- ✅ **Place file discipline guidance at END** of skill documentation
- ✅ **Use simple, concise language** without visual drama
- ✅ **Focus skill emphasis on code standards:** use internal helpers, include @examples, correct prefix usage
- ✅ **List prohibited files factually** without dramatic emphasis
- ⚠️ **Accept that some extra files will be created** - this is less important than correct code
- ❌ **Avoid heavy visual emphasis** that can confuse models
- ❌ **Avoid concrete wrong examples** that may be misinterpreted
- ❌ **Don't front-load file discipline** in skill structure

**Recommended file limits:**
```
Extension development: 2-3 files (R file, test file, optional README)
Source development: 2 files (R file, test file)
```
Accept 75-85% compliance as success - focus energy on code quality instead.

### Pattern-Specific Instructions Can Achieve 100% Success

**Finding:** Complex patterns that completely fail without guidance can achieve 100% success with detailed, annotated examples.

**Evidence from add-dials-parameter:**
- **Qualitative parameters (companion vectors):** 0% → 100%
  - Iteration-1: No evals created companion `values_*` vectors or used `@rdname`
  - Iteration-2: Both qualitative evals (2/2) created vectors with `@rdname` correctly
  - **Key change:** Added detailed "Pattern 4" with step-by-step breakdown and checklist

- **Custom finalization (range_get/range_set):** 0% → 100%
  - Iteration-1: No evals used `dials::range_get()` and `dials::range_set()` correctly
  - Iteration-2: Both finalization evals (2/2) used range manipulation correctly
  - **Key change:** Added annotated step-by-step example with STEP 1-2E labels

**What Made the Difference:**

1. **Annotated Examples with Labels**
   ```r
   # STEP 1: Create the parameter function
   num_genes <- function(...) {

   # STEP 2: Create the custom finalize function
   get_num_genes <- function(object, x) {
     # STEP 2A: Calculate the new bound based on data
     # STEP 2B: Ensure bound is valid
     # STEP 2C: Get the current range from the parameter
     bounds <- dials::range_get(object)
     # STEP 2D: Update the upper bound
     # STEP 2E: Set the new range and return
   ```
   - Breaking complex patterns into numbered steps
   - Inline comments explaining each sub-step
   - Shows the complete flow from start to finish

2. **Verification Checklists**
   ```
   Before completing a qualitative parameter, verify:
   - [ ] Created parameter function with dials::new_qual_param()
   - [ ] Created companion values_* vector
   - [ ] Used @rdname to group them
   - [ ] Added @export to BOTH
   ```
   - Converts implicit requirements into explicit checks
   - Easy to verify compliance

3. **"Key Components Explained" Sections**
   - Separate explanation of what each piece does
   - Why each component is required
   - What happens if you skip it

4. **"Common Mistakes" Lists**
   - Shows anti-patterns explicitly
   - Prevents predictable errors
   - Learned from actual failures

**Implication for Skill Design:**
- ✅ **Identify complex patterns that users struggle with** (analyze failure modes)
- ✅ **Create detailed, annotated examples** with step-by-step labels
- ✅ **Add verification checklists** for multi-part patterns
- ✅ **Explain each component separately** before showing them together
- ✅ **Document common mistakes** based on actual failures
- ✅ **Expect near-perfect success** when patterns are taught properly
- ⚠️ **Don't over-annotate simple patterns** (save detail for genuinely complex cases)

**Pattern Complexity Tiers:**
- **Simple patterns:** Brief example sufficient (e.g., basic parameter creation)
- **Moderate patterns:** Complete example with explanatory comments
- **Complex patterns:** Annotated with STEP labels, separate component explanations, checklists
  - Examples: Companion vectors with @rdname, custom finalization, S3 method sets

### Consistency is More Valuable Than Speed

**Finding:** Skills provide more consistent behavior with lower variance.

**Evidence:**
- `add-recipe-step` without skill: Token usage stddev 18,382 (high variance)
- `add-recipe-step` with skill: Token usage stddev 7,366 (low variance, 60% more consistent)
- Baseline struggled on some tasks (eval-3: 18 files including debug attempts)

**Implication for Skill Design:**
- ✅ **Design for predictable, consistent outputs**
- ✅ Provide clear structure that works across different task complexities
- ✅ Consistency is worth some performance cost
- ✅ Users benefit from knowing what to expect

### Simple Tasks May Not Need Extensive Guidance

**Finding:** Skills show biggest benefits on moderate complexity tasks; simple tasks may be over-served.

**Evidence:**
- `add-recipe-step` row-operation tests (simple): +86% time with skill in iteration-1
- `add-recipe-step` modify-in-place tests (moderate): -14% to -21% time with skill
- Simple tasks may need streamlined guidance

**Implication for Skill Design:**
- ⚠️ **Consider task complexity when designing guidance depth**
- ✅ Provide complete guidance but avoid over-explanation for straightforward tasks
- ✅ Focus extensive guidance on edge cases, common errors, and complex patterns
- ⚠️ Don't assume simpler = less valuable; simple tasks still benefit from correct patterns

### Documentation Quality Matters More Than Quantity

**Finding:** Skills that produce comprehensive reference materials have higher value.

**Evidence:**
- `add-recipe-step` with skill: Consistent README files, implementation guides, PR checklists
- `tabular-data-ml` with skill: Proper explanations of why practices matter (test set protection, temporal ordering)
- Documentation helps users understand not just what to do, but why

**Implication for Skill Design:**
- ✅ **Include clear explanations of key concepts**
- ✅ Document design decisions and trade-offs
- ✅ Provide working examples with context
- ✅ For source development: Include PR submission guidance
- ⚠️ But respect file limits - put comprehensive docs in fewer files, not more files

### Skills Should Be Designed for Iteration

**Finding:** Skills improve significantly through evaluation and optimization cycles.

**Evidence:**
- `add-recipe-step` iteration-1 → iteration-2: Token gap reduced from +39% to +19%, execution time improved from +9% to -20%
- Specific optimizations (file discipline, case weight logic) had measurable impact
- Evaluation identified specific areas for improvement

**Implication for Skill Design:**
- ✅ **Plan for multiple evaluation cycles**
- ✅ Start with comprehensive guidance, then optimize
- ✅ Use quantitative evaluations to identify improvement areas
- ✅ Time budget: 14-22 hours initial creation + 4-8 hours per optimization iteration
- ✅ Don't over-optimize in first iteration - ship and learn

### Best Practices Adherence Has Measurable Impact

**Finding:** Skills significantly improve adherence to established best practices.

**Evidence:**
- `tabular-data-ml` pass rate: 93.8% with skill vs 37.4% without (56.4pp improvement)
- Specific improvements: Seed setting, cross-validation strategy, proper resampling, feature engineering
- Time series awareness: 100% pass rate with skill vs 17% without

**Implication for Skill Design:**
- ✅ **Focus on teaching specific, measurable best practices**
- ✅ Identify the practices that are commonly missed without guidance
- ✅ Make best practices explicit in skill content
- ✅ Include test cases that specifically verify best practice adherence

### Evaluation Design Recommendations

Based on lessons learned, structure evaluations to measure:

1. **Context Detection** (Critical)
   - Include equal split between extension and source development (for developer skills)
   - Use clear prompt signals
   - Verify appropriate code patterns (prefix usage, internal functions)

2. **Critical Behaviors** (Critical)
   - Include at least one test that specifically checks non-negotiable practices
   - Test refusal patterns when appropriate
   - Verify explanations are provided

3. **Code Quality** (Important)
   - Verify complete implementations (all required components)
   - Check pattern adherence (three-function pattern, S3 methods, etc.)
   - Validate edge case handling

4. **File Discipline** (Important)
   - Count files created
   - Verify only necessary files are produced
   - Check that README is focused and useful

5. **Performance** (Monitor, don't over-optimize)
   - Track tokens and time
   - Look for extreme outliers
   - Accept reasonable trade-offs for quality

6. **Consistency** (Valuable)
   - Run multiple iterations of same test
   - Measure variance in outputs
   - Lower variance indicates more reliable skill

### Summary: Design Principles from Evaluations

1. **Quality > Speed**: Skills should prioritize correctness and completeness
2. **Consistency > Brevity**: Predictable behavior is worth some token cost
3. **Critical Behaviors**: Identify and enforce non-negotiable practices
4. **Code Quality > File Discipline**: Prioritize code correctness over file counts; de-emphasize file discipline to avoid confusing models
5. **Context Detection**: Design for 100% accuracy in distinguishing contexts
6. **Iterative Improvement**: Plan for evaluation → optimization cycles
7. **Clear Explanations**: Document why, not just what
8. **Measurable Impact**: Focus on best practices that baseline behavior misses

---

## Advanced Topics: Evaluation Design and Iteration Methodology

This section documents advanced lessons from multi-iteration skill optimization, particularly from the `add-parsnip-engine` skill development (iterations 1-3).

**Last Updated:** 2026-04-03 (based on add-parsnip-engine analysis)

### The Paradox of Helpful Guidance

**Core Finding:** Adding more "helpful" guidance can make performance WORSE, not better.

**The Paradox:**
- **Intuition says:** More detail → Better understanding → Better performance
- **Reality shows:** More detail → More tokens → Slower execution → Potential confusion

**Evidence from add-parsnip-engine:**

| Iteration | Multi-Mode Token Gap | Simple Case Performance | Outcome |
|-----------|---------------------|------------------------|---------|
| Iteration-1 | +36% | Baseline | Reasonable |
| Iteration-2 | +93% | +48% slower | **REGRESSION** |
| Iteration-3 | +67% | +4% slower | Improved |

**What Happened:**
- **Iteration-2** added a 180-line "Multi-Mode Development Checklist" to help with complex engines
- **Result:** 93% token overhead and made SIMPLE engines 48% slower
- **Iteration-3** removed verbose checklist, replaced with 2-sentence pattern
- **Result:** Recovered performance partially (67% token gap, 4% slower on simple)

**Key Lesson: Constraining vs Expanding Guidance**

**Expanding guidance** (what we did in iteration-2):
- Long checklists that models read completely
- Detailed debug procedures
- Comprehensive "what to do when X happens" sections
- **Effect:** Forces model to read everything before acting

**Constraining guidance** (what worked in iteration-3):
- Concise patterns: "Register each mode separately and completely..."
- Clear decision points: "Simple engine? Use streamlined approach"
- Trust the model to apply patterns without exhaustive enumeration
- **Effect:** Model gets to the right pattern faster

**Implication for Skill Design:**
- ✅ **Prefer concise patterns over verbose checklists**
- ✅ **Trust the model to generalize from examples**
- ✅ **Use routing logic for complexity tiers** (simple vs complex)
- ✅ **Remove "helpful" sections that become token bloat**
- ⚠️ **More words ≠ better understanding**

### Level 1 vs Level 2 Evaluation Design

**Critical Gap Discovered:** Structural checks don't verify functional correctness.

**Level 1: Structural Evaluation** (What we implemented)
- Checks file existence and naming
- Verifies code patterns exist (e.g., `register_engine`, `set_fit`, `set_pred`)
- Counts files created
- Searches for specific function calls
- **Weakness:** Can pass with broken implementations

**Level 2: Functional Evaluation** (What we need)
- Runs the generated code
- Tests predictions on actual data
- Verifies engines integrate with parsnip workflows
- Checks error handling behavior
- **Strength:** Verifies code actually works

**Evidence from add-parsnip-engine iteration-3:**
- All evals passed structural checks (mode registration, engine functions present)
- Spot-check of eval-3 revealed: Complete file, but predictions likely incorrect
- **Problem:** Can have all required code patterns but wrong implementations

**Why This Matters:**

**Level 1 is sufficient for:**
- File discipline (did they create too many files?)
- Pattern adherence (did they use the three-function pattern?)
- Context detection (extension vs source)
- Basic structure (did they create the required components?)

**Level 1 is insufficient for:**
- Algorithm correctness (does the metric calculate the right value?)
- Integration (does the engine work with parsnip workflows?)
- Edge cases (what happens with missing data, extreme values?)
- Functional behavior (does it actually do what it claims?)

**Implication for Skill Design:**
- ✅ **Level 1 is good for initial development** (fast, catches structural issues)
- ✅ **Level 2 is essential for validation** (slower, but confirms correctness)
- ✅ **Use Level 1 for iteration speed** (structural fixes)
- ✅ **Use Level 2 before considering skill "done"** (functional verification)
- ⚠️ **Don't confuse "passes checks" with "works correctly"**

**Practical Recommendation:**

```
Phase 1: Develop with Level 1 evaluation
- Fast iteration cycles
- Structural correctness
- Pattern adherence
- 3-5 iterations to optimize guidance

Phase 2: Validate with Level 2 evaluation
- Run generated code on test data
- Verify functional correctness
- Test integration with package ecosystem
- 1-2 iterations to fix functional issues discovered
```

### Iteration Methodology: When to Stop

**Question:** How many iterations are enough?

**Evidence-Based Answer:** Stop when you hit diminishing returns or persistent patterns.

**From add-parsnip-engine:**

| Metric | Iteration-1 → 2 | Iteration-2 → 3 |
|--------|----------------|----------------|
| Multi-mode token gap | +36% → +93% | +93% → +67% |
| Simple case speed | Baseline → +48% | +48% → +4% |
| File discipline | Not measured | 5-10 files (target: 2-3) |

**Observations:**
1. **Iteration-2 was a regression** - made things worse
2. **Iteration-3 recovered partially** - but didn't fully return to iteration-1 performance
3. **File discipline didn't improve** despite explicit guidance (10-16 → 5-10 files)

**When to Stop Iterating:**

**Stop if you see:**
- ✅ **3+ iterations without file discipline improvement** - guidance approach isn't working
- ✅ **Regression followed by partial recovery** - you've found the optimum
- ✅ **Token/time trade-offs stabilize** - additional changes have minimal impact
- ✅ **Persistent behaviors despite guidance** - structural problem, not guidance problem

**Continue iterating if:**
- 📈 **Clear improvement trajectory** - each iteration measurably better
- 📈 **New failure modes discovered** - guidance can address them
- 📈 **Low-hanging fruit remains** - obvious improvements not yet tried
- 📈 **<3 iterations completed** - haven't explored enough

**From add-parsnip-engine, we learned:**
- File discipline guidance (prohibited lists, consolidation steps) didn't improve compliance
- **After 3 iterations:** Files went from 10-16 → 5-10, but target is 2-3
- **Conclusion:** File discipline improvements require different approach (not more guidance)

**Alternative Strategies After Persistent Failures:**

When guidance fails after 3+ iterations:

1. **Accept the behavior** if code quality is good
   - Example: 5-10 files instead of 2-3 is acceptable if code is correct
   - File discipline is lower priority than functional correctness

2. **Change evaluation approach** if checks are flawed
   - Example: Pattern matching gives false positives
   - Solution: Update grading config, not skill

3. **Simplify guidance** if verbosity is the problem
   - Example: 180-line checklist → 2-sentence pattern
   - Solution: Remove "helpful" sections that cause token bloat

4. **Add routing logic** if complexity varies widely
   - Example: Simple vs complex engine detection
   - Solution: Guide model to assess complexity first, then choose approach

5. **Move to Level 2 evaluation** if structure passes but function fails
   - Example: Code exists but doesn't work
   - Solution: Run functional tests instead of just structural checks

### Complexity-Based Routing Pattern

**Problem:** Single guidance approach doesn't work for both simple and complex cases.

**Solution:** Teach the skill to assess complexity first, then route to appropriate guidance.

**From add-parsnip-engine iteration-3:**

```markdown
### Simple Engine?
- Single mode, formula/matrix interface, 1-3 parameters
→ Use streamlined approach: 2 files, 15-30 lines, NO extra docs

### Complex Engine?
- Multi-mode, matrix with encoding, survival
→ Reference detailed guides, still 2-3 files max
```

**Why This Works:**
- **Simple engines** don't need 180-line checklists - just create the basic structure
- **Complex engines** need detailed patterns for multi-mode, encoding, survival
- **Routing upfront** prevents over-engineering of simple cases

**Evidence:**
- Iteration-2 (no routing): Simple Spark engine +48% slower
- Iteration-3 (with routing): Simple Spark engine +4% slower (recovered)

**Pattern Structure:**

1. **Assessment criteria** - How to determine complexity
2. **Decision point** - Simple vs complex determination
3. **Streamlined path** - Minimal guidance for simple cases
4. **Detailed path** - Comprehensive guidance for complex cases
5. **File constraints** - Same limits regardless of complexity

**Implication for Skill Design:**
- ✅ **Add complexity routing when skill spans wide range**
- ✅ **Place routing at TOP of implementation section**
- ✅ **Make criteria objective** (countable features, not subjective)
- ✅ **Keep file limits consistent** across complexity tiers
- ✅ **Simple path should be truly minimal** - trust the model

### Token Budget Awareness

**Problem:** Skills can create massive token overhead that slows execution.

**From add-parsnip-engine:**
- Simple engines without skill: ~50k tokens
- Complex engines without skill: ~50k tokens
- With skill iteration-2: +93% tokens (multi-mode), +48% time (simple)

**Solution: Explicit Token Budgets**

```markdown
### Token Budget Awareness
Target token usage by complexity:
- Simple engines: <50,000 tokens
- Complex engines: <70,000 tokens
- Very complex: <80,000 tokens

If exceeding budget: simplify guidance, remove verbose sections
```

**Why This Matters:**
- Token usage directly impacts execution time
- Models read skill content before acting
- Verbose guidance forces complete reading
- **Trade-off:** Quality vs speed

**When Token Overhead is Acceptable:**
- Quality improvements (correctness, completeness)
- Critical behavior enforcement (test set protection)
- Context detection (extension vs source)

**When Token Overhead is Problematic:**
- No quality improvement
- Verbose checklists that don't change behavior
- "Helpful" sections that models ignore
- Duplicate content across sections

**Implication for Skill Design:**
- ✅ **Set explicit token budgets by task complexity**
- ✅ **Measure baseline token usage** (without skill)
- ✅ **Target 30% overhead maximum** for quality improvement
- ✅ **Remove guidance that doesn't improve outcomes**
- ⚠️ **Budget violations signal verbosity problems**

### Quick Refusal Patterns Work Exceptionally Well

**Finding:** Teaching skills to quickly refuse invalid requests has dramatic efficiency gains.

**Evidence from add-parsnip-engine:**
- Eval-4 (edge case refusal): -64% time, -59% tokens in iteration-3
- Qualitative: Clean, immediate refusal with explanation
- No wasted effort trying to implement invalid engine

**Pattern Structure:**

```markdown
# For engines requiring unsupported features:

**INSTRUCTIONS FOR CLAUDE:**
If the user requests an engine that requires:
- Custom survival distributions not in survival package
- Time-varying coefficients
- [Other unsupported features]

→ Politely explain parsnip doesn't support this yet
→ Don't attempt implementation
→ Suggest alternatives if available
```

**Why This Works:**
- **Prevents wasted work** on impossible tasks
- **Saves tokens** by avoiding exploration of dead ends
- **Improves user experience** with clear explanations
- **Protects quality** by preventing broken implementations

**When to Add Refusal Patterns:**
- Known edge cases that can't be handled
- Package limitations that users might not know
- Request types that would produce broken code
- Scenarios where baseline tries and fails

**Implication for Skill Design:**
- ✅ **Identify common "impossible" requests** during skill development
- ✅ **Add explicit refusal guidance** for these cases
- ✅ **Include brief explanation** of why it's not possible
- ✅ **Suggest alternatives** when available
- ✅ **Expect dramatic efficiency gains** (50-60% time/token savings)

### Case Study: add-parsnip-engine Iterations 1-3

**Context:** Skill for adding computational engines to parsnip package.

**Complexity:** Wide spectrum from simple (single-mode, few parameters) to complex (multi-mode, custom encodings, survival).

**Challenge:** Initial skill (iteration-1) showed 93% token gap on multi-mode engines, needed optimization.

**Iteration-1 Baseline:**
- Multi-mode token gap: +36%
- Simple cases: Reasonable performance
- File discipline: Not measured
- **Assessment:** Good starting point, but token-heavy on complex cases

**Iteration-2: "Helpful" Guidance (REGRESSION)**
- **Added:** 180-line multi-mode checklist with debug procedures
- **Intention:** Help models handle complex multi-mode development
- **Results:**
  - Multi-mode token gap: +93% (regression from +36%)
  - Simple cases: +48% slower (major regression)
  - **Diagnosis:** Verbose guidance created token bloat, slowed ALL cases

**Iteration-3: Simplified and Routed (RECOVERY)**
- **Changes:**
  1. Removed 180-line checklist → 2-sentence pattern
  2. Added complexity routing (simple vs complex assessment)
  3. Added token budget targets
  4. Added quick refusal pattern
  5. Removed verbose multi-mode debug section
- **Results:**
  - Multi-mode token gap: +67% (improved from +93%, still above target)
  - Simple cases: +4% slower (recovered from +48%)
  - Quick refusal: -64% time (dramatic improvement)
  - File discipline: 5-10 files (improved from 10-16, still above 2-3 target)

**Key Lessons:**

1. **Verbose "helpful" guidance backfired** - iteration-2 made things worse
2. **Concise patterns work better** than exhaustive checklists
3. **Complexity routing recovered simple case performance** - from +48% to +4%
4. **Some behaviors persist despite guidance** - file discipline 5-10 vs target 2-3
5. **Quick refusal patterns have huge ROI** - 64% time savings on edge cases

**Stopping Decision:**
- After 3 iterations, file discipline still not at target (2-3 files)
- Code quality improved, token efficiency partially recovered
- **Conclusion:** Accept 5-10 files as reasonable, focus on functional correctness
- **Next step:** Move to Level 2 evaluation (functional testing) before more guidance iterations

**Broader Implication:**
- Not all goals are achievable through guidance refinement
- After 3 iterations without convergence, try different approach or accept behavior
- Prioritize functional correctness over structural perfection

---

### Evaluation Infrastructure and Best Practices

Based on experience from add-yardstick-metric, add-dials-parameter, and add-recipe-step, here's how to build and maintain quantitative evaluation infrastructure.

#### 1. Grading Configuration Design

**Use Configuration-Driven Grading** (`grading-config.json`):

```json
{
  "skill_name": "add-yardstick-metric",
  "checks": {
    "file_count": {
      "extension": {"type": "range", "value": [2, 3]},
      "source": {"type": "exact", "value": 2}
    },
    "patterns": {
      "extension": {
        "has_three_functions": {
          "file_pattern": "**/*.R",
          "patterns": ["_impl\\s*<-\\s*function", "_vec\\s*<-\\s*function"],
          "logic": "all"
        }
      },
      "source": {
        "uses_internal_helpers": {
          "file_pattern": "**/*.R",
          "patterns": ["yardstick_mean|sens_binary|spec_binary"],
          "logic": "any"
        }
      }
    }
  }
}
```

**Pattern Matching Best Practices:**

1. **Be Comprehensive in Pattern Lists**
   - ❌ Too narrow: `yardstick_mean|yardstick_median` (misses sens_binary, spec_binary)
   - ✅ Comprehensive: `yardstick_mean|yardstick_median|sens_binary|spec_binary|sens_multiclass|spec_multiclass`
   - Evaluate which helpers are actually used in practice, not just the most common ones

2. **Avoid False Positives from Comments**
   - ❌ Pattern: `yardstick:::` matches comments explaining why NOT to use internal functions
   - ✅ Pattern: `yardstick:::\w+\(` matches actual function calls only
   - Accept that some explanatory comments may still trigger false positives
   - Document known false positives in config notes field

3. **Context-Specific Checks**
   - Extension: Check for prefix usage (`yardstick::`)
   - Source: Check for internal helper usage (no prefix)
   - Use separate check definitions per context
   - Provide explicit context field in eval_metadata.json

4. **Relax Checks for Test Files**
   - Source dev may occasionally use `package::` in test files for clarity
   - Don't enforce strict "max_count: 0" for prefix in tests
   - Use `max_count: 3` to allow reasonable test file usage

**Example Grading Configuration Structure:**
```json
{
  "skill_name": "...",
  "notes": "Document known limitations or false positives here",
  "checks": {
    "file_count": { ... },
    "prohibited_files": [...],
    "patterns": {
      "extension": { ... },
      "source": { ... }
    },
    "prefix_usage": {
      "extension": {"min_count": 3},
      "source": {"max_count": 3}
    }
  }
}
```

#### 2. Using the Centralized Grading Script

**grade-evaluations.py** in `skill-development/` provides reusable grading:

```bash
# With explicit config
python skill-development/grade-evaluations.py \
  developers/add-yardstick-metric-workspace/iteration-3 \
  --config developers/add-yardstick-metric/evals/grading-config.json

# With auto-detection (looks for ../developers/<skill>/evals/grading-config.json)
python skill-development/grade-evaluations.py \
  developers/add-yardstick-metric-workspace/iteration-3 \
  --skill add-yardstick-metric
```

**Outputs:**
- `grading.json` in each eval directory (individual results)
- `grading-summary.json` in workspace root (aggregate results)
- Console summary with pass rates and failed checks

**Context Detection:**
- Priority 1: Explicit `"context": "extension"` or `"source"` in eval_metadata.json
- Priority 2: Analyze prompt text for signals (e.g., "for my package" vs "PR to tidymodels")
- Default: extension (most common case)

#### 3. Iteration Strategy

**Prioritization Framework** (learned from yardstick iterations):

**Priority 1: Code Correctness** (Most Critical)
- Using correct internal helpers (source dev)
- Including required @examples
- Proper prefix usage (extension vs source)
- Implementing required patterns (three-function, case weights)
- These are FUNCTIONAL requirements that affect code quality

**Priority 2: Documentation Quality**
- Complete roxygen documentation
- Proper test coverage
- NA handling patterns
- Edge case handling

**Priority 3: File Discipline** (Least Critical)
- Number of files created
- Prohibited file lists
- README discipline
- These are STYLE requirements that don't affect functionality

**When Code Standards Conflict with File Discipline:**
- Always prioritize code standards
- De-emphasize file discipline if it's confusing the model
- Accept extra files if code quality improves

**Evidence-Based Iteration:**
```
Iteration-1: Establish baseline
- Run all evals with current skill
- Identify major failure categories
- Prioritize by impact on code quality

Iteration-2: Address highest-priority issues
- Focus on code correctness first
- Don't over-emphasize file discipline
- Avoid heavy visual emphasis that confuses models

Iteration-3: Refine based on results
- If regression occurs, back out problematic changes
- Re-test to confirm improvement
- Accept reasonable trade-offs (e.g., 75-85% file discipline is fine)
```

#### 4. Common Grading Pitfalls and Solutions

**Pitfall 1: False Positives from Comments**
- **Problem:** Pattern `yardstick:::` matches explanatory comments
- **Solution:** Update pattern to `yardstick:::\w+\(` to match function calls only
- **Accept:** Some comments may still trigger (e.g., in critical behavior tests)
- **Document:** Add note to config explaining known false positive

**Pitfall 2: Too-Narrow Pattern Matching**
- **Problem:** Check for `yardstick_mean` misses `sens_binary`, `spec_binary`
- **Solution:** Expand pattern to include all relevant helpers used in practice
- **Method:** Review actual eval outputs to see what helpers models naturally use
- **Update:** Add newly discovered helpers to pattern list

**Pitfall 3: Over-Emphasis Causing Regression**
- **Problem:** Dramatic visual warnings made iteration-2 WORSE than iteration-1
- **Solution:** Remove visual emphasis, move guidance to end, use simple language
- **Principle:** De-prioritize file discipline relative to code quality
- **Evidence:** Yardstick iter-2 (14% file discipline) → iter-3 (better file discipline AND code quality)

**Pitfall 4: Grading Artifacts vs Real Issues**
- **Problem:** Grading shows failure but code is actually correct
- **Example:** Eval 7 "uses internal functions" - only in comments explaining refusal
- **Solution:** Distinguish between grading limitations and skill issues
- **Action:** Fix grading config, not skill, when code is correct

**Pitfall 5: Context Detection Failures**
- **Problem:** All evals detected as same context
- **Solution:** Add explicit `"context"` field to eval_metadata.json
- **Priority:** Use explicit field over heuristics for reliability

#### 5. Interpreting Results

**What Pass Rates Mean:**

- **90-100%:** Excellent - skill working as intended
- **75-89%:** Good - acceptable with some edge cases
- **60-74%:** Moderate - needs improvement but functional
- **<60%:** Poor - significant issues to address

**By Check Category:**

- **Code correctness** (internal helpers, @examples, patterns): Target 90%+
- **Documentation** (roxygen, tests): Target 85%+
- **File discipline**: Target 75-85% (lower priority)

**When to Fix Grading Config vs Skill:**

**Fix Grading Config When:**
- Code is objectively correct but check fails
- Pattern is too narrow (missing valid helpers)
- False positives from comments or edge cases
- Check doesn't match actual requirements

**Fix Skill When:**
- Code is incorrect or missing required components
- Pattern adherence is genuinely failing
- Context detection is failing
- Models consistently misunderstand guidance

**Red Flags (Fix Skill Immediately):**
- Catastrophic failure (e.g., eval-7 in iteration-2: 60% → 10%)
- Regression across multiple evals
- Breaking of critical behaviors
- Code quality degradation

**Green Flags (May Be Grading Artifact):**
- Single eval fails while others pass
- Failure in comments or documentation
- Edge case that doesn't affect functionality
- Known false positive documented in config

#### 6. Measuring Iteration Impact

**Key Metrics to Track:**

```
Overall pass rate: X/Y checks (Z%)
Per-eval pass rates: Individual eval performance
Total files created: Across all evals
Failed check categories: Group failures by type
```

**Compare Across Iterations:**

```
Iteration-1 → Iteration-2 → Iteration-3
Pass rate:     62.5%   →   56.2%   →   84.4%   (Track direction)
Total files:   39      →   57      →   17      (Lower is better for file discipline)
Code quality:  Good    →   Poor    →   Excellent (Qualitative assessment)
```

**Success Indicators:**
- ✅ Pass rate improves or stays stable
- ✅ Code quality improves
- ✅ File counts decrease (if prioritizing file discipline)
- ✅ Critical behaviors maintain 100% or improve

**Warning Signs:**
- ⚠️ Pass rate decreases
- ⚠️ Critical behaviors regress
- ⚠️ File counts increase dramatically
- ⚠️ Code quality degrades (even if pass rate looks good)

**When to Back Out Changes:**
- Pass rate drops >10 percentage points
- Critical behavior fails completely (e.g., 60% → 10%)
- Code quality degrades noticeably
- Multiple evals show regression

**When to Accept Results:**
- Pass rate improves or stays within 5pp
- Code quality improves
- Trade-offs are acceptable (e.g., slight file increase for better code)
- Regressions are minor and in low-priority areas

---
---

## Summary

### Key Principles

1. **No Code Duplication:** Avoid duplicating code across files at all costs
   - Each piece of content should exist in exactly one place
   - SKILL.md links to references, never duplicates their content
   - References link to shared-references for universal patterns
   - If you find yourself copying code, create a reference and link to it instead
   - **Why:** Prevents inconsistency, reduces maintenance burden, ensures single source of truth
2. **Dual Context:** Always support extension and source development
3. **Extension First:** Main examples use extension patterns (most users)
4. **Complete Examples:** Show full working code, not fragments
5. **Cross-Reference Heavily:** Help users navigate
6. **Test All Code:** Examples must work as shown
7. **Consistent Structure:** Follow established patterns
8. **Clear Constraints:** Be explicit about extension limitations
9. **Package-Specific Details:** In skill directories, not shared-references

### Quick Start for New Skill

1. Copy structure from existing skill (yardstick or recipes)
2. Replace package name throughout
3. Identify 3-5 key concepts for references/
4. Write complete examples
5. Test all code
6. Add cross-references
7. Review as both extension and source developer

### Success Criteria

A skill is complete when:
- ✅ Extension developers can create working packages
- ✅ Source developers can contribute PRs
- ✅ All examples run without errors
- ✅ Navigation is clear and intuitive
- ✅ Both contexts are well-documented
- ✅ Cross-references work correctly

---

**Last Updated:** 2026-04-03

For questions or feedback about this guide, review the planning documents in `.github/planning/` or examine existing skills for examples.
