<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let slide = null;
  export let submitted = false;

  // true_false or single_choice or multiple_choice
  const COLORS = ['#e84393', '#1368ce', '#ffa602', '#26890c'];
  const SHAPES = ['▲', '◆', '●', '■'];

  let selected = [];

  function toggle(idx) {
    if (submitted) return;
    if (slide.type === 'single_choice' || slide.type === 'true_false') {
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

<div class="buttons" style="--count:{options.length}">
  {#each options as opt, i}
    <button
      class="btn"
      class:selected={selected.includes(i)}
      class:submitted
      style="background:{COLORS[i % 4]}"
      on:click={() => toggle(i)}
      disabled={submitted}
    >
      <span class="shape">{SHAPES[i % 4]}</span>
      <span class="label">{opt}</span>
    </button>
  {/each}
</div>

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
    border-radius: 12px;
    color: #fff;
    font-size: clamp(1rem, 4vw, 1.4rem);
    font-weight: 700;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.3rem;
    padding: 0.8rem;
    min-height: 80px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    transition: transform 0.1s, opacity 0.2s;
    -webkit-tap-highlight-color: transparent;
  }
  .btn:active:not(:disabled) { transform: scale(0.97); }
  .btn.selected { outline: 4px solid #fff; }
  .btn.submitted { opacity: 0.5; cursor: default; }
  .shape { font-size: 1.5rem; }
  .label { text-align: center; word-break: break-word; }
  .submit-wrap { padding: 0 0.8rem 0.8rem; }
  .submit-btn {
    width: 100%;
    padding: 1rem;
    border: none;
    border-radius: 12px;
    background: #7c3aed;
    color: #fff;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
  }
  .submit-btn:disabled { opacity: 0.4; cursor: default; }
</style>
