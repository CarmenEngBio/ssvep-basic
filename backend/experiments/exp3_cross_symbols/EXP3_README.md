# Experimento 3: 4 Celdas en Cruz (Simultáneo)

## Descripción

Experimento SSVEP con **4 estímulos de frecuencias simultáneas** dispuestos en forma de **cruz**, cada uno asociado a un **emoji emocional**:

| Posición | Emoji | Contexto | Frecuencia |
|----------|-------|----------|-----------|
| **Superior** | ❄️ | Frío | 10.0 Hz |
| **Inferior** | 😴 | Cansado | 12.0 Hz |
| **Izquierda** | 🔥 | Calor | 8.0 Hz |
| **Derecha** | 😣 | Dolor | 9.0 Hz |

Las 4 celdas **parpadean simultáneamente** a sus respectivas frecuencias. El grabado es **automático** durante 60 segundos.

### Modelo de Backend

Sigue el patrón del **Experimento 2 simultáneo** (sin CCA, sin voting, sin cooldown):
- Adquisición continua de la placa Cyton
- Monitorización de calidad de señal en canales occipitales (P7, P8, O1, O2)
- Grabación automática con cierre a los 60 segundos
- WebSocket para comunicación frontend ↔ backend

## Estructura de Archivos

```
ssvep-basic/
├── backend/
│   ├── experiments/
│   │   └── exp3/
│   │       ├── exp3_config.py        # Configuración (4 frecuencias)
│   │       └── exp3_server.py        # Servidor WebSocket
│   ├── config.py                     # (Configuración del proyecto)
│   ├── eegsource.py                  # (Interfaz con Cyton)
│   ├── recorder.py                   # (Grabadora de EEG)
│   └── server.py                     # (Servidor principal)
│
└── frontend/
    └── experiments/
        └── exp3/
            ├── index_exp3.html       # Interfaz principal
            └── assets/
                ├── css/
                │   ├── styles.css    # (Estilos compartidos)
                │   └── styles_exp3.css # Estilos Exp3 (cruz, emojis)
                └── js/
                    ├── ui.js         # (Funciones UI compartidas)
                    ├── websocket.js  # (Comunicación WebSocket)
                    ├── flicker.js    # (Motor de flickering)
                    └── app_exp3.js   # Inicializador Exp3
```

## Instalación y Configuración

### 1. Copiar archivos al repositorio

```bash
# Backend
cp exp3_config.py        /ruta/a/ssvep-basic/backend/experiments/exp3/
cp exp3_server.py        /ruta/a/ssvep-basic/backend/experiments/exp3/

# Frontend
cp index_exp3.html       /ruta/a/ssvep-basic/frontend/experiments/exp3/
cp styles_exp3.css       /ruta/a/ssvep-basic/frontend/experiments/exp3/assets/css/
cp app_exp3.js           /ruta/a/ssvep-basic/frontend/experiments/exp3/assets/js/

# Copiar también los scripts compartidos (si no están ya presentes)
cp /ruta/a/ssvep-basic/frontend/assets/js/ui.js        /ruta/a/ssvep-basic/frontend/experiments/exp3/assets/js/
cp /ruta/a/ssvep-basic/frontend/assets/js/websocket.js /ruta/a/ssvep-basic/frontend/experiments/exp3/assets/js/
cp /ruta/a/ssvep-basic/frontend/assets/js/flicker.js   /ruta/a/ssvep-basic/frontend/experiments/exp3/assets/js/
```

### 2. Configurar el puerto serial

Edita `backend/experiments/exp3/exp3_config.py` y establece el puerto correcto para tu placa Cyton:

```python
SERIAL_PORT = "COM5"  # En Windows: COMx (ver Device Manager)
                       # En Linux/Mac: /dev/ttyUSB0 o /dev/cu.usbserial-xxxx
```

### 3. Instalar dependencias (si no están ya instaladas)

```bash
pip install websockets numpy brainflow
```

## Ejecución

### Arrancar el Backend

```bash
# Desde la carpeta backend
cd /ruta/a/ssvep-basic/backend
python experiments/exp3/exp3_server.py
```

Deberías ver:

```
============================================================
  SSVEP BCI — Experimento 3: 4 Celdas en Cruz (Simultáneo)
============================================================
  Estímulos:
    • ❄️ Frío                 → 10.0 Hz
    • 😴 Cansado            → 12.0 Hz
    • 🔥 Calor               → 8.0 Hz
    • 😣 Dolor               → 9.0 Hz

  Grabación automática: 60s
  Solo conexión con hardware Cyton (sin CCA/voting).
  Abre el fichero index_exp3.html en el navegador (doble clic).
============================================================
  Esperando 4s para llenar el buffer EEG...
  Listo! Pulsa 'Iniciar Experimento 3' en la interfaz para comenzar.
```

### Abrir el Frontend

**Opción 1: Doble clic directo** (sin servidor HTTP)
- Navega a `frontend/experiments/exp3/`
- Haz doble clic en `index_exp3.html`
- Se abrirá en tu navegador predeterminado

**Opción 2: Con servidor HTTP local** (recomendado)
```bash
# Python 3
python -m http.server 8000 --directory /ruta/a/ssvep-basic/frontend/experiments/exp3

# O si estás en la carpeta
cd /ruta/a/ssvep-basic/frontend/experiments/exp3
python -m http.server 8000
```

Luego abre `http://localhost:8000/index_exp3.html` en el navegador.

## Protocolo de Uso

1. **Arranca el servidor backend** (ver arriba)
2. **Abre el frontend** → deberías ver "● Cyton conectada"
3. **Ajusta tu postura**: siéntate cómodamente, brazos relajados, vista enfocada en el **punto de fijación central** (el pequeño círculo gris)
4. **Pulsa "Iniciar Experimento 3 (60 s)"**
   - Las 4 celdas comienzan a parpadear simultáneamente
   - El timer muestra los segundos restantes
5. **Mantén la atención relajada** en el punto central durante todo el experimento
   - No necesitas enfocar ninguna celda específica
   - El objetivo es captar la respuesta SSVEP armónica de todas las frecuencias
6. **Espera a que finalice**: a los 60 segundos, el servidor guarda automáticamente el archivo

## Archivos de Grabación

Los datos se guardan en:

```
backend/recordings/
└── exp3_test_<timestamp>.txt
```

Formato compatible con **OpenBCI GUI** y el mismo pipeline de análisis en Jupyter que ya uses.

### Análisis Posterior

Usa tu notebook de análisis habitual (ej: `EEG_Experiments_1_2_Analysis.py`):

1. Carga el archivo `.txt`:
   ```python
   data = np.loadtxt('exp3_test_<timestamp>.txt', skiprows=5)
   ```

2. Aplica el pipeline estándar:
   - Preprocesamiento (Butterworth bandpass 6–40 Hz, notch 50/100/150 Hz, CAR)
   - Welch PSD con ventanas cortas (2 s)
   - Busca picos en:
     - **8 Hz** (Calor) + armónicos 16, 24 Hz
     - **9 Hz** (Dolor) + armónicos 18, 27 Hz
     - **10 Hz** (Frío) + armónicos 20, 30 Hz
     - **12 Hz** (Cansado) + armónicos 24, 36 Hz

3. Canales de interés: **P7, P8, O1, O2** (índices 4–7)

## Consideraciones de Diseño

### ¿Por qué estas frecuencias?

- **8.0 Hz, 9.0 Hz, 10.0 Hz, 12.0 Hz**: Seleccionadas para:
  - Compatibilidad con refresh rate de 60 Hz (todas son divisibles)
  - Espaciamiento suficiente (0.5–1.0 Hz) para minimizar crosstalk armónico
  - Rango alfa extendido (8–12 Hz es potente en SSVEP)
  - Separación clara de armónicos (ej: 8 Hz → 16, 24 Hz; 12 Hz → 24, 36 Hz)

### ¿Por qué 60 segundos?

- Suficiente para múltiples ciclos de cada frecuencia
- Cómodo para el participante (no fatigante)
- Permite análisis con ventanas Welch de 2–4 segundos

### ¿Por qué sin CCA aquí?

Este experimento es de **captura y análisis posterior**, no de **clasificación en tiempo real**. 
El enfoque es caracterizar la respuesta SSVEP a 4 frecuencias simultáneas en contexto emocional.

## Troubleshooting

### "● Sin conexión — reintentando..."
- Verifica que el servidor está en marcha
- Comprueba que `localhost:8765` no está bloqueado (firewall)
- Si accedes desde otra máquina, cambia `localhost` por la IP del servidor

### "ERROR: No se pudo abrir puerto COM5"
- Verifica el puerto correcto en `Device Manager` (Windows) o `dmesg` (Linux)
- Actualiza `SERIAL_PORT` en `exp3_config.py`
- Cierra cualquier otra aplicación usando ese puerto (OpenBCI GUI, IDE serial, etc.)

### "El archivo `.txt` no se guarda"
- Verifica que `backend/recordings/` existe y es escribible
- Comprueba permisos de carpeta
- En Linux/Mac: `chmod 755 backend/recordings/`

### "Calidad de señal muy baja (> 100 µV²)"
- Revisa los electrodos (contacto seco, arena en los contactos)
- Reduce interferencias electromagnéticas (lejos de pantallas, móviles)
- Aumenta `WINDOW_SEC` en config si el buffer no se estabiliza

## Historial de Cambios

- **v1.0**: Versión inicial con 4 celdas en cruz, grabación automática a 60 s, emojis contextuales
- Basado en modelo Exp2 (simultáneo) del proyecto `ssvep-basic`

## Licencia

Mismo scope que el proyecto principal `ssvep-bci`.

---

**Contacto**: Carmen Engbio (CarmenEngBio/ssvep-basic)
**Supervisores**: Dra. Nieves Cubo Mateo, Dra. Mónica Albaladejo Belmonte (CEU San Pablo)
