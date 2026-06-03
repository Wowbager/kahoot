<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { api } from '../lib/api.js';
  import { session } from '../stores/session.js';

  let presentations = [];
  let selected = '';
  let error = '';
  let loading = false;

  onMount(async () => {
    try {
      presentations = await api.getPresentations();
      if (presentations.length) selected = presentations[0];
    } catch (e) {
      error = 'Could not load presentations.';
    }
  });

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

  function prettyName(f) {
    return f.replace(/\.json$/, '').replace(/[-_]/g, ' ');
  }
</script>

<div class="host bg-animated">
  <div class="card panel">
    <h1>Host a game</h1>
    {#if presentations.length === 0 && !error}
      <p class="hint">Loading presentations…</p>
    {:else if presentations.length === 0}
      <p class="hint">No presentations found in the <code>presentations/</code> folder.</p>
    {:else}
      <label class="field">
        Choose a quiz
        <select class="input" bind:value={selected}>
          {#each presentations as p}
            <option value={p}>{prettyName(p)}</option>
          {/each}
        </select>
      </label>
      <button class="btn btn-primary btn-lg btn-block" on:click={createSession} disabled={loading}>
        {loading ? 'Creating…' : 'Create game'}
      </button>
    {/if}
    {#if error}<p class="error-text">{error}</p>{/if}
    <button class="btn link" on:click={() => push('/')}>← Back</button>
  </div>
</div>

<style>
  .host {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100%;
    padding: 1.5rem;
  }
  .panel {
    width: 100%;
    max-width: 440px;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
  }
  h1 { font-size: 1.8rem; text-align: center; }
  .field { display: flex; flex-direction: column; gap: 0.5rem; color: var(--text-dim); font-size: 0.9rem; }
  select { text-transform: capitalize; }
  .hint { color: var(--text-faint); font-size: 0.9rem; text-align: center; }
  code { background: var(--surface-2); padding: 0.1em 0.4em; border-radius: 4px; }
  .link { background: transparent; color: var(--text-dim); align-self: center; }
  .link:hover:not(:disabled) { background: transparent; color: var(--text); }
</style>
