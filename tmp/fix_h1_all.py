#!/usr/bin/env python3
"""
Fix two types of H1-in-body false positives in dictionary files:

Type A - Indented fences: ``` lines with leading spaces are not
  recognized by the validator's fence tracker (uses startswith).
  Fix: de-indent ``` lines to column 0.

Type B - Missing openers: a ``` close exists with no matching open,
  causing fence-count phase shift for all subsequent code blocks.
  Fix: insert a matching ``` opener before the orphaned block.

Usage:
  python fix_h1_all.py [--dry-run]
  python fix_h1_all.py --file SYD-061
"""

import re
import sys
import io
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )

REPO_ROOT = Path("c:/Shiva/northstar")
DICT_DIR = REPO_ROOT / "dictionary"

FENCE_RE = re.compile(r"^```")          # column-0 fence (validator sees)
INDENTED_FENCE_RE = re.compile(r"^ +```")  # indented fence


def get_frontmatter_end(lines):
    if not lines or lines[0].rstrip() != "---":
        return -1
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return i
    return -1


def has_h1_violations(lines, body_start):
    """Check if file has H1 violations using validator logic."""
    in_fence = False
    for i in range(body_start, len(lines)):
        line = lines[i]
        if line.rstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.lstrip()
        if (stripped.startswith("# ")
                and not stripped.startswith("## ")):
            return True
    return False


def find_h1_violation_lines(lines, body_start):
    """Return list of 0-indexed lines with H1 violations."""
    violations = []
    in_fence = False
    for i in range(body_start, len(lines)):
        line = lines[i]
        if line.rstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.lstrip()
        if (stripped.startswith("# ")
                and not stripped.startswith("## ")):
            violations.append(i)
    return violations


def fix_type_a_indented_fences(lines, body_start):
    """
    De-indent ``` lines that have leading spaces.
    Returns (new_lines, count_fixed).
    """
    fixed = 0
    new_lines = []
    for i, line in enumerate(lines):
        if i >= body_start and INDENTED_FENCE_RE.match(line):
            # De-indent: remove leading spaces before ```
            stripped = line.lstrip()
            if stripped.rstrip() == stripped.rstrip("` \t"):
                # Line is ONLY backtick chars (close fence)
                new_lines.append(stripped)
                fixed += 1
            elif stripped.startswith("```"):
                # Line is ```lang or ``` - de-indent
                new_lines.append(stripped)
                fixed += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    return new_lines, fixed


def fix_type_b_missing_opener(lines, body_start):
    """
    Find ``` lines treated as OPEN by validator but should be CLOSE,
    and insert a matching ``` opener before the code block.
    Returns (new_lines, count_fixed).
    """
    fixed = 0
    offset = 0

    # Find all column-0 fence positions AFTER body_start
    fence_positions = []
    for i in range(body_start, len(lines)):
        if lines[i].rstrip().startswith("```"):
            fence_positions.append(i)

    for pos_idx, fence_pos in enumerate(fence_positions):
        if pos_idx % 2 == 0:
            # This is treated as OPEN by validator (even index)
            # Check if it looks like a closer contextually:
            # - Line before it is code-like (indented or # comment)
            # - Line after it is markdown (heading/prose)
            actual_pos = fence_pos + offset

            before = lines[actual_pos - 1].rstrip() if actual_pos > 0 else ""
            after = lines[actual_pos + 1].rstrip() if actual_pos + 1 < len(lines) else ""

            # Skip if preceded by ``` (can't be a closer after opener)
            if before.startswith("```"):
                continue

            # Looks like a closer if:
            # 1. Preceded by code content (indented text, # comment, etc.)
            # 2. Followed by empty line or markdown text
            is_preceded_by_code = (
                before != ""
                and not before.startswith("#")
                and not before.startswith("---")
                and not before.startswith("**")
                and not before.startswith("> ")
            )

            is_followed_by_markdown = (
                after == ""
                or after.startswith("---")
                or after.startswith("#")
                or after.startswith("**")
                or after.startswith("> ")
                or (after[0].isdigit() if after else False)
            )

            if not (is_preceded_by_code and is_followed_by_markdown):
                continue

            # Find where this code block started
            insert_pos = actual_pos
            for j in range(actual_pos - 1, body_start - 1, -1):
                s = lines[j].rstrip()
                if s == "":
                    insert_pos = j + 1
                    break
                if s.startswith("```"):
                    insert_pos = -1
                    break
                if (s.startswith("---")
                        or s.startswith("### ")
                        or s.startswith("## ")):
                    insert_pos = j + 1
                    break
                if s.startswith("**") and "**" in s[2:]:
                    insert_pos = j + 1
                    break

            if insert_pos < 0 or insert_pos >= actual_pos:
                continue
            if (insert_pos > 0
                    and lines[insert_pos - 1].rstrip().startswith("```")):
                continue

            lines.insert(insert_pos, "```")
            offset += 1
            fixed += 1

            # Update fence_positions for subsequent entries
            fence_positions = [
                fp + 1 if fp >= insert_pos else fp
                for fp in fence_positions
            ]

    return lines, fixed


def fix_file(filepath, dry_run=False):
    """Fix H1 violations in one file. Returns (count_a, count_b)."""
    try:
        text = filepath.read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"  ERROR reading {filepath.name}: {e}")
        return 0, 0

    lines = text.split("\n")
    fm_end = get_frontmatter_end(lines)
    if fm_end < 0:
        return 0, 0

    fm_raw = "\n".join(lines[:fm_end + 1])
    if "folder:" not in fm_raw and "category:" not in fm_raw:
        return 0, 0  # Not a dictionary file

    body_start = fm_end + 1

    if not has_h1_violations(lines, body_start):
        return 0, 0

    # Fix Type A: de-indent fences
    lines, count_a = fix_type_a_indented_fences(lines, body_start)

    # Check if Type A fixed everything
    if not has_h1_violations(lines, body_start):
        if count_a > 0 and not dry_run:
            filepath.write_text("\n".join(lines), encoding="utf-8")
        return count_a, 0

    # Fix Type B: missing openers
    lines, count_b = fix_type_b_missing_opener(lines, body_start)

    if count_a == 0 and count_b == 0:
        return 0, 0

    if not dry_run:
        filepath.write_text("\n".join(lines), encoding="utf-8")
    return count_a, count_b


def main():
    dry_run = "--dry-run" in sys.argv
    file_filter = None
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--file" and i + 1 < len(args):
            file_filter = args[i + 1].lower()

    if dry_run:
        print("DRY RUN - no files modified\n")

    total_a = 0
    total_b = 0
    n_changed = 0
    n_files = 0

    for fp in sorted(DICT_DIR.rglob("*.md")):
        if fp.name == "index.md":
            continue
        if file_filter and file_filter not in fp.name.lower():
            continue
        n_files += 1
        ca, cb = fix_file(fp, dry_run=dry_run)
        if ca or cb:
            n_changed += 1
            total_a += ca
            total_b += cb
            rel = fp.relative_to(REPO_ROOT)
            print(f"  {'DRY' if dry_run else 'FIX'} {rel.name}"
                  f"  [deindent:{ca} opener:{cb}]")

    print(f"\nFiles: {n_changed}/{n_files} changed")
    print(f"  Type A (de-indent): {total_a} fence lines fixed")
    print(f"  Type B (opener): {total_b} fences inserted")


if __name__ == "__main__":
    main()
