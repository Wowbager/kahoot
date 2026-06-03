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
    border-top-color: #7c3aed;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .msg { font-size: 1.2rem; color: #ccc; text-align: center; }
  .count { font-size: 1rem; color: #7c3aed; font-weight: 600; }
</style>
