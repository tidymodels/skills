#!/usr/bin/env python3
"""
Perform text replacement in a file.

Usage:
    ./replace-text.py <file> <from_text> <to_text> [--dry-run]

Arguments:
    file       - Path to the file to modify
    from_text  - Text to search for (exact match)
    to_text    - Text to replace with
    --dry-run  - Show what would be changed without modifying the file

Examples:
    # Replace text in a file
    ./replace-text.py README.md "old text" "new text"

    # Preview changes without modifying
    ./replace-text.py README.md "old text" "new text" --dry-run

Features:
    - Exact string replacement (not regex)
    - Shows count of replacements made
    - Dry-run mode to preview changes
    - Preserves file permissions and encoding
"""

import sys
from pathlib import Path


def replace_text_in_file(file_path: Path, from_text: str, to_text: str, dry_run: bool = False):
    """Replace all occurrences of from_text with to_text in the specified file."""

    # Check if file exists
    if not file_path.exists():
        print(f"Error: File does not exist: {file_path}")
        return False

    # Check if it's a file (not a directory)
    if not file_path.is_file():
        print(f"Error: Not a file: {file_path}")
        return False

    # Read the file
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False

    # Check if from_text exists in the file
    if from_text not in content:
        print(f"No occurrences found of: {from_text}")
        print(f"In file: {file_path}")
        return False

    # Count occurrences
    count = content.count(from_text)

    # Perform replacement
    new_content = content.replace(from_text, to_text)

    # Show what would be changed
    if dry_run:
        print(f"[DRY RUN] Would replace {count} occurrence(s) in: {file_path}")
        print(f"  From: {from_text}")
        print(f"  To:   {to_text}")
        print()

        # Show context for each replacement (first 3 occurrences)
        lines = content.split('\n')
        occurrences_shown = 0
        for i, line in enumerate(lines, 1):
            if from_text in line:
                occurrences_shown += 1
                if occurrences_shown <= 3:
                    print(f"  Line {i}: {line.strip()[:100]}")

        if count > 3:
            print(f"  ... and {count - 3} more occurrence(s)")

        return True

    # Write the modified content back to the file
    try:
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✓ Replaced {count} occurrence(s) in: {file_path}")
        print(f"  From: {from_text}")
        print(f"  To:   {to_text}")
        return True
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
        return False


def main():
    if len(sys.argv) < 4:
        print("Usage: ./replace-text.py <file> <from_text> <to_text> [--dry-run]")
        print()
        print("Arguments:")
        print("  file       - Path to the file to modify")
        print("  from_text  - Text to search for (exact match)")
        print("  to_text    - Text to replace with")
        print("  --dry-run  - Show what would be changed without modifying the file")
        print()
        print("Examples:")
        print('  ./replace-text.py README.md "old text" "new text"')
        print('  ./replace-text.py README.md "old text" "new text" --dry-run')
        sys.exit(1)

    file_path = Path(sys.argv[1])
    from_text = sys.argv[2]
    to_text = sys.argv[3]
    dry_run = '--dry-run' in sys.argv[4:]

    # Validate arguments
    if from_text == to_text:
        print("Error: from_text and to_text are the same")
        sys.exit(1)

    if not from_text:
        print("Error: from_text cannot be empty")
        sys.exit(1)

    # Perform replacement
    success = replace_text_in_file(file_path, from_text, to_text, dry_run)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
