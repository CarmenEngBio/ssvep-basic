// app.js — Inicializador principal actualizado para exp2+online
 
console.log('[BCI] Cargando aplicación...');
 
window.addEventListener('load', function() {
  console.log('[BCI] DOM cargado, inicializando...');
  
  // Inicializar flickering
  initFlicker();
  console.log('[BCI] Flickering iniciado');
});
 
// ==========================================
// FUNCIÓN: Iniciar Sesión
// ==========================================
function startTest() {
  console.log('[StartTest] Sesión iniciada');
  
  if (!socket) {
    alert('⚠️ No hay conexión con el servidor');
    return;
  }
  
  if (socket.readyState !== WebSocket.OPEN) {
    alert('⚠️ Desconectado del servidor');
    return;
  }
  
  // Enviar mensaje
  socket.send(JSON.stringify({
    type: "start_session",
    label: "bci_vital_" + new Date().getTime()
  }));
  
  // Desactivar botón
  document.getElementById('btn-test').disabled = true;
  console.log('[StartTest] Botón desactivado');
}
 
// ==========================================
// FUNCIÓN: Detener Sesión
// ==========================================
function stopTest() {
  console.log('[StopTest] Sesión detenida');
  
  if (!socket) {
    alert('⚠️ No hay conexión con el servidor');
    return;
  }
  
  if (socket.readyState !== WebSocket.OPEN) {
    alert('⚠️ Desconectado del servidor');
    return;
  }
  
  // Enviar mensaje de parada
  socket.send(JSON.stringify({
    type: "stop_session"
  }));
  
  // Reactivar botón de inicio
  document.getElementById('btn-test').disabled = false;
  console.log('[StopTest] Botón reactivado');
}
 
// Hacer funciones globales
window.startTest = startTest;
window.stopTest = stopTest;