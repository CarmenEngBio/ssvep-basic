// flicker.js — Experimento 2
// Motor de flicker sin cambios respecto a ssvep-basic: todas las celdas con
// data-freq parpadean continuamente, sin estado activo/inactivo. A
// diferencia del Experimento 1, aquí no hay setActiveCell — el backend solo
// informa la fase para la etiqueta en pantalla, no controla el estímulo.

function initFlicker() {
  const flickerKeys = Array.from(document.querySelectorAll('.key[data-freq]'))
    .filter(el => parseFloat(el.dataset.freq) > 0)
    .map(el => ({
      el,
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
