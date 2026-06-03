<script>
  import { onDestroy } from 'svelte';
  export let timeLimit = 30;
  export let startedAt = null; // unix ms

  let remaining = timeLimit;
  let interval;

  $: if (startedAt) {
    clearInterval(interval);
    interval = setInterval(() => {
      const elapsed = (Date.now() - startedAt) / 1000;
      remaining = Math.max(0, timeLimit - elapsed);
      if (remaining <= 0) clearInterval(interval);
    }, 100);
  }

  onDestroy(() => clearInterval(interval));

  $: pct = timeLimit > 0 ? remaining / timeLimit : 0;
  $: color = pct > 0.5 ? '#22c55e' : pct > 0.25 ? '#f59e0b' : '#ef4444';

  const R = 44;
  const CIRC = 2 * Math.PI * R;
  $: dash = pct * CIRC;
</script>

<div class="timer">
  <svg viewBox="0 0 100 100" class="ring">
    <circle cx="50" cy="50" r={R} fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="8" />
    <circle
      cx="50" cy="50" r={R}
      fill="none"
      stroke={color}
      stroke-width="8"
      stroke-dasharray="{dash} {CIRC}"
      stroke-linecap="round"
      transform="rotate(-90 50 50)"
    />
  </svg>
  <span class="num" style="color:{color}">{Math.ceil(remaining)}</span>
</div>

<style>
  .timer { position: relative; width: 100px; height: 100px; }
  .ring { width: 100%; height: 100%; }
  .num {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    font-weight: 700;
  }
</style>
