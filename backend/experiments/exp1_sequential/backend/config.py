# config.py — Experimento 1: Parpadeo secuencial
# Las 4 celdas están visibles todo el rato, pero el backend activa el
# flicker de una sola cada vez, TRIAL_SEC segundos, en el orden de CELLS.
# Las demás permanecen apagadas (estáticas) mientras tanto.

# --- Hardware ---
SERIAL_PORT = "COM5"     # Puerto de la placa Cyton. Device Manager → Ports → COMx

# --- Adquisición ---
FS         = 250
N_CHANNELS = 8

# --- Buffer inicial ---
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

# --- Celdas y frecuencias del experimento ---
# Orden de presentación: 1 → 2 → 3 → 4
CELLS = {
    1: 8.57,
    2: 10.0,
    3: 12.0,
    4: 15.0,
}

# --- Duración de cada fase / celda ---
TRIAL_SEC = 40
TOTAL_SEC = TRIAL_SEC * len(CELLS)   # 160 s — grabación única y continua
