import { writable } from 'svelte/store';

export const game = writable({
  phase: 'idle',         // idle | countdown | active | revealed | finished
  started: false,        // false while in the pre-game lobby
  finished: false,
  slideIndex: 0,
  totalSlides: 0,
  slide: null,
  title: '',
  code: '',
  players: [],
  answerCount: 0,
  questionStartedAt: null,  // unix ms — when answering opens
  questionRevealAt: null,   // unix ms — when the question text is revealed (stage 2)
  timeLimit: 0,
  answersOpen: false,
  myAnswer: null,
  myScore: 0,
  myRank: null,
  totalPlayers: 0,
  distribution: null,
  leaderboard: [],
  results: null,
  error: '',
});

export function applyMessage(msg) {
  game.update(g => {
    switch (msg.type) {
      case 'session_state':
        return {
          ...g,
          phase: msg.phase,
          started: !!msg.started,
          finished: !!msg.finished,
          slideIndex: msg.slide_index,
          totalSlides: msg.total_slides,
          slide: msg.slide,
          title: msg.title,
          code: msg.code || g.code,
          players: msg.players || [],
          answerCount: msg.answer_count || 0,
          questionStartedAt: msg.question_started_at || null,
          questionRevealAt: msg.reveal_question_at || null,
          timeLimit: msg.time_limit || 0,
          answersOpen: !!msg.answers_open,
          myAnswer: null,
          distribution: null,
          results: null,
        };

      case 'game_started':
        return { ...g, started: true, finished: false, phase: 'idle', answersOpen: false };

      case 'slide_changed':
        return {
          ...g,
          slideIndex: msg.slide_index,
          totalSlides: msg.total_slides,
          slide: msg.slide,
          phase: 'idle',
          answerCount: 0,
          answersOpen: false,
          myAnswer: null,
          questionStartedAt: null,
          questionRevealAt: null,
          distribution: null,
          results: null,
        };

      case 'question_start':
        return {
          ...g,
          phase: 'countdown',
          slide: msg.slide,
          slideIndex: msg.slide_index,
          questionStartedAt: msg.started_at,
          questionRevealAt: msg.reveal_question_at ?? null,
          timeLimit: msg.time_limit,
          answersOpen: !!msg.answers_open,
          myAnswer: null,
          answerCount: 0,
          distribution: null,
          results: null,
        };

      case 'question_open':
        return {
          ...g,
          phase: 'active',
          answersOpen: true,
          slideIndex: msg.slide_index ?? g.slideIndex,
          questionStartedAt: msg.started_at ?? g.questionStartedAt,
          timeLimit: msg.time_limit ?? g.timeLimit,
        };

      case 'answer_accepted':
        return { ...g, myAnswer: '__submitted__' };

      case 'answer_update':
        return { ...g, answerCount: msg.count };

      case 'reveal':
        return {
          ...g,
          phase: 'revealed',
          answersOpen: false,
          myAnswer: msg.your_answer,
          myScore: msg.total_score,
          myRank: msg.rank ?? g.myRank,
          totalPlayers: msg.total_players ?? g.totalPlayers,
          results: {
            correct: msg.correct,
            isCorrect: msg.is_correct,
            scoreDelta: msg.score_delta,
            streak: msg.streak ?? 0,
            streakBonus: msg.streak_bonus ?? 0,
          },
        };

      case 'question_revealed':
        return {
          ...g,
          phase: 'revealed',
          answersOpen: false,
          distribution: msg.distribution,
          leaderboard: msg.leaderboard || [],
          results: { correct: msg.correct },
        };

      case 'leaderboard':
        return { ...g, leaderboard: msg.standings || [] };

      case 'your_rank':
        return { ...g, myRank: msg.rank, totalPlayers: msg.total, myScore: msg.score ?? g.myScore };

      case 'game_over':
        // Stage/display receive `standings`; players receive their own `rank`.
        if (msg.standings) {
          return { ...g, phase: 'finished', finished: true, answersOpen: false, leaderboard: msg.standings };
        }
        return {
          ...g,
          phase: 'finished',
          finished: true,
          answersOpen: false,
          myRank: msg.rank ?? g.myRank,
          totalPlayers: msg.total ?? g.totalPlayers,
          myScore: msg.score ?? g.myScore,
        };

      case 'player_joined':
      case 'player_left':
        return { ...g, players: msg.players || g.players };

      case 'error':
        return { ...g, error: msg.message || 'Something went wrong' };

      default:
        return g;
    }
  });
}
