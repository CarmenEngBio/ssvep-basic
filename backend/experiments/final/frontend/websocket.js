// websocket.js — Comunicación WebSocket actualizada para exp2+online
 
var WS_URL = 'ws://localhost:8765';
var RETRY_MS = 2000;
var socket = null;
 
function connect() {
  console.log('[WebSocket] Intentando conectar a ' + WS_URL);
  socket = new WebSocket(WS_URL);
 
  socket.onopen = function() {
    console.log('[WebSocket] ✓ Conectado');
    setConnectionStatus('connected');
  };
 
  socket.onclose = function() {
    console.log('[WebSocket] Desconectado, reintentando en ' + RETRY_MS + 'ms...');
    setConnectionStatus('disconnected');
    socket = null;
    setTimeout(connect, RETRY_MS);
  };
 
  socket.onerror = function(err) {
    console.error('[WebSocket] ✗ Error:', err);
    setConnectionStatus('error');
  };
 
  socket.onmessage = function(e) {
    try {
      var msg = JSON.parse(e.data);
      console.log('[WebSocket] Mensaje:', msg.type, msg);
 
      switch (msg.type) {
        case 'session_started':
          handleSessionStarted(msg);
          break;
        case 'block_started':
          handleBlockStarted(msg);
          break;
        case 'block_result':
          handleBlockResult(msg);
          break;
        case 'session_ended':
          handleSessionEnded(msg);
          break;
        case 'status':
          handleStatus(msg);
          break;
      }
    } catch (err) {
      console.error('[WebSocket] Error parseando mensaje:', err);
    }
  };
}
 
// ========================================================
// HANDLERS PARA EXP2 + ONLINE
// ========================================================
 
function handleSessionStarted(msg) {
  console.log('[Session Started] Archivo:', msg.file);
  showMessage('✓ Sesión iniciada - Grabando...', 'success');
  document.getElementById('rec-filename').textContent = 'Grabando: ' + msg.file;
  
  // Mostrar botón detener, esconder iniciar
  document.getElementById('btn-test').style.display = 'none';
  document.getElementById('btn-stop').style.display = 'block';
}
 
function handleBlockStarted(msg) {
  console.log('[Block Started] ID:', msg.cell_id, 'Label:', msg.label, 'Freq:', msg.freq);
  
  // Mostrar instrucción
  var instruction = msg.emoji + ' Mira: ' + msg.label + ' (' + msg.freq + 'Hz)';
  showMessage(instruction, 'info');
  
  // Iniciar countdown
  startCountdown(msg.duration);
  
  // Destacar celda actual
  clearCellSelection();
  var cell = document.getElementById('cell-' + msg.cell_id);
  if (cell) {
    cell.style.backgroundColor = '#f0f0f0';  // Suave highlight
  }
}
 
function handleBlockResult(msg) {
  console.log('[Block Result]', msg);
  
  // Detener countdown
  stopCountdown();
  
  var cell = document.getElementById('cell-' + msg.cell_id);
  
  if (msg.correct) {
    // ✅ CORRECTO
    if (cell) cell.classList.add('selected');
    showMessage(
      '✅ ' + msg.emoji + ' ' + msg.label + ' - Corr: ' + msg.correlation.toFixed(4),
      'success'
    );
  } else {
    // ❌ INCORRECTO
    if (cell) cell.classList.add('error');
    var detected = msg.detected_freq ? msg.detected_freq.toFixed(2) : '?';
    showMessage(
      '❌ ' + msg.emoji + ' ' + msg.label + ' - Detectó ' + detected + 'Hz (corr: ' + msg.correlation.toFixed(4) + ')',
      'error'
    );
  }
  
  console.log('[All correlations]', msg.all_corrs);
}
 
function handleSessionEnded(msg) {
  console.log('[Session Ended] Precisión:', msg.accuracy, '%');
  stopCountdown();
  clearCellSelection();
  
  var summary = '✓ Sesión finalizada - Precisión: ' + msg.correct + '/' + msg.total + 
                ' (' + msg.accuracy + '%)';
  showMessage(summary, 'success');
  
  // Mostrar botón iniciar, esconder detener
  document.getElementById('btn-test').style.display = 'block';
  document.getElementById('btn-stop').style.display = 'none';
  
  // Log detallado de resultados
  console.log('[Results Summary]', msg.results);
}
 
function handleStatus(msg) {
  // Actualizar estado de grabación
  if (msg.recording) {
    // Está grabando
  }
  // Actualizar calidad de señal
  if (msg.signal_quality !== undefined) {
    updateSignalQuality(msg.signal_quality);
  }
}
 
// ========================================================
// FUNCIONES DE UTILIDAD
// ========================================================
 
var stopCountdownInterval = null;
 
function stopCountdown() {
  if (stopCountdownInterval) {
    clearInterval(stopCountdownInterval);
    stopCountdownInterval = null;
  }
  var timer = document.getElementById('timer');
  if (timer) {
    timer.textContent = '';
  }
}
 
// Llamar connect() cuando se carga la página
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', connect);
} else {
  connect();
}