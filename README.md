# Single-Cell Test — SSVEP BCI

Proyecto independiente, abstraído de `ssvep-bci`, para validar la respuesta SSVEP
y la calidad de señal cruda **antes** de depurar fallos en el sistema completo
multi-frecuencia.

## Qué incluye

- **Incluye**: una sola celda parpadeante (dígito "1" fijo en negro, celda
  completa 8×8 cm alternando blanco/negro a 8.57 Hz) + grabación automática
  de 40 s de señal cruda, guardada en el mismo formato `.txt` compatible con
  OpenBCI GUI que ya usa `recorder.py` en el proyecto principal — lista para
  el mismo flujo de análisis en Jupyter (Welch PSD).
- **No incluye**: clasificación CCA, voting, cooldown, ni modo DEMO. El
  backend solo se conecta a la placa Cyton real. La idea es aislar si la
  respuesta SSVEP y la señal del electrodo están presentes, sin la
  complejidad añadida del teclado de 10 dígitos.

## Estructura

```
single-cell-test/
├── README.md
├── backend/
│   ├── config.py      # SERIAL_PORT, STIM_FREQ (8.57 Hz), RECORD_SEC (40 s)
│   ├── eegsource.py    # Solo CytonEEG (sin DemoEEG ni MODE)
│   ├── recorder.py     # Mismo grabador formato-OpenBCI-GUI del proyecto principal
│   └── server.py       # Handler WS: start_recording → auto-stop a los 40 s
└── frontend/
    ├── index.html
    └── assets/
        ├── css/styles.css
        └── js/
            ├── flicker.js     # Mismo motor de flicker del proyecto principal
            ├── websocket.js
            ├── ui.js
            └── app.js
```

## Cómo ejecutarlo

1. Edita `backend/config.py` y pon el `SERIAL_PORT` correcto para tu Cyton.
2. Instala dependencias (mismas que el backend principal, sin scikit-learn
   porque aquí no hay CCA):
   ```
   pip install websockets numpy brainflow
   ```
3. Arranca el servidor:
   ```
   python backend/server.py
   ```
4. Haz doble clic en `frontend/index.html` para abrirlo en el navegador
   (sin servidor HTTP local, igual que el proyecto principal — por eso
   `websocket.js` sigue usando `<script src="">` en vez de `import`).
5. Cuando aparezca "● Cyton conectada", pulsa **Iniciar prueba (40 s)** y
   enfoca la vista en el "1" mientras parpadea. La grabación se detiene y
   guarda sola a los 40 s — no hace falta pulsar nada más.
6. El fichero `.txt` aparece en `backend/recordings/`, listo para cargarlo
   en el mismo notebook que ya usas, y comprobar si aparece un pico de
   potencia en 8.57 Hz (y sus armónicos) en P7/P8/O1/O2.


## Nota

Los valores numéricos empleados son el resultado de los cálculos de números 
enteros divididos respecto a la tasa de refresco del PC equivalente a 60 Hz. 
