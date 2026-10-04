"""
Paáré — Phase 2: AI Classification Engine
------------------------------------------
Takes a list of URLs + metadata and returns removability scores,
content types, and recommended actions via Google Gemini API.
"""

import os
import json
import time
from google import genai

# ─── Gemini client ────────────────────────────────────────────────────────────
with open("config.json", "r") as f:
    config = json.load(f)

client = genai.Client(api_key=config["GEMINI_API_KEY"])

SYSTEM_PROMPT = """
You are the classification engine inside "Paáré", a digital footprint removal tool.
Your job is to analyse URLs and page snippets and determine how removable the content 
is and what the user should do.
 
You MUST respond with ONLY a valid JSON array. No preamble, no explanation, 
no markdown fences. Just the raw JSON array.
 
Each item in the array must follow this exact schema:
{
  "url": "string — the original URL",
  "platform": "string — e.g. Instagram, Twitter, Reddit, Facebook, Google, News, Unknown",
  "content_type": "string — one of: social_post, photo, video, profile, news_article, forum_post, data_broker, other",
  "subject": "string — brief description of what the content appears to be",
  "removability": "HIGH | MEDIUM | LOW | NONE",
  "removability_reason": "string — 1-2 sentences explaining the score",
  "legal_basis": "string — e.g. GDPR Article 17, CCPA 1798.105, Platform ToS, None",
  "suggested_action": "string — one of: gdpr_email, ccpa_request, platform_form, account_login_delete, dmca, manual_report, not_removable",
  "priority": 1,
  "notes": "string — any extra context the user should know"
}
 
Priority must be an integer 1-5 (not a string).
 
Removability scale:
- HIGH: Platform must comply (GDPR/CCPA applies, or it's the user's own account content)
- MEDIUM: Likely removable with effort (platform discretion, abuse reports)
- LOW: Difficult but not impossible (third-party content, data brokers)
- NONE: Protected speech, journalism, court records — legally cannot force removal
 
Priority scale (1 = urgent, 5 = low):
- 1: Embarrassing personal content, photos, explicit material
- 2: Old social profiles, tagged photos
- 3: Forum posts, comments
- 4: Data broker listings
- 5: Old news mentions with low search ranking
""".strip()


# ─── Core classification function ────────────────────────────────────────────

def classify_urls(urls_with_context: list[dict]) -> list[dict]:
    items_text = ""
    for i, item in enumerate(urls_with_context, 1):
        items_text += f"\n[{i}] URL: {item['url']}"
        if item.get("page_title"):
            items_text += f"\n    Title: {item['page_title']}"
        if item.get("snippet"):
            items_text += f"\n    Snippet: {item['snippet'][:300]}"
        items_text += "\n"

    prompt = f"""{SYSTEM_PROMPT}

Classify the following {len(urls_with_context)} URL(s) for digital content removal.
Return a JSON array with one object per URL. Raw JSON only, no markdown.

{items_text}"""

    # Retry logic for 503s
    for attempt in range(3):
        try:
            response = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
            break
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                wait = (attempt + 1) * 10
                print(f"   ⏳ Gemini busy, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    results = json.loads(raw)
    return results


# ─── Pretty printer ──────────────────────────────────────────────────────────

REMOVABILITY_EMOJI = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🟠", "NONE": "🔴"}
PRIORITY_LABEL = {1: "🚨 Urgent", 2: "⚠️  High", 3: "📋 Medium", 4: "📦 Low", 5: "💤 Minimal"}

def print_results(results: list[dict]) -> None:
    print("\n" + "═" * 65)
    print("  PAÁRÉ — Classification Results")
    print("═" * 65)

    for r in results:
        emoji = REMOVABILITY_EMOJI.get(r.get("removability", "NONE"), "❓")
        priority = PRIORITY_LABEL.get(r.get("priority", 5), "")
        print(f"\n{emoji} [{r.get('removability')}]  {r.get('platform')} — {r.get('content_type')}")
        print(f"   URL      : {r.get('url')}")
        print(f"   Subject  : {r.get('subject')}")
        print(f"   Priority : {priority}")
        print(f"   Action   : {r.get('suggested_action')}")
        print(f"   Legal    : {r.get('legal_basis')}")
        print(f"   Reason   : {r.get('removability_reason')}")
        if r.get("notes"):
            print(f"   Notes    : {r.get('notes')}")

    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "NONE": 0}
    for r in results:
        counts[r.get("removability", "NONE")] += 1

    print("\n" + "─" * 65)
    print(f"  Total: {len(results)} items  |  "
          f"🟢 {counts['HIGH']} HIGH  "
          f"🟡 {counts['MEDIUM']} MEDIUM  "
          f"🟠 {counts['LOW']} LOW  "
          f"🔴 {counts['NONE']} NONE")
    print("═" * 65 + "\n")


def save_results(results: list[dict], filepath: str = "scan_results.json") -> None:
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)
    print(f"💾 Results saved to {filepath}")

