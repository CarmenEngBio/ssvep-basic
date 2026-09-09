// app.js
 
console.log('[BCI] Loading application ...');
 
window.addEventListener('load', function() {
  console.log('[BCI] DOM loaded, initialising ...');
  
  initFlicker();
  console.log('[BCI] Flickering launched');
});
 

function startTest() {
  console.log('[StartTest] Initialised session');
  
  if (!socket) {
    alert('No connection with server');
    return;
  }
  
  if (socket.readyState !== WebSocket.OPEN) {
    alert('Disconnected from server');
    return;
  }
  
  // Send message
  socket.send(JSON.stringify({
    type: "start_session",
    label: "bci_vital_" + new Date().getTime()
  }));
  
  document.getElementById('btn-test').disabled = true;
  console.log('[StartTest] Disables start button once begins');
}
 

function stopTest() {
  console.log('[StopTest] Session ended');
  
  if (!socket) {
    alert('No connection with server');
    return;
  }
  
  if (socket.readyState !== WebSocket.OPEN) {
    alert('Lost connection with server');
    return;
  }
  
  socket.send(JSON.stringify({
    type: "stop_session"
  }));
  
  document.getElementById('btn-test').disabled = false;
  console.log('[StopTest] Start button active again');
}
 
window.startTest = startTest;
window.stopTest = stopTest;