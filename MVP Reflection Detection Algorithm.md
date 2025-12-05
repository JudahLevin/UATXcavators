MVP Reflection Detection Algorithm
1. Load & Preprocess
    •    Load 3-channel WAV file (M1, M2, M3)
    •    Remove DC offset from each channel
    •    Normalize all channels to the same scale
2. Bandpass Filter
    •    Apply 1-6 kHz bandpass filter to isolate the frequency range where the source signal is strongest (steel pipe clang)
    •    Removes low-frequency rumble and high-frequency noise
3. Compute Envelopes
    •    Use Hilbert transform to get the envelope (amplitude over time) of each filtered channel
    •    Sum all 3 envelopes together → this increases SNR by combining energy from all mics
4. Detect Direct Arrival
    •    Find the first moment the summed envelope exceeds 30% of its maximum value
    •    This marks t = 0 (when the source sound first hits the array)
5. Mark Predicted Reflection
    •    You manually set REFLECT_PREDICT_MS based on the physics calculation:

  Δt = (2R + 0.866) / 337.9 × 1000 ms

    •    The algorithm draws a vertical red line at this predicted time
    •    A shaded ±10% margin window is shown around it for visual reference
6. Compute TDOAs
    •    At the predicted reflection time, extract a small ±3ms window from each channel
    •    Cross-correlate channel pairs (M1-M2, M1-M3, M2-M3) to find time differences of arrival
    •    Flag any TDOA that exceeds the physical maximum (2.96 ms for 1m array)
7. Output
    •    Print summary with expected distance
    •    Save energy map plot showing all envelopes with direct (green) and predicted reflection (red) markers

Key simplification: We don't detect the reflection peak — we predict where it should be based on known geometry, then visually verify if the actual signal peak aligns with our prediction.
