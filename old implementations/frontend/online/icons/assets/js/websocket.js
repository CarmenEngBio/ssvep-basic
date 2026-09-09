// bci_websocket.js — Comunicación WebSocket con servidor BCI
 

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
    } catch (err) {
      console.error('[WebSocket] Error parseando mensaje:', err);
    }
  };
}
 
// Handlers para mensajes del servidor
 
function handleSessionStarted(msg) {
  console.log('[Session Started] Archivo:', msg.file);
  showMessage('Sesión iniciada - Grabando...', 'success');
  document.getElementById('rec-filename').textContent = 'Grabando: ' + msg.file;
  
  // ✓ Mostrar botón detener, esconder iniciar
  document.getElementById('btn-test').style.display = 'none';
  document.getElementById('btn-stop').style.display = 'block';
}
 
function handleTrialStarted(msg) {
  console.log('[Trial Started] ID:', msg.trial_id, 'Duración:', msg.duration, 's');
  startCountdown(msg.duration);
  showMessage('Trial iniciado, mirando...', 'success');
}
 
function handleSelection(msg) {
  console.log('[Selection] ✓', msg);
 
  // Marcar celda
  var cell = document.getElementById('cell-' + msg.cell_id);
  if (cell) {
    cell.classList.add('selected');
  }
 
  // Mostrar feedback
  showMessage('✓ ' + msg.emoji + ' ' + msg.label + ' - Correlación: ' + msg.correlation.toFixed(4), 'success');
}
 
function handleNoSelection(msg) {
  console.log('[No Selection] Correlación:', msg.correlation.toFixed(4));
  showMessage('✗ No seleccionado (corr: ' + msg.correlation.toFixed(4) + ')', 'error');
}
 
function handleSessionEnded(msg) {
  console.log('[Session Ended]');
  stopCountdown();
  clearCellSelection();
  
  // ✓ Esconder botón detener, mostrar iniciar
  document.getElementById('btn-test').style.display = 'block';
  document.getElementById('btn-stop').style.display = 'none';
  document.getElementById('btn-test').disabled = false;
  
  showMessage('Sesión finalizada', 'success');
}
 
function handleStatus(msg) {
  if (msg.signal_quality) {
    updateSignalQuality(msg.signal_quality);
  }
}
 
// Conectar al cargar SOLO una vez (desde aquí, no desde app.js)
window.addEventListener('load', function() {
  console.log('[App] DOM cargado, conectando WebSocket...');
  // PEQUEÑO DELAY para asegurar que todo está listo
  setTimeout(connect, 100);
});