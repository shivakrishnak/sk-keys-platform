#!/usr/bin/env python3
"""
Fix H1-in-body false positives caused by missing code fence openers.

Root cause: some files have a closing ``` (triple backtick) with no
matching opener, which shifts the fence-tracking state by 1. This
makes subsequent code blocks appear to be outside a fence, causing
# comment lines inside those blocks to be flagged as H1 headings.

Fix strategy:
1. Walk the body tracking fence state the same way the validator does
2. Find ``` lines that appear to be CLOSING a fence but are tracked
   as OPENING (because fence count before them is even, but context
   shows they end a code block)
3. Insert a matching opening ``` before the code block that this
   orphaned closer closes

Usage:
  python fix_h1_fence.py [--dry-run]
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

# Files known to have H1 violations
TARGET_FILES = [
    ("tier-5-distributed-architecture/SYD-system-design",
     "SYD-061 - Bulkhead Pattern.md"),
    ("tier-2-networking-security/API-http-apis",
     "API-032 - Long Polling.md"),
    ("tier-6-infrastructure-devops/OBS-observability-sre",
     "OBS-016 - Grafana -- Dashboards.md"),
    ("tier-6-infrastructure-devops/OBS-observability-sre",
     "OBS-031 - Golden Signals.md"),
    ("tier-6-infrastructure-devops/OBS-observability-sre",
     "OBS-030 - USE Method (Utilization, Saturation, Errors).md"),
    ("tier-6-infrastructure-devops/OBS-observability-sre",
     "OBS-032 - Cardinality in Metrics Systems.md"),
    ("tier-6-infrastructure-devops/OBS-observability-sre",
     "OBS-033 - Continuous Profiling (Pyroscope, Parca).md"),
    ("tier-6-infrastructure-devops/OBS-observability-sre",
     "OBS-034 - eBPF for Observability.md"),
    ("tier-6-infrastructure-devops/OBS-observability-sre",
     "OBS-035 - Chaos Engineering for Observability.md"),
]


def get_frontmatter_end(lines):
    if not lines or lines[0].rstrip() != "---":
        return -1
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return i
    return -1


def find_h1_violations(lines, body_start):
    """Find 0-indexed line numbers flagged as H1 by the validator."""
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


def find_mismatched_closers(lines, body_start):
    """
    Find ``` lines that are 'mismatched' - i.e., they appear to
    OPEN a fence (even fence count before them) but contextually
    they should CLOSE a block.

    Heuristic: a ``` preceded by code-looking lines (indented or
    with # comments) and succeeded by non-code markdown is likely
    a CLOSER that needs a matching OPENER inserted before the
    code block it closes.
    """
    fence_positions = []
    for i in range(body_start, len(lines)):
        if lines[i].rstrip().startswith("```"):
            fence_positions.append(i)

    mismatched = []
    for pos_idx, fence_line in enumerate(fence_positions):
        fence_count_before = pos_idx  # 0-indexed
        if fence_count_before % 2 == 0:
            # This ``` is treated as OPEN by the validator
            # Check if context suggests it should be a CLOSER:
            # - The line BEFORE it looks like code content
            # - The line AFTER it looks like markdown text
            before_content = (
                lines[fence_line - 1].rstrip()
                if fence_line > 0 else ""
            )
            after_content = (
                lines[fence_line + 1].rstrip()
                if fence_line + 1 < len(lines) else ""
            )

            # Looks like a closer if preceded by code-like content
            looks_like_closer = (
                before_content != ""
                and not before_content.startswith("```")
                and not before_content.startswith("---")
                and not before_content.startswith("#")
                and not before_content.startswith("**")
            )

            if looks_like_closer:
                mismatched.append(fence_line)

    return mismatched


def find_code_block_start(lines, closer_idx, body_start):
    """
    Walk backward from closer_idx to find where the code block starts.
    Returns the 0-indexed line where we should insert the opening ```.
    """
    # Walk backward until we find a clear separator
    for j in range(closer_idx - 1, body_start - 1, -1):
        stripped = lines[j].rstrip()
        if stripped == "":
            # Blank line - code starts AFTER this blank line
            return j + 1
        if stripped.startswith("```"):
            # Another fence - can't go further back
            return j + 1
        if stripped.startswith("---"):
            return j + 1
        if stripped.startswith("### ") or stripped.startswith("## "):
            return j + 1
        # Bold label or similar
        if stripped.startswith("**") and stripped.endswith("**"):
            return j + 1
        if stripped.startswith("**") and "**" in stripped[2:]:
            # **LABEL:** style
            return j + 1

    return body_start


def fix_file(filepath, dry_run=False):
    """Fix missing opening fences. Returns count of fixes."""
    try:
        text = filepath.read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"  ERROR reading {filepath.name}: {e}")
        return 0

    lines = text.split("\n")
    fm_end = get_frontmatter_end(lines)
    if fm_end < 0:
        return 0
    body_start = fm_end + 1

    # First check if there are any H1 violations to fix
    violations = find_h1_violations(lines, body_start)
    if not violations:
        return 0

    # Find mismatched closers that cause the fence tracking issue
    mismatched = find_mismatched_closers(lines, body_start)

    if not mismatched:
        return 0

    fixes = 0
    offset = 0  # Track shift from insertions

    for closer_idx in mismatched:
        actual_closer = closer_idx + offset

        # Find where to insert the opening fence
        insert_pos = find_code_block_start(
            lines, actual_closer, body_start
        )

        if insert_pos <= body_start or insert_pos >= actual_closer:
            continue

        # Don't insert if there's already a fence at insert_pos - 1
        if (insert_pos > 0
                and lines[insert_pos - 1].rstrip().startswith("```")):
            continue

        if dry_run:
            print(f"    Would insert ``` at line {insert_pos + 1}"
                  f" (before: {lines[insert_pos][:50]!r})"
                  f" closing at line {actual_closer + 1}")

        lines.insert(insert_pos, "```")
        offset += 1
        fixes += 1

        # Verify violations are now fixed
        new_violations = find_h1_violations(lines, body_start)
        if not new_violations:
            break  # All fixed!

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
    n_changed = 0

    for rel_dir, fname in TARGET_FILES:
        fp = DICT_DIR / rel_dir / fname
        if not fp.exists():
            print(f"  NOT FOUND: {fname}")
            continue
        count = fix_file(fp, dry_run=dry_run)
        if count:
            n_changed += 1
            total_fixes += count
            print(f"  {'DRY' if dry_run else 'FIX'} {fname}"
                  f"  [fences:{count}]")
        else:
            print(f"  SKIP {fname}  (no changes needed)")

    print(f"\n{n_changed}/{len(TARGET_FILES)} files changed,"
          f" {total_fixes} fences inserted")


if __name__ == "__main__":
    main()
