from __future__ import annotations
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from models import Presentation
from session import manager

router = APIRouter(prefix="/api")

PRESENTATIONS_DIR = Path(__file__).parent.parent.parent / "presentations"


# ---------------------------------------------------------------------------
# Presentations
# ---------------------------------------------------------------------------

@router.get("/presentations")
async def list_presentations():
    files = sorted(PRESENTATIONS_DIR.glob("*.json"))
    return [f.name for f in files]


@router.get("/presentations/{filename}")
async def get_presentation(filename: str):
    if ".." in filename or "/" in filename:
        raise HTTPException(400, "Invalid filename")
    path = PRESENTATIONS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Not found")
    return json.loads(path.read_text())


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

class CreateSessionRequest(BaseModel):
    presentation_file: str


class CreateSessionResponse(BaseModel):
    session_code: str
    presenter_token: str


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(body: CreateSessionRequest):
    filename = body.presentation_file
    if ".." in filename or "/" in filename:
        raise HTTPException(400, "Invalid filename")
    path = PRESENTATIONS_DIR / filename
    if not path.exists():
        raise HTTPException(404, f"Presentation '{filename}' not found")
    try:
        data = json.loads(path.read_text())
        presentation = Presentation.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(422, str(e))

    code, token = manager.create_session(presentation)
    return CreateSessionResponse(session_code=code, presenter_token=token)


@router.get("/sessions/{code}")
async def get_session(code: str):
    s = manager.get(code)
    if not s:
        raise HTTPException(404, "Session not found")
    return {
        "code": s.code,
        "title": s.presentation.title,
        "phase": s.phase.value,
        "player_count": len(s.players),
        "slide_count": len(s.presentation.slides),
    }


@router.delete("/sessions/{code}")
async def delete_session(code: str):
    s = manager.get(code)
    if not s:
        raise HTTPException(404, "Session not found")
    manager.delete(code)
    return {"ok": True}
