# BCI processing.py 
# SSVEP preprocessing + CCA classification
# Preprocesses the gathered signals by using Bandpass, Notch and CAR
# Processes the CCA comparison signals
#
# All filter/CCA constants live in config.py (single source of truth).
#
# Pipeline:
#   1. Double Butterworth bandpass
#   2. Notch comb (50 / 100 / 150 Hz)
#   3. Channel selection (P7, P8, O1, O2)
#   4. Common Average Reference (CAR)
# Classification: CCA against reference signals built from CCA_HARMONICS.
 
import numpy as np
from scipy.signal import butter, iirnotch, tf2sos, sosfiltfilt
from sklearn.cross_decomposition import CCA
 
from config import (
    FS, USED_CHANNELS,
    BP_LO, BP_HI,
    NOTCH_FUND, NOTCH_NH, NOTCH_Q,
    CCA_HARMONICS, CCA_N_COMPONENTS,
    APPLY_CAR,
)
 
 
# Pre-compute filters
 
def build_bandpass(lo=BP_LO, hi=BP_HI, order=4):
    """Butterworth bandpass as second-order sections."""
    nyq = FS / 2
    return butter(order, [max(lo / nyq, 1e-4), min(hi / nyq, 0.999)],
                  btype='bandpass', output='sos')
 
 
def build_notch_comb(fundamental=NOTCH_FUND, n_harmonics=NOTCH_NH, Q=NOTCH_Q):
    """Notch comb at fundamental and its harmonics (50 / 100 / 150 Hz)."""
    sos_list = []
    for k in range(1, n_harmonics + 1):
        freq = fundamental * k
        if freq >= FS / 2:
            break
        b, a = iirnotch(freq, Q=Q, fs=FS)
        sos_list.append(tf2sos(b, a))
    return sos_list
 
 
_SOS_BP = build_bandpass()
_SOS_NOTCH = build_notch_comb()
 
print("[Processing] Pre-computed filters:")
print(f"  - Bandpass: {BP_LO}-{BP_HI} Hz")
print(f"  - Notch comb: 50 / 100 / 150 Hz (Q={NOTCH_Q})")
print(f"  - CCA harmonics: {CCA_HARMONICS}")
 
 
class EEGProcessor:
    """SSVEP preprocessing and CCA classification."""
 
    def __init__(self):
        self.fs = FS
        self.used_channels = USED_CHANNELS  # P7, P8, O1, O2
 
    def preprocess(self, eeg_data):
        """Full pipeline: double bandpass -> notch comb -> select channels -> CAR."""
        # 1. Double Butterworth bandpass
        eeg = sosfiltfilt(_SOS_BP, eeg_data, axis=1) # filtrado de fase cero (ida y vuelta) con secciones de segundo orden
        #para otorgar mayor estabilidad 
        eeg = sosfiltfilt(_SOS_BP, eeg, axis=1)
 
        # 2. Notch comb (50 / 100 / 150 Hz)
        for sos_n in _SOS_NOTCH:
            eeg = sosfiltfilt(sos_n, eeg, axis=1)
 
        # 3. Select occipital/parietal channels
        eeg = eeg[self.used_channels, :]
 
        # 4. Common Average Reference
        if APPLY_CAR:
            eeg = self.apply_car(eeg)
        return eeg
 
    def apply_car(self, eeg_data):
        """Common Average Reference: subtract the mean across channels."""
        mean_ref = np.mean(eeg_data, axis=0, keepdims=True)
        return eeg_data - mean_ref
 
    def generate_references(self, frequency, n_samples):
        """Sine/cosine reference bank for the given frequency and its harmonics.
 
        Returns an array of shape (n_samples, 2 * len(CCA_HARMONICS)).
        """
        t = np.arange(n_samples) / self.fs
        components = []
        for harmonic in CCA_HARMONICS:
            freq_h = frequency * harmonic
            components.append(np.sin(2 * np.pi * freq_h * t))
            components.append(np.cos(2 * np.pi * freq_h * t))
        return np.array(components).T
 
    def classify(self, eeg_data, frequencies):
        """Return (best_freq, best_corr, all_corrs) via CCA over candidate freqs.
 
        eeg_data: (n_channels, n_samples)
        """
        n_samples = eeg_data.shape[1]
        X = eeg_data.T.astype(np.float64)  # (n_samples, n_channels)
 
        all_corrs = {}
        for freq in frequencies:
            Y = self.generate_references(freq, n_samples)
            corr = self.canonical_corr(X, Y)
            all_corrs[freq] = corr
            print(f"[CCA] {freq}Hz: {corr:.4f}")
 
        if all_corrs:
            best_freq = max(all_corrs, key=all_corrs.get)
            best_corr = all_corrs[best_freq]
        else:
            best_freq, best_corr = frequencies[0], 0.0
 
        return best_freq, best_corr, all_corrs
 
    def canonical_corr(self, X, Y):
        """First canonical correlation between X and Y (sklearn CCA)."""
        try:
            X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
            Y = np.nan_to_num(Y, nan=0.0, posinf=0.0, neginf=0.0)
 
            X_norm = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
            Y_norm = (Y - Y.mean(axis=0)) / (Y.std(axis=0) + 1e-8)
 
            cca = CCA(n_components=CCA_N_COMPONENTS)
            cca.fit(X_norm, Y_norm)
            X_c, Y_c = cca.transform(X_norm, Y_norm)
 
            rho = abs(np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1])
            return float(np.clip(rho, 0.0, 1.0))
        except Exception as e:
            print(f"[CCA] Error: {e}")
            return 0.0