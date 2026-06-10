#!/usr/bin/env python3
"""
Fix H1-in-body false positives caused by missing code fence openers.

When the validator flags "H1 in body" for a line starting with "# ",
it might be a Python/bash comment inside a code block whose opening
fence (```) was accidentally omitted. This script detects such cases
and inserts the missing opening fence.

Strategy:
  1. Parse the file body tracking fence state (same as validator)
  2. For each "# text" line flagged as H1, check if this line is
     part of a run of indented/code-looking lines preceded by a blank
     line and a descriptive text line (indicating a missing ```)
  3. If yes, insert the missing opening ``` before the block
  4. Find the closing ``` that should match and verify it exists

Usage:
  python fix_h1_false_positives.py [--dry-run]
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


def get_frontmatter_end(lines):
    if not lines or lines[0].rstrip() != "---":
        return -1
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return i
    return -1


def is_dict_file(lines, fm_end):
    fm_raw = "\n".join(lines[:fm_end + 1])
    return "folder:" in fm_raw or "category:" in fm_raw


def find_h1_violations(lines, body_start):
    """Find lines flagged as H1 (# text) that are outside a fence."""
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
            violations.append(i)  # 0-indexed
    return violations


def find_fence_count_before(lines, body_start, target_idx):
    """Count fence toggles from body_start to target_idx."""
    count = 0
    for i in range(body_start, target_idx):
        if lines[i].rstrip().startswith("```"):
            count += 1
    return count


def is_code_comment_line(line):
    """True if line looks like a code comment (# or //)."""
    stripped = line.lstrip()
    return (stripped.startswith("# ")
            or stripped.startswith("// ")
            or stripped.startswith("## "))


def fix_file(filepath, dry_run=False):
    """
    Fix missing opening code fences in one file.
    Returns count of fixes made.
    """
    try:
        text = filepath.read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"  ERROR reading {filepath.name}: {e}")
        return 0

    lines = text.split("\n")
    fm_end = get_frontmatter_end(lines)
    if fm_end < 0:
        return 0
    if not is_dict_file(lines, fm_end):
        return 0

    body_start = fm_end + 1
    violations = find_h1_violations(lines, body_start)
    if not violations:
        return 0

    fixes = 0
    offset = 0  # Track line number shift due to insertions

    for viol_idx in violations:
        actual_idx = viol_idx + offset

        # Count fences from body to just before this line
        fence_count = find_fence_count_before(
            lines, body_start, actual_idx
        )

        if fence_count % 2 == 1:
            # fence_count is ODD = we are INSIDE a fence
            # The validator should have skipped this.
            # This means there's a miscount - likely a prior
            # missing fence opener caused the off-by-one.
            # We need to find and insert a missing ```
            # at the right place (before this code block starts).

            # Search backward for where this code block starts
            # A code block starts after a blank line
            insert_pos = actual_idx
            for j in range(actual_idx - 1, body_start - 1, -1):
                stripped = lines[j].rstrip()
                if stripped == "":
                    # Blank line - insert ``` AFTER this blank
                    insert_pos = j + 1
                    break
                if stripped.startswith("```"):
                    # Already a fence - don't insert before it
                    insert_pos = -1
                    break
                if stripped.startswith("#"):
                    # Another heading - stop
                    insert_pos = j + 1
                    break

            if insert_pos < 0:
                continue

            # Verify there's a closing ``` after this block
            closing_idx = -1
            for j in range(actual_idx + 1, len(lines)):
                if lines[j].rstrip().startswith("```"):
                    closing_idx = j
                    break

            if closing_idx < 0:
                continue  # No closing fence found

            # Insert opening ``` at insert_pos
            lines.insert(insert_pos, "```")
            offset += 1
            fixes += 1

        elif fence_count % 2 == 0:
            # fence_count is EVEN = we appear to be OUTSIDE a fence
            # BUT we're inside a code block - this means there's a
            # missing opening fence that caused off-by-one for all
            # subsequent code blocks.

            # Look backward for the code block this comment belongs to
            # It should start after a blank line or a label line
            # and the ACTUAL content is code (# comments, code lines)
            insert_pos = -1
            for j in range(actual_idx - 1, body_start - 1, -1):
                stripped = lines[j].rstrip()
                if stripped == "":
                    # Blank line - code block starts after this blank
                    insert_pos = j + 1
                    break
                if stripped.startswith("```"):
                    # Already a fence marker - can't insert here
                    break
                if (stripped.startswith("**")
                        or stripped.startswith("###")
                        or stripped.startswith("---")):
                    # A heading/separator line - insert AFTER it
                    insert_pos = j + 1
                    break

            if insert_pos < 0 or insert_pos >= actual_idx:
                continue

            # Verify there's a closing ``` after this block
            closing_idx = -1
            for j in range(actual_idx + 1, len(lines)):
                if lines[j].rstrip().startswith("```"):
                    closing_idx = j
                    break

            if closing_idx < 0:
                continue

            # Insert opening ``` at insert_pos
            lines.insert(insert_pos, "```")
            offset += 1
            fixes += 1

    if fixes == 0:
        return 0

    new_text = "\n".join(lines)
    if not dry_run:
        filepath.write_text(new_text, encoding="utf-8")
    return fixes


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("DRY RUN - no files modified\n")

    total_fixes = 0
    n_files = 0
    n_changed = 0

    for fp in sorted(DICT_DIR.rglob("*.md")):
        if fp.name == "index.md":
            continue
        n_files += 1
        count = fix_file(fp, dry_run=dry_run)
        if count:
            n_changed += 1
            total_fixes += count
            rel = fp.relative_to(REPO_ROOT)
            print(f"  {'DRY' if dry_run else 'FIX'} {rel.name}"
                  f"  [h1_fence:{count}]")

    print(f"\nFiles: {n_changed}/{n_files} changed,"
          f" {total_fixes} fences inserted")


if __name__ == "__main__":
    main()
