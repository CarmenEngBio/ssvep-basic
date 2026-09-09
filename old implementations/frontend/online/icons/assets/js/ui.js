// bci_ui.js — Funciones de interfaz del BCI
 
// Inicialmente, desactivar el botón de detener

console.log('[UI] Inicializando interfaz...');

function setConnectionStatus(state) {
  var el = document.getElementById('status');
  if (!el) {
    console.warn('[UI] Elemento status no encontrado');
    return;
  }
  
  if (state === 'connected') {
    el.textContent = '● Conectado al servidor';
    el.style.color = '#51cf66';
    console.log('[UI] Estado: Conectado');
  } else {
    el.textContent = '● Desconectado - reintentando...';
    el.style.color = '#ff6b6b';
    console.log('[UI] Estado: Desconectado');
  }
}

function clearCellSelection() {
  var cells = document.querySelectorAll('.key');  // ✅ CORRECTO
  cells.forEach(cell => {
    cell.classList.remove('selected');
  });
  console.log('[UI] Celdas deseleccionadas');
}

function showMessage(text, type) {
  var feedback = document.getElementById('phase-label');  // ✅ CORRECTO
  if (!feedback) {
    console.warn('[UI] Elemento phase-label no encontrado');
    return;
  }
  
  feedback.textContent = text;
  
  if (type === 'error') {
    feedback.style.color = '#ff6b6b';
  } else if (type === 'success') {
    feedback.style.color = '#51cf66';
  } else {
    feedback.style.color = '#aaa';
  }
  
  console.log('[UI] Mensaje:', text);
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
  timer.textContent = 'Grabando... ' + remaining + ' s';

  if (countdownInterval) clearInterval(countdownInterval);
  
  countdownInterval = setInterval(function() {
    remaining--;
    if (remaining <= 0) {
      clearInterval(countdownInterval);
      timer.textContent = 'Finalizando...';
    } else {
      timer.textContent = 'Grabando... ' + remaining + ' s';
    }
  }, 1000);
}