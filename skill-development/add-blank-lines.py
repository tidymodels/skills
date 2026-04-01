#!/usr/bin/env python3
"""
Add blank lines before bullet points in markdown files for readability.

This script ensures that bullet points (lines starting with `-` or `  -`)
have a blank line before them, unless they already do.

Can process a single file or recursively process all .md files in a directory.
"""

import sys
import re
from pathlib import Path


def add_blank_lines_before_bullets(content):
    """
    Add blank lines before bullets that don't already have them.

    Args:
        content: The file content as a string

    Returns:
        Modified content with blank lines added
    """
    lines = content.split('\n')
    result = []

    for i, line in enumerate(lines):
        # Check if current line is a bullet (starts with - or two spaces and -)
        is_bullet = re.match(r'^(-|\s{2}-)(\s|$)', line)

        if is_bullet and i > 0:
            # Check if previous line exists and is not empty
            prev_line = lines[i - 1]

            # If previous line is not empty, add a blank line
            if prev_line.strip() != '':
                result.append('')

        result.append(line)

    return '\n'.join(result)


def process_file(file_path):
    """Process a single markdown file."""
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    # Process content
    modified_content = add_blank_lines_before_bullets(content)

    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"Successfully added blank lines to {file_path}")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python add-blank-lines.py <markdown-file-or-directory>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: Path '{input_path}' not found")
        sys.exit(1)

    # If it's a directory, process all .md files recursively
    if input_path.is_dir():
        md_files = list(input_path.rglob("*.md"))
        if not md_files:
            print(f"No .md files found in {input_path}")
            sys.exit(0)

        print(f"Processing {len(md_files)} markdown files in {input_path}...")
        success_count = 0
        for md_file in md_files:
            if process_file(md_file):
                success_count += 1

        print(f"\nCompleted: {success_count}/{len(md_files)} files processed successfully")
        sys.exit(0 if success_count == len(md_files) else 1)

    # If it's a file, process it directly
    elif input_path.is_file():
        success = process_file(input_path)
        sys.exit(0 if success else 1)

    else:
        print(f"Error: '{input_path}' is neither a file nor a directory")
        sys.exit(1)


if __name__ == '__main__':
    main()
