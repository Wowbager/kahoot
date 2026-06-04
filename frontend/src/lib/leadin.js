// Shared question lead-in timing, used by both the player view (Play.svelte) and
// the big-screen display (QuestionDisplay.svelte) so they stay perfectly in sync.
//
// When a question starts the backend sets question_started_at = now + 6s (the moment
// answering opens). The lead-in is split into two visible stages before that instant:
//   Stage 1 (first 2s):  show the question TYPE only
//   Stage 2 (next 4s):   show the question TEXT only — no answers, not even blurred
//   Stage 3 (at open):   show question + answers, answering is live
//
// LEAD_IN_MS must match the `+ 6` delay in backend/session.py handle_start_question.
export const LEAD_IN_MS = 6000;
export const STAGE1_MS = 2000;

// Returns 1 | 2 | 3 given the answering-open timestamp (ms) and current time (ms).
export function leadInStage(startedAt, now) {
  if (!startedAt) return 3;
  const remaining = startedAt - now; // ms until answering opens
  if (remaining <= 0) return 3;
  if (remaining > LEAD_IN_MS - STAGE1_MS) return 1;
  return 2;
}

export const TYPE_LABELS = {
  true_false: 'True / False',
  single_choice: 'Single Choice',
  multiple_choice: 'Multiple Choice',
  number_slider: 'Number Slider',
  multiple_matching: 'Matching',
};
