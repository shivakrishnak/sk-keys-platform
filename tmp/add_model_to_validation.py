#!/usr/bin/env python3
"""
Add model: "claude-sonnet-4.6" after spec_version: 6.0 in all
technical-mastery validation blocks.
"""
import os
import re

ROOT = r"c:\Shiva\northstar\technical-mastery"
MODEL_LINE = '  model: "claude-sonnet-4.6"'
SPEC_PATTERN = re.compile(r'(  spec_version: 6\.0)')

updated = 0
skipped = 0
errors = 0

for dirpath, dirnames, filenames in os.walk(ROOT):
    for fname in filenames:
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(dirpath, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"READ ERROR: {fpath}: {e}")
            errors += 1
            continue

        # Skip if model line already present
        if 'model: "claude-sonnet' in content:
            skipped += 1
            continue

        # Skip if no validation block
        if "spec_version: 6.0" not in content:
            continue

        # Insert model line after spec_version: 6.0
        new_content = SPEC_PATTERN.sub(
            r'\1\n' + MODEL_LINE,
            content
        )

        if new_content == content:
            continue

        try:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            updated += 1
        except Exception as e:
            print(f"WRITE ERROR: {fpath}: {e}")
            errors += 1

print(f"\nDone: updated={updated}, already_had_model={skipped}, errors={errors}")
