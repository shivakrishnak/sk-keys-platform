#!/usr/bin/env python3
"""Fix all validation errors in technical-mastery files.

Targets:
1. DLN-056..060 - wrong parent, missing fields, H1 in body,
   missing --- dividers, em dash (DLN-058)
2. GEN-004      - BOLD_LABEL_NO_BLANK at L141
3. VUE-028      - QRC_BORDER_BROKEN at L609 (missing closing pipe)
4. VUE-034      - QRC_BORDER_BROKEN at L166, L168
5. DBF-005      - QRC_BORDER_BROKEN at L310, L311 (trailing comments)
6. DPT-088      - QRC_BORDER_BROKEN at L265 (leading spaces + no close)
7. SYD files    - QRC_BORDER_BROKEN (spacer lines "  |" inside boxes)
8. MVN files    - same spacer pattern
9. TST-026      - same spacer pattern
10. OBS-022..027 AWS/AppDynamics files - missing id: field
"""

import os
import re

BASE = r"c:\Shiva\northstar\technical-mastery"


def read_utf8(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_utf8(path, content):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def fix_file_lines(path, line_fixes):
    """Apply targeted line-number-based fixes.
    line_fixes: {1-based-line-num: new_line_content_without_newline}
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for lineno, new_content in line_fixes.items():
        idx = lineno - 1
        # Preserve original line ending
        ending = "\n" if lines[idx].endswith("\n") else ""
        lines[idx] = new_content + ending
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)


def find_file(directory, prefix):
    """Find a file starting with prefix in directory."""
    for name in os.listdir(directory):
        if name.startswith(prefix) and name.endswith(".md"):
            return os.path.join(directory, name)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# FIX 1: DLN-056 to DLN-060
# ─────────────────────────────────────────────────────────────────────────────
print("=== FIX 1: DLN-056 to DLN-060 ===")
DLN_DIR = os.path.join(
    BASE, "tier-8-artificial-intelligence", "DLN-deep-learning"
)

dln_info = {
    "DLN-056": "model-quantization",
    "DLN-057": "knowledge-distillation",
    "DLN-058": "neural-network-pruning",
    "DLN-059": "inference-optimization",
    "DLN-060": "cuda-and-gpu-memory",
}

for code, slug in dln_info.items():
    fpath = find_file(DLN_DIR, code + " - ")
    if not fpath:
        print(f"  WARNING: {code} not found, skipping")
        continue

    content = read_utf8(fpath)

    # ── Fix frontmatter ───────────────────────────────────────────────
    # Split at exactly the first two --- delimiters
    m = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not m:
        print(f"  WARNING: {code} frontmatter not parsed, skipping")
        continue

    fm_lines = m.group(1).split("\n")
    body = m.group(2)

    new_fm_lines = []
    for line in fm_lines:
        if re.match(r"^parent:\s*tier-8-artificial-intelligence\s*$", line):
            new_fm_lines.append('parent: "Deep Learning"')
        else:
            new_fm_lines.append(line)

    # Add missing fields after layout: default
    fm_str = "\n".join(new_fm_lines)
    if "grand_parent:" not in fm_str:
        fm_str = re.sub(
            r"(layout:\s*default)",
            r'\1\ngrand_parent: "Technical Mastery"',
            fm_str,
        )
    if "status:" not in fm_str:
        fm_str = re.sub(
            r"(layout:\s*default)",
            r"\1\nstatus: complete",
            fm_str,
        )
    if "permalink:" not in fm_str:
        fm_str = re.sub(
            r"(nav_order:\s*\d+)",
            r"\1\npermalink: /technical-mastery/deep-learning/" + slug + "/",
            fm_str,
        )

    # ── Fix em dash in DLN-058 ────────────────────────────────────────
    if code == "DLN-058":
        body = body.replace("\u2014", "-")

    # ── Add --- dividers before ### headings ──────────────────────────
    body_lines = body.split("\n")
    new_body = []
    for i, line in enumerate(body_lines):
        if line.startswith("### "):
            # Find last non-empty line in new_body
            last_nonempty = ""
            for prev in reversed(new_body):
                if prev.strip():
                    last_nonempty = prev.strip()
                    break
            if last_nonempty != "---":
                if new_body and new_body[-1].strip() != "":
                    new_body.append("")
                new_body.append("---")
                new_body.append("")
        new_body.append(line)
    body = "\n".join(new_body)

    # ── Remove H1 yaml-validation line (and preceding --- if present) ─
    # Pattern: optional \n---\n then \n# yaml-validation:... at end
    body = re.sub(
        r"\n\n---\n# yaml-validation:.*$", "", body.rstrip(), flags=re.DOTALL
    )
    body = re.sub(r"\n# yaml-validation:.*$", "", body.rstrip())
    body = body.rstrip()

    # ── Rebuild and write ─────────────────────────────────────────────
    new_content = "---\n" + fm_str + "\n---\n" + body + "\n"
    write_utf8(fpath, new_content)
    print(f"  Fixed {code}: {os.path.basename(fpath)}")


# ─────────────────────────────────────────────────────────────────────────────
# FIX 2: GEN-004 - BOLD_LABEL_NO_BLANK at L141
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 2: GEN-004 BOLD_LABEL_NO_BLANK ===")
GEN_DIR = os.path.join(
    BASE, "tier-8-artificial-intelligence", "GEN-generative-ai"
)
gen004 = find_file(GEN_DIR, "GEN-004 - ")
if gen004:
    lines = open(gen004, "r", encoding="utf-8").readlines()
    # L141 (0-indexed: 140) is a **Cost:** line immediately after **Gain:**
    # We need to insert a blank line BEFORE the **Cost:** line at L141
    # Find the pair: line ending **Gain:**... immediately followed by **Cost:**...
    fixed = []
    i = 0
    inserted = False
    while i < len(lines):
        line = lines[i]
        if (not inserted
                and line.strip().startswith("**Gain:**")
                and i + 1 < len(lines)
                and lines[i + 1].strip().startswith("**Cost:**")):
            fixed.append(line)
            fixed.append("\n")  # insert blank line
            inserted = True
        else:
            fixed.append(line)
        i += 1
    with open(gen004, "w", encoding="utf-8", newline="") as f:
        f.writelines(fixed)
    print(f"  Fixed GEN-004: inserted blank between **Gain:** and **Cost:**")
else:
    print("  WARNING: GEN-004 not found")


# ─────────────────────────────────────────────────────────────────────────────
# FIX 3: VUE-028 L609 - missing closing pipe
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 3: VUE-028 L609 ===")
VUE_DIR = os.path.join(BASE, "tier-7-frontend", "VUE-vuejs")
vue028 = find_file(VUE_DIR, "VUE-028 - ")
if vue028:
    lines = open(vue028, "r", encoding="utf-8").readlines()
    idx = 608  # L609 = index 608
    old = lines[idx].rstrip("\n")
    # Change 4-space indent to 2-space and add closing pipe
    # Old: "│    useForm({ validationSchema }) → { handleSubmit, errors }"
    # New: "│  useForm({ validationSchema }) → { handleSubmit, errors }│"
    if old.startswith("\u2502    useForm"):
        lines[idx] = (
            "\u2502  useForm({ validationSchema }) "
            "\u2192 { handleSubmit, errors }\u2502\n"
        )
        with open(vue028, "w", encoding="utf-8", newline="") as f:
            f.writelines(lines)
        print(f"  Fixed VUE-028 L609")
    else:
        print(f"  WARNING: VUE-028 L609 content unexpected: {repr(old[:60])}")
else:
    print("  WARNING: VUE-028 not found")


# ─────────────────────────────────────────────────────────────────────────────
# FIX 4: VUE-034 L166 and L168 - missing closing pipe
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 4: VUE-034 L166, L168 ===")
vue034 = find_file(VUE_DIR, "VUE-034 - ")
if vue034:
    lines = open(vue034, "r", encoding="utf-8").readlines()
    changed = []

    # L166 (idx=165): ends with └──────────────────────┘ → append │
    idx166 = 165
    old166 = lines[idx166].rstrip("\n")
    if old166.startswith("\u2502") and not old166.endswith("\u2502"):
        lines[idx166] = old166 + "\u2502\n"
        changed.append("L166")

    # L168 (idx=167): ends with "URLs" → append │
    idx168 = 167
    old168 = lines[idx168].rstrip("\n")
    if old168.startswith("\u2502") and not old168.endswith("\u2502"):
        lines[idx168] = old168 + "\u2502\n"
        changed.append("L168")

    if changed:
        with open(vue034, "w", encoding="utf-8", newline="") as f:
            f.writelines(lines)
        print(f"  Fixed VUE-034 lines: {', '.join(changed)}")
    else:
        print("  WARNING: VUE-034 L166/L168 not matching expected pattern")
else:
    print("  WARNING: VUE-034 not found")


# ─────────────────────────────────────────────────────────────────────────────
# FIX 5: DBF-005 L310, L311 - trailing inline comments after closing pipe
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 5: DBF-005 L310, L311 ===")
DBF_DIR = os.path.join(BASE, "tier-4-data", "DBF-database-fundamentals")
dbf005 = find_file(DBF_DIR, "DBF-005 - ")
if dbf005:
    lines = open(dbf005, "r", encoding="utf-8").readlines()
    changed = []
    for lineno in (309, 310):  # L310=idx309, L311=idx310
        old = lines[lineno].rstrip("\n")
        # Line starts with │ and has │ somewhere in the middle,
        # then trailing text after last │. Truncate at last │.
        if old.startswith("\u2502") and "\u2502" in old[1:]:
            last_pipe = old.rfind("\u2502")
            # Only fix if there's trailing text after last pipe
            if last_pipe < len(old) - 1:
                lines[lineno] = old[: last_pipe + 1] + "\n"
                changed.append(f"L{lineno + 1}")
    if changed:
        with open(dbf005, "w", encoding="utf-8", newline="") as f:
            f.writelines(lines)
        print(f"  Fixed DBF-005 lines: {', '.join(changed)}")
    else:
        print("  WARNING: DBF-005 L310/L311 not matching expected pattern")
else:
    print("  WARNING: DBF-005 not found")


# ─────────────────────────────────────────────────────────────────────────────
# FIX 6: DPT-088 L265 - leading spaces before │ inside QRC box
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 6: DPT-088 L265 ===")
DPT_DIR = os.path.join(
    BASE, "tier-5-distributed-architecture", "DPT-design-patterns"
)
dpt088 = find_file(DPT_DIR, "DPT-088 - ")
if dpt088:
    lines = open(dpt088, "r", encoding="utf-8").readlines()
    idx = 264  # L265 = index 264
    old = lines[idx].rstrip("\n")
    # Old: "  │ (renewal)"  - 2 leading spaces + │ + content, no closing │
    # Box is 59 chars wide (57 content). Make a proper content line.
    # "│ (renewal)                                              │" = 59 chars
    BOX_WIDTH = 59
    if old.startswith("  \u2502"):
        # Remove leading spaces, add padding + closing │
        content_part = old.lstrip()  # e.g. "│ (renewal)"
        inner = content_part[1:]     # " (renewal)"
        # Pad inner to 57 chars, then add closing │
        inner_padded = inner.ljust(57)
        lines[idx] = "\u2502" + inner_padded + "\u2502\n"
        with open(dpt088, "w", encoding="utf-8", newline="") as f:
            f.writelines(lines)
        print(f"  Fixed DPT-088 L265")
    else:
        print(f"  WARNING: DPT-088 L265 content unexpected: {repr(old)}")
else:
    print("  WARNING: DPT-088 not found")


# ─────────────────────────────────────────────────────────────────────────────
# FIX 7 + 8 + 9: SYD / MVN / TST - remove "  │" spacer lines inside QRC boxes
# Strategy: inside any ┌...┐ box, delete lines that are ONLY whitespace+│
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 7+8+9: SYD / MVN / TST spacer lines ===")

# Exact files and lines from _errors_only.txt
SPACER_FILES = {
    # SYD files
    "tier-5-distributed-architecture/SYD-system-design/SYD-044": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-045": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-046": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-048": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-049": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-050": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-051": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-052": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-053": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-054": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-055": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-057": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-058": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-059": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-060": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-062": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-063": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-064": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-065": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-066": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-067": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-068": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-069": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-070": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-071": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-073": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-074": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-075": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-076": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-077": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-078": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-079": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-080": None,
    "tier-5-distributed-architecture/SYD-system-design/SYD-081": None,
    # MVN files
    "tier-6-infrastructure-devops/MVN-maven-build/MVN-006": None,
    "tier-6-infrastructure-devops/MVN-maven-build/MVN-008": None,
    "tier-6-infrastructure-devops/MVN-maven-build/MVN-011": None,
    "tier-6-infrastructure-devops/MVN-maven-build/MVN-013": None,
    "tier-6-infrastructure-devops/MVN-maven-build/MVN-014": None,
    "tier-6-infrastructure-devops/MVN-maven-build/MVN-015": None,
    # TST files
    "tier-6-infrastructure-devops/TST-testing/TST-026": None,
}

# Spacer line pattern: line stripped is exactly "│" (U+2502)
SPACER_PAT = re.compile(r"^\s+\u2502\s*$")

fixed_spacer_count = 0
for rel_prefix, _ in SPACER_FILES.items():
    parts = rel_prefix.rsplit("/", 1)
    dir_path = os.path.join(BASE, parts[0])
    code = parts[1]
    fpath = find_file(dir_path, code + " - ")
    if not fpath:
        print(f"  WARNING: {code} not found")
        continue

    raw_lines = open(fpath, "r", encoding="utf-8").readlines()
    in_box = False
    new_lines = []
    removed = 0
    for raw_line in raw_lines:
        line_stripped = raw_line.rstrip("\n")
        if line_stripped.startswith("\u250c") and line_stripped.endswith(
            "\u2510"
        ):
            in_box = True
            new_lines.append(raw_line)
        elif in_box and line_stripped.startswith("\u2514"):
            in_box = False
            new_lines.append(raw_line)
        elif in_box and SPACER_PAT.match(line_stripped):
            # Skip spacer lines
            removed += 1
        else:
            new_lines.append(raw_line)

    if removed > 0:
        with open(fpath, "w", encoding="utf-8", newline="") as f:
            f.writelines(new_lines)
        fixed_spacer_count += 1
        print(f"  Fixed {code}: removed {removed} spacer line(s)")
    else:
        print(f"  WARNING: {code} - no spacer lines found (check manually)")

print(f"  Total spacer files fixed: {fixed_spacer_count}")


# ─────────────────────────────────────────────────────────────────────────────
# FIX 10: OBS-022..027 (AWS/AppDynamics files) - add missing id: field
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 10: OBS missing id: fields ===")
OBS_DIR = os.path.join(
    BASE, "tier-6-infrastructure-devops", "OBS-observability-sre"
)

obs_files_needing_id = [
    ("OBS-022", "OBS-022 - AWS CloudWatch Dashboards.md"),
    ("OBS-023", "OBS-023 - AWS CloudWatch Log Insights.md"),
    ("OBS-024", "OBS-024 - AWS CloudWatch Alarms.md"),
    ("OBS-025", "OBS-025 - AWS X-Ray (Distributed Tracing).md"),
    ("OBS-026", "OBS-026 - Actionable Alerting Patterns.md"),
    ("OBS-027", "OBS-027 - AppDynamics.md"),
]

for obs_id, fname in obs_files_needing_id:
    fpath = os.path.join(OBS_DIR, fname)
    if not os.path.exists(fpath):
        print(f"  WARNING: {fname} not found")
        continue
    content = read_utf8(fpath)
    if "\nid: " in content or content.startswith("---\nid:"):
        print(f"  SKIP {fname} - already has id:")
        continue
    # Insert id: as first field after opening ---
    new_content = re.sub(
        r"^---\n",
        f"---\nid: {obs_id}\n",
        content,
    )
    write_utf8(fpath, new_content)
    print(f"  Fixed {fname}: added id: {obs_id}")

print("\n=== ALL FIXES COMPLETE ===")
