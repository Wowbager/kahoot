<script>
  import { onMount, onDestroy } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';
  import { connectWS, closeWS, sendWS, onWsMessage } from '../lib/ws.js';
  import { game } from '../stores/game.js';
  import WaitingScreen from '../components/player/WaitingScreen.svelte';
  import AnswerButtons from '../components/player/AnswerButtons.svelte';
  import SliderInput from '../components/player/SliderInput.svelte';
  import MatchingInput from '../components/player/MatchingInput.svelte';
  import ScoreReveal from '../components/player/ScoreReveal.svelte';

  export let params = {};
  const code = params.code;
  const nickname = decodeURIComponent(params.nickname || '');

  let errored = '';

  if (code && nickname) {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    connectWS(`${proto}://${location.host}/ws/player/${code}/${encodeURIComponent(nickname)}`);
  }

  const off = onWsMessage((msg) => {
    if (msg.type === 'error') {
      errored = msg.message || 'Could not join the game.';
      closeWS();
    }
  });

  // Tick for countdown
  let _now = Date.now();
  let _nowTick;
  onMount(() => { _nowTick = setInterval(() => { _now = Date.now(); }, 100); });
  onDestroy(() => { off(); closeWS(); clearInterval(_nowTick); });

  function submitAnswer(answer) {
    sendWS({ type: 'submit_answer', answer });
  }

  function ordinal(n) {
    return n + (n === 1 ? 'st' : n === 2 ? 'nd' : n === 3 ? 'rd' : 'th');
  }

  const TYPE_LABELS = {
    true_false: 'True / False',
    single_choice: 'Single Choice',
    multiple_choice: 'Multiple Choice',
    number_slider: 'Number Slider',
    multiple_matching: 'Matching',
  };

  $: submitted = $game.myAnswer !== null && $game.myAnswer !== undefined;
  $: slide = $game.slide;
  $: questionDeadline = $game.questionStartedAt && $game.timeLimit
    ? $game.questionStartedAt + ($game.timeLimit * 1000)
    : null;
  $: timeExpired = questionDeadline !== null && _now >= questionDeadline;
  // In preview until the server opens answering (it emits the open moment), or once time has run out.
  $: inPreview = $game.phase === 'countdown' || ($game.phase === 'active' && (!$game.answersOpen || timeExpired));
  // Countdown until answering opens; the server emits the open moment.
  $: countdown = (($game.phase === 'countdown' || ($game.phase === 'active' && !$game.answersOpen)) && $game.questionStartedAt && _now < $game.questionStartedAt)
    ? Math.ceil(($game.questionStartedAt - _now) / 1000)
    : 0;
  $: showPreview = inPreview && !submitted;
  // Stage 1 shows only the question type; once reveal time passes we move to
  // stage 2 which shows the question text (answers stay hidden until the server opens answering).
  $: showTypeOnly = showPreview && $game.questionRevealAt && _now < $game.questionRevealAt;

  // --- Final-screen reveal ---
  // Hold the player's placement back until the big screen has revealed the top
  // three (its podium reveals 3rd→2nd→winner over ~4.1s), so phones never spoil it.
  const FINAL_REVEAL_DELAY_MS = 4600;
  let finalReady = false;
  let finalDone = false;
  const finalScore = tweened(0, { duration: 1400, easing: cubicOut });
  $: if ($game.phase === 'finished' && !finalDone) {
    finalDone = true;
    setTimeout(() => {
      finalReady = true;
      finalScore.set($game.myScore ?? 0);
    }, FINAL_REVEAL_DELAY_MS);
  }
  $: isWinner = $game.myRank === 1;
  $: medalFor = (r) => (r === 1 ? '🥇' : r === 2 ? '🥈' : r === 3 ? '🥉' : '🎉');
  // Light confetti for top-3 finishers on their own device
  const confetti = Array.from({ length: 36 }, (_, i) => ({
    left: Math.random() * 100,
    delay: Math.random() * 1.2,
    dur: 2.4 + Math.random() * 2,
    color: ['#e84393', '#1368ce', '#ffa602', '#26890c', '#fbbf24'][i % 5],
    size: 6 + Math.random() * 7,
  }));
</script>

<div class="play bg-animated">
  <div class="topbar">
    <span class="nick">{nickname}</span>
    <span class="score">{$game.myScore?.toLocaleString() ?? 0} pts</span>
  </div>

  <div class="content">
    {#if errored}
      <div class="errscreen">
        <div class="big">😕</div>
        <p class="msg">{errored}</p>
        <button class="btn btn-primary" on:click={() => push('/')}>Try again</button>
      </div>

    {:else if $game.phase === 'finished'}
      <div class="final" class:winner={isWinner}>
        {#if (($game.myRank ?? 99) <= 3) && finalReady}
          <div class="confetti">
            {#each confetti as c}
              <span style="left:{c.left}%;animation-delay:{c.delay}s;animation-duration:{c.dur}s;background:{c.color};width:{c.size}px;height:{c.size}px"></span>
            {/each}
          </div>
        {/if}

        {#if !finalReady}
          <div class="calc">Calculating final results…</div>
        {:else}
          <div class="medal">{medalFor($game.myRank)}</div>
          <div class="place">{$game.myRank ? ordinal($game.myRank) : ''}{#if $game.totalPlayers}<span class="of"> of {$game.totalPlayers}</span>{/if}</div>
          <div class="finalscore">{Math.round($finalScore).toLocaleString()}<span class="pts"> pts</span></div>
          <p class="gg">{isWinner ? 'You won! 🏆' : ($game.myRank ?? 99) <= 3 ? 'Podium finish!' : 'Great game!'}</p>
        {/if}
      </div>

    {:else if $game.phase === 'revealed'}
      <ScoreReveal results={$game.results} myScore={$game.myScore} rank={$game.myRank} totalPlayers={$game.totalPlayers} />

    {:else if showTypeOnly}
      <div class="preview">
        <div class="cd-label">Question type</div>
        <div class="type-badge big">{TYPE_LABELS[slide?.type] ?? slide?.type}</div>
        <div class="cd-label">Get ready!</div>
      </div>

    {:else if showPreview}
      <div class="preview">
        <div class="type-badge">{TYPE_LABELS[slide?.type] ?? slide?.type}</div>
        <div class="preview-q">{slide?.question ?? ''}</div>
        <div class="cdnum">{countdown}</div>
        <div class="cd-label">{timeExpired ? "Time's up!" : 'Get ready!'}</div>
      </div>

    {:else if $game.phase === 'active' && slide}
      {#if submitted}
        <div class="submitted-wait">
          <div class="check">✓</div>
          <p>Answer received!</p>
          <p class="sub">Look up at the screen…</p>
        </div>
      {:else if slide.type === 'true_false' || slide.type === 'single_choice' || slide.type === 'multiple_choice'}
        <AnswerButtons {slide} {submitted} on:answer={(e) => submitAnswer(e.detail)} />
      {:else if slide.type === 'number_slider'}
        <SliderInput {slide} {submitted} on:answer={(e) => submitAnswer(e.detail)} />
      {:else if slide.type === 'multiple_matching'}
        <MatchingInput {slide} {submitted} on:answer={(e) => submitAnswer(e.detail)} />
      {/if}

    {:else}
      <WaitingScreen
        message={slide?.type === 'presentation' ? 'Watch the screen' : 'Get ready…'}
        playerCount={$game.players?.length}
      />
    {/if}
  </div>
</div>

<style>
  .play { display: flex; flex-direction: column; height: 100%; }
  .topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.7rem 1rem;
    background: rgba(0, 0, 0, 0.35);
    border-bottom: 1px solid var(--surface-border);
  }
  .nick { font-size: 0.95rem; color: var(--text-dim); font-weight: 700; }
  .score { font-size: 1rem; color: var(--accent); font-weight: 800; }
  .content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

  .submitted-wait, .errscreen, .final {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 100%; gap: 1rem; text-align: center; padding: 2rem; color: var(--text-dim);
  }
  .check { font-size: 5rem; color: var(--correct); animation: pop 0.3s ease; }
  @keyframes pop { 0% { transform: scale(0); } 70% { transform: scale(1.2); } 100% { transform: scale(1); } }
  .sub { font-size: 0.9rem; color: var(--text-faint); }
  .errscreen .big { font-size: 4rem; }
  .errscreen .msg { font-size: 1.1rem; color: var(--text); }

  .final { position: relative; overflow: hidden; }
  .final .calc {
    font-family: var(--font-display);
    font-size: 1.3rem;
    color: var(--text-dim);
    letter-spacing: 1px;
    animation: pulse 1.1s ease-in-out infinite;
  }
  .final .medal { font-size: 5.5rem; animation: medalIn 0.7s cubic-bezier(0.2, 1.3, 0.4, 1) both; }
  .final .place {
    font-family: var(--font-display);
    font-size: clamp(2.4rem, 11vw, 3.2rem);
    font-weight: 800;
    color: var(--text);
    animation: riseIn 0.5s ease both 0.1s;
  }
  .final .place .of { font-size: 0.5em; color: var(--text-faint); font-weight: 700; }
  .final .finalscore {
    font-family: var(--font-display);
    font-size: clamp(2.2rem, 10vw, 3rem);
    font-weight: 800;
    color: var(--accent);
    animation: riseIn 0.5s ease both 0.2s;
  }
  .final .finalscore .pts { font-size: 0.45em; color: var(--text-faint); font-weight: 700; }
  .final .gg { color: var(--text-dim); animation: riseIn 0.5s ease both 0.3s; }
  .final.winner .medal { filter: drop-shadow(0 0 22px rgba(251, 191, 36, 0.65)); }
  .final.winner .place { color: var(--accent); text-shadow: 0 0 26px rgba(251, 191, 36, 0.45); }
  p { font-size: 1.2rem; }

  @keyframes medalIn { 0% { transform: scale(0) rotate(-30deg); opacity: 0; } 100% { transform: scale(1) rotate(0); opacity: 1; } }
  @keyframes riseIn { from { transform: translateY(14px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

  .confetti { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
  .confetti span {
    position: absolute;
    top: -16px;
    border-radius: 2px;
    will-change: transform;
    animation-name: cfall;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
  }
  @keyframes cfall {
    0% { transform: translateY(-16px) rotate(0deg); opacity: 1; }
    100% { transform: translateY(105vh) rotate(540deg); opacity: 0.9; }
  }

  /* Countdown preview */
  .preview {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 1.2rem;
    padding: 2rem;
    text-align: center;
  }
  .type-badge {
    background: var(--primary, #7c3aed);
    color: #fff;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 0.3rem 1rem;
    border-radius: 999px;
  }
  .type-badge.big {
    font-size: clamp(1.3rem, 7vw, 2.2rem);
    letter-spacing: 3px;
    padding: 0.8rem 2rem;
    animation: pulse 1.2s ease-in-out infinite;
  }
  .preview-q {
    font-family: var(--font-display, sans-serif);
    font-size: clamp(1.1rem, 5vw, 1.6rem);
    font-weight: 700;
    color: var(--text, #fff);
    max-width: 340px;
  }
  .cdnum {
    font-family: var(--font-display, sans-serif);
    font-size: clamp(5rem, 20vw, 8rem);
    font-weight: 900;
    color: var(--primary, #7c3aed);
    line-height: 1;
    animation: pulse 1s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.08); opacity: 0.85; }
  }
  .cd-label { font-size: 0.9rem; color: var(--text-faint); text-transform: uppercase; letter-spacing: 2px; }

  @media (prefers-reduced-motion: reduce) {
    .medal, .place, .finalscore, .gg, .calc, .type-badge.big, .cdnum { animation: none !important; }
    .confetti { display: none; }
  }
</style>
