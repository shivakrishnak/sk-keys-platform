#!/usr/bin/env python3
"""
Fix DPT formatting violations:
1. Remove H1 header from body (# DPT-NNN - Title line)
2. Fix ASCII diagram lines > 59 chars (box drawing and text)
3. Fix code lines > 70 chars (inline comments + wrapping)
4. Fix bold-label spacing (add blank line before consecutive **LABEL:**)

Usage: python fix_dpt_formatting.py [--dry-run] [--file DPT-073*]
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path("c:/Shiva/northstar")
DPT_DIR = (
    REPO_ROOT
    / "dictionary/tier-5-distributed-architecture/DPT-design-patterns"
)
MAX_ASCII = 59
MAX_CODE = 70

# Unicode box-drawing chars used in borders
BOX_BORDER_CHARS = set("\u250c\u2514\u252c\u2534")  # ┌└┬┴
BOX_HORIZ_EDGE = set("\u251c\u2524")                # ├┤
BOX_ALL = set(
    "\u250c\u2510\u2514\u2518\u251c\u2524\u252c\u2534\u253c"
    "\u2500\u2502\u2550\u2551"
)  # ┌┐└┘├┤┬┴┼─│═║

H1_PATTERN = re.compile(r"^# DPT-\d+")


def get_frontmatter_end(lines):
    """Return index of closing --- of YAML frontmatter, or -1."""
    if not lines or lines[0].rstrip() != "---":
        return -1
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return i
    return -1


# ─── ASCII line trimming ────────────────────────────────────────

def trim_ascii_line(raw_line):
    """
    Trim one ASCII diagram line to <= MAX_ASCII chars.
    Returns the fixed line (with original trailing newline preserved).
    """
    # Preserve the trailing newline / no-newline
    if raw_line.endswith("\n"):
        line = raw_line.rstrip("\n")
        trail = "\n"
    else:
        line = raw_line
        trail = ""

    stripped = line.rstrip()
    if len(stripped) <= MAX_ASCII:
        return raw_line

    excess = len(stripped) - MAX_ASCII

    # ── Case 1: horizontal border   ┌────────────────┐
    #            or                  └────────────────┘
    if (
        len(stripped) >= 2
        and stripped[0] in "\u250c\u2514"  # ┌└
        and stripped[-1] in "\u2510\u2518"  # ┐┘
        and all(c == "\u2500" for c in stripped[1:-1])  # only ─
    ):
        # Remove 'excess' dashes from the interior
        inner = stripped[1:-1]
        inner = inner[:len(inner) - excess]
        return stripped[0] + inner + stripped[-1] + trail

    # ── Case 2: horizontal separator ├──────┼──────────┤
    if (
        stripped[0] == "\u251c"  # ├
        and stripped[-1] == "\u2524"  # ┤
        and all(c in "\u2500\u253c\u2502" for c in stripped[1:-1])
    ):
        # Remove 'excess' ─ chars from the rightmost dash run
        s = list(stripped)
        removed = 0
        for i in range(len(s) - 2, 0, -1):
            if s[i] == "\u2500":  # ─
                s.pop(i)
                removed += 1
                if removed >= excess:
                    break
        return "".join(s) + trail

    # ── Case 3: content line  │ LEFT │ RIGHT   │
    if stripped[0] == "\u2502" and stripped[-1] == "\u2502":  # │
        inner = list(stripped[1:-1])
        # Remove trailing spaces from right side
        removed = 0
        for i in range(len(inner) - 1, -1, -1):
            if inner[i] == " ":
                inner.pop(i)
                removed += 1
                if removed >= excess:
                    break
            else:
                break
        # If still too long, truncate
        result = stripped[0] + "".join(inner) + stripped[-1]
        if len(result) > MAX_ASCII:
            result = result[:MAX_ASCII - 1] + "\u2502"  # close with │
        return result + trail

    # ── Case 4: plain text line — wrap at last space within limit
    # Find last space at or before MAX_ASCII
    indent = len(stripped) - len(stripped.lstrip())
    indent_str = " " * indent
    cut = MAX_ASCII
    while cut > indent + 4 and stripped[cut - 1] != " ":
        cut -= 1
    if cut <= indent + 4:
        # No good split point: hard truncate
        return stripped[:MAX_ASCII] + trail

    first = stripped[:cut].rstrip()
    rest = stripped[cut:].lstrip()
    if not rest:
        return first + trail
    # Continuation line: same indent + 2 extra spaces
    cont_indent = indent_str + "  "
    cont = cont_indent + rest
    # Return first line only (caller may need to insert a new line)
    # We signal continuation by returning a tuple
    return (first + trail, cont + trail)


# ─── Code line trimming ─────────────────────────────────────────

def break_comment_line(raw_line):
    """
    Try to break a Java/Python comment line that exceeds MAX_CODE.
    Handles:
    - Full comment lines (// ... or # ...)
    - Inline comments (code; // comment → split to two lines)
    Returns list of fixed lines, or [raw_line] if not fixable here.
    """
    if raw_line.endswith("\n"):
        line = raw_line.rstrip("\n")
        trail = "\n"
    else:
        line = raw_line
        trail = ""

    stripped = line.rstrip()
    if len(stripped) <= MAX_CODE:
        return [raw_line]

    indent = len(stripped) - len(stripped.lstrip())
    indent_str = " " * indent
    content = stripped.lstrip()

    # Handle full // comment line
    if content.startswith("//"):
        comment_body = content[2:].lstrip()
        prefix = indent_str + "// "
        return wrap_text(prefix, comment_body, MAX_CODE, trail)

    # Handle full # comment line
    if content.startswith("#") and not content.startswith("#!"):
        comment_body = content[1:].lstrip()
        prefix = indent_str + "# "
        return wrap_text(prefix, comment_body, MAX_CODE, trail)

    # Handle inline comment: code; // comment
    # Try splitting at last ' //' before MAX_CODE
    for sep in (" //", " #"):
        # Find the LAST occurrence of the separator pattern
        idx = stripped.rfind(sep)
        if idx > indent and idx < len(stripped) - 2:
            code_part = stripped[:idx].rstrip()
            comment_part = stripped[idx:].lstrip()
            if len(code_part) <= MAX_CODE:
                # Put comment on next line with same indent
                comment_line = indent_str + comment_part
                if len(comment_line) <= MAX_CODE:
                    return [code_part + trail, comment_line + trail]
                # Comment itself too long — wrap it
                comment_body = comment_part.lstrip("/# ").lstrip()
                c_prefix = indent_str + sep.lstrip() + " "
                wrapped = wrap_text(c_prefix, comment_body, MAX_CODE, trail)
                return [code_part + trail] + wrapped

    # Handle long code lines with no comment — split at method call args
    # Find last space before MAX_CODE that could be a safe break point
    # Look for: after (, before ), at + operator
    split_chars = [", ", " + ", " +=", " = "]
    for sc in split_chars:
        idx = stripped.rfind(sc, indent, MAX_CODE - 1)
        if idx > indent:
            first = stripped[:idx + len(sc)].rstrip()
            rest = stripped[idx + len(sc):]
            if first and rest:
                # Continuation indent: 4 more spaces than current
                cont_indent = indent_str + "    "
                cont_line = cont_indent + rest
                if len(first) <= MAX_CODE and len(cont_line) <= MAX_CODE:
                    return [first + trail, cont_line + trail]

    # Not fixable safely - return as-is
    return [raw_line]


def wrap_text(prefix, body, max_len, trail):
    """Wrap body text with the given prefix, respecting max_len."""
    lines = []
    available = max_len - len(prefix)
    if available <= 0:
        return [prefix + body + trail]

    words = body.split(" ")
    current = prefix
    for word in words:
        test = current + word
        if len(test) <= max_len:
            current = test + " "
        else:
            if current.strip():
                lines.append(current.rstrip() + trail)
            current = prefix + word + " "
    if current.strip():
        lines.append(current.rstrip() + trail)
    return lines


# ─── File fixer ────────────────────────────────────────────────

def fix_file(filepath, dry_run=False):
    """Fix all formatting violations in a DPT file.
    Returns (changed: bool, n_h1: int, n_ascii: int, n_code: int).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    lines = raw.split("\n")
    fm_end = get_frontmatter_end(lines)
    if fm_end < 0:
        print(f"  SKIP (no frontmatter): {filepath.name}")
        return False, 0, 0, 0

    n_h1 = 0
    n_ascii = 0
    n_code = 0

    # ── Pass 1: Remove H1 in body ──────────────────────────────
    body_start = fm_end + 1
    new_lines = list(lines)
    for i in range(body_start, min(body_start + 5, len(new_lines))):
        s = new_lines[i].lstrip()
        if s.startswith("# ") and not s.startswith("## "):
            new_lines[i] = None
            # Remove trailing blank line too
            if (
                i + 1 < len(new_lines)
                and new_lines[i + 1].strip() == ""
            ):
                new_lines[i + 1] = None
            n_h1 += 1
            break
    new_lines = [l for l in new_lines if l is not None]

    # ── Pass 2: Fix ASCII and code line widths ─────────────────
    result = []
    in_code = False
    in_ascii = False

    for line in new_lines:
        raw_line = line + "\n"  # re-add newline for processing

        if line.rstrip().startswith("```"):
            if in_code:
                in_code = False
                in_ascii = False
            else:
                in_code = True
                lang = line.rstrip()[3:].strip().lower()
                in_ascii = lang in ("", "text")
            result.append(line)
            continue

        if in_code:
            stripped = line.rstrip()
            line_len = len(stripped)

            if in_ascii and line_len > MAX_ASCII:
                fixed = trim_ascii_line(raw_line)
                if isinstance(fixed, tuple):
                    # Wrapped into multiple lines
                    for part in fixed:
                        result.append(part.rstrip("\n"))
                else:
                    result.append(fixed.rstrip("\n"))
                n_ascii += 1
                continue

            if not in_ascii and line_len > MAX_CODE:
                fixed_lines = break_comment_line(raw_line)
                if len(fixed_lines) > 1 or fixed_lines[0] != raw_line:
                    for fl in fixed_lines:
                        result.append(fl.rstrip("\n"))
                    n_code += 1
                    continue

        result.append(line)

    # ── Pass 3: Fix bold-label spacing ───────────────────────
    BOLD_LABEL_RE = re.compile(r"^\*\*[A-Z][^*]*:\*\*")
    n_bold = 0
    result2 = []
    in_fence2 = False
    prev_was_bold_content = False

    for line in result:
        stripped = line.rstrip()
        if stripped.startswith("```"):
            in_fence2 = not in_fence2
            prev_was_bold_content = False
            result2.append(line)
            continue
        if in_fence2:
            result2.append(line)
            continue

        if BOLD_LABEL_RE.match(stripped.lstrip()):
            if prev_was_bold_content:
                # Insert blank line before this bold-label
                result2.append("")
                n_bold += 1
            prev_was_bold_content = True
        elif stripped == "":
            prev_was_bold_content = False

        result2.append(line)

    result = result2

    # Reconstruct content
    new_content = "\n".join(result)

    changed = new_content != raw
    if changed and not dry_run:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            f.write(new_content)

    return changed, n_h1, n_ascii, n_code + n_bold


# ─── Main ──────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    file_filter = None
    for a in sys.argv[1:]:
        if not a.startswith("--"):
            file_filter = a

    files = sorted(DPT_DIR.glob("DPT-*.md"))
    if file_filter:
        files = [f for f in files if file_filter.lower() in f.name.lower()]

    if dry_run:
        print("DRY RUN - no files will be modified\n")

    total_changed = 0
    total_h1 = 0
    total_ascii = 0
    total_code = 0

    for fp in files:
        changed, n_h1, n_ascii, n_code = fix_file(fp, dry_run=dry_run)
        if changed or n_h1 or n_ascii or n_code:
            status = "DRY" if dry_run else "FIXED"
            print(
                f"  [{status}] {fp.name}"
                f"  H1:{n_h1} ASCII:{n_ascii} code:{n_code}"
            )
            total_changed += 1
        total_h1 += n_h1
        total_ascii += n_ascii
        total_code += n_code

    print(
        f"\nTotal files changed: {total_changed}/{len(files)}\n"
        f"H1 removed: {total_h1}\n"
        f"ASCII lines fixed: {total_ascii}\n"
        f"Code lines broken: {total_code}"
    )


if __name__ == "__main__":
    main()
