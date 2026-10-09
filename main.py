"""
Paáré — REST API
-----------------
FastAPI backend exposing all three phases as HTTP endpoints.
Collaborators can build any frontend on top of this.

Run with:
    uvicorn main:app --reload

API Docs (auto-generated):
    http://localhost:8000/docs
"""

import warnings
warnings.filterwarnings("ignore")

import json
import time
import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from discovery import discover
from classifier import classify_urls
from phase3_generator import generate_request, save_request

# ─── App setup ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Paáré API",
    description="AI-powered digital footprint removal tool — REST API",
    version="1.0.0",
)

# Allow all origins so any frontend can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request / Response models ────────────────────────────────────────────────

class ScanRequest(BaseModel):
    name: str
    usernames: list[str] = []
    email: str = ""
    deep: bool = False

class ClassifyRequest(BaseModel):
    urls: list[dict]

class GenerateRequest(BaseModel):
    scan_results: list[dict]


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "Paáré API",
        "version": "1.0.0",
        "description": "AI-powered digital footprint removal tool",
        "docs": "/docs",
        "endpoints": {
            "POST /scan": "Run full pipeline (Phase 1 + 2 + 3)",
            "POST /discover": "Phase 1 — discover URLs for a person",
            "POST /classify": "Phase 2 — classify a list of URLs",
            "POST /generate": "Phase 3 — generate removal requests",
            "GET  /health": "Health check",
        }
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/discover")
def discover_endpoint(body: ScanRequest):
    """
    Phase 1 — Search the web for a person's digital footprint.

    Returns a list of discovered URLs with titles and snippets.
    """
    try:
        results = discover(
            name=body.name,
            usernames=body.usernames,
            email=body.email,
            deep=body.deep,
        )
        return {
            "success": True,
            "name": body.name,
            "total": len(results),
            "urls": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify")
def classify_endpoint(body: ClassifyRequest):
    """
    Phase 2 — Classify a list of URLs for removability.

    Accepts the output of /discover directly.
    Returns removability scores, legal basis, and suggested actions.
    """
    if not body.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")
    try:
        results = classify_urls(body.urls)
        return {
            "success": True,
            "total": len(results),
            "summary": {
                "HIGH": sum(1 for r in results if r.get("removability") == "HIGH"),
                "MEDIUM": sum(1 for r in results if r.get("removability") == "MEDIUM"),
                "LOW": sum(1 for r in results if r.get("removability") == "LOW"),
                "NONE": sum(1 for r in results if r.get("removability") == "NONE"),
            },
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
def generate_endpoint(body: GenerateRequest):
    """
    Phase 3 — Generate removal requests for classified results.

    Accepts the output of /classify directly.
    Returns generated emails, guides, and instruction cards.
    """
    if not body.scan_results:
        raise HTTPException(status_code=400, detail="No scan results provided")
    try:
        output = []
        for i, item in enumerate(body.scan_results, 1):
            result = generate_request(item)
            save_request(result, i)
            output.append(result)
        return {
            "success": True,
            "total": len(output),
            "requests": output,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scan")
def full_scan(body: ScanRequest):
    """
    Full pipeline — runs Phase 1 + 2 + 3 in one request.

    This is the main endpoint most frontends will use.
    Returns discovered URLs, classifications, and removal requests all at once.
    """
    try:
        # Phase 1
        urls = discover(
            name=body.name,
            usernames=body.usernames,
            email=body.email,
            deep=body.deep,
        )
        if not urls:
            return {
                "success": True,
                "name": body.name,
                "total_discovered": 0,
                "message": "No URLs found for this person.",
                "urls": [],
                "classifications": [],
                "removal_requests": [],
            }

        # Phase 2
        classifications = classify_urls(urls)

        # Phase 3
        removal_requests = []
        for i, item in enumerate(classifications, 1):
            result = generate_request(item)
            save_request(result, i)
            removal_requests.append(result)

        return {
            "success": True,
            "name": body.name,
            "total_discovered": len(urls),
            "summary": {
                "HIGH": sum(1 for r in classifications if r.get("removability") == "HIGH"),
                "MEDIUM": sum(1 for r in classifications if r.get("removability") == "MEDIUM"),
                "LOW": sum(1 for r in classifications if r.get("removability") == "LOW"),
                "NONE": sum(1 for r in classifications if r.get("removability") == "NONE"),
            },
            "urls": urls,
            "classifications": classifications,
            "removal_requests": removal_requests,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)