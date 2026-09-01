// BCI app.js

window.addEventListener('load', function () {
  initFlicker();
});
 
function startTest() {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    alert('Not connected to the server');
    return;
  }
 
  socket.send(JSON.stringify({
    type: 'start_session',
    label: 'bci_vital_' + new Date().getTime(),
  }));
 
  document.getElementById('btn-test').disabled = true;
}
 
window.startTest = startTest;