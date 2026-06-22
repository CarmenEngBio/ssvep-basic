# server.py — Fase de Testeo: Celda Única
# Versión reducida del servidor principal: aquí NO hay clasificación (CCA),
# NI voting, NI cooldown, NI modo DEMO. Solo gestiona la conexión con la
# placa Cyton y el ciclo de vida de una única grabación de RECORD_SEC
# segundos, que arranca cuando el frontend lo pide y se detiene/guarda sola.

import asyncio
import json
import time
import numpy as np
import websockets

from config    import STIM_LABEL, STIM_FREQ, RECORD_SEC, WINDOW_SEC, WINDOW
from eegsource import CytonEEG
from recorder  import EEGRecorder

recorder  = EEGRecorder()
# LOOP_STEP = int(0.5 * WINDOW) 


async def auto_stop(ws, duration: float):
    """Espera `duration` segundos y detiene/guarda la grabación sin intervención manual."""
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
            #   Mensajes entrantes
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

            #   Adquisición
            raw_eeg = source.get_window()

            if recorder.is_recording:
                new_eeg, new_ts = source.get_new_samples()
                if new_eeg.shape[1] > 0:
                    recorder.write_chunk(new_eeg, new_ts)

            #   Calidad de señal — P7, P8, O1, O2 (mismos 4 canales del protocolo del tutor)
            occ_var = float(np.mean(np.var(raw_eeg[4:8], axis=1)))

            await ws.send(json.dumps({
                "type":           "status",
                "recording":      recorder.is_recording,
                "signal_quality": round(occ_var, 2),
            }))

            await asyncio.sleep(0.5)

    except websockets.exceptions.ConnectionClosed:
        print("✗ Cliente desconectado.")
    finally:
        if stop_task and not stop_task.done():
            stop_task.cancel()
        if recorder.is_recording:
            recorder.stop()


#   Main
async def main():
    print("=" * 50)
    print("  SSVEP BCI — Fase de Testeo (celda única)")
    print(f"  Estímulo: '{STIM_LABEL}' a {STIM_FREQ} Hz")
    print(f"  Grabación automática: {RECORD_SEC}s")
    print("  Solo conexión con hardware Cyton (sin modo DEMO).")
    print("  Abre el fichero index.html en el navegador (doble clic).")
    print("=" * 50)

    source = CytonEEG()

    print(f"  Esperando {WINDOW_SEC}s para llenar el buffer EEG...")
    await asyncio.sleep(WINDOW_SEC)
    print("  Listo! Pulsa 'Iniciar prueba' en la interfaz para comenzar.\n")

    try:
        async with websockets.serve(
            lambda ws: handler(ws, source),
            "localhost", 8765
        ):
            await asyncio.Future()
    finally:
        source.stop()
        print("Cyton desconectada correctamente.")


asyncio.run(main())
