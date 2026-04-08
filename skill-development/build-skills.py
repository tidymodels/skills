#!/usr/bin/env python3
"""
Build skills by localizing shared files.

This script copies files from shared-references/ to each skill's references/ folder.

Usage:
    ./build-skills.py [directory]

    If no directory specified, uses parent directory relative to script location

Examples:
    ./build-skills.py ../developers/
    ./build-skills.py ../users/
"""

import sys
import shutil
from pathlib import Path
from typing import List, Tuple


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
            # Skip if not a directory
            if not item.is_dir():
                continue

            # Skip workspace directories
            if '-workspace' in item.name:
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

    def build_all(self, quiet=False):
        """Copy shared files to each skill's references folder."""
        header = "=" * 14 + " BUILD: Localizing Shared Files " + "=" * 14
        if quiet:
            print(header)
        else:
            print(header)
            print()

        if not self.shared_dir.exists():
            self.errors.append(f"Shared references directory not found: {self.shared_dir}")
            return False

        success = True
        skill_stats = []
        failed_skills = []
        for skill in self.skills:
            md_count, script_count = self.build_skill(skill, quiet=quiet)
            if md_count is None:
                success = False
                failed_skills.append(skill)
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
            print(f"Failed skills: {', '.join(failed_skills)}")
            print(f"Total errors: {len(self.errors)}")
            print()
            for i, error in enumerate(self.errors, 1):
                print(f"  ERROR {i}:")
                for line in error.split('\n'):
                    print(f"    {line}")
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
            error = (f"{skill}: references/ directory not found\n"
                    f"  Expected location: {refs_dir}\n"
                    f"  Each skill must have a references/ subdirectory")
            self.errors.append(error)
            print(f"  ERROR: {error}")
            return None, None

        # Copy shared-references/*.md files
        if not quiet:
            print(f"  Copying shared-references/*.md → {refs_dir.name}/")
        md_files = list(self.shared_dir.glob("*.md"))
        if not md_files:
            error = (f"{skill}: No .md files found in shared-references/\n"
                    f"  Checked directory: {self.shared_dir}\n"
                    f"  This may indicate a missing or empty shared-references directory")
            self.errors.append(error)
            print(f"  WARNING: {error}")

        for md_file in md_files:
            try:
                dest = (refs_dir / md_file.name).resolve()
                # Validate destination is within root_dir
                try:
                    dest.relative_to(self.root_dir)
                except ValueError:
                    error = (f"{skill}: Destination path outside project\n"
                            f"  Source: {md_file}\n"
                            f"  Destination: {dest}")
                    self.errors.append(error)
                    print(f"  ERROR: {error}")
                    return None, None
                shutil.copy2(md_file, dest)
                if not quiet:
                    print(f"    {md_file.name}")
            except Exception as e:
                error = (f"{skill}: Failed to copy shared markdown file\n"
                        f"  File: {md_file.name}\n"
                        f"  Source: {md_file}\n"
                        f"  Destination: {dest}\n"
                        f"  Error: {type(e).__name__}: {e}")
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
                        error = (f"{skill}: Destination path outside project\n"
                                f"  Source: {md_file}\n"
                                f"  Destination: {dest}")
                        self.errors.append(error)
                        print(f"  ERROR: {error}")
                        return None, None
                    shutil.copy2(md_file, dest)
                    parsnip_md_count += 1
                    if not quiet:
                        print(f"    {md_file.name}")
                except Exception as e:
                    error = (f"{skill}: Failed to copy parsnip-specific markdown file\n"
                            f"  File: {md_file.name}\n"
                            f"  Source: {md_file}\n"
                            f"  Destination: {dest}\n"
                            f"  Error: {type(e).__name__}: {e}")
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
                            error = (f"{skill}: Destination path outside project\n"
                                    f"  Source: {script_file}\n"
                                    f"  Destination: {dest}")
                            self.errors.append(error)
                            print(f"  ERROR: {error}")
                            return None, None
                        shutil.copy2(script_file, dest)
                        script_count += 1
                        if not quiet:
                            print(f"    {script_file.name}")
                    except Exception as e:
                        error = (f"{skill}: Failed to copy script file\n"
                                f"  File: {script_file.name}\n"
                                f"  Source: {script_file}\n"
                                f"  Destination: {dest}\n"
                                f"  Error: {type(e).__name__}: {e}")
                        self.errors.append(error)
                        print(f"  ERROR: {error}")
                        return None, None

        if not quiet:
            print(f"  ✓ {skill} complete")
            print()
        return len(md_files) + parsnip_md_count, script_count


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

    # Build skills
    builder = Builder(root_dir)
    build_success = builder.build_all(quiet=True)

    if build_success:
        print("✅ BUILD SUCCESSFUL")
    else:
        print("❌ BUILD FAILED - Fix errors above")

    print()
    sys.exit(0 if build_success else 1)


if __name__ == "__main__":
    main()
