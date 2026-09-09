# BCI config.py - Assistive SSVEP BCI with 4  vital cells
# Target icons: Hunger/Thirsty, Cold/Warm, Emergencies, Bathroom
# Frequencies: 8.57, 10, 12, 15 Hz
 
# Hardware
SERIAL_PORT = "COM5"
 
# Acquisition
FS         = 250          # (Hz)
N_CHANNELS = 8            # Fp1 Fp2 C3 C4 P7 P8 O1 O2
USED_CHANNELS = [4, 5, 6, 7]  # P7, P8, O1, O2
CHANNEL_NAMES = ["P7", "P8", "O1", "O2"]
 
# Initial Buffer
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

TARGET_CELL = 4
 
# Vital Cells and their frequencies
CELLS = {
    1: {"emoji": "🍽️",  "label": "Eat", "freq": 8.57},
    2: {"emoji": "❄️",  "label": "Cold", "freq": 10.0},
    3: {"emoji": "📞",  "label": "SOS", "freq": 12.0},
    4: {"emoji": "🚽",  "label": "WC", "freq": 15.0},
}
 
# Classification Parameters
TRIAL_SEC = 40          # Time of each recording test
CCA_THRESHOLD = 0.15      # Canonical correlation threshold
NOTCH_FREQ = [50, 100, 150]  # (Hz)
NOTCH_WIDTH = 2           # (Hz)
 
# Recording path or folder
RECORD_DIR = "recordings"