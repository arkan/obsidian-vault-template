---
name: resume
description: >
  Synthesize long documents (PDF, Markdown, URL) into concise summaries in English.
  Uses hierarchical table-of-contents chunking with parallel sub-agents to process
  hundreds of pages without context loss. Use when user wants to summarize a long
  document, says "summarize this report", "give me a synthesis of this document",
  "what does this PDF say", or mentions /resume. Triggers on any request to summarize,
  synthesize, or extract key points from reports, white papers, or long-form content.
argument_hint: "<file|url> [--words N] [--detailed|--concise] [--lang fr]"
---

# resume — Long Document Synthesis

Hierarchical synthesis with parallel sub-agents. Strategy B (table of contents) with fallback A (fixed-size chunks).

## Parameters

| Parameter | Effect |
|-----------|--------|
| `<source>` | PDF/Markdown path or URL |
| `--words N` | Target length in words (default: ~500) |
| `--detailed` | Long summary (~1000 words) |
| `--concise` | Short summary (~250 words) |
| `--lang fr` | Output language (default: en) |

## Workflow

### 1. Get the text

- **HTML URL** → `webfetch` with `extract_main: true`
- **PDF URL** → `curl -L <url> -o /tmp/resume-input.pdf`
- **Local PDF** → `python3 .claude/skills/resume/scripts/extract_pdf.py <pdf> > /tmp/resume-extracted.json`
- **Markdown** → direct read with Read tool

The script outputs a JSON: `{text, toc: [{title, page, level}], pages}`.

### 2. Detect structure and chunk

**If table of contents available (Strategy B)** :
- Group ToC entries into chunks of ~12K tokens max
- Each chunk = one or more contiguous sections
- Keep titles as chunk headers

**If no ToC (Strategy A, automatic fallback)** :
- Split text into blocks of ~12K tokens
- 200 token overlap between blocks

**If < 2 pages** → direct summary, no chunking.

### 3. Summarize chunks in parallel

Launch one sub-agent per chunk with this prompt:

```
Summarize the following text in {language}. Capture:
- Main facts and findings
- Key numbers and data points
- Conclusions and recommendations
- Essential context

Length: {1-2% of chunk size, max 800 words}.
```

Collect all summaries. Use the cheapest model capable of proper summarization for chunks.

### 4. Final synthesis

With all chunk summaries assembled, produce the final synthesis:

- **Language**: English by default, or as requested via `--lang`
- **Length**: per `--words`, `--detailed`, or `--concise`
- **Format**: freeform, structured naturally based on content
- Prioritize: conclusions, implications, controversies if present

Use the primary model for this step.

### 5. Write output

Create the file in `Resources/` with this frontmatter:

```yaml
type: summary
source: "<url or path>"
source_type: <pdf|markdown|url>
lang: <en|fr>
tags: [summary]
created: <YYYY-MM-DD>
```

Display the summary in chat, then confirm the path: `Summary saved: Resources/<slug>.md`.

## Error handling

| Case | Action |
|------|--------|
| PDF with no text (scan) | Message: "This PDF is a scan without OCR. Use an OCR tool first." |
| URL unreachable | Display HTTP code, stop |
| Document without ToC | Silent fallback to Strategy A |
| Document < 2 pages | Direct summary, no chunking |
| pymupdf missing | Message: `pip install pymupdf` |
| Chunk > 12K tokens | Recursive re-chunking of that chunk |

## Notes

- Extracted text → `/tmp/`, cleaned up after use
- Always include the exact source in the frontmatter
- File slug = document title in kebab-case
- For URLs, `webfetch` with `prefer_llms_txt: auto` by default
- Requires `pymupdf` for PDF extraction and `summarize` CLI for content extraction
