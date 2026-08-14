# BCI config.py 
# Assistive communication SSVEP with 4 vital need cells
# Each symbol indicates: Hunger/Thirsty; Cold/Warm; Call Emergency Services or WC.
# The used frequencies are: 8.57, 10, 12, 15 Hz.
# Preprocessing: Notch filtering and CAR.
# Classification: CCA using maximum correlation

# Hardware configuration
SERIAL_PORT ="COM5" # Cyton used port
# Cyton serial port (Windows: Device Manager -> Ports -> COMx)

USE_SYNTHETIC_BOARD = False   # True -> BrainFlow synthetic board (no hardware, for testing full pipeline)

# Acquisition
FS = 250 # Sampling frequency (Hz)
N_CHANNELS = 8 # Fp1 Fp2 C3 C4 P7 P8 O1 O2
USED_CHANNELS = [4, 5, 6, 7] # P7, P8, O1, O2 used by the classifier
CHANNEL_NAMES = ["P7", "P8", "O1", "O2"]

WINDOW_SEC = 4 # window length for classification (s)
WINDOW     = FS * WINDOW_SEC

# Session target cell
# The online server runs one cell per session
# To set which symbol the user is asked to gaze at this is changed to record every symbol.
TARGET_CELL = 4

# Assistive vital cells with linked stimulus frequencies
CELLS = {
    1: {"emoji": "🍽️",  "label": "Eat", "freq": 8.57},
    2: {"emoji": "❄️",  "label": "Cold", "freq": 10.0},
    3: {"emoji": "📞",  "label": "SOS", "freq": 12.0},
    4: {"emoji": "🚽",  "label": "WC", "freq": 15.0},
}

# Trial timing
TRIAL_SEC = 40  # Duration of each session (s)

# Signal processing

# Bandpass
BP_LO = 7.0                  # Hz (low cut)
BP_HI = 70.0                 # Hz (high cut)
# Notch comb
NOTCH_FUND = 50.0            # Fundamental (Hz)
NOTCH_NH   = 3               # Harmonics -> 50, 100, 150 Hz
NOTCH_Q    = 30              # Notch quality factor
# CCA
CCA_HARMONICS    = [1, 2, 3]  # Fundamental + 2nd + 3rd harmonic
CCA_N_COMPONENTS = 1
# Common Average Reference
APPLY_CAR = True

# Recording sessions storage
RECORD_DIR = "recordings"