#!/usr/bin/env python3
"""
Create docs wrapper files for skill references.

This script generates thin wrapper .qmd files in docs/ that include source .md files.
It handles arbitrary nesting depth and skips scripts/ subdirectories.

Usage:
    ./create-docs-wrappers.py --skill users/tabular-data-ml [--dry-run] [--force]
    ./create-docs-wrappers.py --all

Examples:
    ./create-docs-wrappers.py --skill users/tabular-data-ml --dry-run  # Preview
    ./create-docs-wrappers.py --skill users/tabular-data-ml            # Apply
    ./create-docs-wrappers.py --all                                    # All skills
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class DocsWrapperGenerator:
    """Generates wrapper .qmd files in docs/ for skill reference .md files."""

    def __init__(self, project_root: Path, dry_run: bool = False, force: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.force = force
        self.created_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.errors: List[str] = []

    def process_skill(self, skill_path: str) -> bool:
        """Process a single skill, creating wrappers for all its references.

        Args:
            skill_path: Relative path to skill (e.g., 'users/tabular-data-ml')

        Returns:
            True if successful, False if errors occurred
        """
        skill_full_path = self.project_root / skill_path
        if not skill_full_path.exists():
            self._add_error(f"Skill directory does not exist: {skill_path}")
            return False

        # Check if references/ directory exists
        refs_dir = skill_full_path / "references"
        if not refs_dir.exists():
            print(f"ℹ Skill has no references/ directory: {skill_path}")
            return True

        # Determine audience (developers or users)
        parts = Path(skill_path).parts
        if len(parts) < 2:
            self._add_error(f"Invalid skill path (expected audience/skill): {skill_path}")
            return False

        audience = parts[0]
        skill_name = parts[1]

        # Create docs output directory
        docs_skill_dir = self.project_root / "docs" / audience / skill_name
        docs_refs_dir = docs_skill_dir / "references"

        print(f"\n{'='*60}")
        print(f"Processing: {skill_path}")
        print(f"{'='*60}")
        print(f"Source:  {refs_dir.relative_to(self.project_root)}")
        print(f"Target:  {docs_refs_dir.relative_to(self.project_root)}")

        if self.dry_run:
            print(f"⚠ DRY RUN MODE - No files will be created\n")

        # Walk through all .md files in references/
        md_files = self._find_md_files(refs_dir)

        if not md_files:
            print(f"ℹ No .md files found in references/")
            return True

        print(f"Found {len(md_files)} source .md file(s)\n")

        # Process each .md file
        for md_file in md_files:
            self._create_wrapper(
                md_file,
                refs_dir,
                docs_refs_dir,
                audience,
                skill_name
            )

        # Summary
        print(f"\n{'='*60}")
        print(f"Summary for {skill_path}")
        print(f"{'='*60}")
        print(f"✓ Created: {self.created_count}")
        if self.skipped_count > 0:
            print(f"⊘ Skipped: {self.skipped_count}")
        if self.error_count > 0:
            print(f"✗ Errors: {self.error_count}")

        return self.error_count == 0

    def _find_md_files(self, refs_dir: Path) -> List[Path]:
        """Recursively find all .md files, excluding scripts/ subdirectories."""
        md_files = []
        for path in refs_dir.rglob("*.md"):
            # Skip if in scripts/ subdirectory
            if "scripts" in path.parts:
                continue
            # Skip README.md
            if path.name == "README.md":
                continue
            if path.is_file():
                md_files.append(path)
        return sorted(md_files)

    def _create_wrapper(
        self,
        md_file: Path,
        refs_dir: Path,
        docs_refs_dir: Path,
        audience: str,
        skill_name: str
    ) -> None:
        """Create a wrapper .qmd file for a source .md file.

        Args:
            md_file: Path to source .md file
            refs_dir: Base references/ directory
            docs_refs_dir: Target docs/.../references/ directory
            audience: Audience directory (developers or users)
            skill_name: Skill directory name
        """
        # Get relative path from references/ directory
        rel_path = md_file.relative_to(refs_dir)

        # Calculate depth (how many directories deep from docs/.../references/)
        depth = len(rel_path.parts)  # 1 for flat, 2+ for nested

        # Build target .qmd path
        qmd_path = docs_refs_dir / rel_path.with_suffix('.qmd')

        # Calculate correct number of ../ for include path
        # Base depth is 4 for files directly in references/
        # Add 1 for each level of nesting
        back_levels = 3 + depth  # 3 base + depth

        # Build include path
        include_path_parts = ['..'] * back_levels
        include_path_parts.extend([audience, skill_name, 'references'])
        include_path_parts.extend(rel_path.parts)
        include_path_str = '/'.join(include_path_parts)

        # Check if wrapper already exists
        if qmd_path.exists() and not self.force:
            print(f"⊘ Skipped (exists): {qmd_path.relative_to(self.project_root)}")
            self.skipped_count += 1
            return

        # Validate source file exists (should always be true, but check anyway)
        if not md_file.exists():
            self._add_error(f"Source file does not exist: {md_file}")
            return

        # Create wrapper content
        wrapper_content = f"{{{{< include {include_path_str} >}}}}\n"

        # Show what we're doing
        action = "Would create" if self.dry_run else "Creating"
        print(f"✓ {action}: {qmd_path.relative_to(self.project_root)}")
        if depth > 1:
            print(f"  Depth: {depth} (nested), Back-levels: {back_levels}")

        # Create the wrapper file (unless dry run)
        if not self.dry_run:
            try:
                qmd_path.parent.mkdir(parents=True, exist_ok=True)
                qmd_path.write_text(wrapper_content)
                self.created_count += 1
            except Exception as e:
                self._add_error(f"Failed to create {qmd_path}: {e}")

    def _add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.error_count += 1
        print(f"✗ Error: {message}")


def discover_all_skills(project_root: Path) -> List[str]:
    """Discover all skills in developers/ and users/ directories."""
    skills = []

    for audience in ['developers', 'users']:
        audience_dir = project_root / audience
        if not audience_dir.exists():
            continue

        for skill_dir in audience_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            if skill_dir.name == "shared-references":
                continue

            # Check if it has a references/ directory
            if (skill_dir / "references").exists():
                skills.append(f"{audience}/{skill_dir.name}")

    return sorted(skills)


def main():
    parser = argparse.ArgumentParser(
        description="Generate wrapper .qmd files in docs/ for skill reference .md files"
    )
    parser.add_argument(
        "--skill",
        help="Skill to process (e.g., users/tabular-data-ml)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all skills"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without creating files"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing wrapper files"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.skill and not args.all:
        parser.error("Must specify either --skill or --all")

    if args.skill and args.all:
        parser.error("Cannot specify both --skill and --all")

    # Find project root
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    print("="*60)
    print("Create Docs Wrappers")
    print("="*60)
    print(f"Project root: {project_root}")
    if args.dry_run:
        print("⚠ DRY RUN MODE - No files will be created")
    if args.force:
        print("⚠ FORCE MODE - Will overwrite existing files")

    # Determine which skills to process
    if args.all:
        skills = discover_all_skills(project_root)
        if not skills:
            print("\n✗ No skills found")
            return 1
        print(f"\nFound {len(skills)} skill(s):")
        for skill in skills:
            print(f"  • {skill}")
    else:
        skills = [args.skill]

    # Process each skill
    generator = DocsWrapperGenerator(project_root, args.dry_run, args.force)

    all_successful = True
    for skill in skills:
        success = generator.process_skill(skill)
        if not success:
            all_successful = False

    # Final summary
    print(f"\n{'='*60}")
    print("Final Summary")
    print(f"{'='*60}")
    print(f"Skills processed: {len(skills)}")
    print(f"Wrappers created: {generator.created_count}")
    if generator.skipped_count > 0:
        print(f"Wrappers skipped: {generator.skipped_count}")
    if generator.error_count > 0:
        print(f"Errors: {generator.error_count}")
        print("\nErrors encountered:")
        for error in generator.errors:
            print(f"  • {error}")

    if args.dry_run:
        print("\n⚠ DRY RUN: No actual changes were made")
        print("Run without --dry-run to apply changes")
    elif all_successful:
        print("\n✓ All wrappers created successfully!")

    return 0 if all_successful else 1


if __name__ == "__main__":
    sys.exit(main())
