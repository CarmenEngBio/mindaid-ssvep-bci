# eegsource.py
 
import asyncio
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
 
from config import SERIAL_PORT, N_CHANNELS, WINDOW, FS, USE_SYNTHETIC_BOARD
 
 
class CytonEEG:
 
    def __init__(self):
        BoardShim.disable_board_logger()
        params = BrainFlowInputParams()
        params.serial_port = SERIAL_PORT
 
        self.board_id = (BoardIds.SYNTHETIC_BOARD.value if USE_SYNTHETIC_BOARD
                         else BoardIds.CYTON_BOARD.value)
        self.board = BoardShim(self.board_id, params)
        all_eeg = BoardShim.get_eeg_channels(self.board_id)
        self.eeg_chs = all_eeg[:N_CHANNELS]
        self.ts_ch = BoardShim.get_timestamp_channel(self.board_id)
 
        self.board.prepare_session()
        self.board.start_stream()
        if USE_SYNTHETIC_BOARD:
            print("✓ Synthetic board started (no hardware)")
        else:
            print(f"✓ Cyton connected at {SERIAL_PORT}")
 
    async def get_window(self):
        data = self.board.get_current_board_data(WINDOW)
        n = data.shape[1]
        if n < WINDOW:
            missing_sec = (WINDOW - n) / FS
            await asyncio.sleep(missing_sec + 0.1)
            data = self.board.get_current_board_data(WINDOW)
 
        eeg = np.array([data[ch] for ch in self.eeg_chs])
        timestamps = data[self.ts_ch]
        return eeg[:, -WINDOW:], timestamps[-WINDOW:]
 
    def get_new_samples(self):
        data = self.board.get_board_data()
        if data.shape[1] == 0:
            return np.zeros((N_CHANNELS, 0)), np.zeros(0)
 
        eeg = np.array([data[ch] for ch in self.eeg_chs])
        return eeg, data[self.ts_ch]
 
    def stop(self) -> None:
        self.board.stop_stream()
        self.board.release_session()
        print("✓ Board disconnected")