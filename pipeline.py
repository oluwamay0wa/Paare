"""
Paáré — Full Pipeline
----------------------
Chains Phase 1 → Phase 2 → Phase 3 in one run.

Usage:
    python pipeline.py
"""

from discovery import discover, print_discovered, save_discovered
from classifier import classify_urls, print_results, save_results
from phase3_generator import generate_request, save_request

# ─── Edit target details here ─────────────────────────────────────────────────
TARGET = {
    "name": "John Adebayo",
    "usernames": ["jadebayo"],
    "email": "johnadebayo@gmail.com",
    "deep": False,
}

# ─── Run pipeline ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🩸 Paáré — Full Pipeline")
    print("=" * 60)

    # ── Phase 1: Discovery ────────────────────────────────────────
    print("\n📡 PHASE 1 — Discovery")
    urls = discover(
        name=TARGET["name"],
        usernames=TARGET["usernames"],
        email=TARGET["email"],
        deep=TARGET["deep"],
    )
    print_discovered(urls)
    save_discovered(urls, "discovered_urls.json")

    if not urls:
        print("❌ No URLs found. Check your API keys or try a different name.")
        exit()

    # ── Phase 2: Classification ───────────────────────────────────
    print("\n🧠 PHASE 2 — AI Classification")
    results = classify_urls(urls)
    print_results(results)
    save_results(results, "scan_results.json")

    # ── Phase 3: Removal Requests ─────────────────────────────────
    print("\n📨 PHASE 3 — Removal Request Generation")
    for i, item in enumerate(results, 1):
        platform = item.get("platform", "Unknown")
        action = item.get("suggested_action", "unknown")
        print(f"   [{i}/{len(results)}] {platform} — {action}...", end=" ", flush=True)
        result = generate_request(item)
        filepath = save_request(result, i)
        print(f"✅")

    print(f"\n{'=' * 60}")
    print(f"  🎉 Pipeline complete!")
    print(f"  📁 Removal requests saved to: ./removal_requests/")
    print(f"{'=' * 60}\n")
