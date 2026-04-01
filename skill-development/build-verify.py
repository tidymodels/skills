#!/usr/bin/env python3
"""
Build and verify skills.

This script performs three operations:
1. BUILD: Localizes shared files to each skill's references folder
2. VERIFY: Checks all markdown links and file references
3. DOCS: Verifies that skills have corresponding .qmd files in docs/

Usage:
    ./build-verify.py [directory]

    If no directory specified, uses parent directory relative to script location

Examples:
    ./build-verify.py ../developers/
    ./build-verify.py ../users/
"""

import os
import re
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Set
from collections import defaultdict


class Builder:
    """Handles building skills by localizing shared files."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.skills = self._discover_skills()
        self.shared_dir = self.root_dir / "shared-references"
        self.shared_parsnip_dir = self.root_dir / "shared-references-parsnip"
        self.errors = []

    def _discover_skills(self) -> List[str]:
        """Discover all skill directories in root_dir."""
        skills = []
        if not self.root_dir.exists():
            return skills

        for item in self.root_dir.iterdir():
            # Skip if not a directory or if it's shared-references
            if not item.is_dir() or item.name in ["shared-references", "shared-references-parsnip"]:
                continue

            # A directory is a skill if it contains SKILL.md or references/
            has_skill_md = (item / "SKILL.md").exists()
            has_references = (item / "references").exists()

            if has_skill_md or has_references:
                skills.append(item.name)

        return sorted(skills)

    def build_all(self, quiet=False):
        """Copy shared files to each skill's references folder."""
        if quiet:
            print("BUILD: Localizing Shared Files")
        else:
            print("=" * 60)
            print("BUILD: Localizing Shared Files to Skills")
            print("=" * 60)
            print()

        if not self.shared_dir.exists():
            self.errors.append(f"Shared references directory not found: {self.shared_dir}")
            return False

        success = True
        skill_stats = []
        for skill in self.skills:
            md_count, script_count = self.build_skill(skill, quiet=quiet)
            if md_count is None:
                success = False
            else:
                skill_stats.append((skill, md_count, script_count))

        if quiet and success:
            for skill, md_count, script_count in skill_stats:
                print(f"✓ {skill} ({md_count} md files, {script_count} scripts)")

        if not success:
            print()
            print("=" * 60)
            print("✗ BUILD FAILED")
            print("=" * 60)
            print()
            for error in self.errors:
                print(f"  ERROR: {error}")
            print()

        return success

    def build_skill(self, skill: str, quiet=False):
        """Copy shared files to a single skill. Returns (md_count, script_count) or (None, None) on error."""
        if not quiet:
            print(f"Processing: {skill}")

        skill_dir = self.root_dir / skill
        refs_dir = skill_dir / "references"

        # Check if references directory exists
        if not refs_dir.exists():
            error = f"{skill}: references/ directory not found"
            self.errors.append(error)
            print(f"  ERROR: {error}")
            return None, None

        # Copy shared-references/*.md files
        if not quiet:
            print(f"  Copying shared-references/*.md → {refs_dir.name}/")
        md_files = list(self.shared_dir.glob("*.md"))
        if not md_files:
            error = f"{skill}: No .md files found in shared-references/"
            self.errors.append(error)
            print(f"  WARNING: {error}")

        for md_file in md_files:
            try:
                dest = (refs_dir / md_file.name).resolve()
                # Validate destination is within root_dir
                try:
                    dest.relative_to(self.root_dir)
                except ValueError:
                    error = f"{skill}: Destination path outside project: {dest}"
                    self.errors.append(error)
                    print(f"  ERROR: {error}")
                    return None, None
                shutil.copy2(md_file, dest)
                if not quiet:
                    print(f"    {md_file.name}")
            except Exception as e:
                error = f"{skill}: Failed to copy {md_file.name} - {e}"
                self.errors.append(error)
                print(f"  ERROR: {error}")
                return None, None

        # Copy shared-references-parsnip/*.md files (for parsnip skills only)
        parsnip_md_count = 0
        if "parsnip" in skill and self.shared_parsnip_dir.exists():
            if not quiet:
                print(f"  Copying shared-references-parsnip/*.md → {refs_dir.name}/")
            parsnip_md_files = list(self.shared_parsnip_dir.glob("*.md"))

            for md_file in parsnip_md_files:
                try:
                    dest = (refs_dir / md_file.name).resolve()
                    # Validate destination is within root_dir
                    try:
                        dest.relative_to(self.root_dir)
                    except ValueError:
                        error = f"{skill}: Destination path outside project: {dest}"
                        self.errors.append(error)
                        print(f"  ERROR: {error}")
                        return None, None
                    shutil.copy2(md_file, dest)
                    parsnip_md_count += 1
                    if not quiet:
                        print(f"    {md_file.name}")
                except Exception as e:
                    error = f"{skill}: Failed to copy {md_file.name} - {e}"
                    self.errors.append(error)
                    print(f"  ERROR: {error}")
                    return None, None

        # Create scripts subdirectory
        scripts_dir = refs_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        # Copy shared-references/scripts/* files
        script_count = 0
        shared_scripts_dir = self.shared_dir / "scripts"
        if shared_scripts_dir.exists():
            if not quiet:
                print(f"  Copying shared-references/scripts/* → {refs_dir.name}/scripts/")
            script_files = list(shared_scripts_dir.iterdir())

            for script_file in script_files:
                if script_file.is_file():
                    try:
                        dest = (scripts_dir / script_file.name).resolve()
                        # Validate destination is within root_dir
                        try:
                            dest.relative_to(self.root_dir)
                        except ValueError:
                            error = f"{skill}: Destination path outside project: {dest}"
                            self.errors.append(error)
                            print(f"  ERROR: {error}")
                            return None, None
                        shutil.copy2(script_file, dest)
                        script_count += 1
                        if not quiet:
                            print(f"    {script_file.name}")
                    except Exception as e:
                        error = f"{skill}: Failed to copy {script_file.name} - {e}"
                        self.errors.append(error)
                        print(f"  ERROR: {error}")
                        return None, None

        if not quiet:
            print(f"  ✓ {skill} complete")
            print()
        return len(md_files) + parsnip_md_count, script_count


class DocsVerifier:
    """Verifies that skills have corresponding .qmd files in docs/."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.project_root = self.root_dir.parent  # Go up one level to project root
        self.docs_dir = self.project_root / "docs"
        self.errors = []
        self.warnings = []

    def verify_all(self, quiet=False):
        """Check that skills have corresponding .qmd files."""
        if quiet:
            print("DOCS: Checking .qmd files")
        else:
            print("=" * 60)
            print("DOCS: Checking .qmd files")
            print("=" * 60)
            print()

        # Determine which folder we're checking (developers or users)
        folder_name = self.root_dir.name
        if folder_name not in ['developers', 'users']:
            if not quiet:
                print(f"Skipping docs verification (not in developers/ or users/)")
            return 0

        docs_subdir = self.docs_dir / folder_name
        if not docs_subdir.exists():
            self.errors.append(f"docs/{folder_name}/ directory does not exist")
            return self.report_results(quiet=quiet)

        # Find all skill directories
        skills = self._discover_skills()

        if not quiet:
            print(f"Checking {len(skills)} skills in {folder_name}/")
            print()

        # Check each skill
        for skill in skills:
            self.verify_skill_docs(skill, docs_subdir, quiet=quiet)

        return self.report_results(quiet=quiet)

    def _discover_skills(self) -> List[str]:
        """Discover all skill directories."""
        skills = []
        if not self.root_dir.exists():
            return skills

        for item in self.root_dir.iterdir():
            # Skip if not a directory or if it's shared-references
            if not item.is_dir() or item.name in ["shared-references", "shared-references-parsnip"]:
                continue

            # A directory is a skill if it contains SKILL.md or references/
            has_skill_md = (item / "SKILL.md").exists()
            has_references = (item / "references").exists()

            if has_skill_md or has_references:
                skills.append(item.name)

        return sorted(skills)

    def verify_skill_docs(self, skill: str, docs_subdir: Path, quiet=False):
        """Verify that a skill has corresponding .qmd files."""
        skill_dir = self.root_dir / skill

        # Check 1: Skill should have index.qmd in its subfolder
        skill_docs_dir = docs_subdir / skill
        expected_qmd = skill_docs_dir / "index.qmd"
        if not expected_qmd.exists():
            self.errors.append(
                f"{skill}:\n"
                f"  Missing docs file: {expected_qmd.relative_to(self.project_root)}\n"
                f"  Expected index.qmd file in skill subfolder"
            )
        elif not quiet:
            print(f"✓ {skill}/index.qmd exists")

        # Check 2: Each .md file in references/ should have a corresponding .qmd
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            docs_refs_dir = skill_docs_dir / "references"
            if not docs_refs_dir.exists():
                self.errors.append(
                    f"{skill}:\n"
                    f"  Missing docs/{skill}/references/ directory: {docs_refs_dir.relative_to(self.project_root)}"
                )
                return

            md_files = list(refs_dir.rglob("*.md"))
            for md_file in md_files:
                # Skip files in scripts/ subdirectories
                if "scripts" in md_file.parts:
                    continue

                # Get relative path from refs_dir and convert .md to .qmd
                rel_path = md_file.relative_to(refs_dir)
                expected_ref_qmd = docs_refs_dir / rel_path.with_suffix('.qmd')

                if not expected_ref_qmd.exists():
                    self.errors.append(
                        f"{skill}:\n"
                        f"  Missing reference doc: {expected_ref_qmd.relative_to(self.project_root)}\n"
                        f"  For reference file: {md_file.relative_to(self.root_dir)}"
                    )
                elif not quiet:
                    print(f"  ✓ {skill}/references/{rel_path.with_suffix('.qmd')} exists")

    def report_results(self, quiet=False):
        """Print docs verification results."""
        if quiet and not self.errors:
            print(f"✓ All skills have corresponding .qmd files")
            return 0

        if not quiet or self.errors:
            print()
            print("=" * 60)
            print("DOCS VERIFICATION RESULTS")
            print("=" * 60)

        if self.errors:
            print(f"✗ ERRORS FOUND: {len(self.errors)}")
            print("-" * 60)
            for error in self.errors:
                print(error)
                print()
        else:
            print("✓ No errors found!")

        if not quiet or self.errors:
            print("=" * 60)

        return 1 if self.errors else 0


class ReferenceVerifier:
    """Verifies references in markdown files and scripts."""

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

        # Skip shared-references directories
        if 'shared-references' in file_path.parts or 'shared-references-parsnip' in file_path.parts:
            return True

        # Skip SKILL_IMPLEMENTATION_GUIDE.md
        if file_path.name == "SKILL_IMPLEMENTATION_GUIDE.md":
            return True

        return False

    def strip_html_comments(self, content: str) -> str:
        """Remove HTML comments from content."""
        # Remove single-line and multi-line HTML comments
        return re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    def strip_script_comments(self, content: str) -> str:
        """Remove # comments from script content, preserving shebangs."""
        lines = []
        for line in content.split('\n'):
            # Keep shebang lines
            if line.startswith('#!'):
                lines.append(line)
                continue
            # Remove everything from # to end of line
            # Note: This doesn't handle # inside strings, but for our
            # file path detection (which looks for quoted paths), this works fine
            line = re.sub(r'#.*$', '', line)
            lines.append(line)
        return '\n'.join(lines)

    def verify_all(self, quiet=False):
        """Run all verification checks."""
        if quiet:
            print("VERIFY: Checking References")
        else:
            print("=" * 60)
            print("VERIFY: Checking References")
            print("=" * 60)
            print()

        # Find all markdown files (excluding those that should be skipped)
        all_md_files = list(self.root_dir.rglob("*.md"))
        md_files = [f for f in all_md_files if not self.should_skip(f)]
        if not quiet:
            print(f"Found {len(md_files)} markdown files (excluded {len(all_md_files) - len(md_files)})")

        # Find all script files (excluding those that should be skipped)
        all_script_files = list(self.root_dir.rglob("*.py")) + list(self.root_dir.rglob("*.sh"))
        script_files = [f for f in all_script_files if not self.should_skip(f)]
        if not quiet:
            print(f"Found {len(script_files)} script files (excluded {len(all_script_files) - len(script_files)})")
            print()

        # Check markdown files
        for md_file in md_files:
            self.verify_markdown_file(md_file)

        # Check script files
        for script_file in script_files:
            self.verify_script_file(script_file)

        # Report results
        return self.report_results(quiet=quiet)

    def verify_markdown_file(self, md_file: Path):
        """Verify all references in a markdown file."""
        self.checked_files += 1

        try:
            content = md_file.read_text()
        except Exception as e:
            self.errors.append(f"{md_file}: Could not read file - {e}")
            return

        # Strip HTML comments before processing
        content = self.strip_html_comments(content)

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
            # Use resolve() to properly handle all .. and . in the path
            target_file = (source_file.parent / file_part).resolve()

            # Verify the resolved path is within the repository
            try:
                target_file.relative_to(self.root_dir)
            except ValueError:
                self.errors.append(
                    f"{source_file}:\n"
                    f"  Invalid link: [{link_text}]({link_url})\n"
                    f"  Path escapes repository: {file_part}\n"
                    f"  Resolved to: {target_file}"
                )
                return

            # Check if target file exists
            if not target_file.exists():
                self.errors.append(
                    f"{source_file}:\n"
                    f"  Broken link: [{link_text}]({link_url})\n"
                    f"  Target does not exist: {file_part}\n"
                    f"  Resolved to: {target_file}"
                )
                return

            # If there's an anchor, verify it exists in the target file
            if anchor:
                if target_file.suffix == '.md':
                    target_content = target_file.read_text()
                    target_content = self.strip_html_comments(target_content)
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
                source_content = self.strip_html_comments(source_content)
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

        # Strip # comments before processing
        content = self.strip_script_comments(content)

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

                # Verify the resolved path is within the repository
                try:
                    target_path.relative_to(self.root_dir)
                except ValueError:
                    self.warnings.append(
                        f"{script_file}:\n"
                        f"  Path escapes repository: {match}\n"
                        f"  Resolved to: {target_path}"
                    )
                    continue

                if not target_path.exists():
                    self.warnings.append(
                        f"{script_file}:\n"
                        f"  Possible broken path: {match}\n"
                        f"  Resolved to: {target_path}"
                    )

    def report_results(self, quiet=False):
        """Print verification results."""
        # If quiet and no issues, show concise summary
        if quiet and not self.errors and not self.warnings:
            print(f"✓ Checked {self.checked_files} files, {self.checked_links} links - No errors")
            return 0

        # Verbose output for errors/warnings or non-quiet mode
        print()
        print("=" * 60)
        print("VERIFICATION RESULTS")
        print("=" * 60)
        print(f"Files checked: {self.checked_files}")
        print(f"Links checked: {self.checked_links}")
        print()

        if self.errors:
            print(f"✗ ERRORS FOUND: {len(self.errors)}")
            print("-" * 60)
            for error in self.errors:
                print(error)
                print()
        else:
            print("✓ No errors found!")

        if self.warnings:
            print(f"\n⚠ WARNINGS: {len(self.warnings)}")
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
        # Default to parent directory relative to script location
        script_dir = Path(__file__).parent
        root_dir = script_dir.parent

    if not Path(root_dir).exists():
        print(f"Error: Directory does not exist: {root_dir}")
        sys.exit(1)

    # Step 1: Build (localize shared files)
    builder = Builder(root_dir)
    build_success = builder.build_all(quiet=True)

    if not build_success:
        print("Build failed. Skipping verification.")
        sys.exit(1)

    # Step 2: Verify (check references)
    verifier = ReferenceVerifier(root_dir)
    verify_exit_code = verifier.verify_all(quiet=True)

    # Step 3: Verify docs (check .qmd files exist)
    docs_verifier = DocsVerifier(root_dir)
    docs_exit_code = docs_verifier.verify_all(quiet=True)

    # Final summary
    all_checks_passed = verify_exit_code == 0 and docs_exit_code == 0
    if all_checks_passed:
        print("✅ BUILD AND VERIFY SUCCESSFUL")
    else:
        print("❌ VERIFICATION FAILED - Fix errors above before committing")
    print()

    sys.exit(0 if all_checks_passed else 1)


if __name__ == "__main__":
    main()
