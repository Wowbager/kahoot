<script>
  export let results = null;
  export let myScore = 0;
  export let rank = null;
  export let totalPlayers = 0;
</script>

<div class="reveal" class:correct={results?.isCorrect} class:wrong={!results?.isCorrect}>
  <div class="icon">{results?.isCorrect ? '✓' : '✗'}</div>
  <div class="verdict">{results?.isCorrect ? 'Correct!' : 'Wrong!'}</div>

  {#if results?.scoreDelta > 0}
    <div class="delta">+{results.scoreDelta.toLocaleString()}</div>
  {/if}

  {#if results?.streak >= 2}
    <div class="streak">🔥 {results.streak} in a row!{#if results.streakBonus > 0} <span>+{results.streakBonus}</span>{/if}</div>
  {/if}

  {#if rank}
    <div class="rank">{rank}{rank === 1 ? 'st' : rank === 2 ? 'nd' : rank === 3 ? 'rd' : 'th'} of {totalPlayers}</div>
  {/if}

  <div class="total">{myScore.toLocaleString()} pts</div>
</div>

<style>
  .reveal {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 0.7rem;
    padding: 2rem;
    transition: background 0.3s;
  }
  .correct { background: rgba(34, 197, 94, 0.18); }
  .wrong { background: rgba(239, 68, 68, 0.15); }
  .icon { font-size: 5rem; line-height: 1; animation: pop 0.4s cubic-bezier(0.2, 1.3, 0.4, 1) both; }
  .correct .icon { color: var(--correct); }
  .wrong .icon { color: var(--wrong); }
  .verdict { font-family: var(--font-display); font-size: 2.2rem; font-weight: 800; }
  .correct .verdict { color: var(--correct); }
  .wrong .verdict { color: var(--wrong); }
  .delta { font-size: 2.4rem; font-weight: 800; color: var(--accent); animation: riseIn 0.4s ease both 0.15s; }
  @keyframes pop { 0% { transform: scale(0); } 70% { transform: scale(1.2); } 100% { transform: scale(1); } }
  @keyframes riseIn { from { transform: translateY(12px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
  @media (prefers-reduced-motion: reduce) { .icon, .delta { animation: none; } }
  .streak {
    font-weight: 700;
    color: #fdba74;
    background: rgba(249, 115, 22, 0.18);
    padding: 0.4rem 1rem;
    border-radius: var(--radius-pill);
  }
  .streak span { color: var(--accent); }
  .rank { font-size: 1.1rem; color: var(--text-dim); font-weight: 600; }
  .total { font-size: 1rem; color: var(--text-faint); }
</style>
