<script>
  export let slide = null;
  export let distribution = null;
  export let correct = null;

  const COLORS = ['#e84393', '#1368ce', '#ffa602', '#26890c'];
  const SHAPES = ['▲', '◆', '●', '■'];

  function getMax(dist) {
    if (!dist) return 1;
    return Math.max(1, ...Object.values(dist).map(v => typeof v === 'number' ? v : 0));
  }

  $: maxVal = getMax(distribution);
</script>

{#if slide?.type === 'single_choice' || slide?.type === 'multiple_choice'}
  <div class="chart">
    {#each (slide.options ?? []) as opt, i}
      {@const count = distribution?.[String(i)] ?? 0}
      {@const isCorrect = Array.isArray(correct) && correct.includes(i)}
      <div class="bar-row">
        <div class="label" style="background:{COLORS[i%4]};{isCorrect ? 'outline:3px solid gold' : ''}">{SHAPES[i%4]} {opt}</div>
        <div class="bar-wrap">
          <div class="bar" style="width:{(count/maxVal)*100}%;background:{isCorrect ? 'gold' : COLORS[i%4]}"></div>
          <span class="count">{count}</span>
        </div>
      </div>
    {/each}
  </div>

{:else if slide?.type === 'true_false'}
  <div class="chart">
    {#each [['true', '✓ True', '#26890c'], ['false', '✗ False', '#e84393']] as [key, label, color]}
      {@const count = distribution?.[key] ?? 0}
      {@const isCorrect = (key === 'true') === correct}
      <div class="bar-row">
        <div class="label" style="background:{color};{isCorrect ? 'outline:3px solid gold' : ''}">{label}</div>
        <div class="bar-wrap">
          <div class="bar" style="width:{(count/maxVal)*100}%;background:{isCorrect ? 'gold' : color}"></div>
          <span class="count">{count}</span>
        </div>
      </div>
    {/each}
  </div>

{:else if slide?.type === 'number_slider'}
  <div class="slider-result">
    <div class="correct-value">Correct answer: <strong>{correct}</strong></div>
    <div class="answers-list">
      {#each (distribution?.values ?? []) as v}
        <span class="val-chip">{v}</span>
      {/each}
    </div>
  </div>

{:else if slide?.type === 'multiple_matching'}
  <div class="match-result">
    <p>{distribution?.total ?? 0} players submitted answers</p>
  </div>
{/if}

<style>
  .chart { display: flex; flex-direction: column; gap: 1rem; width: 100%; max-width: 800px; }
  .bar-row { display: flex; align-items: center; gap: 1rem; }
  .label {
    min-width: 180px;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    color: #fff;
    font-weight: 700;
    font-size: 0.95rem;
    text-align: center;
  }
  .bar-wrap { flex: 1; display: flex; align-items: center; gap: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 6px; padding: 4px; }
  .bar { height: 36px; border-radius: 4px; transition: width 0.5s ease; min-width: 4px; }
  .count { font-weight: 700; color: #fff; min-width: 2rem; }
  .slider-result, .match-result { text-align: center; color: #ccc; }
  .correct-value { font-size: 1.5rem; color: #fff; margin-bottom: 1rem; }
  .correct-value strong { color: gold; }
  .answers-list { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; }
  .val-chip { background: rgba(255,255,255,0.1); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem; }
</style>
