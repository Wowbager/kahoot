<script>
  export let message = 'Waiting for the presenter…';
  export let playerCount = 0;
</script>

<div class="wait">
  <div class="spinner"></div>
  <p class="msg">{message}</p>
  {#if playerCount > 0}
    <p class="count">{playerCount} player{playerCount !== 1 ? 's' : ''} joined</p>
  {/if}
</div>

<style>
  .wait {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 1.5rem;
    padding: 2rem;
  }
  .spinner {
    width: 60px;
    height: 60px;
    border: 5px solid rgba(255,255,255,0.15);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .msg { font-size: 1.3rem; color: var(--text-dim); text-align: center; font-weight: 600; }
  .count { font-size: 1rem; color: var(--text-faint); font-weight: 700; }

  @media (prefers-reduced-motion: reduce) {
    .spinner { animation: pulse 1.2s ease-in-out infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
  }
</style>
