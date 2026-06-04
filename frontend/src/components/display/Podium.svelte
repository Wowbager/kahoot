<script>
  import { onMount, onDestroy } from 'svelte';
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  export let standings = [];

  // Order on the podium: 2nd (left), 1st (centre, tallest), 3rd (right)
  $: top = standings.slice(0, 3);
  $: ordered = [top[1], top[0], top[2]].filter(Boolean).map((p) => ({
    ...p,
    place: standings.indexOf(p) + 1,
  }));
  const medals = { 1: '🥇', 2: '🥈', 3: '🥉' };
  const heights = { 1: '100%', 2: '72%', 3: '54%' };

  // Suspenseful staged reveal: 3rd → 2nd → winner.
  // step: 0 suspense · 1 reveal 3rd · 2 reveal 2nd · 3 winner spotlight · 4 celebrate
  let step = 0;
  let timers = [];
  // Each place gets a count-up tween that starts when its block is revealed.
  // (Named stores — Svelte can't auto-subscribe to a store looked up dynamically.)
  const score1 = tweened(0, { duration: 1100, easing: cubicOut });
  const score2 = tweened(0, { duration: 900, easing: cubicOut });
  const score3 = tweened(0, { duration: 900, easing: cubicOut });
  $: scoreVals = { 1: $score1, 2: $score2, 3: $score3 };

  function scoreOf(place) {
    const row = standings[place - 1];
    return row ? row.score : 0;
  }

  let audio;
  onMount(() => {
    timers.push(setTimeout(() => { step = 1; score3.set(scoreOf(3)); }, 900));
    timers.push(setTimeout(() => { step = 2; score2.set(scoreOf(2)); }, 2200));
    // Winner reveal — punctuate it with the outro fanfare.
    timers.push(setTimeout(() => { step = 3; audio?.play?.().catch(() => {}); }, 3600));
    timers.push(setTimeout(() => { step = 4; score1.set(scoreOf(1)); }, 4100));
  });
  onDestroy(() => timers.forEach(clearTimeout));

  const revealStep = { 1: 3, 2: 2, 3: 1 }; // place -> step at which it appears
  $: winner = top[0];

  // Confetti: a continuous gentle fall plus a celebratory burst on the winner reveal.
  const PALETTE = ['#e84393', '#1368ce', '#ffa602', '#26890c', '#fbbf24'];
  const confetti = Array.from({ length: 120 }, (_, i) => ({
    left: Math.random() * 100,
    delay: Math.random() * 3,
    dur: 2.5 + Math.random() * 2.5,
    color: PALETTE[i % PALETTE.length],
    size: 6 + Math.random() * 8,
  }));
</script>

<audio src="/sounds/outro.mp3" bind:this={audio}></audio>

<div class="podium-screen">
  {#if step >= 4}
    <div class="confetti">
      {#each confetti as c}
        <span
          style="left:{c.left}%;animation-delay:{c.delay}s;animation-duration:{c.dur}s;background:{c.color};width:{c.size}px;height:{c.size}px"
        ></span>
      {/each}
    </div>
  {/if}

  {#if step < 3}
    <h1 class="headline suspense">And the winner is…</h1>
  {:else}
    <h1 class="headline champ">🏆 {winner?.nickname ?? 'Champion'}</h1>
  {/if}

  <div class="stage">
    {#each ordered as p (p.nickname)}
      <div class="slot place-{p.place}" class:revealed={step >= revealStep[p.place]} class:isWinner={p.place === 1 && step >= 3}>
        {#if p.place === 1 && step >= 3}<div class="crown">👑</div>{/if}
        <div class="medal">{medals[p.place]}</div>
        <div class="name">{p.nickname}</div>
        <div class="score">{Math.round(scoreVals[p.place] ?? 0).toLocaleString()}</div>
        <div class="block" style="height:{heights[p.place]}">
          {#if p.place === 1}<div class="spotlight"></div>{/if}
          <span class="place-num">{p.place}</span>
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .podium-screen {
    position: relative;
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    padding: 2rem 2rem 0;
    overflow: hidden;
  }
  .headline {
    font-family: var(--font-display);
    font-size: clamp(2.8rem, 6.5vw, 5.5rem);
    margin-bottom: 2rem;
    color: var(--accent);
    text-shadow: 0 4px 20px rgba(0,0,0,0.4);
    text-align: center;
  }
  .headline.suspense { color: var(--text-dim); animation: pulse 1.2s ease-in-out infinite; }
  .headline.champ { animation: champIn 0.6s cubic-bezier(0.2, 1.2, 0.4, 1) both; text-shadow: 0 0 40px rgba(251,191,36,0.5); }
  @keyframes pulse { 0%, 100% { opacity: 0.55; } 50% { opacity: 1; } }
  @keyframes champIn { 0% { transform: scale(0.7); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

  .stage {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: clamp(1rem, 3vw, 3rem);
    height: 60vh;
    width: 100%;
    max-width: 900px;
  }
  .slot {
    display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
    flex: 1; max-width: 240px; position: relative;
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.5s ease, transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
  }
  .slot.revealed { opacity: 1; transform: translateY(0); }
  .crown { font-size: clamp(2rem, 4vw, 3rem); animation: crownDrop 0.7s cubic-bezier(0.2, 1.4, 0.4, 1) both; }
  @keyframes crownDrop { 0% { transform: translateY(-40px) scale(0.4); opacity: 0; } 70% { transform: translateY(4px) scale(1.1); } 100% { transform: translateY(0) scale(1); opacity: 1; } }
  .medal { font-size: clamp(2.6rem, 6vw, 4.5rem); }
  .name { font-family: var(--font-display); font-weight: 800; font-size: clamp(1.5rem, 3.2vw, 2.8rem); text-align: center; }
  .score { color: var(--accent); font-weight: 800; font-size: clamp(1.3rem, 2.6vw, 2.2rem); margin-bottom: 0.7rem; }
  .block {
    width: 100%;
    border-radius: 14px 14px 0 0;
    background: linear-gradient(180deg, var(--primary), var(--primary-700));
    box-shadow: var(--shadow-lg);
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 0.6rem;
    transform-origin: bottom;
    position: relative;
    overflow: visible;
  }
  .place-1 .block { background: linear-gradient(180deg, #fbbf24, #d97706); }
  .isWinner .block { box-shadow: var(--shadow-lg), 0 0 60px rgba(251, 191, 36, 0.55); animation: winnerGlow 2s ease-in-out infinite; }
  @keyframes winnerGlow {
    0%, 100% { box-shadow: var(--shadow-lg), 0 0 50px rgba(251, 191, 36, 0.45); }
    50% { box-shadow: var(--shadow-lg), 0 0 80px rgba(251, 191, 36, 0.75); }
  }
  .spotlight {
    position: absolute;
    left: 50%;
    bottom: 0;
    width: 320%;
    height: 200%;
    transform: translateX(-50%);
    background: radial-gradient(ellipse at bottom, rgba(251, 191, 36, 0.35), transparent 65%);
    pointer-events: none;
    z-index: -1;
    animation: fadeIn 0.8s ease both;
  }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  .place-num { font-family: var(--font-display); font-weight: 800; font-size: clamp(2rem, 4vw, 3.5rem); color: rgba(255,255,255,0.85); }

  .confetti { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
  .confetti span {
    position: absolute;
    top: -20px;
    border-radius: 2px;
    will-change: transform;
    animation-name: fall;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
  }
  @keyframes fall {
    0% { transform: translateY(-20px) rotate(0deg); opacity: 1; }
    100% { transform: translateY(105vh) rotate(540deg); opacity: 0.9; }
  }

  @media (prefers-reduced-motion: reduce) {
    .slot { transition: none; opacity: 1; transform: none; }
    .headline.suspense, .headline.champ, .crown, .isWinner .block, .spotlight { animation: none; }
    .confetti { display: none; }
  }
</style>
