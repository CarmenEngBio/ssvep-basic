# server.py — Estructura Exp2 + Clasificación Online
# Basado en exp2_simultaneous pero CON clasificación de cada bloque de 40s
# 4 bloques secuenciales: Usuario mira cada celda 40s
# Al final de cada bloque: Clasificación + Resultado
 
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
 
# Calcular TOTAL_SEC
TOTAL_SEC = TRIAL_SEC * len(CELLS)
 
 
class BCIBlock:
    """Sesión de un bloque (40 segundos mirando UNA celda)."""
    
    def __init__(self):
        self.trial_data = []
        self.trial_timestamps = []
        self.start_time = None
    
    def reset(self):
        self.trial_data = []
        self.trial_timestamps = []
        self.start_time = None
    
    def add_samples(self, eeg_chunk, timestamps):
        """Acumula muestras."""
        self.trial_data.append(eeg_chunk)
        self.trial_timestamps.extend(timestamps)
    
    def has_enough_data(self) -> bool:
        """Verifica si hay suficientes muestras (al menos 2s)."""
        return len(self.trial_timestamps) > FS * 2
    
    def classify(self, target_freq) -> dict:
        """Clasifica bloque contra frecuencia objetivo."""
        if not self.has_enough_data():
            return {"freq": None, "corr": 0.0, "correct": False}
        
        # Concatenar datos
        X = np.hstack(self.trial_data)
        
        # Preprocesar
        X_processed = processor.preprocess(X)
        
        # Clasificar contra TODAS las frecuencias
        frequencies = [CELLS[i]["freq"] for i in sorted(CELLS.keys())]
        best_freq, best_corr, all_corrs = processor.classify(X_processed, frequencies)
        
        # ¿Es correcta?
        is_correct = abs(best_freq - target_freq) < 0.5
        
        return {
            "freq": best_freq,
            "corr": round(best_corr, 4),
            "correct": is_correct,
            "all_corrs": {f: round(c, 4) for f, c in all_corrs.items()}
        }
 
 
bci_block = BCIBlock()
 
 
async def run_blocks(ws, source):
    """Recorre 4 bloques de 40s, clasifica cada uno."""
    results = []
    
    for cell_id in sorted(CELLS.keys()):
        cell_info = CELLS[cell_id]
        freq = cell_info["freq"]
        emoji = cell_info["emoji"]
        label = cell_info["label"]
        
        print(f"\n[Bloque {cell_id}] Usuario debe mirar: {emoji} {label} ({freq} Hz) durante 40s...")
        
        # Avisar al frontend
        await ws.send(json.dumps({
            "type": "block_started",
            "cell_id": cell_id,
            "emoji": emoji,
            "label": label,
            "freq": freq,
            "duration": TRIAL_SEC,
        }))
        
        # Marcar en grabador
        recorder.set_marker(cell_id)
        
        # Acumular 40 segundos
        bci_block.reset()
        bci_block.start_time = time.time()
        elapsed = 0.0
        
        while elapsed < TRIAL_SEC:
            raw_eeg = source.get_window()
            new_eeg, new_ts = source.get_new_samples()
            
            if new_eeg.shape[1] > 0 and recorder.is_recording:
                recorder.write_chunk(new_eeg, new_ts)
                bci_block.add_samples(new_eeg, new_ts)
            
            elapsed = time.time() - bci_block.start_time
            await asyncio.sleep(0.1)
        
        # CLASIFICAR ESTE BLOQUE
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
        
        # Avisar resultado al frontend
        if result["correct"]:
            status = "✅ CORRECTO"
            color = "green"
        else:
            status = f"❌ INCORRECTO (detectó {result['freq']:.2f}Hz)"
            color = "red"
        
        print(f"[Resultado] {emoji} {label}: Corr={result['corr']:.4f} — {status}")
        
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
        
        await asyncio.sleep(0.5)  # Pausa entre bloques
    
    # Finalizar grabación
    recorder.stop()
    
    # Resumen final
    correct_count = sum(1 for r in results if r["correct"])
    accuracy = (correct_count / len(results)) * 100 if results else 0
    
    print(f"\n[RESUMEN] Precisión: {correct_count}/{len(results)} ({accuracy:.1f}%)")
    
    await ws.send(json.dumps({
        "type": "session_ended",
        "accuracy": round(accuracy, 1),
        "correct": correct_count,
        "total": len(results),
        "results": results,
    }))
 
 
async def handler(ws, source):
    print(f"✓ Cliente conectado: {ws.remote_address}")
    block_task = None
 
    try:
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.01)
                msg = json.loads(raw)
 
                if msg.get("type") == "start_session" and not recorder.is_recording:
                    # Vacía backlog de BrainFlow
                    source.get_new_samples()
 
                    # Iniciar grabación
                    fname = recorder.start("bci_exp2_online")
                    await ws.send(json.dumps({
                        "type": "session_started",
                        "file": fname or "",
                        "duration": TOTAL_SEC,
                    }))
                    
                    # Ejecutar 4 bloques
                    block_task = asyncio.create_task(run_blocks(ws, source))
 
            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass
 
            # Calidad de señal (monitoreo continuo)
            raw_eeg = source.get_window()
            if raw_eeg is not None:
                occ_var = float(np.mean(np.var(raw_eeg[4:8], axis=1)))
            else:
                occ_var = 0.0
 
            await ws.send(json.dumps({
                "type": "status",
                "recording": recorder.is_recording,
                "signal_quality": round(occ_var, 2),
            }))
 
            await asyncio.sleep(0.5)
 
    except websockets.exceptions.ConnectionClosed:
        print("✗ Cliente desconectado")
    finally:
        if block_task and not block_task.done():
            block_task.cancel()
        if recorder.is_recording:
            recorder.stop()
 
 
async def main():
    print("=" * 70)
    print("  SSVEP Online Assistive BCI ")
    print("=" * 70)
    print("  Structure: 4 blocks of 60s for each cell )")
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