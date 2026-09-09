# SSVEP BCI - Several Models of Brain-Computer Interfaces
 
An assistive SSVEP-based Brain–Computer Interface was built (check at https://github.com/CarmenEngBio/mindaid-ssvep-bci). 
Four "vital" cells flicker at different frequencies at the screen; the user gazes at one, the occipital EEG is captured with
an **OpenBCI Cyton** board and Ultracortex Mark IV headset, and the target is identified by 
**Canonical Correlation Analysis (CCA)**. A small web interface runs the stimulation and the
real-time feedback named as final placed at online folders at backend and frontend. 
The repository is arranged as a **progression of experiments**, from the first single-cell test to the final real-time system
named as final;
earlier steps are kept under `old implementations/` while presented Bachelor Thesis configurations mentioned as found at backend and frontend paths as offline folder and as exp2_simultaneous and exp3_cross_symbols.
 
**Stack:** Python (BrainFlow, NumPy, SciPy, scikit-learn, websockets) + web UI
(HTML/CSS/JS over WebSocket). EEG channels used: **P7, P8, O1, O2**
(occipito-parietal). Cells: **Eat 8.57 Hz · Cold 10 Hz · SOS 12 Hz · WC 15 Hz**.
 
---

## Requirements
 
```bash
pip install websockets numpy scipy scikit-learn brainflow
```
 
## Running an experiment
 
Set your Cyton port in that experiment's `config.py` (`SERIAL_PORT = "COM5"`).

Then open the matching frontend:
 
```bash
cd backend/online/final
python server.py
# Then open frontend/online/final/index.html in the browser by double clicking it
```
 
Recordings are written to `recordings/` generated folder. The online `final` system
needs the OpenBCI Cyton hardware, but all experiments can be runned by reassigning data al eegsource as synthetic which
places fake EEG data to launch a simulation an observer the pipeline, workflow and web User Interface (UI).
---
 
## Repository structure
 
```
ssvep-basic/
├── backend/                  # Acquisition, Preprocessing and WebSocket communication with the server
│   ├── offline/              # Only acquisition, further analysis was processed at Jupyter Notebooks, see docs
│   │   ├── exp2_simultaneous/
│   │   └── exp3_cross_symbols/
│   └── online/final/         # Real-time system
├── frontend/                 # Web User Interface (UI)
│   ├── offline/{exp2_simultaneous, exp3_cross_symbols}/
│   └── online/final/
└── old implementations/      # Earlier steps and deprecated versions that were analyzed
    ├── backend/  offline/{exp1_sequential, single_cell} and online/icons
    └── frontend/ offline/{exp1_sequential, single_cell} and online/icons
```
 
*offline* = only records raw EEG (`.txt`, OpenBCI-GUI compatible), and preprocessing, feature extraction and classification was analyzed later at Jupyter Notebooks

*online* = classifies in real time and provides feedback to the user
 
---
 
## Development path (experiments)
 
1. **single_cell** *(offline)* — First test: validates the SSVEP response with one flickering cell 
   (8×8 cm, fixed digit) and 40 s of recording. Frequencies from the 60 Hz refresh were divided by integers
   (4–7).

2. **exp1_sequential** *(offline)* — Four cells were recorded were one cell was active flickering while the others were      switched off. This occured each 40s from left to right in order to gaze at each cell consecutively and sequentially.

3. **exp2_simultaneous** *(offline)* — The four cells flicker at once; the user
   gazes at each for 40s with the use of an external timer to switch to next the consecutive cell from left to right. 

4. **exp3_cross_symbols** *(offline)* — Discriminates the BCI performance when target icons are arranged in a cross-shaped.

5. **icons** *(online)* — First real-time version with the assistive icons and
   live CCA (`server_old.py` → `server_final.py`). Precursor of `final`.

6. **final** *(online)* — Definitive system: preprocessing implementation (bandpass + notch + CAR) + CCA (harmonics [1, 2, 3])  over 40 s trials, real-time feedback.

---
 
**Author:** Carmen Areses Sanchez - Biomedical Engineering - Bachelor Thesis 2026
**License:** [`LICENSE`](LICENSE) 
 