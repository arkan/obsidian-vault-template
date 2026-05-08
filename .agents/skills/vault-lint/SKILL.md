# Vault Lint

Audit the vault for structural issues, stale content, and inconsistencies. Inspired by Karpathy's LLM wiki "lint" operation — the vault reviews and improves itself.

## Trigger

`/vault-lint` — full run (all 7 checks)
`/vault-lint --quick` — quick checks only (2: wikilinks + 7: frontmatter)
`/vault-lint --fix` — auto-apply safe fixes without asking

## Checks

### Check 1 — Stale drafts

Find notes with `status: draft` created more than 7 days ago.

1. Grep `status: draft` across all `.md` files in the vault (exclude `.obsidian/`, `.Codex/`, `node_modules/`)
2. For each match, extract `created:` date from frontmatter
3. If `created` is > 7 days ago, flag it
4. **Action**: list files with age. If `--fix`, change `status: draft` to `status: active` for notes older than 30 days.

### Check 2 — Broken wikilinks

Find `[[Target]]` links where no matching file exists.

1. Grep `\[\[([^\]|]+)` across all `.md` files to extract wikilink targets
2. For each unique target, check if a file named `<target>.md` exists anywhere in the vault (case-insensitive glob)
3. **Ignore**: targets containing `#` (section anchors), targets matching `.base` files, targets inside dataview code blocks, targets that are tag-like (e.g. `[[tag1]]` in footer lines)
4. **Action**: list broken links with source file and line number. No auto-fix.

### Check 3 — Dormant entities

Find entity files (project/person/company) without recent activity.

1. Read frontmatter of all files in `Projects/*.md`, `Areas/People/*.md`, `Areas/Companies/*.md`
2. Check `last_synthesis` field — flag if > 30 days ago or missing
3. Check `status` — only flag `active` entities (ignore `archived`, `inactive`, `done`)
4. **Action**: list dormant entities with last synthesis date. If `--fix`, update `last_synthesis` to today.

### Check 4 — Inconsistent tags

Detect tag variants that should be normalized.

1. Grep `tags:` arrays from all frontmatters
2. Build frequency index: tag → count
3. Detect known variants:
   - `ai` / `ia` → normalize to `ai`
   - `open-source` / `opensource` → normalize to `open-source`
   - `cli` / `command-line` → normalize to `cli`
   - `frontend` / `front-end` → normalize to `frontend`
   - `backend` / `back-end` → normalize to `backend`
   - `devops` / `dev-ops` → normalize to `devops`
4. Also flag tags used only once (possible typos)
5. **Action**: list variants with counts. If `--fix`, normalize to the canonical form.

### Check 5 — Duplicate sources

Find multiple notes pointing to the same URL.

1. Grep `source:` from all frontmatters
2. Group by URL (strip quotes and trailing whitespace)
3. Flag groups with 2+ files
4. **Action**: list duplicates with file paths. No auto-fix.

### Check 6 — Empty "Voir aussi"

Find import notes (x-bookmark, github-star) with empty cross-links.

1. For `type: x-bookmark` and `type: github-star` notes, check if `## Voir aussi` section exists and has content
2. "Empty" means: section missing, or section exists but has no list items (no `- [[` lines after it)
3. **Action**: report count and percentage. No auto-fix (cross-linking requires context).

### Check 7 — Incomplete frontmatter

Verify required fields by note type.

1. Required fields per type:
   - `x-bookmark`: tweet_id, author, date, tags, source
   - `github-star`: repo_fullname, owner, language, stars, source
   - `importedURL`: title, source, source_type, tags
   - `project`: status
   - `person`: status
   - `company`: status
   - `daily`: date
   - `meeting`: date
2. For each note, check that all required fields for its type are present and non-empty
3. **Action**: list files with missing fields. If `--fix`, add missing fields with placeholder values.

## Output

Generate report at `Areas/Codex/vault-lint-YYYY-MM-DD.md`:

```markdown
---
type: Codex
date: YYYY-MM-DD
---
# Vault Lint — YYYY-MM-DD

## Résumé

| Check | Issues | Status |
|-------|--------|--------|
| Drafts stagnants | X | ⚠️/✅ |
| Wikilinks cassés | Y | ⚠️/✅ |
| Entités dormantes | Z | ⚠️/✅ |
| Tags inconsistants | N | ⚠️/✅ |
| Doublons source | N | ⚠️/✅ |
| Voir aussi vides | N | ⚠️/✅ |
| Frontmatter incomplet | N | ⚠️/✅ |

**Score global** : X/7 checks OK

## Détails

### Drafts stagnants (X)
- `path/to/file.md` — créé le YYYY-MM-DD (N jours)
...

### Wikilinks cassés (Y)
- `source.md:42` → [[Cible inexistante]]
...

### Entités dormantes (Z)
- [[Entity Name]] — dernière synthèse : YYYY-MM-DD (N jours)
...

### Tags inconsistants (N)
- `ia` (3 occurrences) → devrait être `ai` (45 occurrences)
...

### Doublons source (N)
- URL : `https://...`
  - `file1.md`
  - `file2.md`
...

### Voir aussi vides (N)
- X/Y notes x-bookmark sans liens (Z%)
- X/Y notes github-star sans liens (Z%)

### Frontmatter incomplet (N)
- `file.md` — manque : field1, field2
...
```

Use ✅ when 0 issues found, ⚠️ when issues exist.

## Post-Lint — Log

After generating the report, append one line to `Areas/Codex/operations-log.md`:
```
| YYYY-MM-DD HH:MM | lint | vault-lint | X issues | Areas/Codex/vault-lint-YYYY-MM-DD.md |
```
Create the log file with header if it doesn't exist.

## Rules

- Never modify `.obsidian/` directory
- The `--quick` flag runs only Check 2 (wikilinks) and Check 7 (frontmatter)
- The `--fix` flag only applies SAFE fixes: tag normalization, status upgrades, placeholder fields. It does NOT delete files, remove content, or modify wikilinks.
- Always generate the report file, even if 0 issues found
- Present the summary table to the user after generating the report
- For large vaults (>1000 files), use grep efficiently — don't read files individually when grep can extract frontmatter in bulk
