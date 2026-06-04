<script>
    import { onMount } from "svelte";

  export let standings = [];

  // Order on the podium: 2nd (left), 1st (centre, tallest), 3rd (right)
  $: top = standings.slice(0, 3);
  $: ordered = [top[1], top[0], top[2]].filter(Boolean).map((p) => ({
    ...p,
    place: standings.indexOf(p) + 1,
  }));
  const medals = { 1: '🥇', 2: '🥈', 3: '🥉' };
  const heights = { 1: '100%', 2: '72%', 3: '54%' };

  // A handful of confetti pieces with randomised timing/position
  const confetti = Array.from({ length: 60 }, (_, i) => ({
    left: Math.random() * 100,
    delay: Math.random() * 3,
    dur: 2.5 + Math.random() * 2.5,
    color: ['#e84393', '#1368ce', '#ffa602', '#26890c', '#fbbf24'][i % 5],
    size: 6 + Math.random() * 8,
  }));

  onMount(() => {
    audio.play();
  });

  let audio;
</script>

<audio src="/sounds/outro.mp3" bind:this={audio}></audio>

<div class="podium-screen">
  <div class="confetti">
    {#each confetti as c}
      <span
        style="left:{c.left}%;animation-delay:{c.delay}s;animation-duration:{c.dur}s;background:{c.color};width:{c.size}px;height:{c.size}px"
      ></span>
    {/each}
  </div>

  <h1 class="headline">🏆 Final Results</h1>

  <div class="stage">
    {#each ordered as p}
      <div class="slot place-{p.place}">
        <div class="medal">{medals[p.place]}</div>
        <div class="name">{p.nickname}</div>
        <div class="score">{p.score.toLocaleString()}</div>
        <div class="block" style="height:{heights[p.place]}">
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
    font-size: clamp(2rem, 5vw, 3.5rem);
    margin-bottom: 2rem;
    color: var(--accent);
    text-shadow: 0 4px 20px rgba(0,0,0,0.4);
  }
  .stage {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: clamp(1rem, 3vw, 3rem);
    height: 60vh;
    width: 100%;
    max-width: 900px;
  }
  .slot { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; flex: 1; max-width: 240px; }
  .medal { font-size: clamp(2rem, 5vw, 3.5rem); }
  .name { font-family: var(--font-display); font-weight: 700; font-size: clamp(1.1rem, 2.4vw, 1.8rem); text-align: center; }
  .score { color: var(--accent); font-weight: 700; font-size: clamp(1rem, 2vw, 1.4rem); margin-bottom: 0.6rem; }
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
    animation: rise 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) backwards;
  }
  .place-1 .block { background: linear-gradient(180deg, #fbbf24, #d97706); animation-delay: 0.45s; }
  .place-2 .block { animation-delay: 0.2s; }
  .place-3 .block { animation-delay: 0s; }
  .place-num { font-family: var(--font-display); font-weight: 800; font-size: 2rem; color: rgba(255,255,255,0.85); }
  @keyframes rise { from { transform: scaleY(0); opacity: 0; } to { transform: scaleY(1); opacity: 1; } }

  .confetti { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
  .confetti span {
    position: absolute;
    top: -20px;
    border-radius: 2px;
    animation-name: fall;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
  }
  @keyframes fall {
    0% { transform: translateY(-20px) rotate(0deg); opacity: 1; }
    100% { transform: translateY(105vh) rotate(540deg); opacity: 0.9; }
  }
</style>
