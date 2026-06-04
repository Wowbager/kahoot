from __future__ import annotations
import asyncio
import random
import string
import time
from dataclasses import dataclass, field
from typing import Optional

from fastapi import WebSocket

from models import (
    AnySlide, Presentation, Player, QuestionPhase,
    MultipleMatchingSlide, QUESTION_TYPES, safe_slide_dict,
)
from scoring import calculate_score, streak_bonus

# Intro stages played after the presenter starts a question, before answering opens.
TYPE_STAGE_SECONDS = 3      # stage 1: question type only
QUESTION_STAGE_SECONDS = 3  # stage 2: question text shown, answers still hidden


def _generate_pin(length: int = 6) -> str:
    """A short numeric game PIN, easy to type on a phone keypad."""
    return "".join(random.choices(string.digits, k=length))


def _generate_token(length: int = 16) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


@dataclass
class SessionData:
    code: str
    presenter_token: str
    presentation: Presentation
    current_index: int = 0
    phase: QuestionPhase = QuestionPhase.IDLE
    started: bool = False    # False while in the pre-game lobby
    finished: bool = False   # True once the podium/game-over has been shown
    players: dict[str, Player] = field(default_factory=dict)
    answers: dict[str, object] = field(default_factory=dict)
    answer_times: dict[str, float] = field(default_factory=dict)  # nickname → time.time() when answered
    question_started_at: Optional[float] = None  # time.time() — when answering opens / scoring clock starts
    question_reveal_at: Optional[float] = None   # time.time() — when the question text is revealed (stage 2)
    shuffled_right: Optional[list[str]] = None   # for multiple_matching
    last_activity: float = field(default_factory=time.time)

    # WebSocket registries
    presenter_ws: Optional[WebSocket] = None
    display_ws_list: list[WebSocket] = field(default_factory=list)
    player_ws: dict[str, WebSocket] = field(default_factory=dict)  # nickname → ws

    def current_slide(self) -> AnySlide:
        return self.presentation.slides[self.current_index]

    def is_question_slide(self) -> bool:
        return self.current_slide().type in QUESTION_TYPES

    def touch(self):
        self.last_activity = time.time()


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, SessionData] = {}

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def create_session(self, presentation: Presentation) -> tuple[str, str]:
        code = _generate_pin()
        for _ in range(50):
            if code not in self._sessions:
                break
            code = _generate_pin()
        token = _generate_token(16)
        self._sessions[code] = SessionData(
            code=code,
            presenter_token=token,
            presentation=presentation,
        )
        return code, token

    def get(self, code: str) -> Optional[SessionData]:
        return self._sessions.get(code)

    def delete(self, code: str):
        self._sessions.pop(code, None)

    def cleanup_idle(self, max_idle_seconds: int = 7200):
        now = time.time()
        stale = [c for c, s in self._sessions.items() if now - s.last_activity > max_idle_seconds]
        for code in stale:
            del self._sessions[code]

    # ------------------------------------------------------------------
    # WebSocket registration
    # ------------------------------------------------------------------

    async def register_presenter(self, code: str, ws: WebSocket):
        s = self._sessions[code]
        s.presenter_ws = ws
        s.touch()
        await self._send(ws, self._state_snapshot(s, "presenter"))

    async def register_display(self, code: str, ws: WebSocket):
        s = self._sessions[code]
        s.display_ws_list.append(ws)
        s.touch()
        await self._send(ws, self._state_snapshot(s, "display"))

    async def register_player(self, code: str, nickname: str, ws: WebSocket) -> bool:
        s = self._sessions[code]
        if nickname in s.players and nickname in s.player_ws:
            return False  # duplicate
        s.players[nickname] = Player(nickname=nickname)
        s.player_ws[nickname] = ws
        s.touch()
        await self._send(ws, self._state_snapshot(s, "player"))
        await self._broadcast_presenter(s, {
            "type": "player_joined",
            "nickname": nickname,
            "players": [p.model_dump() for p in s.players.values()],
        })
        await self._broadcast_display(s, {
            "type": "player_joined",
            "nickname": nickname,
            "count": len(s.players),
        })
        return True

    async def unregister_player(self, code: str, nickname: str):
        s = self._sessions.get(code)
        if not s:
            return
        s.player_ws.pop(nickname, None)
        await self._broadcast_presenter(s, {
            "type": "player_left",
            "nickname": nickname,
            "players": [p.model_dump() for p in s.players.values()],
        })

    async def unregister_display(self, code: str, ws: WebSocket):
        s = self._sessions.get(code)
        if s and ws in s.display_ws_list:
            s.display_ws_list.remove(ws)

    # ------------------------------------------------------------------
    # Game actions (called from WebSocket handlers)
    # ------------------------------------------------------------------

    async def handle_start_game(self, code: str):
        s = self._sessions[code]
        if s.started:
            return
        s.started = True
        s.finished = False
        s.current_index = 0
        s.phase = QuestionPhase.IDLE
        s.touch()
        await self._broadcast_all(s, {"type": "game_started"})
        await self._broadcast_slide_changed(s)

    async def handle_end_game(self, code: str):
        s = self._sessions[code]
        s.finished = True
        s.phase = QuestionPhase.FINISHED
        s.touch()
        ranked, rank_map = self._ranked(s)
        # Stage / display: full final standings (rendered as a top-3 podium)
        await self._broadcast_presenter(s, {"type": "game_over", "standings": ranked})
        await self._broadcast_display(s, {"type": "game_over", "standings": ranked})
        # Each player privately learns their own final placing
        for nickname, ws in s.player_ws.items():
            rank, total = rank_map.get(nickname, (len(ranked), len(ranked)))
            await self._send(ws, {
                "type": "game_over",
                "rank": rank,
                "total": total,
                "score": s.players[nickname].score if nickname in s.players else 0,
            })

    async def handle_next_slide(self, code: str):
        s = self._sessions[code]
        if s.current_index < len(s.presentation.slides) - 1:
            s.current_index += 1
            s.phase = QuestionPhase.IDLE
            s.answers = {}
            s.answer_times = {}
            s.question_started_at = None
            s.question_reveal_at = None
            s.shuffled_right = None
            s.touch()
            await self._broadcast_slide_changed(s)

    async def handle_prev_slide(self, code: str):
        s = self._sessions[code]
        if s.current_index > 0:
            s.current_index -= 1
            s.phase = QuestionPhase.IDLE
            s.answers = {}
            s.answer_times = {}
            s.question_started_at = None
            s.question_reveal_at = None
            s.shuffled_right = None
            s.touch()
            await self._broadcast_slide_changed(s)

    async def handle_start_question(self, code: str):
        s = self._sessions[code]
        if not s.is_question_slide() or s.phase != QuestionPhase.IDLE:
            return
        slide = s.current_slide()
        s.phase = QuestionPhase.ACTIVE
        s.answers = {}
        s.answer_times = {}
        # Three-stage intro before answering opens:
        #   stage 1 (TYPE_STAGE_SECONDS): show only the question type
        #   stage 2 (QUESTION_STAGE_SECONDS): show the question, answers still hidden
        #   stage 3: answering opens (scoring clock starts at question_started_at)
        now = time.time()
        s.question_reveal_at = now + TYPE_STAGE_SECONDS
        s.question_started_at = s.question_reveal_at + QUESTION_STAGE_SECONDS
        s.touch()

        # Prepare shuffled right column for matching
        if slide.type == "multiple_matching":
            rights = [p.right for p in slide.pairs]
            random.shuffle(rights)
            s.shuffled_right = rights
        else:
            s.shuffled_right = None

        started_at_ms = int(s.question_started_at * 1000)
        reveal_at_ms = int(s.question_reveal_at * 1000)
        safe = self._safe_slide(slide, "player")
        if slide.type == "multiple_matching":
            safe["left_items"] = [p.left for p in slide.pairs]
            safe["right_items"] = s.shuffled_right

        await self._broadcast_all(s, {
            "type": "question_start",
            "slide_index": s.current_index,
            "slide": safe,
            "started_at": started_at_ms,
            "reveal_question_at": reveal_at_ms,
            "time_limit": slide.time_limit,
        })

    async def handle_reveal(self, code: str):
        s = self._sessions[code]
        if s.phase != QuestionPhase.ACTIVE:
            return
        s.phase = QuestionPhase.REVEALED
        slide = s.current_slide()
        s.touch()

        # Calculate scores (base points + speed bonus + streak bonus)
        score_deltas: dict[str, int] = {}
        is_correct_map: dict[str, bool] = {}
        streak_map: dict[str, int] = {}
        bonus_map: dict[str, int] = {}
        for nickname, answer in s.answers.items():
            # Per-player elapsed time: how long *this* player took, not the reveal time.
            answered_at = s.answer_times.get(nickname, time.time())
            elapsed = max(0.0, answered_at - (s.question_started_at or answered_at))
            pts, correct = calculate_score(slide, answer, elapsed, s.shuffled_right)
            player = s.players[nickname]
            if correct:
                player.streak += 1
                bonus = streak_bonus(player.streak)
            else:
                player.streak = 0
                bonus = 0
            gained = pts + bonus
            player.score += gained
            score_deltas[nickname] = gained  # includes streak bonus — don't re-add client side
            is_correct_map[nickname] = correct
            streak_map[nickname] = player.streak
            bonus_map[nickname] = bonus

        # Players who didn't answer break their streak too
        for nickname, player in s.players.items():
            if nickname not in s.answers:
                player.streak = 0

        # Build answer distribution for display
        distribution = self._build_distribution(slide, s.answers, s.shuffled_right)

        # Leaderboard + per-player rank
        leaderboard, rank_map = self._ranked(s)

        # Correct value for reveal
        correct_value = self._correct_value(slide, s.shuffled_right)

        # Notify each player individually
        for nickname, ws in s.player_ws.items():
            delta = score_deltas.get(nickname, 0)
            correct = is_correct_map.get(nickname, False)
            my_answer = s.answers.get(nickname)
            rank, total = rank_map.get(nickname, (len(leaderboard), len(leaderboard)))
            await self._send(ws, {
                "type": "reveal",
                "correct": correct_value,
                "your_answer": my_answer,
                "is_correct": correct,
                "score_delta": delta,
                "total_score": s.players[nickname].score,
                "streak": streak_map.get(nickname, 0),
                "streak_bonus": bonus_map.get(nickname, 0),
                "rank": rank,
                "total_players": total,
            })

        # Notify presenter and display
        reveal_msg = {
            "type": "question_revealed",
            "correct": correct_value,
            "distribution": distribution,
            "leaderboard": leaderboard,
        }
        await self._broadcast_presenter(s, reveal_msg)
        await self._broadcast_display(s, reveal_msg)

    async def handle_show_leaderboard(self, code: str):
        s = self._sessions[code]
        leaderboard, rank_map = self._ranked(s)
        # Big screen shows the standings (top players); players only see their own rank
        msg = {"type": "leaderboard", "standings": leaderboard}
        await self._broadcast_presenter(s, msg)
        await self._broadcast_display(s, msg)
        for nickname, ws in s.player_ws.items():
            rank, total = rank_map.get(nickname, (len(leaderboard), len(leaderboard)))
            await self._send(ws, {
                "type": "your_rank",
                "rank": rank,
                "total": total,
                "score": s.players[nickname].score if nickname in s.players else 0,
            })

    async def handle_player_answer(self, code: str, nickname: str, answer):
        s = self._sessions[code]
        if s.phase != QuestionPhase.ACTIVE:
            return
        if nickname in s.answers:
            return  # already answered
        s.answers[nickname] = answer
        s.answer_times[nickname] = time.time()  # per-player timestamp drives the speed bonus
        s.touch()

        # Ack to player
        ws = s.player_ws.get(nickname)
        if ws:
            await self._send(ws, {"type": "answer_accepted"})

        # Progress to presenter
        await self._broadcast_presenter(s, {
            "type": "answer_update",
            "count": len(s.answers),
            "total": len(s.players),
        })

        # Auto-reveal when everyone answered
        if len(s.answers) >= len(s.players) and s.players:
            await self.handle_reveal(code)

    # ------------------------------------------------------------------
    # Broadcast helpers
    # ------------------------------------------------------------------

    async def _send(self, ws: WebSocket, data: dict):
        try:
            await ws.send_json(data)
        except Exception:
            pass

    async def _broadcast_all(self, s: SessionData, msg: dict):
        await self._broadcast_presenter(s, msg)
        await self._broadcast_display(s, msg)
        await self._broadcast_players(s, msg)

    async def _broadcast_presenter(self, s: SessionData, msg: dict):
        if s.presenter_ws:
            await self._send(s.presenter_ws, msg)

    async def _broadcast_display(self, s: SessionData, msg: dict):
        for ws in list(s.display_ws_list):
            await self._send(ws, msg)

    async def _broadcast_players(self, s: SessionData, msg: dict):
        for ws in list(s.player_ws.values()):
            await self._send(ws, msg)

    async def _broadcast_slide_changed(self, s: SessionData):
        slide = s.current_slide()
        msg = {
            "type": "slide_changed",
            "slide_index": s.current_index,
            "slide": self._safe_slide(slide, "player"),
            "total_slides": len(s.presentation.slides),
        }
        await self._broadcast_all(s, msg)
        # Presenter gets full slide
        if s.presenter_ws:
            full_msg = {**msg, "slide": slide.model_dump()}
            await self._send(s.presenter_ws, full_msg)

    # ------------------------------------------------------------------
    # Snapshot / safe helpers
    # ------------------------------------------------------------------

    def _ranked(self, s: SessionData) -> tuple[list[dict], dict[str, tuple[int, int]]]:
        """Return (sorted leaderboard dicts, nickname -> (rank, total))."""
        leaderboard = sorted(
            [p.model_dump() for p in s.players.values()],
            key=lambda x: x["score"], reverse=True,
        )
        total = len(leaderboard)
        rank_map = {row["nickname"]: (i + 1, total) for i, row in enumerate(leaderboard)}
        return leaderboard, rank_map

    def _state_snapshot(self, s: SessionData, role: str) -> dict:
        slide = s.current_slide()
        slide_dict = slide.model_dump() if role == "presenter" else self._safe_slide(slide, role)
        if slide.type == "multiple_matching" and role in ("player", "display") and s.shuffled_right:
            slide_dict["left_items"] = [p.left for p in slide.pairs]
            slide_dict["right_items"] = s.shuffled_right
        return {
            "type": "session_state",
            "code": s.code,
            "title": s.presentation.title,
            "slide_index": s.current_index,
            "total_slides": len(s.presentation.slides),
            "slide": slide_dict,
            "phase": s.phase.value,
            "started": s.started,
            "finished": s.finished,
            "players": [p.model_dump() for p in s.players.values()],
            "answer_count": len(s.answers),
            "question_started_at": int(s.question_started_at * 1000) if s.question_started_at else None,
            "reveal_question_at": int(s.question_reveal_at * 1000) if s.question_reveal_at else None,
            "time_limit": getattr(slide, "time_limit", None),
        }

    def _safe_slide(self, slide: AnySlide, role: str) -> dict:
        return safe_slide_dict(slide, role)

    def _correct_value(self, slide: AnySlide, shuffled_right: list[str] | None):
        if slide.type == "true_false":
            return slide.correct
        if slide.type in ("single_choice", "multiple_choice"):
            return slide.correct
        if slide.type == "number_slider":
            return slide.correct
        if slide.type == "multiple_matching":
            # return pairs as [[left_idx, right_idx_in_shuffled], ...]
            if not shuffled_right:
                return []
            result = []
            for li, pair in enumerate(slide.pairs):
                try:
                    ri = shuffled_right.index(pair.right)
                    result.append([li, ri])
                except ValueError:
                    pass
            return result
        return None

    def _build_distribution(self, slide: AnySlide, answers: dict, shuffled_right) -> dict:
        if slide.type == "true_false":
            dist = {"true": 0, "false": 0}
            for a in answers.values():
                key = "true" if a else "false"
                dist[key] += 1
            return dist
        if slide.type in ("single_choice", "multiple_choice"):
            dist = {str(i): 0 for i in range(len(slide.options))}
            for a in answers.values():
                idxs = [a] if isinstance(a, int) else (a or [])
                for idx in idxs:
                    dist[str(idx)] = dist.get(str(idx), 0) + 1
            return dist
        if slide.type == "number_slider":
            return {"values": list(answers.values()), "correct": slide.correct}
        if slide.type == "multiple_matching":
            return {"total": len(answers)}
        return {}


# Singleton
manager = SessionManager()
