# utility_debug_tool is used as a signal quality module 
# Module used for signal quality analysis with files previously recorded
 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, iirnotch, tf2sos, sosfiltfilt, periodogram
from pathlib import Path
import sys
 
FS = 250
BP_LO = 5.0
BP_HI = 25.0
NOTCH_FUND = 50.0
NOTCH_Q = 40
USED_CHANNELS = [4, 5, 6, 7]  # P7, P8, O1, O2

USAR_CAR = True
 
EXPECTED_FREQS = [8.57, 10.0, 12.0, 15.0]

 
def load_recording_test(filepath):
    df = pd.read_csv(filepath, comment='%')
    df.columns = df.columns.str.strip()
    return df
 
def detect_channels(df):
    return [c for c in df.columns if 'EXG Channel' in c][:8]
 
def build_filters():
    nyq = FS / 2
    sos_bp = butter(4, [max(BP_LO/nyq, 1e-4), min(BP_HI/nyq, 0.999)],
                    btype='bandpass', output='sos')
    
    b, a = iirnotch(NOTCH_FUND, Q=NOTCH_Q, fs=FS)
    sos_notch = tf2sos(b, a)
    
    return sos_bp, sos_notch
 
def analize_signal(eeg_data, label, sos_bp, sos_notch):
    
    print(f"Analysis: {label}")
    
    print(f"\n1. Raw EEG signal")
    print(f"   Shape: {eeg_data.shape}")
    print(f"   Range: [{eeg_data.min():.2f}, {eeg_data.max():.2f}] µV")
    print(f"   Average: {eeg_data.mean():.2f} µV")
    print(f"   Std: {eeg_data.std():.2f} µV")
    print(f"   RMS: {np.sqrt(np.mean(eeg_data**2)):.2f} µV")
    

    print(f"\n2. Raw FFT")
    eeg_single = eeg_data[0, :]
    freqs, pxx = periodogram(eeg_single, fs=FS)
    
    def band_energy(freqs, pxx, f_low, f_high):
        mask = (freqs >= f_low) & (freqs <= f_high)
        return np.sum(pxx[mask])
    
    alpha = band_energy(freqs, pxx, 8, 12) 
    ssvep_band = band_energy(freqs, pxx, 8, 15)
    notch_band = band_energy(freqs, pxx, 48, 52)  # 50Hz
    
    print(f"   Energy 8-12 Hz (alpha): {alpha:.2e}")
    print(f"   Energy 8-15 Hz (SSVEP): {ssvep_band:.2e}")
    print(f"   Energy 48-52 Hz: {notch_band:.2e}")
    print(f"   Ratio SSVEP/Noise: {ssvep_band/notch_band:.4f}")
    
    print(f"\n3. Applying filters")
    eeg_bp = sosfiltfilt(sos_bp, eeg_data, axis=1)
    print(f"Bandpass {BP_LO}-{BP_HI} Hz (double pass)")
    
    eeg_notch = sosfiltfilt(sos_notch, eeg_bp, axis=1)
    eeg_notch = sosfiltfilt(sos_notch, eeg_notch, axis=1)
    print(f"Notch 50 Hz")
    
    # eeg_car = eeg_notch - np.mean(eeg_notch, axis=0, keepdims=True)
    # print(f"CAR")

    if USAR_CAR:
        eeg_car = eeg_notch - np.mean(eeg_notch, axis=0, keepdims=True)
        print(f"CAR")
    else:
        eeg_car = eeg_notch  # Without CAR
        print(f"CAR disabled")
    
    print(f"\n4. Filtered signal")
    print(f"   Range: [{eeg_car.min():.2f}, {eeg_car.max():.2f}] µV")
    print(f"   Average: {eeg_car.mean():.2f} µV")
    print(f"   Std: {eeg_car.std():.2f} µV")
    print(f"   RMS: {np.sqrt(np.mean(eeg_car**2)):.2f} µV")
    
    print(f"\n5. Raw FFT filtered")
    eeg_car_single = eeg_car[0, :]
    freqs_filt, pxx_filt = periodogram(eeg_car_single, fs=FS)
    
    alpha_filt = band_energy(freqs_filt, pxx_filt, 8, 12)
    ssvep_filt = band_energy(freqs_filt, pxx_filt, 8, 15)
    notch_filt = band_energy(freqs_filt, pxx_filt, 48, 52)
    
    print(f"   Energy 8-12 Hz (alpha): {alpha_filt:.2e}")
    print(f"   Energy 8-15 Hz (SSVEP): {ssvep_filt:.2e}")
    print(f"   Energy 48-52 Hz: {notch_filt:.2e}")
    print(f"   Ratio SSVEP/ Noise: {ssvep_filt/notch_filt:.4f}")
    
    print(f"\n6. Filter use impact")
    print(f"   Energy SSVEP: {ssvep_band:.2e} → {ssvep_filt:.2e}")
    print(f"   Change: {(ssvep_filt/ssvep_band - 1)*100:+.1f}%")
    print(f"   Energy 50Hz: {notch_band:.2e} → {notch_filt:.2e}")
    print(f"   Reduction 50Hz: {(1 - notch_filt/notch_band)*100:.1f}%")
    
    print(f"\n7. DIAGNOSIS")
    
    if ssvep_band < 1e-6:
        print(f"   CRITICAL: Raw signal has no SSVEP energy")
        print(f"              Problem: due to conductivity or user")
    elif ssvep_filt < ssvep_band * 0.1:
        print(f"   CRITICAL: Filters destroy SSVEP signal")
        print(f"              Problem: Bandpass/Notch too aggresive")
    elif notch_band > ssvep_band * 10:
        print(f"   CRITICAL: Noise of 50Hz domains upon SSVEP signal")
        print(f"              Problem: Strong PLI")
    else:
        print(f"   OK: Signal seems adequate")
    

    print(f"\n8. Expected activities")
    for freq in EXPECTED_FREQS:
        idx = np.argmin(np.abs(freqs_filt - freq))
        poder = pxx_filt[idx]
        print(f"   {freq:5.2f} Hz: {poder:.2e}")
    
    #return eeg_car
    return eeg_car, eeg_notch

def cca_correlations_calculation(eeg_car, eeg_sin_car):
    from sklearn.cross_decomposition import CCA
    
    print(f"\n9. CCA comparison WITH CAR vs WITHOUT CAR")
    
    freqs_ssvep = [8.57, 10.0, 12.0, 15.0]
    
    for eeg, label in [(eeg_car, "WITH CAR"), (eeg_sin_car, "WITHOUT CAR")]:
        print(f"\n   {label}:")
        
        for freq in freqs_ssvep:
            t = np.arange(eeg.shape[1]) / FS
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
            
            print(f"      {freq:5.2f} Hz: {corr:.4f}")


def detect_blocks(df, fs=FS, dur_bloque_s=60):

    posibles = [c for c in df.columns if any(k in c.lower() for k in ['marker', 'label', 'stim', 'event', 'block'])]

    if posibles:
        col = posibles[0]
        print(f"   Using marker column: '{col}'")
        bloques = []
        for _, grupo in df.groupby(col):
            idx = grupo.index.values
            bloques.append((idx[0], idx[-1] + 1))
        return bloques

    print(f"   Not found - asuming fixed blocks of "
          f"{dur_bloque_s}s ir order {EXPECTED_FREQS}")
    n = int(dur_bloque_s * fs)
    return [(i * n, (i + 1) * n) for i in range(len(EXPECTED_FREQS))]


def correlations_per_block(eeg_car, eeg_sin_car, bloques):

    from sklearn.cross_decomposition import CCA

    def cca_corr(segmento, freq, t):
        ref = np.column_stack([
            np.sin(2*np.pi*freq*t),   np.cos(2*np.pi*freq*t),
            np.sin(2*np.pi*freq*2*t), np.cos(2*np.pi*freq*2*t),
        ])
        cca = CCA(n_components=1)
        cca.fit(segmento.T, ref)
        U, V = cca.transform(segmento.T, ref)
        return np.corrcoef(U[:, 0], V[:, 0])[0, 1]

    print(f"\n9. CCA per block - WITH CAR vs WITHOUT CAR")
    aciertos = {"WITH CAR": 0, "WITHOUT CAR": 0}

    for i, (inicio, fin) in enumerate(bloques):
        freq_obj = EXPECTED_FREQS[i] if i < len(EXPECTED_FREQS) else None
        seg_car     = eeg_car[:, inicio:fin]
        seg_sin_car = eeg_sin_car[:, inicio:fin]
        t = np.arange(seg_car.shape[1]) / FS

        print(f"\n   Block {i+1} (samples {inicio}:{fin}, expected: {freq_obj} Hz)")
        print(f"      {'Freq':>7} | {'WITH CAR':>9} | {'WITHOUT CAR':>9}")
        print(f"      {'-'*7}-+-{'-'*9}-+-{'-'*9}")

        corr_car, corr_sin = {}, {}
        for freq in EXPECTED_FREQS:
            c_car = cca_corr(seg_car, freq, t)
            c_sin = cca_corr(seg_sin_car, freq, t)
            corr_car[freq], corr_sin[freq] = c_car, c_sin
            marca = " ←" if freq == freq_obj else ""
            print(f"      {freq:7.2f} | {c_car:9.4f} | {c_sin:9.4f}{marca}")

        det_car = max(corr_car, key=corr_car.get)
        det_sin = max(corr_sin, key=corr_sin.get)
        ok_car = freq_obj is not None and np.isclose(det_car, freq_obj)
        ok_sin = freq_obj is not None and np.isclose(det_sin, freq_obj)
        aciertos["WITH CAR"] += int(ok_car)
        aciertos["WITHOUT CAR"] += int(ok_sin)
        print(f"      → WITH CAR: {det_car} Hz {'✅' if ok_car else '❌'}   "
              f"| WITHOUT CAR: {det_sin} Hz {'✅' if ok_sin else '❌'}")

    n = len(bloques)
    print(f"\n   SUMMARY:")
    print(f"      WITH CAR: {aciertos['WITH CAR']}/{n} ({100*aciertos['WITH CAR']/n:.1f}%)")
    print(f"      WITHOUT CAR: {aciertos['WITHOUT CAR']}/{n} ({100*aciertos['WITHOUT CAR']/n:.1f}%)")
 
 
def main(filepath):

    print("DEBUG SIGNAL QUALITY - Signal Analysis and Diagnosis")
    
    print(f"\nLoading: {filepath}")
    df = load_recording_test(filepath)
    canales = detect_channels(df)
    
    if len(canales) == 0:
        print("ERROR: None EXG channel were found")
        return
    
    eeg_raw = np.array([df[canales[i]].values for i in USED_CHANNELS]).astype(np.float64)
    
    sos_bp, sos_notch = build_filters()
    
    #eeg_proc = analizar_signal(eeg_raw, "CANALIZA REALES (P7, P8, O1, O2)", sos_bp, sos_notch)
    eeg_proc, eeg_notch = analize_signal(eeg_raw, "(P7, P8, O1, O2)", sos_bp, sos_notch)
    
    #eeg_sin_car = eeg_notch  # WITHOUT CAR
    #cca_correlations_calculation(eeg_proc, eeg_sin_car)

    bloques = detect_blocks(df)
    correlations_per_block(eeg_proc, eeg_notch, bloques)
    
    print("Observations")
    
    print("If correlations < 0.1 with headset:")
    print()
    print("1. Check electrodes conductivity:")
    print("   - Verify that all of them reach the scalp")
    print()
    print("2. Check users focus:")
    print("   - Try not to blink during the recording trial")
    print("   - Gazed at the cell relaxed, without making cognitive effort")
    print()
    print("3. Check PLI (50 Hz):")
    print("   - Be far from electronic equipment")
    print("   - Disconnect close devices")
    print("   - Verify if Notch is applied")
    print()
    print("4. Changes in parameters configuration:")
    print("   - Increase windowsize")
    print("   - Lower the canonical correlation threshold")
    print("   - Manipulate the CAR")
    print()
    print("5. Desactivate CAR temporalily:")
    print("   - Observe if there is better correlation")
    print("   - Analyze if CAR improves/worsens the results with the configured classification")
    print()
    print("="*80 + "\n")
 
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Use: python debug_signal_quality.py <archivo.txt>")
        sys.exit(1)
    
    main(sys.argv[1])