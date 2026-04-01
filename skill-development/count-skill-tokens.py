#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "frontmatter",
#   "tiktoken",
# ]
# ///

"""Count lines and estimate tokens for a Claude Code skill directory.

Usage:
    ./count-skill-tokens.py <skill-directory>
    uv run count-skill-tokens.py shiny/shiny-bslib

Finds SKILL.md and references/**/*.md, counts lines and tokens (cl100k_base),
and outputs a Markdown summary table.
"""

import sys
from pathlib import Path

import tiktoken
from frontmatter import Frontmatter


def count_tokens(text: str, encoding: tiktoken.Encoding) -> int:
    return len(encoding.encode(text))


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <skill-directory>", file=sys.stderr)
        sys.exit(1)

    # Determine project root (grandparent of script directory)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    skill_dir = Path(sys.argv[1]).resolve()

    # Validate skill_dir is within project_root
    try:
        skill_dir.relative_to(project_root)
    except ValueError:
        print(f"Error: Skill directory is outside project directory", file=sys.stderr)
        print(f"  Skill dir: {skill_dir}", file=sys.stderr)
        print(f"  Project root: {project_root}", file=sys.stderr)
        print(f"  Only directories within the project can be analyzed", file=sys.stderr)
        sys.exit(1)

    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        print(f"Error: {skill_md} not found", file=sys.stderr)
        sys.exit(1)

    enc = tiktoken.get_encoding("cl100k_base")

    # Parse SKILL.md frontmatter
    parsed = Frontmatter.read_file(str(skill_md))
    attrs = parsed["attributes"]
    skill_name = attrs.get("name", skill_dir.name)
    skill_description = attrs.get("description", "")

    # Collect files: SKILL.md first, then references sorted alphabetically
    files: list[Path] = [skill_md]
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        files.extend(sorted(refs_dir.rglob("*.md")))

    # Count lines and tokens per file
    rows: list[tuple[str, int, int]] = []
    total_lines = 0
    total_tokens = 0

    for f in files:
        text = f.read_text()
        n_lines = text.count("\n")
        # Match wc -l: count newlines (trailing newline = last line counted)
        if text and not text.endswith("\n"):
            n_lines += 1
        n_tokens = count_tokens(text, enc)
        rel_path = f.relative_to(skill_dir)
        rows.append((str(rel_path), n_lines, n_tokens))
        total_lines += n_lines
        total_tokens += n_tokens

    # Description tokens
    desc_tokens = count_tokens(skill_description, enc) if skill_description else 0

    # Limits
    METADATA_TOKEN_LIMIT = 100
    SKILL_TOKEN_LIMIT = 5000
    SKILL_LINE_LIMIT = 500

    # Output
    print(f"### {skill_name} ({total_lines:,} lines, ~{total_tokens:,} tokens)")
    print()
    if skill_description:
        desc_warn = " ⚠️" if desc_tokens > METADATA_TOKEN_LIMIT else ""
        print(f"Skill description: ~{desc_tokens:,} tokens{desc_warn}")
        print()
        print(f"> {skill_description}")
        print()

    # Table
    print("| File | Lines | ~Tokens |")
    print("|---|---:|---:|")
    for rel_path, n_lines, n_tokens in rows:
        warn = ""
        if rel_path == "SKILL.md":
            if n_tokens > SKILL_TOKEN_LIMIT or n_lines > SKILL_LINE_LIMIT:
                warn = " ⚠️"
        print(f"| {rel_path} | {n_lines:,} | {n_tokens:,} |{warn}")


if __name__ == "__main__":
    main()
