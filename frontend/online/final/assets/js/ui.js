// ui.js 

console.log('[UI] Initialising interface...');
 
function setConnectionStatus(state) {
  var el = document.getElementById('status');
  if (!el) {
    console.warn('[UI] Status element not found');
    return;
  }
  
  if (state === 'connected') {
    el.textContent = '● Connecting to server';
    el.style.color = '#51cf66';
    console.log('[UI] Status: Connected');
  } else {
    el.textContent = '● Disconnected - reattempting...';
    el.style.color = '#ff6b6b';
    console.log('[UI] Status: Disconnected');
  }
}
 
function clearCellSelection() {
  var cells = document.querySelectorAll('.key');
  cells.forEach(cell => {
    cell.classList.remove('selected');
    cell.classList.remove('error');
    cell.style.backgroundColor = '';
  });
  console.log('[UI] Disabled cells selection');
}
 
function showMessage(text, type) {
  var feedback = document.getElementById('phase-label');
  if (!feedback) {
    console.warn('[UI] Element not found');
    return;
  }
  
  feedback.textContent = text;
  
  if (type === 'error') {
    feedback.style.color = '#ff6b6b';
  } else if (type === 'success') {
    feedback.style.color = '#51cf66';
  } else if (type === 'info') {
    feedback.style.color = '#74c0fc';
  } else {
    feedback.style.color = '#aaa';
  }
  
  console.log('[UI] Message:', text, '(' + type + ')');
}
 
function updateSignalQuality(quality) {
  console.log('[Signal Quality]', quality.toFixed(2), 'µV');
}
 
var countdownInterval = null;
 
function startCountdown(seconds) {
  var timer = document.getElementById('timer');
  if (!timer) {
    console.warn('[UI] Timer element not found');
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