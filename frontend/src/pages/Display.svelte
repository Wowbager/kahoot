<script>
  import { onDestroy } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { connectWS, closeWS } from '../lib/ws.js';
  import { game } from '../stores/game.js';
  import Markdown from '../components/Markdown.svelte';
  import QuestionDisplay from '../components/display/QuestionDisplay.svelte';
  import ResultsChart from '../components/display/ResultsChart.svelte';
  import Leaderboard from '../components/display/Leaderboard.svelte';

  export let params = {};
  let code = params.code || '';
  let enteredCode = '';
  let connected = false;
  let error = '';

  function connect() {
    const c = (enteredCode || code).trim().toUpperCase();
    if (!c) { error = 'Enter a session code'; return; }
    code = c;
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    connectWS(`${proto}://${location.host}/ws/display/${c}`);
    connected = true;
  }

  onDestroy(closeWS);

  $: showLeaderboard = $game.leaderboard?.length > 0 && $game.phase === 'revealed';
  $: showResults = $game.phase === 'revealed' && $game.distribution;
</script>

{#if !connected}
  <div class="enter-code">
    <h1>Display Screen</h1>
    <input
      type="text"
      placeholder="Session code"
      bind:value={enteredCode}
      on:keydown={e => e.key === 'Enter' && connect()}
      maxlength="6"
      autocapitalize="characters"
      spellcheck="false"
    />
    {#if error}<p class="error">{error}</p>{/if}
    <button on:click={connect}>Connect</button>
    <button class="back" on:click={() => push('/')}>← Back</button>
  </div>

{:else}
  <div class="display">
    <!-- Lobby -->
    {#if $game.phase === 'idle' && $game.slide?.type === 'presentation'}
      <div class="pres-full">
        <Markdown content={$game.slide.content} />
      </div>

    {:else if $game.phase === 'idle' && $game.slide}
      <!-- Question slide not yet started — show question, wait for presenter -->
      <div class="waiting-question">
        <div class="wq-header">Get ready!</div>
        <div class="wq-question">{$game.slide.question}</div>
        <div class="player-count">{$game.players.length} player{$game.players.length !== 1 ? 's' : ''} connected</div>
      </div>

    {:else if $game.phase === 'active'}
      <QuestionDisplay
        slide={$game.slide}
        startedAt={$game.questionStartedAt}
        timeLimit={$game.timeLimit}
      />

    {:else if $game.phase === 'revealed'}
      <div class="revealed-layout">
        {#if showResults}
          <ResultsChart slide={$game.slide} distribution={$game.distribution} correct={$game.results?.correct} />
        {/if}
        {#if showLeaderboard}
          <Leaderboard standings={$game.leaderboard} />
        {/if}
      </div>
    {/if}

    <!-- Session code watermark -->
    <div class="watermark">{code}</div>
  </div>
{/if}

<style>
  .enter-code {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 100%; gap: 1rem; padding: 2rem;
  }
  h1 { font-size: 2rem; font-weight: 800; }
  input {
    padding: 0.9rem 1rem; border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.08); color: #fff; font-size: 1.4rem;
    text-align: center; letter-spacing: 4px; width: 220px;
  }
  button {
    padding: 0.8rem 2rem; border: none; border-radius: 10px;
    background: #7c3aed; color: #fff; font-size: 1rem; font-weight: 700; cursor: pointer;
  }
  .back { background: rgba(255,255,255,0.1); }
  .error { color: #f87171; }

  .display { position: relative; height: 100%; display: flex; align-items: center; justify-content: center; overflow: hidden; }
  .pres-full { padding: 4rem; max-width: 900px; width: 100%; font-size: 1.3rem; }
  .waiting-question { display: flex; flex-direction: column; align-items: center; gap: 2rem; text-align: center; padding: 3rem; }
  .wq-header { font-size: 1.5rem; color: #888; }
  .wq-question { font-size: clamp(1.8rem, 4vw, 3rem); font-weight: 700; max-width: 800px; }
  .player-count { font-size: 1.2rem; color: #7c3aed; }
  .revealed-layout { display: flex; flex-direction: column; align-items: center; gap: 2rem; padding: 2rem; width: 100%; }
  .watermark { position: absolute; bottom: 1rem; right: 1.5rem; font-size: 1rem; color: rgba(255,255,255,0.2); letter-spacing: 2px; }
</style>
