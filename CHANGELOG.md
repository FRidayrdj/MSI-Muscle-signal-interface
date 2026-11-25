# Changelog

## v0.1 — channel-1 EMG acquisition (published 2026-11-26)

First public version. Bench work was done 13–17 Nov 2026 and is written up here as it stands.

- 3.3 V regulator and a 1.65 V mid-supply (Vmid) reference
- Homemade 3-op-amp instrumentation amplifier (gain ≈ 8.4) and a gain stage (×101, high-pass ≈ 16 Hz)
- ESP32 firmware: 2 kHz sampling, digital high-pass, 50 Hz notch and low-pass, UDP streaming over Wi-Fi
- `msi_live.py`: live plot with envelope, measure panel (RMS, peak-to-peak, FFT tone readout), recording and logging
- Measurements: gain, input-referred noise, CMRR, wireless link, and a real forearm EMG burst
- A second in-amp from a bought chip, measured as a comparison
