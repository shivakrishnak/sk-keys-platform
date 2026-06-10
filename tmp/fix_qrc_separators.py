#!/usr/bin/env python3
"""
Fix QRC separator rows that are missing the closing box char.

Validator rule: lines containing both ├ (U+251C) and ┼ (U+253C)
must end with ┤ (U+2524).

Two cases to handle:
  1. Line ends with ─ (dash) - was truncated by fix_all_formatting.py
     → append ┤, trim one ─ if len >= 59
  2. Line ends with  │ (spaces + vertical bar) - original malformed
     → strip trailing spaces + U+2502, append ┤, trim if needed

Usage:
  python fix_qrc_separators.py [--dry-run]
"""

import sys
import io
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )

REPO_ROOT = Path("c:/Shiva/northstar")
DICT_DIR = REPO_ROOT / "dictionary"
MAX_ASCII = 59
BOX_H = "\u2500"   # ─
BOX_HT = "\u2524"  # ┤
BOX_TL = "\u251c"  # ├
BOX_X = "\u253c"   # ┼
BOX_V = "\u2502"   # │


def fix_separator(line: str) -> str:
    """Fix a separator row that has ├ and ┼ but doesn't end with ┤."""
    s = line.rstrip()

    # Case 1: ends with ─  (truncated)
    if s.endswith(BOX_H):
        if len(s) >= MAX_ASCII:
            # Need to trim one ─ before appending ┤
            # Find last ─ and remove it
            idx = len(s) - 1
            while idx > 0 and s[idx] == BOX_H:
                idx -= 1
            # Remove rightmost ─
            s = s[:len(s) - 1]
        return s + BOX_HT

    # Case 2: ends with spaces + │ (vertical bar, not ┤)
    # Strip trailing whitespace + │
    stripped = s.rstrip()
    if stripped.endswith(BOX_V):
        stripped = stripped[:-1].rstrip()
        # stripped now ends with ─ or ┼
        if len(stripped) + 1 >= MAX_ASCII:
            # Trim one ─
            if stripped.endswith(BOX_H):
                stripped = stripped[:-1]
        return stripped + BOX_HT

    # Already OK or unknown pattern - return as-is
    return s


def fix_file(filepath: Path, dry_run: bool = False) -> int:
    """Fix QRC separators in one file. Returns count of fixes."""
    try:
        text = filepath.read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"  ERROR reading {filepath.name}: {e}")
        return 0

    lines = text.split("\n")
    fixed = 0
    in_fence = False
    new_lines = []

    for line in lines:
        stripped = line.rstrip()

        # Track code fence state (for context, but apply fix everywhere)
        if stripped.startswith("```"):
            in_fence = not in_fence
            new_lines.append(line)
            continue

        # Apply fix both inside and outside code fences
        # (validator checks all body lines)
        if BOX_TL in stripped and BOX_X in stripped:
            if not stripped.endswith(BOX_HT):
                fixed_line = fix_separator(line)
                if fixed_line != stripped:
                    new_lines.append(fixed_line)
                    fixed += 1
                    continue
        new_lines.append(line)

    if fixed == 0:
        return 0

    new_text = "\n".join(new_lines)
    if not dry_run:
        filepath.write_text(new_text, encoding="utf-8")
    return fixed


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("DRY RUN - no files modified\n")

    total_fixed = 0
    n_files = 0
    n_changed = 0

    for fp in sorted(DICT_DIR.rglob("*.md")):
        if fp.name == "index.md":
            continue
        n_files += 1
        count = fix_file(fp, dry_run=dry_run)
        if count:
            n_changed += 1
            total_fixed += count
            rel = fp.relative_to(REPO_ROOT)
            print(f"  {'DRY' if dry_run else 'FIX'} {rel.name}"
                  f"  [qrc:{count}]")

    print(f"\nFiles: {n_changed}/{n_files} changed,"
          f" {total_fixed} separator rows fixed")


if __name__ == "__main__":
    main()
