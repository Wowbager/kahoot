<script>
  export let players = [];
  export let answerCount = 0;
</script>

<div class="panel">
  <div class="header">
    <h3>Players ({players.length})</h3>
    {#if answerCount > 0}
      <span class="answers">{answerCount}/{players.length} answered</span>
    {/if}
  </div>
  {#if players.length === 0}
    <p class="empty">Waiting for players to join…</p>
  {:else}
    <div class="progress-bar">
      <div class="fill" style="width:{players.length ? (answerCount/players.length)*100 : 0}%"></div>
    </div>
    <ul>
      {#each players as p}
        <li>
          <span class="nick">{p.nickname}</span>
          <span class="score">{p.score}</span>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .panel { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem; }
  .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem; }
  h3 { font-size: 1rem; color: #ccc; }
  .answers { font-size: 0.85rem; color: #7c3aed; font-weight: 600; }
  .empty { color: #666; font-size: 0.9rem; }
  .progress-bar { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; margin-bottom: 0.8rem; overflow: hidden; }
  .fill { height: 100%; background: #7c3aed; border-radius: 3px; transition: width 0.3s ease; }
  ul { list-style: none; display: flex; flex-direction: column; gap: 0.3rem; max-height: 300px; overflow-y: auto; }
  li { display: flex; justify-content: space-between; padding: 0.3rem 0.5rem; border-radius: 6px; background: rgba(255,255,255,0.05); }
  .nick { color: #eee; font-size: 0.9rem; }
  .score { color: #fbbf24; font-size: 0.85rem; font-weight: 600; }
</style>
