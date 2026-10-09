# Paáré 🩸

> *Paáré* — Yoruba for "to wipe away, to clean off"

**Paáré** is an AI-powered digital footprint removal tool that helps individuals reclaim their digital past. It finds your old content across the web, classifies how removable each piece is, and automatically generates the legal requests and action guides needed to get it taken down.

---

## What it does

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** — Discovery | Searches the web for your name, usernames, photos | ✅ Complete |
| **Phase 2** — Classification | AI classifies each result by removability & legal basis | ✅ Complete |
| **Phase 3** — Removal Requests | Generates GDPR emails, CCPA requests, platform guides | ✅ Complete |
| **API Layer** | FastAPI endpoints for the full pipeline and each phase | ✅ Complete |
| **Phase 4** — Dashboard | React UI to track everything in one place | 🔜 Coming soon |

---

## How it works

```
Your name / username / email
        ↓
  Discovery Engine  (Phase 1)  →  DuckDuckGo search across platforms & data brokers
        ↓
  AI Classifier     (Phase 2)  →  removability score, legal basis, priority
        ↓
  Request Generator (Phase 3)  →  GDPR emails, CCPA requests, manual guides
        ↓
  FastAPI REST API              →  expose the pipeline to any frontend
        ↓
  Dashboard         (Phase 4)  →  track status of every removal request [coming soon]
```

---

## Tech Stack

- **Python 3.13** — core engine
- **ddgs** (DuckDuckGo Search) — free web discovery, no API key needed
- **Google Gemini API** (gemini-3.8-flash) — AI classification and request generation
- **FastAPI + Uvicorn** — REST API with interactive OpenAPI documentation
- **React + Tailwind** — dashboard UI *(Phase 4, coming soon)*

---

## Project Structure

```
Paare/
├── discovery.py          # Phase 1 — web scraper & search engine
├── classifier.py         # Phase 2 — AI classification engine
├── phase3_generator.py   # Phase 3 — removal request generator
├── pipeline.py           # Full pipeline — runs all 3 phases in one go
├── main.py               # FastAPI REST API for the complete pipeline
├── demo.py               # Phase 2 demo with sample URLs
├── requirements.txt      # Python dependencies
├── config.json           # API keys (gitignored — never committed)
├── config.example.json   # Template for config.json
├── discovered_urls.json  # Phase 1 output (gitignored)
├── scan_results.json     # Phase 2 output (gitignored)
└── removal_requests/     # Phase 3 output folder (gitignored)
```

---

## Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/oluwamay0wa/Paare.git
cd Paare
```

### 2. Create a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
Copy `config.example.json` to `config.json` and fill in your key:
```json
{
  "GEMINI_API_KEY": "your-gemini-key-here"
}
```
Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com)

### 5. Run the full pipeline
Edit the `TARGET` in `pipeline.py` with the person's details:
```python
TARGET = {
    "name": "John Adebayo",
    "usernames": ["jadebayo"],
    "email": "johnadebayo@gmail.com",
    "deep": False,
}
```

Then run:
```bash
python pipeline.py
```

### 6. Or run phases individually
```bash
python discovery.py          # Phase 1 only — find URLs
python demo.py               # Phase 2 only — classify sample URLs
python phase3_generator.py   # Phase 3 only — generate removal requests
```

### 7. Run the REST API
Start the API locally with:
```bash
uvicorn main:app --reload
```

The interactive API documentation is available at [localhost:8000/docs](http://localhost:8000/docs).
The API also exposes an OpenAPI schema at [localhost:8000/openapi.json](http://localhost:8000/openapi.json).

Available endpoints:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/` | API metadata and endpoint list |
| `GET` | `/health` | Health check |
| `POST` | `/discover` | Discover URLs for a person |
| `POST` | `/classify` | Classify discovered URLs |
| `POST` | `/generate` | Generate removal requests |
| `POST` | `/scan` | Run all three phases in one request |

Example full scan request:
```bash
curl -X POST http://localhost:8000/scan ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"John Adebayo\",\"usernames\":[\"jadebayo\"],\"email\":\"johnadebayo@gmail.com\",\"deep\":false}"
```

On macOS/Linux, replace the continuation characters (`^`) with backslashes (`\`).

---

## Sample Output

```
🩸 Paáré — Full Pipeline
============================================================

📡 PHASE 1 — Discovery

🔍 Searching for: John Adebayo
   Usernames : jadebayo

   [1/5] General name search...     → 10 results
   [2/5] Social platform search...  → 7 results
   [3/5] Username searches...       → 4 results
   [4/5] Email search...            → 0 results
   [5/5] Data broker search...      → 5 results

  Total discovered: 26 URLs

🧠 PHASE 2 — AI Classification

═════════════════════════════════════════════════════════════════
  PAÁRÉ — Classification Results
═════════════════════════════════════════════════════════════════

🟢 [HIGH]  LinkedIn — profile
   URL      : https://www.linkedin.com/in/john-adebayo
   Priority : ⚠️  High
   Action   : gdpr_email
   Legal    : GDPR Article 17

🟠 [LOW]  Data Broker — data_broker
   URL      : https://www.spokeo.com/John-Adebayo
   Priority : 📦 Low
   Action   : ccpa_request
   Legal    : CCPA 1798.105

─────────────────────────────────────────────────────────────────
  Total: 26 items  |  🟢 8 HIGH  🟡 4 MEDIUM  🟠 6 LOW  🔴 8 NONE
═════════════════════════════════════════════════════════════════

📨 PHASE 3 — Removal Request Generation
   [1/26] LinkedIn — gdpr_email... ✅
   [2/26] Spokeo — ccpa_request... ✅
   ...

  Done! 26 removal requests saved to ./removal_requests/
```

---

## Removability Scale

| Score | Meaning |
|-------|---------|
| 🟢 **HIGH** | Platform must comply — GDPR/CCPA applies or it's your own content |
| 🟡 **MEDIUM** | Likely removable with effort — platform discretion or abuse reports |
| 🟠 **LOW** | Difficult but not impossible — data brokers, third-party content |
| 🔴 **NONE** | Protected speech, journalism — cannot be legally forced down |

---

## Legal Basis

Paáré leverages real privacy law to back every removal request:

- **GDPR Article 17** — Right to Erasure (EU)
- **CCPA Section 1798.105** — Right to Delete (California)
- **Platform ToS** — Internal content moderation policies
- **DMCA** — For copyright-infringing content

---

## Important Notes

- Paáré automates the *request* process — platforms ultimately decide on removal
- News articles and press content are generally protected by freedom of the press
- Wayback Machine / Archive.org has a manual opt-out process
- Keep your `config.json` local — never commit API keys to GitHub

---

## Roadmap

- [x] Phase 1 — Discovery Engine
- [x] Phase 2 — AI Classification
- [x] Phase 3 — Removal Request Generator
- [x] FastAPI REST API for frontend integration
- [ ] Phase 4 — React Dashboard
- [ ] Playwright automation for platform form filling
- [ ] Email sending integration
- [ ] User authentication & multi-profile support

---

## Built by

**Mayowa** — CS Student, Covenant University, Nigeria
GitHub: [@oluwamay0wa](https://github.com/oluwamay0wa)

---

*"Everyone deserves a second chance — even on the internet."*
