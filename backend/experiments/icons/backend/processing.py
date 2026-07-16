# bci_processing.py — Preprocesamiento (Notch + CAR) y Clasificación (CCA)
 
import numpy as np
from scipy import signal
from scipy.linalg import svd
 
from config import FS, NOTCH_FREQ, NOTCH_WIDTH, CCA_THRESHOLD, USED_CHANNELS
 
 
class EEGProcessor:
    """
    Procesa señales EEG:
    1. Filtrado Notch (50, 100, 150 Hz)
    2. Common Average Reference (CAR)
    3. Clasificación CCA
    """
 
    def __init__(self):
        self.fs = FS
        self.notch_freqs = NOTCH_FREQ
        self.notch_width = NOTCH_WIDTH
        self.used_channels = USED_CHANNELS
 
        # Precomputar referencias de frecuencias
        self.freq_refs = {}
 
    def apply_notch_filter(self, eeg_data):
        """
        Aplica filtro notch en las frecuencias especificadas.
        
        Args:
            eeg_data: array (n_channels, n_samples)
        
        Returns:
            eeg_filtered: array (n_channels, n_samples)
        """
        filtered = eeg_data.copy()
 
        for freq in self.notch_freqs:
            # Diseña filtro notch Butterworth 2do orden
            nyquist = self.fs / 2
            low = (freq - self.notch_width) / nyquist
            high = (freq + self.notch_width) / nyquist
 
            # Clip para evitar valores fuera de rango (0, 1)
            low = np.clip(low, 0.001, 0.999)
            high = np.clip(high, 0.001, 0.999)
 
            if low < high:
                b, a = signal.butter(2, [low, high], btype='bandstop')
                filtered = signal.filtfilt(b, a, filtered, axis=1)
 
        return filtered
 
    def apply_car(self, eeg_data):
        """
        Aplica Common Average Reference (CAR).
        Resta el promedio de todos los canales a cada uno.
        
        Args:
            eeg_data: array (n_channels, n_samples)
        
        Returns:
            eeg_car: array (n_channels, n_samples)
        """
        car_signal = np.mean(eeg_data, axis=0, keepdims=True)
        return eeg_data - car_signal
 
    def preprocess(self, eeg_data):
        """
        Aplica pipeline completo de preprocesamiento.
        
        Args:
            eeg_data: array (n_channels, n_samples)
        
        Returns:
            eeg_processed: array (n_channels, n_samples) solo canales usados
        """
        # 1. Filtrado notch
        eeg_notch = self.apply_notch_filter(eeg_data)
 
        # 2. CAR
        eeg_car = self.apply_car(eeg_notch)
 
        # 3. Seleccionar solo los canales usados (P7, P8, O1, O2)
        eeg_processed = eeg_car[self.used_channels, :]
 
        return eeg_processed
 
    def generate_reference_signals(self, n_samples, frequencies):
        """
        Genera referencias sinusoidales para CCA.
        
        Args:
            n_samples: número de muestras
            frequencies: lista de frecuencias (Hz)
        
        Returns:
            dict: referencias por frecuencia
        """
        t = np.arange(n_samples) / self.fs
        refs = {}
 
        for freq in frequencies:
            # Componente 1: sin(2πft)
            sin_comp = np.sin(2 * np.pi * freq * t)
            # Componente 2: cos(2πft)
            cos_comp = np.cos(2 * np.pi * freq * t)
            # Matriz de referencia (2, n_samples)
            refs[freq] = np.vstack([sin_comp, cos_comp])
 
        return refs
 
    def cca(self, X, Y):
        """
        Canonical Correlation Analysis (CCA) simplificado.
        
        Args:
            X: array (n_features_X, n_samples) - datos EEG
            Y: array (n_features_Y, n_samples) - señal de referencia
        
        Returns:
            corr: correlación canónica (escalar entre 0 y 1)
        """
        X = X.astype(np.float64)
        Y = Y.astype(np.float64)
 
        n = X.shape[1]  # número de muestras
 
        if n < max(X.shape[0], Y.shape[0]):
            # Si hay pocas muestras, retornar correlación baja
            return 0.0
 
        # Centrar datos
        X = X - np.mean(X, axis=1, keepdims=True)
        Y = Y - np.mean(Y, axis=1, keepdims=True)
 
        # Matrices de covarianza
        try:
            Cxx = (X @ X.T) / n
            Cyy = (Y @ Y.T) / n
            Cxy = (X @ Y.T) / n
 
            # Regularización para evitar singularidad
            reg = 1e-4
            Cxx += reg * np.eye(Cxx.shape[0])
            Cyy += reg * np.eye(Cyy.shape[0])
 
            # Resolver SVD
            # Cxx^{-1/2} @ Cxy @ Cyy^{-1/2}
            try:
                inv_sqrt_Cxx = np.linalg.inv(np.linalg.cholesky(Cxx))
                inv_sqrt_Cyy = np.linalg.inv(np.linalg.cholesky(Cyy))
            except np.linalg.LinAlgError:
                return 0.0
 
            M = inv_sqrt_Cxx @ Cxy @ inv_sqrt_Cyy.T
            U, S, Vt = np.linalg.svd(M)
 
            # Correlación canónica es el valor singular máximo
            corr = np.max(S) if len(S) > 0 else 0.0
 
        except Exception as e:
            print(f"[CCA Error] {e}")
            corr = 0.0
 
        return float(np.clip(corr, 0.0, 1.0))
 
    def classify(self, eeg_data, frequencies):
        """
        Clasifica según CCA.
        
        Args:
            eeg_data: array (n_channels_used, n_samples) - datos preprocesados
            frequencies: lista de frecuencias a probar
        
        Returns:
            (best_freq, best_corr, all_corrs): frecuencia, correlación máxima, dict de todas
        """
        all_corrs = {}
 
        # Generar referencias
        references = self.generate_reference_signals(eeg_data.shape[1], frequencies)
 
        # Calcular CCA para cada frecuencia
        for freq in frequencies:
            ref = references[freq]
            corr = self.cca(eeg_data, ref)
            all_corrs[freq] = corr
 
        # Encontrar frecuencia con máxima correlación
        best_freq = max(all_corrs, key=all_corrs.get)
        best_corr = all_corrs[best_freq]
 
        return best_freq, best_corr, all_corrs