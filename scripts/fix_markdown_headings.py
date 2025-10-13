#!/usr/bin/env python3
"""Normalize heading levels and remove emphasis from Markdown headings.

This utility walks the repository, finds Markdown files, and applies two fixes:
1. Only the first level-one heading is kept; subsequent level-one headings are
   demoted to level two.
2. Bold and italic markers within headings are removed to avoid styling issues.

Any path containing directories such as `node_modules`, `.venv`, or `.archive` is skipped
while traversing the repository.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable

# Regular expressions compiled once for efficiency
H1_PATTERN = re.compile(r"^\s*# ")
HEADING_WITH_EMPHASIS_PATTERN = re.compile(r"^\s*#{1,6} .*(\*\*|\*|__|_)")
EMPHASIS_MARKERS_PATTERN = re.compile(r"(\*\*|\*|__|_)")
EXCLUDED_PARTS = {"node_modules", ".venv", ".archive"}


def iter_markdown_files(root: Path) -> Iterable[Path]:
    """Yield Markdown files underneath *root*, ignoring excluded directories."""
    for current_root, dirs, files in os.walk(root):
        path = Path(current_root)
        # Skip any directory containing an excluded part in its path
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue

        for filename in files:
            if filename.lower().endswith(".md"):
                yield path / filename


def fix_markdown_file(file_path: Path) -> bool:
    """Apply heading corrections to *file_path*.

    Returns ``True`` if the file was modified, otherwise ``False``.
    """
    try:
        original_content = file_path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive guard
        print(f"Error reading {file_path}: {exc}")
        return False

    lines = original_content.splitlines()
    first_h1_seen = False
    modified = False

    for index, line in enumerate(lines):
        if H1_PATTERN.match(line):
            if first_h1_seen:
                lines[index] = H1_PATTERN.sub("## ", line, count=1)
                modified = True
                print(f"  Demoted extra H1 on line {index + 1} in {file_path}")
            else:
                first_h1_seen = True

        if HEADING_WITH_EMPHASIS_PATTERN.match(line):
            cleaned_line = EMPHASIS_MARKERS_PATTERN.sub("", line)
            if cleaned_line != line:
                lines[index] = cleaned_line
                modified = True
                print(f"  Removed emphasis on line {index + 1} in {file_path}")

    if not modified:
        return False

    new_content = "\n".join(lines) + ("\n" if original_content.endswith("\n") else "")
    try:
        file_path.write_text(new_content, encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive guard
        print(f"Error writing {file_path}: {exc}")
        return False

    return True


def main() -> None:
    """Entry point for the CLI script."""
    repo_root = Path(__file__).resolve().parent.parent
    markdown_files = list(iter_markdown_files(repo_root))

    print(f"Found {len(markdown_files)} markdown files to process")

    fixed_count = 0
    for md_file in markdown_files:
        print(f"Processing: {md_file}")
        if fix_markdown_file(md_file):
            fixed_count += 1
            print(f"  Updated: {md_file.name}")
        else:
            print(f"  No changes required for: {md_file.name}")

    print("\n✅ Markdown heading normalization complete")
    print(f"  Files updated: {fixed_count}")
    print(f"  Files unchanged: {len(markdown_files) - fixed_count}")
    print(f"  Total processed: {len(markdown_files)}")


if __name__ == "__main__":
    main()
