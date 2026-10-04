"""
Paáré — Phase 3: Removal Request Generator
--------------------------------------------
Reads scan_results.json from Phase 2 and generates:
  - GDPR / CCPA erasure emails
  - Manual instruction cards
  - Login-and-delete guides
  - Platform form instructions

All outputs saved to /removal_requests/
"""

import json
import time
from google import genai
from pathlib import Path


# ─── Gemini client ────────────────────────────────────────────────────────────
with open("config.json", "r") as f:
    config = json.load(f)

client = genai.Client(api_key=config["GEMINI_API_KEY"])

OUTPUT_DIR = Path("removal_requests")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── Prompt templates ────────────────────────────────────────────────────────

GDPR_PROMPT = """
Write a formal GDPR Article 17 Right to Erasure request email.
Platform: {platform}
Content URL: {url}
Content description: {subject}
Legal basis: {legal_basis}

Include:
1. Subject line: "Erasure Request under GDPR Article 17 — Right to be Forgotten"
2. Identify sender as a data subject exercising legal rights
3. State the URL clearly
4. Cite GDPR Article 17 and grounds for erasure
5. Request confirmation within 30 days
6. Sign as "The Data Subject"

Write only the email. No extra commentary.
""".strip()

CCPA_PROMPT = """
Write a formal CCPA Section 1798.105 deletion request email.
Platform/Data Broker: {platform}
Listing URL: {url}
Content description: {subject}

Include:
1. Subject line: "CCPA Deletion Request — Section 1798.105"
2. Identify sender as a consumer invoking CCPA rights
3. State the listing URL clearly
4. Cite CCPA Section 1798.105
5. Request confirmation within 45 days
6. Sign as "The Consumer"

Write only the email. No extra commentary.
""".strip()

MANUAL_PROMPT = """
Write a clear step-by-step instruction card for manually handling removal of content.
Platform: {platform}
Content URL: {url}
Content description: {subject}
Suggested action: {suggested_action}
Why it's difficult: {removability_reason}

Write practical numbered steps. Be honest about likelihood of success.
Keep it under 200 words. No extra commentary.
""".strip()

LOGIN_DELETE_PROMPT = """
Write a short step-by-step guide for logging into a platform and deleting content.
Platform: {platform}
Content URL: {url}
Content description: {subject}

Write numbered steps specific to this platform.
Include direct URLs to navigate to where possible.
Keep it under 150 words. No extra commentary.
""".strip()

PLATFORM_FORM_PROMPT = """
Write step-by-step instructions for submitting a content removal request through a platform's official form.
Platform: {platform}
Content URL: {url}
Content description: {subject}
Legal basis available: {legal_basis}

Include the direct link to the platform's removal form if you know it.
Write numbered steps. Keep it under 200 words. No extra commentary.
""".strip()


# ─── Generator ────────────────────────────────────────────────────────────────

def call_ai(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
            return response.text.strip()
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                wait = (attempt + 1) * 10
                print(f"\n   ⏳ Server busy, retrying in {wait}s...", end=" ")
                time.sleep(wait)
            else:
                raise
    raise Exception("Gemini API unavailable after 3 retries")


def generate_request(item: dict) -> dict:
    action = item.get("suggested_action")
    platform = item.get("platform", "Unknown")
    url = item.get("url", "")
    subject = item.get("subject", "")
    legal_basis = item.get("legal_basis", "None")
    removability_reason = item.get("removability_reason", "")

    if action == "gdpr_email":
        prompt = GDPR_PROMPT.format(platform=platform, url=url, subject=subject, legal_basis=legal_basis)
        output_type = "GDPR Erasure Email"
    elif action == "ccpa_request":
        prompt = CCPA_PROMPT.format(platform=platform, url=url, subject=subject)
        output_type = "CCPA Deletion Request"
    elif action == "account_login_delete":
        prompt = LOGIN_DELETE_PROMPT.format(platform=platform, url=url, subject=subject)
        output_type = "Login & Delete Guide"
    elif action == "platform_form":
        prompt = PLATFORM_FORM_PROMPT.format(platform=platform, url=url, subject=subject, legal_basis=legal_basis)
        output_type = "Platform Form Instructions"
    else:
        prompt = MANUAL_PROMPT.format(platform=platform, url=url, subject=subject,
                                       suggested_action=action, removability_reason=removability_reason)
        output_type = "Manual Instruction Card"

    content = call_ai(prompt)
    return {
        "url": url,
        "platform": platform,
        "output_type": output_type,
        "action": action,
        "removability": item.get("removability"),
        "content": content
    }


def save_request(result: dict, index: int) -> Path:
    safe_platform = result["platform"].replace(" ", "_").lower()
    filename = OUTPUT_DIR / f"{index:02d}_{safe_platform}_{result['action']}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{'═' * 60}\n")
        f.write(f"  PAÁRÉ — {result['output_type'].upper()}\n")
        f.write(f"{'═' * 60}\n\n")
        f.write(f"Platform    : {result['platform']}\n")
        f.write(f"URL         : {result['url']}\n")
        f.write(f"Action Type : {result['action']}\n")
        f.write(f"Removability: {result['removability']}\n")
        f.write(f"\n{'─' * 60}\n\n")
        f.write(result["content"])
        f.write(f"\n\n{'═' * 60}\n")
    return filename


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    scan_file = Path("scan_results.json")
    if not scan_file.exists():
        print("❌ scan_results.json not found. Run demo.py first.")
        return

    with open(scan_file, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"\n🩸 Paáré — Phase 3 Removal Request Generator")
    print(f"   Processing {len(items)} items...\n")

    for i, item in enumerate(items, 1):
        platform = item.get("platform", "Unknown")
        action = item.get("suggested_action", "unknown")
        print(f"   [{i}/{len(items)}] {platform} — {action}...", end=" ", flush=True)
        result = generate_request(item)
        filepath = save_request(result, i)
        print(f"✅ {filepath.name}")

    summary_path = OUTPUT_DIR / "summary.json"
    print(f"\n{'═' * 60}")
    print(f"  Done! {len(items)} removal requests generated.")
    print(f"  📁 Saved to: ./{OUTPUT_DIR}/")
    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    main()