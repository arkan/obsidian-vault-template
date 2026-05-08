---
name: fact
description: "Add facts to vault entities (projects, people, companies). USE WHEN user says /fact followed by entity and fact text."
user_invocable: true
argument: "[[Entity]] fact text"
---

# Fact Skill

## Trigger

`/fact [[Entity]] Fact description`

## Behavior

1. Parse the argument:
   - Extract the `[[Entity]]` wikilink — this identifies the target file
   - Remaining text = fact description

2. Locate the entity file:
   - Search in `Projects/`, `Areas/People/`, `Areas/Companies/` for matching filename
   - If not found, ask user to clarify

3. Read the entity file to determine:
   - Current `fact_count` from frontmatter
   - Existing fact IDs under `## Active Facts`
   - Generate next ID: `<lowercase-filename>-<NNN>` (zero-padded 3 digits, auto-incremented)

4. Append the fact under `## Active Facts`:
   ```
   - `<id>` Fact description #status/active
   ```

5. Update frontmatter:
   - Increment `fact_count` by 1
   - Set `last_synthesis` to today's date (YYYY-MM-DD)

6. Confirm: "Fact `<id>` added to [[Entity]]"

## Superseding a fact

`/fact [[Entity]] !supersede <old-id> New fact description`

1. Find the fact with `<old-id>` under `## Active Facts`
2. Change its `#status/active` to `#status/superseded`
3. Move it to `## Superseded Facts`
4. Add the new fact under `## Active Facts` with a new ID
5. Net `fact_count` stays the same (one removed, one added from active perspective) — but increment the ID counter

## ID Generation

- Prefix = filename in lowercase with spaces replaced by `-`
  - `SaaS-Dashboard.md` → `saas-dashboard-001`
  - `Bob Dupont.md` → `bob-dupont-001`
- Number = max existing ID number + 1, zero-padded to 3 digits
- If no existing facts, start at `001`

## Rules

- ALWAYS read the entity file before modifying
- Preserve existing content and formatting
- Each fact is a single line — no multi-line facts
- Wikilinks inside facts are allowed: `/fact [[SaaS-Dashboard]] Deployed on [[Fly.io]] on March 20`
- If `## Active Facts` section doesn't exist, create it before `## Superseded Facts`
- If `## Superseded Facts` section doesn't exist, create it after `## Active Facts`

## Examples

Input: `/fact [[SaaS-Dashboard]] MVP deployed on Fly.io since March 20`
→ Appends under `## Active Facts`: `- \`saas-dashboard-001\` MVP deployed on Fly.io since March 20 #status/active`
→ Updates `fact_count: 1`, `last_synthesis: 2026-03-24`

Input: `/fact [[Bob Dupont]] Joined the Mobile-App project as lead backend in March 2026`
→ Appends: `- \`bob-dupont-003\` Joined the [[Mobile-App]] project as lead backend in March 2026 #status/active`

Input: `/fact [[SaaS-Dashboard]] !supersede saas-dashboard-001 MVP v2 deployed with new widget engine`
→ Moves `saas-dashboard-001` to superseded, adds new fact under active
