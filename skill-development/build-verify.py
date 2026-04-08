#!/usr/bin/env python3
"""
Build and verify skills.

This script orchestrates four operations by calling discrete scripts:
1. BUILD: Localizes shared files to each skill's references folder (build-skills.py)
2. FORMAT: Adds blank lines before bullets in all markdown files (add-blank-lines.py)
3. VERIFY: Checks all markdown links and file references (verify-references.py)
4. DOCS: Verifies that skills have corresponding .qmd files in docs/ (verify-docs.py)

Usage:
    ./build-verify.py [directory]

    If no directory specified, runs against both ../developers/ and ../users/

Examples:
    ./build-verify.py              # Runs against both developers/ and users/
    ./build-verify.py ../developers/
    ./build-verify.py ../users/
"""

import sys
import subprocess
from pathlib import Path


def run_script(script_name: str, root_dir: Path, label: str) -> int:
    """Run a discrete script and return its exit code."""
    script_dir = Path(__file__).parent
    script_path = script_dir / script_name

    if not script_path.exists():
        print(f"Error: {script_name} not found at {script_path}")
        return 1

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(root_dir)],
            capture_output=True,
            text=True
        )

        # Print the script's output
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='')

        return result.returncode

    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return 1


def main():
    # Determine root directories
    if len(sys.argv) > 1:
        # Single directory specified
        root_dirs = [sys.argv[1]]
    else:
        # Default to both users/ and developers/ directories
        script_dir = Path(__file__).parent
        parent_dir = script_dir.parent
        root_dirs = [
            str(parent_dir / "developers"),
            str(parent_dir / "users")
        ]

    # Process each directory
    all_format_passed = True
    all_verify_passed = True
    all_docs_passed = True

    for root_dir in root_dirs:
        root_path = Path(root_dir)
        if not root_path.exists():
            print(f"Error: Directory does not exist: {root_dir}")
            sys.exit(1)

        # Print separator if processing multiple directories
        if len(root_dirs) > 1:
            print()
            print("=" * 60)
            print(f"Processing: {root_path.name}/")
            print("=" * 60)

        # Step 1: Build (localize shared files)
        build_exit_code = run_script("build-skills.py", root_path, "BUILD")
        if build_exit_code != 0:
            print(f"Build failed for {root_path.name}/. Skipping remaining steps.")
            sys.exit(1)

        # Step 2: Format (add blank lines before bullets)
        format_exit_code = run_script("add-blank-lines.py", root_path, "FORMAT")
        if format_exit_code != 0:
            all_format_passed = False

        # Step 3: Verify (check references)
        verify_exit_code = run_script("verify-references.py", root_path, "VERIFY")
        if verify_exit_code != 0:
            all_verify_passed = False

        # Step 4: Verify docs (check .qmd files exist)
        docs_exit_code = run_script("verify-docs.py", root_path, "DOCS")
        if docs_exit_code != 0:
            all_docs_passed = False

    # Final summary
    all_checks_passed = (all_format_passed and
                         all_verify_passed and
                         all_docs_passed)
    print()
    print("=" * 60)
    if all_checks_passed:
        print("✅ BUILD, FORMAT, AND VERIFY SUCCESSFUL")
    else:
        print("❌ VERIFICATION FAILED - Fix errors above before committing")
    print("=" * 60)
    print()

    sys.exit(0 if all_checks_passed else 1)


if __name__ == "__main__":
    main()
