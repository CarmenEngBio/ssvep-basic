# server.py

import asyncio
import json
import time
import numpy as np
import websockets

from config    import LABEL, FREQ, RECORD_SEC, WINDOW_SEC, WINDOW
from eegsource import CytonEEG
from recorder  import EEGRecorder

recorder  = EEGRecorder()
#LOOP_STEP = int(0.5 * WINDOW) 


async def auto_stop(ws, duration: float):
    # Waits for determined seconds to stop automatically the recording without further interaction.
    await asyncio.sleep(duration)
    if recorder.is_recording:
        recorder.stop()
        try:
            await ws.send(json.dumps({"type": "recording_stopped", "reason": "auto"}))
        except websockets.exceptions.ConnectionClosed:
            pass


#   Handler WebSocket
async def handler(ws, source):

    print(f"✓ Cliente conectado: {ws.remote_address}")
    stop_task = None

    try:
        while True:
            # Incoming messages
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.01)
                msg = json.loads(raw)

                if msg.get("type") == "start_recording" and not recorder.is_recording:
                    fname = recorder.start(msg.get("label", "test_celda1"))
                    await ws.send(json.dumps({
                        "type":     "recording_started",
                        "file":     fname or "",
                        "duration": RECORD_SEC,
                    }))
                    stop_task = asyncio.create_task(auto_stop(ws, RECORD_SEC))

            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass

            #  Acquisition
            raw_eeg = source.get_window()

            if recorder.is_recording:
                new_eeg, new_ts = source.get_new_samples()
                if new_eeg.shape[1] > 0:
                    recorder.write_chunk(new_eeg, new_ts)

            # Signal quality (4 channels as requested by mentor)
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
        if stop_task and not stop_task.done():
            stop_task.cancel()
        if recorder.is_recording:
            recorder.stop()


#  Main
async def main():
    print("=" * 50)
    print("  SSVEP BCI - Initial Testing Phase (single cell)")
    print(f"  Stimulus: '{LABEL}' a {FREQ} Hz")
    print(f"  Automatic recording: {RECORD_SEC}s")
    print("  Connection with Cyton board.")
    print("  Open the index.html file on the navigator (double click).")
    print("=" * 50)

    source = CytonEEG()

    print(f"  Waiting {WINDOW_SEC}s to fill the EEG buffer ...")
    await asyncio.sleep(WINDOW_SEC)
    print("  Ready! Press 'Begin test' on the interface to start.\n")

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
