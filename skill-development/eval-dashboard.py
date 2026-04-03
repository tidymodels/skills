#!/usr/bin/env python3
"""
Evaluation Dashboard Generator

Automatically finds all *-workspace directories, compiles quantitative evaluation results
across iterations, and generates a markdown dashboard summary.

Usage:
    # Search from project root
    python eval-dashboard.py /Users/edgar/Projects/skills-personal/developers

    # Search from specific workspace
    python eval-dashboard.py /Users/edgar/Projects/skills-personal/developers/add-parsnip-engine-workspace

    # Search from specific iteration
    python eval-dashboard.py /Users/edgar/Projects/skills-personal/developers/add-parsnip-engine-workspace/iteration-1

    # Output to specific file
    python eval-dashboard.py ../developers --output evaluation-report.md
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class EvaluationDashboard:
    """Compiles and formats evaluation results across workspaces and iterations."""

    def __init__(self, search_path: Path):
        self.search_path = search_path
        self.workspaces = []

    def find_workspaces(self) -> List[Dict[str, Any]]:
        """Find all workspace directories and their iterations."""
        workspaces = []

        # Check if search_path itself is a workspace or iteration
        if self.search_path.name.endswith('-workspace'):
            workspaces.append(self._process_workspace(self.search_path))
        elif self.search_path.name.startswith('iteration-'):
            # Parent should be the workspace
            workspace_path = self.search_path.parent
            if workspace_path.name.endswith('-workspace'):
                workspace = self._process_workspace(workspace_path, specific_iteration=self.search_path.name)
                workspaces.append(workspace)
        else:
            # Search for all workspaces in directory tree
            for workspace_path in self.search_path.rglob('*-workspace'):
                if workspace_path.is_dir():
                    workspaces.append(self._process_workspace(workspace_path))

        self.workspaces = [w for w in workspaces if w['iterations']]
        return self.workspaces

    def _process_workspace(self, workspace_path: Path, specific_iteration: Optional[str] = None) -> Dict[str, Any]:
        """Process a single workspace and gather iteration data."""
        skill_name = workspace_path.name.replace('-workspace', '')

        workspace_data = {
            'skill_name': skill_name,
            'path': str(workspace_path),
            'iterations': []
        }

        # Find iterations
        if specific_iteration:
            iteration_dirs = [workspace_path / specific_iteration]
        else:
            iteration_dirs = sorted([d for d in workspace_path.iterdir()
                                   if d.is_dir() and d.name.startswith('iteration-')])

        for iteration_dir in iteration_dirs:
            if not iteration_dir.exists():
                continue

            iteration_data = self._process_iteration(iteration_dir)
            if iteration_data:
                workspace_data['iterations'].append(iteration_data)

        return workspace_data

    def _process_iteration(self, iteration_dir: Path) -> Optional[Dict[str, Any]]:
        """Process a single iteration directory."""
        iteration_name = iteration_dir.name

        # Load benchmark.json if it exists
        benchmark_file = iteration_dir / 'benchmark.json'
        benchmark_data = None
        if benchmark_file.exists():
            try:
                with open(benchmark_file) as f:
                    benchmark_data = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {benchmark_file}: {e}")

        # Find all eval directories
        eval_dirs = sorted([d for d in iteration_dir.iterdir()
                          if d.is_dir() and (d.name.startswith('eval-') or d.name == 'eval')])

        if not eval_dirs:
            return None

        iteration_data = {
            'name': iteration_name,
            'path': str(iteration_dir),
            'benchmark': benchmark_data,
            'evaluations': []
        }

        # Process each evaluation
        for eval_dir in eval_dirs:
            eval_data = self._process_evaluation(eval_dir)
            if eval_data:
                iteration_data['evaluations'].append(eval_data)

        return iteration_data if iteration_data['evaluations'] else None

    def _process_evaluation(self, eval_dir: Path) -> Optional[Dict[str, Any]]:
        """Process a single evaluation directory."""
        eval_data = {
            'name': eval_dir.name,
            'path': str(eval_dir),
            'metadata': None,
            'configurations': {}
        }

        # Load metadata
        metadata_file = eval_dir / 'eval_metadata.json'
        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    eval_data['metadata'] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {metadata_file}: {e}")

        # Find configuration directories (with_skill, without_skill, old_skill)
        for config_dir in eval_dir.iterdir():
            if not config_dir.is_dir():
                continue

            config_name = config_dir.name
            if config_name in ['with_skill', 'without_skill', 'old_skill', 'outputs']:
                if config_name == 'outputs':
                    continue

                config_data = {
                    'name': config_name,
                    'grading': None,
                    'timing': None
                }

                # Load grading results
                grading_file = config_dir / 'grading.json'
                if grading_file.exists():
                    try:
                        with open(grading_file) as f:
                            config_data['grading'] = json.load(f)
                    except Exception as e:
                        print(f"Warning: Could not load {grading_file}: {e}")

                # Load timing data
                timing_file = config_dir / 'timing.json'
                if timing_file.exists():
                    try:
                        with open(timing_file) as f:
                            config_data['timing'] = json.load(f)
                    except Exception as e:
                        print(f"Warning: Could not load {timing_file}: {e}")

                eval_data['configurations'][config_name] = config_data

        return eval_data if eval_data['configurations'] else None

    def generate_markdown(self) -> str:
        """Generate markdown dashboard from workspace data."""
        if not self.workspaces:
            return "# Evaluation Dashboard\n\nNo evaluation workspaces found.\n"

        md = ["# Evaluation Dashboard\n"]
        md.append(f"**Search Path:** `{self.search_path}`\n")
        md.append(f"**Workspaces Found:** {len(self.workspaces)}\n")

        # Table of contents
        md.append("## Table of Contents\n")
        for i, workspace in enumerate(self.workspaces, 1):
            md.append(f"{i}. [{workspace['skill_name']}](#{workspace['skill_name'].replace('_', '-')})")
        md.append("\n---\n")

        # Process each workspace
        for workspace in self.workspaces:
            md.extend(self._format_workspace(workspace))

        return "\n".join(md)

    def _format_workspace(self, workspace: Dict[str, Any]) -> List[str]:
        """Format a single workspace section."""
        md = [f"## {workspace['skill_name']}\n"]
        md.append(f"**Path:** `{workspace['path']}`\n")
        md.append(f"**Iterations:** {len(workspace['iterations'])}\n")

        # Summary across all iterations
        md.append("### Summary Across Iterations\n")
        md.extend(self._format_iteration_summary(workspace['iterations']))

        # Detailed iteration breakdown
        md.append("### Iteration Details\n")
        for iteration in workspace['iterations']:
            md.extend(self._format_iteration(iteration, workspace['skill_name']))

        md.append("\n---\n")
        return md

    def _format_iteration_summary(self, iterations: List[Dict[str, Any]]) -> List[str]:
        """Create summary table across iterations."""
        md = []

        if not iterations:
            md.append("No iteration data available.\n")
            return md

        # Check if we have benchmark data
        has_benchmark = any(it.get('benchmark') for it in iterations)

        if has_benchmark:
            md.append("| Iteration | Pass Rate (with_skill) | Pass Rate (baseline) | Δ Pass Rate | Duration (s) | Tokens |\n")
            md.append("|-----------|----------------------|---------------------|-------------|--------------|--------|\n")

            for iteration in iterations:
                benchmark = iteration.get('benchmark')
                if not benchmark:
                    continue

                iter_name = iteration['name']

                with_skill = benchmark.get('with_skill', {})
                baseline_key = 'without_skill' if 'without_skill' in benchmark else 'old_skill'
                baseline = benchmark.get(baseline_key, {})

                ws_pr = with_skill.get('pass_rate', {}).get('mean', 0)
                bl_pr = baseline.get('pass_rate', {}).get('mean', 0)
                delta_pr = ws_pr - bl_pr

                ws_dur = with_skill.get('duration_seconds', {}).get('mean', 0)
                ws_tok = with_skill.get('total_tokens', {}).get('mean', 0)

                delta_sign = "🟢" if delta_pr > 0 else "🔴" if delta_pr < 0 else "⚪"

                md.append(f"| {iter_name} | {ws_pr:.1%} | {bl_pr:.1%} | {delta_sign} {delta_pr:+.1%} | {ws_dur:.1f} | {ws_tok:,.0f} |\n")
        else:
            # Fallback: count evals
            md.append("| Iteration | Evaluations | Configurations |\n")
            md.append("|-----------|-------------|----------------|\n")

            for iteration in iterations:
                iter_name = iteration['name']
                eval_count = len(iteration.get('evaluations', []))

                # Count unique configurations
                configs = set()
                for eval_data in iteration.get('evaluations', []):
                    configs.update(eval_data.get('configurations', {}).keys())

                md.append(f"| {iter_name} | {eval_count} | {', '.join(sorted(configs))} |\n")

        md.append("\n")
        return md

    def _format_iteration(self, iteration: Dict[str, Any], skill_name: str) -> List[str]:
        """Format a single iteration section."""
        md = [f"#### {iteration['name']}\n"]

        benchmark = iteration.get('benchmark')

        if benchmark:
            # Use benchmark data for summary
            md.extend(self._format_benchmark(benchmark))

        # Per-evaluation breakdown
        if iteration['evaluations']:
            md.append("**Per-Evaluation Breakdown:**\n")
            md.extend(self._format_evaluations(iteration['evaluations']))

        return md

    def _format_benchmark(self, benchmark: Dict[str, Any]) -> List[str]:
        """Format benchmark data."""
        md = []

        with_skill = benchmark.get('with_skill', {})
        baseline_key = 'without_skill' if 'without_skill' in benchmark else 'old_skill'
        baseline = benchmark.get(baseline_key, {})

        md.append("**Aggregate Metrics:**\n")
        md.append("| Metric | with_skill | baseline | Δ |\n")
        md.append("|--------|-----------|----------|---|\n")

        # Pass rate
        ws_pr = with_skill.get('pass_rate', {})
        bl_pr = baseline.get('pass_rate', {})
        if ws_pr and bl_pr:
            delta = ws_pr.get('mean', 0) - bl_pr.get('mean', 0)
            md.append(f"| Pass Rate | {ws_pr.get('mean', 0):.1%} ± {ws_pr.get('stdev', 0):.1%} | "
                     f"{bl_pr.get('mean', 0):.1%} ± {bl_pr.get('stdev', 0):.1%} | {delta:+.1%} |\n")

        # Duration
        ws_dur = with_skill.get('duration_seconds', {})
        bl_dur = baseline.get('duration_seconds', {})
        if ws_dur and bl_dur:
            delta = ws_dur.get('mean', 0) - bl_dur.get('mean', 0)
            md.append(f"| Duration (s) | {ws_dur.get('mean', 0):.1f} ± {ws_dur.get('stdev', 0):.1f} | "
                     f"{bl_dur.get('mean', 0):.1f} ± {bl_dur.get('stdev', 0):.1f} | {delta:+.1f} |\n")

        # Tokens
        ws_tok = with_skill.get('total_tokens', {})
        bl_tok = baseline.get('total_tokens', {})
        if ws_tok and bl_tok:
            delta = ws_tok.get('mean', 0) - bl_tok.get('mean', 0)
            md.append(f"| Tokens | {ws_tok.get('mean', 0):,.0f} ± {ws_tok.get('stdev', 0):,.0f} | "
                     f"{bl_tok.get('mean', 0):,.0f} ± {bl_tok.get('stdev', 0):,.0f} | {delta:+,.0f} |\n")

        md.append("\n")
        return md

    def _format_evaluations(self, evaluations: List[Dict[str, Any]]) -> List[str]:
        """Format evaluation breakdown table."""
        md = []

        md.append("| Eval | Context | Pass Rate (with) | Pass Rate (baseline) | Duration (with) | Tokens (with) |\n")
        md.append("|------|---------|-----------------|---------------------|-----------------|---------------|\n")

        for eval_data in evaluations:
            eval_name = eval_data.get('name', 'Unknown')
            metadata = eval_data.get('metadata', {})
            context = metadata.get('context', 'unknown') if metadata else 'unknown'

            configs = eval_data.get('configurations', {})

            # Get with_skill data
            with_skill = configs.get('with_skill', {})
            ws_grading = with_skill.get('grading', {})
            ws_timing = with_skill.get('timing', {})

            ws_pr = ws_grading.get('summary', {}).get('pass_rate', 0) if ws_grading else 0
            ws_dur = ws_timing.get('total_duration_seconds', 0) if ws_timing else 0
            ws_tok = ws_timing.get('total_tokens', 0) if ws_timing else 0

            # Get baseline data
            baseline = configs.get('without_skill') or configs.get('old_skill', {})
            bl_grading = baseline.get('grading', {})
            bl_pr = bl_grading.get('summary', {}).get('pass_rate', 0) if bl_grading else 0

            md.append(f"| {eval_name} | {context} | {ws_pr:.1%} | {bl_pr:.1%} | {ws_dur:.1f}s | {ws_tok:,} |\n")

        md.append("\n")
        return md


def main():
    parser = argparse.ArgumentParser(
        description='Generate evaluation dashboard from workspace results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        'path',
        help='Path to search (project folder, workspace, or iteration)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output markdown file (default: eval-dashboard.md)'
    )

    args = parser.parse_args()

    search_path = Path(args.path).resolve()
    if not search_path.exists():
        print(f"Error: Path does not exist: {search_path}")
        return 1

    # Generate dashboard
    dashboard = EvaluationDashboard(search_path)
    print(f"Searching for workspaces in: {search_path}")
    workspaces = dashboard.find_workspaces()

    if not workspaces:
        print("No evaluation workspaces found.")
        return 1

    print(f"Found {len(workspaces)} workspace(s):")
    for ws in workspaces:
        print(f"  - {ws['skill_name']} ({len(ws['iterations'])} iterations)")

    # Generate markdown
    markdown = dashboard.generate_markdown()

    # Output
    output_file = args.output or 'eval-dashboard.md'
    output_path = Path(output_file)

    with open(output_path, 'w') as f:
        f.write(markdown)

    print(f"\nDashboard generated: {output_path.resolve()}")
    print(f"Total size: {len(markdown)} characters")

    return 0


if __name__ == '__main__':
    sys.exit(main())
