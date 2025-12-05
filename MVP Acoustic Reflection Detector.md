#!/usr/bin/env python3
"""
MVP Acoustic Reflection Detector

Detects direct arrival and wall reflections from 3-channel microphone array recordings.

Setup:
- 3 mics in equilateral triangle, side d = 44" = 1.118 m
- M1, M2 at base (facing reflector), M3 at apex (toward source)
- Source behind M3
- Reflector (wall) in front of M1/M2
"""

import sys
import os
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import matplotlib.pyplot as plt

# =============================================================================
# CONFIGURATION - Adjust these for your setup
# =============================================================================

# Array geometry
D_ARRAY = 1.0                # Array side length (m) - 1 meter
TEMP_C = 11.0                # Air temperature (°C)

# Filter settings
F_LOW = 1000                 # Bandpass low cutoff (Hz)
F_HIGH = 6000                # Bandpass high cutoff (Hz)

# Detection settings
DIRECT_THRESH = 0.3          # Threshold fraction for direct arrival detection
REFLECT_PREDICT_MS = 309     # Predicted reflection time (ms after direct)
REFLECT_MARGIN_PCT = 10      # Visual margin (±% of predicted time)
TDOA_WINDOW_MS = 3           # Window for TDOA cross-correlation (±ms)

# Compute visual window bounds
REFLECT_MIN_MS = REFLECT_PREDICT_MS * (1 - REFLECT_MARGIN_PCT / 100)
REFLECT_MAX_MS = REFLECT_PREDICT_MS * (1 + REFLECT_MARGIN_PCT / 100)

# =============================================================================
# PHYSICS
# =============================================================================

def sound_speed(temp_c):
    """Calculate speed of sound in air at given temperature (°C)."""
    return 331.3 * np.sqrt(1 + temp_c / 273.15)

C = sound_speed(TEMP_C)
MAX_TDOA_MS = D_ARRAY / C * 1000  # Physical limit on TDOA

print(f"Sound speed at {TEMP_C}°C: {C:.1f} m/s")
print(f"Max TDOA for d={D_ARRAY:.3f}m: {MAX_TDOA_MS:.2f} ms")
print(f"Predicted reflection: {REFLECT_PREDICT_MS} ms ±{REFLECT_MARGIN_PCT}% → window [{REFLECT_MIN_MS:.1f}, {REFLECT_MAX_MS:.1f}] ms")

# =============================================================================
# SIGNAL PROCESSING
# =============================================================================

def load_wav(path):
    """Load WAV file and extract first 3 channels."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    fs, data = wav.read(path)
    
    # Handle mono/stereo/multi-channel
    if data.ndim == 1:
        raise ValueError("Need at least 3 channels, got mono")
    
    n_channels = data.shape[1]
    if n_channels < 3:
        raise ValueError(f"Need 3 channels, got {n_channels}")
    
    # Extract first 3 channels, convert to float64
    m1 = data[:, 0].astype(np.float64)
    m2 = data[:, 1].astype(np.float64)
    m3 = data[:, 2].astype(np.float64)
    
    # Remove DC offset
    m1 -= np.mean(m1)
    m2 -= np.mean(m2)
    m3 -= np.mean(m3)
    
    # Normalize to [-1, 1]
    max_val = max(np.max(np.abs(m1)), np.max(np.abs(m2)), np.max(np.abs(m3)))
    if max_val > 0:
        m1 /= max_val
        m2 /= max_val
        m3 /= max_val
    
    print(f"\nLoaded: {os.path.basename(path)}")
    print(f"  Sample rate: {fs} Hz")
    print(f"  Duration: {len(m1)/fs:.3f} s")
    print(f"  Channels: {n_channels} (using first 3)")
    
    return fs, m1, m2, m3


def bandpass(sig, fs, f_low, f_high):
    """Apply 4th-order Butterworth bandpass filter."""
    nyq = fs / 2
    low = f_low / nyq
    high = f_high / nyq
    b, a = signal.butter(4, [low, high], btype='band')
    return signal.filtfilt(b, a, sig)


def envelope(sig):
    """Compute signal envelope using Hilbert transform."""
    return np.abs(signal.hilbert(sig))


# =============================================================================
# DETECTION
# =============================================================================

def find_direct_arrival(env_sum, fs, threshold_frac=DIRECT_THRESH):
    """
    Find direct arrival using summed envelope.
    
    Args:
        env_sum: Sum of envelopes from all channels
        fs: Sample rate
        threshold_frac: Fraction of max for threshold
    
    Returns:
        (sample_index, time_in_seconds)
    """
    threshold = threshold_frac * np.max(env_sum)
    
    # Find first sample exceeding threshold
    idx = np.argmax(env_sum > threshold)
    
    if env_sum[idx] <= threshold:
        raise ValueError("Could not detect direct arrival")
    
    return idx, idx / fs


def compute_tdoa(sig1, sig2, fs, center1, center2, window_ms=TDOA_WINDOW_MS):
    """
    Compute TDOA between two signals using cross-correlation.
    
    Args:
        sig1, sig2: Signal arrays
        fs: Sample rate
        center1, center2: Center indices for windowing
        window_ms: Half-window size in ms
    
    Returns:
        (tdoa_microseconds, tdoa_samples)
    """
    # Window in samples
    hw = int(window_ms * fs / 1000)
    
    # Extract windows
    s1 = max(0, center1 - hw)
    e1 = min(len(sig1), center1 + hw)
    s2 = max(0, center2 - hw)
    e2 = min(len(sig2), center2 + hw)
    
    w1 = sig1[s1:e1]
    w2 = sig2[s2:e2]
    
    # Match lengths
    n = min(len(w1), len(w2))
    w1 = w1[:n]
    w2 = w2[:n]
    
    if n < 10:
        return 0.0, 0
    
    # Cross-correlation
    corr = signal.correlate(w1, w2, mode='full')
    lags = np.arange(-(n-1), n)
    
    # Find peak
    peak_idx = np.argmax(corr)
    lag_samples = lags[peak_idx]
    
    # Convert to microseconds
    tdoa_us = lag_samples / fs * 1e6
    
    return tdoa_us, lag_samples


# =============================================================================
# VISUALIZATION
# =============================================================================

def plot_energy_map(env1, env2, env3, fs, direct_idx, predict_ms, margin_min_ms, margin_max_ms, output_path=None):
    """
    Plot energy map: envelopes with predicted reflection marker and margin window.
    """
    n = len(env1)
    t_ms = (np.arange(n) - direct_idx) / fs * 1000
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot envelopes
    ax.plot(t_ms, env1, color='#2563eb', linewidth=1, alpha=0.8, label='M1')
    ax.plot(t_ms, env2, color='#16a34a', linewidth=1, alpha=0.8, label='M2')
    ax.plot(t_ms, env3, color='#ea580c', linewidth=1, alpha=0.8, label='M3')
    
    # Summed envelope (scaled down for visibility)
    env_sum = (env1 + env2 + env3) / 3
    ax.plot(t_ms, env_sum, color='black', linewidth=2, alpha=0.6, label='Combined')
    
    # Direct arrival marker
    ax.axvline(0, color='green', linewidth=2, linestyle='--', label='Direct')
    
    # Margin window shading (behind the prediction line)
    ax.axvspan(margin_min_ms, margin_max_ms, alpha=0.15, color='red', label=f'±{REFLECT_MARGIN_PCT}% margin')
    
    # Predicted reflection marker (on top)
    ax.axvline(predict_ms, color='red', linewidth=2, linestyle='--', label=f'Predicted ({predict_ms:.0f} ms)')
    
    ax.set_xlabel('Time (ms) relative to direct arrival', fontsize=11)
    ax.set_ylabel('Envelope Amplitude', fontsize=11)
    ax.set_title('Energy Map', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-20, max(150, REFLECT_MAX_MS + 50))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()
    plt.close()


# =============================================================================
# MAIN PROCESSING
# =============================================================================

def process_file(wav_path):
    """Process a single WAV file."""
    
    print("\n" + "=" * 70)
    print("MVP REFLECTION DETECTION")
    print("=" * 70)
    
    # 1. Load
    fs, m1, m2, m3 = load_wav(wav_path)
    
    # 2. Bandpass filter
    print(f"\nFiltering: {F_LOW}-{F_HIGH} Hz bandpass")
    m1_filt = bandpass(m1, fs, F_LOW, F_HIGH)
    m2_filt = bandpass(m2, fs, F_LOW, F_HIGH)
    m3_filt = bandpass(m3, fs, F_LOW, F_HIGH)
    
    # 3. Compute envelopes
    env1 = envelope(m1_filt)
    env2 = envelope(m2_filt)
    env3 = envelope(m3_filt)
    
    # 4. Sum envelopes for detection (increases SNR)
    env_sum = env1 + env2 + env3
    
    # 5. Find direct arrival
    print(f"\nDetecting direct arrival (threshold={DIRECT_THRESH*100:.0f}% of max)...")
    direct_idx, direct_t = find_direct_arrival(env_sum, fs)
    print(f"  Direct arrival: sample {direct_idx}, t = {direct_t*1000:.2f} ms")
    
    # 6. Use predicted reflection time
    reflect_idx = direct_idx + int(REFLECT_PREDICT_MS * fs / 1000)
    print(f"\nPredicted reflection: {REFLECT_PREDICT_MS} ms after direct (sample {reflect_idx})")
    
    # 7. Calculate expected distance from prediction
    round_trip_m = REFLECT_PREDICT_MS / 1000 * C
    one_way_m = round_trip_m / 2
    print(f"  Expected round-trip: {round_trip_m:.2f} m")
    print(f"  Expected one-way:    {one_way_m:.2f} m")
    
    # 8. Compute TDOAs
    print(f"\nComputing TDOAs (±{TDOA_WINDOW_MS} ms window)...")
    print("-" * 50)
    
    tdoa_12, _ = compute_tdoa(m1_filt, m2_filt, fs, reflect_idx, reflect_idx)
    tdoa_13, _ = compute_tdoa(m1_filt, m3_filt, fs, reflect_idx, reflect_idx)
    tdoa_23, _ = compute_tdoa(m2_filt, m3_filt, fs, reflect_idx, reflect_idx)
    
    print(f"  M1-M2: {tdoa_12:+.1f} μs  {'(VALID)' if abs(tdoa_12) < MAX_TDOA_MS*1000 else '(EXCEEDS MAX)'}")
    print(f"  M1-M3: {tdoa_13:+.1f} μs  {'(VALID)' if abs(tdoa_13) < MAX_TDOA_MS*1000 else '(EXCEEDS MAX)'}")
    print(f"  M2-M3: {tdoa_23:+.1f} μs  {'(VALID)' if abs(tdoa_23) < MAX_TDOA_MS*1000 else '(EXCEEDS MAX)'}")
    
    # 9. Generate plots
    print("\n" + "-" * 50)
    print("Generating plots...")
    
    base = os.path.splitext(wav_path)[0]
    
    plot_energy_map(env1, env2, env3, fs, direct_idx, REFLECT_PREDICT_MS,
                    REFLECT_MIN_MS, REFLECT_MAX_MS, output_path=f"{base}_energy.png")
    
    # 10. Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Direct arrival:       {direct_t*1000:.2f} ms")
    print(f"  Predicted reflection: {REFLECT_PREDICT_MS} ms after direct")
    print(f"  Expected distance:    {one_way_m:.1f} m (one-way)")
    print(f"  Sound speed used:     {C:.1f} m/s (at {TEMP_C}°C)")
    print("=" * 70 + "\n")
    
    return {
        'direct_idx': direct_idx,
        'direct_t_ms': direct_t * 1000,
        'reflect_idx': reflect_idx,
        'predict_ms': REFLECT_PREDICT_MS,
        'distance_m': one_way_m,
        'tdoa_12_us': tdoa_12,
        'tdoa_13_us': tdoa_13,
        'tdoa_23_us': tdoa_23,
    }


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect_reflection.py <wav_file>")
        print("\nExample:")
        print("  python detect_reflection.py recording.wav")
        sys.exit(1)
    
    wav_path = sys.argv[1]
    
    try:
        results = process_file(wav_path)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
