# config.py - Experiment 1: Sequential Flickering
# One cell remains active while the others are turned off

# Hardware
SERIAL_PORT = "COM5"    

# Acquisition 
FS         = 250
N_CHANNELS = 8

# Initial Buffer inicial
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

# Cells and assigned frewuencies
# Iteration goes from left to right
CELLS = {
    1: 8.57,
    2: 10.0,
    3: 12.0,
    4: 15.0,
}

# Timing 
TRIAL_SEC = 40
TOTAL_SEC = TRIAL_SEC * len(CELLS)   # 160 s continuous recording (4 cells)
