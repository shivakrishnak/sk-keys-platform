import pathlib

MAX_CODE = 70

fp = pathlib.Path(
    "dictionary/tier-6-infrastructure-devops"
    "/MVN-maven-build/MVN-019 - Maven Wrapper (mvnw).md"
)
with open(fp, "r", encoding="utf-8-sig") as f:
    raw = f.read()
lines = raw.split("\n")

i = 91
line = lines[i]
stripped = line.rstrip()
content = stripped.lstrip()
indent = len(stripped) - len(content)
body = content[1:].lstrip()

print(f"body bytes: {body.encode('utf-8').hex()[:80]}")
words = body.split(" ")
print(f"words count: {len(words)}")
for j, w in enumerate(words):
    print(f"  words[{j}]: {repr(w[:60])}")

# Trace wrap_text manually
prefix = " " * indent + "# "
trail = "\n"
current = prefix
lines_out = []

for word in words:
    print(f"\nProcessing word: {repr(word[:40])}...")
    print(f"  current: {repr(current)}")
    combined_len = len(current + word)
    print(f"  len(current+word) = {combined_len} vs max {MAX_CODE}")
    if combined_len <= MAX_CODE:
        current = current + word + " "
        print(f"  -> fits, current now: {repr(current[:40])}")
    else:
        if current.strip():
            print(f"  -> doesn't fit, appending: {repr(current.rstrip())}")
            lines_out.append(current.rstrip() + trail)
        current = prefix + word + " "
        print(f"  -> current reset to: {repr(current[:40])}")

print(f"\nAfter loop, current: {repr(current)}")
print(f"current.strip(): {repr(current.strip())}")
if current.strip():
    lines_out.append(current.rstrip() + trail)
    print(f"Appended: {repr(current.rstrip())}")

print(f"\nFinal lines_out: {len(lines_out)} elements")
for j, l in enumerate(lines_out):
    print(f"  [{j}]: {repr(l)}")
