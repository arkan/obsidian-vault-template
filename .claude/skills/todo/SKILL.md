---
name: todo
description: Manage tasks in TODO.md. USE WHEN user says /todo to add, list, complete, or manage tasks.
user_invocable: true
argument: action and task text
---

# Todo Skill

## Trigger

`/todo <action> <args>`

## Actions

### Add (default)

`/todo Follow up with Alice @SaaS-Dashboard !high 📅 2026-03-28`

1. Parse the input:
   - Extract `!high` / `!medium` / `!low` → convert to obsidian-tasks emoji
   - Extract `@ProjectName` → convert to `#project/<lowercase>`
   - Extract `📅 YYYY-MM-DD` → keep as-is
   - Remaining text = task description
2. If no date provided, omit the date emoji
3. If no priority provided, omit the priority emoji
4. Append the task line to `Areas/TODO.md` under `## Tasks` section
5. Confirm with task text as rendered

Priority mapping:
| Input | Emoji |
|-------|-------|
| `!high` | `⏫` |
| `!medium` | `🔼` |
| `!low` | `🔽` |

Task line format (obsidian-tasks compatible):
```
- [ ] <description> <#project/xxx> <priority_emoji> 📅 <date>
```

Order of elements: description, project tag, priority, date.

### List

`/todo list`

1. Read `Areas/TODO.md`
2. Extract all unchecked tasks (`- [ ]`)
3. Present as a numbered markdown table with columns: #, Task, Priority, Project, Due Date

### Done

`/todo done <partial text>`

1. Read `Areas/TODO.md`
2. Find the unchecked task matching the partial text (case-insensitive fuzzy match)
3. If multiple matches, show them and ask user to pick
4. Change `- [ ]` to `- [x]` and append ` ✅ YYYY-MM-DD` (today's date)
5. Move the task from `## Tasks` to `## Archive`
6. Confirm completion

## Rules

- ALWAYS read `Areas/TODO.md` before any operation
- Never duplicate tasks — check for existing similar text before adding
- Preserve existing task formatting when reading
- The `@Project` tag should match an existing project in `Projects/` — use `[[wikilinks]]` in the project tag if the project exists
- When no action keyword is given, default to **add**
- Content language follows user input

## Examples

Input: `/todo Follow up with Alice @SaaS-Dashboard !high 📅 2026-03-28`
→ Appends: `- [ ] Follow up with Alice #project/saas-dashboard ⏫ 📅 2026-03-28`

Input: `/todo list`
→ Shows table of open tasks

Input: `/todo done follow up`
→ Finds matching task, marks done, moves to archive

Input: `/todo Buy groceries`
→ Appends: `- [ ] Buy groceries`
