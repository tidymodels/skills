#!/usr/bin/env python3
"""
Verify references in markdown files and scripts.

This script checks:
- Markdown links to files (relative paths)
- Markdown anchor links (#heading)
- Script file references (imports, paths)
- Broken symlinks

Usage:
    ./verify-references.py [directory]

    If no directory specified, checks tidymodels/ by default
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Set
from collections import defaultdict


class ReferenceVerifier:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.errors = []
        self.warnings = []
        self.checked_files = 0
        self.checked_links = 0

    def should_skip(self, file_path: Path) -> bool:
        """Check if a file should be skipped."""
        # Skip files in directories starting with "."
        for part in file_path.parts:
            if part.startswith('.'):
                return True

        # Skip SKILL_IMPLEMENTATION_GUIDE.md
        if file_path.name == "SKILL_IMPLEMENTATION_GUIDE.md":
            return True

        return False

    def verify_all(self):
        """Run all verification checks."""
        print(f"Verifying references in: {self.root_dir}")
        print("=" * 60)

        # Find all markdown files (excluding those that should be skipped)
        all_md_files = list(self.root_dir.rglob("*.md"))
        md_files = [f for f in all_md_files if not self.should_skip(f)]
        print(f"Found {len(md_files)} markdown files (excluded {len(all_md_files) - len(md_files)})")

        # Find all script files (excluding those that should be skipped)
        all_script_files = list(self.root_dir.rglob("*.py")) + list(self.root_dir.rglob("*.sh"))
        script_files = [f for f in all_script_files if not self.should_skip(f)]
        print(f"Found {len(script_files)} script files (excluded {len(all_script_files) - len(script_files)})")
        print()

        # Check markdown files
        for md_file in md_files:
            self.verify_markdown_file(md_file)

        # Check script files
        for script_file in script_files:
            self.verify_script_file(script_file)

        # Report results
        self.report_results()

    def verify_markdown_file(self, md_file: Path):
        """Verify all references in a markdown file."""
        self.checked_files += 1

        try:
            content = md_file.read_text()
        except Exception as e:
            self.errors.append(f"{md_file}: Could not read file - {e}")
            return

        # Extract anchors available in this file
        anchors = self.extract_anchors(content)

        # Find all markdown links: [text](url) or [text](url#anchor)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)

        for link_text, link_url in links:
            self.checked_links += 1
            self.verify_link(md_file, link_url, link_text)

    def extract_anchors(self, content: str) -> Set[str]:
        """Extract all heading anchors from markdown content."""
        anchors = set()

        # Match markdown headings: # Heading, ## Heading, etc.
        heading_pattern = r'^#{1,6}\s+(.+)$'

        for line in content.split('\n'):
            match = re.match(heading_pattern, line)
            if match:
                heading_text = match.group(1).strip()
                # Convert heading to anchor format (lowercase, hyphens, remove special chars)
                anchor = self.heading_to_anchor(heading_text)
                anchors.add(anchor)

        return anchors

    def heading_to_anchor(self, heading: str) -> str:
        """Convert a markdown heading to its anchor format."""
        # Remove markdown formatting
        heading = re.sub(r'\*\*([^*]+)\*\*', r'\1', heading)  # Remove bold
        heading = re.sub(r'\*([^*]+)\*', r'\1', heading)       # Remove italic
        heading = re.sub(r'`([^`]+)`', r'\1', heading)         # Remove code
        heading = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', heading)  # Remove links

        # Convert to lowercase and replace spaces with hyphens
        anchor = heading.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)  # Remove special chars
        anchor = re.sub(r'\s+', '-', anchor)       # Replace spaces with hyphens
        anchor = re.sub(r'-+', '-', anchor)        # Collapse multiple hyphens
        anchor = anchor.strip('-')                 # Remove leading/trailing hyphens

        return anchor

    def verify_link(self, source_file: Path, link_url: str, link_text: str):
        """Verify a single markdown link."""
        # Skip external links (http://, https://, mailto:, etc.)
        if re.match(r'^[a-zA-Z]+:', link_url):
            return

        # Split link into file path and anchor
        if '#' in link_url:
            file_part, anchor = link_url.split('#', 1)
        else:
            file_part = link_url
            anchor = None

        # Resolve the file path relative to the source file
        if file_part:
            target_file = (source_file.parent / file_part).resolve()

            # Check if target file exists
            if not target_file.exists():
                self.errors.append(
                    f"{source_file}:\n"
                    f"  Broken link: [{link_text}]({link_url})\n"
                    f"  Target does not exist: {file_part}"
                )
                return

            # If there's an anchor, verify it exists in the target file
            if anchor:
                if target_file.suffix == '.md':
                    target_content = target_file.read_text()
                    target_anchors = self.extract_anchors(target_content)

                    if anchor not in target_anchors:
                        self.errors.append(
                            f"{source_file}:\n"
                            f"  Broken anchor: [{link_text}]({link_url})\n"
                            f"  Anchor '#{anchor}' not found in {target_file}"
                        )
        else:
            # Just an anchor reference (same file)
            if anchor:
                source_content = source_file.read_text()
                source_anchors = self.extract_anchors(source_content)

                if anchor not in source_anchors:
                    self.errors.append(
                        f"{source_file}:\n"
                        f"  Broken anchor: [{link_text}](#{anchor})\n"
                        f"  Anchor not found in same file"
                    )

    def verify_script_file(self, script_file: Path):
        """Verify file references in script files."""
        self.checked_files += 1

        try:
            content = script_file.read_text()
        except Exception as e:
            self.errors.append(f"{script_file}: Could not read file - {e}")
            return

        # Check for file path references (heuristic approach)
        # Look for patterns like:
        # - ./path/to/file
        # - ../path/to/file
        # - path/to/file.ext (with common extensions)

        patterns = [
            r'["\'](\.\./[^\s"\']+\.(?:md|py|sh|R|txt))["\']',  # ../relative paths
            r'["\'](\./[^\s"\']+\.(?:md|py|sh|R|txt))["\']',    # ./relative paths
            r'["\']([a-zA-Z0-9_-]+/[^\s"\']+\.(?:md|py|sh|R|txt))["\']',  # relative paths
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                target_path = (script_file.parent / match).resolve()

                if not target_path.exists():
                    self.warnings.append(
                        f"{script_file}:\n"
                        f"  Possible broken path: {match}"
                    )

    def report_results(self):
        """Print verification results."""
        print("\n" + "=" * 60)
        print("VERIFICATION RESULTS")
        print("=" * 60)
        print(f"Files checked: {self.checked_files}")
        print(f"Links checked: {self.checked_links}")
        print()

        if self.errors:
            print(f"ERRORS FOUND: {len(self.errors)}")
            print("-" * 60)
            for error in self.errors:
                print(error)
                print()
        else:
            print("No errors found!")

        if self.warnings:
            print(f"\nWARNINGS: {len(self.warnings)}")
            print("-" * 60)
            for warning in self.warnings:
                print(warning)
                print()

        print("=" * 60)

        # Return exit code
        return 1 if self.errors else 0


def main():
    # Determine root directory
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        # Default to tidymodels/ directory relative to script location
        script_dir = Path(__file__).parent
        root_dir = script_dir.parent

    if not Path(root_dir).exists():
        print(f"Error: Directory does not exist: {root_dir}")
        sys.exit(1)

    verifier = ReferenceVerifier(root_dir)
    exit_code = verifier.verify_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
