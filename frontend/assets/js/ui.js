// BCI ui.js 
// Displays User Interface helper functionalities
 
function setConnectionStatus(state) {
  const el = document.getElementById('status');
  if (!el) return;
 
  if (state === 'connected') {
    el.textContent = '● Connected to server';
    el.style.color = '#51cf66';
  } else {
    el.textContent = '● Disconnected - reattempting...';
    el.style.color = '#ff6b6b';
  }
}
 
function clearCellSelection() {
  document.querySelectorAll('.key').forEach(cell => {
    cell.classList.remove('selected', 'error');
  });
}
 
function showMessage(text, type) {
  const el = document.getElementById('phase-label');
  if (!el) return;
 
  el.textContent = text;
  const colors = { error: '#ff6b6b', success: '#51cf66', info: '#74c0fc' };
  el.style.color = colors[type] || '#aaa';
}
 
let countdownInterval = null;
 
function startCountdown(seconds) {
  const timer = document.getElementById('timer');
  if (!timer) return;
 
  let remaining = seconds;
  timer.textContent = 'Recording... ' + remaining + ' s';
 
  if (countdownInterval) clearInterval(countdownInterval);
  countdownInterval = setInterval(function () {
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
 
function stopCountdown() {
  if (countdownInterval) {
    clearInterval(countdownInterval);
    countdownInterval = null;
  }
  const timer = document.getElementById('timer');
  if (timer) timer.textContent = '';
}