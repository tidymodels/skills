# Repository Access Setup

Having access to tidymodels package source code significantly improves the quality and accuracy of guidance by providing real implementation examples, test patterns, and architectural insights.

## Overview

### Why Repository Access Helps

When you clone the source repositories locally:

- **Real Examples**: See actual implementations instead of generic patterns
- **Test Patterns**: Learn from existing test files and edge cases
- **Architecture**: Understand package structure and conventions
- **Up-to-date**: Reference current implementation details
- **Searchable**: Grep through code for specific patterns

### What Gets Cloned

- **yardstick**: Performance metrics package (~5 MB shallow clone)
- **recipes**: Preprocessing steps package (~8 MB shallow clone)

Total disk space: ~15 MB

### What Gets Modified

The cloning scripts will automatically:
- Create `repos/` directory in your package root
- Add `repos/` to your `.gitignore` (won't be committed)
- Add `^repos$` to your `.Rbuildignore` (won't be built into package)

## Prerequisites

### Git Installation

You must have git installed to clone repositories.

**Check if git is installed:**

```bash
git --version
```

**If git is not installed:**

| Platform | Installation Method |
|----------|-------------------|
| **macOS** | Install Xcode Command Line Tools:<br>`xcode-select --install`<br>Or download from: https://git-scm.com/downloads |
| **Linux** | Use your package manager:<br>- Debian/Ubuntu: `sudo apt-get install git`<br>- RHEL/CentOS: `sudo yum install git`<br>- Fedora: `sudo dnf install git` |
| **Windows** | Download from: https://git-scm.com/downloads<br>Or use package manager:<br>- winget: `winget install Git.Git`<br>- Chocolatey: `choco install git` |

## Quick Start

### Step 1: Choose Your Script

We provide three platform-native scripts:

| Platform | Script | Notes |
|----------|--------|-------|
| macOS, Linux, WSL | `clone-tidymodels-repos.sh` | Bash script |
| Windows | `clone-tidymodels-repos.ps1` | PowerShell (preferred) |
| Any platform | `clone-tidymodels-repos.py` | Python 3.6+ fallback |

### Step 2: Run from Your Package Directory

Navigate to your R package directory (where your `DESCRIPTION` file is) and run the appropriate script.

**macOS/Linux/WSL:**

```bash
# From your package directory
cd /path/to/your-package

# Clone yardstick
./path/to/skills-personal/tidymodels/skills/shared-scripts/clone-tidymodels-repos.sh yardstick

# Or clone all packages
./path/to/skills-personal/tidymodels/skills/shared-scripts/clone-tidymodels-repos.sh all
```

**Windows (PowerShell):**

```powershell
# From your package directory
cd C:\path\to\your-package

# Clone yardstick
.\path\to\skills-personal\tidymodels\skills\shared-scripts\clone-tidymodels-repos.ps1 yardstick

# Or clone all packages
.\path\to\skills-personal\tidymodels\skills\shared-scripts\clone-tidymodels-repos.ps1 all
```

**Any platform (Python):**

```bash
# From your package directory
python3 /path/to/skills-personal/tidymodels/skills/shared-scripts/clone-tidymodels-repos.py yardstick
```

### Step 3: Verify Setup

After running the script, you should see:

```
your-package/
├── repos/
│   └── yardstick/
│       ├── R/
│       ├── tests/
│       └── ...
├── .gitignore        (now includes "repos/")
└── .Rbuildignore     (now includes "^repos$")
```

## Detailed Usage

### Script Options

All scripts accept package names as arguments:

| Argument | Description |
|----------|-------------|
| `yardstick` | Clone only yardstick repository |
| `recipes` | Clone only recipes repository |
| `yardstick recipes` | Clone both repositories |
| `all` | Clone all available repositories |

### Examples

**Clone single package:**
```bash
./clone-tidymodels-repos.sh yardstick
```

**Clone multiple packages:**
```bash
./clone-tidymodels-repos.sh yardstick recipes
```

**Clone all packages:**
```bash
./clone-tidymodels-repos.sh all
```

### Script Output

The scripts provide clear, color-coded progress messages:

```
═══════════════════════════════════════════════════════
  Tidymodels Repository Cloning Script
═══════════════════════════════════════════════════════

ℹ Step 1/4: Checking git installation...
✓ Git is installed (git version 2.50.1)

ℹ Step 2/4: Creating repos/ directory...
✓ Created repos/ directory

ℹ Step 3/4: Cloning repositories...
ℹ Processing yardstick...
ℹ Cloning yardstick from https://github.com/tidymodels/yardstick.git...
  Cloning into 'repos/yardstick'...
✓ Cloned yardstick to repos/yardstick
✓ Shallow clone verified (.git/shallow exists)

ℹ Step 4/4: Updating .gitignore and .Rbuildignore...
✓ Added 'repos/' to .gitignore
✓ Added '^repos$' to .Rbuildignore

═══════════════════════════════════════════════════════
✓ Repository setup complete!
═══════════════════════════════════════════════════════

Cloned repositories:
  ✓ repos/yardstick/

Modified files:
  ✓ .gitignore (added 'repos/')
  ✓ .Rbuildignore (added '^repos$')

ℹ These repositories are now available for reference during development.
```

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Repository access configured |
| 1 | Git not found | Install git (see Prerequisites) |
| 2 | Clone failed | Check network/disk space |
| 3 | Permission error | Check directory write permissions |

## PowerShell Execution Policy (Windows)

PowerShell scripts may be blocked by execution policy. If you see an error like:

```
File cannot be loaded because running scripts is disabled on this system
```

**Solution 1 - Set execution policy for current user (recommended):**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Solution 2 - Run with bypass flag (one-time):**

```powershell
powershell -ExecutionPolicy Bypass -File .\clone-tidymodels-repos.ps1 yardstick
```

## Manual Setup (Alternative)

If you prefer not to use the scripts, you can clone repositories manually:

```bash
# Create repos directory
mkdir repos

# Clone yardstick
cd repos
git clone --depth 1 https://github.com/tidymodels/yardstick.git
cd ..

# Clone recipes
cd repos
git clone --depth 1 https://github.com/tidymodels/recipes.git
cd ..

# Add to .gitignore
echo "repos/" >> .gitignore

# Add to .Rbuildignore
echo "^repos$" >> .Rbuildignore
```

## Troubleshooting

### Git not installed

**Symptom**: Script exits with "Git is not installed" message.

**Solution**: Install git for your platform (see Prerequisites section).

### Permission denied when creating repos/ directory

**Symptom**: Script exits with "Failed to create repos/ directory (permission denied)".

**Solutions**:
- Check that you're running the script from a directory where you have write permissions
- On Windows, try running PowerShell as Administrator
- On Unix-like systems, check directory ownership: `ls -la`

### Network issues / Clone failed

**Symptom**: Script exits with "Failed to clone" message.

**Solutions**:
- Check your internet connection
- Verify you can access github.com in your browser
- Check if you're behind a firewall or proxy
- Try again later (GitHub may be temporarily unavailable)

### Insufficient disk space

**Symptom**: Clone fails with disk space error.

**Solution**: Free up disk space. Requirements:
- yardstick: ~5 MB
- recipes: ~8 MB
- Total for both: ~15 MB

### Repository already exists

**Symptom**: Script reports "Repository already exists at repos/package (skipping)".

**Explanation**: This is not an error. The script detected an existing clone and skipped it to avoid overwriting.

**To update an existing repository:**

```bash
cd repos/yardstick
git pull
```

### Python version too old

**Symptom**: Python script fails with syntax errors.

**Solution**: Python script requires Python 3.6 or higher. Check your version:

```bash
python3 --version
```

If too old, use the bash or PowerShell scripts instead, or upgrade Python.

## Using Cloned Repositories

### During Skill Invocation

Once repositories are cloned, Claude will automatically detect them and use them to provide enhanced guidance with real examples.

### Referencing Files

When working with cloned repositories, you can reference files directly:

**Yardstick examples:**
- `repos/yardstick/R/num-mae.R` - Simple numeric metric
- `repos/yardstick/R/class-accuracy.R` - Simple class metric
- `repos/yardstick/tests/testthat/test-num-mae.R` - Test patterns

**Recipes examples:**
- `repos/recipes/R/center.R` - Modify-in-place step
- `repos/recipes/R/step_dummy.R` - Create-new-columns step
- `repos/recipes/tests/testthat/test-step_center.R` - Test patterns

### Searching for Examples

Use grep to find similar implementations:

```bash
# Find all numeric metrics in yardstick
grep -r "new_numeric_metric" repos/yardstick/R/

# Find all modify-in-place steps in recipes
grep -r "step_" repos/recipes/R/ | grep "prep.*bake"

# Find test patterns
grep -r "test_that.*works correctly" repos/yardstick/tests/
```

## Maintenance

### Updating Cloned Repositories

To update repositories to the latest version:

```bash
# Update yardstick
cd repos/yardstick
git pull
cd ../..

# Update recipes
cd repos/recipes
git pull
cd ../..
```

### Removing Cloned Repositories

To remove cloned repositories and free up disk space:

```bash
# Remove repos directory
rm -rf repos/

# Note: You may want to keep the entries in .gitignore and .Rbuildignore
# in case you want to re-clone later
```

## FAQ

### Do I need to clone repositories to use the skills?

No. Repository access is optional but recommended. Skills will work with built-in reference materials if you choose not to clone.

### Will cloned repositories be committed to my package?

No. The scripts automatically add `repos/` to `.gitignore`, preventing the cloned code from being committed.

### Will cloned repositories be included in my package build?

No. The scripts automatically add `^repos$` to `.Rbuildignore`, excluding them from package builds.

### How often should I update the cloned repositories?

Update frequency depends on your needs:
- **Active development**: Weekly or monthly
- **Stable reference**: Once per project
- **Latest features**: Before starting new features

### Can I clone repositories to a different location?

Yes, but you'll need to modify the scripts. The default `repos/` location is recommended because:
- It's easy to add to ignore files
- It's in the package root (accessible from R/ and tests/)
- It's a common convention

### Why use shallow clones?

Shallow clones (`--depth 1`) include only the latest commit, reducing:
- Clone time (faster download)
- Disk space (90% reduction)
- Complexity (no history to navigate)

For reference purposes, you typically only need the current code, not the full history.

### What if I want the full git history?

If you need the full repository history:

```bash
# Clone without --depth flag
cd repos
rm -rf yardstick  # Remove shallow clone
git clone https://github.com/tidymodels/yardstick.git
```

### Can I modify the cloned repositories?

You can, but it's not recommended because:
- Your changes won't be tracked
- Updates (git pull) may conflict
- They're meant for reference only

If you want to contribute to tidymodels, fork the repository on GitHub instead.

### Why three different scripts?

Platform-native scripts provide the best user experience:
- **Bash**: Native to Unix-like systems (macOS, Linux)
- **PowerShell**: Native to Windows (pre-installed)
- **Python**: Universal fallback (works everywhere)

Users can use whichever is most comfortable for their platform.

## Related Documentation

- **Scripts README**: `../shared-scripts/README.md` - Script usage and quick reference
- **Yardstick skill**: `add-yardstick-metric/SKILL.md` - Creating metrics
- **Recipes skill**: `add-recipe-step/SKILL.md` - Creating recipe steps

## Support

If you encounter issues not covered in troubleshooting:

1. Check that git is installed and in your PATH
2. Verify you have write permissions in your package directory
3. Try the Python fallback script if platform-native scripts fail
4. Review error messages carefully - they often contain helpful hints
5. Consider manual setup as an alternative

---

**Last Updated**: 2026-03-17
