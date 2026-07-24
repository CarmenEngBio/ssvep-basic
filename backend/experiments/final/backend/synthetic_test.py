# real_test_arquitectures.py

import sys
import numpy as np
import pandas as pd
from scipy.signal import butter, iirnotch, sosfiltfilt, tf2sos
from sklearn.cross_decomposition import CCA
from pathlib import Path

FS = 250
CHUNK_SIZE = int(FS * 4)

def load_recording(filepath):
    """Carga archivo .txt."""
    df = pd.read_csv(filepath, skiprows=4)
    df.columns = df.columns.str.strip()
    eeg_cols = [f'EXG Channel {i}' for i in range(8)]
    eeg = df[eeg_cols].values.T / 1e6
    return eeg[4:8]

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

def arquitectura_chunks(eeg, use_car=True):
    chunks = []
    for i in range(0, eeg.shape[1], CHUNK_SIZE):
        chunk = eeg[:, i:i+CHUNK_SIZE]
        if chunk.shape[1] > 0:
            chunks.append(chunk)
    eeg_concatenado = np.hstack(chunks)
    return preprocess(eeg_concatenado, use_car=use_car)

def arquitectura_offline(eeg, use_car=True):
    return preprocess(eeg, use_car=use_car)

def arquitectura_streaming(eeg, use_car=True):
    chunks_procesados = []
    for i in range(0, eeg.shape[1], CHUNK_SIZE):
        chunk = eeg[:, i:i+CHUNK_SIZE]
        if chunk.shape[1] >= FS * 2:
            chunk_proc = preprocess(chunk, use_car=use_car)
            chunks_procesados.append(chunk_proc)
    return np.hstack(chunks_procesados)

# ==========================================
# MAIN - ACEPTA ARGUMENTO
# ==========================================

# Usar argumento o default
if len(sys.argv) > 1:
    recording_file = Path(sys.argv[1])  # ← RUTA RELATIVA
else:
    recording_file = Path("recordings/bci_exp2_online_20260722_173915.txt")  # default

print("="*90)
print(f"TEST CON DATOS REALES: {recording_file.name}")
print("="*90)

if not recording_file.exists():
    print(f"❌ Archivo no encontrado: {recording_file}")
    print(f"   Ruta absoluta: {recording_file.absolute()}")
    exit(1)

print(f"\n1. Cargando {recording_file.name}...")
eeg = load_recording(str(recording_file))
print(f"   Shape: {eeg.shape}")

# Usar bloque 1 (primeros 60s)
eeg_bloque = eeg[:, :FS*60]

freqs_target = [8.57, 10.0, 12.0, 15.0]
resultados = {}

print("\n2. PRUEBA 1: Chunks acumulados (TU CÓDIGO ACTUAL)")
print("-" * 90)
for use_car in [True, False]:
    label = "CON CAR" if use_car else "SIN CAR"
    eeg_proc = arquitectura_chunks(eeg_bloque, use_car=use_car)
    corr = classify_cca(eeg_proc, freqs_target)
    resultados[f"chunks_{use_car}"] = corr
    print(f"   {label:12} → Promedio: {np.mean(list(corr.values())):.4f}")
    for freq, c in corr.items():
        print(f"      {freq:5.2f} Hz: {c:.4f}")

print("\n3. PRUEBA 2: Todo de una vez (OFFLINE)")
print("-" * 90)
for use_car in [True, False]:
    label = "CON CAR" if use_car else "SIN CAR"
    eeg_proc = arquitectura_offline(eeg_bloque, use_car=use_car)
    corr = classify_cca(eeg_proc, freqs_target)
    resultados[f"offline_{use_car}"] = corr
    print(f"   {label:12} → Promedio: {np.mean(list(corr.values())):.4f}")
    for freq, c in corr.items():
        print(f"      {freq:5.2f} Hz: {c:.4f}")

print("\n4. PRUEBA 3: Streaming (procesar cada chunk)")
print("-" * 90)
for use_car in [True, False]:
    label = "CON CAR" if use_car else "SIN CAR"
    eeg_proc = arquitectura_streaming(eeg_bloque, use_car=use_car)
    corr = classify_cca(eeg_proc, freqs_target)
    resultados[f"streaming_{use_car}"] = corr
    print(f"   {label:12} → Promedio: {np.mean(list(corr.values())):.4f}")
    for freq, c in corr.items():
        print(f"      {freq:5.2f} Hz: {c:.4f}")

# ANÁLISIS
print("\n5. COMPARACIÓN CON DATOS REALES")
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
if chunks_car == offline_car:
    print("✅ CHUNKS y OFFLINE son IDÉNTICOS")
    print("   El problema NO es chunks desfasados")
elif abs(chunks_car - offline_car) > 0.02:
    print("⚠️ CHUNKS y OFFLINE DIFIEREN")
    print("   Chunks SÍ degradan respecto a offline")
else:
    print("~ CHUNKS y OFFLINE son MUY SIMILARES")

print("="*90)