# BCI eegsource.py 

import numpy as np
import asyncio
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
 
from config import SERIAL_PORT, N_CHANNELS, WINDOW, FS


class CytonEEG:
    
    # Interface with OpenBCI Cyton board

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

        # Cummulative buffer
        self.buffer = np.zeros((N_CHANNELS, 0))
        self.last_window = None

    async def get_window(self) -> np.ndarray:
        data = self.board.get_current_board_data(WINDOW)
        number_samples = data.shape[1] 
        if  number_samples < WINDOW:
            remain_sec = (WINDOW - number_samples)/FS 
            await asyncio.sleep(remain_sec + 0.1)
            data = self.board.get_current_board_data(WINDOW)
            number_samples = data.shape[1]   
        eeg = np.array([data[ch] for ch in self.eeg_chs])
        ts_ch = BoardShim.get_timestamp_channel(BoardIds.CYTON_BOARD.value)
        time_stamps = data[ts_ch]
        return eeg[:, -WINDOW:], time_stamps[-WINDOW:]  # Last registered window is taken as buffer accumulates the signal


    def get_new_samples(self):
        # Releases buffer and returns new samples
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