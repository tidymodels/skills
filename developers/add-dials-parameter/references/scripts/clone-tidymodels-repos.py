#!/usr/bin/env python3
"""
Clone Tidymodels Repositories

Description:
    Clones tidymodels package repositories (yardstick, recipes) for development
    reference. Creates repos/ directory, clones with shallow clone for speed,
    and updates .gitignore and .Rbuildignore to prevent committing cloned code.

Usage:
    python3 clone-tidymodels-repos.py yardstick
    python3 clone-tidymodels-repos.py recipes
    python3 clone-tidymodels-repos.py yardstick recipes
    python3 clone-tidymodels-repos.py all

Exit Codes:
    0 - Success
    1 - Git not found
    2 - Clone failed (network/disk space)
    3 - Permission error

Target Platforms:
    Universal (macOS, Linux, Windows) - Requires Python 3.6+
"""

import sys
import os
import subprocess
import shutil
import argparse
from pathlib import Path

# Repository configuration
REPOS = {
    "yardstick": "https://github.com/tidymodels/yardstick.git",
    "recipes": "https://github.com/tidymodels/recipes.git",
}

# ANSI color codes (fallback to no color on Windows without colorama)
try:
    # Try to enable ANSI colors on Windows
    if sys.platform == "win32":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
except:
    pass

COLORS = {
    "RED": "\033[0;31m",
    "GREEN": "\033[0;32m",
    "YELLOW": "\033[1;33m",
    "BLUE": "\033[0;34m",
    "NC": "\033[0m",  # No Color
}

# Disable colors if not supported
if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    COLORS = {k: "" for k in COLORS}


def print_info(message):
    """Print info message with blue color."""
    print(f"{COLORS['BLUE']}[INFO]{COLORS['NC']} {message}")


def print_success(message):
    """Print success message with green color."""
    print(f"{COLORS['GREEN']}[OK]{COLORS['NC']} {message}")


def print_warning(message):
    """Print warning message with yellow color."""
    print(f"{COLORS['YELLOW']}[WARN]{COLORS['NC']} {message}")


def print_error(message):
    """Print error message with red color."""
    print(f"{COLORS['RED']}[ERROR]{COLORS['NC']} {message}")


def check_git():
    """Check if git is installed."""
    git_path = shutil.which("git")

    if not git_path:
        print_error("Git is not installed.")
        print()
        print("Please install git to use this script:")
        if sys.platform == "darwin":
            print("  - Install Xcode Command Line Tools or visit https://git-scm.com/downloads")
        elif sys.platform.startswith("linux"):
            print("  - Use your package manager (apt-get install git, yum install git, etc.)")
        elif sys.platform == "win32":
            print("  - Download from https://git-scm.com/downloads")
            print("  - Or install via winget: winget install Git.Git")
            print("  - Or install via Chocolatey: choco install git")
        else:
            print("  - Visit https://git-scm.com/downloads")
        sys.exit(1)

    # Get git version
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        git_version = result.stdout.strip()
        print_success(f"Git is installed ({git_version})")
        return True
    except subprocess.CalledProcessError:
        print_error("Git is installed but not working correctly")
        sys.exit(1)


def update_gitignore():
    """Update .gitignore to include repos/ directory."""
    gitignore_path = Path(".gitignore")
    entry = "repos/"

    if gitignore_path.exists():
        content = gitignore_path.read_text()

        if entry in content.splitlines():
            print_info(f".gitignore already contains '{entry}'")
        else:
            # Append with proper line ending
            with gitignore_path.open("a", newline="\n") as f:
                if not content.endswith("\n"):
                    f.write("\n")
                f.write(f"{entry}\n")
            print_success(f"Added '{entry}' to .gitignore")
    else:
        # Create new file with proper line ending
        with gitignore_path.open("w", newline="\n") as f:
            f.write(f"{entry}\n")
        print_success(f"Created .gitignore with '{entry}'")


def update_rbuildignore():
    """Update .Rbuildignore to include ^repos$ pattern."""
    rbuildignore_path = Path(".Rbuildignore")
    entry = "^repos$"

    if rbuildignore_path.exists():
        content = rbuildignore_path.read_text()

        if entry in content.splitlines():
            print_info(f".Rbuildignore already contains '{entry}'")
        else:
            # Append with proper line ending
            with rbuildignore_path.open("a", newline="\n") as f:
                if not content.endswith("\n"):
                    f.write("\n")
                f.write(f"{entry}\n")
            print_success(f"Added '{entry}' to .Rbuildignore")
    else:
        # Create new file with proper line ending
        with rbuildignore_path.open("w", newline="\n") as f:
            f.write(f"{entry}\n")
        print_success(f"Created .Rbuildignore with '{entry}'")


def clone_repo(repo_name, repo_url):
    """Clone a repository with shallow clone."""
    repo_path = Path("repos") / repo_name

    print_info(f"Processing {repo_name}...")

    # Check if repository already exists
    if repo_path.exists():
        print_warning(f"Repository already exists at {repo_path} (skipping)")
        return True

    # Clone repository with shallow clone
    print_info(f"Cloning {repo_name} from {repo_url}...")

    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(repo_path)],
            capture_output=True,
            text=True,
            check=True
        )

        # Print git output with indentation
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                print(f"  {line}")
        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                print(f"  {line}")

        print_success(f"Cloned {repo_name} to {repo_path}")

        # Verify shallow clone
        shallow_file = repo_path / ".git" / "shallow"
        if shallow_file.exists():
            print_success("Shallow clone verified (.git/shallow exists)")

        return True

    except subprocess.CalledProcessError as e:
        print_error(f"Failed to clone {repo_name}")
        if e.stderr:
            for line in e.stderr.strip().split("\n"):
                print(f"  {line}")
        return False


def main():
    """Main script execution."""
    parser = argparse.ArgumentParser(
        description="Clone tidymodels repositories for development reference",
        epilog="Examples:\n"
               "  python3 clone-tidymodels-repos.py yardstick\n"
               "  python3 clone-tidymodels-repos.py recipes\n"
               "  python3 clone-tidymodels-repos.py yardstick recipes\n"
               "  python3 clone-tidymodels-repos.py all",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "packages",
        nargs="+",
        metavar="PACKAGE",
        help="Package(s) to clone: yardstick, recipes, or all"
    )

    args = parser.parse_args()

    print()
    print("=" * 55)
    print("  Tidymodels Repository Cloning Script")
    print("=" * 55)
    print()

    # Step 1: Check git installation
    print_info("Step 1/4: Checking git installation...")
    check_git()
    print()

    # Step 2: Create repos/ directory
    print_info("Step 2/4: Creating repos/ directory...")
    repos_dir = Path("repos")

    if not repos_dir.exists():
        try:
            repos_dir.mkdir(parents=True, exist_ok=True)
            print_success("Created repos/ directory")
        except PermissionError:
            print_error("Failed to create repos/ directory (permission denied)")
            sys.exit(3)
    else:
        print_info("repos/ directory already exists")
    print()

    # Step 3: Clone repositories
    print_info("Step 3/4: Cloning repositories...")

    # Determine which packages to clone
    packages_to_clone = []

    for package in args.packages:
        if package == "all":
            packages_to_clone = list(REPOS.keys())
            break
        elif package in REPOS:
            packages_to_clone.append(package)
        else:
            print_warning(f"Unknown package: {package} (skipping)")

    if not packages_to_clone:
        print_error("No valid packages specified")
        print()
        print("Valid packages: yardstick, recipes, all")
        sys.exit(1)

    # Clone each repository
    clone_failed = False
    for package in packages_to_clone:
        if not clone_repo(package, REPOS[package]):
            clone_failed = True

    if clone_failed:
        print()
        print_error("Some repositories failed to clone")
        print()
        print("Possible issues:")
        print("  - Network connectivity problems")
        print("  - Insufficient disk space (~5-8 MB per repository)")
        print("  - Repository URL changed (unlikely)")
        sys.exit(2)
    print()

    # Step 4: Update ignore files
    print_info("Step 4/4: Updating .gitignore and .Rbuildignore...")
    update_gitignore()
    update_rbuildignore()
    print()

    # Success summary
    print("=" * 55)
    print_success("Repository setup complete!")
    print("=" * 55)
    print()
    print("Cloned repositories:")
    for package in packages_to_clone:
        repo_path = Path("repos") / package
        if repo_path.exists():
            print(f"  - {repo_path}/")
    print()
    print("Modified files:")
    print("  - .gitignore (added 'repos/')")
    print("  - .Rbuildignore (added '^repos$')")
    print()
    print_info("These repositories are now available for reference during development.")
    print()


if __name__ == "__main__":
    main()
