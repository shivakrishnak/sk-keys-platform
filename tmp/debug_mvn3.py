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

# Debug: show what's happening at line 92 step by step
i = 91  # 0-indexed = line 92
line = lines[i]
raw_line = line + "\n"
print(f"raw_line: {repr(raw_line)}")
print(f"raw_line ends with newline: {raw_line.endswith(chr(10))}")
print(f"len(line) = {len(line)}")

stripped = line.rstrip()
print(f"stripped: {repr(stripped[:50])}...")
content = stripped.lstrip()
indent = len(stripped) - len(content)
print(f"indent = {indent}")
print(f"content[0] = {repr(content[0])}")
body = content[1:].lstrip()
print(f"body: {repr(body[:60])}")
print(f"body word count: {len(body.split(' '))}")

result = wrap_text(" " * indent + "# ", body, MAX_CODE, "\n")
print(f"\nwrap_text result: {len(result)} elements")
for j, r in enumerate(result):
    print(f"  [{j}]: {repr(r)}")

print(f"\nresult[0] == raw_line: {result[0] == raw_line}")
print(f"diff: {repr(result[0])} vs {repr(raw_line)}")
