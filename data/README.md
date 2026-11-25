# Data

Raw logs written by the measure panel in `software/msilive.py` (one row per click of "Log reading"). Nothing has been edited or removed, so a few rows are known-bad and are listed here.

## measurements.csv
RMS and peak-to-peak readings at the amplifier output, 17 Nov 2026. Columns: `time, label, channel, rms_1s_mV, rms_window_mV, window_s, pp_1s_mV`.

| Rows (time) | Label | Notes |
|---|---|---|
| 06:28:46 – 06:29:09 | noise homemade | tone off, input tied to Vmid |
| 06:31:50 – 06:32:23 | noise clone | **invalid.** Both amplifier outputs were wired into the gain-stage input at once, so this is really the homemade amp |
| 06:37:52 – 06:38:24 | noise clone | valid (bought chip alone) |
| 06:44:54 – 06:45:26 | noise gainstage only | the measurement floor: gain stage + ADC, input at Vmid |
| 06:54:26 – 06:54:47 | cmrr homemade | **invalid.** A rewiring mistake left an input floating, so every value is 0.00 |
| 06:58:31 – 06:59:36 | cmrr homemade / clone | 1 V common-mode, large-signal check; see `docs/results.md` |

## measurements_v3.csv
Later log with an extra column, `tone100_rms_mV`: the 100 Hz component found with a Hann-windowed FFT, which can read tone residuals far below the broadband noise. These are the runs behind the CMRR numbers, with a 90.9 mV, 100 Hz common-mode signal on both inputs.

| Rows (time) | Label | Mean tone residual |
|---|---|---|
| 07:42:02 – 07:42:18 | cmrr homemade v3 | 2.07 mV |
| 07:45:23 – 07:45:49 | cmrr clone v3 | 0.47 mV |
| 07:47:36 – 07:48:03 | cmrr toneoff | 0.22 mV (the detection floor) |

## Other files
- `dc_checks.md` — supply and bias voltages read with a multimeter.
- `real_emg/` — see the note in that folder.
