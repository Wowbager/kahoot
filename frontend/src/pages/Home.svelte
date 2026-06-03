<script>
  import { push } from 'svelte-spa-router';
  import { api } from '../lib/api.js';
  import { session } from '../stores/session.js';

  let presentations = [];
  let selected = '';
  let error = '';
  let loading = false;

  async function loadPresentations() {
    presentations = await api.getPresentations();
    if (presentations.length) selected = presentations[0];
  }
  loadPresentations();

  async function createSession() {
    if (!selected) return;
    loading = true;
    error = '';
    try {
      const { session_code, presenter_token } = await api.createSession(selected);
      session.set({ sessionCode: session_code, presenterToken: presenter_token, nickname: null, role: 'presenter' });
      push(`/presenter/${session_code}`);
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="home">
  <div class="card">
    <h1>🎮 Kahoot Clone</h1>

    <section>
      <h2>Host a Session</h2>
      {#if presentations.length === 0}
        <p class="hint">No presentations found in the <code>presentations/</code> folder.</p>
      {:else}
        <label>
          Select presentation
          <select bind:value={selected}>
            {#each presentations as p}
              <option value={p}>{p}</option>
            {/each}
          </select>
        </label>
        <button class="btn-primary" on:click={createSession} disabled={loading}>
          {loading ? 'Creating…' : 'Create Session'}
        </button>
        {#if error}<p class="error">{error}</p>{/if}
      {/if}
    </section>

    <hr />

    <section>
      <h2>Join a Session</h2>
      <button class="btn-secondary" on:click={() => push('/join')}>Join →</button>
    </section>

    <hr />

    <section>
      <h2>Display Screen</h2>
      <p class="hint">Open this on your projector / big screen after creating a session.</p>
      <button class="btn-secondary" on:click={() => push('/display')}>Open Display →</button>
    </section>
  </div>
</div>

<style>
  .home {
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
    max-width: 480px;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  h1 { font-size: 2rem; font-weight: 800; text-align: center; }
  h2 { font-size: 1.1rem; color: #ccc; margin-bottom: 0.8rem; }
  section { display: flex; flex-direction: column; gap: 0.8rem; }
  label { display: flex; flex-direction: column; gap: 0.4rem; font-size: 0.9rem; color: #aaa; }
  select {
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.08);
    color: #fff;
    font-size: 1rem;
  }
  .btn-primary, .btn-secondary {
    padding: 0.8rem 1.5rem;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
  }
  .btn-primary { background: #7c3aed; color: #fff; }
  .btn-primary:hover:not(:disabled) { background: #6d28d9; }
  .btn-primary:disabled { opacity: 0.5; }
  .btn-secondary { background: rgba(255,255,255,0.1); color: #fff; }
  .btn-secondary:hover { background: rgba(255,255,255,0.18); }
  hr { border: none; border-top: 1px solid rgba(255,255,255,0.1); }
  .hint { font-size: 0.85rem; color: #888; }
  .error { color: #f87171; font-size: 0.9rem; }
  code { background: rgba(255,255,255,0.1); padding: 0.1em 0.4em; border-radius: 4px; font-size: 0.85em; }
</style>
