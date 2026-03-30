---
name: article
description: Write and iterate on blog articles from idea to publishable draft. Use this skill whenever the user wants to write a new article, continue working on a draft, edit or improve an existing article, or mentions /article. Covers the full lifecycle — from brainstorming and outlining to polishing and finalizing. Also triggers when the user says things like "write a blog post about...", "I have an article idea", "help me finish this draft", or "improve this article".
---

# Article Skill

Write, iterate, and polish blog articles stored in `Resources/Articles/`.

## Trigger

- `/article <idea or title>` — start a new article from an idea
- `/article edit <filename>` — resume/improve an existing article
- `/article list` — list all articles with their status
- `/article status <filename>` — show current state and next steps for an article

## Article Storage

All articles live in `Resources/Articles/` as Markdown files with frontmatter.

### Frontmatter Schema

```yaml
---
type: article
title: "Article Title"
slug: "article-title"
tags: []
lang: en          # en or fr — match the article's language
status: idea      # idea → outline → draft → review → published
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### Status Lifecycle

| Status | Meaning |
|--------|---------|
| `idea` | Just the seed — title and rough concept |
| `outline` | Structure validated, sections defined |
| `draft` | Full content written, needs revision |
| `review` | Polished, ready for final read-through |
| `published` | Done — no further edits expected |

### File Naming

`Title-Of-Article.md` — PascalCase with hyphens, matching vault conventions.

## Workflow: New Article

When the user provides an idea, walk through these stages. Each stage ends by **saving the file** so progress is never lost. The user can stop at any point and resume later.

### Stage 1 — Seed

1. Understand the idea: ask 1-2 clarifying questions if the intent is ambiguous (audience, angle, key takeaway). Skip if the idea is already clear.
2. Detect or ask the target language.
3. Create the file in `Resources/Articles/` with frontmatter (`status: idea`) and a `## Notes` section capturing the raw idea, audience, and angle.
4. Save and confirm: "Article created. Shall we move to the outline?"

### Stage 2 — Outline

1. Propose an outline: title, sections with 1-line summaries, estimated length.
2. Information flows like a DAG — order sections so each one builds on what came before. Flag any dependency you're unsure about.
3. Present the outline and ask for validation. The user may reorder, add, remove, or merge sections.
4. Once approved, update the file with the outline under `## Outline` and set `status: outline`.
5. Save and confirm.

### Stage 3 — Draft

1. Write section by section. After each section:
   - Append it to the file under its heading
   - Save immediately
   - Show a brief summary of what was written and ask: "Next section, or do you want to adjust something?"
2. Keep paragraphs tight — aim for clarity over length. Each paragraph should carry one idea.
3. The user can interrupt to revise, rewrite, or skip ahead at any time.
4. When all sections are drafted, set `status: draft`.

### Stage 4 — Review

1. Do a full pass focusing on:
   - **Flow**: transitions between sections, logical progression
   - **Clarity**: jargon, ambiguity, sentences that try to do too much
   - **Hooks**: does the intro grab? does the conclusion land?
   - **Redundancy**: repeated ideas across sections
2. Present proposed changes as a numbered list. The user approves, rejects, or tweaks each one.
3. Apply approved changes, save, set `status: review`.

### Stage 5 — Polish

1. Final pass: grammar, typos, formatting consistency, link placeholders.
2. Generate a meta-description (max 160 chars) and suggest tags if missing.
3. Save, set `status: published`.
4. Confirm: "Article ready to publish."

## Workflow: Edit Existing Article

When the user says `/article edit <filename>` or asks to improve an article:

1. Read the file from `Resources/Articles/`.
2. Check `status` to understand where it left off.
3. Present a quick diagnostic:
   - Current status and word count
   - What's done vs what's missing
   - Suggested next step
4. Ask: "Shall we resume at [suggested step], or do you want to do something else?"
5. Resume the iterative workflow from the appropriate stage.

For targeted edits (rewrite a section, change tone, shorten), apply the change directly, save, and show the diff summary.

## Workflow: List Articles

Read all `.md` files in `Resources/Articles/`, extract frontmatter, and present:

| Article | Status | Lang | Updated |
|---------|--------|------|---------|

## Writing Principles

These aren't rigid rules — they're the reasoning behind good article writing. Apply judgment.

- **Lead with value.** The reader should know within the first 2-3 sentences what they'll get from this article and why it matters to them.
- **One idea per paragraph.** If a paragraph covers two ideas, split it. This makes articles scannable and ideas easier to follow.
- **Show, don't just tell.** Concrete examples, code snippets, or anecdotes make abstract ideas tangible. When you catch yourself writing "it's important to...", look for a way to demonstrate *why* instead.
- **Respect the reader's time.** Every sentence should earn its place. Cut filler, hedge words, and throat-clearing ("In this article, we will..."). Get to the point.
- **Match the user's voice.** Pay attention to tone cues in the idea description and any existing content. Mirror that register — technical and precise, conversational and direct, or somewhere in between.
- **Structure serves comprehension.** Use headings, lists, and code blocks to break up walls of text. But don't over-structure — a list of 2 items is just two sentences.

## Key Behaviors

- **Always save after each stage.** The file is the source of truth. If the conversation ends, the user can resume from exactly where they left off.
- **Update `updated` date** in frontmatter on every save.
- **Never overwrite without reading first.** Always read the current file state before editing.
- **Propose, don't impose.** Especially during outline and review — present options, let the user decide.
- **Detect language from context.** If the idea is written in French, write in French. If in English, write in English. Ask only if ambiguous.
