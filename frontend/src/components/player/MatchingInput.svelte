<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let slide = null;   // has left_items: string[], right_items: string[]
  export let submitted = false;

  $: leftItems = slide?.left_items ?? [];
  $: rightItems = slide?.right_items ?? [];

  // pairs[leftIdx] = rightIdx | null
  let pairs = {};
  let selectedLeft = null;

  function tapLeft(i) {
    if (submitted) return;
    selectedLeft = selectedLeft === i ? null : i;
  }

  function tapRight(j) {
    if (submitted || selectedLeft === null) return;
    // unlink previous pairing for this right item
    for (const [k, v] of Object.entries(pairs)) {
      if (v === j) { delete pairs[k]; pairs = { ...pairs }; }
    }
    pairs = { ...pairs, [selectedLeft]: j };
    selectedLeft = null;
  }

  function unpair(i) {
    if (submitted) return;
    pairs = { ...pairs };
    delete pairs[i];
    pairs = { ...pairs };
  }

  $: allMatched = leftItems.length > 0 && leftItems.every((_, i) => pairs[i] !== undefined);

  function submit() {
    const answer = Object.entries(pairs).map(([l, r]) => [Number(l), Number(r)]);
    dispatch('answer', answer);
  }
</script>

<div class="wrap">
  <div class="columns">
    <div class="col left-col">
      {#each leftItems as item, i}
        <button
          class="item"
          class:selected={selectedLeft === i}
          class:paired={pairs[i] !== undefined}
          on:click={() => tapLeft(i)}
        >
          {item}
          {#if pairs[i] !== undefined}
            <span class="badge" on:click|stopPropagation={() => unpair(i)}>✕</span>
          {/if}
        </button>
      {/each}
    </div>

    <div class="divider">→</div>

    <div class="col right-col">
      {#each rightItems as item, j}
        {@const isLinked = Object.values(pairs).includes(j)}
        <button
          class="item"
          class:linked={isLinked}
          class:highlight={selectedLeft !== null && !isLinked}
          on:click={() => tapRight(j)}
        >
          {item}
        </button>
      {/each}
    </div>
  </div>

  <div class="summary">
    {#each leftItems as item, i}
      {#if pairs[i] !== undefined}
        <span class="pair-chip">{item} → {rightItems[pairs[i]]}</span>
      {/if}
    {/each}
  </div>

  <button class="submit-btn" disabled={!allMatched || submitted} on:click={submit}>
    {submitted ? 'Answer submitted!' : 'Submit'}
  </button>
</div>

<style>
  .wrap { display: flex; flex-direction: column; gap: 1rem; padding: 1rem; flex: 1; overflow-y: auto; }
  .columns { display: flex; align-items: flex-start; gap: 0.5rem; }
  .col { display: flex; flex-direction: column; gap: 0.5rem; flex: 1; }
  .divider { align-self: center; font-size: 1.5rem; color: #666; padding: 0 0.3rem; }
  .item {
    padding: 0.7rem 0.8rem;
    background: rgba(255,255,255,0.1);
    border: 2px solid transparent;
    border-radius: 10px;
    color: #fff;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    position: relative;
    transition: border-color 0.15s, background 0.15s;
    -webkit-tap-highlight-color: transparent;
  }
  .item.selected { border-color: var(--primary); background: rgba(124,58,237,0.25); }
  .item.paired { border-color: var(--correct); background: rgba(34,197,94,0.15); }
  .item.linked { border-color: var(--correct); background: rgba(34,197,94,0.15); }
  .item.highlight { border-color: rgba(124,58,237,0.5); }
  .badge {
    position: absolute;
    top: -6px;
    right: -6px;
    background: #ef4444;
    color: #fff;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    font-size: 0.7rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .summary { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .pair-chip {
    background: rgba(34,197,94,0.2);
    border: 1px solid rgba(34,197,94,0.4);
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.8rem;
    color: #86efac;
  }
  .submit-btn {
    width: 100%;
    padding: 1rem;
    border: none;
    border-radius: var(--radius-md);
    background: linear-gradient(135deg, var(--primary), var(--primary-700));
    color: #fff;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    margin-top: auto;
  }
  .submit-btn:disabled { opacity: 0.5; cursor: default; }
</style>
