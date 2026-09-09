<img align="left" width="100" alt="MindAid_logo_transparent_small" src="https://github.com/user-attachments/assets/a28d5faf-4894-45be-ac04-4fe38ef18689" />

<h1 align="center">SSVEP Assistive BCI</h1>

<p align="center">
  Bachelor Thesis · Biomedical Engineering · Carmen Areses Sánchez
</p>

<p align="center">
  A Brain-Computer Interface based on Steady-State Visual Evoked Potentials (SSVEP) for assistive communication using symbolic visual stimuli.
</p>

## Main Features

- SSVEP stimulation
- EEG signal processing
- Canonical Correlation Analysis (CCA) classification
- Web User Interface

## Requirements

```
pip install websockets numpy scipy scikit-learn brainflow
```
---

## Before beginning
 
1. Connect the **USB Dongle** with the Cyton board.
2. Open the **Device Manager** → Ports (COM)
3. Note down the port: usually `COM3`,`COM4`, `COM5` or similar.
4. Edit `backend/config.py`:
```python
  MODE        = "HARDWARE"   # change from "DEMO" to "HARDWARE"
  SERIAL_PORT = "COM5"       # write down your port linked to the OpenBCI equipment 
```

---

## Running the program

```bash
cd backend
python server.py
```

Then open the `frontend/index.html` file in your browser (double-click).

---

## System operation

During each experimental registration (40s), the four visual stimuli flicker simultaneously at their corresponding frequencies. The user focuses their gaze on the target stimulus previously assigned while EEG data are acquired.

The EEG signal is processed in real time using band-pass filtering, notch filtering, Common Average Reference (CAR), and Canonical Correlation Analysis (CCA). At the end of each iteration, the system compares the estimated frequency with the target frequency.

When the detected stimulus corresponds to the target, the selected cell is highlighted in green as visual feedback at the web User Interface.

---

## Electrodes placement

| Channel | Electrode | Region |
|-------------|-----------|--------|
| CH1 | Fp1 | Frontal |
| CH2 | Fp2 | Frontal |
| CH3 | C3  | Central |
| CH4 | C4  | Central |
| **CH5** | **P7**  | **Parietal ← channel used** |
| **CH6** | **P8**  | **Parietal ← channel used** |
| **CH7** | **O1** | **Occipital ← channel used** |
| **CH8** | **O2** | **Occipital ← channel used** |

---

## Frequencies associated per channel 

| Key | Hz  |
|-------|-----|
| 1     | 8.57 |
| 2     | 10 |
| 3     | 12 |
| 4     | 15 |

---

## Project Files (summarized sketch)

```
mindaid-ssvep-bci/
├── backend    ← connects Cyton raw data + preprocessing + CCA + WebSocket
├── frontend   ← calls the UI arrangement + flicker + real-time visualization + WebSocket
└── README.md
```

---

## Project Structure
 
```
mindaid-ssvep-bci/
├── backend/
│   ├── config.py          ← parameters are declared here
│   ├── eegsource.py      ← connection with OpenBCI Cyton board or synthetic board
│   ├── processing.py   ← preprocessing (bandpass + notch + CAR) & CCA classification
|   ├── recorder.py      ← EEG data reocording and file generation 
│   └── server.py          ← WebSocket communication and main application
│
└── frontend/
    ├── index.html
    └── assets/
        ├── css/
        │   └── styles.css (website visualization)
        └── js/
            ├── app.js         ← entry endpoint
            ├── flicker.js     ← flickering SSVEP engine
            ├── websocket.js   ← WebSocket connection + re-connection
            └── ui.js          ← update of DOM
```

---

## Modules Functionalities
 
| File | Functionality |
|---|---|
| `config.py` | System parameters (fs, window, frequencies, recording duration, …) |
| `eegsource.py` | Abstraction of EGG source (DEMO or real HARDWARE) |
| `processing.py` | Filters: bandpass, notch 50 Hz, CAR; CCA classification |
| `recorder.py` | Recording and storage of EEG data in OpenBCI-compatible `.txt` files |
| `server.py` | Handler WebSocket and launch of server |
| `flicker.js` | Key flickering at SSVEP exact frequencies |
| `websocket.js` | Connection/re-connection of the WebSocket and messages exchange management |
| `ui.js` | Use of DOM management created by the html and linked to css that manages its appearance |
| `app.js` | Entry main point that launches the flickering and the websocket communication |

<hr>

<p align="center">
  <img width="100" alt="MindAid" src="https://github.com/user-attachments/assets/a28d5faf-4894-45be-ac04-4fe38ef18689" />
  <br><br>
  <sub><strong>MindAid</strong> · SSVEP Assistive BCI</sub><br>
  <sub>Bachelor Thesis · Biomedical Engineering · Carmen Areses Sánchez</sub>
</p>
