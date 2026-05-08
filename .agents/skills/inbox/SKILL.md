---
name: inbox
description: Quick capture to Inbox. USE WHEN user says /inbox followed by text. Extracts #tags, generates summary title, creates timestamped note in Inbox/.
user_invocable: true
argument: text to capture (free text with optional #tags inline)
---

# Inbox Capture Skill

## Trigger

`/inbox <free text with optional #tags>`

## Behavior

1. Parse the argument text:
   - Extract all `#tag` patterns from the text (e.g., `#urgent`, `#tech`, `#client/xxx`)
   - Remove extracted tags from the body text
   - The remaining cleaned text is the capture content

2. Generate a short summary title (3-6 words max) from the capture content. This becomes the `title` field in frontmatter.

3. Create a new file at: `Inbox/YYYY-MM-DD-HHmmss.md`
   - Use current date/time for the filename
   - Timestamp format: `date +%Y-%m-%d-%H%M%S`

4. File content format:

```markdown
---
type: note
status: inbox
tags: [inbox, <extracted_tags>]
created: YYYY-MM-DD HH:mm
source: claude-code
title: "<generated summary>"
---

## Content

<cleaned capture text with [[wikilinks]] preserved>
```

5. Confirm capture to user with: filename, title, and tags extracted.

## Rules

- Always include `inbox` in the tags array alongside any extracted tags
- Preserve any `[[wikilinks]]` in the content as-is
- If no #tags are found, tags array is just `[inbox]`
- Strip the `#` prefix when putting tags in frontmatter YAML array
- Content language follows user input
- Do NOT open or read the file after creation — just confirm

## Examples

Input: `/inbox #urgent Follow up with [[Alice Martin]] about the freelance contract`
→ File: `Inbox/2026-03-23-143022.md`
→ Title: "Follow up Alice contract"
→ Tags: `[inbox, urgent]`
→ Body: `Follow up with [[Alice Martin]] about the freelance contract`

Input: `/inbox Idea: use Dataview to track fact_count per project #tech #knowledge-management`
→ File: `Inbox/2026-03-23-150100.md`
→ Title: "Dataview tracking fact_count"
→ Tags: `[inbox, tech, knowledge-management]`
→ Body: `Idea: use Dataview to track fact_count per project`
