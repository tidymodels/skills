# Shared Scripts

Repository cloning scripts for tidymodels development reference.

## Purpose

These scripts clone tidymodels package repositories (yardstick, recipes) into a local `repos/` directory for development reference. Having local access to the source code helps Claude provide more accurate guidance with real implementation examples during skill execution.

## Scripts

We provide three platform-native scripts for the best user experience:

| Script | Platform | Description |
|--------|----------|-------------|
| `clone-tidymodels-repos.sh` | macOS, Linux, WSL, Git Bash | Bash script (preferred for Unix-like systems) |
| `clone-tidymodels-repos.ps1` | Windows | PowerShell script (native to Windows 7+) |
| `clone-tidymodels-repos.py` | Universal | Python 3.6+ fallback (works on all platforms) |

## Quick Start

**Note:** These examples assume you're running from the `skills-personal` repository root. If running from elsewhere, adjust the path accordingly.

### macOS / Linux / WSL

```bash
# Clone yardstick
./tidymodels/shared-scripts/clone-tidymodels-repos.sh yardstick

# Clone recipes
./tidymodels/shared-scripts/clone-tidymodels-repos.sh recipes

# Clone multiple packages
./tidymodels/shared-scripts/clone-tidymodels-repos.sh yardstick recipes

# Clone all packages
./tidymodels/shared-scripts/clone-tidymodels-repos.sh all
```

### Windows (PowerShell)

```powershell
# Clone yardstick
.\tidymodels\shared-scripts\clone-tidymodels-repos.ps1 yardstick

# Clone recipes
.\tidymodels\shared-scripts\clone-tidymodels-repos.ps1 recipes

# Clone multiple packages
.\tidymodels\shared-scripts\clone-tidymodels-repos.ps1 yardstick recipes

# Clone all packages
.\tidymodels\shared-scripts\clone-tidymodels-repos.ps1 all
```

**PowerShell Execution Policy Note:**

If you encounter execution policy errors, run one of these commands:

```powershell
# Option 1: Set execution policy for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Option 2: Run with bypass flag (one-time)
powershell -ExecutionPolicy Bypass -File .\tidymodels\shared-scripts\clone-tidymodels-repos.ps1 yardstick
```

### Any Platform (Python)

```bash
# macOS/Linux
python3 tidymodels/shared-scripts/clone-tidymodels-repos.py yardstick

# Windows
python tidymodels/shared-scripts/clone-tidymodels-repos.py yardstick
```

## What the Scripts Do

1. **Check git installation** - Verifies git is available
2. **Create repos/ directory** - Creates directory if it doesn't exist
3. **Clone repositories** - Shallow clones specified packages (~5-8 MB each)
4. **Update ignore files** - Adds `repos/` to .gitignore and `^repos$` to .Rbuildignore

## Exit Codes

All scripts use consistent exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Git not found |
| 2 | Clone failed (network/disk space issues) |
| 3 | Permission error (cannot create repos/ directory) |

## Requirements

- **Git**: Must be installed and available in PATH
  - macOS: Install Xcode Command Line Tools or download from https://git-scm.com/downloads
  - Linux: Install via package manager (`apt-get install git`, `yum install git`, etc.)
  - Windows: Download from https://git-scm.com/downloads
- **Disk Space**: ~5 MB for yardstick, ~8 MB for recipes (shallow clones)
- **Python script only**: Python 3.6 or higher

## Directory Structure

After running the scripts, your package will have:

```
my-package/
├── R/
├── tests/
├── DESCRIPTION
├── repos/                    # Created by script
│   ├── yardstick/           # Cloned repository
│   │   ├── R/
│   │   ├── tests/
│   │   └── ...
│   └── recipes/             # Cloned repository
│       ├── R/
│       ├── tests/
│       └── ...
├── .gitignore               # Modified to include repos/
└── .Rbuildignore            # Modified to include ^repos$
```

The `repos/` directory is automatically added to your `.gitignore` and `.Rbuildignore` files, so cloned repositories won't be committed to your package or included in builds.

## Features

- **Shallow clones**: Uses `git clone --depth 1` for speed and disk space efficiency
- **Idempotent**: Safe to run multiple times (skips existing repositories)
- **No duplicates**: Checks before adding entries to ignore files
- **Clear output**: Color-coded progress messages
- **Error handling**: Detailed error messages with troubleshooting hints

## Troubleshooting

### Git not found

If git is not installed:
- **macOS**: Install Xcode Command Line Tools or visit https://git-scm.com/downloads
- **Linux**: Use package manager (e.g., `sudo apt-get install git`)
- **Windows**: Download from https://git-scm.com/downloads

### Permission denied

If you get permission errors:
- Check that you have write permissions in the current directory
- On Windows, try running PowerShell as Administrator
- On Unix-like systems, check directory ownership with `ls -la`

### Network issues

If cloning fails:
- Check your internet connection
- Verify you can access github.com in your browser
- Try again later (GitHub may be temporarily unavailable)

### Repository already exists

If a repository already exists in `repos/`, the script will skip it with a warning. This is expected behavior and not an error.

To update an existing repository, navigate to it and run:
```bash
cd repos/yardstick && git pull
```

## For More Information

See the comprehensive documentation: `tidymoderepository-access.md`

## License

These scripts are part of the skills-personal repository. See the repository's LICENSE for details.
