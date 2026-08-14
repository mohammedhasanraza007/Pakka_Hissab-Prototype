"""Pakka Hisaab local web application."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .db import DEFAULT_DB, dashboard_state, ensure_database, seed
from .intent import parse_command
from .workflow import checkout, inventory_query, settle_payment, view_cart


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
app = FastAPI(title="Pakka Hisaab", version="1.0.0")
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
logger = logging.getLogger("pakkahisaab")


class CommandRequest(BaseModel):
    text: str
    language: str = "English"


class TTSRequest(BaseModel):
    text: str
    language: str = "en"


@app.on_event("startup")
def startup() -> None:
    ensure_database(DEFAULT_DB).close()


def connection():
    return ensure_database(DEFAULT_DB)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "database": "sqlite", "voice": "browser + optional edge-tts"}


@app.get("/api/state")
def state() -> dict:
    db = connection()
    try:
        return dashboard_state(db)
    finally:
        db.close()


@app.post("/api/command")
def command(request: CommandRequest) -> dict:
    parsed = parse_command(request.text)
    db = connection()
    try:
        if parsed.intent == "checkout_cart":
            result = checkout(db, parsed.cart_id, parsed.payment_method or "upi")
        elif parsed.intent == "view_cart":
            result = view_cart(db, parsed.cart_id)
        elif parsed.intent == "inventory_query":
            result = inventory_query(db, parsed.product_query)
        elif parsed.intent == "reset_demo":
            seed(db)
            result = {"ok": True, "kind": "reset_demo", "message": "Demo data restored from the deterministic seed.", "state": dashboard_state(db)}
        elif parsed.intent == "switch_language":
            result = {"ok": True, "kind": "switch_language", "language": parsed.language, "message": f"Language set to {parsed.language.title()}.", "state": dashboard_state(db)}
        else:
            result = {"ok": False, "kind": "unsupported", "error": "I couldn't map that to a supported POS action. Try checkout, show cart, stock, language, or reset."}
        result["intent"] = parsed.as_dict()
        return result
    finally:
        db.close()


@app.post("/api/payment/{payment_id}/{outcome}")
def payment(payment_id: int, outcome: str) -> JSONResponse:
    if outcome not in {"success", "failure"}:
        return JSONResponse({"ok": False, "error": "Unsupported payment outcome."}, status_code=400)
    db = connection()
    try:
        return JSONResponse(settle_payment(db, payment_id, outcome))
    finally:
        db.close()


@app.post("/api/tts")
async def tts(request: TTSRequest) -> Response:
    """Optional multilingual edge-tts endpoint; the browser fallback remains primary."""
    try:
        import edge_tts
    except ImportError:
        return JSONResponse({"ok": False, "error": "edge-tts is not installed; use browser speech playback."}, status_code=503)
    voices = {"en": "en-IN-NeerjaNeural", "hi": "hi-IN-SwaraNeural", "ta": "ta-IN-PallaviNeural"}
    voice = voices.get(request.language, voices["en"])
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as target:
        path = Path(target.name)
    try:
        await edge_tts.Communicate(request.text, voice).save(str(path))
        return Response(path.read_bytes(), media_type="audio/mpeg")
    except Exception:
        logger.exception("TTS request failed")
        return JSONResponse({"ok": False, "error": "TTS unavailable; browser speech remains available."}, status_code=503)
    finally:
        path.unlink(missing_ok=True)
