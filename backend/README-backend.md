 # Backend Manual - Server Endpoint explanation

 **Assistive communication SSVEP with 4 vital need cells**:
 - Each symbol indicates: **Hunger/Thirsty**; **Cold/Warm**; **Call Emergency Services** or **WC**.
 - The used frequencies are: **8.57**, **10**, **12**, **15** Hz.
 - Preprocessing: **Notch** filtering and **CAR**.
 - Classification: **CCA** using maximum correlation

 ## Requirements

 **Python** language **must** be **installed** to run the server:

 ```
 pip install websockets numpy scipy scikit-learn brainflow
 ```
---

# Config.py 

 Where the system **global parameters** of the SSVEP BCI are placed.

 For this module:
 1. Selection of the execution MODE:
```python
MODE        = "HARDWARE"   # "DEMO" | "HARDWARE"
SERIAL_PORT = "COM5"   # If MODE = "HARDWARE" it matches the serial port at Device Manager → Ports → COMx
```
 When there is no hardware available and to test the full pipeline:
```python
USE_SYNTHETIC_BOARD = True   # Uses generated BrainFlow synthetic board
# If HARDWARE is selected -> real OpenBCI Cyton board equipment is used (USE_SYNTHETIC_BOARD = False)
# If DEMO is chosen -> BrainFlow synthetic board is used (USE_SYNTHETIC_BOARD = True)
```
 2. Acquisition Hardware
 ```python
    FS         = 250   # Cyton fs is around 250 Hz
    N_CHANNELS = 8     # Fp1 Fp2 C3 C4 P7 P8 O1 O2
    USED_CHANNELS = [4, 5, 6, 7] # P7, P8, O1, O2 are used by the classifier
 ```
 3. Classification Window
 The typical literature values are between 1–4 s.
 ```python
    WINDOW_SEC = 4 # window length for classification (s)
    WINDOW     = FS * WINDOW_SEC   # number of samples: 250 x 4 = 1000 samples
 ```
 4. Session per target cell
 The online server runs one cell per session.
 To set which symbol the user is asked to gaze at the following is changed to record every symbol:
```python
TARGET_CELL = 4 # variable changed in every session to assign the objective cell

# These are the assistive vital cells with linked stimulus frequencies:
CELLS = {
    1: {"emoji": "🍽️",  "label": "Eat", "freq": 8.57},
    2: {"emoji": "❄️",  "label": "Cold", "freq": 10.0},
    3: {"emoji": "📞",  "label": "SOS", "freq": 12.0},
    4: {"emoji": "🚽",  "label": "WC", "freq": 15.0},
}
```
5. Trial timing
 Can be adjusted considering the possible effects (higher recording time -> introduction of artifacts due to tiredness):
```python
TRIAL_SEC = 40  # Duration of each session (s)
```
6. Signal Processing
 ```python
    #Bandpass
    BP_LOW       = 7.0    # low cut Hz
    BP_HIGH      = 70.0   # high cut Hz
    NOTCH_FREQ   = 50.0   # Hz (Power Line Interference)
    # Notch comb
    NOTCH_FUND = 50.0            # Fundamental frequency of PLI (Hz)
    NOTCH_NH   = 3               # Harmonics included: 50, 100, 150 Hz
    NOTCH_Q    = 30              # Notch quality factor
    # CCA
    CCA_HARMONICS    = [1, 2, 3]  # Number of reference harmonics: f, 2f and 3f
    CCA_N_COMPONENTS = 1 # canonical component following the SSVEP standard
    # CAR
    APPLY_CAR = True   # Common Average Reference
 ```
7. Recording sessions storage
 Raw EEG data is saved in a `.txt` file to try to mimic OpenBCI GUI operation:
```python
RECORD_DIR = "recordings" # files are saved automatically inside this generated folder
```
---

 # Server.py

 SSVEP BCI Server with real-time feedback operation. It implements:
 - CCA classification
 - Recording one 40s block per session: the user gazes at the TARGET_CELL while all flicker simultaneously. 
 - Every 4s window is classified with CCA and the result is streamed to the frontend.
 - To record every symbol, change **TARGET_CELL** in config.py and run again.

 It is also the entry point of the backend where:
  - **BCIBlock()** accumulates the EEG windows and classifies them with CCA. 
  - **run_blocks(ws, source)** runs one 40s block for the TARGET_CELL, classifying every window.
  - **handler(ws, source)** establishes the connection with the client, manages the exchange regarding connection messages and launches run_blocks.
  - The **main()** launches the server. 
 
 All the specified parameters are declared and initialised at the `config.py` file.
 The signal logics is split among the different specialised modules.

 ## BCIBlock
 - Each 0.1 s it gathers the **window** of the signal (through CytonEEG class), then it **preprocess** the signal (through EEGProcessor class), it applies the **classification** (through EEGProcessor) and lastly the data is **sent** through the WS in order to be displaced at the UI.

 - It splits the discrimination upon 0.5 Hz of difference to avoid missclassifications:
 ```python
 is_correct = abs(best_freq - target_freq) < 0.5
 ```
 - According to the Nyquist theorem, it requires at least **2s** of raw EEG data before classifying:
 ```python
 def has_enough_data(self) -> bool:
        return len(self.trial_timestamps) > FS * 2
 ```
 - This class returns the **highest correlation value** in comparison with the other 3 values from the other cells,
 it returns the **frequency** associated to that winner value, a **boolean** based on the **correct classification**
 and **all the correlations** obtained from that **iteration**.

 ## Run Blocks
 Receives the ***raw EEG data per session**, calculates the **times of signal processing per iteration**, **classifies** the data and **calculates the accuracy** to send it through the WS. 

 Initially it waits for 4s of buffer to be full:
 ```python
 raw_eeg, raw_ts = await source.get_window()  # 4s of EEG
```
 Then it starts recording through the recorder. 
 When the 40s are reached, the full trial was saved to the disk and the recording automatically stopped:
 ```python
 new_eeg, new_ts = source.get_new_samples()
    if recorder.is_recording:
        recorder.write_chunk(new_eeg, new_ts)
    recorder.stop()
 ```
 Some of the **results** calculated at each step of this function are **shown at the server console** (i.e.✅CORRECT,
 ❌INCORRECT, Result, Time elapsed and Accuracy) and others are **sent to the frontend through the WebSocket** (i.e. cell_id, emoji, label, correlation, detected_freq, ...).

---

 # Eegsource.py 
 
 Cyton acquisition interface (real board or synthetic).
 The EEG signal source is placed here. It contains the **USE_SYNTHETIC_BOARD == True** (fakes the signal) and the **USE_SYNTHETIC_BOARD == False** (real hardware).
 Then the `server.py` instances one or the other depending on the `config.MODE`. 

 This module gathers:
 - **CytonEEG()** class: it is the OpenBCI Cyton board / Brainflow synthetic board interface.
 - **get_window(self)**: returns the last WINDOW (1000) samples as (eeg, timestamps) without deleting them. If the buffer is not full it waits for the missing samples to always classify with a complete window:
 ```python
 if n < WINDOW:
            missing_sec = (WINDOW - n) / FS
            await asyncio.sleep(missing_sec + 0.1)
            data = self.board.get_current_board_data(WINDOW)
```
 - **get_new_samples(self)**: it drains the Brainflow buffer and returns directly new (eeg, timestamps) data empting the buffer to paste it at the generated recording file.  

 ---

 # Preprocessing.py

 Includes SSVEP preprocessing and CCA classification.
 - Preprocesses the gathered signals by using **Bandpass**, **Notch** and **CAR**
 - Processes the **CCA reference comparison signals** built from CCA_HARMONICS.
 - Classifies the entry data against the reference signals built.

 As a summary, the pipeline is the following:
 1. Double Butterworth bandpass
 2. Notch comb (50 / 100 / 150 Hz)
 3. Channel selection (P7, P8, O1, O2) which improved SSVEP discrimination
 4. Common Average Reference (CAR)

 All the parameters established came from the `config.py` file.

 # Pre-compute filters

 - **def build_bandpass(lo=BP_LO, hi=BP_HI, order=4)**: 
    - It implements a bandpass filter of 4th order. 
    - It calculates the Butterworth coefficients normalized at the Nyquist frequency.
    - It erases the DC offset and high frequency artifacts.
    - Signal used is a one dimensional array (one window of one channel).

 - **def build_notch_comb(fundamental=NOTCH_FUND, n_harmonics=NOTCH_NH, Q=NOTCH_Q)**:
    - It implements Notch comb at fundamental freq (50 Hz) and its harmonics (50 / 100 / 150 Hz).
    - It erases the power line interference. 
    - Signal used is a one dimensional array (one window of one channel).

 This module also includes:
 - **EEGProcessor()**: it integrates the preprocessing and classification pipeline.
 - **CCA** implementation inside this previous class mentioned.

 Inside EEGProcessor the following functions are included:
 1. **preprocess(self, eeg_data)**:
      - Gathers the full pipeline: bandpass + notch comb + channel selection and CAR.
      - It returns the eeg data filtered to classify it afterwards.

      ```python
      # 1. Double Butterworth bandpass
      eeg = sosfiltfilt(_SOS_BP, eeg_data, axis=1) # zero phase filter (both directions) to provide stability
      eeg = sosfiltfilt(_SOS_BP, eeg, axis=1)

      # 2. Notch comb (50 / 100 / 150 Hz)
      for sos_n in _SOS_NOTCH:
         eeg = sosfiltfilt(sos_n, eeg, axis=1)

      # 3. Selection of occipital and parietal channels
      eeg = eeg[self.used_channels, :]

      # 4. Common Average Reference
      if APPLY_CAR:
         eeg = self.apply_car(eeg)
        
      return eeg
      ```
      - Common Average Reference substracts the spatial average to each sample across channels.
      - It reduces the common artifacts to all the electrodes (movement, EMG).
      - eeg is an ndarray: `(N_CHANNELS, WINDOW)`
      ```python
      def apply_car(self, eeg_data):
        mean_ref = np.mean(eeg_data, axis=0, keepdims=True)
        return eeg_data - mean_ref
      ```
 
 2. **CCA** 
      - It is the SSVEP Classifier based on Canonical Correlation Analysis (CCA).
      - For each candidate frequency, it is built a sinusoidal reference signal with N harmonics and it is calculated the canonical one with the EEG window. 
      - The frequency with mayor correlation will be the prediction.

   - **generate_references(self, frequency, n_samples)**:
    - Builds the sinusoidal reference matrix for one frequency.
    - Includes `N_HARMONICS` to combine them with sines and cosines per harmonic.
    - This function is the bank of reference generated signals.
    - It returns an array of shape (n_samples, 2*len(CCA_HARMONICS)).
   ```python
    t = np.arange(n_samples) / self.fs
    components = []
    for harmonic in CCA_HARMONICS:
        freq_h = frequency * harmonic
        components.append(np.sin(2 * np.pi * freq_h * t))
        components.append(np.cos(2 * np.pi * freq_h * t))
    return np.array(components).T
   ```
 
   - **classify(self, eeg_data, frequencies)**:
    - It classifies one EEG window with CCA against all the SSVEP frequencies.
    - The parameters are: eeg, which is a ndarray `(n_channels, n_samples)` already preprocessed.
    - It returns (best_freq, best_corr, all_corrs) via CCA over candidate freqs.

   - **def canonical_corr(self, X, Y)**:
    - It considers the first canonical correlation between X and Y.

---

# Recorder.py

 It is the EEG recorder in OpenBCI GUI .txt format
 It registers the EGG raw entry signals like OpenBCI GUI does.

 This module contains:
 - **EEGRecorder()**: this class is a thread-safe recorder that writes OpenBCI GUI .txt files, following the GUI header:
   ```python
    _COLUMN_HEADER = (
        "Sample Index, EXG Channel 0, EXG Channel 1, EXG Channel 2, "
        "EXG Channel 3, EXG Channel 4, EXG Channel 5, EXG Channel 6, "
        "EXG Channel 7, Accel Channel 0, Accel Channel 1, Accel Channel 2, "
        "Not Used, Digital Channel 0 (D11), Digital Channel 1 (D12), "
        "Digital Channel 2 (D13), Digital Channel 3 (D17), Not Used, "
        "Digital Channel 4 (D18), Analog Channel 0, Analog Channel 1, "
        "Analog Channel 2, Timestamp, Marker Channel, Timestamp (Formatted)"
    )
   ```
 - **start(self, label="bci_session")**: opens a new file and writes the header.
 - **stop(self)**: closes the file and ends the recording.
 - **write_chunk(self, eeg_uv, timestamps, accel=None)**: writes a chunk of EEG samples to the open file.
