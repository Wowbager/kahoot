import { writable } from 'svelte/store';

export const game = writable({
  phase: 'idle',         // idle | active | revealed
  slideIndex: 0,
  totalSlides: 0,
  slide: null,
  title: '',
  players: [],
  answerCount: 0,
  questionStartedAt: null,  // unix ms
  timeLimit: 0,
  myAnswer: null,
  myScore: 0,
  distribution: null,
  leaderboard: [],
  results: null,
});

export function applyMessage(msg) {
  game.update(g => {
    switch (msg.type) {
      case 'session_state':
        return {
          ...g,
          phase: msg.phase,
          slideIndex: msg.slide_index,
          totalSlides: msg.total_slides,
          slide: msg.slide,
          title: msg.title,
          players: msg.players || [],
          answerCount: msg.answer_count || 0,
          questionStartedAt: msg.question_started_at || null,
          timeLimit: msg.time_limit || 0,
          myAnswer: null,
          distribution: null,
          results: null,
        };

      case 'slide_changed':
        return {
          ...g,
          slideIndex: msg.slide_index,
          totalSlides: msg.total_slides,
          slide: msg.slide,
          phase: 'idle',
          answerCount: 0,
          myAnswer: null,
          questionStartedAt: null,
          distribution: null,
          results: null,
        };

      case 'question_start':
        return {
          ...g,
          phase: 'active',
          slide: msg.slide,
          slideIndex: msg.slide_index,
          questionStartedAt: msg.started_at,
          timeLimit: msg.time_limit,
          myAnswer: null,
          answerCount: 0,
          distribution: null,
          results: null,
        };

      case 'answer_accepted':
        return { ...g, myAnswer: '__submitted__' };

      case 'answer_update':
        return { ...g, answerCount: msg.count };

      case 'reveal':
        return {
          ...g,
          phase: 'revealed',
          myAnswer: msg.your_answer,
          myScore: msg.total_score,
          results: {
            correct: msg.correct,
            isCorrect: msg.is_correct,
            scoreDelta: msg.score_delta,
          },
        };

      case 'question_revealed':
        return {
          ...g,
          phase: 'revealed',
          distribution: msg.distribution,
          leaderboard: msg.leaderboard || [],
          results: { correct: msg.correct },
        };

      case 'leaderboard':
        return { ...g, leaderboard: msg.standings || [] };

      case 'player_joined':
      case 'player_left':
        return { ...g, players: msg.players || g.players };

      default:
        return g;
    }
  });
}
