# Experimentos — Validación multi-frecuencia (4 celdas)

Estos dos experimentos amplían `ssvep-basic` más allá de la validación de una
sola celda: ahora se prueban las 4 frecuencias candidatas del teclado
(8.57, 10, 12 y 15 Hz — las mismas que ya diste problemas en
`EEG_Phase_8_sketch_end_version.ipynb`), pero variando **cómo se presentan**
los estímulos, para poder comparar después si el modo de presentación influye
en si el ritmo alpha (~10 Hz) sigue enmascarando la clasificación a 12 y 15 Hz.

- **`exp1_secuencial/`** — las 4 celdas están visibles todo el rato, pero solo
  una parpadea cada vez (40 s por celda, 160 s en total). Las otras 3
  permanecen apagadas (estáticas). El backend controla el orden y avisa al
  frontend qué celda debe encenderse.
- **`exp2_simultaneo/`** — las 4 celdas parpadean **a la vez** durante los
  160 s. Tú decides con tu alarma del móvil a qué celda mirar cada 40 s. El
  backend no controla el flicker (todas están siempre activas), pero sí lleva
  internamente el mismo temporizador de 40 s por celda para that el marcador
  del fichero `.txt` quede etiquetado automáticamente — así no dependes solo
  de anotar a mano cuándo mirabas cada celda.

## Qué comparten ambos experimentos

- **`recorder.py` sin modificar** respecto al de `ssvep-basic`: mismo formato
  `.txt` compatible con OpenBCI GUI, mismo notebook de análisis (Welch PSD).
- **Grabación única y continua** de principio a fin (no 4 ficheros sueltos),
  segmentada por la columna de marcador (`1`, `2`, `3`, `4` según la celda).
- **Flush del backlog de BrainFlow antes de `recorder.start()`**: se llama a
  `source.get_new_samples()` una vez y se descarta el resultado justo antes
  de arrancar la grabación, para evitar que el backlog acumulado durante el
  reposo se cuele como los primeros segundos de la grabación (el bug que
  tenías pendiente de resolver en `ssvep-basic`).
- **Flicker de celda completa** (blanco/negro a contraste máximo), igual que
  en `ssvep-basic` y a diferencia del proyecto principal — aquí interesa
  maximizar la amplitud SSVEP para el análisis offline, no la comodidad visual
  de uso repetido (Dehais et al. 2022 se aplica en `ssvep-bci`, no aquí).

## Una cosa a confirmar antes de usarlos

En tu `eegsource.py` actual de `ssvep-basic`, la línea del board es:
```python
self.board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)
```
con la línea de `CYTON_BOARD` comentada justo encima. Los `eegsource.py` de
estos dos experimentos usan `CYTON_BOARD` (placa real), asumiendo que la
sintética era un resto de una prueba sin hardware conectado. Si en realidad
la querías dejar así a propósito, cámbialo antes de grabar datos reales.

## Cómo ejecutar cada uno

Igual que `ssvep-basic`: `python backend/server.py` y doble clic en
`frontend/index.html`. Cada carpeta tiene su propio README con el detalle.
