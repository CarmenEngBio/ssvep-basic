# server.py - Experiment 1: Sequential Flickering
# One cell gathers the flieckering engine active each 40s while the rest are turned off


import asyncio
import json
import numpy as np
import websockets

from config    import CELLS, TRIAL_SEC, TOTAL_SEC, WINDOW_SEC
from eegsource import CytonEEG
from recorder  import EEGRecorder

recorder = EEGRecorder()


async def run_phases(ws):
    
    # Iterates consecutively the 4 displaced cells, sending the frontend to activate one cell and disable the others
    
    for cell_id, freq in CELLS.items():
        recorder.set_marker(cell_id)
        await ws.send(json.dumps({
            "type":     "phase",
            "cell":     cell_id,
            "freq":     freq,
            "duration": TRIAL_SEC,
        }))
        await asyncio.sleep(TRIAL_SEC)

    recorder.stop()
    try:
        await ws.send(json.dumps({"type": "recording_stopped", "reason": "auto"}))
    except websockets.exceptions.ConnectionClosed:
        pass


async def handler(ws, source):
    print(f"✓ Client connected: {ws.remote_address}")
    phase_task = None

    try:
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.01)
                msg = json.loads(raw)

                if msg.get("type") == "start_recording" and not recorder.is_recording:
                    # BrainFlow buffer is cleaned here in order to fill the buffer for the recording
                    source.get_new_samples()

                    fname = recorder.start(msg.get("label", "exp1_secuencial"))
                    await ws.send(json.dumps({
                        "type":     "recording_started",
                        "file":     fname or "",
                        "duration": TOTAL_SEC,
                    }))
                    phase_task = asyncio.create_task(run_phases(ws))

            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass

            raw_eeg = source.get_window()

            if recorder.is_recording:
                new_eeg, new_ts = source.get_new_samples()
                if new_eeg.shape[1] > 0:
                    recorder.write_chunk(new_eeg, new_ts)

            # Performance of signal quality indicators
            occ_var = float(np.mean(np.var(raw_eeg[4:8], axis=1)))

            await ws.send(json.dumps({
                "type":           "status",
                "recording":      recorder.is_recording,
                "signal_quality": round(occ_var, 2),
            }))

            await asyncio.sleep(0.5)

    except websockets.exceptions.ConnectionClosed:
        print("✗ Client disconnected.")
    finally:
        if phase_task and not phase_task.done():
            phase_task.cancel()
        if recorder.is_recording:
            recorder.stop()


async def main():
    print("=" * 50)
    print("  SSVEP BCI - Experiment 1: Sequential Flickering ")
    print(f"  Cells: {CELLS}")
    print(f"  Timing stipulated for each cell: {TRIAL_SEC}s and total: {TOTAL_SEC}s")
    print("  Connection with OpenBCI Cyton hardware.")
    print("=" * 50)

    source = CytonEEG()

    print(f"  Waiting {WINDOW_SEC}s to fill the EEG buffer ...")
    await asyncio.sleep(WINDOW_SEC)
    print("  Ready! Press 'Initialise experiment' at the web interface to begin.\n")

    try:
        async with websockets.serve(
            lambda ws: handler(ws, source),
            "localhost", 8765
        ):
            await asyncio.Future()
    finally:
        source.stop()
        print("Cyton disconnected correctly.")


asyncio.run(main())
