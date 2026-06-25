# config.py — Fase de Testeo: Celda Única
# Configuración mínima para validar la respuesta SSVEP a un solo estímulo,
# sin clasificación (CCA) ni modo DEMO. Pensado para grabar señal cruda y
# analizarla después con el mismo flujo de Jupyter / Welch PSD del proyecto
# principal, sin la complejidad del sistema multi-frecuencia completo.

# --- Hardware ---
SERIAL_PORT = "COM5"     # Puerto de la placa Cyton. Device Manager → Ports → COMx

# --- Adquisición ---
FS         = 250          # Frecuencia de muestreo del Cyton (Hz)
N_CHANNELS = 8             # Fp1 Fp2 C3 C4 P7 P8 O1 O2

# --- Buffer inicial ---
# Mismo criterio que el proyecto principal: el buffer de BrainFlow tarda en
# llenarse, por lo que se espera WINDOW_SEC segundos antes de aceptar
# conexiones, evitando ventanas con zero-padding al arrancar.
WINDOW_SEC = 4
WINDOW     = FS * WINDOW_SEC

# --- Estímulo único ---
#STIM_LABEL = "1"
#STIM_FREQ  = 8.57         # Hz

STIM_LABEL = "2"
STIM_FREQ  = 10

#STIM_LABEL = "3"
#STIM_FREQ  = 12

#STIM_LABEL = "4"
#STIM_FREQ  = 15

# --- Grabación automática ---
RECORD_SEC = 40
#RECORD_SEC = 40            # Duración fija; el servidor para y guarda solo, sin
                            # necesidad de pulsar un botón de "detener".
