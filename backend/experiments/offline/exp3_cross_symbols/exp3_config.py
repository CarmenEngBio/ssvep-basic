# exp3_config.py - Experiment 3: 4 Cells will be changed into a Cross arrangement

# - Upwards icons shown is linked to Cold as ❄️ emoji at a frequency value of 8.57 Hz
# - Down icon displayed is assigned as Tired as 😴 symbol at a freq value of 15.0 Hz  
# - Left cell is linked to Warm expressed as 🔥 icon with a value of 10.0 Hz
# - Right cell is associated to Pain with the 😣 emoji and to the 12.0 Hz value

# Hardware
SERIAL_PORT = "COM5"     

# Acquisition
FS         = 250          # (Hz)
N_CHANNELS = 8            # Fp1 Fp2 C3 C4 P7 P8 O1 O2

# Initial Buffer
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

# 4 cross-shaped simultaneous stimulation considering:
# - The screen refresh rate used equal to 60 Hz that defines the range of frequencies
# - Inclusion of SSVEP frequencies with possibility of later processing their harmonics
STIM_MATRIX = [
    {"key": "top",    "label": "❄️ Cold",   "emoji": "❄️", "freq": 8.57},
    {"key": "left",   "label": "🔥 Warm",   "emoji": "🔥", "freq": 10.0},
    {"key": "right",  "label": "😣 Pain",   "emoji": "😣", "freq": 12.0},
    {"key": "bottom", "label": "😴 Tired", "emoji": "😴", "freq": 15.0},
]

# Automatic recording time 
RECORD_SEC = 160          # in seconds
