import sys

files = [
    r"c:\Shiva\northstar\technical-mastery\tier-7-frontend\FEA-frontend-architecture\FEA-092 - Next.js RSC Migration Strategy (2023-2025).md",
    r"c:\Shiva\northstar\technical-mastery\tier-7-frontend\FEA-frontend-architecture\FEA-095 - GDPR Cookie Consent Architecture.md",
    r"c:\Shiva\northstar\technical-mastery\tier-7-frontend\FEA-frontend-architecture\FEA-099 - Production Incident Simulation SPA Route Failure.md",
]

YAML_FENCE = "```yaml\n"
CLOSE_FENCE = "```"

for f in files:
    with open(f, encoding="utf-8") as fh:
        content = fh.read()

    last_yaml_idx = content.rfind(YAML_FENCE)
    if last_yaml_idx == -1:
        print(f"ERROR: no yaml fence found in {f}")
        continue

    # Check if already wrapped
    pre = content[max(0, last_yaml_idx - 20):last_yaml_idx]
    if "{% raw %}" in pre:
        print(f"SKIP (already wrapped): {f}")
        continue

    before = content[:last_yaml_idx]
    after = content[last_yaml_idx:]

    # after ends with: ...notes: "..."\n```\n  (possibly with trailing \n)
    # Strip trailing whitespace from after, then add {% endraw %}
    after_stripped = after.rstrip("\n")
    # Verify it ends with the closing fence
    if not after_stripped.endswith(CLOSE_FENCE):
        print(f"WARNING: after block does not end with ``` in {f}, ending: {after_stripped[-30:]!r}")
    
    new_content = before + "{% raw %}\n" + after_stripped + "\n{% endraw %}\n"

    with open(f, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new_content)

    # Verify
    with open(f, encoding="utf-8") as fh:
        verify = fh.read()
    raw_count = verify.count("{% raw %}")
    endraw_count = verify.count("{% endraw %}")
    print(f"Fixed: {f}")
    print(f"  raw tags: {raw_count}, endraw tags: {endraw_count}")
    last_lines = verify.splitlines()[-3:]
    print(f"  last 3 lines: {last_lines}")

print("Done")
