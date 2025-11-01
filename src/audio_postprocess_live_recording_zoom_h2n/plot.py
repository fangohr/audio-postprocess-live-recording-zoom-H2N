# pip install librosa scipy matplotlib numpy
import numpy as np
import librosa as lr
import matplotlib.pyplot as plt
from scipy.signal import welch, savgol_filter
import pathlib
from pathlib import Path
from audio_postprocess_live_recording_zoom_h2n.cli import process_file
import ffmpeg


def create_white_noise_file(n_sec: float, filename: str) -> pathlib.Path:
    """Create a n_sec seconds long white noise file with name `filename` and
    return its path.
    """
    path = pathlib.Path(filename)

    command = f"anoisesrc=d={n_sec}:c=white:r=44100"

    (
        ffmpeg.input(command, f="lavfi")
        .filter("loudnorm", I=-14, TP=-1.5, LRA=11)
        .output(str(path), acodec="libmp3lame", audio_bitrate="192k")
        .overwrite_output()
        .run(quiet=False)
    )

    return path


def load_mono(path, sr=44100):
    y, _ = lr.load(path, sr=sr, mono=True)
    # avoid all-zero vectors if silence
    if np.max(np.abs(y)) > 0:
        y = y / np.max(np.abs(y))
    return y, sr


def psd_db(y, sr, nperseg=1024 * 16, overlap=0.5):
    nperseg = min(nperseg, len(y)) if len(y) > 0 else nperseg
    noverlap = int(nperseg * overlap)
    f, Pxx = welch(
        y,
        fs=sr,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        detrend=False,
        return_onesided=True,
        scaling="density",
    )
    # avoid log of zero
    Pxx = np.maximum(Pxx, 1e-20)
    db = 10 * np.log10(Pxx)
    return f, db


def smooth(y_db, window=51, poly=3):
    # Savitzky–Golay smoothing (keep features but reduce variance).
    w = min(window, len(y_db) - (1 - len(y_db) % 2))  # ensure odd & ≤ len
    w = w if w >= 5 and w % 2 == 1 else 5
    return savgol_filter(y_db, window_length=w, polyorder=min(poly, w - 2))


def plot_two_spectra(
    white_mp3, eq_mp3, sr=44100, fmin=10, fmax=10000, smooth_curves=True
):
    y1, sr1 = load_mono(white_mp3, sr=sr)
    y2, sr2 = load_mono(eq_mp3, sr=sr)

    # Match lengths (Welch averages better with same-length signals)
    n = min(len(y1), len(y2))
    if n == 0:
        raise ValueError("One of the inputs is empty.")
    y1, y2 = y1[:n], y2[:n]

    f1, db1 = psd_db(y1, sr1)
    f2, db2 = psd_db(y2, sr2)

    if smooth_curves:
        db1 = smooth(db1)
        db2 = smooth(db2)

    # Restrict to audible range
    m1 = (f1 >= fmin) & (f1 <= fmax)
    m2 = (f2 >= fmin) & (f2 <= fmax)

    plt.figure(figsize=(9, 5.5))
    plt.semilogx(f1[m1], db1[m1], label=Path(white_mp3).name)
    plt.semilogx(f2[m2], db2[m2], label=Path(eq_mp3).name)

    plt.title("Power Spectral Density (Welch) — White Noise vs. EQ’d")
    plt.xlabel("Frequency (Hz, log scale)")
    plt.ylabel("Level (dB / Hz)")
    plt.grid(True, which="both", ls=":")
    plt.legend()
    plt.xlim(fmin, fmax)

    # ✅ Custom x-axis ticks (log scale)
    xticks = [20, 50, 70, 100, 200, 500, 700, 1000, 2000, 5000, 10000]
    xlabels = ["20", "50", "70", "100", "200", "500", "700", "1k", "2k", "5k", "10k"]
    plt.xticks(xticks, xlabels)

    plt.tight_layout()
    plt.show()


def main():
    _ = create_white_noise_file(10, "white_noise.mp3")
    process_file("white_noise.mp3", "processed.mp3")
    plot_two_spectra("white_noise.mp3", "processed.mp3")
