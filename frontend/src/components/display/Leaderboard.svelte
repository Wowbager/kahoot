<script>
  export let standings = [];
  const medals = ['🥇', '🥈', '🥉'];
</script>

<div class="board">
  <h2>Leaderboard</h2>
  <ol>
    {#each standings.slice(0, 10) as player, i}
      <li class="entry" class:top={i < 3}>
        <span class="rank">{medals[i] ?? (i + 1)}</span>
        <span class="name">{player.nickname}</span>
        <span class="score">{player.score.toLocaleString()}</span>
      </li>
    {/each}
  </ol>
</div>

<style>
  .board { width: 100%; max-width: 600px; }
  h2 { text-align: center; font-size: 2rem; margin-bottom: 1.5rem; color: gold; }
  ol { list-style: none; display: flex; flex-direction: column; gap: 0.6rem; }
  .entry {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem 1.2rem;
    background: rgba(255,255,255,0.08);
    border-radius: 10px;
    font-size: 1.1rem;
  }
  .top { background: rgba(255,215,0,0.15); border: 1px solid rgba(255,215,0,0.3); }
  .rank { font-size: 1.4rem; min-width: 2.5rem; }
  .name { flex: 1; font-weight: 600; }
  .score { font-weight: 700; color: #fbbf24; font-size: 1.2rem; }
</style>
