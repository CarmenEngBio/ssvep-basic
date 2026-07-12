# exp3_config.py — Experimento 3: 4 Celdas en Cruz (Simultáneo)
# Configuración para un experimento de 4 estímulos SSVEP frecuencias simultáneas
# dispuestos en forma de cruz, cada uno mostrando un emoji de contexto emocional:
# - Superior (❄️ Frío):      10.0 Hz
# - Inferior (😴 Cansado):   12.0 Hz  
# - Izquierda (🔥 Calor):    8.0 Hz
# - Derecha (😣 Dolor):      9.0 Hz

# --- Hardware ---
SERIAL_PORT = "COM5"     # Puerto de la placa Cyton

# --- Adquisición ---
FS         = 250          # Frecuencia de muestreo del Cyton (Hz)
N_CHANNELS = 8            # Fp1 Fp2 C3 C4 P7 P8 O1 O2

# --- Buffer inicial ---
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

# --- Estímulos simultáneos (4 celdas en cruz) ---
# Frecuencias seleccionadas respetando:
# - Divisibilidad por 60 Hz (refresh rate estándar)
# - Espaciamiento mínimo recomendado (0.5–1.0 Hz)
# - Compatibilidad con análisis armónico
STIM_MATRIX = [
    {"key": "top",    "label": "❄️ Frío",   "emoji": "❄️", "freq": 8.57},
    {"key": "left",   "label": "🔥 Calor",   "emoji": "🔥", "freq": 10.0},
    {"key": "right",  "label": "😣 Dolor",   "emoji": "😣", "freq": 12.0},
    {"key": "bottom", "label": "😴 Cansado", "emoji": "😴", "freq": 15.0},
]

# --- Grabación automática ---
RECORD_SEC = 160          # Duración del experimento en segundos
