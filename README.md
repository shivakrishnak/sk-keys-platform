# sk-keys Technical Reference

A comprehensive software engineering reference:

1. **Technical Mastery** - 3,638+ keyword entries across 55 categories in 9 tiers (v4.0) - Finalized and Locked

## Structure

| Folder                | Purpose                                       |
| --------------------- | --------------------------------------------- |
| `technical-mastery/`         | technical-mastery entries organized by tier/category |
| `technical-mastery/_config/` | technical-mastery specs and generation scripts       |
| `.github/`            | Copilot instructions, prompts, and workflows  |
| `tmp/`                | Historical utility scripts                    |

## Agents (recommended)

Use `/technical-mastery` in VS Code Copilot chat for end-to-end content generation:

```
/technical-mastery tier-3 JVM              Generate entries for JVM category
/technical-mastery upgrade tier-1 CSF      Upgrade CSF entries to v4.0
/technical-mastery new: PostgreSQL, Trino  Generate keywords + content for new topics
/technical-mastery "Strong SQL skills..."  Analyze description, create keywords + content
```

## Prompts

```bash
# Technical Mastery: @technical-mastery-generate-entries, @technical-mastery-generate-keywords, @technical-mastery-upgrade-batch
```

## Specs

- Technical Mastery: `technical-mastery/_config/ENTRY_GENERATOR_PROMPT.md` (v4.0)
- Keywords: `technical-mastery/_config/MASTERY_OS_PROMPT.md`

See `.github/copilot-instructions.md` for workspace instructions.

## Deploy to GitHub Pages

1. Go to **Settings -> Pages**
2. Select `main` branch, root `/`
3. Live at `https://shivakrishnak.github.io/sk-keys/`
