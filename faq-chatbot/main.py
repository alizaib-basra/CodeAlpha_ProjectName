"""
FAQ Chatbot — FastAPI Backend
==============================
Run: uvicorn main:app --reload
Open: http://localhost:8000
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from nlp import get_best_match, get_all_faqs

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="FAQ Chatbot", version="1.0.0")

# ── Serve static files ───────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Request model ────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str

# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/")
def home():
    """Serve the chat UI."""
    return FileResponse("static/index.html")


@app.post("/chat")
def chat(request: ChatRequest):
    """
    Receive user message, find best matching FAQ,
    return the answer with confidence score.
    """
    if not request.message.strip():
        return {
            "question":   None,
            "answer":     "Please type a question!",
            "confidence": 0,
            "matched":    False
        }

    result = get_best_match(request.message)
    return result


@app.get("/faqs")
def list_faqs():
    """Return all FAQs."""
    return get_all_faqs()


@app.get("/health")
def health():
    return {"status": "ok"}
