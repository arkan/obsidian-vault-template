---
name: x-import
description: "Import X (Twitter) bookmarks into the Obsidian vault using the bird CLI. Two-phase architecture: Python script handles fetching/dedup/URL resolution/content fetching/file writing, LLM generates English summaries from pre-fetched content. Creates notes in Resources/X-Bookmarks/ with a .base database view. Use this skill when the user wants to sync, import, or fetch their X/Twitter bookmarks, or mentions bird bookmarks."
argument_hint: "[--all | --count N]"
---

# X Bookmarks Import

Import X (Twitter) bookmarks into the vault as individual structured Obsidian notes, with an Obsidian Bases database view for browsing, filtering, and sorting.

## Trigger

`/x-import` — fetch last 30 bookmarks (daily incremental)
`/x-import --all` — fetch all bookmarks (full initial sync, slow)
`/x-import --count N` — fetch N bookmarks

## Storage

- Individual notes: `Resources/X-Bookmarks/<YYYY-MM-DD>-<Slug>.md`
- Database view: `Bases/X-Bookmarks.base`
- Script: `.agents/skills/x-import/x_bookmarks.py`
- LLM manifest: `/tmp/x_bookmarks_manifest.json`

## Architecture

The import is split into two phases to minimize LLM token usage:

1. **Python script** (mechanical) — fetches bookmarks via bird CLI, deduplicates, groups threads, resolves t.co URLs, fetches linked page content (title + body text), auto-generates tags, writes all files with `{{SUMMARY_PLACEHOLDER}}`. Outputs a manifest with pre-fetched content for LLM summarization. Also builds a See Also index of all existing files.
2. **LLM** (intelligence) — reads the manifest (which already contains fetched page content), generates English summaries, writes `## Linked Content` sections, scans vault for wikilinks, and fills `## See Also` cross-links using the pre-built index.

## Workflow

### Phase 1 — Run the Python script

```bash
# Incremental (default): last 30
python3 .agents/skills/x-import/x_bookmarks.py

# Full sync
python3 .agents/skills/x-import/x_bookmarks.py --all

# Custom count
python3 .agents/skills/x-import/x_bookmarks.py --count 50
```

The script:
1. Fetches bookmarks via `bird` CLI with `--json --include-parent --thread-meta`
2. Deduplicates by `tweet_id` against existing files in `Resources/X-Bookmarks/`
3. Groups tweets by `conversationId` into threads
4. For each new bookmark/thread (resolves URLs in parallel):
   - Resolves t.co shortened URLs to final destinations
   - Fetches linked page HTML, extracts title + body text (truncated to 5000 chars)
   - Skips media domains (x.com, twitter.com, youtube.com, etc.)
   - Auto-generates tags from tweet text + linked content
   - Writes the `.md` file with `{{SUMMARY_PLACEHOLDER}}`
5. Builds a See Also index: `{filename: {author, tags}}` from all existing files
6. Writes manifest to `/tmp/x_bookmarks_manifest.json`

Report the script's output to the user, then proceed to Phase 2.

If zero new bookmarks, stop here.

### Phase 2 — LLM generates English summaries

Read `/tmp/x_bookmarks_manifest.json`. It contains:
```json
{
  "manifest": [
    {
      "file": "2026-04-03-Slug-Name.md",
      "tweet_id": "123456",
      "author": "@username",
      "author_name": "Display Name",
      "date": "2026-04-03",
      "text": "tweet content (max 3000 chars)",
      "linked_content": [
        {
          "url": "https://example.com/article",
          "title": "Article Title",
          "content": "extracted page text (max 5000 chars)"
        }
      ],
      "tags": ["ai", "tools"],
      "is_thread": false,
      "tweet_count": 1
    }
  ],
  "see_also_index": {
    "2026-03-05-Some-Bookmark": {"author": "@user", "tags": ["ai", "tech"]}
  }
}
```

For each manifest entry:

#### 2a — Generate English summary

Using the tweet `text` and the pre-fetched `linked_content`, generate an English summary (2-5 sentences) covering: what the tweet/thread is about, why it's interesting, and key insights.

Replace `{{SUMMARY_PLACEHOLDER}}` in the file with the summary.

#### 2b — Add linked content section

If `linked_content` is non-empty, insert a `## Linked Content` section between `## Summary` and `## Media`/`## Engagement`:

```markdown
## Linked Content

### <title from linked_content>
<English summary of the linked article/resource, based on the pre-fetched content field>
Source: <url>
```

The page content is already in the manifest — summarize it in English (3-5 sentences). No need to fetch URLs again.

#### 2c — Scan vault for wikilinks

Check vault entities for mentions in the tweet text:
- `Projects/*.md`, `Areas/People/*.md`, `Areas/Companies/*.md`

Replace recognized names with `[[Entity-Name]]` or `[[Entity-Name|alias]]` wikilinks in the `## Tweet` section.

#### 2d — Fill See Also

Using the `see_also_index` from the manifest, find related bookmarks for each new note:

1. **Same author**: other files with matching `author` field
2. **Shared tags (≥2 in common)**: prioritize 3+ shared tags
3. **Subject overlap**: use your judgment based on the tweet content

Format:
```markdown
## See Also

- [[2026-03-05-Some-Bookmark]] — same author (@username)
- [[2026-02-03-Other-Bookmark]] — AI tools
```

Keep 3-8 links max. Edit the `## See Also` section in each file.

**Parallelization**: Split the manifest into batches of ~30 and spawn one Agent per batch (run_in_background=true, mode=bypassPermissions). Each agent reads its batch, generates summaries from the pre-fetched content, and edits the files.

### Phase 3 — Report

Display a summary:

```
X Import complete.
- Bookmarks fetched: Y
- New: X (Z duplicates skipped)
- Links resolved: N
- Notes created: X
```

List the created files with their titles.

## Note Format

Each note in `Resources/X-Bookmarks/<YYYY-MM-DD>-<Slug>.md`:

```markdown
---
type: x-bookmark
tweet_id: "<id>"
author: "@username"
author_name: "Display Name"
date: YYYY-MM-DD
tags: [tag1, tag2]
likes: N
retweets: N
replies: N
source: "tweet_url"
status: draft
created: YYYY-MM-DD
---

## Tweet

<Tweet text — preserved as-is, with wikilinks injected>

> — @username, DD/MM/YYYY

## Summary

<English summary — 2-5 sentences>

## Linked Content

### <Title>
<English summary from pre-fetched content>
Source: <url>

## Media

- ![](image_url)

## Engagement

- Likes: N
- Retweets: N
- Replies: N

## See Also

- [[Related-Bookmark]] — reason

---
↑ [[X-Bookmarks]]
```

Omit empty sections. The `## See Also` section and footer `↑ [[X-Bookmarks]]` are always present.

## Rules

- The `bird` CLI reads browser cookies — no API keys needed. If auth fails, tell the user to log into x.com.
- Tweet text is preserved verbatim (original language). Only `## Summary` and `## Linked Content` are in English.
- For `--all` mode, the script reports progress periodically.
- File naming uses the tweet date, not today's date.
- The script pre-fetches linked content — the LLM should NOT re-fetch URLs. It summarizes the `content` field from the manifest.
- If a URL could not be fetched, it won't appear in `linked_content` — no need to note broken links.

### Post-Import — Log

After reporting results, append one line to `Areas/Codex/operations-log.md`:
```
| YYYY-MM-DD HH:MM | ingest | x-import | X created, Y duplicates | Resources/X-Bookmarks/ |
```
Use actual counts from the import. Create the file with header if it doesn't exist.

## Examples

Input: `/x-import`
→ Runs script for 30 latest, then LLM generates summaries from pre-fetched content

Input: `/x-import --all`
→ Full sync of all bookmarks

Input: `/x-import --count 10`
→ Fetches and processes 10 latest bookmarks
