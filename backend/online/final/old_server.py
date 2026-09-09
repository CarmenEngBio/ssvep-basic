# BCI old_server.py - Uses experiment 2 but with ONLINE performance
# Classification occurs each 40s
# At the end of the recording it is shown the classification result of how many cells were sequentially detected
 
import asyncio
import json
import time
import numpy as np
import websockets
 
from config import CELLS, TRIAL_SEC, WINDOW_SEC, WINDOW, FS
from eegsource import CytonEEG
from recorder import EEGRecorder
from processing import EEGProcessor
 
recorder = EEGRecorder()
processor = EEGProcessor()
 
TOTAL_SEC = TRIAL_SEC * len(CELLS)
 
 
class BCIBlock:
    # Each block represents 40s gazing at one cell.
    
    def __init__(self):
        self.trial_data = []
        self.trial_timestamps = []
        self.start_time = None
    
    def reset(self):
        self.trial_data = []
        self.trial_timestamps = []
        self.start_time = None
    
    def add_samples(self, eeg_chunk, timestamps):
        # Accumulates samples or appends them
        self.trial_data.append(eeg_chunk)
        self.trial_timestamps.extend(timestamps)
    
    def has_enough_data(self) -> bool:
        #Verifies if there are enough samples at least 2s
        return len(self.trial_timestamps) > FS * 2
    
    def classify(self, target_freq) -> dict:
        # Classification of target freq against frequencies
        if not self.has_enough_data():
            return {"freq": None, "corr": 0.0, "correct": False}
        
        X = np.hstack(self.trial_data)
        
        X_processed = processor.preprocess(X)
        
        frequencies = [CELLS[i]["freq"] for i in sorted(CELLS.keys())]
        best_freq, best_corr, all_corrs = processor.classify(X_processed, frequencies)
        
        is_correct = abs(best_freq - target_freq) < 0.5 # 0.5 Hz margin
        
        return {
            "freq": best_freq,
            "corr": round(best_corr, 4),
            "correct": is_correct,
            "all_corrs": {f: round(c, 4) for f, c in all_corrs.items()}
        }
 
 
bci_block = BCIBlock()
 
 
async def run_blocks(ws, source):
    # Iterates 4 blocks of 40s and classifies each one
    results = []
    
    for cell_id in sorted(CELLS.keys()):
        cell_info = CELLS[cell_id]
        freq = cell_info["freq"]
        emoji = cell_info["emoji"]
        label = cell_info["label"]
        
        print(f"\n[Block {cell_id}] User must gaze at: {emoji} {label} ({freq} Hz) during 60s...")
        
        # messages to frontend
        await ws.send(json.dumps({
            "type": "block_started",
            "cell_id": cell_id,
            "emoji": emoji,
            "label": label,
            "freq": freq,
            "duration": TRIAL_SEC,
        }))
        
        # For .txt file
        recorder.set_marker(cell_id)
        
        # 40 s are gathered
        bci_block.reset()
        bci_block.start_time = time.time()
        elapsed = 0.0
        
        while elapsed < TRIAL_SEC:
            # raw_eeg = source.get_window()
            new_eeg, new_ts = source.get_new_samples()
            
            if new_eeg.shape[1] > 0 and recorder.is_recording:
                recorder.write_chunk(new_eeg, new_ts)
                bci_block.add_samples(new_eeg, new_ts)
            
            elapsed = time.time() - bci_block.start_time
            await asyncio.sleep(0.1)
        
        # One block is classified
        result = bci_block.classify(freq)
        results.append({
            "cell_id": cell_id,
            "label": label,
            "target_freq": freq,
            "detected_freq": result["freq"],
            "correlation": result["corr"],
            "correct": result["correct"],
            "all_corrs": result["all_corrs"],
        })
        
        # Results are sent to the frontend and displaced through the server console 
        if result["correct"]:
            status = "✅ CORRECT"
            color = "green"
        else:
            status = f"❌ INCORRECT (detected {result['freq']:.2f}Hz)"
            color = "red"
        
        print(f"[Result] {emoji} {label}: Corr={result['corr']:.4f} — {status}")
        
        await ws.send(json.dumps({
            "type": "block_result",
            "cell_id": cell_id,
            "emoji": emoji,
            "label": label,
            "correlation": result["corr"],
            "correct": result["correct"],
            "detected_freq": result["freq"],
            "all_corrs": result["all_corrs"],
            "status": status,
        }))
        
        await asyncio.sleep(0.5)  # Blocks pause
    
    # End of recording
    recorder.stop()
    
    # Final summary
    correct_count = sum(1 for r in results if r["correct"])
    accuracy = (correct_count / len(results)) * 100 if results else 0
    
    print(f"\n[SUMMARY] Accuracy: {correct_count}/{len(results)} ({accuracy:.1f}%)")
    
    await ws.send(json.dumps({
        "type": "session_ended",
        "accuracy": round(accuracy, 1),
        "correct": correct_count,
        "total": len(results),
        "results": results,
    }))
 
 
async def handler(ws, source):
    print(f"✓ Client connected: {ws.remote_address}")
    block_task = None
 
    try:
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.01)
                msg = json.loads(raw)
 
                if msg.get("type") == "start_session" and not recorder.is_recording:
                    # Releases BrainFlow buffer
                    source.get_new_samples()
 
                    # Begins recording session
                    fname = recorder.start("bci_exp2_online")
                    await ws.send(json.dumps({
                        "type": "session_started",
                        "file": fname or "",
                        "duration": TOTAL_SEC,
                    }))
                    
                    # Executing for 4 blocks which are the 4 cells
                    block_task = asyncio.create_task(run_blocks(ws, source))
 
            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass
 
            await ws.send(json.dumps({
                "type": "status",
                "recording": recorder.is_recording,
            }))
 
            await asyncio.sleep(0.5)
 
    except websockets.exceptions.ConnectionClosed:
        print("✗ Client disconnected")
    finally:
        if block_task and not block_task.done():
            block_task.cancel()
        if recorder.is_recording:
            recorder.stop()
 
 
async def main():
    print("=" * 70)
    print("  SSVEP Online Assistive BCI ")
    print("=" * 70)
    print("  Structure: 4 blocks of 40s for each cell ")
    print("  Classification: at the end of each registered data cell")
    print("  Frequencies:")
    for cid, info in sorted(CELLS.items()):
        print(f"    {cid}. {info['emoji']} {info['label']:20} → {info['freq']} Hz")
    print(f"\n  Total duration: {TOTAL_SEC}s")
    print("  Connected to Cyton hardware ")
    print("=" * 70)
 
    source = CytonEEG()
 
    print(f"  Waiting {WINDOW_SEC}s to fill the EEG buffer ...")
    await asyncio.sleep(WINDOW_SEC)
    print("  Ready! Open the browser and click to 'Start Session' .\n")
 
    try:
        async with websockets.serve(
            lambda ws: handler(ws, source),
            "localhost", 8765
        ):
            await asyncio.Future()
    finally:
        source.stop()
        print("Cyton disconnected.")
 
 
if __name__ == "__main__":
    asyncio.run(main())