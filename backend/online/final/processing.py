# BCI processing.py 
 
import numpy as np
from scipy.signal import butter, iirnotch, tf2sos, sosfiltfilt
from sklearn.cross_decomposition import CCA
 
FS = 250                    # (Hz)
UNITS_ALREADY_UV = True
 
# Bandpass
BP_LO = 7.0                  # Hz low-cut
BP_HI = 70.0                 # Hz upper-cut
 
# Notch Comb
NOTCH_FUND = 50.0           # Fundamental (Hz)
NOTCH_NH = 3               # 50 Hz, 100 and 150
NOTCH_Q = 30                # Notch quality
 
# CCA
CCA_HARMONICS = [1, 2, 3]   # Use fundamental, 2nd and 3rd harmonic
CCA_N_COMPONENTS = 1        # First Canonical Component

# CAR
APPLY_CAR = True 
 
def build_bandpass(lo=BP_LO, hi=BP_HI, order=4):
    nyq = FS / 2
    return butter(order, [max(lo/nyq, 1e-4), min(hi/nyq, 0.999)],
                  btype='bandpass', output='sos')
 
def build_comb_notch(fundamental=NOTCH_FUND, n_harmonics=NOTCH_NH, Q=NOTCH_Q):
    sos_list = []
    for k in range(1, n_harmonics + 1):
        freq = fundamental * k
        if freq >= FS / 2:
            break
        b, a = iirnotch(freq, Q=Q, fs=FS)
        sos_list.append(tf2sos(b, a))
    return sos_list
 
_SOS_BP = build_bandpass()
_SOS_NOTCH = build_comb_notch()
 
print("[BCI Processing] Pre-computing filters:")
print(f"  - Bandpass: {BP_LO}-{BP_HI} Hz (double)")
print(f"  - Notch: 50 Hz (Q={NOTCH_Q})")
print(f"  - CCA Harmonics: [1, 2, 3]")
 
 
class EEGProcessor:
    
    def __init__(self):
        self.fs = FS
        self.used_channels = [4, 5, 6, 7]  # P7, P8, O1, O2
    
    def preprocess(self, eeg_data):
        """
        Pipeline:
        1. Double Butterworth bandpass
        2. Notch comb filters
        3. Selecting processing useful channels
        4. CAR
        """

        eeg_notch = sosfiltfilt(_SOS_BP, eeg_data, axis=1)
        eeg_notch = sosfiltfilt(_SOS_BP, eeg_notch, axis=1)
        
        for sos_n in _SOS_NOTCH:
            eeg_notch = sosfiltfilt(sos_n, eeg_notch, axis=1)
        
        eeg_selected = eeg_notch[self.used_channels, :]
        
        if APPLY_CAR:
            eeg_car = self.apply_car(eeg_selected)
        else:
            eeg_car = eeg_selected.copy()        
        return eeg_car
    
    def apply_car(self, eeg_data):
        #Substracts the average from all channels
        mean_ref = np.mean(eeg_data, axis=0, keepdims=True)
        return eeg_data - mean_ref
    
    def generate_references(self, frequency, n_samples):
        t = np.arange(n_samples) / self.fs
        components = []
        
        for harmonic in CCA_HARMONICS:
            freq_h = frequency * harmonic
            components.append(np.sin(2 * np.pi * freq_h * t))
            components.append(np.cos(2 * np.pi * freq_h * t))
        
        return np.array(components).T  # Transposes to (n_samples, n_components)
    
    def classify(self, eeg_data, frequencies):
        n_channels, n_samples = eeg_data.shape
        
        X = eeg_data.T.astype(np.float64)
        
        all_corrs = {}
        
        for freq in frequencies:
    
            Y = self.generate_references(freq, n_samples)
            
            try:
                corr = self.calcular_rho_cca(X, Y)
                all_corrs[freq] = corr
                print(f"[CCA] {freq}Hz: {corr:.4f}")
            except Exception as e:
                print(f"[CCA Error] {freq}Hz: {e}")
                all_corrs[freq] = 0.0
        
        # Finding best correlation value among sequence
        if all_corrs:
            best_freq = max(all_corrs, key=all_corrs.get)
            best_corr = all_corrs[best_freq]
        else:
            best_freq = frequencies[0]
            best_corr = 0.0
        
        return best_freq, best_corr, all_corrs
    
    def calcular_rho_cca(self, X, Y):
        try:
            
            X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
            Y = np.nan_to_num(Y, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Normalize
            X_norm = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
            Y_norm = (Y - Y.mean(axis=0)) / (Y.std(axis=0) + 1e-8)
            
            # CCA
            cca = CCA(n_components=CCA_N_COMPONENTS)
            cca.fit(X_norm, Y_norm)
            
            # Transform
            X_c, Y_c = cca.transform(X_norm, Y_norm)
            
            # Canonical correlation
            rho = abs(np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1])
            
            return float(np.clip(rho, 0.0, 1.0))
        
        except Exception as e:
            print(f"[CCA] Error: {e}")
            return 0.0