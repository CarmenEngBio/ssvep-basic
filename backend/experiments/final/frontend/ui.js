// ui.js — Funciones de interfaz actualizadas para exp2+online
 
console.log('[UI] Inicializando interfaz...');
 
function setConnectionStatus(state) {
  var el = document.getElementById('status');
  if (!el) {
    console.warn('[UI] Elemento status no encontrado');
    return;
  }
  
  if (state === 'connected') {
    el.textContent = '● Connecting to server';
    el.style.color = '#51cf66';
    console.log('[UI] Estado: Connected');
  } else {
    el.textContent = '● Disconnected - reattempting...';
    el.style.color = '#ff6b6b';
    console.log('[UI] Estado: Disconnected');
  }
}
 
function clearCellSelection() {
  var cells = document.querySelectorAll('.key');
  cells.forEach(cell => {
    cell.classList.remove('selected');
    cell.classList.remove('error');
    cell.style.backgroundColor = '';  // Limpiar highlight
  });
  console.log('[UI] Celdas deseleccionadas');
}
 
function showMessage(text, type) {
  var feedback = document.getElementById('phase-label');
  if (!feedback) {
    console.warn('[UI] Elemento phase-label no encontrado');
    return;
  }
  
  feedback.textContent = text;
  
  if (type === 'error') {
    feedback.style.color = '#ff6b6b';
  } else if (type === 'success') {
    feedback.style.color = '#51cf66';
  } else if (type === 'info') {
    feedback.style.color = '#74c0fc';  // Azul para instrucciones
  } else {
    feedback.style.color = '#aaa';
  }
  
  console.log('[UI] Mensaje:', text, '(' + type + ')');
}
 
function updateSignalQuality(quality) {
  console.log('[Signal Quality]', quality.toFixed(2), 'µV');
}
 
var countdownInterval = null;
 
function startCountdown(seconds) {
  var timer = document.getElementById('timer');
  if (!timer) {
    console.warn('[UI] Elemento timer no encontrado');
    return;
  }
  
  var remaining = seconds;
  timer.textContent = 'Recording... ' + remaining + ' s';
 
  if (countdownInterval) clearInterval(countdownInterval);
  
  countdownInterval = setInterval(function() {
    remaining--;
    if (remaining <= 0) {
      clearInterval(countdownInterval);
      countdownInterval = null;
      timer.textContent = '';
    } else {
      timer.textContent = 'Recording... ' + remaining + ' s';
    }
  }, 1000);
}