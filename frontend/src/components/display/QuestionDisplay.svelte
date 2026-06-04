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

  // For matching we show the items on the big screen too (so the back row can read
  // them), with each column shuffled so the correct pairs never line up in a row.
  function shuffle(arr) {
    const a = [...(arr || [])];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }
  // Reshuffle only when the question changes — not on every clock tick.
  let matchLeft = [];
  let matchRight = [];
  let _matchKey = null;
  $: {
    const key = slide?.type === 'multiple_matching' ? (slide?.question ?? '') : null;
    if (key !== _matchKey) {
      _matchKey = key;
      matchLeft = shuffle(slide?.left_items);
      matchRight = shuffle(slide?.right_items);
    }
  }
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
        <div class="match-cols">
          <div class="match-col">
            {#each matchLeft as item}
              <div class="match-item left">{item}</div>
            {/each}
          </div>
          <div class="match-col">
            {#each matchRight as item}
              <div class="match-item right">{item}</div>
            {/each}
          </div>
        </div>
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
    font-size: clamp(2.4rem, 5.2vw, 5rem);
    font-weight: 800;
    text-align: center;
    color: #fff;
    max-width: 1400px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.4);
  }
  .options { display: grid; gap: 1.4rem; width: 100%; max-width: 1300px; }
  .options.tf { grid-template-columns: 1fr 1fr; }
  .options.grid { grid-template-columns: repeat(var(--cols), 1fr); }
  .opt {
    padding: 1.8rem 2rem;
    border-radius: 18px;
    font-size: clamp(1.6rem, 3.4vw, 3rem);
    font-weight: 800;
    color: #fff;
    text-align: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.35);
  }
  .slider-hint { text-align: center; }
  .range { font-size: clamp(1.8rem, 3.5vw, 3rem); color: var(--text); font-weight: 700; }
  .slider-bar { margin-top: 1.4rem; width: min(70vw, 640px); height: 28px; background: rgba(255,255,255,0.2); border-radius: 14px; }
  .bar-track { height: 100%; width: 0%; background: var(--primary); border-radius: 14px; animation: bar-track-fill 5s ease infinite; }

  /* Matching items shown on the big screen — two independently shuffled columns */
  .match-cols {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(1.5rem, 5vw, 5rem);
    width: 100%;
    max-width: 1300px;
  }
  .match-col { display: flex; flex-direction: column; gap: 1.2rem; }
  .match-item {
    padding: 1.3rem 1.6rem;
    border-radius: 16px;
    font-size: clamp(1.4rem, 3vw, 2.6rem);
    font-weight: 700;
    color: #fff;
    text-align: center;
    word-break: break-word;
    box-shadow: 0 6px 18px rgba(0,0,0,0.3);
  }
  .match-item.left { background: rgba(124, 58, 237, 0.55); }
  .match-item.right { background: rgba(19, 104, 206, 0.55); }
  .match-hint { font-size: clamp(1.4rem, 2.6vw, 2.2rem); color: var(--text-dim); }
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
