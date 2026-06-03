import { writable } from 'svelte/store';

function createSessionStore() {
  const stored = sessionStorage.getItem('kahoot_session');
  const initial = stored ? JSON.parse(stored) : {
    sessionCode: null,
    presenterToken: null,
    nickname: null,
    role: null, // 'presenter' | 'player' | 'display'
  };
  const { subscribe, set, update } = writable(initial);

  return {
    subscribe,
    set(val) {
      sessionStorage.setItem('kahoot_session', JSON.stringify(val));
      set(val);
    },
    update(fn) {
      update(v => {
        const next = fn(v);
        sessionStorage.setItem('kahoot_session', JSON.stringify(next));
        return next;
      });
    },
    clear() {
      sessionStorage.removeItem('kahoot_session');
      set({ sessionCode: null, presenterToken: null, nickname: null, role: null });
    },
  };
}

export const session = createSessionStore();
