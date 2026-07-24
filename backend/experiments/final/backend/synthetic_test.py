# synthetic_test.py — Test CON CAR vs SIN CAR en datos simulados

import numpy as np
from scipy.signal import butter, iirnotch, sosfiltfilt, tf2sos
from sklearn.cross_decomposition import CCA

FS = 250
DURATION = 60
CHUNK_SIZE = int(FS * 4)  # 4 segundos (como en online)

# ==========================================
# GENERAR DATOS SINTÉTICOS
# ==========================================

def generate_ssvep_signal(freq, duration=60):
    """Genera SSVEP + ruido 50Hz."""
    t = np.arange(int(FS * duration)) / FS
    ssvep = 2.0 * np.sin(2 * np.pi * freq * t) + \
            1.5 * np.sin(2 * np.pi * freq * 2 * t)
    noise_50hz = 100.0 * np.sin(2 * np.pi * 50 * t)
    noise_gaussian = np.random.normal(0, 5, len(t))
    return ssvep + noise_50hz + noise_gaussian

def generate_synthetic_eeg(frequencies=[8.57, 10.0, 12.0, 15.0]):
    """Genera 4 canales."""
    signals = []
    for freq in frequencies:
        sig = generate_ssvep_signal(freq, duration=DURATION)
        signals.append(sig)
    return np.array(signals)

# ==========================================
# PREPROCESAR
# ==========================================

def preprocess(eeg, use_car=True):
    """Procesa con/sin CAR."""
    nyq = FS / 2
    sos_bp = butter(4, [max(5.0/nyq, 1e-4), min(25.0/nyq, 0.999)],
                    btype='bandpass', output='sos')
    b, a = iirnotch(50, Q=40, fs=FS)
    sos_notch = tf2sos(b, a)
    
    eeg_bp = sosfiltfilt(sos_bp, eeg, axis=1)
    eeg_notch = sosfiltfilt(sos_notch, eeg_bp, axis=1)
    
    if use_car:
        return eeg_notch - np.mean(eeg_notch, axis=0, keepdims=True)
    return eeg_notch

# ==========================================
# CLASIFICAR CCA
# ==========================================

def classify_cca(eeg, target_freqs):
    """Calcula correlaciones."""
    results = {}
    for freq in target_freqs:
        t = np.arange(eeg.shape[1]) / FS
        ref = np.column_stack([
            np.sin(2*np.pi*freq*t),
            np.cos(2*np.pi*freq*t),
            np.sin(2*np.pi*freq*2*t),
            np.cos(2*np.pi*freq*2*t),
        ])
        cca = CCA(n_components=1)
        cca.fit(eeg.T, ref)
        U, V = cca.transform(eeg.T, ref)
        corr = np.corrcoef(U[:, 0], V[:, 0])[0, 1]
        results[freq] = corr
    return results

# ==========================================
# ARQUITECTURA 1: CHUNKS ACUMULADOS (como tu código)
# ==========================================

def arquitectura_chunks(eeg, use_car=True):
    """Acumula chunks, procesa al final."""
    chunks = []
    
    # Simular llegada en chunks de 4s
    for i in range(0, eeg.shape[1], CHUNK_SIZE):
        chunk = eeg[:, i:i+CHUNK_SIZE]
        if chunk.shape[1] > 0:
            chunks.append(chunk)
    
    # Junta TODO al final (como tu código)
    eeg_concatenado = np.hstack(chunks)
    
    # Procesa TODO junto
    eeg_processed = preprocess(eeg_concatenado, use_car=use_car)
    
    return eeg_processed

# ==========================================
# ARQUITECTURA 2: TODO DE UNA VEZ (como offline)
# ==========================================

def arquitectura_offline(eeg, use_car=True):
    """Procesa TODO de una vez."""
    return preprocess(eeg, use_car=use_car)

# ==========================================
# ARQUITECTURA 3: PROCESAMIENTO POR CHUNKS (streaming)
# ==========================================

def arquitectura_streaming(eeg, use_car=True):
    """Procesa CADA chunk independientemente."""
    chunks_procesados = []
    
    for i in range(0, eeg.shape[1], CHUNK_SIZE):
        chunk = eeg[:, i:i+CHUNK_SIZE]
        if chunk.shape[1] >= FS * 2:  # Mínimo 2s
            chunk_proc = preprocess(chunk, use_car=use_car)
            chunks_procesados.append(chunk_proc)
    
    # Junta chunks ya procesados
    return np.hstack(chunks_procesados)

# ==========================================
# TEST PRINCIPAL
# ==========================================

print("="*90)
print("TEST ARQUITECTURAS: ¿Chunks desfasados afectan?")
print("="*90)

freqs_target = [8.57, 10.0, 12.0, 15.0]

# Generar datos
print("\n1. Generando datos sintéticos...")
eeg = generate_synthetic_eeg(freqs_target)
print(f"   Shape: {eeg.shape}")

# TEST: 3 ARQUITECTURAS × 2 OPCIONES (CON/SIN CAR)
resultados = {}

print("\n2. PRUEBA 1: Chunks acumulados (ACTUAL - como tu código)")
print("-" * 90)
for use_car in [True, False]:
    label = "CON CAR" if use_car else "SIN CAR"
    eeg_proc = arquitectura_chunks(eeg, use_car=use_car)
    corr = classify_cca(eeg_proc, freqs_target)
    resultados[f"chunks_{use_car}"] = corr
    print(f"   {label:12} → Promedio: {np.mean(list(corr.values())):.4f}")
    for freq, c in corr.items():
        print(f"      {freq:5.2f} Hz: {c:.4f}")

print("\n3. PRUEBA 2: Todo de una vez (OFFLINE)")
print("-" * 90)
for use_car in [True, False]:
    label = "CON CAR" if use_car else "SIN CAR"
    eeg_proc = arquitectura_offline(eeg, use_car=use_car)
    corr = classify_cca(eeg_proc, freqs_target)
    resultados[f"offline_{use_car}"] = corr
    print(f"   {label:12} → Promedio: {np.mean(list(corr.values())):.4f}")
    for freq, c in corr.items():
        print(f"      {freq:5.2f} Hz: {c:.4f}")

print("\n4. PRUEBA 3: Streaming (procesar cada chunk)")
print("-" * 90)
for use_car in [True, False]:
    label = "CON CAR" if use_car else "SIN CAR"
    eeg_proc = arquitectura_streaming(eeg, use_car=use_car)
    corr = classify_cca(eeg_proc, freqs_target)
    resultados[f"streaming_{use_car}"] = corr
    print(f"   {label:12} → Promedio: {np.mean(list(corr.values())):.4f}")
    for freq, c in corr.items():
        print(f"      {freq:5.2f} Hz: {c:.4f}")

# ==========================================
# ANÁLISIS COMPARATIVO
# ==========================================

print("\n5. COMPARACIÓN: ¿Chunks afectan a CAR?")
print("="*90)

chunks_car = np.mean(list(resultados["chunks_True"].values()))
chunks_no_car = np.mean(list(resultados["chunks_False"].values()))

offline_car = np.mean(list(resultados["offline_True"].values()))
offline_no_car = np.mean(list(resultados["offline_False"].values()))

streaming_car = np.mean(list(resultados["streaming_True"].values()))
streaming_no_car = np.mean(list(resultados["streaming_False"].values()))

print(f"\n{'Arquitectura':<20} {'CON CAR':<15} {'SIN CAR':<15} {'Mejora SIN CAR':<15}")
print("-"*90)
print(f"{'Chunks (actual)':<20} {chunks_car:<15.4f} {chunks_no_car:<15.4f} {((chunks_no_car-chunks_car)/chunks_car*100):<14.1f}%")
print(f"{'Offline':<20} {offline_car:<15.4f} {offline_no_car:<15.4f} {((offline_no_car-offline_car)/offline_car*100):<14.1f}%")
print(f"{'Streaming':<20} {streaming_car:<15.4f} {streaming_no_car:<15.4f} {((streaming_no_car-streaming_car)/streaming_car*100):<14.1f}%")

print("\n" + "="*90)
print("CONCLUSIONES:")
print("="*90)

if abs((chunks_no_car-chunks_car)/chunks_car*100) > abs((offline_no_car-offline_car)/offline_car*100):
    print("✅ CHUNKS EMPEORAN el efecto de CAR")
    print(f"   Chunks: SIN CAR +{((chunks_no_car-chunks_car)/chunks_car*100):.1f}%")
    print(f"   Offline: SIN CAR +{((offline_no_car-offline_car)/offline_car*100):.1f}%")
else:
    print("⚠️ CAR tiene mismo efecto con/sin chunks")
    print("   El problema NO es solo chunks desfasados")

print("="*90)