# BCI server.py
# SSVEP BCI Server with real-time feedback operation
# Implements CCA classification as well
# One 40s block per session: user gazes at the TARGET_CELL while all flicker simultaneously. 
# Every 4s window is classified with CCA and the result is streamed to the frontend. T
# To record every symbol, change TARGET_CELL in config.py and run again.
 
import asyncio
import json
import time
import numpy as np
import websockets
 
from config import CELLS, TRIAL_SEC, WINDOW_SEC, FS, TARGET_CELL
from eegsource import CytonEEG
from recorder import EEGRecorder
from processing import EEGProcessor
 
recorder = EEGRecorder()
processor = EEGProcessor()
 
 
class BCIBlock:
    """Accumulates EEG windows and classifies them with CCA."""
 
    def __init__(self):
        self.trial_data = []
        self.trial_timestamps = []
 
    def reset(self):
        self.trial_data = []
        self.trial_timestamps = []
 
    def add_samples(self, eeg_chunk, timestamps):
        self.trial_data.append(eeg_chunk)
        self.trial_timestamps.extend(timestamps)
 
    def has_enough_data(self) -> bool:
        """At least 2s of samples before classifying."""
        return len(self.trial_timestamps) > FS * 2
 
    def classify(self, target_freq) -> dict:
        if not self.has_enough_data():
            return {"freq": None, "corr": 0.0, "correct": False, "all_corrs": {}}
 
        X = np.hstack(self.trial_data)
        X_processed = processor.preprocess(X)
 
        frequencies = [CELLS[i]["freq"] for i in sorted(CELLS.keys())]
        best_freq, best_corr, all_corrs = processor.classify(X_processed, frequencies)
 
        is_correct = abs(best_freq - target_freq) < 0.5
 
        return {
            "freq": best_freq,
            "corr": round(best_corr, 4),
            "correct": is_correct,
            "all_corrs": {f: round(c, 4) for f, c in all_corrs.items()},
        }
 
 
bci_block = BCIBlock()
 
 
async def run_blocks(ws, source):
    """Run one 40s block for TARGET_CELL, classifying every window."""
    results = []
 
    cell_id = TARGET_CELL
    info = CELLS[cell_id]
    freq, emoji, label = info["freq"], info["emoji"], info["label"]
 
    # Flush the backlog accumulated, then start recording.
    source.get_new_samples()
    fname = recorder.start(f"online_{label}")
    recorder.set_marker(cell_id)
 
    await ws.send(json.dumps({
        "type": "block_started",
        "cell_id": cell_id, "emoji": emoji, "label": label,
        "freq": freq, "duration": TRIAL_SEC, "file": fname or "",
    }))
 
    start_time_trial = time.time()
    elapsed_trial = 0.0
    num_blocks = 0
    num_corrects = 0
 
    while elapsed_trial < TRIAL_SEC and recorder.is_recording:
        start_time_block = time.time()
        raw_eeg, raw_ts = await source.get_window()  # 4s of EEG
 
        if raw_eeg.shape[1] > 0 and recorder.is_recording:
            bci_block.add_samples(raw_eeg, raw_ts)
            result = bci_block.classify(freq)
 
            if result["correct"]:
                num_corrects += 1
            num_blocks += 1
            elapsed_block = time.time() - start_time_block
            acc_trial = num_corrects / num_blocks * 100
 
            results.append({
                "cell_id": cell_id, "label": label, "target_freq": freq,
                "detected_freq": result["freq"], "correlation": result["corr"],
                "correct": result["correct"], "all_corrs": result["all_corrs"],
                "time_elapsed": elapsed_block,
            })
 
            if result["correct"]:
                status = "✅ CORRECT"
            else:
                status = f"❌ INCORRECT (detected {result['freq']:.2f}Hz)"
 
            print(f"[Result] {emoji} {label}: Corr={result['corr']:.4f} — {status}")
            print(f"[Time elapsed] {elapsed_block:.4f} (s)")
            print(f"[SUMMARY] Accuracy: {num_corrects}/{num_blocks} ({acc_trial:.1f}%)")
 
            await ws.send(json.dumps({
                "type": "block_result",
                "cell_id": cell_id, "emoji": emoji, "label": label,
                "correlation": result["corr"], "correct": result["correct"],
                "detected_freq": result["freq"], "all_corrs": result["all_corrs"],
                "accuracy": round(acc_trial, 1), "status": status,
            }))
 
            bci_block.reset()
 
        elapsed_trial = time.time() - start_time_trial
        await asyncio.sleep(0.1)
 
    # At 40 s: write the full trial to disk and stop.
    new_eeg, new_ts = source.get_new_samples()
    if recorder.is_recording:
        recorder.write_chunk(new_eeg, new_ts)
    recorder.stop()
 
    await ws.send(json.dumps({
        "type": "session_ended",
        "accuracy": round(num_corrects / num_blocks * 100, 1) if num_blocks else 0.0,
        "correct": num_corrects, "total": num_blocks, "results": results,
    }))
 
 
async def handler(ws, source):
    print(f"✓ Client connected: {ws.remote_address}")
    block_task = None
 
    try:
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=0.01)
                msg = json.loads(raw)
 
                if msg.get("type") == "start_session" and not recorder.is_recording:
                    block_task = asyncio.create_task(run_blocks(ws, source))
 
            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass
 
            await ws.send(json.dumps({
                "type": "status",
                "recording": recorder.is_recording,
            }))
 
            await asyncio.sleep(0.5)
 
    except websockets.exceptions.ConnectionClosed:
        print("✗ Client disconnected")
    finally:
        if block_task and not block_task.done():
            block_task.cancel()
        if recorder.is_recording:
            recorder.stop()
 
 
async def main():
    print("=" * 70)
    print("  SSVEP Online Assistive BCI")
    print("=" * 70)
    print(f"  One 40 s block per session: user gazes at the {TARGET_CELL} symbol.")
    print("  Classification: CCA winner on every 4s window.")
    print("  Symbols:")
    for cid, info in sorted(CELLS.items()):
        marker = "   <-- target" if cid == TARGET_CELL else ""
        print(f"    {cid}. {info['emoji']} {info['label']:6} -> {info['freq']} Hz{marker}")
    print(f"  Trial duration: {TRIAL_SEC} s")
    print("  Connected to Cyton hardware.")
    print("=" * 70)
 
    source = CytonEEG()
 
    print(f"  Waiting {WINDOW_SEC}s to fill the EEG buffer ...")
    await asyncio.sleep(WINDOW_SEC)
    print("  Ready! Open the browser and click 'Start Session'.\n")
 
    try:
        async with websockets.serve(lambda ws: handler(ws, source), "localhost", 8765):
            await asyncio.Future()
    finally:
        source.stop()
        print("Cyton disconnected.")
 
 
if __name__ == "__main__":
    asyncio.run(main())