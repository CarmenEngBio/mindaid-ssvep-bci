// BCI flicker.js
// Flicker engine for 4 cells oscillations
// Each .key[data-freq] toggles on/off at its own frequency via requestAnimationFrame.
// initFlicker() is called once, from app.js.
 
function initFlicker() {
  const flickerCells = Array.from(document.querySelectorAll('.key[data-freq]'))
    .filter(el => parseFloat(el.dataset.freq) > 0)
    .map(el => ({
      el: el,
      period: 1000 / (parseFloat(el.dataset.freq) * 2),  // ms per half-cycle
      elapsed: 0,
      state: false,   // false = off (black), true = on (white)
    }));
 
  if (flickerCells.length === 0) {
    console.error('[Flicker] No .key[data-freq] cells found');
    return;
  }
 
  let lastT = null;
 
  function tick(ts) {
    if (lastT === null) lastT = ts;
    const dt = ts - lastT;
    lastT = ts;
 
    flickerCells.forEach(k => {
      k.elapsed += dt;
      // while-loop keeps timing correct even if a frame is dropped
      while (k.elapsed >= k.period) {
        k.elapsed -= k.period;
        k.state = !k.state;
        k.el.classList.toggle('on', k.state);
        k.el.classList.toggle('off', !k.state);
      }
    });
 
    requestAnimationFrame(tick);
  }
 
  requestAnimationFrame(tick);
}
 