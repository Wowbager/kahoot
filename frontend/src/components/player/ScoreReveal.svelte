<script>
  export let results = null;
  export let myScore = 0;
</script>

<div class="reveal" class:correct={results?.isCorrect} class:wrong={!results?.isCorrect}>
  <div class="icon">{results?.isCorrect ? '✓' : '✗'}</div>
  <div class="verdict">{results?.isCorrect ? 'Correct!' : 'Wrong!'}</div>
  {#if results?.scoreDelta > 0}
    <div class="delta">+{results.scoreDelta.toLocaleString()} pts</div>
  {/if}
  <div class="total">Total: {myScore.toLocaleString()}</div>
</div>

<style>
  .reveal {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 1rem;
    padding: 2rem;
    transition: background 0.3s;
  }
  .correct { background: rgba(34,197,94,0.2); }
  .wrong { background: rgba(239,68,68,0.15); }
  .icon {
    font-size: 5rem;
    line-height: 1;
  }
  .correct .icon { color: #22c55e; }
  .wrong .icon { color: #ef4444; }
  .verdict { font-size: 2rem; font-weight: 800; }
  .correct .verdict { color: #22c55e; }
  .wrong .verdict { color: #ef4444; }
  .delta { font-size: 2.5rem; font-weight: 700; color: #fbbf24; }
  .total { font-size: 1.1rem; color: #aaa; }
</style>
