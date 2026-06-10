import pathlib

fp = pathlib.Path(
    "dictionary/tier-6-infrastructure-devops"
    "/MVN-maven-build/MVN-019 - Maven Wrapper (mvnw).md"
)
with open(fp, "r", encoding="utf-8-sig") as f:
    raw = f.read()
lines = raw.split("\n")

# Show line 92 (0-indexed: 91) character by character
line = lines[91]
print(f"Line 92 length: {len(line)}")
print(f"First 40 chars: {repr(line[:40])}")
print(f"Chars 60-80: {repr(line[60:80])}")
print(f"Full repr: {repr(line)}")

# Check body passed to wrap_text
content = line.rstrip().lstrip()
print(f"\ncontent starts with #: {content.startswith('#')}")
body = content[1:].lstrip()
print(f"body: {repr(body[:60])}")
words = body.split(" ")
print(f"word count: {len(words)}")
print(f"word[0] len: {len(words[0])}")
