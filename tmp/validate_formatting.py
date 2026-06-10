#!/usr/bin/env python3
"""
Pre-commit formatting validator for dictionary/ and interview/ files.
Checks rules from copilot-instructions.md and generator specs.

Usage:
  python validate_formatting.py <file1.md> [file2.md ...]
  python validate_formatting.py --all          # scan all entries
  python validate_formatting.py --staged       # scan git staged files

Exit code: 0 = all pass, 1 = errors found
"""
import sys
import re
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_CODE_LINE = 70
MAX_ASCII_WIDTH = 59
EM_DASH = "\u2014"


def parse_frontmatter(lines):
    """Return (end_index, is_dictionary) of YAML frontmatter."""
    if not lines or lines[0].rstrip() != "---":
        return -1, False
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            raw = "\n".join(lines[:i + 1])
            is_dict = "folder:" in raw or "category:" in raw
            return i, is_dict
    return -1, False


def check_file(filepath):
    """Run all checks on a single file. Returns list of errors."""
    errors = []
    rel = os.path.relpath(filepath, REPO_ROOT)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        return [f"{rel}: cannot read file: {e}"]

    # BOM check
    if raw.startswith("\ufeff"):
        errors.append(f"{rel}:1: BOM detected - file must be UTF-8 without BOM")

    lines = raw.splitlines()
    if not lines:
        return [f"{rel}: empty file"]

    # YAML starts at byte 0
    if lines[0].rstrip() != "---":
        errors.append(f"{rel}:1: file must start with --- (YAML frontmatter)")

    fm_end, is_dict = parse_frontmatter(lines)
    if fm_end < 0:
        errors.append(f"{rel}: no closing --- for YAML frontmatter")
        return errors

    body_start = fm_end + 1
    body = lines[body_start:]

    # Em dash check (entire file)
    for i, line in enumerate(lines, 1):
        if EM_DASH in line:
            errors.append(
                f"{rel}:{i}: em dash found - use hyphen instead"
            )

    # No H1 in body (dictionary files only) - skip code blocks
    if is_dict:
        in_fence = False
        for i, line in enumerate(body, body_start + 1):
            if line.rstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            stripped = line.lstrip()
            if stripped.startswith("# ") and not stripped.startswith("## "):
                errors.append(
                    f"{rel}:{i}: H1 in body - Just the Docs "
                    "renders H1 from YAML title"
                )

    # Track code fence state for width checks
    in_code = False
    in_ascii_block = False
    for i, line in enumerate(body, body_start + 1):
        stripped = line.rstrip()
        if stripped.startswith("```"):
            if in_code:
                in_code = False
                in_ascii_block = False
            else:
                in_code = True
                lang = stripped[3:].strip().lower()
                in_ascii_block = lang == "" or lang == "text"
            continue

        if in_code:
            line_len = len(stripped)
            if in_ascii_block and line_len > MAX_ASCII_WIDTH:
                errors.append(
                    f"{rel}:{i}: ASCII diagram line {line_len} "
                    f"chars (max {MAX_ASCII_WIDTH})"
                )
            elif not in_ascii_block and line_len > MAX_CODE_LINE:
                errors.append(
                    f"{rel}:{i}: code line {line_len} chars "
                    f"(max {MAX_CODE_LINE})"
                )

    # --- before every ### heading (skip code blocks)
    in_fence = False
    for i, line in enumerate(body, body_start + 1):
        if line.rstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("### "):
            # Find the previous non-blank line
            rel_i = i - body_start - 1
            prev_non_blank = None
            for j in range(rel_i - 1, -1, -1):
                if body[j].strip():
                    prev_non_blank = body[j].strip()
                    break
            if prev_non_blank != "---":
                errors.append(
                    f"{rel}:{i}: ### heading not preceded by ---"
                )

    # Bold-label spacing: consecutive **LABEL:** blocks
    # need a blank line between them (skip code blocks)
    bold_label_re = re.compile(r"^\*\*[A-Z][^*]*:\*\*")
    prev_was_bold_content = False
    in_fence = False
    for i, line in enumerate(body, body_start + 1):
        if line.rstrip().startswith("```"):
            in_fence = not in_fence
            prev_was_bold_content = False
            continue
        if in_fence:
            continue
        if bold_label_re.match(line.strip()):
            if prev_was_bold_content:
                errors.append(
                    f"{rel}:{i}: bold-label line follows "
                    "content without blank line separator"
                )
            prev_was_bold_content = True
        elif line.strip() == "":
            prev_was_bold_content = False
        # non-blank non-bold-label: still in content
        # of previous bold label

    # QRC border check: separator rows should end with ┤ or ┘
    for i, line in enumerate(body, body_start + 1):
        stripped = line.rstrip()
        if "├" in stripped and "┼" in stripped:
            if not stripped.endswith("┤"):
                errors.append(
                    f"{rel}:{i}: QRC separator row should "
                    "end with ┤"
                )

    return errors


def get_staged_files():
    """Get list of staged .md files in dictionary/ and interview/."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only",
         "--diff-filter=ACM"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    files = []
    for line in result.stdout.strip().splitlines():
        if line.endswith(".md") and (
            line.startswith("dictionary/")
            or line.startswith("interview/")
        ):
            files.append(REPO_ROOT / line)
    return files


def get_all_files():
    """Get all .md files in dictionary/ and interview/."""
    files = []
    for folder in ["dictionary", "interview"]:
        root = REPO_ROOT / folder
        for md in root.rglob("*.md"):
            if md.name == "index.md":
                continue
            if "_config" in str(md):
                continue
            files.append(md)
    return files


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_formatting.py <file ...>"
              " | --all | --staged")
        sys.exit(2)

    if sys.argv[1] == "--staged":
        files = get_staged_files()
        if not files:
            print("No staged dictionary/interview .md files.")
            sys.exit(0)
    elif sys.argv[1] == "--all":
        files = get_all_files()
    else:
        files = [Path(f).resolve() for f in sys.argv[1:]]

    all_errors = []
    for f in files:
        all_errors.extend(check_file(f))

    if all_errors:
        print(f"\n{'='*60}")
        print(f"FORMATTING ERRORS: {len(all_errors)}")
        print(f"{'='*60}\n")
        for err in all_errors:
            print(f"  {err}")
        print(f"\n{'='*60}")
        print(f"Files checked: {len(files)}")
        print(f"Errors found:  {len(all_errors)}")
        print(f"{'='*60}\n")
        sys.exit(1)
    else:
        print(f"All {len(files)} files passed formatting checks.")
        sys.exit(0)


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    main()
