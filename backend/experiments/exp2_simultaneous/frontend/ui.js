function setConnectionStatus(state) {
  var el = document.getElementById('status');
  if (state === 'connected') {
    el.textContent = '● Connected Cyton ';
    el.classList.add('ok');
  } else {
    el.textContent = '● Sin conexión — reintentando...';
    el.classList.remove('ok');
  }
}

var countdownInterval = null;

function startCountdown(seconds) {
  var timer = document.getElementById('timer');
  var remaining = seconds;
  timer.textContent = 'Grabando... ' + remaining + ' s restantes';

  if (countdownInterval) clearInterval(countdownInterval);
  countdownInterval = setInterval(function() {
    remaining--;
    if (remaining <= 0) {
      clearInterval(countdownInterval);
      timer.textContent = 'Finalizando experimento...';
    } else {
      timer.textContent = 'Grabando... ' + remaining + ' s restantes';
    }
  }, 1000);
}

function handleRecordingMessage(msg) {
  var btn   = document.getElementById('btn-test');
  var fname = document.getElementById('rec-filename');

  if (msg.type === 'recording_started') {
    btn.disabled = true;
    fname.textContent = msg.file || '';
    startCountdown(msg.duration || 160);
  }

  if (msg.type === 'phase') {
    // Solo informativo: apoyo/cruce con tu alarma del móvil, el estímulo
    // (las 4 celdas parpadeando) no cambia.
    document.getElementById('phase-label').textContent =
      'Según el reloj interno, ahora tocaría mirar: celda ' + msg.cell + ' (' + msg.freq + ' Hz)';
  }

  if (msg.type === 'recording_stopped') {
    btn.disabled = false;
    if (countdownInterval) clearInterval(countdownInterval);
    document.getElementById('timer').textContent = '✓ Experimento finalizado y guardado.';
    document.getElementById('phase-label').textContent = '—';
  }
}
