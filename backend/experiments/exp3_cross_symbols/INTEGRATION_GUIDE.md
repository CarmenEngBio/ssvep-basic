# Guía de Integración — Experimento 3

## Resumen

Se proporciona un **Experimento 3 completo** que sigue el modelo del **Experimento 2 (simultáneo)**:
- **4 celdas** en forma de **cruz**
- Cada celda muestra un **emoji emocional** (❄️🔥😴😣)
- Parpadeo **simultáneo** a 4 frecuencias (8.0, 9.0, 10.0, 12.0 Hz)
- **Grabación automática** de 60 segundos
- **Sin CCA, sin voting** (enfoque en captura y análisis posterior)

## Archivos Proporcionados

### Backend (Python)

| Archivo | Propósito |
|---------|-----------|
| `exp3_config.py` | Configuración de 4 frecuencias simultáneas y matriz de estímulos |
| `exp3_server.py` | Servidor WebSocket con grabación automática (60 s) |

**Ubicación en repositorio**: `backend/experiments/exp3/`

**Dependencias**: `websockets`, `numpy`, `brainflow` (ya debería tenerlas)

**Archivos reutilizados**: `eegsource.py`, `recorder.py` (del backend principal)

### Frontend (HTML/CSS/JS)

| Archivo | Propósito |
|---------|-----------|
| `index_exp3.html` | Interfaz principal con 4 celdas en cruz + emojis |
| `styles_exp3.css` | Estilos CSS para layout de cruz, colores, emoji sizing |
| `app_exp3.js` | Inicializador (lanza flickering + WebSocket) |

**Ubicación en repositorio**: `frontend/experiments/exp3/`

**Archivos reutilizados**: 
- `assets/js/ui.js` (funciones UI compartidas)
- `assets/js/websocket.js` (comunicación WS)
- `assets/js/flicker.js` (motor de flickering)

---

## Cómo Agregar Experiment 3 al Repositorio

### Paso 1: Crear estructura de carpetas

```bash
cd /ruta/a/ssvep-basic

# Backend
mkdir -p backend/experiments/exp3

# Frontend
mkdir -p frontend/experiments/exp3/assets/css
mkdir -p frontend/experiments/exp3/assets/js
```

### Paso 2: Copiar archivos Python (backend)

```bash
# Los 2 archivos nuevos de Exp3
cp exp3_config.py   backend/experiments/exp3/
cp exp3_server.py   backend/experiments/exp3/
```

### Paso 3: Copiar archivos Frontend

```bash
# HTML + CSS nuevos
cp index_exp3.html      frontend/experiments/exp3/
cp styles_exp3.css      frontend/experiments/exp3/assets/css/

# JavaScript de Exp3
cp app_exp3.js          frontend/experiments/exp3/assets/js/

# Copiar scripts compartidos (para que funcione standalone si se desea)
cp frontend/assets/js/ui.js         frontend/experiments/exp3/assets/js/
cp frontend/assets/js/websocket.js  frontend/experiments/exp3/assets/js/
cp frontend/assets/js/flicker.js    frontend/experiments/exp3/assets/js/
```

### Paso 4: Crear documentación

```bash
# README específico de Exp3
cp EXP3_README.md  backend/experiments/exp3/README.md
```

### Paso 5: Validar estructura

```bash
tree backend/experiments/exp3/
# Debe mostrar:
# backend/experiments/exp3/
# ├── exp3_config.py
# ├── exp3_server.py
# └── README.md

tree frontend/experiments/exp3/
# Debe mostrar:
# frontend/experiments/exp3/
# ├── index_exp3.html
# └── assets/
#     ├── css/
#     │   └── styles_exp3.css
#     └── js/
#         ├── app_exp3.js
#         ├── flicker.js
#         ├── ui.js
#         └── websocket.js
```

---

## Configuración Inicial

### 1. Editar `exp3_config.py`

Abre `backend/experiments/exp3/exp3_config.py` y establece el puerto serial correcto:

```python
SERIAL_PORT = "COM5"  # Ajusta según tu sistema
```

Ver Device Manager (Windows) o `ls /dev/ttyUSB*` (Linux) para encontrar el puerto.

### 2. Opcionalmente, ajustar frecuencias

Si necesitas otras frecuencias (ej: para otra sesión experimental):

```python
STIM_MATRIX = [
    {"key": "top",    "label": "❄️ Frío",     "emoji": "❄️", "freq": 10.0},
    {"key": "bottom", "label": "😴 Cansado",  "emoji": "😴", "freq": 12.0},
    {"key": "left",   "label": "🔥 Calor",    "emoji": "🔥", "freq": 8.0},
    {"key": "right",  "label": "😣 Dolor",    "emoji": "😣", "freq": 9.0},
]
```

Recuerda: todas las frecuencias deben ser divisibles por 60 Hz (refresh rate estándar).

---

## Ejecución Rápida

### Terminal 1: Arrancar Backend

```bash
cd /ruta/a/ssvep-basic/backend
python experiments/exp3/exp3_server.py
```

### Terminal 2: Abrir Frontend

**Opción A: Doble clic directo**
```bash
# Navega a frontend/experiments/exp3/ y haz doble clic en index_exp3.html
```

**Opción B: Servidor HTTP local** (recomendado)
```bash
cd /ruta/a/ssvep-basic/frontend/experiments/exp3
python -m http.server 8000
# Luego abre http://localhost:8000/index_exp3.html
```

---

## Diferencias Clave vs. Experimento 1 (Single Cell)

| Aspecto | Exp 1 | Exp 3 |
|---------|-------|-------|
| **Celdas** | 1 | 4 (cruz) |
| **Frecuencias** | 1 (8.57 Hz) | 4 simultáneas (8.0, 9.0, 10.0, 12.0 Hz) |
| **Duración** | 40 s | 60 s |
| **Estímulos** | "1" (fijo) | Emojis contextuales (❄️🔥😴😣) |
| **Layout** | Centrado | Cruz |
| **Análisis** | Welch single-freq | Multi-freq + armónicos |

---

## Flujo de Datos (Backend)

```
Cyton EEG ──→ BrainFlow ──→ eegsource.py (buffer)
                                    ↓
                        (4 frecuencias simultáneas)
                                    ↓
                            recorder.py (escribe .txt)
                                    ↓
                            WebSocket → Frontend
                                    ↓
                                Timer UI
```

---

## Flujo de Datos (Frontend)

```
index_exp3.html ──┬──→ flicker.js     (4 celdas parpadean a sus freqs)
                  ├──→ websocket.js   (comunica con servidor)
                  ├──→ ui.js          (updates de status/timer)
                  └──→ app_exp3.js    (inicializa todo)

                            ↓
                    
                    WebSocket (localhost:8765)
                            ↓
                    
                        server.py
                    (grabación automática)
```

---

## Análisis de Datos Posterior

Una vez grabado el archivo `.txt` en `backend/recordings/exp3_test_<timestamp>.txt`:

### Cargar en Jupyter

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Cargar
data = np.loadtxt('recordings/exp3_test_TIMESTAMP.txt', skiprows=5)
eeg = data[:, 1:-1].T  # Excluir timestamp y marker
fs = 250

# Preprocesamiento (igual que en EEG_Experiments_1_2_Analysis.py)
# ... bandpass, notch, CAR ...

# Welch PSD
freqs, psd = signal.welch(eeg[4:8], fs, nperseg=fs*2)  # P7, P8, O1, O2; ventana de 2s

# Buscar picos en las 4 frecuencias fundamentales:
# 8.0 Hz (Calor) → 16, 24 Hz
# 9.0 Hz (Dolor) → 18, 27 Hz
# 10.0 Hz (Frío) → 20, 30 Hz
# 12.0 Hz (Cansado) → 24, 36 Hz

plt.semilogy(freqs, psd.T)
plt.xlim([5, 40])
plt.grid()
plt.show()
```

### Hitos esperados en PSD

- Picos claros en **8, 16, 24 Hz** (Calor + armónicos)
- Picos claros en **9, 18, 27 Hz** (Dolor + armónicos)
- Picos claros en **10, 20, 30 Hz** (Frío + armónicos)
- Picos claros en **12, 24, 36 Hz** (Cansado + armónicos)
- Amplitudes mayores en canales **P7, P8, O1, O2**

---

## Debugging y Troubleshooting

### Error: "ConnectionRefused" en frontend

**Causa**: El servidor backend no está corriendo

**Solución**:
```bash
# Terminal 1: Arranca el servidor
cd backend
python experiments/exp3/exp3_server.py
```

### Error: "Serial port COM5 not found"

**Causa**: Puerto incorrecto

**Solución**: Edita `exp3_config.py` y pon el puerto correcto

### Calidad de señal muy baja

**Causa**: Contacto pobre de electrodos

**Solución**:
- Limpia los electrodos con alcohol isopropílico
- Asegura que hay suficiente pasta conductora
- Verifica que están bien colocados (especialmente P7, P8, O1, O2)

### Las 4 celdas no parpadean

**Causa**: Problema de flickering.js

**Solución**:
1. Abre las DevTools (F12) del navegador
2. Ve a Console
3. Verifica que no hay errores JavaScript
4. Comprueba que `flicker.js` se carga correctamente

---

## Ampliaciones Futuras

Si quieres extender Exp3:

1. **Agregar CCA/clasificación**: Inspirarse en `exp2_server.py` del proyecto principal
2. **Cambiar emojis**: Edita `STIM_MATRIX` en `exp3_config.py`
3. **Modo DEMO**: Agregar opción `MODE = "DEMO"` para test sin hardware
4. **Más frecuencias**: Ajusta el layout CSS (`#stim-wrap`) y añade celdas a `STIM_MATRIX`
5. **Análisis en tiempo real**: Enviar FFT/PSD al frontend vía WebSocket

---

## Referencias

- **Proyecto principal**: `CarmenEngBio/ssvep-bci`
- **Supervisores**: Dra. Nieves Cubo Mateo, Dra. Mónica Albaladejo Belmonte (CEU San Pablo)
- **Hardware**: Cyton + OpenBCI Ultracortex Mark IV
- **Bibliotecas clave**: BrainFlow, websockets, numpy, scipy

---

**Última actualización**: Julio 2026

Cualquier duda, revisá los archivos fuente (comentarios en Python/JS) o contacta con Carmen.
