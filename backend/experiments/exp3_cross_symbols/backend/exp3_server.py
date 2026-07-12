# exp3_server.py — Experimento 3: 4 Celdas en Cruz (Simultáneo)
# Backend que maneja 4 estímulos SSVEP de frecuencias simultáneas sin CCA/voting.
# Grabación automática de duración fija (RECORD_SEC) con cierre automático.
# Monitoriza la calidad de señal en canales occipitales (P7, P8, O1, O2).

import asyncio
import json
import time
import sys
import os
import numpy as np
import websockets

# Añadir el directorio backend al path para importar eegsource y recorder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from exp3_config import STIM_MATRIX, RECORD_SEC, WINDOW_SEC, WINDOW
from eegsource   import CytonEEG
from recorder    import EEGRecorder

recorder = EEGRecorder()


async def auto_stop(ws, duration: float):
    """Espera `duration` segundos y detiene/guarda la grabación sin intervención manual."""
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
    print(f"✓ Cliente conectado: {ws.remote_address}")
    stop_task = None

    try:
        while True:
            # Mensajes entrantes
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

            # Adquisición
            raw_eeg = source.get_window()

            if recorder.is_recording:
                new_eeg, new_ts = source.get_new_samples()
                if new_eeg.shape[1] > 0:
                    recorder.write_chunk(new_eeg, new_ts)

            # Calidad de señal — canales occipitales P7, P8, O1, O2 (índices 4:8)
            occ_var = float(np.mean(np.var(raw_eeg[4:8], axis=1)))

            # Estado del servidor (latido periódico)
            await ws.send(json.dumps({
                "type":           "status",
                "recording":      recorder.is_recording,
                "signal_quality": round(occ_var, 2),
                "stim_matrix":    STIM_MATRIX,  # Enviar configuración de estímulos al cliente
            }))

            await asyncio.sleep(0.5)

    except websockets.exceptions.ConnectionClosed:
        print("✗ Cliente desconectado.")
    finally:
        if stop_task and not stop_task.done():
            stop_task.cancel()
        if recorder.is_recording:
            recorder.stop()


async def main():
    print("=" * 60)
    print("  SSVEP BCI — Experimento 3: 4 Celdas en Cruz (Simultáneo)")
    print("=" * 60)
    print("  Estímulos:")
    for stim in STIM_MATRIX:
        print(f"    • {stim['label']:20} → {stim['freq']} Hz")
    print(f"\n  Grabación automática: {RECORD_SEC}s")
    print("  Solo conexión con hardware Cyton (sin CCA/voting).")
    print("  Abre el fichero index_exp3.html en el navegador (doble clic).")
    print("=" * 60)

    source = CytonEEG()

    print(f"  Esperando {WINDOW_SEC}s para llenar el buffer EEG...")
    await asyncio.sleep(WINDOW_SEC)
    print("  Listo! Pulsa 'Iniciar Experimento 3' en la interfaz para comenzar.\n")

    try:
        async with websockets.serve(
            lambda ws: handler(ws, source),
            "localhost", 8765
        ):
            await asyncio.Future()
    finally:
        source.stop()
        print("Cyton desconectada correctamente.")


if __name__ == "__main__":
    asyncio.run(main())
