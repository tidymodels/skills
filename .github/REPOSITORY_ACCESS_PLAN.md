# Repository Access Enhancement Plan

## Overview

Enhance the tidymodels skills system to provide automatic access to source code repositories (yardstick, recipes) for improved context, examples, and reference during skill execution. This will enable Claude to provide more accurate guidance by referencing actual implementations.

## Goals

1. **Automatic Context**: Provide Claude with access to package source code when using skills
2. **Flexible Access**: Support local cloning (preferred) or GitHub web access (fallback)
3. **User Control**: Always ask permission before cloning or accessing external resources
4. **Cross-Platform**: Work on macOS, Linux, and Windows
5. **Low Friction**: Minimal setup overhead for users

## Architecture

### Three-Tier Access Strategy

```
┌─────────────────────────────────────────────────────────┐
│ Skill Invocation (e.g., add-yardstick-metric)          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Check Repository Access                                 │
│                                                          │
│ 1. Local Clone?    → repos/yardstick/                  │
│ 2. GitHub Access?  → https://github.com/...            │
│ 3. No Access?      → Continue with built-in references │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Provide Enhanced Context                                │
│ - Direct file references (R/metric.R)                   │
│ - Example implementations                               │
│ - Test patterns                                         │
│ - Documentation templates                               │
└─────────────────────────────────────────────────────────┘
```

### Repository Location

- **Standard location**: `repos/` directory in **user's R package root** (not skills-personal)
- **Structure**:
  ```
  my-custom-package/          # User's R package
  ├── R/
  ├── tests/
  ├── DESCRIPTION
  ├── repos/                  # Added by skill
  │   ├── yardstick/         # Clone of tidymodels/yardstick
  │   ├── recipes/           # Clone of tidymodels/recipes
  │   └── ...                # Future: other tidymodels packages
  ├── .gitignore             # Modified to include repos/
  └── .Rbuildignore          # Modified to include repos/
  ```

**Note**: The `repos/` directory is created in the user's working package, not in the skills-personal repository.

## Implementation Components

### 1. Repository Cloning Scripts

**Implementation**: Standalone scripts in `shared-scripts/` directory that can be executed by Claude or run manually by users

**Location**: `shared-scripts/` in skills-personal repository

**Scripts** (platform-native approach):
1. `shared-scripts/clone-tidymodels-repos.sh` - POSIX shell script (macOS, Linux, WSL, Git Bash)
2. `shared-scripts/clone-tidymodels-repos.ps1` - PowerShell script (Windows native, preferred)
3. `shared-scripts/clone-tidymodels-repos.py` - Python script (universal fallback for any platform)

**Requirements**:
- Work on macOS, Linux, Windows
- Clone from official tidymodels repositories
- Handle existing clones (skip or offer to update)
- Provide clear output/status messages
- Handle errors gracefully
- Update .gitignore and .Rbuildignore automatically

**Repositories to clone**:
| Package | Repository URL |
|---------|---------------|
| yardstick | https://github.com/tidymodels/yardstick |
| recipes | https://github.com/tidymodels/recipes |

**Bash Script Features** (`clone-tidymodels-repos.sh`):
```bash
#!/bin/bash
# Target: macOS, Linux, WSL, Git Bash on Windows
# Check git installation
# Accept package name as argument (yardstick, recipes, all)
# Create repos/ directory if needed
# Clone with --depth 1 (shallow clone)
# Update .gitignore and .Rbuildignore
# Handle errors with clear messages
# Exit codes: 0 = success, 1 = git not found, 2 = clone failed, 3 = permission error
```

**PowerShell Script Features** (`clone-tidymodels-repos.ps1`):
```powershell
# Target: Windows (PowerShell 5.1+, pre-installed on Windows 7+)
# Check git installation (git.exe in PATH)
# Accept package name as parameter (yardstick, recipes, all)
# Create repos\ directory if needed
# Clone with --depth 1 (shallow clone)
# Update .gitignore and .Rbuildignore (handle CRLF line endings)
# Handle errors with clear messages
# Exit codes: 0 = success, 1 = git not found, 2 = clone failed, 3 = permission error
```

**Python Script Features** (`clone-tidymodels-repos.py`):
```python
#!/usr/bin/env python3
# Target: Universal fallback (requires Python 3.6+)
# Same functionality as platform scripts
# Uses subprocess for git commands
# Works on all platforms (macOS, Linux, Windows)
# Automatic line ending handling
# More detailed error messages with color output
```

**Script Usage**:

**macOS/Linux/WSL:**
```bash
# Clone specific package
./shared-scripts/clone-tidymodels-repos.sh yardstick

# Clone multiple packages
./shared-scripts/clone-tidymodels-repos.sh yardstick recipes

# Clone all packages
./shared-scripts/clone-tidymodels-repos.sh all
```

**Windows (PowerShell):**
```powershell
# Clone specific package
.\shared-scripts\clone-tidymodels-repos.ps1 yardstick

# Clone multiple packages
.\shared-scripts\clone-tidymodels-repos.ps1 yardstick recipes

# Clone all packages
.\shared-scripts\clone-tidymodels-repos.ps1 all
```

**Any platform (Python fallback):**
```bash
# If native scripts don't work or Python is preferred
python3 shared-scripts/clone-tidymodels-repos.py yardstick
```

**Script Selection Logic**:

When Claude invokes repository cloning, use this decision tree:

```
Platform Detection
        │
        ├─ macOS/Linux/WSL → Use .sh script
        ├─ Windows → Check PowerShell available?
        │            ├─ Yes → Use .ps1 script (preferred)
        │            └─ No → Use .py script (fallback)
        └─ Unknown/Other → Use .py script (universal)
```

**Platform Detection**:
- macOS: `uname` returns `Darwin`
- Linux: `uname` returns `Linux`
- WSL: `uname` contains `Microsoft` or `WSL`
- Windows: `$env:OS` contains `Windows_NT` or `os.name == 'nt'`

**PowerShell Availability Check** (Windows):
```powershell
# Check if PowerShell is available (should always be on Windows 7+)
$PSVersionTable.PSVersion
# If this returns version info, use .ps1 script
# If PowerShell not found (rare), fallback to .py
```

**Error handling**:
- Git not installed → Exit code 1, inform user with installation links
- No write permissions → Exit code 3, suggest checking permissions
- Network issues → Exit code 2, suggest retry or GitHub fallback
- Disk space issues → Exit code 2, report size requirements (~5-8 MB per repo)

### 2. Centralized Repository Access Documentation

**Location**: `tidymodels/skills/shared-references/repository-access.md`

**Purpose**: Single source of truth for repository access workflow, referenced by all skills

**Content Structure**:
1. **Overview** - Why repository access improves skill effectiveness
2. **Prerequisites** - Git installation check and instructions
3. **Quick Start** - Running the clone script
4. **Step-by-Step Workflow**:
   - Check git installation
   - Check for existing repository
   - Clone repository (using script)
   - Verify setup
5. **Using the Scripts**:
   - Shell script usage
   - Python script usage (fallback)
   - Script output and exit codes
6. **Manual Setup** - For users who prefer manual cloning
7. **Troubleshooting**:
   - Git not installed
   - Permission errors
   - Network issues
   - Disk space issues
8. **What Gets Modified**:
   - repos/ directory structure
   - .gitignore changes
   - .Rbuildignore changes
9. **FAQ**:
   - Disk space requirements
   - Update frequency
   - Removing cloned repositories

**Skills Reference**:
Each skill (add-yardstick-metric, add-recipe-step) will have a brief section:
```markdown
## Repository Access (Optional but Recommended)

For enhanced guidance with real implementation examples, see:
[Repository Access Setup](../shared-references/repository-access.md)

This will help clone the {package} source code to provide more accurate patterns.
```

### 3. Gitignore and Rbuildignore Updates (Handled by Scripts)

**Scripts handle ignore file modifications automatically**:

The clone scripts will:
- Add `repos/` to `.gitignore` (or create if doesn't exist)
- Add `^repos$` to `.Rbuildignore` (or create if doesn't exist)
- Avoid duplicates with conditional checks
- Provide clear output about what was modified

**Important**: These modifications happen in the user's R package directory, NOT in the skills-personal repository.

### 4. Skill Enhancement Pattern (Simplified)

**At skill invocation**, Claude should:

1. **Check if repository exists locally**: `ls repos/{package}/ 2>/dev/null`

2. **If repository EXISTS**: Use it for enhanced guidance

3. **If repository DOES NOT exist**: Present brief message with link to setup guide
   ```
   I notice you don't have the {package} source code locally. For enhanced
   guidance with real implementation examples, see:

   Repository Access Setup: shared-references/repository-access.md

   Or run: shared-scripts/clone-tidymodels-repos.sh {package}

   I'll proceed using built-in references for now.
   ```

4. **Continue with skill workflow** (non-blocking)

**Benefits of this approach**:
- Skills stay concise
- All setup logic centralized in one place
- Scripts provide reproducible setup
- Users can run scripts independently
- Clear separation of concerns

### 5. File Path Reference Pattern

**Current approach**: Abstract descriptions of what to do

**Enhanced approach**: Include specific file references

**Format for references**:
```
R/{filename}.R                    # Generic path works locally or online
tests/testthat/test-{name}.R      # Test file reference
```

**Example in skill documentation**:
```markdown
## Numeric Metrics

**Pattern:** Three-function approach (_impl, _vec, data.frame method)

**Reference implementations:**
- MAE: `R/num-mae.R`
- RMSE: `R/num-rmse.R`
- Huber Loss: `R/num-huber_loss.R`

**Test patterns:**
- `tests/testthat/test-num-mae.R`
- `tests/testthat/test-num-rmse.R`
```

**Benefits**:
- User can navigate to files locally if cloned
- Claude can reference specific files from repos/
- Works as GitHub reference if not cloned
- More specific than "see existing implementations"

### 6. Integration Points in Skills (Minimal Approach)

**Files to update** with repository references:

#### yardstick skill
- `tidymodels/skills/add-yardstick-metric/SKILL.md`
  - Add file references throughout examples
  - Reference specific metrics by path

- `tidymodels/skills/add-yardstick-metric/references/*.md`
  - **numeric-metrics.md**: Add paths to R/num-*.R files
  - **class-metrics.md**: Add paths to R/class-*.R files
  - **probability-metrics.md**: Add paths to R/prob-*.R files
  - etc.

#### recipes skill
- `tidymodels/skills/add-recipe-step/SKILL.md`
  - Add file references throughout examples
  - Reference specific steps by path

- `tidymodels/skills/add-recipe-step/references/*.md`
  - **modify-in-place-steps.md**: Add paths to R/step_*.R files
  - **create-new-columns-steps.md**: Add paths to relevant step files
  - etc.

### 7. Reference Frequency and Level

**Experimentation needed**: Find the right balance

**Proposed guidelines**:

| Section | Reference Frequency | Example |
|---------|-------------------|---------|
| Overview | Low (1-2 references) | Link to key architectural file |
| Pattern Introduction | Medium (2-4 references) | Link to 2-3 canonical examples |
| Detailed Examples | High (5+ references) | Link to similar implementations |
| Testing Section | Medium (3-5 references) | Link to test files for examples |

**Avoid over-referencing**:
- Don't list every possible file
- Focus on canonical/representative examples
- Link to similar patterns, not every variation

**Example - Good referencing**:
```markdown
## Numeric Metrics

Regression metrics compare continuous predictions to truth values.

**Core pattern files:**
- Simple metrics: `R/num-mae.R`, `R/num-rmse.R`
- Weighted metrics: `R/num-huber_loss.R`
- Complex metrics: `R/num-ccc.R` (correlation-based)

**Tests:**
- Basic pattern: `tests/testthat/test-num-mae.R`
- Edge cases: `tests/testthat/test-num-huber_loss.R`
```

**Example - Too much referencing**:
```markdown
❌ Don't do this:
See R/num-mae.R, R/num-rmse.R, R/num-mse.R, R/num-mape.R,
R/num-mpe.R, R/num-smape.R, R/num-huber_loss.R, R/num-ccc.R,
R/num-iic.R, R/num-rpd.R, R/num-rpiq.R, ...
```

## User Experience Flow

### First-Time User (git installed)

```
User: "Add a new yardstick metric for calculating MAPE"

Claude: I'll help you create a new yardstick metric.

I notice you don't have a local clone of the yardstick repository.
Having the source code available will help me provide more accurate
examples from the actual implementation.

Would you like me to:
1. Clone the repository (recommended) - stored in repos/yardstick/
2. Reference GitHub as needed - I'll link to online files
3. Skip repository access - I'll use built-in references only

Note: If you choose option 1, I'll add 'repos/' to your .gitignore
and .Rbuildignore files.

User: [chooses option 1]

Claude: Great! Cloning yardstick repository...

[Clone succeeds, updates .gitignore and .Rbuildignore]

Now I'll create your metric. I can see from repos/yardstick/R/num-mape.R
that MAPE is already implemented. Would you like me to:
- Show you how it works
- Create a similar custom metric
- Modify the existing implementation
```

### First-Time User (git NOT installed)

```
User: "Add a new yardstick metric for calculating MAPE"

Claude: I'll help you create a new yardstick metric.

I notice git is not installed on your system. While I can help you create
this metric using built-in references, having access to the yardstick source
code repository would significantly improve the quality and accuracy of my
guidance.

If you'd like enhanced assistance with real examples from the package:
- Install git: https://git-scm.com/downloads
- Then we can clone the repository for reference

For now, I'll proceed using the built-in reference materials.

For a numeric metric, you'll need three functions following the standard
pattern...
```

### Returning User (with cloned repos)

```
User: "Add a new recipe step for winsorizing"

Claude: I'll create a winsorizing step for recipes. Let me check the
existing step implementations in your local repository...

Looking at repos/recipes/R/step_center.R and R/step_normalize.R, I can
see the modify-in-place pattern you'll need. Let's create step_winsorize().
```

### User Who Declines Repository Access

```
User: [declines repository access]

Claude: No problem! I'll use the built-in reference materials.

For a numeric metric, you'll need three functions following the
standard pattern shown in the references/numeric-metrics.md guide...
```

## Implementation Phases (Revised)

### Phase 1: Foundation (Week 1)
- [ ] **Create shared-scripts/ directory** in skills-personal
- [ ] **Write clone-tidymodels-repos.sh** - POSIX shell script
  - [ ] Check git installation
  - [ ] Accept package name arguments
  - [ ] Create repos/ directory
  - [ ] Clone with --depth 1
  - [ ] Update .gitignore and .Rbuildignore
  - [ ] Error handling with exit codes
- [ ] **Write clone-tidymodels-repos.py** - Python fallback
  - [ ] Same functionality as shell script
  - [ ] Windows compatibility
  - [ ] Detailed error messages
- [ ] **Test scripts on macOS**
- [ ] **Test scripts on Linux** (if available)
- [ ] **Test scripts on Windows** (if available)

### Phase 2: Documentation and Integration (Week 2)
- [ ] **Create shared-references/repository-access.md** - Centralized guide
  - [ ] Overview and benefits
  - [ ] Prerequisites (git check)
  - [ ] Quick start with scripts
  - [ ] Step-by-step workflow
  - [ ] Script usage examples
  - [ ] Manual setup instructions
  - [ ] Comprehensive troubleshooting
  - [ ] FAQ section
- [ ] **Update add-yardstick-metric/SKILL.md** - Replace long section
  - [ ] Remove detailed "Repository Access Setup" section
  - [ ] Add brief "Repository Access (Optional)" section
  - [ ] Link to shared-references/repository-access.md
- [ ] **Update add-recipe-step/SKILL.md** - Replace long section
  - [ ] Remove detailed "Repository Access Setup" section
  - [ ] Add brief "Repository Access (Optional)" section
  - [ ] Link to shared-references/repository-access.md
- [ ] **Test documentation clarity** - Ensure users can follow setup

### Phase 3: File References Enhancement (Week 3)
- [ ] **Add file path references to yardstick skill**
  - [ ] Review and update SKILL.md with repo file references
  - [ ] Update numeric-metrics.md with R/ file paths
  - [ ] Update class-metrics.md with R/ file paths
  - [ ] Update probability-metrics.md with R/ file paths
  - [ ] Update test patterns with test file paths
  - [ ] Balance reference density (avoid over-referencing)
- [ ] **Add file path references to recipes skill**
  - [ ] Review and update SKILL.md with repo file references
  - [ ] Update modify-in-place-steps.md with R/ file paths
  - [ ] Update create-new-columns-steps.md with R/ file paths
  - [ ] Update test patterns with test file paths
  - [ ] Balance reference density

### Phase 4: Refinement (Week 4)
- [ ] Test with real users
- [ ] Adjust reference frequency based on feedback
- [ ] Document best practices for reference density
- [ ] Create examples showing effective usage

## Technical Considerations

### Repository Updates

**Question**: How often to update cloned repos?

**Options**:
1. **Manual**: User runs `scripts/clone-repos.sh --update` when desired
2. **Prompt**: Claude asks "Your clone is X days old, update?" if detected as stale
3. **Automatic**: Git pull on each skill invocation (may be slow)

**Recommendation**: Option 1 (manual) for initial version, can add Option 2 later

### Disk Space

- Shallow clone (`--depth 1`) of yardstick: ~5 MB
- Shallow clone of recipes: ~8 MB
- Total overhead: ~15 MB (negligible)

### Privacy and Security

**Considerations**:
- Only clone from official tidymodels GitHub repos
- Use HTTPS (not SSH) for wider compatibility
- No authentication required (public repos)
- User must explicitly approve cloning

### Cross-Platform Compatibility

**Git availability**:
- macOS: Git typically pre-installed or via Xcode tools
- Linux: Git typically pre-installed or via package manager
- Windows: Check for git.exe in PATH, provide instructions if missing

**Script compatibility**:
- **Bash script**: Works on macOS, Linux, WSL, Git Bash (Windows)
- **PowerShell script**: Works on Windows (PowerShell 5.1+, pre-installed on Windows 7+)
  - Note: May require execution policy adjustment: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
  - Alternative: Run with bypass flag: `powershell -ExecutionPolicy Bypass -File clone-tidymodels-repos.ps1`
- **Python script**: Works everywhere Python 3.6+ is installed
- **Fallback**: Provide manual git commands if all scripts fail

**Line Ending Handling**:
- Bash script: Creates files with LF (Unix) line endings
- PowerShell script: Creates files with CRLF (Windows) line endings - appropriate for Windows
- Python script: Uses platform-appropriate line endings automatically

## Success Metrics

**Quantitative**:
- % of users who choose to clone repos
- % of users who successfully clone repos
- Reduction in "can you show an example" follow-up questions

**Qualitative**:
- More accurate code generation (matches tidymodels patterns)
- Fewer iterations to get correct implementation
- User feedback on helpfulness

## Open Questions

1. **Reference density**: How many file references per section is optimal?
   - *Needs experimentation*: Start conservative, gather feedback

2. **Update frequency**: How often should users update cloned repos?
   - *Start with manual*: Add prompts later if needed

3. **Multiple package versions**: Support checking out specific versions/tags?
   - *Defer to Phase 2+*: Clone main branch initially

4. **Package expansion**: Which other tidymodels packages to include?
   - *Start with yardstick and recipes*: Add parsnip, workflows later

5. **Reference format**: Always show relative path from package root?
   - *Yes*: Consistent format works for local and GitHub

## Alternative Approaches Considered

### 1. Embed full source in skill files
**Pros**: No cloning needed, always available
**Cons**: Massive file bloat, sync issues, copyright concerns
**Decision**: ❌ Rejected - files would be too large

### 2. Dynamic GitHub API calls
**Pros**: Always up-to-date, no cloning
**Cons**: Rate limits, requires internet, slower
**Decision**: ⚠️ Possible fallback option

### 3. Submodules
**Pros**: Git-native approach
**Cons**: Complexity, user confusion, tracking issues
**Decision**: ❌ Rejected - too complex for users

### 4. Package installation + code reading
**Pros**: Uses installed packages
**Cons**: Finding source location varies, incomplete without tests
**Decision**: ❌ Rejected - repos provide more complete context

## Next Steps

1. **Review and edit this plan**: User feedback on approach
2. **Implement git check and cloning logic**: Add to skill invocation pattern
3. **Test cross-platform**: Verify on different OS configurations
4. **Update one skill**: Start with yardstick, add file references incrementally
5. **Gather feedback**: Test with users, adjust reference frequency
6. **Scale to other skills**: Apply learnings to recipes and future skills

## References

- tidymodels/yardstick: https://github.com/tidymodels/yardstick
- tidymodels/recipes: https://github.com/tidymodels/recipes
- Git documentation: https://git-scm.com/doc
- Claude Code skills: https://code.claude.com/docs/en/skills

---

**Status**: Planning phase
**Created**: 2026-03-17
**Last Updated**: 2026-03-17
**Owner**: @edgararuiz
