# BCI server module 
 
import asyncio
import json
import time
import numpy as np
import websockets
 
from config import (
    CELLS, TRIAL_SEC, WINDOW_SEC, WINDOW, USED_CHANNELS,
    CCA_THRESHOLD, FS
)
from eegsource import CytonEEG
from recorder import EEGRecorder
from processing import EEGProcessor
 
 
recorder = EEGRecorder()
processor = EEGProcessor()
 
 
class BCISession:
    # Handles a BCI session of 40s by getting the signal, processing it and classifying it. 
 
    def __init__(self):
        self.trial_data = []  # Data buffer during the recording trial 
        self.trial_timestamps = []
        self.start_time = None
        self.selected_cell = None
        self.selection_time = None
 
    def reset(self):
        self.trial_data = []
        self.trial_timestamps = []
        self.start_time = None
        self.selected_cell = None
        self.selection_time = None
 
    def add_samples(self, eeg_chunk, timestamps):
        # Cummulates samples during the recording trial
        self.trial_data.append(eeg_chunk)
        self.trial_timestamps.extend(timestamps)
 
    def has_enough_data(self) -> bool:
        # Verifies if there are enough samples to process and classify
        return len(self.trial_timestamps) > FS * 2  # At least less than 2 seconds
 
    def classify(self) -> dict:
        
        if not self.has_enough_data():
            return None
 
        X = np.hstack(self.trial_data)
 
        X_processed = processor.preprocess(X)
 
        frequencies = [CELLS[i]["freq"] for i in sorted(CELLS.keys())]
 
        best_freq, best_corr, all_corrs = processor.classify(X_processed, frequencies)
 
        # Correlations are gahtered with respect to a cut threshold
        if best_corr < CCA_THRESHOLD:
            return {"cell_id": None, "corr": best_corr, "time_ms": None}
 
        # Matching the best correlation to its cell
        cell_id = None
        for cid, info in CELLS.items():
            if abs(info["freq"] - best_freq) < 0.1:
                cell_id = cid
                break
 
        # Time of iteration
        time_ms = (len(self.trial_timestamps) / FS) * 1000
 
        self.selected_cell = cell_id
        self.selection_time = time_ms
 
        return {
            "cell_id": cell_id,
            "corr": round(best_corr, 4),
            "time_ms": round(time_ms, 2),
            "all_corrs": {f: round(c, 4) for f, c in all_corrs.items()}
        }
 
 
bci_session = BCISession()
 
 
async def run_trial(ws, source, trial_id: int):
    # Executes one classification trial
    print(f"\n[Trial {trial_id}] initialising ...")
    bci_session.reset()
    bci_session.start_time = time.time()
 
    # Sends a message regarding the begin of the test
    await ws.send(json.dumps({
        "type": "trial_started",
        "trial_id": trial_id,
        "duration": TRIAL_SEC,
    }))
 
    # Accumulates data during 40s
    elapsed = 0.0
    while elapsed < TRIAL_SEC:
        raw_eeg = source.get_window()
        new_eeg, new_ts = source.get_new_samples()
 
        if new_eeg.shape[1] > 0 and recorder.is_recording:
            recorder.write_chunk(new_eeg, new_ts)
            bci_session.add_samples(new_eeg, new_ts)
 
        elapsed = time.time() - bci_session.start_time
        await asyncio.sleep(0.05)
 
    result = bci_session.classify()
 
    if result and result["cell_id"] is not None:
        cell_info = CELLS[result["cell_id"]]
        msg = {
            "type": "selection",
            "trial_id": trial_id,
            "cell_id": result["cell_id"],
            "emoji": cell_info["emoji"],
            "label": cell_info["label"],
            "correlation": result["corr"],
            "time_ms": result["time_ms"],
        }
 
        print(f"[Selection] Cell {result['cell_id']} "
              f"({cell_info['label']}) - Correlation: {result['corr']}")
    else:
        msg = {
            "type": "no_selection",
            "trial_id": trial_id,
            "correlation": result["corr"] if result else 0.0,
            "reason": "Correlation lower than threshold",
        }
        print(f"[No Selection] Not enough correlation value")
 
    await ws.send(json.dumps(msg))
 
 
async def handler(ws, source):
    print(f"✓ Client connected: {ws.remote_address}")
 
    try:
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.01)
                msg = json.loads(raw)
 
                if msg.get("type") == "start_session" and not recorder.is_recording:
                    source.get_new_samples()
 
                    label = msg.get("label", "bci_session")
                    fname = recorder.start(label)
 
                    await ws.send(json.dumps({
                        "type": "session_started",
                        "file": fname or "",
                        "cell_labels": {str(k): v["emoji"] + " " + v["label"]
                                       for k, v in CELLS.items()},
                    }))
 
                    await run_trial(ws, source, trial_id=1)
 
                    recorder.stop()
                    await ws.send(json.dumps({
                        "type": "session_ended",
                    }))
 
            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass
 
            # Signal quality is assesed continuosly 
            raw_eeg = source.get_window()
            occ_var = float(np.mean(np.var(raw_eeg[4:8], axis=1)))
 
            await ws.send(json.dumps({
                "type": "status",
                "recording": recorder.is_recording,
                "signal_quality": round(occ_var, 2),
            }))
 
            await asyncio.sleep(0.5)
 
    except websockets.exceptions.ConnectionClosed:
        print("✗ Client disconnected")
    finally:
        if recorder.is_recording:
            recorder.stop()
 
 
async def main():
    print("=" * 70)
    print("  Assistential SSVEP BCI - 4 Vital Cells  ")
    print("=" * 70)
    print("  Cells:")
    for cid, info in sorted(CELLS.items()):
        print(f"    {cid}. {info['emoji']} {info['label']:25} → {info['freq']} Hz")
    print(f"\n  CCA threshold: {CCA_THRESHOLD}")
    print(f"  Timing per trial: {TRIAL_SEC}s")
    print("  Preprocessing: Bandpass, Notch and CAR")
    print("  Connection with Cyton hardware.")
    print("=" * 70)
 
    source = CytonEEG()
 
    print(f"  Waiting {WINDOW_SEC}s to fill the EEG buffer ...")
    await asyncio.sleep(WINDOW_SEC)
    print("  Ready! Open the browser and select 'Begin Session'.\n")
 
    try:
        async with websockets.serve(
            lambda ws: handler(ws, source),
            "localhost", 8765
        ):
            await asyncio.Future()
    finally:
        source.stop()
 
 
if __name__ == "__main__":
    asyncio.run(main())