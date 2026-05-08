---
name: brief
description: "Daily and weekly brief workflows. USE WHEN user says /brief morning, /brief evening, /brief weekly, /brief monthly, or synonyms like 'start my day', 'end of day', 'weekly brief', 'monthly brief'."
user_invocable: true
argument: "morning | evening | weekly | monthly"
argument-hint: "morning | evening | weekly | monthly"
---

# Brief Skill

Structured brief routines for the Obsidian vault.

## Routing

| User says | Workflow |
|-----------|----------|
| `/brief morning`, "start my day" | `workflows/morning.md` |
| `/brief evening`, "end of day" | `workflows/evening.md` |
| `/brief weekly`, "weekly brief" | `workflows/weekly.md` |
| `/brief monthly`, "monthly brief" | `workflows/monthly.md` |

## Shared Rules

### Daily Note (lazy creation)

All routines that touch the daily note must:
1. Check if `Daily Notes/YYYY/YYYY-MM/YYYY-MM-DD.md` exists
2. If not, create it using `Templates/daily-note.md` format with proper frontmatter (`date`, `mood`, `sleep`)
3. The daily note path follows the vault convention: `Daily Notes/YYYY/YYYY-MM/YYYY-MM-DD.md`

### Data Sources

- **Tasks**: Use `td list` and `td list --all` (never read `Areas/TODO.md` directly). See the `td` skill for command reference.
- **Projects**: Read frontmatter from `Projects/*.md`
- **Goals**: Read `Areas/Goals.md` section `## Objectives`
- **Inbox**: List files in `Inbox/` excluding `To sort.md`
- **Entities**: Files in `Areas/People/`, `Areas/Companies/`, `Projects/`

### Output Style

- Concise, actionable, in French
- Use `[[wikilinks]]` when referencing vault entities
- Do NOT create separate check-in files — everything goes in the daily note
