from __future__ import annotations
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from session import manager

router = APIRouter()


@router.websocket("/ws/presenter/{code}")
async def ws_presenter(code: str, ws: WebSocket, token: str = Query(...)):
    s = manager.get(code)
    if not s or s.presenter_token != token:
        await ws.close(code=4003)
        return
    await ws.accept()
    await manager.register_presenter(code, ws)
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")
            if msg_type == "next_slide":
                await manager.handle_next_slide(code)
            elif msg_type == "prev_slide":
                await manager.handle_prev_slide(code)
            elif msg_type == "start_question":
                await manager.handle_start_question(code)
            elif msg_type == "reveal_answers":
                await manager.handle_reveal(code)
            elif msg_type == "show_leaderboard":
                await manager.handle_show_leaderboard(code)
    except WebSocketDisconnect:
        s2 = manager.get(code)
        if s2 and s2.presenter_ws is ws:
            s2.presenter_ws = None


@router.websocket("/ws/display/{code}")
async def ws_display(code: str, ws: WebSocket):
    s = manager.get(code)
    if not s:
        await ws.close(code=4004)
        return
    await ws.accept()
    await manager.register_display(code, ws)
    try:
        while True:
            # Display is read-only; just keep connection alive
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.unregister_display(code, ws)


@router.websocket("/ws/player/{code}/{nickname}")
async def ws_player(code: str, nickname: str, ws: WebSocket):
    s = manager.get(code)
    if not s:
        await ws.close(code=4004)
        return
    if not nickname or len(nickname) > 30:
        await ws.close(code=4001)
        return
    await ws.accept()
    ok = await manager.register_player(code, nickname, ws)
    if not ok:
        await ws.send_json({"type": "error", "message": "Nickname already taken"})
        await ws.close(code=4001)
        return
    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "submit_answer":
                await manager.handle_player_answer(code, nickname, data.get("answer"))
    except WebSocketDisconnect:
        await manager.unregister_player(code, nickname)
