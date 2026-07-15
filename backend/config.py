# BCI config.py 
# Assistive communication SSVEP with 4 Vital functionalities Cells
# Each symbol indicates: Hunger/Thirsty; Cold/Warm; Call emergency or WC.
# The used frequencies are: 8.57, 10, 12 and 15 Hz.
# Prepocessing variables are linked with Notch and CAR
# Classification to CCA with 0.62 threshold 

# Hardware configuration
SERIAL_PORT ="COM5" # Cyton used port

# Acquisition
FS = 250 # Sampling frequency (Hz)
N_CHANNELS = 8 # Fp1 Fp2 C3 C4 P7 P8 O1 O2
USED_CHANNELS = [4, 5, 6, 7] # P7, P8, O1, O2 
CHANNEL_NAMES = ["P7", "P8", "O1", "O2"]

WINDOW_SEC = 1
WINDOW = FS*WINDOW_SEC

CELLS = {
    1: {"emoji": "", "label": "Hunger/Thirsty", "freq": 8.57},
    1: {"emoji": "", "label": "Cold/Warm", "freq": 10},
    1: {"emoji": "", "label": "Call Emergency", "freq": 12},
    1: {"emoji": "", "label": "WC", "freq": 15},
}

# Classification parameters
TRIAL_SEC = 10 
CCA_THRESHOLD = 0.62 # canonical correlation threshold
NOTCH_FREQ = 50

# Recroding sessions
RECOR_DIR = "recordings"