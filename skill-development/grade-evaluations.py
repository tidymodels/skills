#!/usr/bin/env python3
"""
Centralized grading script for skill evaluations.

Usage:
    python grade-evaluations.py <workspace_path> --config <config_json>
    python grade-evaluations.py ../developers/add-yardstick-metric-workspace/iteration-1 \\
        --config ../developers/add-yardstick-metric/evals/grading-config.json

Or with auto-detection:
    python grade-evaluations.py ../developers/add-yardstick-metric-workspace/iteration-1 \\
        --skill add-yardstick-metric

The script:
1. Reads grading configuration (checks to perform per eval)
2. Scans workspace/iteration-N/eval-M-name/outputs/ directories
3. Runs checks (file counts, pattern matching, function presence, etc.)
4. Generates grading.json for each eval with pass/fail + evidence
5. Creates summary report

Configuration format (JSON):
{
  "skill_name": "add-yardstick-metric",
  "checks": {
    "file_count": {"type": "exact|range|max", "value": 2 or [2,3]},
    "prohibited_files": ["IMPLEMENTATION_SUMMARY.md", "QUICKSTART.md", ...],
    "required_files": ["R/*.R", "tests/testthat/test-*.R"],
    "patterns": {
      "has_three_functions": {
        "file": "R/*.R",
        "patterns": ["_impl\\(", "_vec\\(", "\\.data\\.frame.*<-.*function"],
        "logic": "all"  # all patterns must be present
      }
    },
    "prefix_usage": {
      "extension": {"file": "R/*.R", "prefix": "yardstick::", "min_count": 3},
      "source": {"file": "R/*.R", "prefix": "yardstick::", "max_count": 0}
    }
  }
}
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import glob


class GradingCheck:
    """Base class for different types of grading checks."""

    def __init__(self, name: str, description: str, optional: bool = False):
        self.name = name
        self.description = description
        self.optional = optional

    def run(self, outputs_dir: Path) -> Tuple[bool, str]:
        """Run check and return (passed, evidence)."""
        raise NotImplementedError


class FileCountCheck(GradingCheck):
    """Check number of files created."""

    def __init__(self, name: str, expected: Any, check_type: str = "exact"):
        """
        Args:
            expected: int for exact, tuple for range, int for max
            check_type: 'exact', 'range', 'max'
        """
        super().__init__(name, f"File count check: {check_type} {expected}")
        self.expected = expected
        self.check_type = check_type

    def run(self, outputs_dir: Path) -> Tuple[bool, str]:
        if not outputs_dir.exists():
            return False, f"Directory not found: {outputs_dir}"

        # Count all files (not directories)
        files = [f for f in outputs_dir.rglob("*") if f.is_file() and not f.name.startswith('.')]
        count = len(files)

        if self.check_type == "exact":
            passed = count == self.expected
            evidence = f"Created {count} files (expected exactly {self.expected})"
        elif self.check_type == "range":
            min_val, max_val = self.expected
            passed = min_val <= count <= max_val
            evidence = f"Created {count} files (expected {min_val}-{max_val})"
        elif self.check_type == "max":
            passed = count <= self.expected
            evidence = f"Created {count} files (expected max {self.expected})"
        else:
            return False, f"Unknown check type: {self.check_type}"

        if files:
            evidence += f"\nFiles: {', '.join(f.name for f in files)}"

        return passed, evidence


class ProhibitedFilesCheck(GradingCheck):
    """Check that certain files were NOT created."""

    def __init__(self, name: str, prohibited: List[str]):
        super().__init__(name, f"Prohibited files check: {len(prohibited)} patterns")
        self.prohibited = prohibited

    def run(self, outputs_dir: Path) -> Tuple[bool, str]:
        if not outputs_dir.exists():
            return True, "No output directory (no files created)"

        files = [f for f in outputs_dir.rglob("*") if f.is_file()]
        violations = []

        for pattern in self.prohibited:
            for file in files:
                if self._matches_pattern(file.name, pattern):
                    violations.append(file.name)

        if violations:
            return False, f"Prohibited files created: {', '.join(violations)}"
        else:
            return True, f"No prohibited files created (checked {len(self.prohibited)} patterns)"

    @staticmethod
    def _matches_pattern(filename: str, pattern: str) -> bool:
        """Simple pattern matching (exact or glob-style)."""
        if '*' in pattern:
            regex = pattern.replace('*', '.*').replace('?', '.')
            return bool(re.match(regex, filename, re.IGNORECASE))
        else:
            return filename.lower() == pattern.lower()


class RequiredFilesCheck(GradingCheck):
    """Check that required files exist."""

    def __init__(self, name: str, required: List[str]):
        super().__init__(name, f"Required files check: {len(required)} patterns")
        self.required = required

    def run(self, outputs_dir: Path) -> Tuple[bool, str]:
        if not outputs_dir.exists():
            return False, f"Directory not found: {outputs_dir}"

        missing = []
        found = []

        for pattern in self.required:
            matches = list(outputs_dir.glob(pattern))
            if not matches:
                missing.append(pattern)
            else:
                found.append(f"{pattern} → {', '.join(m.name for m in matches)}")

        if missing:
            return False, f"Missing required files: {', '.join(missing)}"
        else:
            return True, f"All required files present:\n" + "\n".join(found)


class PatternCheck(GradingCheck):
    """Check for patterns in files (grep-like)."""

    def __init__(self, name: str, description: str, file_pattern: str,
                 patterns: List[str], logic: str = "all", optional: bool = False,
                 exclude_files: Optional[List[str]] = None,
                 skip_comment_lines: bool = False):
        """
        Args:
            file_pattern: glob pattern for files to check (e.g., "R/*.R")
            patterns: list of regex patterns to search for
            logic: 'all' (all must be present), 'any' (at least one), 'none' (none present)
            optional: if True, failures do not count against the score
            exclude_files: glob patterns for files to exclude from the check
            skip_comment_lines: if True, lines starting with # are excluded before matching
        """
        super().__init__(name, description, optional=optional)
        self.file_pattern = file_pattern
        self.patterns = patterns
        self.logic = logic
        self.exclude_files = exclude_files or []
        self.skip_comment_lines = skip_comment_lines

    def run(self, outputs_dir: Path) -> Tuple[bool, str]:
        if not outputs_dir.exists():
            return False, f"Directory not found: {outputs_dir}"

        all_files = list(outputs_dir.glob(self.file_pattern))
        excluded = set()
        for exc_pattern in self.exclude_files:
            excluded.update(outputs_dir.glob(exc_pattern))
        files = [f for f in all_files if f not in excluded]
        if not files:
            return False, f"No files matching pattern: {self.file_pattern}"

        found_patterns = {pattern: [] for pattern in self.patterns}

        for file in files:
            try:
                content = file.read_text()
                if self.skip_comment_lines:
                    content = "\n".join(
                        line for line in content.splitlines()
                        if not line.lstrip().startswith("#")
                    )
                for pattern in self.patterns:
                    if re.search(pattern, content, re.MULTILINE):
                        found_patterns[pattern].append(file.name)
            except Exception as e:
                return False, f"Error reading {file.name}: {e}"

        # Evaluate based on logic
        if self.logic == "all":
            missing = [p for p, files in found_patterns.items() if not files]
            if missing:
                return False, f"Missing patterns: {', '.join(missing)}"
            else:
                evidence = "All patterns found:\n" + "\n".join(
                    f"  - {p}: {', '.join(files)}" for p, files in found_patterns.items()
                )
                return True, evidence

        elif self.logic == "any":
            found_any = any(files for files in found_patterns.values())
            if found_any:
                evidence = "Found patterns:\n" + "\n".join(
                    f"  - {p}: {', '.join(files)}" for p, files in found_patterns.items() if files
                )
                return True, evidence
            else:
                return False, "No patterns found"

        elif self.logic == "none":
            found_any = any(files for files in found_patterns.values())
            if found_any:
                violations = [f"{p} in {', '.join(files)}"
                             for p, files in found_patterns.items() if files]
                return False, f"Prohibited patterns found:\n" + "\n".join(f"  - {v}" for v in violations)
            else:
                return True, f"No prohibited patterns found (checked {len(self.patterns)} patterns)"

        else:
            return False, f"Unknown logic: {self.logic}"


class PrefixUsageCheck(GradingCheck):
    """Check for prefix usage (e.g., yardstick::, recipes::)."""

    def __init__(self, name: str, file_pattern: str, prefix: str,
                 min_count: Optional[int] = None, max_count: Optional[int] = None):
        super().__init__(name, f"Prefix usage check: {prefix}")
        self.file_pattern = file_pattern
        self.prefix = prefix
        self.min_count = min_count
        self.max_count = max_count

    def run(self, outputs_dir: Path) -> Tuple[bool, str]:
        if not outputs_dir.exists():
            return False, f"Directory not found: {outputs_dir}"

        files = list(outputs_dir.glob(self.file_pattern))
        if not files:
            return False, f"No files matching pattern: {self.file_pattern}"

        total_count = 0
        per_file = {}

        for file in files:
            try:
                content = file.read_text()
                count = len(re.findall(re.escape(self.prefix) + r'(?!:)', content))
                total_count += count
                per_file[file.name] = count
            except Exception as e:
                return False, f"Error reading {file.name}: {e}"

        # Check constraints
        passed = True
        evidence_parts = [f"Total {self.prefix} usage: {total_count} occurrences"]

        if self.min_count is not None and total_count < self.min_count:
            passed = False
            evidence_parts.append(f"FAIL: Expected at least {self.min_count} occurrences")

        if self.max_count is not None and total_count > self.max_count:
            passed = False
            evidence_parts.append(f"FAIL: Expected at most {self.max_count} occurrences")

        if passed and self.min_count is not None:
            evidence_parts.append(f"PASS: At least {self.min_count} occurrences found")
        if passed and self.max_count is not None:
            evidence_parts.append(f"PASS: At most {self.max_count} occurrences found")

        # Add per-file breakdown
        evidence_parts.append("Per-file breakdown:")
        for fname, count in per_file.items():
            evidence_parts.append(f"  - {fname}: {count}")

        return passed, "\n".join(evidence_parts)


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load grading configuration from JSON file."""
    with open(config_path) as f:
        return json.load(f)


def create_checks_from_config(config: Dict[str, Any], eval_context: str) -> List[GradingCheck]:
    """
    Create check objects from configuration.

    Args:
        config: Configuration dict
        eval_context: 'extension' or 'source' to determine which checks apply
    """
    checks = []
    checks_config = config.get("checks", {})

    # File count check
    if "file_count" in checks_config:
        fc = checks_config["file_count"]
        if eval_context in fc:
            fc_config = fc[eval_context]
            check_type = fc_config.get("type", "exact")
            value = fc_config["value"]
            checks.append(FileCountCheck("file_count", value, check_type))

    # Prohibited files
    if "prohibited_files" in checks_config:
        prohibited = checks_config["prohibited_files"]
        checks.append(ProhibitedFilesCheck("prohibited_files", prohibited))

    # Required files
    if "required_files" in checks_config:
        if eval_context in checks_config["required_files"]:
            required = checks_config["required_files"][eval_context]
            checks.append(RequiredFilesCheck("required_files", required))

    # Pattern checks
    if "patterns" in checks_config:
        patterns_config = checks_config["patterns"]
        if eval_context in patterns_config:
            for check_name, check_config in patterns_config[eval_context].items():
                checks.append(PatternCheck(
                    check_name,
                    check_config.get("description", check_name),
                    check_config["file_pattern"],
                    check_config["patterns"],
                    check_config.get("logic", "all"),
                    optional=check_config.get("optional", False),
                    exclude_files=check_config.get("exclude_files", []),
                    skip_comment_lines=check_config.get("skip_comment_lines", False)
                ))

    # Prefix usage
    if "prefix_usage" in checks_config:
        if eval_context in checks_config["prefix_usage"]:
            pu = checks_config["prefix_usage"][eval_context]
            checks.append(PrefixUsageCheck(
                "prefix_usage",
                pu["file_pattern"],
                pu["prefix"],
                pu.get("min_count"),
                pu.get("max_count")
            ))

    return checks


def grade_eval(eval_dir: Path, checks: List[GradingCheck]) -> Dict[str, Any]:
    """Grade a single evaluation."""
    outputs_dir = eval_dir / "outputs"

    results = {
        "eval_name": eval_dir.name,
        "checks": [],
        "total_checks": len(checks),
        "passed_checks": 0,
        "failed_checks": 0
    }

    optional_checks = 0
    for check in checks:
        passed, evidence = check.run(outputs_dir)
        is_optional = getattr(check, "optional", False)

        results["checks"].append({
            "name": check.name,
            "description": check.description,
            "passed": passed,
            "optional": is_optional,
            "evidence": evidence
        })

        if is_optional:
            optional_checks += 1
        elif passed:
            results["passed_checks"] += 1
        else:
            results["failed_checks"] += 1

    # Scored checks exclude optional ones
    scored = results["total_checks"] - optional_checks
    results["scored_checks"] = scored
    results["optional_checks"] = optional_checks
    results["pass_rate"] = results["passed_checks"] / scored if scored > 0 else 0

    return results


def detect_eval_context(eval_dir: Path) -> str:
    """Detect if eval is extension or source development based on metadata or outputs."""
    # Priority 1: Use explicit context field from eval_metadata.json
    metadata_file = eval_dir / "eval_metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
                # Check for explicit context field first
                if "context" in metadata:
                    context = metadata["context"].lower()
                    if context in ("extension", "source", "refusal"):
                        return context
                # Fallback: analyze prompt text
                prompt = metadata.get("prompt", "").lower()
                if "extension" in prompt or "my own package" in prompt or "my package" in prompt:
                    return "extension"
                if "pr" in prompt or "contributing" in prompt or "tidymodels/" in prompt or "fork" in prompt:
                    return "source"
        except Exception as e:
            print(f"  Warning: Could not read eval_metadata.json: {e}")

    # Priority 2: Check outputs directory for patterns
    outputs_dir = eval_dir / "outputs"
    if outputs_dir.exists():
        r_files = list(outputs_dir.glob("R/*.R")) or list(outputs_dir.glob("*.R")) or list(outputs_dir.glob("**/*.R"))
        for f in r_files:
            try:
                content = f.read_text()
                # Source dev uses no prefix, extension uses prefix
                if "yardstick::" in content or "recipes::" in content or "dials::" in content:
                    return "extension"
            except Exception:
                pass

    # Default to extension
    return "extension"


def main():
    parser = argparse.ArgumentParser(description="Grade skill evaluation outputs")
    parser.add_argument("workspace", help="Path to workspace/iteration-N directory")
    parser.add_argument("--config", help="Path to grading config JSON file")
    parser.add_argument("--skill", help="Skill name (for auto-config detection)")
    parser.add_argument("--output", help="Output file for grading results (default: grading-summary.json)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-check detail during grading")

    args = parser.parse_args()

    workspace = Path(args.workspace)
    if not workspace.exists():
        print(f"Error: Workspace not found: {workspace}")
        return 1

    # Load or auto-detect config
    if args.config:
        config = load_config(Path(args.config))
    elif args.skill:
        # Try to find config in ../developers/<skill>/evals/grading-config.json
        config_path = workspace.parent.parent / args.skill / "evals" / "grading-config.json"
        if config_path.exists():
            config = load_config(config_path)
        else:
            print(f"Error: Config not found at {config_path}")
            print("Please provide --config or create grading-config.json")
            return 1
    else:
        print("Error: Must provide either --config or --skill")
        return 1

    # Find all eval directories
    eval_dirs = sorted([d for d in workspace.iterdir() if d.is_dir() and d.name.startswith("eval-")])

    if not eval_dirs:
        print(f"No evaluation directories found in {workspace}")
        return 1

    if args.verbose:
        print(f"Found {len(eval_dirs)} evaluations to grade")
        print(f"Skill: {config.get('skill_name', 'unknown')}")
        print()

    # Grade each eval
    all_results = []

    for eval_dir in eval_dirs:
        if args.verbose:
            print(f"Grading {eval_dir.name}...")

        # Detect context (extension vs source)
        context = detect_eval_context(eval_dir)
        if args.verbose:
            print(f"  Context detected: {context}")

        # Create checks for this context
        checks = create_checks_from_config(config, context)
        if args.verbose:
            print(f"  Running {len(checks)} checks...")

        # Grade
        results = grade_eval(eval_dir, checks)
        all_results.append(results)

        # Save individual grading.json
        grading_file = eval_dir / "grading.json"
        with open(grading_file, 'w') as f:
            json.dump(results, f, indent=2)

        if args.verbose:
            scored = results.get('scored_checks', results['total_checks'])
            print(f"  Result: {results['passed_checks']}/{scored} scored checks passed ({results['pass_rate']:.1%})")
            if results.get('optional_checks', 0) > 0:
                print(f"  ({results['optional_checks']} optional checks not counted)")
            if results['failed_checks'] > 0:
                print(f"  Failed checks:")
                for check in results['checks']:
                    if not check['passed'] and not check.get('optional', False):
                        print(f"    - {check['name']}: {check['evidence'].split(chr(10))[0]}")
            print()

    # Summary
    total_checks = sum(r.get('scored_checks', r['total_checks']) for r in all_results)
    total_passed = sum(r['passed_checks'] for r in all_results)
    overall_pass_rate = total_passed / total_checks if total_checks > 0 else 0

    summary = {
        "skill_name": config.get("skill_name"),
        "workspace": str(workspace),
        "total_evals": len(all_results),
        "total_checks": total_checks,
        "passed_checks": total_passed,
        "failed_checks": total_checks - total_passed,
        "overall_pass_rate": overall_pass_rate,
        "per_eval_results": all_results
    }

    # Save summary
    output_file = args.output or workspace / "grading-summary.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Build human-readable table
    col_eval = 32
    col_score = 12

    lines = []
    lines.append("=" * 60)
    lines.append(f"RESULTS: {config.get('skill_name')}  ({total_passed}/{total_checks} checks, {overall_pass_rate:.1%})")
    lines.append("=" * 60)
    lines.append(f"{'Eval':<{col_eval}} {'Score':>{col_score}}  Failed checks")
    lines.append("-" * 60)

    for r in all_results:
        scored = r.get('scored_checks', r['total_checks'])
        bar = "PASS" if r['pass_rate'] == 1.0 else f"{r['passed_checks']}/{scored}"
        name = r['eval_name']
        failed_names = [c['name'] for c in r['checks'] if not c['passed'] and not c.get('optional', False)]
        fail_str = ", ".join(failed_names) if failed_names else ""
        lines.append(f"{name:<{col_eval}} {bar:>{col_score}}  {fail_str}")

    lines.append("-" * 60)
    status = "PASS" if overall_pass_rate == 1.0 else f"{total_passed}/{total_checks} ({overall_pass_rate:.1%})"
    lines.append(f"{'OVERALL':<{col_eval}} {status:>{col_score}}")

    table = "\n".join(lines)

    # Save table as text file
    report_file = Path(str(output_file).replace(".json", "-report.txt"))
    with open(report_file, 'w') as f:
        f.write(table + "\n")

    print(table)
    print(f"\nReport saved to: {report_file}")

    return 0 if overall_pass_rate >= 0.8 else 1


if __name__ == "__main__":
    sys.exit(main())
