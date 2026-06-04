<script>
  import { onMount, onDestroy } from 'svelte';
  import Timer from '../Timer.svelte';
  export let slide = null;
  export let startedAt = null;
  export let revealAt = null;
  export let timeLimit = 30;
  export let answersOpen = false;

  const COLORS = ['#e84393', '#1368ce', '#ffa602', '#26890c'];
  const SHAPES = ['▲', '◆', '●', '■'];
  const TYPE_LABELS = {
    true_false: 'True / False',
    single_choice: 'Single Choice',
    multiple_choice: 'Multiple Choice',
    number_slider: 'Number Slider',
    multiple_matching: 'Matching',
  };

  let _now = Date.now();
  let _tick;
  onMount(() => { _tick = setInterval(() => { _now = Date.now(); }, 100); });
  onDestroy(() => clearInterval(_tick));

  $: countdown = (!answersOpen && startedAt && _now < startedAt)
    ? Math.ceil((startedAt - _now) / 1000)
    : 0;
  // In preview until the server opens answering.
  $: isPreview = !answersOpen;
  // Stage 1: only the question type. Stage 2: question text but no answers.
  $: showTypeOnly = isPreview && revealAt && _now < revealAt;
  // Answers are only ever shown once answering has opened (never during preview).
  $: showAnswers = answersOpen;
</script>

<div class="wrap">
  {#if showTypeOnly}
    <div class="type-stage">
      <div class="type-label">Question type</div>
      <div class="type-badge">{TYPE_LABELS[slide?.type] ?? slide?.type}</div>
    </div>
  {:else}
    <div class="question">{slide?.question ?? ''}</div>

    {#if showAnswers}
      {#if slide?.type === 'true_false'}
        <div class="options tf">
          <div class="opt" style="background:#26890c">✓ True</div>
          <div class="opt" style="background:#e84393">✗ False</div>
        </div>
      {:else if slide?.type === 'single_choice' || slide?.type === 'multiple_choice'}
        <div class="options grid" style="--cols:{Math.min(slide.options?.length ?? 2, 2)}">
          {#each (slide.options ?? []) as opt, i}
            <div class="opt" style="background:{COLORS[i % 4]}">{SHAPES[i % 4]} {opt}</div>
          {/each}
        </div>
      {:else if slide?.type === 'number_slider'}
        <div class="slider-hint">
          <span class="range">Range: {slide.min} – {slide.max}</span>
          <div class="slider-bar">
            <div class="bar-track"></div>
          </div>
        </div>
      {:else if slide?.type === 'multiple_matching'}
        <div class="match-hint">Match the pairs on your phone</div>
      {/if}
    {/if}
  {/if}

  <div class="timer-wrap">
    <Timer {timeLimit} {startedAt} />
  </div>

  {#if isPreview && countdown > 0}
    <!-- Plain countdown — never blurs the content, so the question stays readable in stage 2 -->
    <div class="cd-num">{countdown}</div>
  {/if}
</div>

<style>
  .wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 2rem;
    gap: 2rem;
    position: relative;
  }
  .question {
    font-family: var(--font-display);
    font-size: clamp(1.8rem, 4vw, 3.5rem);
    font-weight: 700;
    text-align: center;
    color: #fff;
    max-width: 1000px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.4);
  }
  .options { display: grid; gap: 1rem; width: 100%; max-width: 800px; }
  .options.tf { grid-template-columns: 1fr 1fr; }
  .options.grid { grid-template-columns: repeat(var(--cols), 1fr); }
  .opt {
    padding: 1.2rem 1.5rem;
    border-radius: 12px;
    font-size: clamp(1rem, 2.5vw, 1.6rem);
    font-weight: 700;
    color: #fff;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }
  .slider-hint { text-align: center; }
  .range { font-size: 1.4rem; color: var(--text-dim); }
  .slider-bar { margin-top: 1rem; width: 400px; height: 20px; background: rgba(255,255,255,0.2); border-radius: 10px; }
  .bar-track { height: 100%; width: 0%; background: var(--primary); border-radius: 10px; animation: bar-track-fill 5s ease infinite; }
  .match-hint { font-size: 1.5rem; color: var(--text-dim); }
  .timer-wrap { position: absolute; top: 2rem; right: 2rem; }

  /* Stage 1: question type only */
  .type-stage {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }
  .type-label {
    font-size: clamp(1rem, 2vw, 1.5rem);
    color: var(--text-faint);
    text-transform: uppercase;
    letter-spacing: 4px;
  }
  .type-badge {
    font-family: var(--font-display);
    font-size: clamp(2.5rem, 8vw, 6rem);
    font-weight: 900;
    color: #fff;
    background: rgba(124, 58, 237, 0.45);
    padding: 1rem 3rem;
    border-radius: var(--radius-pill, 999px);
    text-shadow: 0 2px 12px rgba(0,0,0,0.4);
    animation: cdpop 0.4s ease;
  }

  /* Plain (non-blurring) preview countdown */
  .cd-num {
    font-family: var(--font-display);
    font-size: clamp(4rem, 12vw, 9rem);
    font-weight: 900;
    color: #fff;
    opacity: 0.85;
    text-shadow: 0 4px 30px rgba(0,0,0,0.5);
    animation: cdpop 0.4s ease;
    line-height: 1;
  }
  @keyframes cdpop {
    0%   { transform: scale(1.3); opacity: 0; }
    100% { transform: scale(1);   opacity: 0.85; }
  }

  @keyframes bar-track-fill {
    0% {
      width: 10%;
    }
    50% {
      width: 100%;
    }
    100% {
      width: 10%;
    }
  }
</style>
