#!/usr/bin/env python3
"""
X Bookmarks Import — mechanical pipeline.

Fetches X/Twitter bookmarks via bird CLI, deduplicates, groups threads,
resolves t.co URLs, fetches linked page content, generates Obsidian notes
with frontmatter/Tweet/footer. Outputs a manifest of bookmarks needing
LLM summarization.

Usage:
    python3 x_bookmarks.py                    # last 30 bookmarks
    python3 x_bookmarks.py --all              # full sync
    python3 x_bookmarks.py --count 50         # last 50 bookmarks
"""

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

VAULT_ROOT = Path(__file__).resolve().parents[3]  # up from .claude/skills/x-import/
BOOKMARKS_DIR = VAULT_ROOT / "Resources" / "X-Bookmarks"
MANIFEST_FILE = Path("/tmp/x_bookmarks_manifest.json")
TODAY = date.today().isoformat()
MAX_WORKERS = 5  # parallel URL fetches

# Tag mapping rules (same conventions as GitHub stars)
TOPIC_KEYWORDS = {
    "ai": ["ai", "gpt", "llm", "claude", "openai", "anthropic", "machine learning",
            "deep learning", "neural", "transformer", "diffusion", "model", "agent"],
    "tech": ["programming", "software", "engineering", "developer", "code", "coding",
             "framework", "library", "api", "sdk"],
    "startup": ["startup", "founder", "vc", "venture", "fundrais", "saas", "yc",
                "y combinator", "series a", "seed round"],
    "business": ["business", "revenue", "profit", "market", "growth", "strategy",
                 "enterprise", "b2b", "b2c"],
    "finance": ["finance", "invest", "stock", "crypto", "bitcoin", "ethereum",
                "trading", "defi", "web3"],
    "design": ["design", "ui", "ux", "figma", "css", "tailwind", "frontend"],
    "devops": ["devops", "docker", "kubernetes", "k8s", "ci/cd", "infrastructure",
               "terraform", "deploy"],
    "security": ["security", "hack", "vulnerability", "exploit", "pentest", "cve",
                 "zero-day", "malware"],
    "open-source": ["open source", "open-source", "oss", "foss", "github", "gitlab"],
    "tools": ["tool", "productivity", "workflow", "automation", "cli", "terminal"],
    "career": ["career", "hiring", "interview", "salary", "job", "resume"],
    "go": ["golang", " go ", "#go "],
    "python": ["python", "django", "flask", "fastapi"],
    "rust": ["rust", "rustlang"],
    "typescript": ["typescript", "nextjs", "next.js", "react", "svelte", "vue"],
}


# ---------------------------------------------------------------------------
# Simple HTML text extractor
# ---------------------------------------------------------------------------

class _TextExtractor(HTMLParser):
    """Extract visible text from HTML, skipping scripts/styles."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "head"}

    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
        if tag == "title" and not self.title:
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self._parts.append(text)

    def get_text(self) -> str:
        return "\n".join(self._parts)


def extract_text_from_html(html: str) -> tuple[str, str]:
    """Extract (title, body_text) from HTML."""
    parser = _TextExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass
    return parser.title.strip(), parser.get_text()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_twitter_date(date_str: str) -> str:
    """Parse Twitter date format to YYYY-MM-DD."""
    try:
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return TODAY


def normalize_emoji(text: str) -> str:
    """Normalize emoji sequences so Quartz's Twemoji-based OG image map can resolve them.

    - Strips U+FE0E (text-presentation selector). Quartz can't resolve `<cp>-fe0e`.
    - Rewrites bare ZWJ sequences whose canonical form requires U+FE0F, e.g.
      `👁‍🗨` -> `👁️‍🗨️` (eye in speech bubble).
    """
    if not text:
        return text
    text = text.replace("︎", "")
    text = text.replace(
        "\U0001F441‍\U0001F5E8",
        "\U0001F441️‍\U0001F5E8️",
    )
    return text


def slugify(text: str) -> str:
    """Generate a PascalCase-With-Hyphens slug from text."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    words = text.split()[:8]
    slug = "-".join(w.capitalize() for w in words if w)
    return slug or "Untitled"


def generate_tags_from_text(text: str) -> list[str]:
    """Auto-generate tags by scanning text for keyword patterns."""
    text_lower = text.lower()
    tags: set[str] = set()
    for tag, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                tags.add(tag)
                break
    return sorted(tags)[:8]


def extract_urls(text: str) -> list[str]:
    """Extract URLs from tweet text."""
    return re.findall(r"https?://\S+", text)


def escape_yaml_string(s: str) -> str:
    """Escape a string for YAML double-quoted value."""
    if not s:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def yaml_list(items: list[str]) -> str:
    """Format a list for YAML frontmatter inline."""
    if not items:
        return "[]"
    return "[" + ", ".join(items) + "]"


# ---------------------------------------------------------------------------
# URL resolution and content fetching
# ---------------------------------------------------------------------------

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

# Domains to skip (media, tweets, tracking)
_SKIP_DOMAINS = {
    "x.com", "twitter.com", "t.co",
    "pic.twitter.com", "pbs.twimg.com", "video.twimg.com",
    "youtube.com", "youtu.be",  # video — no useful text extraction
}


def resolve_and_fetch(url: str) -> dict | None:
    """Resolve a t.co URL, fetch the page, extract text. Returns dict or None."""
    try:
        req = Request(url, headers=_HEADERS, method="GET")
        with urlopen(req, timeout=10) as resp:
            final_url = resp.url
            # Check if resolved domain should be skipped
            from urllib.parse import urlparse
            domain = urlparse(final_url).netloc.replace("www.", "")
            if domain in _SKIP_DOMAINS:
                return None

            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None

            html = resp.read(200_000).decode("utf-8", errors="replace")
            title, body = extract_text_from_html(html)
            if not body or len(body) < 100:
                return None

            return {
                "url": final_url,
                "title": title[:200] if title else "",
                "content": body[:5000],  # truncate like gh_stars READMEs
            }
    except Exception:
        return None


def fetch_linked_content(urls: list[str]) -> list[dict]:
    """Resolve and fetch content for a list of URLs in parallel."""
    if not urls:
        return []

    # Only process t.co links (the ones in tweets)
    tco_urls = [u for u in urls if "t.co/" in u][:3]
    if not tco_urls:
        return []

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(resolve_and_fetch, url): url for url in tco_urls}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    return results


# ---------------------------------------------------------------------------
# Fetch bookmarks
# ---------------------------------------------------------------------------

def _run_bird(extra_args: list[str], timeout: int = 300) -> tuple[list[dict], str | None]:
    """Run bird CLI and return (tweets, next_cursor)."""
    cmd = ["npx", "-y", "@steipete/bird", "bookmarks",
           "--include-parent", "--thread-meta", "--json"] + extra_args
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        print(f"ERROR: bird CLI failed: {r.stderr}", file=sys.stderr)
        sys.exit(1)
    stdout = r.stdout.strip()
    if not stdout:
        return [], None
    data = json.loads(stdout)
    # --all returns {tweets, nextCursor}; --count returns a list
    if isinstance(data, dict):
        return data.get("tweets", []), data.get("nextCursor")
    return data, None


def fetch_bookmarks(mode: str, count: int = 30) -> list[dict]:
    """Fetch bookmarks via bird CLI with automatic pagination for --all."""
    print(f"Fetching bookmarks (mode={mode}, count={count})...")

    if mode != "all":
        tweets, _ = _run_bird([f"--count={count}"], timeout=300)
        print(f"  Fetched {len(tweets)} bookmarks.")
        return tweets

    # Paginated --all: fetch in chunks of max-pages=3, then follow cursor
    all_tweets: list[dict] = []
    cursor: str | None = None
    page = 0
    seen_ids: set[str] = set()

    while True:
        page += 1
        args = ["--all", "--max-pages=3"]
        if cursor:
            args.append(f"--cursor={cursor}")
        print(f"  Fetching page batch {page} (cursor={'yes' if cursor else 'start'})...")

        try:
            tweets, next_cursor = _run_bird(args, timeout=300)
        except subprocess.TimeoutExpired:
            print(f"  WARNING: timeout on batch {page}, stopping pagination.")
            break
        except json.JSONDecodeError as e:
            print(f"  WARNING: JSON error on batch {page}: {e}, stopping.")
            break

        if not tweets:
            print(f"  No more tweets returned, pagination complete.")
            break

        new_count = 0
        for t in tweets:
            tid = t.get("id", "")
            if tid and tid not in seen_ids:
                seen_ids.add(tid)
                all_tweets.append(t)
                new_count += 1

        print(f"    Got {len(tweets)} tweets ({new_count} new, {len(all_tweets)} total).")

        if not next_cursor:
            print(f"  No next cursor, pagination complete.")
            break

        cursor = next_cursor

    print(f"  Fetched {len(all_tweets)} bookmarks total across {page} batch(es).")
    return all_tweets


# ---------------------------------------------------------------------------
# Deduplicate
# ---------------------------------------------------------------------------

def deduplicate(bookmarks: list[dict]) -> list[dict]:
    """Remove bookmarks that already exist in the vault."""
    print("Deduplicating...")

    existing_ids: set[str] = set()
    for f in BOOKMARKS_DIR.glob("*.md"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                in_frontmatter = False
                for line in fh:
                    stripped = line.strip()
                    if stripped == "---":
                        if not in_frontmatter:
                            in_frontmatter = True
                            continue
                        else:
                            break
                    if in_frontmatter and stripped.startswith("tweet_id:"):
                        match = re.search(r'"([^"]+)"', stripped)
                        if match:
                            existing_ids.add(match.group(1))
                        break
        except (OSError, UnicodeDecodeError):
            continue

    new_bookmarks = []
    dupes = 0
    for bm in bookmarks:
        tweet_id = bm.get("id", "")
        if tweet_id in existing_ids:
            dupes += 1
        else:
            new_bookmarks.append(bm)
            existing_ids.add(tweet_id)  # prevent intra-batch dupes

    print(f"  {len(new_bookmarks)} nouveaux sur {len(bookmarks)} total ({dupes} doublons ignores).")
    return new_bookmarks


# ---------------------------------------------------------------------------
# Group threads
# ---------------------------------------------------------------------------

def group_threads(bookmarks: list[dict]) -> list[list[dict]]:
    """Group bookmarks by conversationId into thread groups."""
    threads: dict[str, list[dict]] = defaultdict(list)
    for bm in bookmarks:
        conv_id = bm.get("conversationId", bm.get("id", ""))
        threads[conv_id].append(bm)

    groups = []
    for conv_id, tweets in threads.items():
        tweets.sort(key=lambda t: t.get("createdAt", ""))
        groups.append(tweets)

    # Sort groups oldest first
    groups.sort(key=lambda g: g[0].get("createdAt", ""))

    thread_count = sum(1 for g in groups if len(g) > 1)
    if thread_count:
        print(f"  Grouped into {len(groups)} notes ({thread_count} threads).")

    return groups


# ---------------------------------------------------------------------------
# Build note content
# ---------------------------------------------------------------------------

def build_note(tweet_group: list[dict], linked_content: list[dict]) -> tuple[str, str, dict]:
    """Build note content. Returns (filename, content, manifest_entry)."""
    primary = tweet_group[0]
    tweet_id = primary.get("id", "")
    author = primary.get("author", {})
    username = author.get("username", "unknown")
    author_name = normalize_emoji(author.get("name", username))
    tweet_date = parse_twitter_date(primary.get("createdAt", ""))
    text = normalize_emoji(primary.get("text", ""))

    # Combine text from all tweets in thread
    all_text = "\n".join(t.get("text", "") for t in tweet_group)
    # Also include linked content for better tag generation
    all_text_for_tags = all_text + "\n" + "\n".join(
        lc.get("content", "")[:500] for lc in linked_content
    )

    # Engagement (sum for threads)
    likes = sum(t.get("likeCount", 0) for t in tweet_group)
    retweets = sum(t.get("retweetCount", 0) for t in tweet_group)
    replies = sum(t.get("replyCount", 0) for t in tweet_group)

    # Tags — use tweet text + linked content for richer tagging
    tags = generate_tags_from_text(all_text_for_tags)

    # Generate slug
    slug_text = re.sub(r"https?://\S+", "", text)
    slug_text = re.sub(r"@\w+", "", slug_text).strip()[:80]
    slug = slugify(slug_text)
    filename = f"{tweet_date}-{slug}.md"

    # Build tweet section
    tweet_section_parts = []
    for i, t in enumerate(tweet_group):
        t_text = normalize_emoji(t.get("text", ""))
        t_author = t.get("author", {}).get("username", username)
        t_date = parse_twitter_date(t.get("createdAt", ""))
        t_date_formatted = datetime.strptime(t_date, "%Y-%m-%d").strftime("%d/%m/%Y")

        if len(tweet_group) > 1 and i > 0:
            tweet_section_parts.append("")

        tweet_section_parts.append(t_text)
        tweet_section_parts.append("")
        tweet_section_parts.append(f"> — @{t_author}, {t_date_formatted}")

    tweet_section = "\n".join(tweet_section_parts)

    # Media
    media_items = []
    for t in tweet_group:
        for m in (t.get("media") or []):
            url = m.get("url", "")
            if url:
                media_items.append(url)

    source_url = f"https://x.com/{username}/status/{tweet_id}"

    # -- Build file content --
    lines = ["---"]
    lines.append('type: x-bookmark')
    lines.append(f'tweet_id: "{tweet_id}"')
    lines.append(f'author: "@{escape_yaml_string(username)}"')
    lines.append(f'author_name: "{escape_yaml_string(author_name)}"')
    lines.append(f'date: {tweet_date}')
    lines.append(f'tags: {yaml_list(tags)}')
    lines.append(f'likes: {likes}')
    lines.append(f'retweets: {retweets}')
    lines.append(f'replies: {replies}')
    lines.append(f'source: "{source_url}"')
    lines.append(f'status: draft')
    lines.append(f'created: {TODAY}')
    lines.append("---")
    lines.append("")
    lines.append("## Tweet")
    lines.append("")
    lines.append(tweet_section)
    lines.append("")
    lines.append("## Resume")
    lines.append("")
    lines.append("{{RESUME_PLACEHOLDER}}")
    lines.append("")

    if media_items:
        lines.append("## Media")
        lines.append("")
        for url in media_items:
            lines.append(f"- ![]({url})")
        lines.append("")

    lines.append("## Engagement")
    lines.append("")
    lines.append(f"- Likes : {likes}")
    lines.append(f"- Retweets : {retweets}")
    lines.append(f"- Replies : {replies}")
    lines.append("")
    lines.append("## Voir aussi")
    lines.append("")
    lines.append("")
    lines.append("---")
    lines.append("↑ [[X-Bookmarks]]")
    lines.append("")

    content = "\n".join(lines)

    # Manifest entry — includes pre-fetched linked content for LLM
    manifest_entry = {
        "file": filename,
        "tweet_id": tweet_id,
        "author": f"@{username}",
        "author_name": author_name,
        "date": tweet_date,
        "text": all_text[:3000],
        "linked_content": linked_content,  # pre-fetched page content
        "tags": tags,
        "is_thread": len(tweet_group) > 1,
        "tweet_count": len(tweet_group),
    }

    return filename, content, manifest_entry


# ---------------------------------------------------------------------------
# Process bookmarks
# ---------------------------------------------------------------------------

def process_bookmarks(groups: list[list[dict]]) -> list[dict]:
    """Process all bookmark groups: fetch links, write notes, return manifest."""
    total = len(groups)
    manifest = []
    links_fetched = 0

    for i, group in enumerate(groups, 1):
        # Extract URLs from all tweets in group
        all_text = "\n".join(t.get("text", "") for t in group)
        urls = extract_urls(all_text)

        # Resolve t.co links and fetch page content (mechanical work)
        linked_content = fetch_linked_content(urls)
        links_fetched += len(linked_content)

        filename, content, manifest_entry = build_note(group, linked_content)
        filepath = BOOKMARKS_DIR / filename

        if filepath.exists():
            continue

        filepath.write_text(content, encoding="utf-8")
        manifest.append(manifest_entry)

        if i % 10 == 0 or i == total:
            print(f"  Progress: {i}/{total} notes written ({links_fetched} links fetched).")

    return manifest


# ---------------------------------------------------------------------------
# Build Voir aussi index
# ---------------------------------------------------------------------------

def build_voir_aussi_index() -> dict[str, dict]:
    """Build {filename: {author, tags}} index from all existing files."""
    print("Building Voir aussi index...")
    index: dict[str, dict] = {}

    for f in BOOKMARKS_DIR.glob("*.md"):
        try:
            author = ""
            tags: list[str] = []
            with open(f, "r", encoding="utf-8") as fh:
                in_fm = False
                for line in fh:
                    s = line.strip()
                    if s == "---":
                        if not in_fm:
                            in_fm = True
                            continue
                        else:
                            break
                    if in_fm:
                        if s.startswith("author:"):
                            author = s.split(":", 1)[1].strip().strip('"')
                        elif s.startswith("tags:"):
                            tag_match = re.search(r"\[([^\]]*)\]", s)
                            if tag_match:
                                tags = [t.strip() for t in tag_match.group(1).split(",") if t.strip()]
            if author:
                index[f.stem] = {"author": author, "tags": tags}
        except (OSError, UnicodeDecodeError):
            continue

    print(f"  Index built: {len(index)} files.")
    return index


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="X Bookmarks Import")
    parser.add_argument("--all", action="store_true", help="Fetch all bookmarks")
    parser.add_argument("--count", type=int, default=30, help="Number of bookmarks to fetch")
    args = parser.parse_args()

    BOOKMARKS_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1 — Fetch
    mode = "all" if args.all else "incremental"
    bookmarks = fetch_bookmarks(mode, args.count)
    if not bookmarks:
        print("No bookmarks found.")
        return

    # Step 2 — Dedup
    new_bookmarks = deduplicate(bookmarks)
    if not new_bookmarks:
        print("Aucun nouveau bookmark. Rien a faire.")
        return

    # Step 3 — Group threads
    groups = group_threads(new_bookmarks)

    # Step 4 — Process: resolve URLs, fetch content, write notes
    print(f"\nProcessing {len(groups)} bookmark notes...")
    manifest = process_bookmarks(groups)
    print(f"  Done: {len(manifest)} notes created.")

    # Step 5 — Build Voir aussi index (for LLM to use)
    va_index = build_voir_aussi_index()

    # Write manifest with index
    output = {
        "manifest": manifest,
        "voir_aussi_index": va_index,
    }
    MANIFEST_FILE.write_text(json.dumps(output, ensure_ascii=False), encoding="utf-8")

    # Report
    links_total = sum(len(m["linked_content"]) for m in manifest)
    threads_count = sum(1 for m in manifest if m["is_thread"])
    print(f"""
========================================
Import X Bookmarks terminé (Phase 1).
- Bookmarks récupérés : {len(bookmarks)}
- Nouveaux : {len(new_bookmarks)}
- Notes créées : {len(manifest)}
- Threads : {threads_count}
- Liens résolus et fetchés : {links_total}
- Manifest LLM : {MANIFEST_FILE} ({len(manifest)} résumés à générer)
========================================
""")


if __name__ == "__main__":
    main()
