// BCI flicker.js
 
function initFlicker() {
  const flickerCells = Array.from(document.querySelectorAll('.key[data-freq]'))
    .filter(el => parseFloat(el.dataset.freq) > 0)
    .map(el => ({
      el: el,
      period: 1000 / (parseFloat(el.dataset.freq) * 2),
      elapsed: 0,
      state: false,
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
 