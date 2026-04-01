#!/usr/bin/env python3
"""
Add blank lines before bullet points in markdown files for readability.

This script ensures that bullet points (lines starting with `-` or `  -`)
have a blank line before them, unless they already do.
"""

import sys
import re


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


def main():
    if len(sys.argv) != 2:
        print("Usage: python add-blank-lines.py <markdown-file>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Process content
    modified_content = add_blank_lines_before_bullets(content)

    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"Successfully added blank lines to {file_path}")
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
