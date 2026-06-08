"""
Milestone 3: Document ingestion and chunking.

Fetches raw text from all 10 sources (Reddit threads + review pages),
cleans it, chunks it at 300 characters with 50-character overlap, and
saves the results so later stages can embed and index them.

Run:
    pip install requests beautifulsoup4
    python ingest.py
"""

import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DOCUMENTS_DIR = Path("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)

CHUNK_SIZE = 300
OVERLAP = 50

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

SOURCES = [
    {"name": "reddit_1_cs_courses_order",     "type": "reddit",  "url": "https://www.reddit.com/r/learnprogramming/comments/fls11e"},
    {"name": "reddit_2_cs_foundation",        "type": "reddit",  "url": "https://www.reddit.com/r/learnprogramming/comments/1n23o6a"},
    {"name": "reddit_3_data_structures",      "type": "reddit",  "url": "https://www.reddit.com/r/learnprogramming/comments/dx206v"},
    {"name": "reddit_4_intro_cs_design",      "type": "reddit",  "url": "https://www.reddit.com/r/compsci/comments/hh8ijq"},
    {"name": "reviews_cop3502c",              "type": "reviews", "url": "https://www.ratemycourses.io/ucf/course/cop3502c"},
    {"name": "reviews_cop3503c",              "type": "reviews", "url": "https://www.ratemycourses.io/ucf/course/cop3503c"},
    {"name": "reviews_csc241",                "type": "reviews", "url": "https://www.ratemycourses.io/depaul/course/csc241"},
    {"name": "reviews_prof_kapp_nyu",         "type": "reviews", "url": "https://www.ratemyprofessors.com/professor/1579749"},
    {"name": "reviews_prof_decker_delaware",  "type": "reviews", "url": "https://www.ratemyprofessors.com/professor/540363"},
    {"name": "reviews_prof_mazidi_utdallas",  "type": "reviews", "url": "https://www.ratemyprofessors.com/professor/2190788"},
]


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def fetch_reddit_thread(url: str, name: str) -> str:
    """
    Fetches post title, body, and all top-level comments from a Reddit thread.

    Strategy:
    1. Check for a manually saved local file at documents/<name>_raw.txt —
       use it if present (bypasses all network issues).
    2. Try old.reddit.com JSON (less aggressively blocked than www.reddit.com).
    3. Fall back to www.reddit.com JSON.

    If all three fail, raises the last exception so the caller can log it.
    """
    # 1. Local file fallback — paste thread text here to bypass scraping
    local_path = DOCUMENTS_DIR / f"{name}_raw.txt"
    if local_path.exists():
        print(f"  using saved local file: {local_path}")
        return local_path.read_text(encoding="utf-8")

    thread_path = url.split("reddit.com")[-1].rstrip("/")
    last_exc: Exception | None = None

    for base in ("https://old.reddit.com", "https://www.reddit.com"):
        json_url = f"{base}{thread_path}.json?limit=100"
        try:
            response = requests.get(json_url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()

            parts = []
            post = data[0]["data"]["children"][0]["data"]
            parts.append(post.get("title", ""))
            parts.append(post.get("selftext", ""))

            for child in data[1]["data"]["children"]:
                body = child["data"].get("body", "")
                if body and body not in ("[deleted]", "[removed]"):
                    parts.append(body)

            return "\n\n".join(parts)
        except Exception as exc:
            last_exc = exc
            time.sleep(2)

    raise last_exc


def fetch_review_page(url: str) -> str:
    """
    Fetches a RateMyProfessors or RateMyCourses page and extracts
    visible text content, stripping all HTML.
    """
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove navigation, scripts, styles, footers, and other boilerplate
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "noscript", "form", "button", "iframe"]):
        tag.decompose()

    return soup.get_text(separator="\n")


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

# Exact phrases that appear on every review page but carry no content
_BOILERPLATE_PHRASES = {
    "rate my courses",
    "rate my professors",
    "essaypal",
    "this ai writes in your style",
    "read more",
    "share",
    "helpful",
    "not helpful",
    "report",
    "cookie",
    "privacy policy",
    "terms of service",
    "sign in",
    "log in",
    "create account",
    "comments on the course",
    "overall quality based on",
}


def clean_text(text: str) -> str:
    """
    Removes HTML entities, ad/nav boilerplate, and excess whitespace.
    Keeps only lines that carry actual review or discussion content.
    """
    # Decode common HTML entities
    text = text.replace("&amp;", "&").replace("&nbsp;", " ")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) < 25:
            continue
        low = line.lower()
        if any(phrase in low for phrase in _BOILERPLATE_PHRASES):
            continue
        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """
    Splits text into chunks of `chunk_size` characters with `overlap`
    characters of overlap between consecutive chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        current_chunk = text[start:end].strip() 
        print(f"  chunk [{start}:{end}] → {len(current_chunk)} chars")
        if current_chunk:
            chunks.append(current_chunk)
        start += chunk_size - overlap
    # Drop the last chunk if it's just trailing whitespace or too short to be useful
    return [c for c in chunks if len(c) >= 30]


# ---------------------------------------------------------------------------
# Save helpers
# ---------------------------------------------------------------------------

def save_raw(name: str, text: str) -> None:
    path = DOCUMENTS_DIR / f"{name}_raw.txt"
    path.write_text(text, encoding="utf-8")
    print(f"  saved raw  → {path}  ({len(text):,} chars)")


def save_chunks(name: str, chunks: list[str]) -> None:
    path = DOCUMENTS_DIR / f"{name}_chunks.json"
    path.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved chunks → {path}  ({len(chunks)} chunks)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    all_chunks: list[dict] = []

    for source in SOURCES:
        print(f"\nProcessing: {source['name']}")
        try:
            if source["type"] == "reddit":
                raw = fetch_reddit_thread(source["url"], source["name"])
            else:
                raw = fetch_review_page(source["url"])
        except Exception as exc:
            print(f"  ERROR fetching {source['url']}: {exc}")
            continue

        local_exists = (DOCUMENTS_DIR / f"{source['name']}_raw.txt").exists()
        if not local_exists:
            save_raw(source["name"], raw)

        cleaned = clean_text(raw)
        chunks = chunk_text(cleaned)
        save_chunks(source["name"], chunks)

        for chunk in chunks:
            all_chunks.append({"source": source["name"], "text": chunk})

        # Be polite to servers
        time.sleep(1)

    # Save a single combined chunks file for the embedding stage
    combined_path = DOCUMENTS_DIR / "all_chunks.json"
    combined_path.write_text(
        json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nTotal chunks across all sources: {len(all_chunks)}")
    print(f"Combined file saved to: {combined_path}")

    # Print 5 representative chunks for inspection
    print("\n--- 5 representative chunks ---")
    step = max(1, len(all_chunks) // 5)
    for i in range(0, min(5 * step, len(all_chunks)), step):
        c = all_chunks[i]
        print(f"\n[{i}] source={c['source']}")
        print(c["text"])


if __name__ == "__main__":
    main()
