#!/usr/bin/env python3
"""
Fix ALL dictionary formatting violations across all tiers.

Fixes:
1. BOM at start of file
2. H1 in body (dictionary files only - Just the Docs renders from YAML title)
3. ASCII diagram lines > 59 chars
4. Code lines > 70 chars (comment-style breaks)
5. Bold-label spacing (blank line before consecutive **LABEL:**)
6. Em dash (replace U+2014 with hyphen)
7. --- before ### headings

Usage:
  python fix_all_formatting.py [--dry-run]
  python fix_all_formatting.py --tier tier-3-java
  python fix_all_formatting.py --file path/to/file.md
"""

import re
import sys
import io
from pathlib import Path

# Fix Windows console Unicode output
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )

REPO_ROOT = Path("c:/Shiva/northstar")
DICT_DIR = REPO_ROOT / "dictionary"
MAX_ASCII = 59
MAX_CODE = 70
EM_DASH = "\u2014"
BOM = "\ufeff"

BOLD_LABEL_RE = re.compile(r"^\*\*[A-Z][^*]*:\*\*")
BOX_CHARS = set(
    "\u250c\u2510\u2514\u2518\u251c\u2524\u252c\u2534\u253c"
    "\u2500\u2502"
)  # ┌┐└┘├┤┬┴┼─│


# ─── Frontmatter ───────────────────────────────────────────────

def get_frontmatter_end(lines):
    if not lines or lines[0].rstrip() != "---":
        return -1
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return i
    return -1


def is_dict_file(raw_fm):
    return "folder:" in raw_fm or "category:" in raw_fm


# ─── ASCII trimming ─────────────────────────────────────────────

def trim_ascii_line(raw_line):
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

    # Box top/bottom: ┌──────┐  └──────┘
    if (
        len(stripped) >= 2
        and stripped[0] in "\u250c\u2514"
        and stripped[-1] in "\u2510\u2518"
        and all(c == "\u2500" for c in stripped[1:-1])
    ):
        inner = stripped[1:-1][:-excess]
        return stripped[0] + inner + stripped[-1] + trail

    # Horizontal separator: ├──────┤ (may contain ┼)
    if stripped[0] == "\u251c" and stripped[-1] == "\u2524":
        s = list(stripped)
        removed = 0
        for i in range(len(s) - 2, 0, -1):
            if s[i] == "\u2500":
                s.pop(i)
                removed += 1
                if removed >= excess:
                    break
        return "".join(s) + trail

    # Content: │ ... │
    if stripped[0] == "\u2502" and stripped[-1] == "\u2502":
        inner = list(stripped[1:-1])
        removed = 0
        for i in range(len(inner) - 1, -1, -1):
            if inner[i] == " ":
                inner.pop(i)
                removed += 1
                if removed >= excess:
                    break
            else:
                break
        result = stripped[0] + "".join(inner) + stripped[-1]
        if len(result) > MAX_ASCII:
            result = result[:MAX_ASCII - 1] + "\u2502"
        return result + trail

    # Plain text: wrap at last space within limit
    indent = len(stripped) - len(stripped.lstrip())
    cut = MAX_ASCII
    while cut > indent + 4 and stripped[cut - 1] != " ":
        cut -= 1
    if cut <= indent + 4:
        return stripped[:MAX_ASCII] + trail
    first = stripped[:cut].rstrip()
    rest = stripped[cut:].lstrip()
    if not rest:
        return first + trail
    cont_indent = " " * (indent + 2)
    return (first + trail, cont_indent + rest + trail)


# ─── Code line breaking ─────────────────────────────────────────

def wrap_text(prefix, body, max_len, trail):
    lines = []
    words = body.split(" ")
    current = prefix
    prefix_bare = prefix.rstrip()  # e.g. "//" or "#"
    for word in words:
        if len(current + word) <= max_len:
            current = current + word + " "
        else:
            # Only append if current has content beyond the prefix
            if current.rstrip() != prefix_bare:
                lines.append(current.rstrip() + trail)
            current = prefix + word + " "
    if current.rstrip() != prefix_bare:
        lines.append(current.rstrip() + trail)
    return lines if lines else [prefix + body + trail]


def break_code_line(raw_line):
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

    # Full // comment line
    if content.startswith("//"):
        return wrap_text(indent_str + "// ", content[2:].lstrip(),
                         MAX_CODE, trail)

    # Full # comment line
    if content.startswith("#") and not content.startswith("#!"):
        return wrap_text(indent_str + "# ", content[1:].lstrip(),
                         MAX_CODE, trail)

    # Inline comment: split code and comment to separate lines
    for sep in (" //", " #"):
        idx = stripped.rfind(sep)
        if idx > indent and idx < len(stripped) - 2:
            code_part = stripped[:idx].rstrip()
            comment_part = stripped[idx:].lstrip()
            if len(code_part) <= MAX_CODE:
                comment_line = indent_str + comment_part
                if len(comment_line) <= MAX_CODE:
                    return [code_part + trail, comment_line + trail]
                comment_body = comment_part.lstrip("/# ").lstrip()
                c_prefix = indent_str + sep.lstrip() + " "
                return ([code_part + trail] +
                        wrap_text(c_prefix, comment_body, MAX_CODE, trail))

    # Split at natural code break points (with or without space)
    # Try comma-with-space first, then comma-no-space, then operators
    for sc in [", ", " + ", " +=", " = ", ","]:
        search_end = MAX_CODE
        idx = stripped.rfind(sc, indent + 2, search_end)
        if idx > indent:
            split_at = idx + len(sc)
            first = stripped[:split_at].rstrip()
            rest = stripped[split_at:]
            if not rest.strip():
                continue
            # Continuation indent: 4 extra spaces
            cont = indent_str + "    " + rest
            if len(first) <= MAX_CODE and len(cont) <= MAX_CODE:
                return [first + trail, cont + trail]
            # If cont is still too long, try recursively
            if len(cont) > MAX_CODE:
                cont_break = break_code_line(cont + "\n")
                if (len(cont_break) > 1 and
                        all(len(l.rstrip("\n")) <= MAX_CODE
                            for l in cont_break)):
                    return [first + trail] + cont_break

    # Split method chain at ")." - wrap continuation with dot
    idx = stripped.rfind(").", indent + 4, MAX_CODE + 1)
    if idx > indent:
        first = stripped[:idx + 1]  # include )
        rest = "." + stripped[idx + 2:]  # keep the .
        cont = indent_str + "    " + rest
        if (len(first) <= MAX_CODE and len(cont) <= MAX_CODE
                and rest.strip()):
            return [first + trail, cont + trail]

    # Split Java class/method declarations at keywords
    for kw in [" extends ", " implements ", " throws "]:
        idx = stripped.find(kw, indent)
        if idx > indent:
            # kw goes from idx to idx+len(kw)-1 (space at end stays
            # on first line as trailing whitespace, stripped by rstrip)
            split_at = idx + len(kw) - 1  # keep space before keyword
            first = stripped[:split_at].rstrip()
            rest = stripped[split_at:].lstrip()
            if not rest:
                continue
            cont = indent_str + "    " + rest
            if (len(first) <= MAX_CODE and len(cont) <= MAX_CODE
                    and len(first) > indent + 4):
                return [first + trail, cont + trail]

    # Split after opening ( for method/function declarations
    paren_idx = stripped.rfind("(", indent, MAX_CODE)
    if paren_idx > indent + 4:
        first = stripped[:paren_idx + 1].rstrip()
        rest = stripped[paren_idx + 1:]
        if rest.strip():
            cont = indent_str + "    " + rest.lstrip()
            if len(first) <= MAX_CODE and len(cont) <= MAX_CODE:
                return [first + trail, cont + trail]
            if len(cont) > MAX_CODE:
                cont_break = break_code_line(cont + "\n")
                if (len(cont_break) > 1 and
                        all(len(l.rstrip("\n")) <= MAX_CODE
                            for l in cont_break)):
                    return [first + trail] + cont_break

    return [raw_line]


# ─── File fixer ────────────────────────────────────────────────

def fix_file(filepath, dry_run=False):
    """
    Fix all formatting violations in a single dictionary file.
    Returns (changed, counts_dict).
    """
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            raw = f.read()
    except Exception as e:
        print(f"  ERROR reading {filepath.name}: {e}")
        return False, {}

    counts = {
        "bom": 0, "h1": 0, "ascii": 0, "code": 0,
        "bold": 0, "emdash": 0, "hrule": 0,
    }

    # ── BOM removal ────────────────────────────────────────────
    if raw.startswith(BOM):
        raw = raw[len(BOM):]
        counts["bom"] += 1

    # ── Em dash replacement ────────────────────────────────────
    if EM_DASH in raw:
        counts["emdash"] = raw.count(EM_DASH)
        raw = raw.replace(EM_DASH, " - ")

    lines = raw.split("\n")
    fm_end = get_frontmatter_end(lines)
    if fm_end < 0:
        # Not a proper dictionary file, skip content checks
        if counts["bom"] or counts["emdash"]:
            new_content = raw
            if not dry_run:
                with open(filepath, "w", encoding="utf-8", newline="") as f:
                    f.write(new_content)
            return True, counts
        return False, counts

    fm_raw = "\n".join(lines[:fm_end + 1])
    is_dict = is_dict_file(fm_raw)
    body_start = fm_end + 1

    # ── Pass 1: H1 in body (dictionary files only) ────────────
    new_lines = list(lines)
    if is_dict:
        for i in range(body_start, min(body_start + 5, len(new_lines))):
            s = new_lines[i].lstrip()
            if s.startswith("# ") and not s.startswith("## "):
                new_lines[i] = None
                if (i + 1 < len(new_lines)
                        and new_lines[i + 1].strip() == ""):
                    new_lines[i + 1] = None
                counts["h1"] += 1
                break
    new_lines = [l for l in new_lines if l is not None]

    # ── Pass 2: ASCII width + code line fixes ──────────────────
    result = []
    in_code = False
    in_ascii = False

    for line in new_lines:
        raw_line = line + "\n"
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
                    for part in fixed:
                        result.append(part.rstrip("\n"))
                else:
                    result.append(fixed.rstrip("\n"))
                counts["ascii"] += 1
                continue
            if not in_ascii and line_len > MAX_CODE:
                fixed_lines = break_code_line(raw_line)
                if (len(fixed_lines) > 1
                        or fixed_lines[0] != raw_line):
                    for fl in fixed_lines:
                        result.append(fl.rstrip("\n"))
                    counts["code"] += 1
                    continue
        result.append(line)

    # ── Pass 3: Bold-label spacing ─────────────────────────────
    result2 = []
    in_fence = False
    prev_was_bold = False

    for line in result:
        stripped = line.rstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            prev_was_bold = False
            result2.append(line)
            continue
        if in_fence:
            result2.append(line)
            continue
        if BOLD_LABEL_RE.match(stripped.lstrip()):
            if prev_was_bold:
                result2.append("")
                counts["bold"] += 1
            prev_was_bold = True
        elif stripped == "":
            prev_was_bold = False
        result2.append(line)
    result = result2

    # ── Pass 4: --- before ### headings ───────────────────────
    result3 = []
    in_fence = False

    for idx, line in enumerate(result):
        stripped = line.rstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            result3.append(line)
            continue
        if in_fence:
            result3.append(line)
            continue
        if stripped.startswith("### "):
            # Check previous non-blank line
            prev_nb = None
            for j in range(len(result3) - 1, -1, -1):
                if result3[j].strip():
                    prev_nb = result3[j].strip()
                    break
            if prev_nb != "---":
                # Need to insert blank + --- + blank before ###
                # Remove trailing blank lines from result3, add --- structure
                while result3 and result3[-1].strip() == "":
                    result3.pop()
                result3.append("")
                result3.append("---")
                result3.append("")
                counts["hrule"] += 1
        result3.append(line)
    result = result3

    new_content = "\n".join(result)
    changed = new_content != raw or counts["bom"] > 0

    if changed and not dry_run:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            f.write(new_content)

    return changed, counts


# ─── Main ──────────────────────────────────────────────────────

def iter_files(tier_filter=None, file_filter=None):
    """Yield all dictionary .md files (excluding index.md)."""
    for fp in sorted(DICT_DIR.rglob("*.md")):
        if fp.name == "index.md":
            continue
        if tier_filter and tier_filter not in str(fp):
            continue
        if file_filter and file_filter.lower() not in fp.name.lower():
            continue
        yield fp


def main():
    dry_run = "--dry-run" in sys.argv
    tier_filter = None
    file_filter = None

    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--tier" and i + 1 < len(args):
            tier_filter = args[i + 1]
        elif a == "--file" and i + 1 < len(args):
            file_filter = args[i + 1]

    if dry_run:
        print("DRY RUN - no files modified\n")

    totals = {k: 0 for k in
              ["bom", "h1", "ascii", "code", "bold", "emdash", "hrule"]}
    n_changed = 0
    n_files = 0

    for fp in iter_files(tier_filter, file_filter):
        n_files += 1
        changed, c = fix_file(fp, dry_run=dry_run)
        if changed:
            n_changed += 1
            parts = []
            for k, v in c.items():
                if v:
                    parts.append(f"{k}:{v}")
            rel = fp.relative_to(REPO_ROOT)
            print(f"  {'DRY' if dry_run else 'FIX'} {rel.name}"
                  f"  [{' '.join(parts)}]")
        for k in totals:
            totals[k] += c.get(k, 0)

    print(f"\nFiles: {n_changed}/{n_files} changed")
    for k, v in totals.items():
        if v:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
