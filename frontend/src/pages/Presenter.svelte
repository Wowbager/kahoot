<script>
  import { onDestroy, onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { connectWS, closeWS, sendWS } from '../lib/ws.js';
  import { game } from '../stores/game.js';
  import { session } from '../stores/session.js';
  import Markdown from '../components/Markdown.svelte';
  import QuestionDisplay from '../components/display/QuestionDisplay.svelte';
  import ResultsChart from '../components/display/ResultsChart.svelte';
  import Leaderboard from '../components/display/Leaderboard.svelte';
  import Podium from '../components/display/Podium.svelte';
  import Lobby from '../components/presenter/Lobby.svelte';

  export let params = {};
  const code = params.code;

  let sessVal;
  session.subscribe(v => sessVal = v);
  const token = sessVal?.presenterToken;

  if (!code || !token) {
    push('/');
  } else {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    connectWS(`${proto}://${location.host}/ws/presenter/${code}?token=${token}`);
  }
  onDestroy(closeWS);

  const QUESTION_TYPES = ['true_false', 'single_choice', 'multiple_choice', 'number_slider', 'multiple_matching'];
  $: isQuestion = QUESTION_TYPES.includes($game.slide?.type);
  $: isLast = $game.slideIndex >= $game.totalSlides - 1;

  // What the contextual "advance" action will do, given the current state.
  $: actionLabel = (() => {
    const g = $game;
    if (g.finished) return null;
    if (!g.started) return 'Start';
    if (g.phase === 'countdown') return 'Starting…';
    if (g.phase === 'active') return 'Reveal';
    if (g.phase === 'revealed') return isLast ? 'Finish' : 'Next';
    if (isQuestion) return 'Start question';
    return isLast ? 'Finish' : 'Next';
  })();

  function advance() {
    const g = $game;
    if (g.finished) return;
    if (!g.started) { sendWS({ type: 'start_game' }); return; }
    if (g.phase === 'countdown') return;
    if (g.phase === 'active') { sendWS({ type: 'reveal_answers' }); return; }
    if (g.phase === 'revealed') {
      sendWS({ type: isLast ? 'end_game' : 'next_slide' });
      return;
    }
    // idle on a slide
    if (isQuestion) { sendWS({ type: 'start_question' }); return; }
    sendWS({ type: isLast ? 'end_game' : 'next_slide' });
  }

  function back() {
    if (!$game.started || $game.finished) return;
    sendWS({ type: 'prev_slide' });
  }

  function showLeaderboard() { sendWS({ type: 'show_leaderboard' }); }

  function onKey(e) {
    if (e.target?.tagName === 'INPUT') return;
    if (e.key === ' ' || e.key === 'ArrowRight' || e.key === 'Enter') {
      e.preventDefault();
      advance();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      back();
    }
  }

  // Auto-hiding control bar
  let barVisible = true;
  let hideTimer;
  function poke() {
    barVisible = true;
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => { barVisible = false; }, 3000);
  }
  onMount(() => { poke(); });
  onDestroy(() => clearTimeout(hideTimer));
</script>

<svelte:window on:keydown={onKey} on:mousemove={poke} />

<div class="stage bg-stage">
  <div class="content">
    {#if !$game.started && !$game.finished}
      <Lobby code={$game.code || code} players={$game.players} title={$game.title} />

    {:else if $game.finished || $game.phase === 'finished'}
      <Podium standings={$game.leaderboard} />

    {:else if $game.phase === 'active' || $game.phase === 'countdown'}
      <QuestionDisplay slide={$game.slide} startedAt={$game.questionStartedAt} revealAt={$game.questionRevealAt} timeLimit={$game.timeLimit} answersOpen={$game.answersOpen} />

    {:else if $game.phase === 'revealed'}
      <div class="revealed">
        {#if $game.distribution}
          <ResultsChart slide={$game.slide} distribution={$game.distribution} correct={$game.results?.correct} />
        {/if}
        {#if $game.leaderboard?.length && !isLast}
          <Leaderboard standings={$game.leaderboard} />
        {/if}
      </div>

    {:else if $game.slide?.type === 'presentation'}
      <div class="pres"><Markdown content={$game.slide.content} /></div>

    {:else if $game.slide}
      <div class="get-ready">
        <div class="ready-label">Get ready!</div>
        <div class="ready-q">{$game.slide.question}</div>
      </div>
    {/if}
  </div>

  <!-- Minimal auto-hiding control bar -->
  <div class="bar" class:hidden={!barVisible}>
    <button class="btn ghost" on:click={back} disabled={!$game.started || $game.finished} title="Previous (←)">←</button>
    <span class="counter">
      {#if $game.started && !$game.finished}{$game.slideIndex + 1} / {$game.totalSlides}{:else if $game.finished}Done{:else}Lobby{/if}
    </span>
    {#if $game.phase === 'active'}
      <span class="answered">{$game.answerCount} answered</span>
    {/if}
    {#if $game.phase === 'revealed' && !isLast}
      <button class="btn ghost" on:click={showLeaderboard} title="Show leaderboard">📊</button>
    {/if}
    {#if actionLabel}
      <button class="btn btn-primary" on:click={advance} title="Advance (Space)" disabled={$game.phase === 'countdown'}>{actionLabel} →</button>
    {/if}
  </div>
</div>

<style>
  .stage { position: relative; height: 100%; width: 100%; overflow: hidden; }
  .content { height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; }
  .revealed { display: flex; flex-direction: column; align-items: center; gap: 2rem; padding: 2rem; width: 100%; }
  .pres { padding: clamp(1rem, 3vw, 2.5rem); max-width: 1400px; width: 100%; font-size: clamp(1.25rem, 2.5vw, 2rem); }
  .get-ready { display: flex; flex-direction: column; align-items: center; gap: 1.5rem; text-align: center; padding: 3rem; }
  .ready-label { font-size: 1.4rem; color: var(--text-faint); text-transform: uppercase; letter-spacing: 3px; }
  .ready-q { font-family: var(--font-display); font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 700; max-width: 900px; }

  .bar {
    position: absolute;
    bottom: 1.2rem;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.5rem 0.7rem;
    background: rgba(0, 0, 0, 0.45);
    border: 1px solid var(--surface-border);
    border-radius: var(--radius-pill);
    backdrop-filter: blur(8px);
    box-shadow: var(--shadow-md);
    transition: opacity 0.4s ease, transform 0.4s ease;
  }
  .bar.hidden { opacity: 0; transform: translateX(-50%) translateY(20px); pointer-events: none; }
  .counter { color: var(--text-dim); font-weight: 600; min-width: 4rem; text-align: center; }
  .answered { color: var(--accent); font-weight: 700; }
  .ghost { background: var(--surface-2); padding: 0.6rem 0.9rem; }
</style>
