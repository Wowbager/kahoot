from __future__ import annotations
from models import (
    AnySlide, TrueFalseSlide, SingleChoiceSlide, MultipleChoiceSlide,
    NumberSliderSlide, MultipleMatchingSlide,
)

MAX_POINTS = 1000
SPEED_BONUS = 1000


def _speed_multiplier(elapsed: float, time_limit: int) -> float:
    if time_limit <= 0:
        return 1.0
    remaining = max(0.0, time_limit - elapsed)
    return remaining / time_limit


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
        # answer is list of [left_index, right_index] pairs (indices into shuffled right col)
        correct_right_order = [p.right for p in slide.pairs]
        if shuffled_right is None:
            return 0, False
        correct_pairs = 0
        for left_idx, right_idx in (answer or []):
            if 0 <= left_idx < len(slide.pairs) and 0 <= right_idx < len(shuffled_right):
                if shuffled_right[right_idx] == correct_right_order[left_idx]:
                    correct_pairs += 1
        all_correct = correct_pairs == len(slide.pairs)
        pts = round(MAX_POINTS * correct_pairs / len(slide.pairs)) if slide.pairs else 0
        return pts, all_correct

    return 0, False
