#!/usr/bin/env python3
"""
Verify that skills have corresponding .qmd files in docs/.

This script confirms that each skill has a corresponding .qmd file in docs/,
and that each .md file in the skill's references/ folder has a matching .qmd
in docs/*/references/

Usage:
    ./verify-docs.py [directory]

    If no directory specified, uses parent directory relative to script location

Examples:
    ./verify-docs.py ../developers/
    ./verify-docs.py ../users/
"""

import sys
from pathlib import Path
from typing import List


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
        header = "=" * 17 + " DOCS: Checking .qmd files " + "=" * 16
        if quiet:
            print(header)
        else:
            print(header)
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
            # Skip if not a directory
            if not item.is_dir():
                continue

            # Skip workspace directories
            if '-workspace' in item.name:
                print(f"Skipping {item.name}")
                continue

            # Skip shared-references directories
            if item.name in ["shared-references", "shared-references-parsnip"]:
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

    # Verify docs
    docs_verifier = DocsVerifier(root_dir)
    docs_exit_code = docs_verifier.verify_all(quiet=True)

    if docs_exit_code == 0:
        print("✅ DOCS VERIFICATION SUCCESSFUL")
    else:
        print("❌ DOCS VERIFICATION FAILED - Fix errors above")

    print()
    sys.exit(docs_exit_code)


if __name__ == "__main__":
    main()
