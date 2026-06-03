from __future__ import annotations
from enum import Enum
from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Slide types
# ---------------------------------------------------------------------------

class PresentationSlide(BaseModel):
    type: Literal["presentation"]
    content: str  # markdown


class TrueFalseSlide(BaseModel):
    type: Literal["true_false"]
    question: str
    correct: bool
    time_limit: int = 20


class SingleChoiceSlide(BaseModel):
    type: Literal["single_choice"]
    question: str
    options: list[str]
    correct: list[int]
    time_limit: int = 30


class MultipleChoiceSlide(BaseModel):
    type: Literal["multiple_choice"]
    question: str
    options: list[str]
    correct: list[int]
    time_limit: int = 30


class NumberSliderSlide(BaseModel):
    type: Literal["number_slider"]
    question: str
    min: float
    max: float
    correct: float
    time_limit: int = 30


class MatchPair(BaseModel):
    left: str
    right: str


class MultipleMatchingSlide(BaseModel):
    type: Literal["multiple_matching"]
    question: str
    pairs: list[MatchPair]  # always 3 pairs
    time_limit: int = 45


AnySlide = Annotated[
    Union[
        PresentationSlide,
        TrueFalseSlide,
        SingleChoiceSlide,
        MultipleChoiceSlide,
        NumberSliderSlide,
        MultipleMatchingSlide,
    ],
    Field(discriminator="type"),
]


class Presentation(BaseModel):
    title: str
    slides: list[AnySlide]


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

class QuestionPhase(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    REVEALED = "revealed"
    FINISHED = "finished"


class Player(BaseModel):
    nickname: str
    score: int = 0
    streak: int = 0  # consecutive correct answers


# ---------------------------------------------------------------------------
# Safe slide helpers (strip correct answers before sending to players/display)
# ---------------------------------------------------------------------------

QUESTION_TYPES = {
    "true_false", "single_choice", "multiple_choice",
    "number_slider", "multiple_matching",
}


def safe_slide_dict(slide: AnySlide, role: str) -> dict:
    d = slide.model_dump()
    if role in ("player", "display"):
        d.pop("correct", None)
        if d.get("type") == "multiple_matching":
            # send only the items, not in their correct pairing order
            # right-column items are shuffled server-side; pairs list removed
            d.pop("pairs", None)
    return d


def time_limit_for(slide: AnySlide) -> int:
    return getattr(slide, "time_limit", 0)
