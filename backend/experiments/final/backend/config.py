# bci_config.py — BCI Asistencial SSVEP con 4 Celdas Vitales
# Símbolos: Hambre/Sed, Frío/Calor, Emergencias, Baño
# Frecuencias: 8.57, 10, 12, 15 Hz
# Preprocesamiento: Notch + CAR
# Clasificación: CCA con umbral 0.62
 
# --- Hardware ---
SERIAL_PORT = "COM5"     # Puerto de la placa Cyton
 
# --- Adquisición ---
FS         = 250          # Frecuencia de muestreo (Hz)
N_CHANNELS = 8            # Fp1 Fp2 C3 C4 P7 P8 O1 O2
USED_CHANNELS = [4, 5, 6, 7]  # P7, P8, O1, O2 (índices 0-based)
CHANNEL_NAMES = ["P7", "P8", "O1", "O2"]
 
# --- Buffer inicial ---
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

TARGET_CELL = 2
 
# --- Celdas vitales y frecuencias ---
CELLS = {
    1: {"emoji": "🍽️",  "label": "Eat", "freq": 8.57},
    2: {"emoji": "❄️",  "label": "Cold", "freq": 10.0},
    3: {"emoji": "📞",  "label": "SOS", "freq": 12.0},
    4: {"emoji": "🚽",  "label": "WC", "freq": 15.0},
}
 
# --- Parámetros de clasificación ---
TRIAL_SEC = 40          # Duración de cada prueba (s)
CCA_THRESHOLD = 0.15      # Umbral de correlación canónica
NOTCH_FREQ = [50, 100, 150]  # Frecuencias a filtrar (Hz)
NOTCH_WIDTH = 2           # Ancho de banda del filtro notch (Hz)
 
# --- Grabación ---
RECORD_DIR = "recordings"