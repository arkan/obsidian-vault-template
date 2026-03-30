---
name: review
description: "Daily and weekly review workflows. USE WHEN user says /review morning, /review evening, /review weekly, /review monthly, or synonyms like 'start my day', 'end of day', 'weekly review', 'monthly review'."
user_invocable: true
argument: "morning | evening | weekly | monthly"
---

# Review Skill

Structured review routines for the Obsidian vault.

## Routing

| User says | Workflow |
|-----------|----------|
| `/review morning`, "start my day" | `workflows/morning.md` |
| `/review evening`, "end of day" | `workflows/evening.md` |
| `/review weekly`, "weekly review" | `workflows/weekly.md` |
| `/review monthly`, "monthly review" | `workflows/monthly.md` |

## Shared Rules

### Daily Note (lazy creation)

All routines that touch the daily note must:
1. Check if `Daily Notes/YYYY/YYYY-MM/YYYY-MM-DD.md` exists
2. If not, create it using `Templates/daily-note.md` format with proper frontmatter (`date`, `mood`, `sleep`)
3. The daily note path follows the vault convention: `Daily Notes/YYYY/YYYY-MM/YYYY-MM-DD.md`

### Data Sources

- **Tasks**: Read from `Areas/TODO.md` — look for `- [ ]` lines under `## Tasks`
- **Projects**: Read frontmatter from `Projects/*.md`
- **Goals**: Read `Areas/Goals.md` section `## Active Goals`
- **Inbox**: List files in `Inbox/`
- **Entities**: Files in `Areas/People/`, `Areas/Companies/`, `Projects/`

### Output Style

- Concise, actionable
- Use `[[wikilinks]]` when referencing vault entities
- Do NOT create separate check-in files — everything goes in the daily note
