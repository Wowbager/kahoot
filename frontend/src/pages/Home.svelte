<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { api } from '../lib/api.js';
  import { session } from '../stores/session.js';
  import { randomNickname } from '../lib/nicknames.js';

  let step = 'pin';        // 'pin' | 'nick'
  let pin = '';
  let nickname = randomNickname();
  let gameTitle = '';
  let error = '';
  let loading = false;

  onMount(() => {
    // Deep link from the lobby QR code: #/?pin=123456
    const qs = location.hash.includes('?') ? location.hash.split('?')[1] : '';
    const deepPin = new URLSearchParams(qs).get('pin');
    if (deepPin) {
      pin = deepPin.replace(/\D/g, '').slice(0, 6);
      if (pin.length >= 4) submitPin();
    }
  });

  async function submitPin() {
    const code = pin.trim();
    if (!code) { error = 'Enter the game PIN'; return; }
    loading = true;
    error = '';
    try {
      const info = await api.getSession(code);
      gameTitle = info.title || '';
      step = 'nick';
    } catch {
      error = 'No game found with that PIN.';
    } finally {
      loading = false;
    }
  }

  function shuffle() { nickname = randomNickname(); }

  function join() {
    const nick = nickname.trim();
    if (!nick) { error = 'Pick a nickname'; return; }
    if (nick.length > 30) { error = 'Nickname too long (max 30).'; return; }
    session.set({ sessionCode: pin, presenterToken: null, nickname: nick, role: 'player' });
    push(`/play/${pin}/${encodeURIComponent(nick)}`);
  }

  function onPinInput(e) {
    pin = e.target.value.replace(/\D/g, '').slice(0, 6);
  }
  function pinKey(e) { if (e.key === 'Enter') submitPin(); }
  function nickKey(e) { if (e.key === 'Enter') join(); }
</script>

<div class="landing bg-animated">
  <div class="brand">
    <span class="logo">Quizzle</span>
    <span class="tag">Play. Compete. Repeat.</span>
  </div>

  <div class="card panel">
    {#if step === 'pin'}
      <h1>Game PIN</h1>
      <input
        class="input pin-input"
        inputmode="numeric"
        pattern="[0-9]*"
        placeholder="000000"
        maxlength="6"
        value={pin}
        on:input={onPinInput}
        on:keydown={pinKey}
        autofocus
      />
      {#if error}<p class="error-text">{error}</p>{/if}
      <button class="btn btn-primary btn-lg btn-block" on:click={submitPin} disabled={loading || pin.length < 4}>
        {loading ? 'Checking…' : 'Enter'}
      </button>
    {:else}
      {#if gameTitle}<p class="joining">Joining <strong>{gameTitle}</strong></p>{/if}
      <h1>Your nickname</h1>
      <div class="nick-row">
        <input
          class="input"
          placeholder="Pick a name"
          maxlength="30"
          bind:value={nickname}
          on:keydown={nickKey}
          autofocus
        />
        <button class="btn dice" title="Shuffle nickname" on:click={shuffle}>🎲</button>
      </div>
      {#if error}<p class="error-text">{error}</p>{/if}
      <button class="btn btn-primary btn-lg btn-block" on:click={join} disabled={!nickname.trim()}>
        Join game
      </button>
      <button class="btn link" on:click={() => { step = 'pin'; error = ''; }}>← Different PIN</button>
    {/if}
  </div>

  <button class="btn link host-link" on:click={() => push('/host')}>Host a game →</button>
</div>

<style>
  .landing {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100%;
    padding: 1.5rem;
    gap: 1.8rem;
  }
  .brand { text-align: center; }
  .logo {
    display: block;
    font-family: var(--font-display);
    font-size: clamp(2.6rem, 9vw, 4rem);
    font-weight: 800;
    letter-spacing: 1px;
    text-shadow: 0 6px 24px rgba(0,0,0,0.4);
  }
  .tag { color: var(--text-dim); font-size: 0.95rem; letter-spacing: 2px; text-transform: uppercase; }
  .panel {
    width: 100%;
    max-width: 380px;
    padding: 1.8rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  h1 { font-size: 1.3rem; text-align: center; color: var(--text); }
  .joining { text-align: center; color: var(--text-dim); font-size: 0.95rem; }
  .joining strong { color: var(--accent); }
  .pin-input {
    text-align: center;
    font-family: var(--font-display);
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: 0.5rem;
    padding: 0.8rem;
  }
  .nick-row { display: flex; gap: 0.6rem; }
  .nick-row .input { flex: 1; }
  .dice { font-size: 1.4rem; padding: 0 1rem; flex: 0 0 auto; }
  .link { background: transparent; color: var(--text-dim); font-weight: 600; align-self: center; padding: 0.5rem; }
  .link:hover:not(:disabled) { background: transparent; color: var(--text); }
  .host-link { opacity: 0.8; }
</style>
