from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from routes.api import router as api_router
from routes.ws import router as ws_router
from session import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_cleanup_loop())
    yield
    task.cancel()


async def _cleanup_loop():
    while True:
        await asyncio.sleep(600)  # every 10 minutes
        manager.cleanup_idle()


app = FastAPI(title="Quizzle", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(ws_router)

# Serve built frontend in production
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")


@app.get("/health")
async def health():
    return {"status": "ok"}
