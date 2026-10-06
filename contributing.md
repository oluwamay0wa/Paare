# Contributing to Paáré — Frontend

Thanks for collaborating! The backend is fully built. Your job is to build a frontend that talks to it.

---

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/oluwamay0wa/Paare.git
cd Paare
```

### 2. Set up the backend
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Add your API key
Copy `config.example.json` to `config.json` and fill in your Gemini key:
```json
{
  "GEMINI_API_KEY": "your-gemini-key-here"
}
```
Get a free key at [aistudio.google.com](https://aistudio.google.com)

### 4. Start the backend
```bash
uvicorn main:app --reload
```

The API is now running at `http://localhost:8000`
Auto-generated docs at `http://localhost:8000/docs`

---

## API Reference

### `POST /scan` — Full pipeline (recommended)
Runs discovery + classification + request generation in one call.

**Request:**
```json
{
  "name": "John Adebayo",
  "usernames": ["jadebayo"],
  "email": "johnadebayo@gmail.com",
  "deep": false
}
```

**Response:**
```json
{
  "success": true,
  "name": "John Adebayo",
  "total_discovered": 26,
  "summary": {
    "HIGH": 8,
    "MEDIUM": 4,
    "LOW": 6,
    "NONE": 8
  },
  "urls": [...],
  "classifications": [...],
  "removal_requests": [...]
}
```

---

### `POST /discover` — Phase 1 only
Search the web for a person's digital footprint.

### `POST /classify` — Phase 2 only
Classify a list of URLs. Accepts output of `/discover`.

### `POST /generate` — Phase 3 only
Generate removal requests. Accepts output of `/classify`.

### `GET /health` — Health check
Returns `{"status": "ok"}` if the backend is running.

---

## What to Build

The frontend should:

- [ ] Input form: name, usernames, email
- [ ] Loading state while the scan runs (it takes ~30 seconds)
- [ ] Results table showing each URL with its removability badge
- [ ] Detail view for each removal request (email, guide, etc.)
- [ ] Status tracker: Found → Requested → Confirmed Removed
- [ ] Export / download button for removal requests

---

## Tech Suggestions

Use whatever you're comfortable with:
- **React + Tailwind** (recommended)
- **Vue.js**
- **Plain HTML/CSS/JS**
- **Next.js**

Put your frontend code in a `/frontend` folder.

---

## Colour System (for consistency)

| Status | Colour |
|--------|--------|
| HIGH removability | 🟢 Green `#22c55e` |
| MEDIUM removability | 🟡 Yellow `#eab308` |
| LOW removability | 🟠 Orange `#f97316` |
| NONE removability | 🔴 Red `#ef4444` |

---

## Questions?

Open an issue or reach out to [@oluwamay0wa](https://github.com/oluwamay0wa).
