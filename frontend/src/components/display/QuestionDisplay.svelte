<script>
  import { onMount, onDestroy } from 'svelte';
  import Timer from '../Timer.svelte';
  import { leadInStage, TYPE_LABELS } from '../../lib/leadin.js';
  export let slide = null;
  export let startedAt = null;
  export let timeLimit = 30;

  const COLORS = ['#e84393', '#1368ce', '#ffa602', '#26890c'];
  const SHAPES = ['▲', '◆', '●', '■'];

  let _now = Date.now();
  let _tick;
  onMount(() => { _tick = setInterval(() => { _now = Date.now(); }, 100); });
  onDestroy(() => clearInterval(_tick));

  // 1 = type only · 2 = question text only (no answers) · 3 = question + answers, live
  $: stage = leadInStage(startedAt, _now);
  $: countdown = (startedAt && _now < startedAt) ? Math.ceil((startedAt - _now) / 1000) : 0;
</script>

<div class="wrap">
  {#if stage === 1}
    <!-- Stage 1: announce the question type only -->
    <div class="type-stage">
      <div class="type-badge">{TYPE_LABELS[slide?.type] ?? slide?.type}</div>
      <div class="get-ready">Get ready…</div>
    </div>
  {:else}
    <!-- Stage 2 & 3: question text (answers appear only in stage 3) -->
    <div class="question">{slide?.question ?? ''}</div>

    {#if stage === 3}
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

      <div class="timer-wrap">
        <Timer {timeLimit} {startedAt} />
      </div>
    {:else}
      <!-- Stage 2: quiet countdown, no answers shown -->
      <div class="cd-num">{countdown}</div>
    {/if}
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
  .type-stage {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.6rem;
  }
  .type-badge {
    background: linear-gradient(135deg, var(--primary), var(--primary-700));
    color: #fff;
    font-family: var(--font-display);
    font-size: clamp(2rem, 6vw, 4rem);
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 4px;
    padding: 1rem 2.4rem;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    animation: badgeIn 0.5s cubic-bezier(0.2, 1.2, 0.4, 1) both;
  }
  .get-ready { font-size: 1.4rem; color: var(--text-faint); text-transform: uppercase; letter-spacing: 4px; }
  @keyframes badgeIn { 0% { transform: scale(0.6); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

  .question {
    font-family: var(--font-display);
    font-size: clamp(1.8rem, 4vw, 3.5rem);
    font-weight: 700;
    text-align: center;
    color: #fff;
    max-width: 1000px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.4);
  }
  .options { display: grid; gap: 1rem; width: 100%; max-width: 800px; animation: fadeUp 0.35s ease both; }
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
  @keyframes fadeUp { from { transform: translateY(16px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
  .slider-hint { text-align: center; animation: fadeUp 0.35s ease both; }
  .range { font-size: 1.4rem; color: var(--text-dim); }
  .slider-bar { margin-top: 1rem; width: 400px; height: 20px; background: rgba(255,255,255,0.2); border-radius: 10px; }
  .bar-track { height: 100%; width: 40%; background: var(--primary); border-radius: 10px; }
  .match-hint { font-size: 1.5rem; color: var(--text-dim); animation: fadeUp 0.35s ease both; }
  .timer-wrap { position: absolute; top: 2rem; right: 2rem; }

  .cd-num {
    font-family: var(--font-display);
    font-size: clamp(6rem, 16vw, 12rem);
    font-weight: 900;
    color: var(--primary);
    line-height: 1;
    text-shadow: 0 4px 30px rgba(0,0,0,0.4);
    animation: cdpop 0.4s ease;
  }
  @keyframes cdpop {
    0%   { transform: scale(1.3); opacity: 0; }
    100% { transform: scale(1);   opacity: 1; }
  }

  @media (prefers-reduced-motion: reduce) {
    .type-badge, .options, .slider-hint, .match-hint, .cd-num { animation: none !important; }
  }
</style>
