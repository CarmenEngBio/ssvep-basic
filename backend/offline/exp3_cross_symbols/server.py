# server.py - Experiment 3: 4 Cross-shaped Cells
# Recording saves automatically the raw entry EEG data and ends when 160s have passed.

import asyncio
import json
import time
import numpy as np
import websockets

from exp3_config import STIM_MATRIX, RECORD_SEC, WINDOW_SEC, WINDOW
from exp3_eegsource import CytonEEG
from exp3_recorder import EEGRecorder

recorder = EEGRecorder()


async def auto_stop(ws, duration: float):

    # After the complete recording time is achieved it stops the recording and saves automatically the data at the generated file.
    
    await asyncio.sleep(duration)
    if recorder.is_recording:
        recorder.stop()
        try:
            await ws.send(json.dumps({
                "type": "recording_stopped",
                "reason": "auto",
                "total_duration": duration,
            }))
        except websockets.exceptions.ConnectionClosed:
            pass


async def handler(ws, source):
    print(f"✓ Client conected: {ws.remote_address}")
    stop_task = None

    try:
        while True:

            # Incoming messages are exchanged to indicate the begin of the test and recording

            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.01)
                msg = json.loads(raw)

                if msg.get("type") == "start_recording" and not recorder.is_recording:
                    fname = recorder.start(msg.get("label", "exp3_test"))
                    await ws.send(json.dumps({
                        "type":     "recording_started",
                        "file":     fname or "",
                        "duration": RECORD_SEC,
                    }))
                    stop_task = asyncio.create_task(auto_stop(ws, RECORD_SEC))

            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass

            # Acquisition relates to the eegsoruce which connected with the Cyton
            raw_eeg = source.get_window()

            if recorder.is_recording:
                new_eeg, new_ts = source.get_new_samples()
                if new_eeg.shape[1] > 0:
                    recorder.write_chunk(new_eeg, new_ts)

            occ_var = float(np.mean(np.var(raw_eeg[4:8], axis=1)))

            
            await ws.send(json.dumps({
                "type":           "status",
                "recording":      recorder.is_recording,
                "signal_quality": round(occ_var, 2),
                "stim_matrix":    STIM_MATRIX,
            }))

            await asyncio.sleep(0.5)

    except websockets.exceptions.ConnectionClosed:
        print("✗ Client disconnected.")
    finally:
        if stop_task and not stop_task.done():
            stop_task.cancel()
        if recorder.is_recording:
            recorder.stop()


async def main():
    print("=" * 60)
    print("  SSVEP BCI - Experiment 3: 4 Cross-shaped Cells")
    print("=" * 60)
    print("  Stimulis:")
    for stim in STIM_MATRIX:
        print(f"    • {stim['label']:20} → {stim['freq']} Hz")
    print(f"\n  Automatic complete recording lasts: {RECORD_SEC}s")
    print("  Cyton hardware connection.")
    print("  Open the index_exp3.html file at your browser (double clicking).")
    print("=" * 60)

    source = CytonEEG()

    print(f"  Waiting {WINDOW_SEC}s to fill the EEG buffer ...")
    await asyncio.sleep(WINDOW_SEC)
    print("  Ready! Press 'Start Test' at user web interface to begin.\n")

    try:
        async with websockets.serve(
            lambda ws: handler(ws, source),
            "localhost", 8765
        ):
            await asyncio.Future()
    finally:
        source.stop()
        print("Cyton disconnected correctly.")


if __name__ == "__main__":
    asyncio.run(main())
