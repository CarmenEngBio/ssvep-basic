# **SSVEP BCI - Several Models of Brain-Computer Interfaces**

---
 
This repository holds the **development history and previous versions** of the
assistive SSVEP-based Brain-Computer Interface built for my Bachelor Thesis. 
The clean, final system is delivered in a separate repository:
**[mindaid-ssvep-bci](https://github.com/CarmenEngBio/mindaid-ssvep-bci)**. 
This one (`ssvep-basic`) is kept so the earlier stages can be reviewed.
 
Four "vital" cells flicker at different frequencies on the screen; the user is
aimed to gaze at one of them, the occipital-parietal EEG electrodes capture the
raw entry signal with the used **OpenBCI Cyton** board and the **Ultracortex Mark IV**
headset, and the targets are identified by **Canonical Correlation Analysis (CCA)**. 
A small web User Interface (UI) runs the flickering stimulation and the real-time 
feedback. 
This final system is the one placed in the `online/` folders of `backend/` and 
`frontend/`.
 
The repository is arranged as a **progression of experiments**, from the first
single-cell test to the final real-time system. Earlier steps are kept under
`old implementations/`. The configurations presented in the Bachelor Thesis proposed
`exp2_simultaneous` and `exp3_cross_symbols`, are found at the `offline/` folders 
inside `backend/` and `frontend/`.
 
**Stack:** 
- Python (BrainFlow, NumPy, SciPy, scikit-learn, websockets) 
- web UI (HTML/CSS/JS over WebSocket)
- EEG channels used: **P7, P8, O1, O2** (occipito-parietal) 
- Cells: **Eat 8.57 Hz - Cold 10 Hz - SOS 12 Hz - WC 15 Hz**

 
---

## Requirements
 
```bash
pip install websockets numpy scipy scikit-learn brainflow
```
 
## Running an experiment
 
Set your Cyton port in `config.py` module (`SERIAL_PORT = "COM5"`) previously searched at **OpenBCI GUI** or 
at **Device Manager → Ports → COMx**.
Then open the matching frontend:
 
```bash
cd backend/online/final
python server.py
# Then open frontend/online/final/index.html in the browser by double clicking it
```
 
Recording session saved `.txt` files are written to `recordings/` generated folder. The online `final` system
requires the OpenBCI Cyton hardware, but any experiment can also be run without it by switching the EEG source in 
`eegsource.py` to synthetic, which generates fake EEG data so you can watch the whole pipeline, workflow and web UI in
live.

---
 
## Repository structure
 
```
ssvep-basic/
├── backend/                  # Acquisition, Preprocessing and WebSocket communication with the server
│   ├── offline/              # Only acquisition, further analysis was processed at Jupyter Notebooks, see docs
│   │   ├── exp2_simultaneous/
│   │   └── exp3_cross_symbols/
│   └── online/
│       └── final/            # Real-time system
├── frontend/                 # Web User Interface (UI)
│   ├── offline/
│   │   ├── exp2_simultaneous/
│   │   └── exp3_cross_symbols/
│   └── online/
│       └── final/
└── old implementations/      # Earlier steps and deprecated versions that were analyzed
    ├── backend/
    │   ├── offline/
    │   │   ├── exp1_sequential/
    │   │   └── single_cell/
    │   └── online/
    │       └── icons/
    └── frontend/
        ├── offline/
        │   ├── exp1_sequential/
        │   └── single_cell/
        └── online/
            └── icons/
```
 
*offline* = only records raw EEG (`.txt`, OpenBCI-GUI compatible), and preprocessing, feature extraction and classification was analyzed later at Jupyter Notebooks
 
*online* = classifies in real time and provides feedback to the user
 
---
 
## Development path (experiments)
 
1. **single_cell** *(offline)* — First test: validates the SSVEP response with one flickering cell
   (8×8 cm, fixed digit) and 40 s of recording. Frequencies from the 60 Hz refresh were divided by integers
   (4–7).

2. **exp1_sequential** *(offline)* — Four cells recorded one at a time: one cell flickered while the others
   were switched off, changing every 40 s from left to right, so the user gazed at each cell consecutively
   and sequentially.

3. **exp2_simultaneous** *(offline)* — The four cells flicker at once; the user gazes at each for 40 s,
   using an external timer to switch to the next cell from left to right.

4. **exp3_cross_symbols** *(offline)* — Assesses the BCI performance when the target icons are arranged in a
   cross-shaped layout.

5. **icons** *(online)* — First real-time version with the assistive icons and live CCA. Precursor of `final`.

6. **final** *(online)* — Definitive system: preprocessing implementation (bandpass + notch + CAR), CCA
   (harmonics [1, 2, 3]) over 40s trials, real-time feedback.

---
 
<p align="center">
  <strong>Carmen Areses Sánchez</strong><br>
  Biomedical Engineering · Bachelor Thesis 2026
</p>

 
