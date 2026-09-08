# config.py - Experiment 2: Simultaneous Flickering upon all cells 


# Hardware
SERIAL_PORT = "COM5"     # Cyton board port: Device Manager → Ports → COMx

# Acquisition 
FS         = 250
N_CHANNELS = 8

# Initial Buffer inicial
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

# Cells and aissgned frequencies for the experiment
# Assumed order of sequence and saved like that with a marker at the .txt file: 1 -> 2 -> 3 -> 4
CELLS = {
    1: 8.57,
    2: 10.0,
    3: 12.0,
    4: 15.0,
}

# Recording time for each cell and for the complete recording 
TRIAL_SEC = 40
TOTAL_SEC = TRIAL_SEC * len(CELLS)   # 160 s continuous reocrding of the 4 cells
