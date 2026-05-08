---
name: import
description: "Import external resources (articles, PDFs, videos, podcasts) into the Obsidian vault using the summarize CLI. Generates a French summary, auto-tags, and stores in Resources/. Use this skill when the user wants to save, import, capture, or archive any external content (URL, PDF, video, podcast) into the vault."
argument_hint: "<url_or_path> [#tags]"
---

# Import Resource

Import external content into the vault as a structured Obsidian note with French summary, auto-generated tags, and proper wikilinks.

## Trigger

`/import <url_or_path> [#tags] [--raw]`

## Input Parsing

1. Extract the URL or file path (first argument that looks like a URL or path)
2. Extract user-provided `#tags` (any `#word` tokens)
3. Detect `--raw` flag: if present, store the extracted raw content instead of a summary

## Workflow

### Step 1 — Extract raw content

Run the `summarize` CLI with `--extract` to fetch the raw content without LLM processing:

```bash
summarize "<url_or_path>" --extract --format md --plain 2>/dev/null
```

This returns the raw markdown content of the source. Save it for analysis.

If the command fails, try with `--firecrawl always` as fallback (some sites block default extraction):

```bash
summarize "<url_or_path>" --extract --format md --plain --firecrawl always 2>/dev/null
```

If both fail, report the error and stop.

### Step 2 — Generate French summary

Run `summarize` with `--cli Codex` to generate a French summary:

```bash
summarize "<url_or_path>" --lang fr --cli Codex --plain --length long 2>/dev/null
```

Save the summary output.

### Step 3 — Analyze and generate metadata

From the raw content and summary, generate:

1. **Title**: a clear, concise French title for the resource. If the source has an obvious title (HTML title, PDF title, video title), use it translated to French if needed. Keep it descriptive.

2. **Slug**: lowercase-kebab-case version of the title for the filename.

3. **Tags**: merge two sources:
   - User-provided `#tags` (strip the `#`)
   - Auto-generated tags (3-8 tags) based on content analysis. Use lowercase, hyphenated tags. Prefer existing vault tag conventions when possible: `go`, `tech`, `devops`, `infra`, `finance`, `ai`, `business`, `health`, `productivity`, etc.

4. **Source type**: detect from URL/content — `article`, `video`, `podcast`, `pdf`, `documentation`, `tutorial`, `talk`

5. **Language of source**: detect the original language (`fr`, `en`, etc.)

### Step 4 — Scan vault for wikilinks

Before writing, scan vault entities for wikilink enrichment:
- `Projects/*.md` — project entities + aliases from frontmatter
- `Areas/People/*.md` — person entities + aliases
- `Areas/Companies/*.md` — company entities + aliases

Replace mentions of known entities in the summary text with `[[Entity-Name]]` wikilinks. For alias matches, use `[[Entity-Name|alias]]`.

### Step 5 — Create the note

Write to: `Resources/ImportedURLs/<Slug>.md`

Use this template:

```markdown
---
type: importedURL
title: "<title>"
source: "<original_url_or_path>"
source_type: <article|video|podcast|pdf|documentation|tutorial|talk>
source_lang: <fr|en|...>
tags: [<tag1>, <tag2>, ...]
status: draft
created: <YYYY-MM-DD>
---

## Resume

<French summary — this is the main content. Well-structured with headers if the summary is long enough. Use ## subsections within the summary for clarity.>

## Points cles

<Bullet list of 5-10 key takeaways from the content, in French.>

## Source

- URL : <source_url>
- Type : <source_type>
- Langue originale : <source_lang>
- Importe le : <YYYY-MM-DD>
```

If `--raw` flag was passed, add an additional section before `## Source`:

```markdown
## Contenu original

<raw extracted content, as-is>
```

### Step 6 — Confirm

Report to the user:
```
Ressource importee : Resources/ImportedURLs/<Slug>.md
Titre : <title>
Tags : #tag1 #tag2 #tag3
Points cles : <count>
```

## Rules

- Always run `summarize --extract` first, then `summarize --lang fr --cli Codex` for the summary. Two separate calls.
- If the raw content is very short (< 500 chars), skip the summary step and store the raw content directly with a note that the source was too short for summarization.
- The summary language is always French, regardless of the source language.
- Tags in frontmatter use the YAML array format: `[tag1, tag2, tag3]`
- File naming: `Resources/ImportedURLs/<Slug>.md` where Slug is PascalCase-With-Hyphens (matching vault convention, e.g., `Migration-4GL-Vers-Go.md`)
- Do not duplicate: before creating, check if a file with the same source URL already exists in `Resources/ImportedURLs/`. If it does, ask the user if they want to overwrite.
- Content language for all note text, section headers, and descriptions is French.
- Keep summaries substantive — aim for 500-1500 words depending on source length. The goal is to capture enough that the user rarely needs to go back to the original source.
- Wikilink enrichment should be subtle: only link entities that are genuinely referenced, don't force connections.

### Post-Import — Log

After creating the note, append one line to `Areas/Codex/operations-log.md`:
```
| YYYY-MM-DD HH:MM | ingest | import | 1 créée | Resources/ImportedURLs/<slug> |
```
Create the file with header if it doesn't exist.

## Examples

Input: `/import https://go.dev/blog/go1.22`
Output: `Resources/ImportedURLs/Go-1.22-Nouveautes.md` with French summary, tags `[go, release, programming]`

Input: `/import https://youtube.com/watch?v=abc123 #ai #talk`
Output: `Resources/ImportedURLs/Conference-IA-Titre.md` with French summary of the video transcript, tags `[ai, talk, ...]`

Input: `/import ~/Downloads/rapport-annuel.pdf #finance`
Output: `Resources/ImportedURLs/Rapport-Annuel-Titre.md` with French summary, tags `[finance, ...]`

Input: `/import https://example.com/article --raw`
Output: Same as above but with an additional `## Contenu original` section containing the raw extracted text.
