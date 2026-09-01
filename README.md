# Single-Cell Test - SSVEP BCI

First trials to validate the SSVEP stimulation response as well as the signal quality for certain
frequency values before implementing and debugging a built real time system and its performance.

- Just one flickering cell with a dark fixated digit placed at the center is shown (8x8 cm size).
- Automatic recording is saved during 40s, with the same `.txt` format compatible with OpenBCI GUI.
- As this approach comprehends the offline implementation, the preprocessign, filtering and classification steps are done at
Jupyter Notebooks. 
- The tested frequency values were obtained from the division resulting from the laptop refresh rate (60 Hz) and integers (4-7)

## Structure

```
ssvep-basic/
├── README.md
├── backend/
│   ├── config.py      # SERIAL_PORT, FREQ (8.57 Hz), RECORD_SEC (40 s)
│   ├── eegsource.py    # Connected through CytonEEG
│   ├── recorder.py     # Saves raw EEG data in a .txt file
│   └── server.py       # Handler of the WebSocket and enables recording till 40s
└── frontend/
    ├── index.html
    └── assets/ 
        ├── css/styles.css   # Configures web User Interface appearance
        └── js/
            ├── flicker.js     # Cell flickering engine with white color
            ├── websocket.js   # Manages the messages exchanged
            ├── ui.js          # Links the css with the messages exchanged through the WebSocket
            └── app.js  # Connects the flickering and the User Interface configuration with the WS
```

## How to execute it

1. Edit `backend/config.py` and indicate the correct `SERIAL_PORT` for the Cyton.
2. Install the dependencies required to launch this application:
   ```
   pip install websockets numpy brainflow
   ```
3. Launch the server:
   ```
   python backend/server.py
   ```
4. Then it is double clicked the `frontend/index.html` to open the web UI 
5. When the "● Cyton connected" appears, it is possible to press **Begin test (40 s)** and
   user must focus their sight to the desired number while it flickers. After 40s the recording is automatically saved. 
6. The file `.txt` will appear at `backend/recordings/` which can processed at Jupyter Notebooks to analyze the system's operation.

