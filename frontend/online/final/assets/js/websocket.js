// websocket.js 
 
var WS_URL = 'ws://localhost:8765';
var RETRY_MS = 2000;
var socket = null;
 
function connect() {
  console.log('[WebSocket] Trying to connect to' + WS_URL);
  socket = new WebSocket(WS_URL);
 
  socket.onopen = function() {
    console.log('[WebSocket] ✓ Connected');
    setConnectionStatus('connected');
  };
 
  socket.onclose = function() {
    console.log('[WebSocket] Disconnected, reattempting in' + RETRY_MS + 'ms...');
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
      console.error('[WebSocket] Error with exchanged message:', err);
    }
  };
}
 
/*
function handleSessionStarted(msg) {
  console.log('[Session Started] File:', msg.file);
  showMessage('✓ Session started - Recording ...', 'success');
  document.getElementById('rec-filename').textContent = 'Recording: ' + msg.file;
  
  document.getElementById('btn-test').style.display = 'none';
  document.getElementById('btn-stop').style.display = 'block';
}
*/
 
function handleBlockStarted(msg) {
  console.log('[Block Started] ID:', msg.cell_id, 'Label:', msg.label, 'Freq:', msg.freq);

  showMessage('✓ Recording...', 'success');
  if (msg.file) {
    document.getElementById('rec-filename').textContent = 'Recording: ' + msg.file;
  }
  document.getElementById('btn-test').style.display = 'none';
  var btnStop = document.getElementById('btn-stop');
  if (btnStop) btnStop.style.display = 'block';

  var instruction = msg.emoji + ' Look at: ' + msg.label + ' (' + msg.freq + 'Hz)';
  showMessage(instruction, 'info');

  startCountdown(msg.duration);

  clearCellSelection();
  var cell = document.getElementById('cell-' + msg.cell_id);
  if (cell) cell.style.backgroundColor = '#f0f0f0';
}

/*
function handleBlockStarted(msg) {
  console.log('[Block Started] ID:', msg.cell_id, 'Label:', msg.label, 'Freq:', msg.freq);
  
  var instruction = msg.emoji + ' Look at: ' + msg.label + ' (' + msg.freq + 'Hz)';
  showMessage(instruction, 'info');
  
  startCountdown(msg.duration);
  
  clearCellSelection();
  var cell = document.getElementById('cell-' + msg.cell_id);
  if (cell) {
    cell.style.backgroundColor = '#f0f0f0';  // Suave highlight
  }
}
*/
 
function handleBlockResult(msg) {
  console.log('[Block Result]', msg);
  
  //stopCountdown();
  
  var cell = document.getElementById('cell-' + msg.cell_id);
  if (cell) cell.classList.remove('selected'); 
  
  if (msg.correct) {
    // CORRECT
    if (cell) cell.classList.add('selected');
    showMessage(
      'CORRECT ' + msg.emoji + ' ' + msg.label + ' - Corr: ' + msg.correlation.toFixed(4),
      'success'
    );
  } else {
    // INCORRECT
   // if (cell) cell.classList.add('error');
    //var detected = msg.detected_freq ? msg.detected_freq.toFixed(2) : '?';
    //showMessage(
    //  'WRONG' + msg.emoji + ' ' + msg.label + ' - Detected ' + detected + 'Hz (corr: ' + msg.correlation.toFixed(4) + ')',
    //  'error'
    //);
  }
  
  console.log('[All correlations]', msg.all_corrs);
}
 
function handleSessionEnded(msg) {
  console.log('[Session Ended] Accuracy:', msg.accuracy, '%');
  stopCountdown();
  clearCellSelection();
  
  var summary = '✓ Finished session - Accuracy: ' + msg.correct + '/' + msg.total + 
                ' (' + msg.accuracy + '%)';
  showMessage(summary, 'success');
  
  // Stop button is not used
  document.getElementById('btn-test').style.display = 'block';
  document.getElementById('btn-stop').style.display = 'none';
  
  console.log('[Results Summary]', msg.results);
}
 
function handleStatus(msg) {
  // Recording status
  if (msg.recording) {
    // Is recording
  }
  //if (msg.signal_quality !== undefined) {
  //  updateSignalQuality(msg.signal_quality);
  //}
}
 
// Utilities
 
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
 
// connect() is called when webpage is loaded 
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', connect);
} else {
  connect();
}