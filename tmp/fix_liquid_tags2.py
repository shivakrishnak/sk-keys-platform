import os, re

files_to_fix = [
    "technical-mastery/tier-7-frontend/VUE-vuejs/VUE-054 - Migration Strategy (Vue 2 to Vue 3, Options to Composition).md",
]

FENCE = "```"

def fix_file(fpath):
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")
    # Step1: remove old raw tag lines
    lines = [l for l in lines if l.strip() not in ("{%- raw -%}", "{%- endraw -%}", "{% raw %}", "{% endraw %}")]
    # Step2: undo inline raw wrapping
    cleaned = []
    for line in lines:
        line = re.sub(r"\{%-?\s*raw\s*-?%\}(\{\{)", r"\1", line)
        line = re.sub(r"(\}\})\{%-?\s*endraw\s*-?%\}", r"\1", line)
        cleaned.append(line)
    lines = cleaned
    # Step3: apply correct fixes
    result = []
    in_fence = False
    fence_has_liquid = False
    fence_lines = []
    for line in lines:
        stripped = line.strip()
        if not in_fence and stripped.startswith(FENCE):
            in_fence = True
            fence_has_liquid = False
            fence_lines = [line]
        elif in_fence:
            fence_lines.append(line)
            if "{{" in line:
                fence_has_liquid = True
            if stripped == FENCE:
                in_fence = False
                if fence_has_liquid:
                    result.append("{% raw %}")
                    result.extend(fence_lines)
                    result.append("{% endraw %}")
                else:
                    result.extend(fence_lines)
                fence_lines = []
        else:
            if "{{" in line:
                fixed = re.sub(r"\{\{([^}]*)\}\}", r"{%- raw -%}{{\1}}{%- endraw -%}", line)
                result.append(fixed)
            else:
                result.append(line)
    if fence_lines:
        result.extend(fence_lines)
    new_content = "\n".join(result)
    if new_content != content:
        with open(fpath, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        return True
    return False

for fpath in files_to_fix:
    try:
        changed = fix_file(fpath)
        print(("Fixed" if changed else "No change") + ": " + os.path.basename(fpath))
    except Exception as e:
        print("ERROR: " + fpath + ": " + str(e))
