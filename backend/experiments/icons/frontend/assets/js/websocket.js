// bci_websocket.js — Comunicación WebSocket con servidor BCI
 
var WS_URL = 'ws://localhost:8765';
var RETRY_MS = 2000;
var socket = null;
 
function connect() {
  socket = new WebSocket(WS_URL);
 
  socket.onopen = function() {
    console.log('[WebSocket] Conectado');
    setConnectionStatus('connected');
  };
 
  socket.onclose = function() {
    console.log('[WebSocket] Desconectado, reintentando...');
    setConnectionStatus('disconnected');
    socket = null;
    setTimeout(connect, RETRY_MS);
  };
 
  socket.onerror = function(err) {
    console.error('[WebSocket Error]', err);
    setConnectionStatus('error');
  };
 
  socket.onmessage = function(e) {
    var msg = JSON.parse(e.data);
 
    switch (msg.type) {
      case 'session_started':
        handleSessionStarted(msg);
        break;
      case 'trial_started':
        handleTrialStarted(msg);
        break;
      case 'selection':
        handleSelection(msg);
        break;
      case 'no_selection':
        handleNoSelection(msg);
        break;
      case 'session_ended':
        handleSessionEnded(msg);
        break;
      case 'status':
        handleStatus(msg);
        break;
    }
  };
}
 
function startSession() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      type: 'start_session',
      label: 'bci_vital_' + new Date().getTime()
    }));
  }
}
 
function stopSession() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      type: 'stop_session'
    }));
  }
}
 
// Handlers para mensajes del servidor
function handleSessionStarted(msg) {
  console.log('[Session Started]', msg.file);
  document.getElementById('rec-filename').textContent = 'Grabando: ' + msg.file;
  document.getElementById('btn-start').disabled = true;
  document.getElementById('btn-stop').disabled = false;
  setConnectionStatus('recording');
}
 
function handleTrialStarted(msg) {
  console.log('[Trial Started]', msg.trial_id, 'Duración:', msg.duration, 's');
  startCountdown(msg.duration);
}
 
function handleSelection(msg) {
  console.log('[Selection]', msg);
 
  // Marcar celda como seleccionada
  var cell = document.getElementById('cell-' + msg.cell_id);
  if (cell) {
    cell.classList.add('selected');
  }
 
  // Mostrar feedback
  var feedback = document.getElementById('selection-feedback');
  feedback.textContent = '✓ ' + msg.emoji + ' ' + msg.label + ' SELECCIONADO';
  feedback.classList.remove('error');
 
  var corrDisplay = document.getElementById('correlation-display');
  corrDisplay.textContent =
    'Correlación: ' + msg.correlation.toFixed(4) + ' | ' +
    'Tiempo: ' + msg.time_ms.toFixed(0) + ' ms';
 
  // Log
  logCorrelation(msg.label, msg.correlation, msg.time_ms);
}
 
function handleNoSelection(msg) {
  console.log('[No Selection]', msg);
 
  var feedback = document.getElementById('selection-feedback');
  feedback.textContent = '✗ No se detectó selección. Intenta de nuevo.';
  feedback.classList.add('error');
 
  var corrDisplay = document.getElementById('correlation-display');
  corrDisplay.textContent = 'Correlación máxima: ' + msg.correlation.toFixed(4);
 
  // Log
  logCorrelation('NO SELECTION', msg.correlation, 0);
}
 
function handleSessionEnded(msg) {
  console.log('[Session Ended]');
  stopCountdown();
  document.getElementById('btn-start').disabled = false;
  document.getElementById('btn-stop').disabled = true;
  setConnectionStatus('connected');
}
 
function handleStatus(msg) {
  // Actualizar calidad de señal si es necesario
  if (msg.signal_quality) {
    // Podría añadirse un indicador visual de calidad
  }
}
 
// Utilidades
function setConnectionStatus(state) {
  var el = document.getElementById('status');
 
  switch (state) {
    case 'connected':
      el.textContent = '● Conectado al servidor';
      el.classList.add('connected');
      el.classList.remove('error', 'loading');
      break;
    case 'disconnected':
      el.textContent = '● Desconectado - reintentando...';
      el.classList.add('loading');
      el.classList.remove('connected', 'error');
      break;
    case 'recording':
      el.textContent = '● Grabando sesión...';
      el.classList.add('connected');
      el.classList.remove('error', 'loading');
      break;
    case 'error':
      el.textContent = '● Error de conexión';
      el.classList.add('error');
      el.classList.remove('connected', 'loading');
      break;
  }
}
 
var countdownInterval = null;
 
function startCountdown(seconds) {
  var timer = document.getElementById('timer');
  var remaining = seconds;
  timer.textContent = 'Grabando... ' + remaining + ' s';
 
  if (countdownInterval) clearInterval(countdownInterval);
 
  countdownInterval = setInterval(function() {
    remaining--;
    if (remaining <= 0) {
      clearInterval(countdownInterval);
      timer.textContent = 'Finalizando...';
    } else {
      timer.textContent = 'Grabando... ' + remaining + ' s';
    }
  }, 1000);
}
 
function stopCountdown() {
  if (countdownInterval) clearInterval(countdownInterval);
  document.getElementById('timer').textContent = '';
}
 
function logCorrelation(label, corr, timeMs) {
  var log = document.getElementById('correlations-log');
  var timestamp = new Date().toLocaleTimeString();
  var line = '[' + timestamp + '] ' + label.padEnd(25) +
             ' | Corr: ' + corr.toFixed(4) +
             ' | Tiempo: ' + timeMs.toFixed(0) + ' ms';
 
  log.innerHTML = line + '<br>' + log.innerHTML;
 
  // Limitar el log a 10 líneas
  var lines = log.innerHTML.split('<br>');
  if (lines.length > 10) {
    lines = lines.slice(0, 10);
    log.innerHTML = lines.join('<br>');
  }
}
 
// Conectar al cargar la página
window.addEventListener('load', function() {
  connect();
});