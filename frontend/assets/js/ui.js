function setConnectionStatus(state) {
  var el = document.getElementById('status');
  if (state === 'connected') {
    el.textContent = '● Cyton conectada';
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
      timer.textContent = 'Finalizando grabación...';
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
    startCountdown(msg.duration || 40);
  }

  if (msg.type === 'recording_stopped') {
    btn.disabled = false;
    if (countdownInterval) clearInterval(countdownInterval);
    document.getElementById('timer').textContent = '✓ Grabación finalizada y guardada.';
  }
}
