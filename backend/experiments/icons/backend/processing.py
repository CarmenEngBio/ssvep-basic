# bci_processing_NOTEBOOK.py — Procesamiento CCA del Notebook
# Implementación exacta del notebook Trials_12 pero para uso ONLINE
 
import numpy as np
from scipy.signal import butter, iirnotch, tf2sos, sosfiltfilt
from sklearn.cross_decomposition import CCA
 
# ==========================================
# CONFIGURACIÓN (del notebook)
# ==========================================
 
FS = 250                    # Frecuencia de muestreo (Hz)
UNITS_ALREADY_UV = True     # Los datos ya vienen en µV
 
# Bandpass
BP_LO = 1.0                 # Hz (baja)
BP_HI = 40.0                # Hz (alta)
 
# Notch Comb
NOTCH_FUND = 50.0           # Fundamental (Hz)
NOTCH_NH = 3               # Solo 50 Hz (no 100, 150)
NOTCH_Q = 30                # Calidad del notch
 
# CCA
CCA_HARMONICS = [1, 2, 3]   # Usar fundamental, 2da y 3ra armónica
CCA_N_COMPONENTS = 1        # Componente principal
 
# ==========================================
# PRE-COMPUTAR FILTROS (como en notebook)
# ==========================================
 
def construir_bandpass(lo=BP_LO, hi=BP_HI, order=4):
    """Construir doble Butterworth bandpass."""
    nyq = FS / 2
    return butter(order, [max(lo/nyq, 1e-4), min(hi/nyq, 0.999)],
                  btype='bandpass', output='sos')
 
def construir_comb_notch(fundamental=NOTCH_FUND, n_harmonics=NOTCH_NH, Q=NOTCH_Q):
    """Construir notch comb (50, 100, 150 Hz)."""
    sos_list = []
    for k in range(1, n_harmonics + 1):
        freq = fundamental * k
        if freq >= FS / 2:
            break
        b, a = iirnotch(freq, Q=Q, fs=FS)
        sos_list.append(tf2sos(b, a))
    return sos_list
 
_SOS_BP = construir_bandpass()
_SOS_NOTCH = construir_comb_notch()
 
print("[BCI Processing] Filtros pre-computados:")
print(f"  - Bandpass: {BP_LO}-{BP_HI} Hz (double)")
print(f"  - Notch: 50 Hz solo (Q={NOTCH_Q})")
print(f"  - CCA Harmonics: [1, 2, 3]")
 
# ==========================================
# FUNCIONES DE PROCESAMIENTO
# ==========================================
 
class EEGProcessor:
    """Procesador EEG con método del notebook."""
    
    def __init__(self):
        self.fs = FS
        self.used_channels = [4, 5, 6, 7]  # P7, P8, O1, O2
    
    def preprocess(self, eeg_data):
        """
        Pipeline completo (como notebook):
        1. Double Butterworth bandpass
        2. Notch comb filters
        3. Seleccionar canales
        4. CAR (se hace aquí junto con datos)
        """
        # Paso 1: Double Butterworth bandpass (aplicado 2 veces)
        eeg_notch = sosfiltfilt(_SOS_BP, eeg_data, axis=1)
        eeg_notch = sosfiltfilt(_SOS_BP, eeg_notch, axis=1)
        
        # Paso 2: Notch comb (50, 100, 150 Hz)
        for sos_n in _SOS_NOTCH:
            eeg_notch = sosfiltfilt(sos_n, eeg_notch, axis=1)
        
        # Paso 3: Seleccionar canales + CAR
        # Nota: CAR se aplica después de seleccionar canales
        eeg_selected = eeg_notch[self.used_channels, :]
        
        # Paso 4: CAR - restar media de todos los canales
        eeg_car = self.apply_car(eeg_selected)
        
        return eeg_car
    
    def apply_car(self, eeg_data):
        """
        Common Average Reference: resta la media de todos los canales.
        eeg_data: shape (n_channels, n_samples)
        """
        mean_ref = np.mean(eeg_data, axis=0, keepdims=True)
        return eeg_data - mean_ref
    
    def generate_references(self, frequency, n_samples):
        """
        Generar referencias SSVEP con harmonics (como notebook).
        Devuelve matrix (n_samples, n_components)
        donde n_components = 2 * len(harmonics)
        """
        t = np.arange(n_samples) / self.fs
        components = []
        
        for harmonic in CCA_HARMONICS:
            freq_h = frequency * harmonic
            components.append(np.sin(2 * np.pi * freq_h * t))
            components.append(np.cos(2 * np.pi * freq_h * t))
        
        return np.array(components).T  # Transponer para (n_samples, n_components)
    
    def classify(self, eeg_data, frequencies):
        """
        Clasificación CCA (como notebook).
        eeg_data: shape (n_channels, n_samples)
        frequencies: lista de frecuencias candidatas
        
        Devuelve: (best_freq, best_corr, all_corrs_dict)
        """
        n_channels, n_samples = eeg_data.shape
        
        # Transpose para que sea (n_samples, n_channels)
        X = eeg_data.T.astype(np.float64)
        
        all_corrs = {}
        
        for freq in frequencies:
            # Generar referencias con harmonics
            Y = self.generate_references(freq, n_samples)
            
            # CCA con sklearn
            try:
                corr = self.calcular_rho_cca(X, Y)
                all_corrs[freq] = corr
                print(f"[CCA] {freq}Hz: {corr:.4f}")
            except Exception as e:
                print(f"[CCA Error] {freq}Hz: {e}")
                all_corrs[freq] = 0.0
        
        # Encontrar mejor correlación
        if all_corrs:
            best_freq = max(all_corrs, key=all_corrs.get)
            best_corr = all_corrs[best_freq]
        else:
            best_freq = frequencies[0]
            best_corr = 0.0
        
        return best_freq, best_corr, all_corrs
    
    def calcular_rho_cca(self, X, Y):
        """
        Calcular correlación canónica con sklearn (como notebook).
        X: (n_samples, n_channels)
        Y: (n_samples, n_components)
        """
        try:
            # Normalizar
            X_norm = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
            Y_norm = (Y - Y.mean(axis=0)) / (Y.std(axis=0) + 1e-8)
            
            # CCA
            cca = CCA(n_components=CCA_N_COMPONENTS)
            cca.fit(X_norm, Y_norm)
            
            # Transform
            X_c, Y_c = cca.transform(X_norm, Y_norm)
            
            # Correlación canónica
            rho = abs(np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1])
            
            return float(np.clip(rho, 0.0, 1.0))
        
        except Exception as e:
            print(f"[CCA] Error: {e}")
            return 0.0
 
 
# ==========================================
# TEST RÁPIDO
# ==========================================
 
if __name__ == "__main__":
    # Test con datos aleatorios
    processor = EEGProcessor()
    
    # Datos fake
    eeg_fake = np.random.randn(8, 2500)  # 8 canales, 10s @ 250Hz
    
    # Procesar
    eeg_proc = processor.preprocess(eeg_fake)
    print(f"\nProcesado: {eeg_proc.shape}")
    
    # Clasificar
    freqs = [8.57, 10.0, 12.0, 15.0]
    best_f, best_c, all_c = processor.classify(eeg_proc, freqs)
    print(f"Mejor: {best_f}Hz (corr={best_c:.4f})")