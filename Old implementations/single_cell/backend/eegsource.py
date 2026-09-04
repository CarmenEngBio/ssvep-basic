
# eegsource.py

import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

from config import SERIAL_PORT, N_CHANNELS, WINDOW


class CytonEEG:

    def __init__(self):
        BoardShim.disable_board_logger()
        params             = BrainFlowInputParams()
        params.serial_port = SERIAL_PORT

        #self.board   = BoardShim(BoardIds.CYTON_BOARD.value, params)
        self.board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)
        all_eeg      = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD.value)
        self.eeg_chs = all_eeg[:N_CHANNELS]

        self.board.prepare_session()
        self.board.start_stream()
        print(f"✓ Cyton connected at {SERIAL_PORT}")

    def get_window(self) -> np.ndarray:
        data = self.board.get_current_board_data(WINDOW)
        eeg  = np.array([data[ch] for ch in self.eeg_chs])

        if eeg.shape[1] < WINDOW:
            pad = np.zeros((N_CHANNELS, WINDOW - eeg.shape[1]))
            eeg = np.hstack([pad, eeg])

        return eeg[:, -WINDOW:]

    # This method reads the data by empting the BrainFlow buffer and returns the new samples with respect to the last call.

    def get_new_samples(self):
       
        data = self.board.get_board_data() 
        if data.shape[1] == 0:
            return np.zeros((N_CHANNELS, 0)), np.zeros(0)

        eeg = np.array([data[ch] for ch in self.eeg_chs])
        ts_ch = BoardShim.get_timestamp_channel(BoardIds.CYTON_BOARD.value)
        return eeg, data[ts_ch]
    

    def stop(self) -> None:
        self.board.stop_stream()
        self.board.release_session()
