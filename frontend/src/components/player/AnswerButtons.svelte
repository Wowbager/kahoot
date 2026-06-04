<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let slide = null;
  export let submitted = false;

  const COLORS = ['#e84393', '#1368ce', '#ffa602', '#26890c'];
  const SHAPES = ['▲', '◆', '●', '■'];

  let selected = [];

  function toggle(idx) {
    if (submitted) return;
    if (slide.type === 'true_false') {
      dispatch('answer', idx === 0); // 0 = True (boolean true), 1 = False
    } else if (slide.type === 'single_choice') {
      dispatch('answer', idx);
    } else {
      // multiple_choice
      if (selected.includes(idx)) {
        selected = selected.filter(i => i !== idx);
      } else {
        selected = [...selected, idx];
      }
    }
  }

  function submitMultiple() {
    if (selected.length > 0) dispatch('answer', selected);
  }

  $: options = slide?.type === 'true_false'
    ? ['True', 'False']
    : (slide?.options ?? []);
</script>

{#if slide?.type === "true_false"}
  <div class="buttons" style="--count:2">
    <button
      class="btn"
      class:selected={selected.includes(0)}
      class:submitted
      style="background:{COLORS[3]}"
      on:click={() => toggle(0)}
      disabled={submitted}
    >
      <span>✓ True</span>
    </button>
    <button
      class="btn"
      class:selected={selected.includes(2)}
      class:submitted
      style="background:{COLORS[0]}"
      on:click={() => toggle(2)}
      disabled={submitted}
    >
      <span>✗ False</span>
    </button>
  </div>
{:else}
  <div class="buttons" style="--count:{options.length}">
    {#each options as _opt, i}
      <button
        class="btn"
        class:selected={selected.includes(i)}
        class:submitted
        style="background:{COLORS[i % 4]}"
        on:click={() => toggle(i)}
        disabled={submitted}
      >
        <span class="shape">{SHAPES[i % 4]}</span>
      </button>
    {/each}
  </div>
{/if}

{#if slide?.type === 'multiple_choice' && !submitted}
  <div class="submit-wrap">
    <button
      class="submit-btn"
      disabled={selected.length === 0}
      on:click={submitMultiple}
    >Submit ({selected.length} selected)</button>
  </div>
{/if}

<style>
  .buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.8rem;
    padding: 0.8rem;
    flex: 1;
    align-content: stretch;
  }
  .btn {
    border: none;
    border-radius: var(--radius-lg);
    color: #fff;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 130px;
    box-shadow: var(--shadow-md);
    transition: transform 0.1s, opacity 0.2s, box-shadow 0.15s;
    -webkit-tap-highlight-color: transparent;
  }
  .btn:active:not(:disabled) { transform: scale(0.95); }
  .btn.selected { box-shadow: 0 0 0 5px #fff, var(--shadow-md); }
  .btn.submitted { opacity: 0.5; cursor: default; }
  .shape { font-size: 3.5rem; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.3)); }
  .submit-wrap { padding: 0 0.8rem 0.8rem; }
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
    box-shadow: var(--shadow-sm);
    transition: opacity 0.15s, transform 0.08s;
  }
  .submit-btn:active:not(:disabled) { transform: scale(0.99); }
  .submit-btn:disabled { opacity: 0.4; cursor: default; box-shadow: none; }
</style>
