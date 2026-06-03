<script>
  import { sendWS } from '../../lib/ws.js';
  export let slideIndex = 0;
  export let totalSlides = 0;
  export let phase = 'idle';
  export let isQuestionSlide = false;

  function prev() { sendWS({ type: 'prev_slide' }); }
  function next() { sendWS({ type: 'next_slide' }); }
  function startQuestion() { sendWS({ type: 'start_question' }); }
  function reveal() { sendWS({ type: 'reveal_answers' }); }
  function showLeaderboard() { sendWS({ type: 'show_leaderboard' }); }
</script>

<div class="controls">
  <div class="nav">
    <button on:click={prev} disabled={slideIndex === 0}>← Prev</button>
    <span class="slide-num">{slideIndex + 1} / {totalSlides}</span>
    <button on:click={next} disabled={slideIndex >= totalSlides - 1}>Next →</button>
  </div>

  {#if isQuestionSlide}
    <div class="actions">
      {#if phase === 'idle'}
        <button class="primary" on:click={startQuestion}>▶ Start Question</button>
      {:else if phase === 'active'}
        <button class="danger" on:click={reveal}>Reveal Answers</button>
      {:else if phase === 'revealed'}
        <button class="secondary" on:click={showLeaderboard}>Show Leaderboard</button>
        <button on:click={next} disabled={slideIndex >= totalSlides - 1}>Next Slide →</button>
      {/if}
    </div>
  {/if}
</div>

<style>
  .controls { display: flex; flex-direction: column; gap: 1rem; }
  .nav { display: flex; align-items: center; gap: 0.8rem; }
  .slide-num { flex: 1; text-align: center; font-size: 0.9rem; color: #aaa; }
  .actions { display: flex; flex-wrap: wrap; gap: 0.6rem; }
  button {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 600;
    background: rgba(255,255,255,0.12);
    color: #fff;
    transition: background 0.15s;
  }
  button:hover:not(:disabled) { background: rgba(255,255,255,0.2); }
  button:disabled { opacity: 0.4; cursor: default; }
  .primary { background: #7c3aed; }
  .primary:hover:not(:disabled) { background: #6d28d9; }
  .danger { background: #dc2626; }
  .danger:hover:not(:disabled) { background: #b91c1c; }
  .secondary { background: #0369a1; }
  .secondary:hover:not(:disabled) { background: #075985; }
</style>
