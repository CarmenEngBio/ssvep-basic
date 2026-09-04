# config.py - Initial Testing Phase: Unique Cell
# Minimal configuration to validate SSVEP answer to just one stimulus.
# No classification is made (CCA) as it just records the raw signal and process it through Jupyter Notebooks.
#

# Hardware
SERIAL_PORT = "COM5"     # Cyton board port

# Acquisition
FS         = 250          # Cyton sampling frequency (Hz)
N_CHANNELS = 8             # Fp1 Fp2 C3 C4 P7 P8 O1 O2

# Initial buffer inicial
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

# Unique assigned stimulus
LABEL = "1"
FREQ  = 8.57         # Hz

#LABEL = "2"
#FREQ  = 10

#LABEL = "3"
#FREQ  = 12

#LABEL = "4"
#FREQ  = 15

# Automatic recording 
RECORD_SEC = 40 # Fixed duration without pressing any stop recording button 

