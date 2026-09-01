// BCI websocket.js
 
var WS_URL = 'ws://localhost:8765';
var RETRY_MS = 2000;
var socket = null;
 
function connect() {
  socket = new WebSocket(WS_URL);
 
  socket.onopen = function () {
    setConnectionStatus('connected');
  };
 
  socket.onclose = function () {
    setConnectionStatus('disconnected');
    socket = null;
    setTimeout(connect, RETRY_MS);
  };
 
  socket.onerror = function () {
    setConnectionStatus('disconnected');
  };
 
  socket.onmessage = function (e) {
    var msg;
    try {
      msg = JSON.parse(e.data);
    } catch (err) {
      console.error('[WebSocket] Bad message:', err);
      return;
    }
 
    switch (msg.type) {
      case 'block_started': handleBlockStarted(msg); break;
      case 'block_result':  handleBlockResult(msg);  break;
      case 'session_ended': handleSessionEnded(msg); break;
    }
  };
}
 
function handleBlockStarted(msg) {
  showMessage(msg.emoji + ' Look at: ' + msg.label + ' (' + msg.freq + ' Hz)', 'info');
 
  if (msg.file) {
    document.getElementById('rec-filename').textContent = 'Recorded at: ' + msg.file;
  }
 
  document.getElementById('btn-test').style.display = 'none';
  startCountdown(msg.duration);
  clearCellSelection();
}

function handleBlockResult(msg) {
  clearCellSelection();

  var cell = document.getElementById('cell-' + msg.cell_id);

  if (msg.correct) {
    if (cell) cell.classList.add('selected');

    showMessage(
      '✅ ' + msg.emoji + ' ' + msg.label + ' - Corr: ' +
      msg.correlation.toFixed(4),
      'success'
    );
  }
}
 
function handleSessionEnded(msg) {
  stopCountdown();
  clearCellSelection();
  showMessage(
    '✓ Finished session - Accuracy: ' + msg.correct + '/' + msg.total +
    ' (' + msg.accuracy + '%)',
    'success'
  );
 
  var btn = document.getElementById('btn-test');
  btn.style.display = 'block';
  btn.disabled = false;
}


if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', connect);
} else {
  connect();
}