"""
Paáré — Phase 1: Discovery Engine
-----------------------------------
Given a person's name, usernames, and email, searches the web
and returns a list of URLs to feed into Phase 2 (classifier.py).

Uses DuckDuckGo Search — no API key or billing required.

Usage:
    python discovery.py
"""

import json
import time
from ddgs import DDGS
from pathlib import Path

# ─── Core discovery function ─────────────────────────────────────────────────

def discover(
    name: str,
    usernames: list[str] = [],
    email: str = "",
    deep: bool = False
) -> list[dict]:
    """
    Search the web for mentions of a person.

    Args:
        name      : Full name e.g. "Ojurongbe Mayowa"
        usernames : List of known usernames e.g. ["oluwamay0wa"]
        email     : Email address e.g. "you@gmail.com"
        deep      : If True, search each platform individually

    Returns:
        Deduplicated list of URL dicts ready for Phase 2 classifier
    """

    all_results = []
    seen_urls = set()

    def add_results(results, label):
        count = 0
        for r in results:
            url = r.get("href", "") or r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append({
                    "url": url,
                    "page_title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                })
                count += 1
        print(f"         → {count} results")

    def ddg_search(query: str, max_results: int = 10) -> list[dict]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            time.sleep(0.8)  # be polite to DDG
            return results
        except Exception as e:
            print(f"   ⚠️  Search failed: {e}")
            return []

    print(f"\n🔍 Searching for: {name}")
    if usernames:
        print(f"   Usernames : {', '.join(usernames)}")
    if email:
        print(f"   Email     : {email}")
    print()

    # ── 1. General name search ────────────────────────────────────────────────
    print("   [1/5] General name search...")
    add_results(ddg_search(f'"{name}"'), "general")

    # ── 2. Social platforms ───────────────────────────────────────────────────
    if deep:
        platforms = [
            "site:instagram.com",
            "site:twitter.com OR site:x.com",
            "site:facebook.com",
            "site:reddit.com",
            "site:youtube.com",
            "site:tiktok.com",
        ]
        print("   [2/5] Platform-specific searches (deep mode)...")
        for p in platforms:
            results = ddg_search(f'"{name}" {p}', max_results=5)
            add_results(results, p)
    else:
        print("   [2/5] Social platform search...")
        add_results(
            ddg_search(f'"{name}" instagram OR twitter OR facebook OR reddit OR youtube', max_results=10),
            "social"
        )

    # ── 3. Username searches ──────────────────────────────────────────────────
    if usernames:
        print("   [3/5] Username searches...")
        for username in usernames:
            print(f"         Searching @{username}...", end=" ")
            add_results(ddg_search(f'"{username}"', max_results=10), f"username:{username}")
    else:
        print("   [3/5] Username search skipped")

    # ── 4. Email search ───────────────────────────────────────────────────────
    if email:
        print("   [4/5] Email search...")
        add_results(ddg_search(f'"{email}"', max_results=5), "email")
    else:
        print("   [4/5] Email search skipped")

    # ── 5. Data broker search ─────────────────────────────────────────────────
    print("   [5/5] Data broker search...")
    add_results(
        ddg_search(f'"{name}" site:spokeo.com OR site:beenverified.com OR site:whitepages.com', max_results=5),
        "data_brokers"
    )

    return all_results


# ─── Save & print ─────────────────────────────────────────────────────────────

def save_discovered(results: list[dict], filepath: str = "discovered_urls.json"):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Saved {len(results)} URLs to {filepath}")


def print_discovered(results: list[dict]):
    print(f"\n{'═' * 60}")
    print(f"  PAÁRÉ — Discovery Results")
    print(f"{'═' * 60}")
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r.get('url')}")
        if r.get("page_title"):
            print(f"     Title  : {r.get('page_title')[:80]}")
        if r.get("snippet"):
            print(f"     Snippet: {r.get('snippet')[:120]}...")
    print(f"\n{'─' * 60}")
    print(f"  Total discovered: {len(results)} URLs")
    print(f"{'═' * 60}\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    TARGET = {
        "name": "Ojurongbe Mayowa",
        "usernames": ["oluwamay0wa"],
        "email": "ojurongbemayowa@gmail.com",
        "deep": False,
    }

    print("\n🩸 Paáré — Phase 1 Discovery Engine")

    results = discover(
        name=TARGET["name"],
        usernames=TARGET["usernames"],
        email=TARGET["email"],
        deep=TARGET["deep"],
    )

    print_discovered(results)
    save_discovered(results, "discovered_urls.json")
    print("✅ Discovery complete. Run pipeline.py for the full pipeline.\n")