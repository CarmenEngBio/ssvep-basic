// app.js
  
window.addEventListener('load', function() {
  initFlicker();
});
 

function startTest() {  
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
}
 

function stopTest() {  
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
}
 
window.startTest = startTest;
window.stopTest = stopTest;