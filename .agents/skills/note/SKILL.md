---
name: note
description: >
  Add a note to today's daily note under ## Notes. Enriches with [[wikilinks]] to known vault entities.
  USE WHEN user says /note followed by text, or "add to my notes", "log this today".
user_invocable: true
argument: text to log (free text)
---

# Note Skill

## Trigger

`/note <free text>`

## Behavior

1. Ensure today's daily note exists at `Daily Notes/YYYY/YYYY-MM/YYYY-MM-DD.md` (lazy creation using `Templates/daily-note.md` format if missing).

2. Scan the vault for known entities to build a wikilink map:
   - `Projects/*.md` — project entities
   - `Areas/People/*.md` — person entities
   - `Areas/Companies/*.md` — company entities
   - For each file: filename (without `.md`) is the primary name, plus `aliases` from frontmatter

3. Enrich the input text:
   - Replace mentions of known entity names or aliases with `[[Entity-Name]]` wikilinks (case-insensitive match, canonical filename in link). For alias matches, use pipe syntax: `[[Entity-Name|alias]]`
   - Preserve any `[[wikilinks]]` already present in the input as-is
   - Do NOT alter the meaning — only add links and light formatting
   - If the text contains multiple distinct points, split into bullet points

4. Append to the daily note under `## Notes`:
   - Add a blank line before the new content if `## Notes` already has content
   - Prefix with a timestamp: `**HH:mm** — `
   - Then the enriched text

5. Confirm to the user with a short summary of what was logged.

## Rules

- Content language follows user input
- Do NOT modify any other section of the daily note
- Do NOT read back the entire daily note — just confirm the append
- If `## Notes` section doesn't exist, create it before `## Log`
- Keep enrichment subtle: only link entities that are clearly referenced, don't force links

## Examples

Input: `/note Discussion with Bob about SaaS-Dashboard subscription pricing`
Result appended under `## Notes`:
```
**14:32** — Discussion with [[Bob Dupont|Bob]] about [[SaaS-Dashboard]] subscription pricing
```
Confirm: "Note added to today's daily note (2026-03-24)."

Input: `/note Three ideas for the dashboard: 1) KPI widget 2) real-time graph 3) CSV export`
Result appended under `## Notes`:
```
**16:05** —
- KPI widget for the dashboard
- Real-time graph
- CSV export
```
Confirm: "Note added (3 points) to today's daily note (2026-03-24)."
