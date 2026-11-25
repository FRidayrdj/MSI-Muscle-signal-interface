# Roadmap

## Done (v0.1)

- Single-channel wireless EMG acquisition: homemade instrumentation amplifier, gain stage, ESP32 sampling and digital filtering, Wi-Fi streaming to a laptop.
- Live app with a measure panel and CSV logging.
- Measured and characterised: gain (≈ 850), noise (≈ 2.8 µV RMS input-referred), CMRR (≈ 91 dB), and a real forearm EMG burst.
- A bench comparison with a bought chip that turned out not to match its marking.

Everything below is **planned, not built**, starting mid-December 2026.

## Planned — channel 2

- Give channel 2 its own gain stage (it currently shares channel 1's through a swap wire).
- Two-channel firmware (`NUM_CH = 2`).
- A second pair of electrodes on the extensor muscles with a shared reference electrode.

## Planned — gesture recognition

- A cue-guided recording tool to collect labelled gestures (rest, fist, open hand, wrist flexion, wrist extension).
- Time-domain features per channel: MAV, RMS, waveform length, zero crossings, slope sign changes.
- A classifier (LDA first, then kNN, SVM or a small MLP), evaluated with leave-one-session-out cross-validation.
- Live inference with majority-vote smoothing.

## Planned — 3D hand

- A 3D hand model, probably with `pyqtgraph.opengl`, that mirrors the predicted gesture in real time.

## Planned — SPICE simulation

- Model the in-amp, gain stage and high-pass corner.
- Compare simulation with the measurements here: gain (8.41 designed vs ≈ 8.4 measured), the ≈ 16 Hz corner, and CMRR with a Monte Carlo run over 1% resistor mismatch.
- Done after the hardware, as a check and to guide the PCB.

## Planned — PCB

- A PCB version of the analog front end, designed in KiCad, replacing the breadboard build.

Nothing in the planned sections is built yet. They are plans, not claims.
