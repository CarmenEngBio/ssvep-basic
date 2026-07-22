# bci_eegsource.py — Conexión con Cyton (solo hardware real)
 
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
 
from config import SERIAL_PORT, N_CHANNELS, WINDOW


class CytonEEG:
    """Interfaz con placa Cyton OpenBCI"""

    def __init__(self):
        BoardShim.disable_board_logger()
        params = BrainFlowInputParams()
        params.serial_port = SERIAL_PORT

        self.board = BoardShim(BoardIds.CYTON_BOARD.value, params)
        all_eeg = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD.value)
        self.eeg_chs = all_eeg[:N_CHANNELS]

        self.board.prepare_session()
        self.board.start_stream()
        print(f"✓ Cyton connected at {SERIAL_PORT}")

        # Buffer acumulativo
        self.buffer = np.zeros((N_CHANNELS, 0))
        self.last_window = None

    def get_window(self) -> np.ndarray:
        """Obtiene ventana rodante de datos."""
        data = self.board.get_current_board_data(WINDOW)
        eeg = np.array([data[ch] for ch in self.eeg_chs])
        
        if eeg.shape[1] < WINDOW:
            pad = np.zeros((len(self.eeg_chs), WINDOW - eeg.shape[1]))
            eeg = np.hstack([pad, eeg])
        
        return eeg[:, -WINDOW:]


    """
    def get_window(self) -> np.ndarray:
        #Obtiene ventana rodante acumulando datos nuevos.
        # Leer muestras nuevas
        new_eeg, _ = self.get_new_samples()
        
        if new_eeg.shape[1] == 0:
            # No hay datos nuevos, devolver buffer anterior
            return self.last_window if self.last_window is not None else np.zeros((N_CHANNELS, WINDOW))
        
        # Acumular
        self.buffer = np.hstack([self.buffer, new_eeg])
        
        # Mantener solo últimas WINDOW muestras
        if self.buffer.shape[1] > WINDOW:
            self.buffer = self.buffer[:, -WINDOW:]
        
        self.last_window = self.buffer.copy()
        return self.buffer
    """

    def get_new_samples(self):
        """Lectura DESTRUCTIVA: vacía el buffer y devuelve muestras nuevas."""
        data = self.board.get_board_data()
        if data.shape[1] == 0:
            return np.zeros((N_CHANNELS, 0)), np.zeros(0)

        eeg = np.array([data[ch] for ch in self.eeg_chs])
        ts_ch = BoardShim.get_timestamp_channel(BoardIds.CYTON_BOARD.value)
        return eeg, data[ts_ch]

    def stop(self) -> None:
        self.board.stop_stream()
        self.board.release_session()
        print("✓ Cyton diconnected")

"""
class CytonEEG:
    #Interfaz con placa Cyton OpenBCI
 
    def __init__(self):
        BoardShim.disable_board_logger()
        params = BrainFlowInputParams()
        params.serial_port = SERIAL_PORT
 
        self.board = BoardShim(BoardIds.CYTON_BOARD.value, params)
        #self.board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)
        all_eeg = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD.value)
        self.eeg_chs = all_eeg[:N_CHANNELS]
 
        self.board.prepare_session()
        self.board.start_stream()
        print(f"✓ Cyton conectada en {SERIAL_PORT}")
 
    def get_window(self) -> np.ndarray:
        #Obtiene ventana rodante de datos (NUESTUCTIVA).
        data = self.board.get_current_board_data(WINDOW)
        eeg = np.array([data[ch] for ch in self.eeg_chs])
 
        if eeg.shape[1] < WINDOW:
            pad = np.zeros((N_CHANNELS, WINDOW - eeg.shape[1]))
            eeg = np.hstack([pad, eeg])
 
        return eeg[:, -WINDOW:]
    
 
    def get_new_samples(self):
        #Lectura DESTRUCTIVA: vacía el buffer y devuelve muestras nuevas.
        data = self.board.get_board_data()
        if data.shape[1] == 0:
            return np.zeros((N_CHANNELS, 0)), np.zeros(0)
 
        eeg = np.array([data[ch] for ch in self.eeg_chs])
        ts_ch = BoardShim.get_timestamp_channel(BoardIds.CYTON_BOARD.value)
        return eeg, data[ts_ch]
 
    def stop(self) -> None:
        self.board.stop_stream()
        self.board.release_session()
        print("✓ Cyton desconectada")

    """