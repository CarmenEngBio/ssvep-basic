// bci_app.js — Inicializador principal del BCI

console.log('[BCI] Cargando aplicación...');

// Esperar a que DOM esté completamente cargado
window.addEventListener('load', function() {
  console.log('[BCI] DOM cargado, inicializando...');
  
  // Ahora SÍ inicializar (DOM existe)
  initFlicker();
  console.log('[BCI] Flickering iniciado');
  
  connect();
  console.log('[BCI] Conectando con servidor WebSocket en ws://localhost:8765');
});

// ==========================================
// FUNCIÓN: Iniciar Sesión (botón)
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

// Hacer global
window.startTest = startTest;