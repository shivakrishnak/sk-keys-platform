import pathlib

MAX_CODE = 70

def wrap_text(prefix, body, max_len, trail):
    lines = []
    words = body.split(" ")
    current = prefix
    for word in words:
        if len(current + word) <= max_len:
            current = current + word + " "
        else:
            if current.strip():
                lines.append(current.rstrip() + trail)
            current = prefix + word + " "
    if current.strip():
        lines.append(current.rstrip() + trail)
    return lines if lines else [prefix + body + trail]

fp = pathlib.Path(
    "dictionary/tier-6-infrastructure-devops"
    "/MVN-maven-build/MVN-019 - Maven Wrapper (mvnw).md"
)
with open(fp, "r", encoding="utf-8-sig") as f:
    raw = f.read()
lines = raw.split("\n")
in_code = False
for i, line in enumerate(lines):
    raw_line = line + "\n"
    stripped_fence = line.rstrip()
    if stripped_fence.startswith("```"):
        in_code = not in_code
        continue
    if in_code:
        stripped = line.rstrip()
        line_len = len(stripped)
        if line_len > MAX_CODE:
            content = stripped.lstrip()
            indent = len(stripped) - len(stripped.lstrip())
            if content.startswith("#") and not content.startswith("#!"):
                result = wrap_text(
                    " " * indent + "# ", content[1:].lstrip(),
                    MAX_CODE, "\n"
                )
                if result[0] != raw_line or len(result) > 1:
                    print(f"Line {i+1} ({line_len}c) WOULD CHANGE:")
                    print(f"  Original: {repr(raw_line)}")
                    for j, r in enumerate(result):
                        print(f"  Result[{j}]: {repr(r)}")
print("Done checking # lines.")
