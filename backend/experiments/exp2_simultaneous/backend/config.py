# config.py — Experimento 2: Parpadeo simultáneo
# Las 4 celdas parpadean a la vez durante toda la grabación. El backend no
# controla el flicker (siempre están activas), pero sí lleva internamente
# el mismo temporizador de TRIAL_SEC por celda para etiquetar el marcador
# del fichero automáticamente — como apoyo/cruce con tu alarma del móvil,
# no como sustituto: sigues siendo tú quien decide a qué celda mirar.

# --- Hardware ---
SERIAL_PORT = "COM5"     # Puerto de la placa Cyton. Device Manager → Ports → COMx

# --- Adquisición ---
FS         = 250
N_CHANNELS = 8

# --- Buffer inicial ---
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

# --- Celdas y frecuencias del experimento ---
# Orden asumido para el marcador automático: 1 → 2 → 3 → 4
CELLS = {
    1: 8.57,
    2: 10.0,
    3: 12.0,
    4: 15.0,
}

# --- Duración de cada fase / celda ---
TRIAL_SEC = 40
TOTAL_SEC = TRIAL_SEC * len(CELLS)   # 160 s — grabación única y continua
