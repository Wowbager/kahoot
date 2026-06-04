from __future__ import annotations
from models import (
    AnySlide, TrueFalseSlide, SingleChoiceSlide, MultipleChoiceSlide,
    NumberSliderSlide, MultipleMatchingSlide,
)

MAX_POINTS = 1000
SPEED_BONUS = 1000

# Answer-streak bonus: nothing for the first correct answer, then +STREAK_STEP
# per consecutive correct answer, capped at STREAK_CAP steps (Kahoot-like).
STREAK_STEP = 100
STREAK_CAP = 5


def streak_bonus(streak: int) -> int:
    """Bonus points for a current streak of `streak` consecutive correct answers."""
    if streak <= 1:
        return 0
    return min(streak - 1, STREAK_CAP) * STREAK_STEP


def _speed_multiplier(elapsed: float, time_limit: int) -> float:
    if time_limit <= 0:
        return 1.0
    remaining = max(0.0, time_limit - elapsed)
    return min(1.0, remaining / time_limit)


def calculate_score(
    slide: AnySlide,
    answer,
    elapsed: float,
    shuffled_right: list[str] | None = None,
) -> tuple[int, bool]:
    """Return (points_earned, is_correct)."""
    sm = _speed_multiplier(elapsed, getattr(slide, "time_limit", 30))

    if isinstance(slide, TrueFalseSlide):
        correct = answer == slide.correct
        pts = round((MAX_POINTS + SPEED_BONUS * sm)) if correct else 0
        return pts, correct

    if isinstance(slide, SingleChoiceSlide):
        correct = isinstance(answer, int) and answer in slide.correct
        pts = round((MAX_POINTS + SPEED_BONUS * sm)) if correct else 0
        return pts, correct

    if isinstance(slide, MultipleChoiceSlide):
        submitted = set(answer) if isinstance(answer, list) else set()
        correct_set = set(slide.correct)
        if submitted == correct_set:
            pts = round((MAX_POINTS + SPEED_BONUS * sm))
            return pts, True
        # partial credit: intersection minus wrong selections
        hit = len(submitted & correct_set)
        wrong = len(submitted - correct_set)
        partial = max(0, hit - wrong)
        ratio = partial / len(correct_set) if correct_set else 0
        pts = round(MAX_POINTS * ratio * sm)
        return pts, submitted == correct_set

    if isinstance(slide, NumberSliderSlide):
        span = slide.max - slide.min
        if span == 0:
            correct = answer == slide.correct
            return (round(MAX_POINTS + SPEED_BONUS * sm) if correct else 0), correct
        proximity = max(0.0, 1 - abs(answer - slide.correct) / span)
        pts = round((MAX_POINTS * proximity + SPEED_BONUS * sm * proximity))
        is_exact = answer == slide.correct
        return pts, is_exact

    if isinstance(slide, MultipleMatchingSlide):
        # Players may now pair ANY two cards together (left-left, right-right or
        # left-right), so each submitted pair is a list of two [side, index] cards.
        # A pair only scores when it joins a left card to its matching right card.
        if shuffled_right is None:
            return 0, False
        correct_right_order = [p.right for p in slide.pairs]  # expected right text per left index
        n = len(slide.pairs)
        correct_pairs = 0
        for pair in (answer or []):
            sides = _parse_match_pair(pair)
            if sides is None:
                continue
            left_idx, right_idx = sides
            if 0 <= left_idx < n and 0 <= right_idx < len(shuffled_right):
                if shuffled_right[right_idx] == correct_right_order[left_idx]:
                    correct_pairs += 1
        all_correct = correct_pairs == n
        ratio = correct_pairs / n if n else 0
        pts = round(MAX_POINTS * ratio + SPEED_BONUS * sm * ratio)
        return pts, all_correct

    return 0, False


def _parse_match_pair(pair) -> tuple[int, int] | None:
    """Extract (left_index, right_index) from a submitted [[side, idx], [side, idx]] pair.

    Returns None unless the pair joins exactly one left card to one right card
    (same-side pairings are always wrong and score nothing).
    """
    if not isinstance(pair, (list, tuple)) or len(pair) != 2:
        return None
    by_side: dict[str, int] = {}
    for card in pair:
        if not isinstance(card, (list, tuple)) or len(card) != 2:
            return None
        side, idx = card
        if side not in ("left", "right") or not isinstance(idx, int):
            return None
        by_side[side] = idx
    if "left" not in by_side or "right" not in by_side:
        return None
    return by_side["left"], by_side["right"]
