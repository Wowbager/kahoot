<script>
  import { push } from 'svelte-spa-router';
  import { api } from '../lib/api.js';
  import { session } from '../stores/session.js';

  let code = '';
  let nickname = '';
  let error = '';
  let loading = false;

  async function join() {
    code = code.trim().toUpperCase();
    nickname = nickname.trim();
    if (!code || !nickname) { error = 'Please fill in both fields.'; return; }
    if (nickname.length > 30) { error = 'Nickname too long (max 30 chars).'; return; }
    loading = true;
    error = '';
    try {
      await api.getSession(code);
      session.set({ sessionCode: code, presenterToken: null, nickname, role: 'player' });
      push(`/play/${code}/${encodeURIComponent(nickname)}`);
    } catch (e) {
      error = 'Session not found. Check the code and try again.';
    } finally {
      loading = false;
    }
  }

  function keydown(e) { if (e.key === 'Enter') join(); }
</script>

<div class="join">
  <div class="card">
    <h1>Join Session</h1>

    <label>
      Session Code
      <input
        type="text"
        placeholder="Enter code (e.g. AB12CD)"
        bind:value={code}
        on:keydown={keydown}
        maxlength="6"
        autocomplete="off"
        autocapitalize="characters"
        spellcheck="false"
      />
    </label>

    <label>
      Your Nickname
      <input
        type="text"
        placeholder="Your name"
        bind:value={nickname}
        on:keydown={keydown}
        maxlength="30"
        autocomplete="off"
      />
    </label>

    {#if error}<p class="error">{error}</p>{/if}

    <button on:click={join} disabled={loading || !code || !nickname}>
      {loading ? 'Joining…' : 'Join!'}
    </button>

    <button class="back" on:click={() => push('/')}>← Back</button>
  </div>
</div>

<style>
  .join {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100%;
    padding: 1.5rem;
  }
  .card {
    background: rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 2rem;
    width: 100%;
    max-width: 380px;
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
  }
  h1 { font-size: 1.8rem; font-weight: 800; text-align: center; }
  label { display: flex; flex-direction: column; gap: 0.4rem; font-size: 0.9rem; color: #aaa; }
  input {
    padding: 0.9rem 1rem;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.08);
    color: #fff;
    font-size: 1.1rem;
    outline: none;
  }
  input:focus { border-color: #7c3aed; }
  button {
    padding: 0.9rem;
    border: none;
    border-radius: 10px;
    background: #7c3aed;
    color: #fff;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
  }
  button:hover:not(:disabled) { background: #6d28d9; }
  button:disabled { opacity: 0.5; cursor: default; }
  .back { background: transparent; border: 1px solid rgba(255,255,255,0.15); color: #aaa; font-size: 0.9rem; }
  .back:hover { background: rgba(255,255,255,0.05); }
  .error { color: #f87171; font-size: 0.9rem; }
</style>
