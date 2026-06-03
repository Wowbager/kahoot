<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let slide = null;
  export let submitted = false;

  let value = slide ? Math.round((slide.min + slide.max) / 2) : 0;

  function submit() {
    if (!submitted) dispatch('answer', Number(value));
  }
</script>

<div class="wrap">
  <div class="value">{value}</div>
  <input
    type="range"
    min={slide?.min ?? 0}
    max={slide?.max ?? 100}
    step="1"
    bind:value
    disabled={submitted}
    class:submitted
  />
  <div class="range-labels">
    <span>{slide?.min}</span>
    <span>{slide?.max}</span>
  </div>
  <button on:click={submit} disabled={submitted} class="submit-btn">
    {submitted ? 'Answer submitted!' : 'Submit'}
  </button>
</div>

<style>
  .wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    padding: 2rem 1.5rem;
    flex: 1;
    justify-content: center;
  }
  .value {
    font-family: var(--font-display);
    font-size: 4.5rem;
    font-weight: 800;
    color: var(--primary);
    min-width: 4rem;
    text-align: center;
  }
  input[type=range] {
    width: 100%;
    height: 8px;
    accent-color: var(--primary);
    cursor: pointer;
  }
  input.submitted { opacity: 0.5; }
  .range-labels { display: flex; justify-content: space-between; width: 100%; color: var(--text-faint); font-size: 0.9rem; }
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
  }
  .submit-btn:disabled { opacity: 0.5; cursor: default; }
</style>
