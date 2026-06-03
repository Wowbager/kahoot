<script>
  import { onDestroy } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { connectWS, closeWS } from '../lib/ws.js';
  import { game } from '../stores/game.js';
  import { session } from '../stores/session.js';
  import SlideControls from '../components/presenter/SlideControls.svelte';
  import PlayerList from '../components/presenter/PlayerList.svelte';
  import Markdown from '../components/Markdown.svelte';
  import Leaderboard from '../components/display/Leaderboard.svelte';

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

  $: isQuestion = ['true_false','single_choice','multiple_choice','number_slider','multiple_matching'].includes($game.slide?.type);
  $: showLeaderboard = $game.leaderboard?.length > 0 && $game.phase === 'revealed';
</script>

<div class="presenter">
  <!-- Header -->
  <header>
    <span class="title">{$game.title || 'Loading…'}</span>
    <span class="code">Code: <strong>{code}</strong></span>
  </header>

  <!-- Main area -->
  <main>
    <!-- Slide preview -->
    <div class="slide-preview">
      {#if $game.slide?.type === 'presentation'}
        <Markdown content={$game.slide.content} />
      {:else if $game.slide}
        <div class="question-preview">
          <p class="qtype">{$game.slide.type?.replace(/_/g,' ').toUpperCase()}</p>
          <p class="qtext">{$game.slide.question}</p>
          {#if $game.slide.options}
            <ul>
              {#each $game.slide.options as opt, i}
                <li class:correct={$game.slide.correct?.includes(i)}>{opt}</li>
              {/each}
            </ul>
          {:else if $game.slide.type === 'true_false'}
            <p>Correct: <strong>{$game.slide.correct ? 'True' : 'False'}</strong></p>
          {:else if $game.slide.type === 'number_slider'}
            <p>Range: {$game.slide.min} – {$game.slide.max} | Correct: <strong>{$game.slide.correct}</strong></p>
          {:else if $game.slide.type === 'multiple_matching'}
            <ul>
              {#each ($game.slide.pairs ?? []) as pair}
                <li>{pair.left} → {pair.right}</li>
              {/each}
            </ul>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Leaderboard after reveal -->
    {#if showLeaderboard}
      <div class="lb-panel">
        <Leaderboard standings={$game.leaderboard} />
      </div>
    {/if}
  </main>

  <!-- Sidebar -->
  <aside>
    <SlideControls
      slideIndex={$game.slideIndex}
      totalSlides={$game.totalSlides}
      phase={$game.phase}
      isQuestionSlide={isQuestion}
    />
    <PlayerList players={$game.players} answerCount={$game.answerCount} />
  </aside>
</div>

<style>
  .presenter {
    display: grid;
    grid-template-rows: auto 1fr;
    grid-template-columns: 1fr 280px;
    grid-template-areas: "hdr hdr" "main side";
    height: 100%;
    gap: 0;
  }
  header {
    grid-area: hdr;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.8rem 1.5rem;
    background: rgba(0,0,0,0.3);
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }
  .title { font-weight: 700; font-size: 1.1rem; }
  .code { font-size: 0.9rem; color: #aaa; }
  .code strong { color: #7c3aed; font-size: 1.3rem; letter-spacing: 2px; }
  main {
    grid-area: main;
    padding: 1.5rem;
    overflow-y: auto;
    display: flex;
    gap: 1.5rem;
  }
  .slide-preview {
    flex: 1;
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 1.5rem;
    overflow-y: auto;
  }
  .question-preview { display: flex; flex-direction: column; gap: 0.8rem; }
  .qtype { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
  .qtext { font-size: 1.2rem; font-weight: 600; }
  ul { list-style: none; display: flex; flex-direction: column; gap: 0.4rem; }
  li { padding: 0.4rem 0.8rem; background: rgba(255,255,255,0.06); border-radius: 6px; font-size: 0.9rem; }
  li.correct { background: rgba(34,197,94,0.2); color: #86efac; }
  .lb-panel { width: 300px; }
  aside {
    grid-area: side;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    background: rgba(0,0,0,0.2);
    border-left: 1px solid rgba(255,255,255,0.06);
    overflow-y: auto;
  }
</style>
