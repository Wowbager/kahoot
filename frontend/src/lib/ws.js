import { applyMessage } from '../stores/game.js';

let socket = null;
let listeners = [];
let reconnectTimer = null;
let currentUrl = null;
let closed = false;

export function connectWS(url) {
  closed = false;
  currentUrl = url;
  _connect(url);
}

export function closeWS() {
  closed = true;
  if (socket) {
    socket.close();
    socket = null;
  }
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
}

export function sendWS(data) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(data));
  }
}

export function onWsMessage(fn) {
  listeners.push(fn);
  return () => { listeners = listeners.filter(l => l !== fn); };
}

function _connect(url) {
  socket = new WebSocket(url);
  let retryDelay = 2000;

  socket.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data);
      applyMessage(msg);
      listeners.forEach(fn => fn(msg));
    } catch {}
  };

  socket.onclose = () => {
    if (closed) return;
    reconnectTimer = setTimeout(() => {
      retryDelay = Math.min(retryDelay * 2, 16000);
      _connect(currentUrl);
    }, retryDelay);
  };

  socket.onerror = () => {
    socket.close();
  };
}
