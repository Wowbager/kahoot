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
        # answer is a list of 2-token pairs, each token "L<i>" (left col item i) or
        # "R<j>" (shuffled right col item j). Players can pair ANY two cards — only a
        # genuine left/right correspondence scores; same-side pairs always score 0.
        if shuffled_right is None:
            return 0, False
        correct_right_order = [p.right for p in slide.pairs]
        correct_set = set()
        for i, pair in enumerate(slide.pairs):
            try:
                j = shuffled_right.index(pair.right)
            except ValueError:
                continue
            correct_set.add(frozenset({f"L{i}", f"R{j}"}))

        seen = set()
        correct_pairs = 0
        for tokens in (answer or []):
            if not isinstance(tokens, (list, tuple)) or len(tokens) != 2:
                continue
            a, b = str(tokens[0]), str(tokens[1])
            key = frozenset({a, b})
            if len(key) != 2:
                continue  # malformed / self-pair
            if a in seen or b in seen:
                continue  # a card can only belong to one pair
            seen.add(a)
            seen.add(b)
            if key in correct_set:
                correct_pairs += 1

        n = len(slide.pairs)
        all_correct = n > 0 and correct_pairs == n
        pts = round(MAX_POINTS * correct_pairs / n) if n else 0
        return pts, all_correct

    return 0, False
