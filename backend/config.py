# BCI config.py 

SERIAL_PORT ="COM5" 

#USE_SYNTHETIC_BOARD = True
USE_SYNTHETIC_BOARD = False

#MODE = "DEMO"
MODE = "HARDWARE"

if MODE not in ("HARDWARE", "DEMO"):
    raise ValueError(f"Invalid MODE {MODE!r}: expected 'HARDWARE' or 'DEMO'")

USE_SYNTHETIC_BOARD = (MODE == "DEMO")  

FS = 250 
N_CHANNELS = 8 
USED_CHANNELS = [4, 5, 6, 7] 
CHANNEL_NAMES = ["P7", "P8", "O1", "O2"]

WINDOW_SEC = 4 
WINDOW     = FS * WINDOW_SEC

TARGET_CELL = 2

CELLS = {
    1: {"emoji": "🍽️",  "label": "Eat", "freq": 8.57},
    2: {"emoji": "❄️",  "label": "Cold", "freq": 10.0},
    3: {"emoji": "📞",  "label": "SOS", "freq": 12.0},
    4: {"emoji": "🚽",  "label": "WC", "freq": 15.0},
}

TRIAL_SEC = 40 

BP_LO = 7.0                  
BP_HI = 70.0                 
NOTCH_FUND = 50.0            
NOTCH_NH   = 3               
NOTCH_Q    = 30              
CCA_HARMONICS    = [1, 2, 3]  
CCA_N_COMPONENTS = 1
APPLY_CAR = True

RECORD_DIR = "recordings"