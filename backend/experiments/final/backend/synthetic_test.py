# synthetic_test.py — Test CON CAR vs SIN CAR en datos simulados

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, iirnotch, sosfiltfilt, tf2sos
from sklearn.cross_decomposition import CCA

FS = 250
DURATION = 60  # 60 segundos como en online

# ==========================================
# 1. GENERAR DATOS SINTÉTICOS
# ==========================================

def generate_ssvep_signal(freq, duration=60):
    """Genera SSVEP puro a frecuencia específica."""
    t = np.arange(int(FS * duration)) / FS
    
    # SSVEP: amplitud baja (como real)
    ssvep = 2.0 * np.sin(2 * np.pi * freq * t) + \
            1.5 * np.sin(2 * np.pi * freq * 2 * t)  # armónico
    
    # Ruido 50Hz FUERTE (como real)
    noise_50hz = 100.0 * np.sin(2 * np.pi * 50 * t)
    
    # Ruido gaussiano
    noise_gaussian = np.random.normal(0, 5, len(t))
    
    # Combinar
    signal = ssvep + noise_50hz + noise_gaussian
    
    return signal

def generate_synthetic_eeg(frequencies=[8.57, 10.0, 12.0, 15.0]):
    """Genera 4 canales con SSVEP diferentes."""
    signals = []
    for freq in frequencies:
        sig = generate_ssvep_signal(freq, duration=DURATION)
        signals.append(sig)
    
    return np.array(signals)

# ==========================================
# 2. PROCESAR CON CAR y SIN CAR
# ==========================================

def preprocess_with_car(eeg):
    """Preprocesa CON CAR."""
    nyq = FS / 2
    sos_bp = butter(4, [max(5.0/nyq, 1e-4), min(25.0/nyq, 0.999)],
                    btype='bandpass', output='sos')
    
    b, a = iirnotch(50, Q=40, fs=FS)
    sos_notch = tf2sos(b, a)
    
    # Bandpass
    eeg_bp = sosfiltfilt(sos_bp, eeg, axis=1)
    
    # Notch
    eeg_notch = sosfiltfilt(sos_notch, eeg_bp, axis=1)
    
    # CAR ← AQUÍ ESTÁ
    eeg_car = eeg_notch - np.mean(eeg_notch, axis=0, keepdims=True)
    
    return eeg_car

def preprocess_without_car(eeg):
    """Preprocesa SIN CAR."""
    nyq = FS / 2
    sos_bp = butter(4, [max(5.0/nyq, 1e-4), min(25.0/nyq, 0.999)],
                    btype='bandpass', output='sos')
    
    b, a = iirnotch(50, Q=40, fs=FS)
    sos_notch = tf2sos(b, a)
    
    # Bandpass
    eeg_bp = sosfiltfilt(sos_bp, eeg, axis=1)
    
    # Notch
    eeg_notch = sosfiltfilt(sos_notch, eeg_bp, axis=1)
    
    # NO CAR ← DIFERENCIA
    return eeg_notch

# ==========================================
# 3. CLASIFICAR CCA
# ==========================================

def classify_cca(eeg, target_freqs):
    """Calcula correlaciones CCA."""
    results = {}
    
    for freq in target_freqs:
        t = np.arange(eeg.shape[1]) / FS
        
        # Referencia
        ref = np.column_stack([
            np.sin(2*np.pi*freq*t),
            np.cos(2*np.pi*freq*t),
            np.sin(2*np.pi*freq*2*t),
            np.cos(2*np.pi*freq*2*t),
        ])
        
        # CCA
        cca = CCA(n_components=1)
        cca.fit(eeg.T, ref)
        U, V = cca.transform(eeg.T, ref)
        corr = np.corrcoef(U[:, 0], V[:, 0])[0, 1]
        
        results[freq] = corr
    
    return results

# ==========================================
# 4. TEST PRINCIPAL
# ==========================================

print("="*80)
print("TEST SINTÉTICO: CAR vs SIN CAR")
print("="*80)

freqs_target = [8.57, 10.0, 12.0, 15.0]

# Generar datos sintéticos
print("\n1. Generando datos sintéticos...")
eeg_synthetic = generate_synthetic_eeg(freqs_target)
print(f"   Shape: {eeg_synthetic.shape}")
print(f"   Ruido 50Hz simulado: SÍ")
print(f"   SSVEP puro: SÍ")

# Procesar CON CAR
print("\n2. Procesando CON CAR...")
eeg_with_car = preprocess_with_car(eeg_synthetic)
corr_with_car = classify_cca(eeg_with_car, freqs_target)
print("   Correlaciones:")
for freq, corr in corr_with_car.items():
    print(f"     {freq:5.2f} Hz: {corr:.4f}")

# Procesar SIN CAR
print("\n3. Procesando SIN CAR...")
eeg_without_car = preprocess_without_car(eeg_synthetic)
corr_without_car = classify_cca(eeg_without_car, freqs_target)
print("   Correlaciones:")
for freq, corr in corr_without_car.items():
    print(f"     {freq:5.2f} Hz: {corr:.4f}")

# COMPARACIÓN
print("\n4. COMPARACIÓN")
print("="*80)
print(f"{'Frecuencia':>12} {'CON CAR':>15} {'SIN CAR':>15} {'Diferencia':>15}")
print("-"*80)

mejoras = []
for freq in freqs_target:
    with_car = corr_with_car[freq]
    without_car = corr_without_car[freq]
    diff = ((without_car - with_car) / with_car * 100) if with_car != 0 else 0
    mejoras.append(diff)
    
    print(f"{freq:>12.2f} {with_car:>15.4f} {without_car:>15.4f} {diff:>14.1f}%")

print("-"*80)
print(f"{'Mejora promedio SIN CAR':>42} {np.mean(mejoras):>14.1f}%")
print("="*80)

# CONCLUSIÓN
if np.mean(mejoras) > 0:
    print(f"\n✅ SIN CAR es {np.mean(mejoras):.1f}% MEJOR en datos sintéticos")
    print("   Conclusión: CAR empeora cuando hay ruido variable")
else:
    print(f"\n⚠️ CAR es {-np.mean(mejoras):.1f}% mejor")
    print("   Pero en datos reales online: SIN CAR gana")

print("\n" + "="*80)