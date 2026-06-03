<script>
  import { onMount } from 'svelte';
  import QRCode from 'qrcode';

  export let code = '';
  export let players = [];
  export let title = '';

  let qrUrl = '';
  $: joinUrl = `${location.origin}/#/?pin=${code}`;

  onMount(async () => {
    try {
      qrUrl = await QRCode.toDataURL(joinUrl, {
        margin: 1,
        width: 320,
        color: { dark: '#1b1140', light: '#ffffff' },
      });
    } catch {}
  });
</script>

<div class="lobby">
  <div class="left">
    <div class="title">{title}</div>
    <div class="join-line">Join at <span class="host">{location.host}</span></div>
    <div class="pin-label">Game PIN</div>
    <div class="pin">{code}</div>
    {#if qrUrl}
      <img class="qr" src={qrUrl} alt="Scan to join" />
      <div class="qr-hint">Scan to join instantly</div>
    {/if}
  </div>

  <div class="right">
    <div class="count">
      <span class="num">{players.length}</span>
      <span class="lbl">{players.length === 1 ? 'player' : 'players'}</span>
    </div>
    {#if players.length === 0}
      <div class="empty">Waiting for players to join…</div>
    {:else}
      <div class="players">
        {#each players as p (p.nickname)}
          <span class="chip">{p.nickname}</span>
        {/each}
      </div>
    {/if}
    <div class="start-hint">Press <kbd>Space</kbd> to start</div>
  </div>
</div>

<style>
  .lobby {
    display: grid;
    grid-template-columns: minmax(280px, 0.8fr) 1.2fr;
    gap: 3rem;
    width: 100%;
    height: 100%;
    align-items: center;
    padding: 3rem clamp(2rem, 5vw, 5rem);
  }
  .left { display: flex; flex-direction: column; align-items: center; gap: 0.6rem; text-align: center; }
  .title { font-family: var(--font-display); font-size: clamp(1.4rem, 2.6vw, 2.2rem); font-weight: 700; }
  .join-line { color: var(--text-dim); font-size: 1rem; }
  .join-line .host { color: var(--text); font-weight: 600; }
  .pin-label { margin-top: 0.5rem; color: var(--text-faint); text-transform: uppercase; letter-spacing: 3px; font-size: 0.9rem; }
  .pin {
    font-family: var(--font-display);
    font-size: clamp(3rem, 8vw, 6rem);
    font-weight: 800;
    letter-spacing: 0.6rem;
    color: var(--accent);
    text-shadow: 0 6px 30px rgba(251, 191, 36, 0.25);
  }
  .qr { width: clamp(160px, 16vw, 240px); height: auto; border-radius: var(--radius-md); box-shadow: var(--shadow-md); }
  .qr-hint { color: var(--text-faint); font-size: 0.85rem; }

  .right { display: flex; flex-direction: column; gap: 1.2rem; height: 100%; justify-content: center; }
  .count { display: flex; align-items: baseline; gap: 0.6rem; }
  .count .num { font-family: var(--font-display); font-size: 3rem; font-weight: 800; color: var(--primary); }
  .count .lbl { font-size: 1.3rem; color: var(--text-dim); }
  .empty { color: var(--text-faint); font-size: 1.2rem; }
  .players { display: flex; flex-wrap: wrap; gap: 0.7rem; align-content: flex-start; max-height: 50vh; overflow-y: auto; }
  .chip {
    background: var(--surface-2);
    border: 1px solid var(--surface-border);
    padding: 0.6rem 1.1rem;
    border-radius: var(--radius-pill);
    font-weight: 600;
    font-size: 1.1rem;
    animation: popIn 0.25s ease;
  }
  @keyframes popIn { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }
  .start-hint { margin-top: auto; color: var(--text-dim); font-size: 1rem; }
  kbd {
    background: var(--surface-2);
    border: 1px solid var(--surface-border);
    border-radius: 6px;
    padding: 0.15rem 0.5rem;
    font-family: var(--font-body);
    font-weight: 700;
  }
</style>
