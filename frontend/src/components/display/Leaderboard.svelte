<script>
    import { onMount } from "svelte";

  export let standings = [];
  const medals = ['🥇', '🥈', '🥉'];
  $: top = standings.slice(0, 5);
  $: rest = Math.max(0, standings.length - top.length);

  onMount(() => {
    audio.play();
  });

  let audio;
</script>

<audio src="/sounds/gong.mp3" bind:this={audio}></audio>

<div class="board">
  <h2>Leaderboard</h2>
  <ol>
    {#each top as player, i (player.nickname)}
      <li class="entry" class:top={i < 3}>
        <span class="rank">{medals[i] ?? (i + 1)}</span>
        <span class="name">{player.nickname}</span>
        <span class="score">{player.score.toLocaleString()}</span>
      </li>
    {/each}
  </ol>
  {#if rest > 0}
    <div class="rest">+{rest} more {rest === 1 ? 'player' : 'players'}</div>
  {/if}
</div>

<style>
  .board { width: 100%; max-width: 640px; }
  h2 { text-align: center; font-size: 2rem; margin-bottom: 1.2rem; color: var(--accent); }
  ol { list-style: none; display: flex; flex-direction: column; gap: 0.6rem; }
  .entry {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1.2rem;
    background: var(--surface);
    border: 1px solid var(--surface-border);
    border-radius: var(--radius-md);
    font-size: 1.15rem;
    animation: slideIn 0.4s ease backwards;
  }
  .entry:nth-child(1) { animation-delay: 0.05s; }
  .entry:nth-child(2) { animation-delay: 0.1s; }
  .entry:nth-child(3) { animation-delay: 0.15s; }
  .entry:nth-child(4) { animation-delay: 0.2s; }
  .entry:nth-child(5) { animation-delay: 0.25s; }
  @keyframes slideIn { from { opacity: 0; transform: translateX(-12px); } to { opacity: 1; transform: translateX(0); } }
  .top { background: rgba(251, 191, 36, 0.14); border-color: rgba(251, 191, 36, 0.35); }
  .rank { font-size: 1.4rem; min-width: 2.5rem; }
  .name { flex: 1; font-weight: 600; }
  .score { font-weight: 800; color: var(--accent); font-size: 1.25rem; }
  .rest { text-align: center; color: var(--text-faint); margin-top: 0.9rem; font-size: 0.95rem; }
</style>
