// bci_flicker.js — Motor de flickering para las 4 celdas vitales
 
function initFlicker() {
  const flickerCells = Array.from(document.querySelectorAll('.key[data-freq]'))  // ✅ CAMBIAR A .key
    .filter(el => parseFloat(el.dataset.freq) > 0)
    .map(el => ({
      el: el,
      freq: parseFloat(el.dataset.freq),
      period: 1000 / (parseFloat(el.dataset.freq) * 2),  // ms por semi-ciclo
      elapsed: 0,
      state: false,  // false = off (negro), true = on (blanco)
    }));

  console.log('[Flicker] Inicializado con ' + flickerCells.length + ' celdas');

  if (flickerCells.length === 0) {
    console.error('[Flicker] ¡¡ERROR!! No se encontraron celdas con clase .key');
    return;
  }

  // Mostrar frecuencias
  flickerCells.forEach(c => {
    console.log('[Flicker] ' + c.el.getAttribute('id') + 
                ' → ' + c.freq + ' Hz (período: ' + c.period.toFixed(1) + ' ms)');
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

  // Iniciar el loop de animación
  requestAnimationFrame(tick);
}

// Inicializar al cargar
window.addEventListener('load', function() {
  console.log('[Flicker] DOM loaded, iniciando flickering...');
  setTimeout(initFlicker, 100);
});