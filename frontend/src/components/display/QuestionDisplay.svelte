<script>
  import Timer from '../Timer.svelte';
  export let slide = null;
  export let startedAt = null;
  export let timeLimit = 30;

  const COLORS = ['#e84393', '#1368ce', '#ffa602', '#26890c'];
  const SHAPES = ['▲', '◆', '●', '■'];
</script>

<div class="wrap">
  <div class="question">{slide?.question ?? ''}</div>

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
  .bar-track { height: 100%; width: 40%; background: var(--primary); border-radius: 10px; }
  .match-hint { font-size: 1.5rem; color: var(--text-dim); }
  .timer-wrap { position: absolute; top: 2rem; right: 2rem; }
</style>
