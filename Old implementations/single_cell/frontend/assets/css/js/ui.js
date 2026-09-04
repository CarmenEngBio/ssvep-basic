
function setConnectionStatus(state) {
  var el = document.getElementById('status');
  if (state === 'connected') {
    el.textContent = '● Cyton connected';
    el.classList.add('ok');
  } else {
    el.textContent = '● No connection - reattempting...';
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
      timer.textContent = 'Ending recording ...';
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
    startCountdown(msg.duration || 40);
  }

  if (msg.type === 'recording_stopped') {
    btn.disabled = false;
    if (countdownInterval) clearInterval(countdownInterval);
    document.getElementById('timer').textContent = '✓ Ended and saved recording.';
  }
}
