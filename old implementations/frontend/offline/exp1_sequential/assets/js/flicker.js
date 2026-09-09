// flicker.js - Experiment 1
// Cell turns ON when indicated by the backend, the rest remains OFF

var currentActiveCell = null;

function setActiveCell(key) {
  currentActiveCell = String(key);
}

function initFlicker() {
  const flickerKeys = Array.from(document.querySelectorAll('.key[data-freq]'))
    .filter(el => parseFloat(el.dataset.freq) > 0)
    .map(el => ({
      el,
      key:     el.dataset.key,
      period:  1000 / (parseFloat(el.dataset.freq) * 2),
      elapsed: 0,
      state:   false,
    }));

  let lastT = null;

  function tick(ts) {
    if (!lastT) lastT = ts;
    const dt = ts - lastT;
    lastT = ts;

    flickerKeys.forEach(k => {
      if (k.key !== currentActiveCell) {
        k.elapsed = 0;
        k.state   = false;
        k.el.classList.remove('on');
        k.el.classList.add('off');
        return;
      }

      k.elapsed += dt;
      if (k.elapsed >= k.period) {
        k.elapsed -= k.period;
        k.state = !k.state;
        k.el.classList.toggle('on',  k.state);
        k.el.classList.toggle('off', !k.state);
      }
    });

    requestAnimationFrame(tick);
  }

  requestAnimationFrame(tick);
}
