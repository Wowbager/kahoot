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

  function toLabel(items, index) {
    if (!Array.isArray(items)) return `Item ${index + 1}`;
    return items[index] ?? `Item ${index + 1}`;
  }

  function buildMatchingPairs() {
    if (slide?.type !== 'multiple_matching' || !Array.isArray(correct) || !correct.length) return [];
    const leftItems = slide?.left_items ?? [];
    const rightItems = slide?.right_items ?? [];

    return correct
      .filter(pair => Array.isArray(pair) && pair.length >= 2)
      .map(([leftIdx, rightIdx]) => ({
        leftIdx,
        rightIdx,
        left: toLabel(leftItems, leftIdx),
        right: toLabel(rightItems, rightIdx),
      }))
      .sort((a, b) => a.leftIdx - b.leftIdx);
  }

  $: maxVal = getMax(distribution);
  $: matchingPairs = buildMatchingPairs();
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
    <div class="match-header">
      <div class="match-title">Correct pairs</div>
      <p>{distribution?.total ?? 0} players submitted answers</p>
    </div>

    {#if matchingPairs.length}
      <div class="pairs">
        {#each matchingPairs as pair}
          <div class="pair-row">
            <div class="pair-left">{pair.left}</div>
            <div class="pair-arrow">→</div>
            <div class="pair-right">{pair.right}</div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="pairs empty">No matching pairs available</div>
    {/if}
  </div>
{/if}

<style>
  .chart { display: flex; flex-direction: column; gap: 1.3rem; width: 100%; max-width: 1200px; }
  .bar-row { display: flex; align-items: center; gap: 1.4rem; }
  .label {
    min-width: clamp(220px, 22vw, 360px);
    padding: 1rem 1.4rem;
    border-radius: 12px;
    color: #fff;
    font-weight: 800;
    font-size: clamp(1.3rem, 2.6vw, 2.2rem);
    text-align: center;
  }
  .bar-wrap { flex: 1; display: flex; align-items: center; gap: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 10px; padding: 6px; }
  .bar { height: clamp(44px, 5vw, 64px); border-radius: 8px; transition: width 0.5s ease; min-width: 6px; }
  .count { font-weight: 800; color: #fff; min-width: 3rem; font-size: clamp(1.4rem, 2.6vw, 2.2rem); }
  .slider-result, .match-result { text-align: center; color: #ccc; }
  .correct-value { font-size: clamp(2rem, 4vw, 3.2rem); color: #fff; margin-bottom: 1.4rem; font-weight: 700; }
  .correct-value strong { color: gold; }
  .answers-list { display: flex; flex-wrap: wrap; gap: 0.7rem; justify-content: center; }
  .val-chip { background: rgba(255,255,255,0.1); padding: 0.5rem 1.1rem; border-radius: 24px; font-size: clamp(1.1rem, 2vw, 1.6rem); }
  .match-result {
    width: min(100%, 1100px);
    margin: 0 auto;
    padding: 1.8rem;
    border-radius: 22px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.2);
  }
  .match-header {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 1.4rem;
  }
  .match-title {
    font-family: var(--font-display);
    font-size: clamp(1.8rem, 3.5vw, 2.8rem);
    font-weight: 800;
    color: #fff;
  }
  .match-header p {
    margin: 0;
    color: var(--text-dim);
    font-size: clamp(1.1rem, 2vw, 1.5rem);
  }
  .pairs {
    display: grid;
    gap: 1rem;
  }
  .pair-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    align-items: center;
    gap: 1rem;
    padding: 1.1rem 1.4rem;
    border-radius: 16px;
    background: rgba(255,255,255,0.08);
  }
  .pair-left, .pair-right {
    font-weight: 800;
    color: #fff;
    word-break: break-word;
    font-size: clamp(1.3rem, 2.6vw, 2.2rem);
  }
  .pair-arrow {
    color: gold;
    font-size: clamp(1.6rem, 3vw, 2.4rem);
    font-weight: 900;
  }
  .pairs.empty {
    padding: 1.1rem 1.4rem;
    color: var(--text-faint);
    border: 1px dashed rgba(255,255,255,0.18);
    border-radius: 16px;
    font-size: 1.3rem;
  }
</style>
