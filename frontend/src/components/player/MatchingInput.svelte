<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let slide = null;
  export let submitted = false;

  $: leftItems = slide?.left_items ?? [];
  $: rightItems = slide?.right_items ?? [];

  const PAIR_COLORS = ['#e84393', '#1368ce', '#ffa602', '#26890c', '#8b5cf6', '#f97316'];

  let pool = [];
  let selectedIdx = null;
  let pairMap = {};    // poolIdx -> pairId
  let pairColors = {}; // pairId -> color
  let nextPairId = 0;
  let pairCount = 0;

  // Rebuild pool whenever items change (new question)
  $: {
    const all = [
      ...leftItems.map((text, i) => ({ text, side: 'left', idx: i })),
      ...rightItems.map((text, j) => ({ text, side: 'right', idx: j })),
    ];
    for (let i = all.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [all[i], all[j]] = [all[j], all[i]];
    }
    pool = all;
    pairMap = {};
    pairColors = {};
    nextPairId = 0;
    pairCount = 0;
    selectedIdx = null;
  }

  function tapItem(i) {
    if (submitted) return;

    // Tap a paired card → unpair both
    if (pairMap[i] != null) {
      const pid = pairMap[i];
      const newMap = { ...pairMap };
      for (const k of Object.keys(newMap)) {
        if (newMap[k] === pid) delete newMap[k];
      }
      pairMap = newMap;
      const newC = { ...pairColors };
      delete newC[pid];
      pairColors = newC;
      pairCount--;
      selectedIdx = null;
      return;
    }

    if (selectedIdx === null) { selectedIdx = i; return; }
    if (selectedIdx === i)    { selectedIdx = null; return; }

    // Any two cards may be paired (no left→right hint) — it's up to the
    // player to figure out which cards actually belong together.
    const pid = nextPairId++;
    pairMap = { ...pairMap, [selectedIdx]: pid, [i]: pid };
    pairColors = { ...pairColors, [pid]: PAIR_COLORS[pairCount % PAIR_COLORS.length] };
    pairCount++;
    selectedIdx = null;
  }

  $: allMatched = leftItems.length > 0 && pairCount === leftItems.length;

  function submit() {
    // Each pair is two [side, idx] cards; the server decides which are correct.
    const byPair = {};
    for (const [k, pid] of Object.entries(pairMap)) {
      const item = pool[Number(k)];
      (byPair[pid] ??= []).push([item.side, item.idx]);
    }
    const answer = Object.values(byPair);
    dispatch('answer', answer);
  }
</script>

<div class="wrap">
  <p class="hint">Tap two cards that belong together</p>
  <div class="pool">
    {#each pool as item, i}
      {@const pid = pairMap[i]}
      {@const color = pid != null ? pairColors[pid] : null}
      <button
        class="card"
        class:selected={selectedIdx === i}
        class:paired={pid != null}
        style={color ? `background:${color};border-color:${color}` : ''}
        on:click={() => tapItem(i)}
        disabled={submitted}
      >
        {item.text}
      </button>
    {/each}
  </div>

  <button class="submit-btn" disabled={!allMatched || submitted} on:click={submit}>
    {submitted ? 'Answer submitted!' : `Submit (${pairCount}/${leftItems.length} paired)`}
  </button>
</div>

<style>
  .wrap {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    padding: 0.6rem;
    flex: 1;
    min-height: 0;
  }
  .hint {
    text-align: center;
    color: var(--text-faint, rgba(255,255,255,0.4));
    font-size: 0.8rem;
    margin: 0;
  }
  .pool {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-auto-rows: 1fr;
    gap: 0.6rem;
    flex: 1;
    min-height: 0;
  }
  .card {
    padding: 0.6rem;
    background: rgba(255,255,255,0.1);
    border: 3px solid transparent;
    border-radius: 14px;
    color: #fff;
    font-size: clamp(0.85rem, 3.5vw, 1.1rem);
    font-weight: 700;
    cursor: pointer;
    text-align: center;
    word-break: break-word;
    transition: border-color 0.15s, background 0.15s, transform 0.1s;
    -webkit-tap-highlight-color: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 3px 10px rgba(0,0,0,0.25);
    min-height: 0;
  }
  .card:active:not(:disabled) { transform: scale(0.96); }
  .card.selected {
    border-color: #fff;
    background: rgba(124,58,237,0.4);
    box-shadow: 0 0 0 3px rgba(124,58,237,0.5);
  }
  .card.paired { opacity: 0.9; }
  .card:disabled { cursor: default; }
  .submit-btn {
    width: 100%;
    padding: 0.9rem;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--primary, #7c3aed), #6d28d9);
    color: #fff;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
  }
  .submit-btn:disabled { opacity: 0.5; cursor: default; }
</style>
