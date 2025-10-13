#!/usr/bin/env python3
"""Normalize heading levels and remove emphasis from Markdown headings.

This utility walks the repository, finds Markdown files, and applies two fixes:
1. Only the first level-one heading is kept; subsequent level-one headings are
   demoted to level two.
2. Bold and italic markers within headings are removed to avoid styling issues.

Directories such as ``node_modules``, ``.venv``, and ``.archive`` are skipped
while traversing the repository.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, Tuple

# Regular expressions compiled once for efficiency
HEADING_PATTERN = re.compile(
    r"^(?P<indent>\s*)(?P<hashes>#{1,6})(?P<space>\s+)(?P<content>.*)$"
)
EXCLUDED_PARTS = {"node_modules", ".venv", ".archive", ".git"}
EMPHASIS_MARKERS = ("**", "__", "*", "_")
CODE_FENCE_PATTERN = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})")


def iter_markdown_files(root: Path) -> Iterable[Path]:
    """Yield Markdown files underneath *root*, ignoring excluded directories."""
    for current_root, dirs, files in os.walk(root):
        path = Path(current_root)

        # Prune excluded directories in-place to avoid walking them entirely
        dirs[:] = [d for d in dirs if d not in EXCLUDED_PARTS]

        # Skip traversal when the current path already includes an excluded directory
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

    current_fence: str | None = None

    for index, line in enumerate(lines):
        fence_match = CODE_FENCE_PATTERN.match(line)
        if fence_match:
            fence = fence_match.group("fence")
            if current_fence is None:
                current_fence = fence
            elif fence == current_fence:
                current_fence = None
            continue

        if current_fence is not None:
            continue

        heading_match = HEADING_PATTERN.match(line)
        if not heading_match:
            continue

        indent = heading_match.group("indent")
        hashes = heading_match.group("hashes")
        space = heading_match.group("space")
        content = heading_match.group("content")
        content_leading_stripped = content.lstrip()
        is_h1_candidate = (
            bool(content_leading_stripped)
            and (
                not content_leading_stripped[0].isalpha()
                or not content_leading_stripped[0] == content_leading_stripped[0].casefold()
            )
        )

        current_hashes = hashes
        line_modified = False

        if len(current_hashes) == 1 and is_h1_candidate:
            if first_h1_seen:
                current_hashes = "##"
                line_modified = True
                modified = True
                print(f"  Demoted extra H1 on line {index + 1} in {file_path}")
            else:
                first_h1_seen = True

        cleaned_content, removed_emphasis = strip_outer_emphasis(content)
        if removed_emphasis:
            content = cleaned_content
            line_modified = True
            modified = True
            print(f"  Removed outer emphasis on line {index + 1} in {file_path}")

        if line_modified:
            lines[index] = f"{indent}{current_hashes}{space}{content}"

    if not modified:
        return False

    new_content = "\n".join(lines)
    if original_content.endswith("\n"):
        new_content += "\n"

    try:
        file_path.write_text(new_content, encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive guard
        print(f"Error writing {file_path}: {exc}")
        return False

    return True

def strip_outer_emphasis(content: str) -> Tuple[str, bool]:
    """Remove emphasis markers that wrap the entire heading content."""

    stripped = content.strip()
    if not stripped:
        return content, False

    original_stripped = stripped
    changed = False

    while True:
        for marker in EMPHASIS_MARKERS:
            if stripped.startswith(marker) and stripped.endswith(marker):
                inner = stripped[len(marker) : -len(marker)]
                if not inner.strip():
                    continue
                stripped = inner.strip()
                changed = True
                break
        else:
            break

    if not changed:
        return content, False

    leading_index = content.find(original_stripped)
    # Defensive fallback: In rare cases (e.g., non-standard whitespace or invisible characters),
    # original_stripped may not be found in content. In such cases, we return the stripped content,
    # even though this may lose leading/trailing whitespace.
    if leading_index == -1:
        return stripped, True

    leading = content[:leading_index]
    trailing = content[leading_index + len(original_stripped) :]
    return f"{leading}{stripped}{trailing}", True


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
