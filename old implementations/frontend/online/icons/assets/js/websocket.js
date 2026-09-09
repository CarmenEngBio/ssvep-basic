// BCI websocket.js
 

var WS_URL = 'ws://localhost:8765';
var RETRY_MS = 2000;
var socket = null;
 
function connect() {
  console.log('[WebSocket] Attempting to connect to ' + WS_URL);
  socket = new WebSocket(WS_URL);
 
  socket.onopen = function() {
    console.log('[WebSocket] ✓ Connected');
    setConnectionStatus('connected');
  };
 
  socket.onclose = function() {
    console.log('[WebSocket] Disconnected, reattempting in ' + RETRY_MS + 'ms...');
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
      console.log('[WebSocket] Message:', msg.type, msg);
 
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
      console.error('[WebSocket] Error message:', err);
    }
  };
}
 
 
function handleSessionStarted(msg) {
  console.log('[Session Started] File:', msg.file);
  showMessage('Started session - Recording...', 'success');
  document.getElementById('rec-filename').textContent = 'Recording: ' + msg.file;
  
  document.getElementById('btn-test').style.display = 'none';
  document.getElementById('btn-stop').style.display = 'block';
}
 
function handleTrialStarted(msg) {
  console.log('[Trial Started] ID:', msg.trial_id, 'Timing:', msg.duration, 's');
  startCountdown(msg.duration);
  showMessage('Trial initialised, looking at...', 'success');
}
 
function handleSelection(msg) {
  console.log('[Selection] ✓', msg);
 
  var cell = document.getElementById('cell-' + msg.cell_id);
  if (cell) {
    cell.classList.add('selected');
  }
 
  showMessage('✓ ' + msg.emoji + ' ' + msg.label + ' - Correlation: ' + msg.correlation.toFixed(4), 'success');
}
 
function handleNoSelection(msg) {
  console.log('[No Selection] Correlation:', msg.correlation.toFixed(4));
  showMessage('✗ Not selected (corr: ' + msg.correlation.toFixed(4) + ')', 'error');
}
 
function handleSessionEnded(msg) {
  console.log('[Session Ended]');
  stopCountdown();
  clearCellSelection();
  
  document.getElementById('btn-test').style.display = 'block';
  document.getElementById('btn-stop').style.display = 'none';
  document.getElementById('btn-test').disabled = false;
  
  showMessage('Finished Session', 'success');
}
 
function handleStatus(msg) {
  if (msg.signal_quality) {
    updateSignalQuality(msg.signal_quality);
  }
}
 
window.addEventListener('load', function() {
  console.log('[App] DOM loaded, connecting with WebSocket...');
  setTimeout(connect, 100);
});