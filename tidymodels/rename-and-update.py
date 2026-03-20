#!/usr/bin/env python3
"""
Rename files and update all references across the tidymodels/ folder.

Usage:
    ./rename-and-update.py <from> <to>
    ./rename-and-update.py <from> <to> --dry-run

Examples:
    # Rename a file
    ./rename-and-update.py r-package-setup.md extension-prerequisites.md

    # Move to subdirectory
    ./rename-and-update.py extension-prerequisites.md shared-references/extension-prerequisites.md

    # Rename with different extension
    ./rename-and-update.py verify-setup.sh verify-setup.py
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple, Set

# File extensions to search for references
SEARCH_EXTENSIONS = {'.md', '.R', '.sh', '.ps1', '.py', '.yml', '.yaml', '.json'}

# Colors for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def log_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def log_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def log_header(msg):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{msg}{Colors.RESET}")

def find_files_to_rename(root_dir: Path, from_pattern: str) -> List[Path]:
    """Find all files matching the 'from' pattern."""
    files = []
    from_name = Path(from_pattern).name

    for path in root_dir.rglob('*'):
        if path.is_file() and path.name == from_name:
            files.append(path)

    return files

def build_rename_map(files: List[Path], from_pattern: str, to_pattern: str, root_dir: Path) -> List[Tuple[Path, Path]]:
    """Build a mapping of old paths to new paths."""
    rename_map = []
    from_path = Path(from_pattern)
    to_path = Path(to_pattern)

    for old_path in files:
        # Determine new path
        if len(to_path.parts) > 1:
            # Moving to a subdirectory
            # Replace the filename part with the new path
            parent = old_path.parent
            new_path = parent / to_path
        else:
            # Simple rename in same directory
            new_path = old_path.parent / to_path.name

        rename_map.append((old_path, new_path))

    return rename_map

def find_searchable_files(root_dir: Path) -> List[Path]:
    """Find all files where we should search for references."""
    files = []

    for path in root_dir.rglob('*'):
        if path.is_file() and path.suffix in SEARCH_EXTENSIONS:
            files.append(path)

    return files

def extract_reference_patterns(from_pattern: str) -> List[Tuple[re.Pattern, str]]:
    """
    Build regex patterns to find references to the 'from' file.
    Returns list of (compiled_regex, description) tuples.
    """
    from_path = Path(from_pattern)
    from_name = from_path.name
    from_stem = from_path.stem  # Without extension

    patterns = []

    # 1. Markdown links: [text](path/to/file.md)
    # Match both relative and absolute paths
    patterns.append((
        re.compile(r'\[([^\]]+)\]\(([^\)]*' + re.escape(from_name) + r')\)'),
        "Markdown link"
    ))

    # 2. File paths in text (with common path separators)
    patterns.append((
        re.compile(r'([\'"]?)([^\s\'"]*/)?' + re.escape(from_name) + r'\1'),
        "File path"
    ))

    # 3. Source/import statements: source("file.R")
    patterns.append((
        re.compile(r'(source|import)\s*\(\s*[\'"]([^\'"]*' + re.escape(from_name) + r')[\'"]'),
        "Source/import"
    ))

    # 4. Shell script paths (without quotes): ./path/to/file.sh
    patterns.append((
        re.compile(r'(\./|\.\./|/)([^\s]*/)?' + re.escape(from_name)),
        "Shell path"
    ))

    # 5. Glob patterns in Sys.glob or similar
    patterns.append((
        re.compile(r'(Sys\.glob|glob\.glob|path\.expand)\([\'"]([^\'"]*' + re.escape(from_name) + r')[\'"]'),
        "Glob pattern"
    ))

    return patterns

def update_references_in_file(
    file_path: Path,
    from_pattern: str,
    to_pattern: str,
    rename_map: List[Tuple[Path, Path]],
    dry_run: bool = False
) -> int:
    """
    Update all references to 'from' with 'to' in a single file.
    Returns number of replacements made.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        from_path = Path(from_pattern)
        to_path = Path(to_pattern)
        from_name = from_path.name
        to_name = to_path.name

        # Simple approach: replace all occurrences of the filename
        # This handles most cases including markdown links, paths, etc.

        # Strategy 1: Direct filename replacement
        content = content.replace(from_name, to_name)

        # Strategy 2: Handle path relocations
        # If moving to subdirectory, update relative paths
        if len(to_path.parts) > 1:
            # Example: from "file.md" to "subdir/file.md"
            # Need to update references like "../file.md" to "../subdir/file.md"

            # Find common path patterns and update them
            for old_ref in [f"../{from_name}", f"./{from_name}", from_name]:
                # Build new reference preserving relative path structure
                if old_ref.startswith("../"):
                    new_ref = f"../{to_path}"
                elif old_ref.startswith("./"):
                    new_ref = f"./{to_path}"
                else:
                    new_ref = str(to_path)

                content = content.replace(old_ref, new_ref)

        if content != original_content:
            if not dry_run:
                file_path.write_text(content, encoding='utf-8')
            return content.count(to_name) - original_content.count(to_name)

        return 0

    except Exception as e:
        log_error(f"Error processing {file_path}: {e}")
        return 0

def rename_files(rename_map: List[Tuple[Path, Path]], dry_run: bool = False) -> int:
    """Rename files according to the rename map."""
    count = 0

    for old_path, new_path in rename_map:
        if not old_path.exists():
            log_warning(f"Source file not found: {old_path}")
            continue

        # Create parent directory if needed
        if not dry_run:
            new_path.parent.mkdir(parents=True, exist_ok=True)
            old_path.rename(new_path)

        log_success(f"Renamed: {old_path} → {new_path}")
        count += 1

    return count

def main():
    parser = argparse.ArgumentParser(
        description='Rename files and update all references in tidymodels/ folder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('from_pattern', help='Current filename or path')
    parser.add_argument('to_pattern', help='New filename or path')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')

    args = parser.parse_args()

    # Get script directory (tidymodels/)
    script_dir = Path(__file__).parent

    log_header("=" * 60)
    log_header("Rename and Update References")
    log_header("=" * 60)

    log_info(f"From: {args.from_pattern}")
    log_info(f"To:   {args.to_pattern}")
    log_info(f"Root: {script_dir}")
    if args.dry_run:
        log_warning("DRY RUN MODE - No files will be modified")

    # Step 1: Find files to rename
    log_header("\n1. Finding files to rename...")
    files_to_rename = find_files_to_rename(script_dir, args.from_pattern)

    if not files_to_rename:
        log_error(f"No files found matching: {args.from_pattern}")
        return 1

    log_info(f"Found {len(files_to_rename)} file(s) to rename:")
    for f in files_to_rename:
        rel_path = f.relative_to(script_dir)
        print(f"  • {rel_path}")

    # Step 2: Build rename map
    rename_map = build_rename_map(files_to_rename, args.from_pattern, args.to_pattern, script_dir)

    # Step 3: Find all searchable files
    log_header("\n2. Finding files to search for references...")
    searchable_files = find_searchable_files(script_dir)
    log_info(f"Found {len(searchable_files)} files to search")

    # Step 4: Update references in all files
    log_header("\n3. Updating references...")
    total_replacements = 0
    files_modified = 0

    for file_path in searchable_files:
        replacements = update_references_in_file(
            file_path,
            args.from_pattern,
            args.to_pattern,
            rename_map,
            args.dry_run
        )

        if replacements > 0:
            rel_path = file_path.relative_to(script_dir)
            log_success(f"Updated {rel_path}: {replacements} reference(s)")
            total_replacements += replacements
            files_modified += 1

    if files_modified == 0:
        log_info("No references found to update")
    else:
        log_info(f"Total: {total_replacements} reference(s) updated in {files_modified} file(s)")

    # Step 5: Rename files
    log_header("\n4. Renaming files...")
    renamed_count = rename_files(rename_map, args.dry_run)

    # Summary
    log_header("\n" + "=" * 60)
    log_header("Summary")
    log_header("=" * 60)
    log_info(f"Files renamed: {renamed_count}")
    log_info(f"References updated: {total_replacements} in {files_modified} file(s)")

    if args.dry_run:
        log_warning("\nDRY RUN: No actual changes were made")
        log_info("Run without --dry-run to apply changes")
    else:
        log_success("\n✓ All changes applied successfully!")

    return 0

if __name__ == '__main__':
    sys.exit(main())
