# BCI config.py - Assistential SSVEP BCI with 4 Vital Cellls
# Target icons: Hunger, Cold, Emergencies, Bathroom
# Frecuencies: 8.57, 10, 12, 15 Hz
 
# Hardware
SERIAL_PORT = "COM5"     
 
# Acquisition
FS         = 250          # (Hz)
N_CHANNELS = 8            # Fp1 Fp2 C3 C4 P7 P8 O1 O2
USED_CHANNELS = [4, 5, 6, 7]  # P7, P8, O1, O2
CHANNEL_NAMES = ["P7", "P8", "O1", "O2"]
 
# Initial Buffer
WINDOW_SEC = 2
WINDOW     = FS * WINDOW_SEC
 
# Vital cells with linked frequencies
CELLS = {
    1: {"emoji": "🍽️",  "label": "Comer", "freq": 8.57},
    2: {"emoji": "❄️",  "label": "Frío", "freq": 10.0},
    3: {"emoji": "🚨",  "label": "SOS", "freq": 12.0},
    4: {"emoji": "🚽",  "label": "Baño", "freq": 15.0},
}
 
# Classification parameters
TRIAL_SEC = 40          # (s)
CCA_THRESHOLD = 0.15      # Canonical correlation threshold 
NOTCH_FREQ = [50, 100, 150]  # (Hz)
NOTCH_WIDTH = 2           # (Hz)
 
# Recording path
RECORD_DIR = "recordings"