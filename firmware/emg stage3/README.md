# emg stage3 — USB-serial bring-up version

The first firmware version: 2 kHz sampling and the digital filter chain (20 Hz high-pass, 50 Hz notch, 450 Hz low-pass), output over USB serial at 115200 baud (230400 dropped characters on Windows).

- `p` = plot mode, for the Arduino Serial Plotter (waveform + envelope)
- `m` = measure mode, prints RMS and DC bias once a second

Board: ESP32 Dev Module. Gain-stage output goes to GPIO34. Use this version for bench checks with **no electrodes attached**; for anything on a person use the Wi-Fi version so the board never has a cable to a laptop.
