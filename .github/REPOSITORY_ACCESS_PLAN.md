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

### 1. Repository Cloning Logic

**Implementation**: Claude executes git commands directly during skill invocation

**Requirements**:
- Work on macOS, Linux, Windows
- Clone from official tidymodels repositories
- Handle existing clones (skip or offer to update)
- Provide clear output/status messages
- Handle errors gracefully

**Repositories to clone**:
| Package | Repository URL |
|---------|---------------|
| yardstick | https://github.com/tidymodels/yardstick |
| recipes | https://github.com/tidymodels/recipes |

**Cloning logic**:
```bash
# 1. Check if git is installed
git --version

# 2. Create repos/ directory if needed
mkdir -p repos

# 3. Check if repository already exists
if [ -d "repos/yardstick" ]; then
  # Ask user if they want to update (git pull)
else
  # Clone with --depth 1 (shallow clone for speed and disk space)
  cd repos
  git clone --depth 1 https://github.com/tidymodels/yardstick
  cd ..
fi

# 4. Update user's .gitignore and .Rbuildignore
# Using R's usethis package:
# usethis::use_git_ignore("repos/")
# usethis::use_build_ignore("repos")
```

**Error handling**:
- Git not installed → Inform user about git benefits
- No write permissions → Suggest fallback to GitHub references
- Network issues → Suggest trying again or using built-in references
- Disk space issues → Report size requirements (~5-8 MB per repo)

### 2. Git Installation Check

**Before attempting to clone**, check if git is installed:

```python
# Pseudo-code for git check
def check_git_installed():
    try:
        result = run_command("git --version")
        return result.returncode == 0
    except:
        return False
```

**If git is NOT installed**:
```
I notice git is not installed on your system. While I can help you create
the metric/step using the built-in references, having access to the source
code repository would improve effectiveness.

If you'd like enhanced guidance with real examples from the package:
1. Install git: https://git-scm.com/downloads
2. Run this conversation again, and I can clone the repository for you

For now, I'll proceed using the built-in reference materials.
```

**If git IS installed**: Proceed to check for existing clone or offer to clone.

### 3. Gitignore and Rbuildignore Updates (User's Package)

When cloning repositories, the skill should modify the **user's package** .gitignore and .Rbuildignore files.

**Add to user's `.gitignore`** (or create if doesn't exist):
```
# Repository clones for development reference
repos/
```

**Add to user's `.Rbuildignore`** (or create if doesn't exist):
```
^repos$
```

**Implementation approach**:
```r
# R code to update user's package ignore files
usethis::use_git_ignore("repos/")
usethis::use_build_ignore("repos")
```

**Alternative - Direct file modification** (if usethis not available):
```r
# Add to .gitignore
gitignore_path <- ".gitignore"
gitignore_content <- if (file.exists(gitignore_path)) {
  readLines(gitignore_path)
} else {
  character(0)
}
if (!"repos/" %in% gitignore_content) {
  write("repos/", file = gitignore_path, append = TRUE)
}

# Add to .Rbuildignore
rbuildignore_path <- ".Rbuildignore"
rbuildignore_content <- if (file.exists(rbuildignore_path)) {
  readLines(rbuildignore_path)
} else {
  character(0)
}
if (!"^repos$" %in% rbuildignore_content) {
  write("^repos$", file = rbuildignore_path, append = TRUE)
}
```

**Important**: These modifications happen in the user's R package directory, NOT in the skills-personal repository.

### 4. Skill Enhancement Pattern

**At skill invocation**, Claude should follow this decision tree:

```
┌─────────────────────────────────┐
│ Skill Invoked                   │
└─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ Check: Is git installed?        │
└─────────────────────────────────┘
        │              │
        NO             YES
        │              │
        ▼              ▼
┌─────────────┐  ┌─────────────────────────────────┐
│ Inform user │  │ Check: repos/{package}/ exists? │
│ about git   │  └─────────────────────────────────┘
│ benefits    │          │              │
└─────────────┘          NO             YES
        │                │              │
        │                ▼              ▼
        │         ┌─────────────┐  ┌─────────────┐
        │         │ Ask to      │  │ Use local   │
        │         │ clone?      │  │ repository  │
        │         └─────────────┘  └─────────────┘
        │                │
        ▼                ▼
┌─────────────────────────────────┐
│ Continue with built-in          │
│ references only                 │
└─────────────────────────────────┘
```

**Step 1: Check git installation**
```bash
git --version
```

**If git NOT installed**:
```
I notice git is not installed on your system. While I can help you create
this metric/step using built-in references, having access to the {package}
source code repository would significantly improve the quality and accuracy
of my guidance.

If you'd like enhanced assistance with real examples from the package:
- Install git: https://git-scm.com/downloads
- Then we can clone the repository for reference

For now, I'll proceed using the built-in reference materials.
```

**Step 2: If git IS installed, check for local repository**
```bash
# Check if repos/{package}/ exists
ls repos/{package}/ 2>/dev/null
```

**If repository NOT found**, ask user:
```
I notice you don't have a local clone of {package}. Having access to the
source code will help me provide more accurate guidance with real examples
from the package.

Would you like me to:
1. Clone the repository locally (recommended) - stored in repos/{package}/
2. Reference the code on GitHub as needed
3. Continue without repository access (uses built-in references only)

Note: If you choose option 1, I'll add 'repos/' to your .gitignore and
.Rbuildignore files to prevent committing or building the cloned code.
```

**Step 3: Execute based on user choice**

**Step 4: Remember choice** for session (don't re-ask)

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

### 6. Integration Points in Skills

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

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Implement git installation check logic
- [ ] Create repository cloning logic (using git commands directly)
- [ ] Implement .gitignore and .Rbuildignore modification for user's package
- [ ] Test on macOS, Linux, Windows
- [ ] Handle edge cases (no git, no write permissions, etc.)

### Phase 2: Skill Enhancement (Week 2)
- [ ] Add repository check logic to skill invocation pattern
- [ ] Update `add-yardstick-metric/SKILL.md` with file references
- [ ] Update yardstick reference files (numeric, class, probability)
- [ ] Test file references work locally and on GitHub

### Phase 3: Expansion (Week 3)
- [ ] Update `add-recipe-step/SKILL.md` with file references
- [ ] Update recipes reference files (step types, patterns)
- [ ] Add references to shared-references files

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
- Bash script: Works on macOS, Linux, WSL, Git Bash (Windows)
- Python script: Works everywhere Python 3 is installed
- Fallback: Provide manual git commands if scripts fail

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
