# server.py — Experimento 2: Parpadeo simultáneo
# Las 4 celdas parpadean siempre (el frontend no recibe ninguna orden de
# activar/desactivar flicker). El backend solo recorre las 4 fases para:
# (1) actualizar el marcador del EEGRecorder cada TRIAL_SEC segundos, y
# (2) avisar al frontend de qué celda "debería" tocar mirar según el reloj
# interno, como apoyo visual en pantalla junto a tu alarma del móvil — no
# como control del estímulo, que sigue siendo el mismo todo el rato.
# La grabación es única y continua durante las 4 fases (TOTAL_SEC en total).

import asyncio
import json
import numpy as np
import websockets

from config    import CELLS, TRIAL_SEC, TOTAL_SEC, WINDOW_SEC
from eegsource import CytonEEG
from recorder  import EEGRecorder

recorder = EEGRecorder()


async def run_phases(ws):
    """Recorre las 4 celdas en orden, marcando cada tramo en el grabador y
    avisando al frontend solo a efectos informativos (no controla flicker)."""
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
    print(f"✓ Cliente conectado: {ws.remote_address}")
    phase_task = None

    try:
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.01)
                msg = json.loads(raw)

                if msg.get("type") == "start_recording" and not recorder.is_recording:
                    # Vacía el backlog acumulado en BrainFlow durante el reposo,
                    # para que no se cuele en los primeros segundos de la grabación.
                    source.get_new_samples()

                    fname = recorder.start(msg.get("label", "exp2_simultaneo"))
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

            # Calidad de señal — P7, P8, O1, O2
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
        if phase_task and not phase_task.done():
            phase_task.cancel()
        if recorder.is_recording:
            recorder.stop()


async def main():
    print("=" * 50)
    print("  SSVEP BCI — Experimento 2: Parpadeo simultáneo")
    print(f"  Celdas: {CELLS}")
    print(f"  Duración por celda: {TRIAL_SEC}s | Total: {TOTAL_SEC}s")
    print("  Solo conexión con hardware Cyton (sin modo DEMO).")
    print("=" * 50)

    source = CytonEEG()

    print(f"  Esperando {WINDOW_SEC}s para llenar el buffer EEG...")
    await asyncio.sleep(WINDOW_SEC)
    print("  Listo! Pulsa 'Iniciar experimento' en la interfaz para comenzar.\n")

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
