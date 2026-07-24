# debug_signal_quality.py — Diagnosticar problemas con señal real
 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, iirnotch, tf2sos, sosfiltfilt, periodogram
from pathlib import Path
import sys
 
# ==========================================
# CONFIGURACIÓN
# ==========================================
 
FS = 250
BP_LO = 5.0
BP_HI = 30.0
NOTCH_FUND = 50.0
NOTCH_Q = 40
USED_CHANNELS = [4, 5, 6, 7]  # P7, P8, O1, O2

USAR_CAR = False
 
# Frecuencias esperadas
EXPECTED_FREQS = [8.57, 10.0, 12.0, 15.0]
 
# ==========================================
# FUNCIONES
# ==========================================
 
def cargar_grabacion(filepath):
    """Cargar archivo .txt."""
    df = pd.read_csv(filepath, comment='%')
    df.columns = df.columns.str.strip()
    return df
 
def detectar_canales(df):
    """Detectar canales EXG."""
    return [c for c in df.columns if 'EXG Channel' in c][:8]
 
def construir_filtros():
    """Pre-construir filtros."""
    nyq = FS / 2
    sos_bp = butter(4, [max(BP_LO/nyq, 1e-4), min(BP_HI/nyq, 0.999)],
                    btype='bandpass', output='sos')
    
    b, a = iirnotch(NOTCH_FUND, Q=NOTCH_Q, fs=FS)
    sos_notch = tf2sos(b, a)
    
    return sos_bp, sos_notch
 
def analizar_signal(eeg_data, label, sos_bp, sos_notch):
    """Análisis completo de una señal."""
    
    print(f"\n{'='*80}")
    print(f"ANÁLISIS: {label}")
    print(f"{'='*80}")
    
    # Estadísticas crudas
    print(f"\n1. SEÑAL CRUDA")
    print(f"   Shape: {eeg_data.shape}")
    print(f"   Rango: [{eeg_data.min():.2f}, {eeg_data.max():.2f}] µV")
    print(f"   Media: {eeg_data.mean():.2f} µV")
    print(f"   Std: {eeg_data.std():.2f} µV")
    print(f"   RMS: {np.sqrt(np.mean(eeg_data**2)):.2f} µV")
    
    # FFT de señal cruda
    print(f"\n2. ESPECTRO CRUDO")
    eeg_single = eeg_data[0, :]  # Canal 0
    freqs, pxx = periodogram(eeg_single, fs=FS)
    
    # Energía en bandas
    def energia_banda(freqs, pxx, f_low, f_high):
        mask = (freqs >= f_low) & (freqs <= f_high)
        return np.sum(pxx[mask])
    
    alpha = energia_banda(freqs, pxx, 8, 12)  # Alpha
    ssvep_banda = energia_banda(freqs, pxx, 8, 15)  # SSVEP esperada
    notch_banda = energia_banda(freqs, pxx, 48, 52)  # 50Hz
    
    print(f"   Energía 8-12 Hz (alpha): {alpha:.2e}")
    print(f"   Energía 8-15 Hz (SSVEP): {ssvep_banda:.2e}")
    print(f"   Energía 48-52 Hz (ruido): {notch_banda:.2e}")
    print(f"   Ratio SSVEP/Ruido: {ssvep_banda/notch_banda:.4f}")
    
    # Aplicar filtros
    print(f"\n3. APLICANDO FILTROS")
    eeg_bp = sosfiltfilt(sos_bp, eeg_data, axis=1)
    print(f"   ✓ Bandpass {BP_LO}-{BP_HI} Hz (double pass)")
    
    eeg_notch = sosfiltfilt(sos_notch, eeg_bp, axis=1)
    eeg_notch = sosfiltfilt(sos_notch, eeg_notch, axis=1)
    print(f"   ✓ Notch 50 Hz")
    
    # Aplicar CAR
    # eeg_car = eeg_notch - np.mean(eeg_notch, axis=0, keepdims=True)
    # print(f"   ✓ CAR")

    # Aplicar CAR (opcional)
    if USAR_CAR:
        eeg_car = eeg_notch - np.mean(eeg_notch, axis=0, keepdims=True)
        print(f"   ✓ CAR")
    else:
        eeg_car = eeg_notch  # Sin CAR
        print(f"   ⊘ CAR deshabilitado")
    
    # Estadísticas después de filtrar
    print(f"\n4. SEÑAL FILTRADA")
    print(f"   Rango: [{eeg_car.min():.2f}, {eeg_car.max():.2f}] µV")
    print(f"   Media: {eeg_car.mean():.2f} µV")
    print(f"   Std: {eeg_car.std():.2f} µV")
    print(f"   RMS: {np.sqrt(np.mean(eeg_car**2)):.2f} µV")
    
    # FFT de señal filtrada
    print(f"\n5. ESPECTRO FILTRADO")
    eeg_car_single = eeg_car[0, :]
    freqs_filt, pxx_filt = periodogram(eeg_car_single, fs=FS)
    
    alpha_filt = energia_banda(freqs_filt, pxx_filt, 8, 12)
    ssvep_filt = energia_banda(freqs_filt, pxx_filt, 8, 15)
    notch_filt = energia_banda(freqs_filt, pxx_filt, 48, 52)
    
    print(f"   Energía 8-12 Hz (alpha): {alpha_filt:.2e}")
    print(f"   Energía 8-15 Hz (SSVEP): {ssvep_filt:.2e}")
    print(f"   Energía 48-52 Hz (ruido): {notch_filt:.2e}")
    print(f"   Ratio SSVEP/Ruido: {ssvep_filt/notch_filt:.4f}")
    
    # Cambio de energía
    print(f"\n6. IMPACTO DE FILTROS")
    print(f"   Energía SSVEP: {ssvep_banda:.2e} → {ssvep_filt:.2e}")
    print(f"   Cambio: {(ssvep_filt/ssvep_banda - 1)*100:+.1f}%")
    print(f"   Energía ruido 50Hz: {notch_banda:.2e} → {notch_filt:.2e}")
    print(f"   Reducción 50Hz: {(1 - notch_filt/notch_banda)*100:.1f}%")
    
    # Diagnóstico
    print(f"\n7. DIAGNÓSTICO")
    
    if ssvep_banda < 1e-6:
        print(f"   🔴 CRÍTICO: Señal cruda NO tiene energía SSVEP")
        print(f"              Problema: Contacto pobre o usuario")
    elif ssvep_filt < ssvep_banda * 0.1:
        print(f"   🔴 CRÍTICO: Filtros destruyen SSVEP (reducen 90%+)")
        print(f"              Problema: Bandpass/Notch demasiado agresivos")
    elif notch_banda > ssvep_banda * 10:
        print(f"   🔴 CRÍTICO: Ruido 50Hz domina señal SSVEP")
        print(f"              Problema: Línea eléctrica muy fuerte")
    else:
        print(f"   🟢 OK: Señal parece buena")
    
    # Picos de frecuencia esperados
    print(f"\n8. PICOS EN FRECUENCIAS ESPERADAS")
    for freq in EXPECTED_FREQS:
        idx = np.argmin(np.abs(freqs_filt - freq))
        poder = pxx_filt[idx]
        print(f"   {freq:5.2f} Hz: {poder:.2e}")
    
    return eeg_car
 
# ==========================================
# MAIN
# ==========================================
 
def main(filepath):
    print("\n" + "="*80)
    print("DEBUG SIGNAL QUALITY — Diagnóstico de Señal Real")
    print("="*80)
    
    # Cargar
    print(f"\nCargando: {filepath}")
    df = cargar_grabacion(filepath)
    canales = detectar_canales(df)
    
    if len(canales) == 0:
        print("ERROR: No se encontraron canales EXG")
        return
    
    eeg_raw = np.array([df[canales[i]].values for i in USED_CHANNELS]).astype(np.float64)
    
    # Construir filtros
    sos_bp, sos_notch = construir_filtros()
    
    # Analizar
    eeg_proc = analizar_signal(eeg_raw, "CANALIZA REALES (P7, P8, O1, O2)", sos_bp, sos_notch)
    
    print("\n" + "="*80)
    print("RECOMENDACIONES")
    print("="*80 + "\n")
    
    print("SI CORRELACIONES < 0.1 CON CASCO REAL:")
    print()
    print("1. REVISAR CONTACTO DEL CASCO:")
    print("   - Verificar que todos los electrodos tocan la piel")
    print("   - Revisar gel conductor")
    print("   - Limpiar electrodos y piel")
    print()
    print("2. COMPROBAR CONCENTRACIÓN DEL USUARIO:")
    print("   - No parpadear durante el trial")
    print("   - Mirar fijamente la celda durante 10+ segundos")
    print("   - Relajarse, no forzar")
    print()
    print("3. REVISAR INTERFERENCIA 50Hz:")
    print("   - Lejos de equipos electrónicos")
    print("   - Desconectar dispositivos cercanos")
    print("   - Revisar que Notch está funcionando")
    print()
    print("4. CAMBIOS EN CONFIGURACIÓN:")
    print("   - Aumentar WINDOW_S de 4.0 a 6.0 segundos")
    print("   - Bajar CCA_THRESHOLD de 0.62 a 0.40")
    print("   - Aumentar CAR_STRENGTH (aunque con cuidado)")
    print()
    print("5. DESABILITAR CAR TEMPORALMENTE:")
    print("   - Comentar línea: eeg_car = eeg_notch")
    print("   - Ver si sin CAR hay correlación")
    print("   - Si mejora: CAR es el problema")
    print()
    print("="*80 + "\n")
 
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python debug_signal_quality.py <archivo.txt>")
        sys.exit(1)
    
    main(sys.argv[1])