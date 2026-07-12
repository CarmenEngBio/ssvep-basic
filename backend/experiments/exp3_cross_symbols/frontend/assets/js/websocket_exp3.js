var WS_URL   = 'ws://localhost:8765';
var RETRY_MS = 2000;

var socket = null;

function connect() {
  socket = new WebSocket(WS_URL);

  socket.onopen = function() {
    setConnectionStatus('connected');
  };

  socket.onclose = function() {
    setConnectionStatus('disconnected');
    socket = null;
    setTimeout(connect, RETRY_MS);
  };

  socket.onmessage = function(e) {
    var msg = JSON.parse(e.data);
    if (msg.type === 'recording_started' || msg.type === 'recording_stopped') {
      handleRecordingMessage(msg);
    }
    // msg.type === 'status' es el latido periódico (calidad de señal);
    // no requiere acción visual en esta versión reducida.
  };
}

function startTest() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: 'start_recording', label: 'test_celda1' }));
  }
}
