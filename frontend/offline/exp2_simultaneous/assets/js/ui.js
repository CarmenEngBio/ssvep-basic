
function setConnectionStatus(state) {
  var el = document.getElementById('status');
  if (state === 'connected') {
    el.textContent = '● Connected Cyton ';
    el.classList.add('ok');
  } else {
    el.textContent = '● No connection - trying again...';
    el.classList.remove('ok');
  }
}

var countdownInterval = null;

function startCountdown(seconds) {
  var timer = document.getElementById('timer');
  var remaining = seconds;
  timer.textContent = 'Recording... ' + remaining + ' s remaining';

  if (countdownInterval) clearInterval(countdownInterval);
  countdownInterval = setInterval(function() {
    remaining--;
    if (remaining <= 0) {
      clearInterval(countdownInterval);
      timer.textContent = 'Ending experiment...';
    } else {
      timer.textContent = 'Recording... ' + remaining + ' s remaining';
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
    document.getElementById('phase-label').textContent =
      'According to the timer the user must gaze at: cell ' + msg.cell + ' (' + msg.freq + ' Hz)';
  }

  if (msg.type === 'recording_stopped') {
    btn.disabled = false;
    if (countdownInterval) clearInterval(countdownInterval);
    document.getElementById('timer').textContent = '✓ Experiment ended and saved.';
    document.getElementById('phase-label').textContent = '—';
  }
}
