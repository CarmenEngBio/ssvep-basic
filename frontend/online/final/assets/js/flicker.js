// flicker.js 
 
function initFlicker() {
  const flickerCells = Array.from(document.querySelectorAll('.key[data-freq]')) 
    .filter(el => parseFloat(el.dataset.freq) > 0)
    .map(el => ({
      el: el,
      freq: parseFloat(el.dataset.freq),
      period: 1000 / (parseFloat(el.dataset.freq) * 2),  // ms 
      elapsed: 0,
      state: false,  // false = off which is black, true = on which corrresponds to white cell
    }));

  console.log('[Flicker] Initialising with ' + flickerCells.length + ' cells');

  if (flickerCells.length === 0) {
    console.error('[Flicker] Cells not found with that key');
    return;
  }

  flickerCells.forEach(c => {
    console.log('[Flicker] ' + c.el.getAttribute('id') + 
                ' -> ' + c.freq + ' Hz (period: ' + c.period.toFixed(1) + ' ms)'); // frequencies shown
  }); 

  let lastT = null;

  function tick(ts) {
    if (!lastT) lastT = ts;
    const dt = ts - lastT;
    lastT = ts;

    flickerCells.forEach(k => {
      k.elapsed += dt;

      while (k.elapsed >= k.period) {
        k.elapsed -= k.period;
        k.state = !k.state;

        // Aplicar clases CSS
        if (k.state) {
          k.el.classList.add('on');
          k.el.classList.remove('off');
        } else {
          k.el.classList.remove('on');
          k.el.classList.add('off');
        }
      }
    });

    requestAnimationFrame(tick);
  }

  // Flicker loop is launched
  requestAnimationFrame(tick);
}

window.addEventListener('load', function() {
  console.log('[Flicker] DOM loaded, starting flickering engine...');
  setTimeout(initFlicker, 100);
});