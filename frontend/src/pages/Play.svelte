<script>
  import { onDestroy } from 'svelte';
  import { connectWS, closeWS, sendWS } from '../lib/ws.js';
  import { game } from '../stores/game.js';
  import WaitingScreen from '../components/player/WaitingScreen.svelte';
  import AnswerButtons from '../components/player/AnswerButtons.svelte';
  import SliderInput from '../components/player/SliderInput.svelte';
  import MatchingInput from '../components/player/MatchingInput.svelte';
  import ScoreReveal from '../components/player/ScoreReveal.svelte';

  export let params = {};
  const code = params.code;
  const nickname = decodeURIComponent(params.nickname || '');

  let wsError = '';

  if (code && nickname) {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    connectWS(`${proto}://${location.host}/ws/player/${code}/${encodeURIComponent(nickname)}`);
  }

  onDestroy(closeWS);

  function submitAnswer(answer) {
    sendWS({ type: 'submit_answer', answer });
  }

  $: submitted = $game.myAnswer !== null && $game.myAnswer !== undefined;
  $: slide = $game.slide;
</script>

<div class="play">
  <!-- Header bar -->
  <div class="topbar">
    <span class="nick">{nickname}</span>
    <span class="score">{$game.myScore?.toLocaleString() ?? 0} pts</span>
  </div>

  <!-- Content area -->
  <div class="content">
    {#if $game.phase === 'revealed'}
      <ScoreReveal results={$game.results} myScore={$game.myScore} />

    {:else if $game.phase === 'active' && slide}

      {#if submitted}
        <!-- Submitted — waiting for reveal -->
        <div class="submitted-wait">
          <div class="check">✓</div>
          <p>Answer received!</p>
          <p class="sub">Waiting for results…</p>
        </div>

      {:else if slide.type === 'true_false' || slide.type === 'single_choice' || slide.type === 'multiple_choice'}
        <AnswerButtons
          {slide}
          submitted={submitted}
          on:answer={(e) => submitAnswer(e.detail)}
        />

      {:else if slide.type === 'number_slider'}
        <SliderInput
          {slide}
          submitted={submitted}
          on:answer={(e) => submitAnswer(e.detail)}
        />

      {:else if slide.type === 'multiple_matching'}
        <MatchingInput
          {slide}
          submitted={submitted}
          on:answer={(e) => submitAnswer(e.detail)}
        />
      {/if}

    {:else}
      <WaitingScreen
        message={slide?.type === 'presentation' ? 'Watch the screen' : 'Waiting for question…'}
        playerCount={$game.players?.length}
      />
    {/if}
  </div>
</div>

<style>
  .play {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #1a1a2e;
  }
  .topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.7rem 1rem;
    background: rgba(0,0,0,0.4);
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }
  .nick { font-size: 0.9rem; color: #ccc; font-weight: 600; }
  .score { font-size: 1rem; color: #fbbf24; font-weight: 700; }
  .content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

  .submitted-wait {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 1rem;
    color: #ccc;
  }
  .check {
    font-size: 5rem;
    color: #22c55e;
    animation: pop 0.3s ease;
  }
  @keyframes pop {
    0% { transform: scale(0); }
    70% { transform: scale(1.2); }
    100% { transform: scale(1); }
  }
  p { font-size: 1.2rem; }
  .sub { font-size: 0.9rem; color: #888; }
</style>
